import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "tools" / "gen_renderer_files.py"
PINS_SCRIPT = REPO / "tools" / "dependency_pins.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("gen_renderer_files", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RendererGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = load_generator()
        cls.renderers = cls.generator.load_manifest()

    def run_generator(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_generated_document_has_no_environment_status(self):
        document = self.generator.build_doc(self.renderers)
        self.assertNotIn("Cross-checked against CNA", document)
        self.assertNotIn(str(REPO.parent), document)

    def test_generated_document_uses_c_api_and_ci_policy_terms(self):
        document = self.generator.build_doc(self.renderers)
        self.assertIn("`cna_graphics_device_supports_capability(...)`", document)
        self.assertIn("`CNA_RESULT_NOT_SUPPORTED`", document)
        self.assertIn("| Dependency | CI tier | Notes |", document)
        self.assertNotIn("GraphicsDevice::SupportsCapability", document)
        self.assertNotIn("| Dependency | Tested | Notes |", document)

    def test_manifest_validation_rejects_malformed_platform_data(self):
        malformed = [dict(self.renderers[0])]
        malformed[0]["platforms"] = [{"not": "a platform"}]
        with self.assertRaisesRegex(ValueError, "at least one platform"):
            self.generator.validate_manifest(malformed)

    def test_manifest_validation_rejects_unknown_renderer_fields(self):
        malformed = [dict(self.renderers[0])]
        malformed[0]["pltaforms"] = malformed[0]["platforms"]
        with self.assertRaisesRegex(ValueError, "unknown field.*pltaforms"):
            self.generator.validate_manifest(malformed)

    def test_manifest_validation_rejects_duplicate_experimental_platforms(self):
        malformed = [dict(self.renderers[0])]
        malformed[0]["experimental"] = ["web", "web"]
        with self.assertRaisesRegex(ValueError, "experimental platform more than once"):
            self.generator.validate_manifest(malformed)

    def test_manifest_validation_rejects_duplicate_supported_platforms(self):
        malformed = [dict(self.renderers[0])]
        malformed[0]["platforms"] = ["linux", "linux"]
        with self.assertRaisesRegex(ValueError, "lists a platform more than once"):
            self.generator.validate_manifest(malformed)

    def test_manifest_validation_rejects_duplicate_web_flags(self):
        web_renderer = next(
            renderer for renderer in self.renderers if renderer.get("webflags")
        )
        malformed = [dict(web_renderer)]
        malformed[0]["webflags"] = [web_renderer["webflags"][0]] * 2
        with self.assertRaisesRegex(ValueError, "web flag more than once"):
            self.generator.validate_manifest(malformed)

    def test_manifest_validation_rejects_unknown_top_level_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "renderers.json"
            manifest.write_text(
                json.dumps({"renderers": self.renderers, "renderres": []})
            )
            with mock.patch.object(self.generator, "MANIFEST", manifest):
                with self.assertRaisesRegex(ValueError, "unknown top-level.*renderres"):
                    self.generator.load_manifest()

    def test_cross_compiled_windows_presets_have_no_test_presets(self):
        presets = self.generator.build_presets(self.renderers)
        test_names = {preset["name"] for preset in presets["testPresets"]}
        self.assertIn("directx11", test_names)
        self.assertIn("directx12", test_names)
        self.assertNotIn("windows-directx11", test_names)
        self.assertNotIn("windows-directx12", test_names)

    def test_native_build_and_test_presets_select_matching_debug_configuration(self):
        presets = self.generator.build_presets(self.renderers)
        configure = {
            preset["name"]: preset for preset in presets["configurePresets"]
        }
        self.assertEqual(
            "Debug", configure["base"]["cacheVariables"]["CMAKE_BUILD_TYPE"]
        )
        builds = {preset["name"]: preset for preset in presets["buildPresets"]}
        tests = {preset["name"]: preset for preset in presets["testPresets"]}
        native_names = {
            name
            for name, preset in configure.items()
            if not preset.get("hidden") and preset.get("inherits") == "base"
        }
        self.assertTrue(native_names)
        self.assertLessEqual(set(tests), native_names)
        for name in native_names:
            self.assertEqual("Debug", builds[name]["configuration"])
        for name, preset in tests.items():
            self.assertEqual(builds[name]["configuration"], preset["configuration"])

    def test_mingw_build_presets_select_debug_and_have_no_tests(self):
        presets = self.generator.build_presets(self.renderers)
        configure = {
            preset["name"]: preset for preset in presets["configurePresets"]
        }
        self.assertEqual(
            "Debug", configure["base"]["cacheVariables"]["CMAKE_BUILD_TYPE"]
        )
        tests = {preset["name"] for preset in presets["testPresets"]}
        mingw_builds = [
            preset
            for preset in presets["buildPresets"]
            if configure[preset["name"]].get("inherits") == "mingw-base"
        ]
        self.assertTrue(mingw_builds)
        for preset in mingw_builds:
            self.assertEqual("Debug", preset["configuration"])
            self.assertNotIn(preset["name"], tests)

    def test_web_build_presets_select_release_and_have_no_tests(self):
        presets = self.generator.build_presets(self.renderers)
        configure = {
            preset["name"]: preset for preset in presets["configurePresets"]
        }
        self.assertEqual(
            "Release", configure["release"]["cacheVariables"]["CMAKE_BUILD_TYPE"]
        )
        tests = {preset["name"] for preset in presets["testPresets"]}
        web_builds = [
            preset
            for preset in presets["buildPresets"]
            if configure[preset["name"]].get("inherits") == "web-base"
        ]
        self.assertTrue(web_builds)
        for preset in web_builds:
            self.assertEqual("Release", preset["configuration"])
            self.assertNotIn(preset["name"], tests)

    def test_host_conditions_cover_configure_build_and_test_presets(self):
        presets = self.generator.build_presets(self.renderers)
        for preset_kind in ("configurePresets", "buildPresets", "testPresets"):
            metal = next(
                preset for preset in presets[preset_kind] if preset["name"] == "metal"
            )
            self.assertEqual("Darwin", metal["condition"]["rhs"])

        for preset_kind in ("configurePresets", "buildPresets", "testPresets"):
            opengl1 = next(
                preset for preset in presets[preset_kind] if preset["name"] == "opengl1"
            )
            self.assertEqual("inList", opengl1["condition"]["type"])
            self.assertEqual(["Linux", "Windows"], opengl1["condition"]["list"])

        for preset_kind in ("configurePresets", "buildPresets"):
            windows = next(
                preset
                for preset in presets[preset_kind]
                if preset["name"] == "windows-directx11"
            )
            self.assertEqual("Linux", windows["condition"]["rhs"])

        for preset_kind in ("configurePresets", "buildPresets", "testPresets"):
            native_windows = next(
                preset
                for preset in presets[preset_kind]
                if preset["name"] == "directx11"
            )
            self.assertEqual("Windows", native_windows["condition"]["rhs"])

    def test_generated_preset_kinds_have_no_orphans_or_condition_drift(self):
        presets = self.generator.build_presets(self.renderers)
        configure = {
            preset["name"]: preset
            for preset in presets["configurePresets"]
            if not preset.get("hidden")
        }
        build = {preset["name"]: preset for preset in presets["buildPresets"]}
        tests = {preset["name"]: preset for preset in presets["testPresets"]}
        self.assertEqual(set(configure), set(build))
        self.assertLessEqual(set(tests), set(configure))
        for name, preset in build.items():
            self.assertEqual(name, preset["configurePreset"])
            self.assertEqual(configure[name]["condition"], preset["condition"])
        for name, preset in tests.items():
            self.assertEqual(name, preset["configurePreset"])
            self.assertEqual(configure[name]["condition"], preset["condition"])
            self.assertEqual(build[name]["configuration"], preset["configuration"])
            self.assertEqual("error", preset["execution"]["noTestsAction"])

    def test_host_condition_derives_every_desktop_platform_combination(self):
        cases = {
            ("linux",): {"Linux"},
            ("windows",): {"Windows"},
            ("macos",): {"Darwin"},
            ("linux", "windows"): {"Linux", "Windows"},
            ("linux", "macos"): {"Linux", "Darwin"},
            ("windows", "macos"): {"Windows", "Darwin"},
            ("linux", "windows", "macos"): {"Linux", "Windows", "Darwin"},
        }
        for platforms, expected_hosts in cases.items():
            with self.subTest(platforms=platforms):
                condition = self.generator.host_condition(list(platforms))
                if condition["type"] == "equals":
                    actual_hosts = {condition["rhs"]}
                else:
                    self.assertEqual("inList", condition["type"])
                    actual_hosts = set(condition["list"])
                self.assertEqual(expected_hosts, actual_hosts)

    def test_web_route_is_host_gated_and_never_gets_a_test_preset(self):
        presets = self.generator.build_presets(self.renderers)
        for preset_kind in ("configurePresets", "buildPresets"):
            webgl2 = next(
                preset
                for preset in presets[preset_kind]
                if preset["name"] == "web-webgl2"
            )
            self.assertEqual("inList", webgl2["condition"]["type"])
            self.assertEqual(
                {"Linux", "Windows", "Darwin"}, set(webgl2["condition"]["list"])
            )
        self.assertNotIn(
            "web-webgl2", {preset["name"] for preset in presets["testPresets"]}
        )

    def test_android_support_does_not_make_a_desktop_preset_host(self):
        presets = self.generator.build_presets(self.renderers)
        sdl = next(
            preset
            for preset in presets["configurePresets"]
            if preset["name"] == "sdl-renderer"
        )
        self.assertEqual(
            {"Linux", "Windows", "Darwin"}, set(sdl["condition"]["list"])
        )

    def test_same_count_semantic_cna_drift_fails_check(self):
        canonical = [renderer["name"] for renderer in self.renderers]
        canonical[0] = "RENAMED_RENDERER"
        strings = " ".join(json.dumps(name) for name in canonical)

        with tempfile.TemporaryDirectory() as temporary:
            cna_root = Path(temporary) / "cna"
            (cna_root / "cmake").mkdir(parents=True)
            (cna_root / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.23)\n")
            (cna_root / "cmake" / "RendererSelection.cmake").write_text(
                "set_property(CACHE CNA_GRAPHICS_RENDERER PROPERTY STRINGS "
                + strings
                + ")\n"
            )
            result = self.run_generator("--check", "--cna-root", str(cna_root))

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("RENAMED_RENDERER", result.stdout)
        self.assertNotIn("generated file(s) up to date", result.stdout)

    def test_unknown_ci_platform_is_rejected(self):
        result = self.run_generator("--ci-matrix", "linx")
        self.assertEqual(2, result.returncode)
        self.assertIn("invalid choice", result.stderr)

    def test_unknown_ci_tier_is_rejected(self):
        result = self.run_generator("--ci-matrix", "linux", "--tiers", "Z")
        self.assertEqual(2, result.returncode)
        self.assertIn("unknown CI tier", result.stderr)

    def test_known_but_empty_ci_selection_is_supported(self):
        result = self.run_generator("--ci-matrix", "android", "--tiers", "X")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], json.loads(result.stdout))


class CMakeRendererValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = load_generator()
        cls.renderer_names = [
            renderer["name"] for renderer in cls.generator.load_manifest()
        ]

    def test_regex_metacharacters_reach_intentional_unknown_renderer_error(self):
        canonical = " ".join(json.dumps(name) for name in self.renderer_names)
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            cna_root = temporary_path / "cna"
            (cna_root / "cmake").mkdir(parents=True)
            (cna_root / "cmake" / "RendererSelection.cmake").write_text(
                "set_property(CACHE CNA_GRAPHICS_RENDERER PROPERTY STRINGS "
                + canonical
                + ")\n"
            )
            script = temporary_path / "validate.cmake"
            script.write_text(
                "cmake_minimum_required(VERSION 3.23)\n"
                f'include("{REPO / "cmake" / "CnaRenderers.cmake"}")\n'
                'cna_template_validate_renderer("${INVALID_RENDERER}" "${CNA_ROOT}")\n'
            )

            for invalid in ("[", "(", "*", ".", "+", "?", "\\"):
                with self.subTest(invalid=invalid):
                    result = subprocess.run(
                        [
                            "cmake",
                            f"-DINVALID_RENDERER={invalid}",
                            f"-DCNA_ROOT={cna_root}",
                            "-P",
                            str(script),
                        ],
                        cwd=REPO,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False,
                    )
                    output = result.stdout + result.stderr
                    self.assertNotEqual(0, result.returncode, output)
                    self.assertIn("cna-template: unknown renderer", output)
                    self.assertNotIn("Regular expression", output)
                    self.assertNotIn("cannot compile", output)


class DependencyPinTests(unittest.TestCase):
    def run_pins(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PINS_SCRIPT), *arguments],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_lock_file_is_valid_and_exposes_cna_revision(self):
        validation = self.run_pins()
        self.assertEqual(0, validation.returncode, validation.stderr)
        revision = self.run_pins("--revision", "CNA")
        self.assertEqual(0, revision.returncode, revision.stderr)
        self.assertRegex(revision.stdout.strip(), r"^[0-9a-f]{40}$")

    def test_lock_file_exposes_repository_url_and_local_directory(self):
        repository = self.run_pins("--repository", "CNA")
        url = self.run_pins("--url", "CNA")
        directory = self.run_pins("--directory", "CNA")
        self.assertEqual(0, repository.returncode, repository.stderr)
        self.assertEqual("openeggbert/cna", repository.stdout.strip())
        self.assertEqual("https://github.com/openeggbert/cna.git", url.stdout.strip())
        self.assertEqual("cna", directory.stdout.strip())

    def test_pin_tool_uses_shared_dependency_layout(self):
        spec = importlib.util.spec_from_file_location("dependency_pins", PINS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        expected_candidates = {REPO.parent.resolve(), REPO.parent.parent.resolve()}
        self.assertIn(module.default_dependencies_dir().resolve(), expected_candidates)

    def test_unknown_dependency_name_is_rejected(self):
        result = self.run_pins("--revision", "NOT_A_DEPENDENCY")
        self.assertEqual(2, result.returncode)
        self.assertIn("unknown dependency", result.stderr)


if __name__ == "__main__":
    unittest.main()

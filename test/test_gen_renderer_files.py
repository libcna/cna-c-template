import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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

    def test_manifest_validation_rejects_malformed_platform_data(self):
        malformed = [dict(self.renderers[0])]
        malformed[0]["platforms"] = [{"not": "a platform"}]
        with self.assertRaisesRegex(ValueError, "at least one platform"):
            self.generator.validate_manifest(malformed)

    def test_cross_compiled_windows_presets_have_no_test_presets(self):
        presets = self.generator.build_presets(self.renderers)
        test_names = {preset["name"] for preset in presets["testPresets"]}
        self.assertNotIn("windows-directx11", test_names)
        self.assertNotIn("windows-directx12", test_names)

    def test_host_conditions_cover_configure_build_and_test_presets(self):
        presets = self.generator.build_presets(self.renderers)
        for preset_kind in ("configurePresets", "buildPresets", "testPresets"):
            metal = next(
                preset for preset in presets[preset_kind] if preset["name"] == "metal"
            )
            self.assertEqual("Darwin", metal["condition"]["rhs"])

        for preset_kind in ("configurePresets", "buildPresets"):
            windows = next(
                preset
                for preset in presets[preset_kind]
                if preset["name"] == "windows-directx11"
            )
            self.assertEqual("Linux", windows["condition"]["rhs"])

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

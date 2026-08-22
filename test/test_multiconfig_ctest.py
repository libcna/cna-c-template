import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
VERIFIER = REPO / "tools" / "verify_ctest_contract.py"
TEST_MODULE = REPO / "cmake" / "CnaTemplateTests.cmake"


def require_ninja_multi_config():
    if shutil.which("ninja") is None:
        raise unittest.SkipTest("required ninja build program is unavailable")

    try:
        capabilities = subprocess.run(
            ["cmake", "-E", "capabilities"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        raise unittest.SkipTest("cmake executable is unavailable") from exc
    if capabilities.returncode != 0:
        raise AssertionError(
            "cmake -E capabilities failed: "
            + (capabilities.stderr.strip() or capabilities.stdout.strip())
        )
    try:
        document = json.loads(capabilities.stdout)
        generators = {
            generator["name"] for generator in document.get("generators", [])
        }
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise AssertionError("cmake -E capabilities returned malformed JSON") from exc
    if "Ninja Multi-Config" not in generators:
        raise unittest.SkipTest("Ninja Multi-Config generator is unavailable")


class NinjaAvailabilityDetectionTests(unittest.TestCase):
    def test_missing_ninja_build_program_skips_before_configure(self):
        with mock.patch.object(shutil, "which", return_value=None), mock.patch.object(
            subprocess, "run"
        ) as run:
            with self.assertRaisesRegex(unittest.SkipTest, "ninja build program"):
                require_ninja_multi_config()
        run.assert_not_called()


class NinjaMultiConfigCTestRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_ninja_multi_config()

        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.source = cls.root / "source"
        cls.build = cls.root / "build-multi"
        cls.single_build = cls.root / "build-single"
        cls.source.mkdir()

        test_module = str(TEST_MODULE).replace("\\", "/").replace('"', '\\"')
        (cls.source / "CMakeLists.txt").write_text(
            "cmake_minimum_required(VERSION 3.23)\n"
            "project(MultiConfigCTestFixture LANGUAGES C)\n"
            'set(CNA_TEMPLATE_APP_NAME "MultiConfigContractApp" CACHE STRING "")\n'
            "add_executable(${CNA_TEMPLATE_APP_NAME} main.c)\n"
            "add_custom_command(TARGET ${CNA_TEMPLATE_APP_NAME} POST_BUILD\n"
            "  COMMAND ${CMAKE_COMMAND} -E copy_if_different\n"
            "    ${CMAKE_CURRENT_SOURCE_DIR}/asset.txt\n"
            "    $<TARGET_FILE_DIR:${CNA_TEMPLATE_APP_NAME}>/asset.txt)\n"
            "enable_testing()\n"
            f'include("{test_module}")\n'
            "cna_template_register_tests(\n"
            '  APPLICATION_TARGET "${CNA_TEMPLATE_APP_NAME}"\n'
            '  DISPLAY_CLASSIFICATION "none")\n',
            encoding="utf-8",
        )
        (cls.source / "asset.txt").write_text("fixture asset\n", encoding="utf-8")
        (cls.source / "main.c").write_text(
            "#include <stdio.h>\n"
            "#include <string.h>\n"
            "int main(int argc, char **argv) {\n"
            '  FILE *asset = fopen("asset.txt", "rb");\n'
            "  if (asset == NULL) {\n"
            '    fputs("asset.txt was not found in the runtime directory\\n", stderr);\n'
            "    return 4;\n"
            "  }\n"
            "  fclose(asset);\n"
            "  if (argc == 3 && strcmp(argv[1], \"--smoke-test\") == 0 &&\n"
            "      strcmp(argv[2], \"--simulate-draw-failure\") == 0) {\n"
            '    fputs("CNA_TEMPLATE_TEST: draw failure injected (result=2)\\n",\n'
            "          stderr);\n"
            '    fputs("CNA_TEMPLATE_TEST: draw failure propagated '
            '(injected_result=2, run_result=9, destroy_result=9, exit_code=86)\\n",\n'
            "          stderr);\n"
            "    return 86;\n"
            "  }\n"
            "  return argc == 2 && strcmp(argv[1], \"--smoke-test\") == 0 ? 0 : 3;\n"
            "}\n",
            encoding="utf-8",
        )

        cls._run_checked(
            [
                "cmake",
                "-S",
                str(cls.source),
                "-B",
                str(cls.build),
                "-G",
                "Ninja Multi-Config",
            ]
        )
        cls._run_checked(
            ["cmake", "--build", str(cls.build), "--config", "Debug"]
        )
        cls._run_checked(
            [
                "cmake",
                "-S",
                str(cls.source),
                "-B",
                str(cls.single_build),
                "-G",
                "Ninja",
                "-DCMAKE_BUILD_TYPE=Debug",
            ]
        )
        cls._run_checked(["cmake", "--build", str(cls.single_build)])

    @classmethod
    def _run_checked(cls, command):
        result = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"command failed ({result.returncode}): {command!r}\n"
                f"{result.stdout}{result.stderr}"
            )
        return result

    def run_verifier(self, *arguments, test_dir=None):
        return subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--test-dir",
                str(test_dir or self.build),
                *arguments,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_verifier_requires_and_uses_multi_config_selection(self):
        missing = self.run_verifier()
        self.assertNotEqual(0, missing.returncode)
        self.assertIn("multi-config generator", missing.stderr)
        self.assertIn("--config", missing.stderr)

        invalid = self.run_verifier("--config", "NotAConfiguration")
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("not available", invalid.stderr)

        selected = self.run_verifier("--config", "Debug")
        self.assertEqual(0, selected.returncode, selected.stdout + selected.stderr)
        self.assertIn("in configuration Debug", selected.stdout)

    def test_verifier_validates_single_config_selection(self):
        implicit = self.run_verifier(test_dir=self.single_build)
        self.assertEqual(0, implicit.returncode, implicit.stdout + implicit.stderr)
        self.assertNotIn("in configuration", implicit.stdout)

        matching = self.run_verifier(
            "--config", "Debug", test_dir=self.single_build
        )
        self.assertEqual(0, matching.returncode, matching.stdout + matching.stderr)
        self.assertIn("in configuration Debug", matching.stdout)

        for invalid in ("Release", "DefinitelyWrong"):
            with self.subTest(config=invalid):
                mismatch = self.run_verifier(
                    "--config", invalid, test_dir=self.single_build
                )
                self.assertNotEqual(0, mismatch.returncode)
                self.assertIn("does not match single-config build tree", mismatch.stderr)
                self.assertIn("CMAKE_BUILD_TYPE='Debug'", mismatch.stderr)

    def test_ctest_runs_from_configuration_specific_executable_directory(self):
        discovery = self._run_checked(
            [
                "ctest",
                "--test-dir",
                str(self.build),
                "-C",
                "Debug",
                "--show-only=json-v1",
            ]
        )
        document = json.loads(discovery.stdout)
        smoke = next(
            test for test in document["tests"] if test["name"] == "CnaCTemplateSmoke"
        )
        failure = next(
            test
            for test in document["tests"]
            if test["name"] == "CnaCTemplateFailurePropagation"
        )
        executable = Path(smoke["command"][0])
        properties = {
            property_document["name"]: property_document["value"]
            for property_document in smoke["properties"]
        }
        failure_properties = {
            property_document["name"]: property_document["value"]
            for property_document in failure["properties"]
        }
        self.assertNotEqual(self.build.resolve(), executable.parent.resolve())
        self.assertEqual(
            executable.parent.resolve(),
            Path(properties["WORKING_DIRECTORY"]).resolve(),
        )
        self.assertEqual(["headless"], properties["LABELS"])
        self.assertEqual(30.0, properties["TIMEOUT"])
        self.assertEqual(
            {"headless", "failure-propagation"},
            set(failure_properties["LABELS"]),
        )
        self.assertEqual(30.0, failure_properties["TIMEOUT"])
        self.assertTrue((executable.parent / "asset.txt").is_file())
        direct_from_build_root = subprocess.run(
            [str(executable), "--smoke-test"],
            cwd=self.build,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(0, direct_from_build_root.returncode)
        self.assertIn("asset.txt was not found", direct_from_build_root.stderr)

        execution = self._run_checked(
            [
                "ctest",
                "--test-dir",
                str(self.build),
                "-C",
                "Debug",
                "--output-on-failure",
            ]
        )
        self.assertIn("100% tests passed", execution.stdout)


if __name__ == "__main__":
    unittest.main()

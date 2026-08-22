import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
VERIFIER = REPO / "tools" / "verify_ctest_contract.py"
FAILURE_WRAPPER = REPO / "cmake" / "VerifyFailurePropagation.cmake"


class NinjaMultiConfigCTestRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        capabilities = subprocess.run(
            ["cmake", "-E", "capabilities"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if capabilities.returncode != 0:
            raise unittest.SkipTest("cmake -E capabilities is unavailable")
        generators = {
            generator["name"]
            for generator in json.loads(capabilities.stdout).get("generators", [])
        }
        if "Ninja Multi-Config" not in generators:
            raise unittest.SkipTest("Ninja Multi-Config generator is unavailable")

        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.source = cls.root / "source"
        cls.build = cls.root / "build"
        cls.source.mkdir()

        wrapper = str(FAILURE_WRAPPER).replace("\\", "/").replace('"', '\\"')
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
            "add_test(NAME CnaCTemplateSmoke\n"
            "  COMMAND ${CNA_TEMPLATE_APP_NAME} --smoke-test)\n"
            "set_tests_properties(CnaCTemplateSmoke PROPERTIES\n"
            '  WORKING_DIRECTORY "$<TARGET_FILE_DIR:${CNA_TEMPLATE_APP_NAME}>")\n'
            "add_test(NAME CnaCTemplateFailurePropagation\n"
            "  COMMAND ${CMAKE_COMMAND}\n"
            '    "-DTEST_EXECUTABLE=$<TARGET_FILE:${CNA_TEMPLATE_APP_NAME}>"\n'
            '    "-DTEST_WORKING_DIRECTORY=$<TARGET_FILE_DIR:${CNA_TEMPLATE_APP_NAME}>"\n'
            f'    -P "{wrapper}")\n',
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

    def run_verifier(self, *arguments):
        return subprocess.run(
            [sys.executable, str(VERIFIER), "--test-dir", str(self.build), *arguments],
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
        executable = Path(smoke["command"][0])
        properties = {
            property_document["name"]: property_document["value"]
            for property_document in smoke["properties"]
        }
        self.assertNotEqual(self.build.resolve(), executable.parent.resolve())
        self.assertEqual(
            executable.parent.resolve(),
            Path(properties["WORKING_DIRECTORY"]).resolve(),
        )
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

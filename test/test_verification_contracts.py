import importlib.util
import re
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "tools" / "verify_ctest_contract.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_ctest_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CTestContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load_verifier()
        cls.expected = list(cls.verifier.EXPECTED_TESTS)

    def valid_tests(self, app_name="RenamedGame"):
        executable = f"/tmp/cna-template-test/{app_name}"
        return {
            "CnaCTemplateSmoke": self.verifier.DiscoveredTest(
                [executable, "--smoke-test"],
                {"WORKING_DIRECTORY": "/tmp/cna-template-test"},
            ),
            "CnaCTemplateFailurePropagation": self.verifier.DiscoveredTest(
                [
                    "/usr/bin/cmake",
                    f"-DTEST_EXECUTABLE={executable}",
                    "-DTEST_WORKING_DIRECTORY=/tmp/cna-template-test",
                    "-P",
                    str(self.verifier.FAILURE_WRAPPER),
                ],
                {"WORKING_DIRECTORY": "/tmp/cna-template-build"},
            ),
        }

    def test_exact_contract_passes(self):
        self.verifier.validate_test_names(self.expected, self.expected)

    def test_zero_tests_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "zero tests"):
            self.verifier.validate_test_names([], self.expected)

    def test_missing_expected_identity_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "CnaCTemplateFailurePropagation"):
            self.verifier.validate_test_names(["CnaCTemplateSmoke"], self.expected)

    def test_unexpected_name_drift_cannot_pass_exact_contract(self):
        with self.assertRaisesRegex(ValueError, "RenamedFailureTest"):
            self.verifier.validate_test_names(
                ["CnaCTemplateSmoke", "RenamedFailureTest"], self.expected
            )

    def test_required_subset_can_be_explicitly_extensible(self):
        self.verifier.validate_test_names(
            self.expected + ["FutureTest"], self.expected, allow_extra=True
        )

    def test_custom_application_name_keeps_stable_valid_test_commands(self):
        tests = self.valid_tests("MyRenamedGame")
        self.verifier.validate_test_contract(tests, "MyRenamedGame")

    def test_smoke_working_directory_must_match_executable_directory(self):
        tests = self.valid_tests()
        tests["CnaCTemplateSmoke"] = self.verifier.DiscoveredTest(
            tests["CnaCTemplateSmoke"].command,
            {"WORKING_DIRECTORY": "/tmp/cna-template-build"},
        )
        with self.assertRaisesRegex(ValueError, "configured executable directory"):
            self.verifier.validate_test_contract(tests, "RenamedGame")

    def test_smoke_working_directory_property_is_required(self):
        tests = self.valid_tests()
        tests["CnaCTemplateSmoke"] = self.verifier.DiscoveredTest(
            tests["CnaCTemplateSmoke"].command, {}
        )
        with self.assertRaisesRegex(ValueError, "no string WORKING_DIRECTORY"):
            self.verifier.validate_test_contract(tests, "RenamedGame")

    def test_success_smoke_command_cannot_replace_failure_wrapper(self):
        tests = self.valid_tests()
        tests["CnaCTemplateFailurePropagation"] = self.verifier.DiscoveredTest(
            list(tests["CnaCTemplateSmoke"].command), {}
        )
        with self.assertRaisesRegex(ValueError, "dedicated CMake wrapper"):
            self.verifier.validate_test_contract(tests, "RenamedGame")

    def test_failure_wrapper_must_target_same_executable(self):
        tests = self.valid_tests()
        command = list(tests["CnaCTemplateFailurePropagation"].command)
        command[1] = "-DTEST_EXECUTABLE=/tmp/cna-template-test/OtherGame"
        tests["CnaCTemplateFailurePropagation"] = self.verifier.DiscoveredTest(
            command, tests["CnaCTemplateFailurePropagation"].properties
        )
        with self.assertRaisesRegex(ValueError, "same configured executable"):
            self.verifier.validate_test_contract(tests, "RenamedGame")

    def test_failure_wrapper_path_is_part_of_contract(self):
        tests = self.valid_tests()
        command = list(tests["CnaCTemplateFailurePropagation"].command)
        command[4] = "/tmp/WrongWrapper.cmake"
        tests["CnaCTemplateFailurePropagation"] = self.verifier.DiscoveredTest(
            command, tests["CnaCTemplateFailurePropagation"].properties
        )
        with self.assertRaisesRegex(ValueError, "VerifyFailurePropagation"):
            self.verifier.validate_test_contract(tests, "RenamedGame")

    def test_ctest_json_requires_command_arrays(self):
        with self.assertRaisesRegex(ValueError, "command array"):
            self.verifier.extract_tests(
                {"tests": [{"name": "CnaCTemplateSmoke", "properties": []}]}
            )

    def test_ctest_json_extracts_named_properties(self):
        tests = self.verifier.extract_tests(
            {
                "tests": [
                    {
                        "name": "CnaCTemplateSmoke",
                        "command": ["/tmp/app", "--smoke-test"],
                        "properties": [
                            {"name": "WORKING_DIRECTORY", "value": "/tmp"},
                            {"name": "TIMEOUT", "value": 30.0},
                        ],
                    }
                ]
            }
        )
        self.assertEqual(
            "/tmp", tests["CnaCTemplateSmoke"].properties["WORKING_DIRECTORY"]
        )

    def test_multi_config_tree_requires_valid_explicit_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            test_dir = Path(temporary)
            (test_dir / "CMakeCache.txt").write_text(
                "CMAKE_GENERATOR:INTERNAL=Ninja Multi-Config\n"
                "CMAKE_CONFIGURATION_TYPES:STRING=Debug;Release\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "pass --config"):
                self.verifier.resolve_ctest_configuration(test_dir, None)
            with self.assertRaisesRegex(ValueError, "not available"):
                self.verifier.resolve_ctest_configuration(test_dir, "RelWithDebInfo")
            self.assertEqual(
                "Debug",
                self.verifier.resolve_ctest_configuration(test_dir, "Debug"),
            )
            self.assertEqual(
                [
                    "ctest",
                    "--test-dir",
                    str(test_dir),
                    "-C",
                    "Debug",
                    "--show-only=json-v1",
                ],
                self.verifier.ctest_discovery_command(test_dir, "Debug"),
            )

    def test_single_config_tree_needs_no_configuration_argument(self):
        with tempfile.TemporaryDirectory() as temporary:
            test_dir = Path(temporary)
            (test_dir / "CMakeCache.txt").write_text(
                "CMAKE_GENERATOR:INTERNAL=Ninja\n"
                "CMAKE_BUILD_TYPE:STRING=Debug\n",
                encoding="utf-8",
            )
            self.assertIsNone(
                self.verifier.resolve_ctest_configuration(test_dir, None)
            )
            self.assertEqual(
                "Debug",
                self.verifier.resolve_ctest_configuration(test_dir, "Debug"),
            )

    def test_configured_application_name_comes_from_cmake_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            test_dir = Path(temporary)
            (test_dir / "CMakeCache.txt").write_text(
                "CNA_TEMPLATE_APP_NAME:STRING=CustomApp\n", encoding="utf-8"
            )
            self.assertEqual(
                "CustomApp", self.verifier.read_configured_app_name(test_dir)
            )

    def test_ci_exercises_a_non_default_application_name(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        self.assertIn("CNA_TEMPLATE_CI_APP_NAME: CnaTemplateCiApp", workflow)
        self.assertIn('-DCNA_TEMPLATE_APP_NAME="$CNA_TEMPLATE_CI_APP_NAME"', workflow)
        self.assertNotIn("./HelloGame", workflow)

    def test_ci_uses_the_verified_strict_linux_compiler_baseline(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        headless_job = workflow.split("  android-gradle-configuration:", 1)[0]
        self.assertIn("runs-on: ubuntu-24.04", headless_job)
        self.assertIn("CC: gcc-14", headless_job)
        self.assertIn("CXX: g++-14", headless_job)
        self.assertNotIn("Wno-error", headless_job)

    def test_ci_installs_the_linux_headers_required_by_pinned_cna(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        headless_job = workflow.split("  android-gradle-configuration:", 1)[0]
        for package in (
            "libavcodec-dev",
            "libavformat-dev",
            "libavutil-dev",
            "libswresample-dev",
            "libx11-dev",
            "libxcursor-dev",
            "libxext-dev",
            "libxfixes-dev",
            "libxi-dev",
            "libxrandr-dev",
            "libxss-dev",
            "libxtst-dev",
        ):
            self.assertIn(package, headless_job)
        self.assertLess(
            headless_job.index("sudo apt-get install"),
            headless_job.index("- name: Build pinned HEADLESS baseline"),
        )

    def test_android_wrapper_validation_precedes_dependency_checkouts(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        android_job = workflow.split("  android-gradle-configuration:", 1)[1]
        wrapper_validation = android_job.index(
            "uses: gradle/actions/setup-gradle@"
        )
        cna_checkout = android_job.index("path: _dependencies/cna")
        sharp_runtime_checkout = android_job.index(
            "path: _dependencies/sharp-runtime"
        )
        self.assertLess(wrapper_validation, cna_checkout)
        self.assertLess(wrapper_validation, sharp_runtime_checkout)
        self.assertIn("validate-wrappers: true", android_job[:cna_checkout])

    def test_ci_uses_only_supported_setup_gradle_inputs(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        self.assertNotIn("build-root-directory:", workflow)

    def test_ci_actions_are_pinned_to_release_shas(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        uses_lines = [line.strip() for line in workflow.splitlines() if "uses:" in line]
        self.assertTrue(uses_lines)
        for line in uses_lines:
            with self.subTest(line=line):
                self.assertRegex(
                    line,
                    re.compile(
                        r"^uses: [^@]+@[0-9a-f]{40} +"
                        r"# v[0-9]+(?:\.[0-9]+){2}$"
                    ),
                )


if __name__ == "__main__":
    unittest.main()

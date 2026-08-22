import importlib.util
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

    def valid_commands(self, app_name="RenamedGame"):
        executable = f"/tmp/cna-template-test/{app_name}"
        return {
            "CnaCTemplateSmoke": [executable, "--smoke-test"],
            "CnaCTemplateFailurePropagation": [
                "/usr/bin/cmake",
                f"-DTEST_EXECUTABLE={executable}",
                "-DTEST_WORKING_DIRECTORY=/tmp/cna-template-test",
                "-P",
                str(self.verifier.FAILURE_WRAPPER),
            ],
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
        commands = self.valid_commands("MyRenamedGame")
        self.verifier.validate_test_commands(commands, "MyRenamedGame")

    def test_success_smoke_command_cannot_replace_failure_wrapper(self):
        commands = self.valid_commands()
        commands["CnaCTemplateFailurePropagation"] = list(
            commands["CnaCTemplateSmoke"]
        )
        with self.assertRaisesRegex(ValueError, "dedicated CMake wrapper"):
            self.verifier.validate_test_commands(commands, "RenamedGame")

    def test_failure_wrapper_must_target_same_executable(self):
        commands = self.valid_commands()
        commands["CnaCTemplateFailurePropagation"][1] = (
            "-DTEST_EXECUTABLE=/tmp/cna-template-test/OtherGame"
        )
        with self.assertRaisesRegex(ValueError, "same configured executable"):
            self.verifier.validate_test_commands(commands, "RenamedGame")

    def test_failure_wrapper_path_is_part_of_contract(self):
        commands = self.valid_commands()
        commands["CnaCTemplateFailurePropagation"][4] = "/tmp/WrongWrapper.cmake"
        with self.assertRaisesRegex(ValueError, "VerifyFailurePropagation"):
            self.verifier.validate_test_commands(commands, "RenamedGame")

    def test_ctest_json_requires_command_arrays(self):
        with self.assertRaisesRegex(ValueError, "command array"):
            self.verifier.extract_test_commands(
                {"tests": [{"name": "CnaCTemplateSmoke"}]}
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

    def test_ci_installs_the_headers_required_by_pinned_cna_sdl(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        headless_job = workflow.split("  android-gradle-configuration:", 1)[0]
        self.assertIn("libx11-dev", headless_job)
        self.assertIn("libxext-dev", headless_job)
        self.assertLess(
            headless_job.index("sudo apt-get install"),
            headless_job.index("- name: Build pinned HEADLESS baseline"),
        )

    def test_android_wrapper_validation_precedes_dependency_checkouts(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        android_job = workflow.split("  android-gradle-configuration:", 1)[1]
        wrapper_validation = android_job.index(
            "uses: gradle/actions/setup-gradle@v6"
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


if __name__ == "__main__":
    unittest.main()

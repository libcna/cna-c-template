import importlib.util
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
        cls.expected = ["HelloGameSmoke", "HelloGameFailurePropagation"]

    def test_exact_contract_passes(self):
        self.verifier.validate_test_names(self.expected, self.expected)

    def test_zero_tests_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "zero tests"):
            self.verifier.validate_test_names([], self.expected)

    def test_missing_expected_identity_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "HelloGameFailurePropagation"):
            self.verifier.validate_test_names(["HelloGameSmoke"], self.expected)

    def test_unexpected_name_drift_cannot_pass_exact_contract(self):
        with self.assertRaisesRegex(ValueError, "RenamedFailureTest"):
            self.verifier.validate_test_names(
                ["HelloGameSmoke", "RenamedFailureTest"], self.expected
            )

    def test_required_subset_can_be_explicitly_extensible(self):
        self.verifier.validate_test_names(
            self.expected + ["FutureTest"], self.expected, allow_extra=True
        )


if __name__ == "__main__":
    unittest.main()

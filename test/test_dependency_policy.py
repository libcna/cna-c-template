import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PINS_SCRIPT = REPO / "tools" / "dependency_pins.py"
PIN_MODULE = REPO / "cmake" / "CnaDependencyPin.cmake"


def load_pins_module():
    spec = importlib.util.spec_from_file_location("dependency_pins_policy", PINS_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DependencyPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins = load_pins_module()

    def git(self, repository: Path, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result.stdout.strip()

    def create_checkout(
        self, root: Path, directory: str = "cna"
    ) -> tuple[Path, str]:
        checkout = root / directory
        checkout.mkdir()
        self.git(checkout, "init", "--quiet")
        self.git(checkout, "config", "user.name", "cna-c-template test")
        self.git(checkout, "config", "user.email", "test@example.invalid")
        self.git(checkout, "config", "commit.gpgsign", "false")
        (checkout / "CMakeLists.txt").write_text(
            "cmake_minimum_required(VERSION 3.23)\n"
        )
        self.git(checkout, "add", "CMakeLists.txt")
        self.git(checkout, "commit", "--quiet", "-m", "fixture")
        return checkout, self.git(checkout, "rev-parse", "HEAD")

    def write_lock(
        self,
        root: Path,
        revision: str,
        dependency: str = "CNA",
        directory: str = "cna",
    ) -> Path:
        lock = root / "dependencies.lock"
        lock.write_text(
            f"{dependency}|example/{directory}|{directory}|{revision}\n"
        )
        return lock

    def run_cmake_policy(
        self,
        root: Path,
        checkout: Path,
        lock: Path,
        allow_unpinned: bool,
        dependency: str = "CNA",
    ) -> subprocess.CompletedProcess[str]:
        script = root / ("allow.cmake" if allow_unpinned else "strict.cmake")
        script.write_text(
            f'set(CNA_TEMPLATE_TEST_DEPENDENCY_LOCK "{lock}")\n'
            f'include("{PIN_MODULE}")\n'
            "cna_template_verify_dependency_checkout("
            f'{dependency} "{checkout}" '
            f'{"TRUE" if allow_unpinned else "FALSE"})\n'
        )
        return subprocess.run(
            ["cmake", "-P", str(script)],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_pin_tool_accepts_correct_checkout_and_rejects_wrong_or_dirty(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout, revision = self.create_checkout(root)
            pin = self.pins.DependencyPin("CNA", "example/cna", "cna", revision)
            self.assertEqual([], self.pins.verify_checkout(pin, root))

            wrong = pin._replace(revision="0" * 40)
            self.assertRegex(
                "\n".join(self.pins.verify_checkout(wrong, root)), "expected 0{40}"
            )

            (checkout / "untracked.txt").write_text("drift\n")
            self.assertIn(
                "not clean", "\n".join(self.pins.verify_checkout(pin, root))
            )

    def test_pin_tool_reports_source_archive_without_git_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "cna"
            source.mkdir()
            pin = self.pins.DependencyPin("CNA", "example/cna", "cna", "0" * 40)
            problem = "\n".join(self.pins.verify_checkout(pin, root))
            self.assertIn("has no .git metadata", problem)
            self.assertIn("cannot be verified", problem)

    def test_cmake_policy_enforces_pin_and_allows_explicit_compatibility_test(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout, revision = self.create_checkout(root)
            correct_lock = self.write_lock(root, revision)
            correct = self.run_cmake_policy(root, checkout, correct_lock, False)
            self.assertEqual(0, correct.returncode, correct.stdout + correct.stderr)
            self.assertIn("matches dependencies.lock", correct.stdout + correct.stderr)

            wrong_lock = self.write_lock(root, "0" * 40)
            rejected = self.run_cmake_policy(root, checkout, wrong_lock, False)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("checkout drift", rejected.stdout + rejected.stderr)
            self.assertIn("CNA_ALLOW_UNPINNED=ON", rejected.stdout + rejected.stderr)

            acknowledged = self.run_cmake_policy(root, checkout, wrong_lock, True)
            self.assertEqual(
                0, acknowledged.returncode, acknowledged.stdout + acknowledged.stderr
            )
            self.assertIn(
                "intentional unpinned", acknowledged.stdout + acknowledged.stderr
            )

    def test_cmake_policy_supports_unverifiable_source_archive_with_warning(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "cna-archive"
            source.mkdir()
            lock = self.write_lock(root, "0" * 40)
            result = self.run_cmake_policy(root, source, lock, False)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("has no .git metadata", result.stdout + result.stderr)
            self.assertIn("verified pinned checkout", result.stdout + result.stderr)

    def test_cmake_policy_is_applied_to_sharp_runtime_not_only_cna(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout, revision = self.create_checkout(root, "sharp-runtime")
            lock = self.write_lock(root, revision, "SHARP_RUNTIME", "sharp-runtime")
            accepted = self.run_cmake_policy(
                root, checkout, lock, False, "SHARP_RUNTIME"
            )
            self.assertEqual(
                0, accepted.returncode, accepted.stdout + accepted.stderr
            )
            self.assertIn(
                "SHARP_RUNTIME matches dependencies.lock",
                accepted.stdout + accepted.stderr,
            )

            (checkout / "drift.txt").write_text("drift\n")
            rejected = self.run_cmake_policy(
                root, checkout, lock, False, "SHARP_RUNTIME"
            )
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn(
                "SHARP_RUNTIME checkout drift", rejected.stdout + rejected.stderr
            )

    def test_ordinary_build_wires_all_direct_consumed_pins(self):
        cmake = (REPO / "CMakeLists.txt").read_text()
        gradle = (REPO / "android" / "app" / "build.gradle").read_text()
        self.assertIn('SHARP_RUNTIME "${CNA_SHARP_RUNTIME_ROOT}"', cmake)
        for dependency, target in (
            ("EASY_GL", "easy-gl"),
            ("META_GL", "meta-gl"),
        ):
            self.assertIn(
                f"{dependency} {target} \"${{CNA_ALLOW_UNPINNED}}\"", cmake
            )
        self.assertIn(
            'verifyPinnedCheckout("SHARP_RUNTIME", cnaSharpRuntimeRootDir)',
            gradle,
        )
        self.assertIn(
            'rendererDependencyNames.addAll(["EASY_GL", "META_GL"])', gradle
        )


if __name__ == "__main__":
    unittest.main()

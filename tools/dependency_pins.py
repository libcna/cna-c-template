#!/usr/bin/env python3
"""Read and verify the reproducible sibling-dependency revisions."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


REPO = Path(__file__).resolve().parent.parent
LOCK_FILE = REPO / "dependencies.lock"
REQUIRED_DEPENDENCIES = {
    "CNA",
    "SHARP_RUNTIME",
    "EASY_GL",
    "META_GL",
}
PIN_RE = re.compile(
    r"^([A-Z][A-Z0-9_]*)"
    r"\|([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"
    r"\|([A-Za-z0-9][A-Za-z0-9._-]*)"
    r"\|([0-9a-f]{40})$"
)


class DependencyPin(NamedTuple):
    """One complete, reproducible dependency record from dependencies.lock."""

    name: str
    repository: str
    directory: str
    revision: str

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.repository}.git"


def default_dependencies_dir(pins: dict[str, DependencyPin] | None = None) -> Path:
    """Use the same ordinary-sibling / _bindings layouts as CMake and Gradle."""
    if pins is None:
        pins = load_pins()
    cna_directory = pins["CNA"].directory
    for candidate in (REPO.parent, REPO.parent.parent):
        if (candidate / cna_directory / "CMakeLists.txt").is_file():
            return candidate
    return REPO.parent


def load_pins() -> dict[str, DependencyPin]:
    pins: dict[str, DependencyPin] = {}
    for line_number, raw_line in enumerate(LOCK_FILE.read_text().splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError(
                f"{LOCK_FILE.name}:{line_number}: expected "
                "NAME|OWNER/REPOSITORY|DIRECTORY|<40 lowercase hex digits>"
            )
        name, repository, directory, revision = match.groups()
        if name in pins:
            raise ValueError(f"{LOCK_FILE.name}:{line_number}: duplicate pin {name}")
        if directory in {".", ".."}:
            raise ValueError(
                f"{LOCK_FILE.name}:{line_number}: unsafe dependency directory {directory!r}"
            )
        pins[name] = DependencyPin(name, repository, directory, revision)

    missing = REQUIRED_DEPENDENCIES - pins.keys()
    extra = pins.keys() - REQUIRED_DEPENDENCIES
    if missing or extra:
        details = []
        if missing:
            details.append("missing " + ", ".join(sorted(missing)))
        if extra:
            details.append("unknown " + ", ".join(sorted(extra)))
        raise ValueError(f"{LOCK_FILE.name}: " + "; ".join(details))
    return pins


def git_output(repository: Path, *arguments: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip()
        raise ValueError(f"git failed for {repository}: {detail}")
    return process.stdout.strip()


def verify_checkout(pin: DependencyPin, dependencies_dir: Path) -> list[str]:
    repository = (dependencies_dir / pin.directory).resolve()
    if not (repository / ".git").exists():
        if repository.is_dir():
            return [
                f"{pin.name}: source tree at {repository} has no .git metadata; "
                "the pinned revision cannot be verified"
            ]
        return [f"{pin.name}: checkout missing at {repository}"]

    problems = []
    actual = git_output(repository, "rev-parse", "HEAD")
    if actual != pin.revision:
        problems.append(
            f"{pin.name}: expected {pin.revision}, found {actual} at {repository}"
        )
    status = git_output(repository, "status", "--porcelain", "--untracked-files=normal")
    if status:
        problems.append(f"{pin.name}: checkout is not clean at {repository}")
    return problems


def main() -> int:
    try:
        pins = load_pins()
        parser = argparse.ArgumentParser(description=__doc__)
        actions = parser.add_mutually_exclusive_group()
        actions.add_argument("--revision", metavar="NAME", help="print one pinned revision")
        actions.add_argument(
            "--repository", metavar="NAME", help="print one OWNER/REPOSITORY identifier"
        )
        actions.add_argument("--url", metavar="NAME", help="print one clone URL")
        actions.add_argument(
            "--directory", metavar="NAME", help="print one local checkout directory"
        )
        actions.add_argument(
            "--check",
            nargs="+",
            metavar="NAME",
            help="verify named sibling checkouts against their revisions and cleanliness",
        )
        parser.add_argument(
            "--dependencies-dir",
            type=Path,
            default=default_dependencies_dir(pins),
            help=(
                "directory containing dependency checkouts (default: ../ or ../../, "
                "whichever contains CNA)"
            ),
        )
        args = parser.parse_args()

        query_name = args.revision or args.repository or args.url or args.directory
        requested = [query_name] if query_name else (args.check or [])
        unknown = [name for name in requested if name not in pins]
        if unknown:
            parser.error(
                "unknown dependency name(s): "
                + ", ".join(unknown)
                + "; expected "
                + ", ".join(pins)
            )

        if args.revision:
            print(pins[args.revision].revision)
            return 0
        if args.repository:
            print(pins[args.repository].repository)
            return 0
        if args.url:
            print(pins[args.url].clone_url)
            return 0
        if args.directory:
            print(pins[args.directory].directory)
            return 0

        if args.check:
            dependencies_dir = args.dependencies_dir.resolve()
            problems = []
            for name in args.check:
                problems.extend(verify_checkout(pins[name], dependencies_dir))
            if problems:
                for problem in problems:
                    print(f"error: {problem}", file=sys.stderr)
                return 1
            print(
                "ok: dependency checkout(s) match dependencies.lock: "
                + ", ".join(args.check)
            )
            return 0

        print(f"ok: {len(pins)} valid dependency pins in {LOCK_FILE.name}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

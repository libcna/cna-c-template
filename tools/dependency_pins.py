#!/usr/bin/env python3
"""Read and verify the reproducible sibling-dependency revisions."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
LOCK_FILE = REPO / "dependencies.lock"
DEPENDENCY_DIRECTORIES = {
    "CNA": "cna",
    "SHARP_RUNTIME": "sharp-runtime",
    "EASY_GL": "easy-gl",
    "META_GL": "meta-gl",
    "FREE_DIRECT": "free-direct",
}
PIN_RE = re.compile(r"^([A-Z][A-Z0-9_]*)=([0-9a-f]{40})$")


def default_dependencies_dir() -> Path:
    """Use the same ordinary-sibling / _bindings layouts as CMake and Gradle."""
    for candidate in (REPO.parent, REPO.parent.parent):
        if (candidate / "cna" / "CMakeLists.txt").is_file():
            return candidate
    return REPO.parent


def load_pins() -> dict[str, str]:
    pins: dict[str, str] = {}
    for line_number, raw_line in enumerate(LOCK_FILE.read_text().splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError(
                f"{LOCK_FILE.name}:{line_number}: expected NAME=<40 lowercase hex digits>"
            )
        name, revision = match.groups()
        if name in pins:
            raise ValueError(f"{LOCK_FILE.name}:{line_number}: duplicate pin {name}")
        pins[name] = revision

    missing = DEPENDENCY_DIRECTORIES.keys() - pins.keys()
    extra = pins.keys() - DEPENDENCY_DIRECTORIES.keys()
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


def verify_checkout(name: str, revision: str, dependencies_dir: Path) -> list[str]:
    repository = dependencies_dir / DEPENDENCY_DIRECTORIES[name]
    if not (repository / ".git").exists():
        return [f"{name}: checkout missing at {repository}"]

    problems = []
    actual = git_output(repository, "rev-parse", "HEAD")
    if actual != revision:
        problems.append(f"{name}: expected {revision}, found {actual} at {repository}")
    status = git_output(repository, "status", "--porcelain", "--untracked-files=normal")
    if status:
        problems.append(f"{name}: checkout is not clean at {repository}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--revision", metavar="NAME", help="print one pinned revision")
    actions.add_argument(
        "--check",
        nargs="+",
        metavar="NAME",
        help="verify named sibling checkouts against their revisions and cleanliness",
    )
    parser.add_argument(
        "--dependencies-dir",
        type=Path,
        default=default_dependencies_dir(),
        help=(
            "directory containing dependency checkouts (default: ../ or ../../, "
            "whichever contains CNA)"
        ),
    )
    args = parser.parse_args()

    try:
        pins = load_pins()
        requested = [args.revision] if args.revision else (args.check or [])
        unknown = [name for name in requested if name not in pins]
        if unknown:
            parser.error(
                "unknown dependency name(s): "
                + ", ".join(unknown)
                + "; expected "
                + ", ".join(pins)
            )

        if args.revision:
            print(pins[args.revision])
            return 0

        if args.check:
            dependencies_dir = args.dependencies_dir.resolve()
            problems = []
            for name in args.check:
                problems.extend(verify_checkout(name, pins[name], dependencies_dir))
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

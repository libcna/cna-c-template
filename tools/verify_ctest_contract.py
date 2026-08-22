#!/usr/bin/env python3
"""Verify machine-readable CTest discovery against an expected test contract."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def validate_test_names(
    discovered: list[str], expected: list[str], allow_extra: bool = False
) -> None:
    if len(discovered) != len(set(discovered)):
        raise ValueError("CTest discovery contains duplicate test names")
    if len(expected) != len(set(expected)):
        raise ValueError("expected CTest contract contains duplicate test names")

    discovered_set = set(discovered)
    expected_set = set(expected)
    missing = sorted(expected_set - discovered_set)
    unexpected = sorted(discovered_set - expected_set)
    problems = []
    if not discovered:
        problems.append("CTest discovered zero tests")
    if missing:
        problems.append("missing expected test(s): " + ", ".join(missing))
    if unexpected and not allow_extra:
        problems.append("unexpected test(s): " + ", ".join(unexpected))
    if problems:
        raise ValueError("; ".join(problems))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-dir", type=Path, required=True)
    parser.add_argument("--expect", nargs="+", required=True, metavar="TEST_NAME")
    parser.add_argument(
        "--allow-extra",
        action="store_true",
        help="require the named subset while allowing additional discovered tests",
    )
    args = parser.parse_args()

    try:
        process = subprocess.run(
            [
                "ctest",
                "--test-dir",
                str(args.test_dir),
                "--show-only=json-v1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if process.returncode != 0:
            detail = process.stderr.strip() or process.stdout.strip()
            raise ValueError(f"CTest discovery failed: {detail}")
        document = json.loads(process.stdout)
        tests = document.get("tests")
        if not isinstance(tests, list):
            raise ValueError("CTest JSON has no 'tests' array")
        names = []
        for index, test in enumerate(tests):
            if not isinstance(test, dict) or not isinstance(test.get("name"), str):
                raise ValueError(f"CTest JSON test entry {index} has no string name")
            names.append(test["name"])
        validate_test_names(names, args.expect, args.allow_extra)
        print(f"ok: discovered {len(names)} CTest(s): " + ", ".join(names))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

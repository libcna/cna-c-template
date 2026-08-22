#!/usr/bin/env python3
"""Verify machine-readable CTest discovery and command wiring."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Union


REPO = Path(__file__).resolve().parents[1]
EXPECTED_TESTS = ["CnaCTemplateSmoke", "CnaCTemplateFailurePropagation"]
FAILURE_WRAPPER = REPO / "cmake" / "VerifyFailurePropagation.cmake"


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


def read_configured_app_name(test_dir: Path) -> str:
    cache = test_dir / "CMakeCache.txt"
    try:
        lines = cache.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(
            f"cannot read configured application name from {cache}: {exc}"
        ) from exc

    prefix = "CNA_TEMPLATE_APP_NAME:STRING="
    values = [line[len(prefix) :] for line in lines if line.startswith(prefix)]
    if len(values) != 1 or not values[0]:
        raise ValueError(
            f"expected one non-empty CNA_TEMPLATE_APP_NAME:STRING entry in {cache}"
        )
    return values[0]


def extract_test_commands(document: object) -> dict[str, list[str]]:
    if not isinstance(document, dict):
        raise ValueError("CTest JSON root is not an object")
    tests = document.get("tests")
    if not isinstance(tests, list):
        raise ValueError("CTest JSON has no 'tests' array")

    commands: dict[str, list[str]] = {}
    for index, test in enumerate(tests):
        if not isinstance(test, dict) or not isinstance(test.get("name"), str):
            raise ValueError(f"CTest JSON test entry {index} has no string name")
        command = test.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(argument, str) for argument in command)
        ):
            raise ValueError(
                f"CTest JSON test entry {index} ({test['name']}) has no string command array"
            )
        if test["name"] in commands:
            raise ValueError(
                f"CTest discovery contains duplicate test name {test['name']}"
            )
        commands[test["name"]] = command
    return commands


def _path_key(value: Union[str, Path]) -> str:
    return os.path.normcase(str(Path(value).resolve()))


def _application_basename(executable: str) -> str:
    name = Path(executable).name
    return name[:-4] if name.lower().endswith(".exe") else name


def validate_test_commands(commands: dict[str, list[str]], app_name: str) -> None:
    smoke = commands.get("CnaCTemplateSmoke")
    failure = commands.get("CnaCTemplateFailurePropagation")
    if smoke is None or failure is None:
        # Identity validation produces the more complete missing-test diagnostic.
        return

    if len(smoke) != 2 or smoke[1] != "--smoke-test":
        raise ValueError(
            "CnaCTemplateSmoke must run only the configured executable with --smoke-test"
        )
    if _application_basename(smoke[0]) != app_name:
        raise ValueError(
            "CnaCTemplateSmoke command does not run configured application "
            f"{app_name!r}: {smoke!r}"
        )

    if len(failure) != 5:
        raise ValueError(
            "CnaCTemplateFailurePropagation must invoke the dedicated CMake wrapper"
        )
    if Path(failure[0]).name.lower() not in {"cmake", "cmake.exe"}:
        raise ValueError(
            "CnaCTemplateFailurePropagation command does not invoke CMake"
        )

    executable_prefix = "-DTEST_EXECUTABLE="
    working_directory_prefix = "-DTEST_WORKING_DIRECTORY="
    if not failure[1].startswith(executable_prefix):
        raise ValueError(
            "CnaCTemplateFailurePropagation command has no TEST_EXECUTABLE assignment"
        )
    if not failure[2].startswith(working_directory_prefix):
        raise ValueError(
            "CnaCTemplateFailurePropagation command has no TEST_WORKING_DIRECTORY assignment"
        )
    if failure[3] != "-P":
        raise ValueError(
            "CnaCTemplateFailurePropagation command does not use CMake script mode"
        )

    failure_executable = failure[1][len(executable_prefix) :]
    failure_working_directory = failure[2][len(working_directory_prefix) :]
    if _path_key(failure_executable) != _path_key(smoke[0]):
        raise ValueError(
            "CnaCTemplateFailurePropagation does not inject failure into the same "
            "configured executable as CnaCTemplateSmoke"
        )
    if _path_key(failure_working_directory) != _path_key(Path(smoke[0]).parent):
        raise ValueError(
            "CnaCTemplateFailurePropagation has the wrong executable working directory"
        )
    if _path_key(failure[4]) != _path_key(FAILURE_WRAPPER):
        raise ValueError(
            "CnaCTemplateFailurePropagation is not wired to "
            "cmake/VerifyFailurePropagation.cmake"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-dir", type=Path, required=True)
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
        commands = extract_test_commands(document)
        names = list(commands)
        validate_test_names(names, EXPECTED_TESTS, args.allow_extra)
        app_name = read_configured_app_name(args.test_dir)
        validate_test_commands(commands, app_name)
        print(
            f"ok: discovered and verified {len(names)} CTest(s) for {app_name}: "
            + ", ".join(names)
        )
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

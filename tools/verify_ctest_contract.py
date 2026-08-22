#!/usr/bin/env python3
"""Verify machine-readable CTest discovery and command wiring."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Optional, Union


REPO = Path(__file__).resolve().parents[1]
EXPECTED_TESTS = ["CnaCTemplateSmoke", "CnaCTemplateFailurePropagation"]
FAILURE_WRAPPER = REPO / "cmake" / "VerifyFailurePropagation.cmake"


class DiscoveredTest(NamedTuple):
    command: list[str]
    properties: dict[str, object]


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


def read_cmake_cache(test_dir: Path) -> dict[str, str]:
    cache = test_dir / "CMakeCache.txt"
    try:
        lines = cache.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read CMake cache {cache}: {exc}") from exc

    entries: dict[str, str] = {}
    for line in lines:
        if not line or line.startswith(("#", "//")) or ":" not in line:
            continue
        name_and_type, separator, value = line.partition("=")
        if not separator:
            continue
        name, separator, _cache_type = name_and_type.partition(":")
        if not separator:
            continue
        if name in entries:
            raise ValueError(f"duplicate CMake cache entry {name!r} in {cache}")
        entries[name] = value
    return entries


def read_configured_app_name(test_dir: Path) -> str:
    cache = test_dir / "CMakeCache.txt"
    value = read_cmake_cache(test_dir).get("CNA_TEMPLATE_APP_NAME")
    if not value:
        raise ValueError(
            f"expected one non-empty CNA_TEMPLATE_APP_NAME:STRING entry in {cache}"
        )
    return value


def resolve_ctest_configuration(
    test_dir: Path, requested: Optional[str]
) -> Optional[str]:
    cache = read_cmake_cache(test_dir)
    generator = cache.get("CMAKE_GENERATOR", "unknown generator")
    available = tuple(
        configuration
        for configuration in cache.get("CMAKE_CONFIGURATION_TYPES", "").split(";")
        if configuration
    )
    if not available:
        return requested
    if requested is None:
        raise ValueError(
            f"build tree uses multi-config generator {generator!r}; pass --config "
            f"<name> (available: {', '.join(available)})"
        )
    if requested not in available:
        raise ValueError(
            f"configuration {requested!r} is not available in multi-config build "
            f"tree {test_dir} (available: {', '.join(available)})"
        )
    return requested


def ctest_discovery_command(
    test_dir: Path, configuration: Optional[str]
) -> list[str]:
    command = ["ctest", "--test-dir", str(test_dir)]
    if configuration is not None:
        command.extend(["-C", configuration])
    command.append("--show-only=json-v1")
    return command


def extract_tests(document: object) -> dict[str, DiscoveredTest]:
    if not isinstance(document, dict):
        raise ValueError("CTest JSON root is not an object")
    tests = document.get("tests")
    if not isinstance(tests, list):
        raise ValueError("CTest JSON has no 'tests' array")

    discovered: dict[str, DiscoveredTest] = {}
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
        properties_document = test.get("properties")
        if not isinstance(properties_document, list):
            raise ValueError(
                f"CTest JSON test entry {index} ({test['name']}) has no properties array"
            )
        properties: dict[str, object] = {}
        for property_index, property_document in enumerate(properties_document):
            if (
                not isinstance(property_document, dict)
                or not isinstance(property_document.get("name"), str)
                or "value" not in property_document
            ):
                raise ValueError(
                    f"CTest JSON property {property_index} for {test['name']} is malformed"
                )
            property_name = property_document["name"]
            if property_name in properties:
                raise ValueError(
                    f"CTest JSON test {test['name']} has duplicate property "
                    f"{property_name!r}"
                )
            properties[property_name] = property_document["value"]

        if test["name"] in discovered:
            raise ValueError(
                f"CTest discovery contains duplicate test name {test['name']}"
            )
        discovered[test["name"]] = DiscoveredTest(command, properties)
    return discovered


def _path_key(value: Union[str, Path]) -> str:
    return os.path.normcase(str(Path(value).resolve()))


def _application_basename(executable: str) -> str:
    name = Path(executable).name
    return name[:-4] if name.lower().endswith(".exe") else name


def validate_test_contract(tests: dict[str, DiscoveredTest], app_name: str) -> None:
    smoke_test = tests.get("CnaCTemplateSmoke")
    failure_test = tests.get("CnaCTemplateFailurePropagation")
    if smoke_test is None or failure_test is None:
        # Identity validation produces the more complete missing-test diagnostic.
        return

    smoke = smoke_test.command
    failure = failure_test.command
    if len(smoke) != 2 or smoke[1] != "--smoke-test":
        raise ValueError(
            "CnaCTemplateSmoke must run only the configured executable with --smoke-test"
        )
    if _application_basename(smoke[0]) != app_name:
        raise ValueError(
            "CnaCTemplateSmoke command does not run configured application "
            f"{app_name!r}: {smoke!r}"
        )

    smoke_working_directory = smoke_test.properties.get("WORKING_DIRECTORY")
    if not isinstance(smoke_working_directory, str) or not smoke_working_directory:
        raise ValueError(
            "CnaCTemplateSmoke has no string WORKING_DIRECTORY property"
        )
    if _path_key(smoke_working_directory) != _path_key(Path(smoke[0]).parent):
        raise ValueError(
            "CnaCTemplateSmoke WORKING_DIRECTORY is not the configured executable "
            f"directory: {smoke_working_directory!r}"
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
        "--config",
        help=(
            "CTest configuration to inspect (required for multi-config build trees, "
            "for example Debug)"
        ),
    )
    parser.add_argument(
        "--allow-extra",
        action="store_true",
        help="require the named subset while allowing additional discovered tests",
    )
    args = parser.parse_args()

    try:
        configuration = resolve_ctest_configuration(args.test_dir, args.config)
        process = subprocess.run(
            ctest_discovery_command(args.test_dir, configuration),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if process.returncode != 0:
            detail = process.stderr.strip() or process.stdout.strip()
            raise ValueError(f"CTest discovery failed: {detail}")
        document = json.loads(process.stdout)
        tests = extract_tests(document)
        names = list(tests)
        validate_test_names(names, EXPECTED_TESTS, args.allow_extra)
        app_name = read_configured_app_name(args.test_dir)
        validate_test_contract(tests, app_name)
        configuration_text = (
            f" in configuration {configuration}" if configuration is not None else ""
        )
        print(
            f"ok: discovered and verified {len(names)} CTest(s) for {app_name}"
            f"{configuration_text}: "
            + ", ".join(names)
        )
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

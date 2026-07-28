#!/usr/bin/env python3
"""Verify that a GitHub release tag matches the Python package prerelease."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expected_tag(package_version: str) -> str:
    match = re.fullmatch(r"(\d+\.\d+\.\d+)a(\d+)", package_version)
    if match is None:
        raise ValueError(f"unsupported package prerelease version: {package_version}")
    return f"v{match.group(1)}-alpha.{match.group(2)}"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check-release-tag.py <git-tag>", file=sys.stderr)
        return 2

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package_version = pyproject["project"]["version"]
    required_tag = expected_tag(package_version)
    actual_tag = sys.argv[1]

    if actual_tag != required_tag:
        print(
            f"release tag {actual_tag!r} does not match package version "
            f"{package_version!r}; expected {required_tag!r}",
            file=sys.stderr,
        )
        return 1

    print(f"release tag {actual_tag} matches package version {package_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

import public_source_extractor


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_VERSION = "0.1.0a2"
TAG_VERSION = "v0.1.0-alpha.2"


class ReleaseMetadataTests(unittest.TestCase):
    def test_python_versions_match(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["version"], PACKAGE_VERSION)
        self.assertEqual(public_source_extractor.__version__, PACKAGE_VERSION)

    def test_tag_mapping_is_documented(self) -> None:
        release_notes = (ROOT / "docs/releases/v0.1.0-alpha.2.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(PACKAGE_VERSION, release_notes)
        self.assertIn(TAG_VERSION, release_notes)
        self.assertNotIn("release candidate", release_notes.lower())
        self.assertNotIn("tag candidate", release_notes.lower())

    def test_readme_install_identifies_package_and_tag_versions(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        tag_pattern = re.escape(f"public-source-extractor.git@{TAG_VERSION}")
        package_pattern = re.escape(f"public-source-extractor@{PACKAGE_VERSION}")
        self.assertGreaterEqual(len(re.findall(tag_pattern, readme)), 1)
        self.assertGreaterEqual(len(re.findall(package_pattern, readme)), 1)
        self.assertNotIn("release candidate", readme.lower())
        self.assertNotIn("tag does not exist", readme.lower())
        self.assertNotIn("after the approved", readme.lower())

    def test_pypi_publish_workflow_uses_trusted_publishing(self) -> None:
        workflow = (ROOT / ".github/workflows/publish-pypi.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("id-token: write", workflow)
        self.assertIn("environment:", workflow)
        self.assertIn("name: pypi", workflow)
        self.assertIn("pypa/gh-action-pypi-publish@release/v1", workflow)
        self.assertNotRegex(workflow, re.compile(r"PYPI_(?:TOKEN|PASSWORD)|password:"))


if __name__ == "__main__":
    unittest.main()

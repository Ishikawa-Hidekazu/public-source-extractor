from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

import public_source_extractor


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_VERSION = "0.1.0a1"
TAG_VERSION = "v0.1.0-alpha.1"


class ReleaseMetadataTests(unittest.TestCase):
    def test_python_versions_match(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["version"], PACKAGE_VERSION)
        self.assertEqual(public_source_extractor.__version__, PACKAGE_VERSION)

    def test_tag_mapping_is_documented(self) -> None:
        release_notes = (ROOT / "docs/releases/v0.1.0-alpha.1.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(PACKAGE_VERSION, release_notes)
        self.assertIn(TAG_VERSION, release_notes)
        self.assertNotIn("release candidate", release_notes.lower())
        self.assertNotIn("tag candidate", release_notes.lower())

    def test_readme_install_is_pinned_to_release_tag(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        pattern = re.escape(f"public-source-extractor.git@{TAG_VERSION}")
        self.assertGreaterEqual(len(re.findall(pattern, readme)), 2)
        self.assertNotIn("release candidate", readme.lower())
        self.assertNotIn("tag does not exist", readme.lower())
        self.assertNotIn("after the approved", readme.lower())


if __name__ == "__main__":
    unittest.main()

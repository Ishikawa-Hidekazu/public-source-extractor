from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

import public_source_extractor


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_VERSION = "0.1.0"
TAG_VERSION = "v0.1.0"


class ReleaseMetadataTests(unittest.TestCase):
    def test_codex_plugin_marketplace_and_manifest_match(self) -> None:
        marketplace = json.loads(
            (ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (
                ROOT
                / "plugins/public-source-extractor/.codex-plugin/plugin.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["name"], "ishikawa-public-tools")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], manifest["name"])
        self.assertEqual(
            entry["source"]["path"], "./plugins/public-source-extractor"
        )
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(
            manifest["repository"],
            "https://github.com/Ishikawa-Hidekazu/public-source-extractor",
        )

    def test_codex_plugin_skill_keeps_the_public_only_boundary(self) -> None:
        skill = (
            ROOT
            / "plugins/public-source-extractor/skills/public-source-extractor/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Firecrawl Cloud", skill)
        self.assertIn("untrusted source material", skill)
        self.assertIn("private, authenticated, signed", skill)
        self.assertIn("public-source-extractor==0.1.0a2", skill)
        self.assertIn("Until stable `0.1.0` is publicly verified", skill)

    def test_python_versions_match(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["version"], PACKAGE_VERSION)
        self.assertEqual(public_source_extractor.__version__, PACKAGE_VERSION)

    def test_package_homepage_points_to_the_product_article(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(
            pyproject["project"]["urls"]["Homepage"],
            "https://taupe.site/entry/public-source-extractor-ai-research-cli/",
        )

    def test_tag_mapping_is_documented(self) -> None:
        release_notes = (ROOT / "docs/releases/v0.1.0.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(PACKAGE_VERSION, release_notes)
        self.assertIn(TAG_VERSION, release_notes)
        self.assertNotIn("release candidate", release_notes.lower())
        self.assertNotIn("tag candidate", release_notes.lower())

    def test_repository_readme_keeps_verified_distribution_until_release(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("public-source-extractor@0.1.0a2", readme)
        self.assertIn("public-source-extractor.git@v0.1.0-alpha.2", readme)
        self.assertIn("release candidate and is not published yet", readme)

    def test_package_index_readme_identifies_stable_package_version(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        readme_config = pyproject["project"]["readme"]
        self.assertEqual(readme_config["file"], "docs/pypi-readme.md")
        pypi_readme = (ROOT / readme_config["file"]).read_text(encoding="utf-8")
        package_pattern = re.escape(f"public-source-extractor@{PACKAGE_VERSION}")
        self.assertGreaterEqual(len(re.findall(package_pattern, pypi_readme)), 1)
        self.assertIn(f"public-source-extractor=={PACKAGE_VERSION}", pypi_readme)

    def test_pypi_publish_workflow_uses_trusted_publishing(self) -> None:
        workflow = (ROOT / ".github/workflows/publish-pypi.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("id-token: write", workflow)
        self.assertIn("environment:", workflow)
        self.assertIn("name: pypi", workflow)
        self.assertRegex(
            workflow,
            re.compile(r"pypa/gh-action-pypi-publish@[0-9a-f]{40}"),
        )
        self.assertIn("scripts/check-release-tag.py", workflow)
        self.assertNotRegex(workflow, re.compile(r"PYPI_(?:TOKEN|PASSWORD)|password:"))

    def test_release_tag_check_accepts_only_matching_tag(self) -> None:
        script = ROOT / "scripts/check-release-tag.py"
        accepted = subprocess.run(
            [sys.executable, str(script), TAG_VERSION],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        rejected = subprocess.run(
            [sys.executable, str(script), "v0.1.0-alpha.99"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(rejected.returncode, 1)
        self.assertIn("does not match package version", rejected.stderr)


if __name__ == "__main__":
    unittest.main()

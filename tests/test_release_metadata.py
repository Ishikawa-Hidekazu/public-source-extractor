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
PACKAGE_VERSION = "0.1.3"
TAG_VERSION = f"v{PACKAGE_VERSION}"
PUBLISHED_VERSION = "0.1.2"


class ReleaseMetadataTests(unittest.TestCase):
    def assert_install_versions(self, text: str, expected: str) -> None:
        pins = re.findall(r"public-source-extractor(?:@|==)([0-9]+\.[0-9]+\.[0-9]+)", text)
        pins += re.findall(r"public-source-extractor\.git@v([0-9]+\.[0-9]+\.[0-9]+)", text)
        self.assertEqual(set(pins), {expected})

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
        self.assert_install_versions(skill, PUBLISHED_VERSION)
        self.assertIn("verified stable package", skill)

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
        release_notes = (ROOT / f"docs/releases/{TAG_VERSION}.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(PACKAGE_VERSION, release_notes)
        self.assertIn(TAG_VERSION, release_notes)
        self.assertIn(f"# {TAG_VERSION} Release Notes", release_notes)
        self.assertNotIn("unpublished", release_notes.lower())
        self.assertNotIn("distribution candidate", release_notes.lower())
        self.assertIn(f"published `{PUBLISHED_VERSION}`", release_notes)

    def test_changelog_identifies_the_release_and_comparison(self) -> None:
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertRegex(
            changelog,
            rf"(?m)^## \[{re.escape(PACKAGE_VERSION)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
        )
        self.assertIn(f"compare/v{PUBLISHED_VERSION}...{TAG_VERSION}", changelog)
        self.assertIn(f"compare/{TAG_VERSION}...HEAD", changelog)

    def test_repository_readme_uses_verified_stable_distribution(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assert_install_versions(readme, PUBLISHED_VERSION)
        self.assertIn(f"public-source-extractor.git@v{PUBLISHED_VERSION}", readme)
        self.assertIn(f"Stable `{PUBLISHED_VERSION}` is available", readme)
        readme_ja = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        self.assert_install_versions(readme_ja, PUBLISHED_VERSION)
        self.assertIn(f"public-source-extractor.git@v{PUBLISHED_VERSION}", readme_ja)

    def test_package_index_readme_identifies_stable_package_version(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        readme_config = pyproject["project"]["readme"]
        self.assertEqual(readme_config["file"], "docs/pypi-readme.md")
        pypi_readme = (ROOT / readme_config["file"]).read_text(encoding="utf-8")
        self.assert_install_versions(pypi_readme, PACKAGE_VERSION)
        self.assertIn(f"These examples target this release, `{PACKAGE_VERSION}`.", pypi_readme)
        self.assertNotRegex(
            pypi_readme.lower(),
            r"unpublished|distribution candidate|candidate-venv|/path/to/",
        )

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
            [sys.executable, str(script), "v0.0.0"],
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

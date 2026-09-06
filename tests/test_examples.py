from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/output-v0.1.schema.json").read_text(encoding="utf-8"))


class PublicExampleTests(unittest.TestCase):
    def test_json_example_matches_public_schema(self) -> None:
        example = json.loads((ROOT / "examples/example-report.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(SCHEMA).validate(example)
        self.assertEqual(example["source"]["requested_url"], "https://example.com/")

    def test_markdown_example_is_public_safe_and_identifies_provider(self) -> None:
        example = (ROOT / "examples/example-report.md").read_text(encoding="utf-8")
        self.assertIn('source_url: "https://example.com/"', example)
        self.assertIn('provider: "firecrawl-keyless"', example)
        self.assertIn("provider_credits_used: 5", example)
        self.assertIn("provider_elapsed_ms: 1000", example)

    def test_case_study_is_reproducible_and_keeps_review_boundary(self) -> None:
        case_study = (ROOT / "docs/case-study-github-changelog.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("public-source-extractor@0.1.0", case_study)
        self.assertIn("verified stable package", case_study)
        self.assertIn("github.blog/changelog/", case_study)
        self.assertIn("experimental_provider", case_study)
        self.assertIn("Human Review", case_study)
        self.assertIn("does not establish source", case_study)
        self.assertIn("reliability or replace review", case_study)

    def test_stable_criteria_do_not_claim_provider_stability_or_publication(self) -> None:
        criteria = (ROOT / "docs/stable-0.1.0-criteria.md").read_text(encoding="utf-8")
        self.assertIn("experimental", criteria)
        self.assertIn("No tag, GitHub Release, or PyPI upload is authorized", criteria)
        self.assertIn("Trusted Publishing", criteria)
        self.assertIn("Not Required For 0.1.0", criteria)


if __name__ == "__main__":
    unittest.main()

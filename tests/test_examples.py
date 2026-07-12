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


if __name__ == "__main__":
    unittest.main()

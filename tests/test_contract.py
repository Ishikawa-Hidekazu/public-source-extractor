from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import jsonschema

from public_source_extractor.output import build_success_envelope
from public_source_extractor.provider import ProviderResult


SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas/output-v0.1.schema.json").read_text()
)
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)


def envelope(mode: str, content: str | dict[str, object]) -> dict[str, object]:
    return build_success_envelope(
        "https://example.com/",
        mode,
        ProviderResult(
            content=content,
            resolved_url="https://example.com/",
            title="Example",
            description=None,
            content_type="text/html",
            source_http_status=200,
            provider_http_status=200,
            credits_used=1,
            elapsed_ms=100,
        ),
    )


class ContractTests(unittest.TestCase):
    def assert_valid(self, value: object) -> None:
        self.assertEqual(list(VALIDATOR.iter_errors(value)), [])

    def assert_invalid(self, value: object) -> None:
        self.assertNotEqual(list(VALIDATOR.iter_errors(value)), [])

    def test_generated_markdown_envelope_is_valid(self) -> None:
        self.assert_valid(envelope("markdown", "# Example"))

    def test_generated_json_envelope_is_valid(self) -> None:
        self.assert_valid(envelope("json", {"title": "Example"}))

    def test_rejects_mode_content_mismatches(self) -> None:
        self.assert_invalid(envelope("markdown", {"wrong": True}))
        self.assert_invalid(envelope("json", "wrong"))

    def test_provider_identifier_is_stable(self) -> None:
        value = envelope("markdown", "# Example")
        self.assertEqual(value["provider"]["name"], "firecrawl-keyless")
        self.assertEqual(value["provider"]["access"], "experimental")
        changed = copy.deepcopy(value)
        changed["provider"]["name"] = "firecrawl"
        self.assert_invalid(changed)

    def test_warns_when_redirect_metadata_is_unavailable(self) -> None:
        value = build_success_envelope(
            "https://example.com/",
            "markdown",
            ProviderResult(
                content="# Example",
                resolved_url=None,
                title="Example",
                description=None,
                content_type="text/html",
                source_http_status=200,
                provider_http_status=200,
                credits_used=1,
                elapsed_ms=100,
            ),
        )
        self.assert_valid(value)
        self.assertIn("resolved_url_unavailable", {item["code"] for item in value["warnings"]})

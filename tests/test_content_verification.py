from __future__ import annotations

import io
import json
import operator
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from public_source_extractor.cli import run
from public_source_extractor.provider import FirecrawlKeylessProvider


class PublicFixtureResponse:
    status = 200

    def __init__(self, content: str | dict[str, object], mode: str) -> None:
        self.body = json.dumps(
            {
                "success": True,
                "data": {
                    mode: content,
                    "metadata": {"sourceURL": "https://example.com/", "statusCode": 200},
                },
            }
        ).encode()

    def __enter__(self) -> PublicFixtureResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        pass

    def read(self, limit: int) -> bytes:
        return self.body[:limit]


class ContentVerificationTests(unittest.TestCase):
    def cli_result(self, content: str | dict[str, object], mode: str) -> str:
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("urllib.request.urlopen", return_value=PublicFixtureResponse(content, mode)):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = run(["https://example.com/", "--mode", mode])
        self.assertEqual(status, 0)
        self.assertEqual(stderr.getvalue(), "")
        return stdout.getvalue()

    def test_json_success_never_claims_semantic_verification(self) -> None:
        content = {"title": "Example", "summary": "Versions 8.2.35 and earlier are affected."}
        envelope = json.loads(self.cli_result(content, "json"))
        self.assertTrue(envelope["ok"])
        self.assertEqual(envelope["schema_version"], "0.1")
        self.assertEqual(envelope["content"], content)
        self.assertIn("content_unverified", {w["code"] for w in envelope["warnings"]})

    def test_markdown_has_visible_and_machine_readable_unverified_notice(self) -> None:
        content = "# Example\nAffected: 8.2.35以前\n"
        rendered = self.cli_result(content, "markdown")
        self.assertIn('content_verification: "unverified"\n', rendered)
        self.assertIn("> Content is unverified.", rendered)
        self.assertTrue(rendered.endswith(content + "\n"))

    def test_comparator_tokens_are_preserved_not_repaired_or_approved(self) -> None:
        for wording in [
            "8.2.35より前",
            "8.2.35以前",
            "before 8.2.35",
            "through 8.2.35",
            "< 8.2.35",
            "<= 8.2.35",
        ]:
            for mode in ["json", "markdown"]:
                with self.subTest(wording=wording, mode=mode):
                    content = {"summary": wording} if mode == "json" else wording
                    output = self.cli_result(content, mode)
                    if mode == "json":
                        value = json.loads(output)
                        self.assertEqual(value["content"], content)
                        self.assertIn("content_unverified", {w["code"] for w in value["warnings"]})
                    else:
                        self.assertTrue(output.endswith(wording + "\n"))
                        self.assertIn("> Content is unverified.", output)

    def test_fixed_boundary_fixture_does_not_become_a_cli_applicability_check(self) -> None:
        # Textual membership only: this is not a CVE or version-range engine.
        versions = [(8, 2, patch) for patch in (34, 35, 36)]
        boundary = (8, 2, 35)
        self.assertEqual([operator.lt(v, boundary) for v in versions], [True, False, False])
        self.assertEqual([operator.le(v, boundary) for v in versions], [True, True, False])
        original = "8.2.35より前 / before 8.2.35 / < 8.2.35"
        inaccurate = "8.2.35以前 / through 8.2.35 / <= 8.2.35"
        for summary in [original, inaccurate]:
            value = json.loads(self.cli_result({"summary": summary}, "json"))
            self.assertEqual(value["content"]["summary"], summary)
            self.assertIn("content_unverified", {w["code"] for w in value["warnings"]})
            self.assertNotIn("affected_versions", value)

    def test_missing_source_conditions_updates_and_banner_only_remain_unverified(self) -> None:
        for summary in [
            "All versions are affected.",
            "The migration is planned.",
            "Accept cookies.",
            "Example page.",
            "",
        ]:
            with self.subTest(summary=summary):
                value = json.loads(self.cli_result({"summary": summary}, "json"))
                self.assertEqual(value["content"]["summary"], summary)
                self.assertIn("content_unverified", {w["code"] for w in value["warnings"]})
                self.assertNotIn("verified_source_text", value)

    def test_provider_parser_does_not_change_comparators_or_fetch_extra_sources(self) -> None:
        content = {"summary": "8.2.35以前 / <= 8.2.35"}
        with patch(
            "urllib.request.urlopen", return_value=PublicFixtureResponse(content, "json")
        ) as get:
            result = FirecrawlKeylessProvider().extract("https://example.com/", "json", 10)
        get.assert_called_once()
        self.assertEqual(result.content, content)
        request = json.loads(get.call_args.args[0].data)
        self.assertEqual(request["formats"][0]["type"], "json")
        self.assertTrue(request["onlyMainContent"])

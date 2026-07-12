from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from public_source_extractor.cli import run
from public_source_extractor.errors import InvalidProviderResponse, ProviderFailure
from public_source_extractor.provider import ProviderResult


RESULT = ProviderResult(
    content="# Example",
    resolved_url="https://example.com/",
    title="Example",
    description=None,
    content_type="text/html",
    source_http_status=200,
    provider_http_status=200,
    credits_used=1,
    elapsed_ms=100,
)


class CliTests(unittest.TestCase):
    def assert_usage_error(self, argv: list[str]) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = run(argv)
        self.assertEqual(code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "input_rejected")
        self.assertNotIn("usage:", stderr.getvalue())

    def test_missing_url_is_stable_json(self) -> None:
        self.assert_usage_error([])

    def test_invalid_mode_is_stable_json(self) -> None:
        self.assert_usage_error(["https://example.com/", "--mode", "html"])

    def test_unknown_option_is_stable_json(self) -> None:
        self.assert_usage_error(["https://example.com/", "--unknown"])

    def test_rejected_input_uses_stderr_and_exit_2(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = run(["http://127.0.0.1/"])
        self.assertEqual(code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "input_rejected")

    def test_provider_failure_uses_stderr_and_exit_3(self) -> None:
        with patch(
            "public_source_extractor.provider.FirecrawlKeylessProvider.extract",
            side_effect=ProviderFailure(),
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = run(["https://example.com/"])
        self.assertEqual(code, 3)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "provider_failure")

    def test_output_file_keeps_stdout_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.md"
            with patch(
                "public_source_extractor.provider.FirecrawlKeylessProvider.extract",
                return_value=RESULT,
            ):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = run(["https://example.com/", "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("# Example", output.read_text())

    def test_invalid_provider_response_uses_exit_4(self) -> None:
        with patch(
            "public_source_extractor.provider.FirecrawlKeylessProvider.extract",
            side_effect=InvalidProviderResponse(),
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = run(["https://example.com/"])
        self.assertEqual(code, 4)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(
            json.loads(stderr.getvalue())["error"]["code"], "invalid_provider_response"
        )

    def test_existing_output_uses_exit_5_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.md"
            output.write_text("original\n")
            with patch(
                "public_source_extractor.provider.FirecrawlKeylessProvider.extract",
                return_value=RESULT,
            ):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = run(["https://example.com/", "--output", str(output)])
            self.assertEqual(code, 5)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(output.read_text(), "original\n")

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

    def test_existing_output_is_rejected_before_provider_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.md"
            output.write_text("original\n")
            with patch("public_source_extractor.cli.FirecrawlKeylessProvider") as provider:
                provider.return_value.extract.side_effect = ProviderFailure()
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = run(["https://example.com/", "--output", str(output)])
            self.assertEqual(code, 5)
            self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "output_failure")
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(output.read_text(), "original\n")
            provider.assert_not_called()

    def test_invalid_output_paths_never_construct_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / "existing.md"
            existing.write_text("original\n")
            folder = root / "folder"
            folder.mkdir()
            linked_file = root / "linked.md"
            linked_file.symlink_to(existing)
            dangling = root / "dangling.md"
            dangling.symlink_to(root / "absent.md")
            linked_parent = root / "linked-folder"
            linked_parent.symlink_to(folder, target_is_directory=True)
            (folder / "nested").mkdir()
            paths = [
                existing,
                folder,
                linked_file,
                dangling,
                root / "missing" / "report.md",
                existing / "report.md",
                linked_parent / "report.md",
                linked_parent / "nested" / "report.md",
            ]
            for output in paths:
                with self.subTest(output=output.name):
                    with patch("public_source_extractor.cli.FirecrawlKeylessProvider") as provider:
                        stdout = io.StringIO()
                        stderr = io.StringIO()
                        with redirect_stdout(stdout), redirect_stderr(stderr):
                            code = run(["https://example.com/", "--output", str(output)])
                    self.assertEqual(code, 5)
                    self.assertEqual(stdout.getvalue(), "")
                    self.assertEqual(stderr.getvalue().count("\n"), 1)
                    self.assertEqual(
                        json.loads(stderr.getvalue())["error"]["code"], "output_failure"
                    )
                    self.assertNotIn(str(root), stderr.getvalue())
                    provider.assert_not_called()
            self.assertEqual(existing.read_text(), "original\n")
            self.assertFalse((folder / "report.md").exists())
            self.assertFalse((folder / "nested" / "report.md").exists())

    def test_output_appearing_during_extraction_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.md"

            def extract(*_args: object) -> ProviderResult:
                output.write_text("created while extracting\n")
                return RESULT

            with patch(
                "public_source_extractor.provider.FirecrawlKeylessProvider.extract",
                side_effect=extract,
            ) as provider:
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = run(["https://example.com/", "--output", str(output)])
            self.assertEqual(code, 5)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "output_failure")
            self.assertEqual(output.read_text(), "created while extracting\n")
            provider.assert_called_once()

    def test_parent_replaced_by_symlink_during_extraction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "parent"
            parent.mkdir()
            other = root / "other"
            other.mkdir()
            output = parent / "report.md"

            def extract(*_args: object) -> ProviderResult:
                parent.rmdir()
                parent.symlink_to(other, target_is_directory=True)
                return RESULT

            with patch(
                "public_source_extractor.provider.FirecrawlKeylessProvider.extract",
                side_effect=extract,
            ) as provider:
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = run(["https://example.com/", "--output", str(output)])
            self.assertEqual(code, 5)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "output_failure")
            self.assertEqual(list(other.iterdir()), [])
            provider.assert_called_once()

    def test_provider_failure_does_not_reserve_valid_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "report.md"
            with patch(
                "public_source_extractor.provider.FirecrawlKeylessProvider.extract",
                side_effect=ProviderFailure(),
            ) as provider:
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = run(["https://example.com/", "--output", str(output)])
            self.assertEqual(code, 3)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "provider_failure")
            self.assertEqual(list(root.iterdir()), [])
            provider.assert_called_once()

    def test_url_policy_still_precedes_output_preflight(self) -> None:
        with patch("public_source_extractor.cli.validate_new_file_path") as validate_output:
            with patch("public_source_extractor.cli.FirecrawlKeylessProvider") as provider:
                self.assert_usage_error(["http://127.0.0.1/", "--output", "report.md"])
        validate_output.assert_not_called()
        provider.assert_not_called()

    def test_stdout_does_not_preflight_a_file(self) -> None:
        with patch("public_source_extractor.cli.validate_new_file_path") as validate_output:
            with patch(
                "public_source_extractor.provider.FirecrawlKeylessProvider.extract",
                return_value=RESULT,
            ) as provider:
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = run(["https://example.com/"])
        self.assertEqual(code, 0)
        self.assertIn("# Example", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")
        validate_output.assert_not_called()
        provider.assert_called_once()

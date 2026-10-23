from __future__ import annotations

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("offline_demo", ROOT / "examples/offline_demo.py")
assert SPEC is not None and SPEC.loader is not None
DEMO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DEMO)


class OfflineDemoTests(unittest.TestCase):
    def test_json_cannot_be_mistaken_for_live_success(self) -> None:
        result = json.loads(DEMO.render_demo("json"))
        self.assertTrue(result["offline_fixture"])
        self.assertFalse(result["live_extraction"])
        self.assertNotIn("ok", result)
        self.assertIn("OFFLINE FIXTURE", result["notice"])

    def test_nested_example_keeps_schema_and_original_timestamp(self) -> None:
        result = json.loads(DEMO.render_demo("json"))["example_output"]
        schema = json.loads((ROOT / "schemas/output-v0.1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(result)
        self.assertEqual(result["source"]["fetched_at"], "2026-07-12T00:00:00Z")
        self.assertEqual(result["source"]["requested_url"], "https://example.com/")

    def test_markdown_labels_preview_and_separates_live_format(self) -> None:
        result = DEMO.render_demo("markdown")
        self.assertTrue(result.startswith("> OFFLINE FIXTURE"))
        self.assertIn("not live Markdown extraction output", result)
        self.assertIn("# Example Domain", result)

    def test_both_modes_work_with_provider_and_network_disabled(self) -> None:
        with (
            patch("socket.socket", side_effect=AssertionError("network forbidden")),
            patch("socket.getaddrinfo", side_effect=AssertionError("DNS forbidden")),
            patch("urllib.request.urlopen", side_effect=AssertionError("HTTP forbidden")),
            patch("public_source_extractor.provider.FirecrawlKeylessProvider.extract",
                  side_effect=AssertionError("provider forbidden")),
        ):
            for mode in ("json", "markdown"):
                with self.subTest(mode=mode), redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(DEMO.main(["--mode", mode]), 0)
                    self.assertIn("OFFLINE FIXTURE", output.getvalue())

    def test_new_file_and_no_overwrite(self) -> None:
        with TemporaryDirectory() as directory:
            target = Path(directory) / "demo.json"
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(DEMO.main(["--output", str(target)]), 0)
                self.assertEqual(output.getvalue(), "")
            original = target.read_bytes()
            with redirect_stderr(io.StringIO()) as error:
                self.assertEqual(DEMO.main(["--output", str(target)]), 5)
                self.assertEqual(json.loads(error.getvalue())["ok"], False)
            self.assertEqual(target.read_bytes(), original)

    def test_fixture_is_not_modified(self) -> None:
        before = DEMO.FIXTURE.read_bytes()
        DEMO.render_demo("json")
        DEMO.render_demo("markdown")
        self.assertEqual(DEMO.FIXTURE.read_bytes(), before)

    def test_unknown_mode_rejected(self) -> None:
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
            DEMO.main(["--mode", "html"])
        self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

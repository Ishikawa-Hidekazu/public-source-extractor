from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from public_source_extractor import __version__


ROOT = Path(__file__).resolve().parents[1]
DOCS = ("README.md", "README.ja.md", "docs/pypi-readme.md")


class FirstUseDocsTests(unittest.TestCase):
    def saved_report_block(self, name: str) -> str:
        text = (ROOT / name).read_text(encoding="utf-8")
        blocks = re.findall(r"```bash\n(.*?)```", text, re.DOTALL)
        matches = [block for block in blocks if "python3 -m json.tool report.json" in block]
        self.assertEqual(len(matches), 1, name)
        return matches[0]

    def test_no_install_examples_keep_using_the_pinned_launcher(self) -> None:
        for name in DOCS:
            with self.subTest(document=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                blocks = re.findall(r"```bash\n(.*?)```", text, re.DOTALL)
                for block in blocks:
                    self.assertNotRegex(block, r"(?m)^public-source-extractor https://")
                block = self.saved_report_block(name)
                self.assertIn(f"uvx public-source-extractor@{__version__}", block)
                self.assertIn("--mode json --output report.json &&\n", block)
                self.assertNotIn("|", block)

    def test_local_inspection_preserves_the_whole_saved_envelope(self) -> None:
        report = json.loads((ROOT / "examples/example-report.json").read_text())
        report["warnings"].append({"code": "future_warning", "message": "Keep me."})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "json.tool", "report.json"],
                cwd=directory,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), report)

    @unittest.skipUnless(os.name == "posix", "The documented shell flow is POSIX.")
    def test_failed_extraction_does_not_read_a_stale_saved_report(self) -> None:
        for name in DOCS:
            with self.subTest(document=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "report.json").write_text('{"stale": true}\n', encoding="utf-8")
                launcher = root / "uvx"
                launcher.write_text(
                    '#!/bin/sh\nprintf \'{"ok":false,"error":{"code":'
                    '"provider_rate_limited"}}\\n\' >&2\nexit 3\n',
                    encoding="utf-8",
                )
                launcher.chmod(0o700)
                result = subprocess.run(
                    ["/bin/sh", "-c", self.saved_report_block(name)],
                    cwd=root,
                    env={"PATH": f"{root}:{Path(sys.executable).parent}:/usr/bin:/bin"},
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 3)
                self.assertEqual(result.stdout, "")
                self.assertEqual(json.loads(result.stderr)["error"]["code"],
                                 "provider_rate_limited")
                self.assertEqual((root / "report.json").read_text(), '{"stale": true}\n')


if __name__ == "__main__":
    unittest.main()

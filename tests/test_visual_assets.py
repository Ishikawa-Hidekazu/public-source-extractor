from __future__ import annotations

import re
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise AssertionError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


class VisualAssetTests(unittest.TestCase):
    def test_generated_dimensions_and_size(self) -> None:
        expected = {
            "terminal-example.png": (1200, 820),
            "terminal-example-mobile.png": (750, 1100),
            "social-preview.png": (1280, 640),
        }
        for name, dimensions in expected.items():
            path = ROOT / "assets" / name
            self.assertEqual(png_dimensions(path), dimensions)
            self.assertLessEqual(path.stat().st_size, 500_000)

    def test_sources_are_fixture_only(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "assets" / "source").glob("*.svg"))
        )
        self.assertIn("https://example.com/", combined)
        self.assertNotRegex(combined, re.compile(r"/Users/|auth\.json|ghp_|sk-|Bearer "))

    def test_readmes_reference_visual_and_alt_text(self) -> None:
        for name in ("README.md", "README.ja.md"):
            content = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("assets/source/terminal-example.svg", content)
            self.assertIn("assets/source/terminal-example-mobile.svg", content)
            self.assertRegex(content, r'<img src="[^"]+" alt="[^"]+">')
            self.assertIn('"code":"provider_rate_limited"', content)
            self.assertIn('"retryable":true', content)
            self.assertRegex(content, r"exit(?:s with)? code `3`|Exit.*`3`")
            self.assertIn("https://github.com/firecrawl/cli", content)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from public_source_extractor.errors import OutputFailure
from public_source_extractor.output import write_new_file_atomic


class OutputTests(unittest.TestCase):
    def test_writes_new_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.md"
            write_new_file_atomic(path, "hello\n")
            self.assertEqual(path.read_text(), "hello\n")

    def test_rejects_existing_file_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.md"
            path.write_text("original\n")
            with self.assertRaises(OutputFailure):
                write_new_file_atomic(path, "replacement\n")
            self.assertEqual(path.read_text(), "original\n")

    def test_rejects_symlink_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.md"
            target.write_text("original\n")
            link = root / "report.md"
            link.symlink_to(target)
            with self.assertRaises(OutputFailure):
                write_new_file_atomic(link, "replacement\n")
            self.assertEqual(target.read_text(), "original\n")

    def test_rejects_symlink_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"
            real.mkdir()
            linked = root / "linked"
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaises(OutputFailure):
                write_new_file_atomic(linked / "report.md", "hello\n")

    def test_rejects_symlink_in_deeper_ancestor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"
            (real / "sub").mkdir(parents=True)
            linked = root / "linked"
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaises(OutputFailure):
                write_new_file_atomic(linked / "sub" / "report.md", "hello\n")

    def test_rejects_missing_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OutputFailure):
                write_new_file_atomic(Path(directory) / "missing" / "report.md", "hello\n")

    def test_allows_macos_tmp_platform_alias(self) -> None:
        path = Path("/tmp/public-source-extractor-output-test.md")
        path.unlink(missing_ok=True)
        try:
            write_new_file_atomic(path, "hello\n")
            self.assertEqual(path.read_text(), "hello\n")
        finally:
            path.unlink(missing_ok=True)

    def test_allows_directory_below_macos_tmp_alias(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory) / "nested" / "report.md"
            path.parent.mkdir()
            write_new_file_atomic(path, "hello\n")
            self.assertEqual(path.read_text(), "hello\n")

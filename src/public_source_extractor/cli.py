from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .errors import ExtractorError, InputRejected
from .output import build_success_envelope, render_json, render_markdown, write_new_file_atomic
from .provider import FirecrawlKeylessProvider
from .url_policy import validate_public_url


class StableArgumentParser(argparse.ArgumentParser):
    def error(self, _message: str) -> None:
        raise InputRejected()


def build_parser() -> argparse.ArgumentParser:
    parser = StableArgumentParser(
        prog="public-source-extractor",
        description="Convert one public URL into Markdown or a stable JSON envelope.",
    )
    parser.add_argument("url", help="Public HTTP or HTTPS URL.")
    parser.add_argument("--mode", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, help="Write to a new file instead of stdout.")
    parser.add_argument("--timeout", type=int, default=60, metavar="SECONDS")
    parser.add_argument("--provider", choices=("firecrawl-keyless",), default="firecrawl-keyless")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        if not 1 <= args.timeout <= 120:
            raise InputRejected()
        validate_public_url(args.url)
        provider = FirecrawlKeylessProvider()
        result = provider.extract(args.url, args.mode, args.timeout)
        envelope = build_success_envelope(args.url, args.mode, result)
        rendered = (
            render_markdown(envelope)
            if args.mode == "markdown"
            else render_json(envelope, args.pretty)
        )
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            write_new_file_atomic(args.output, rendered)
        return 0
    except ExtractorError as exc:
        sys.stderr.write(json.dumps(exc.envelope(), ensure_ascii=False) + "\n")
        return exc.exit_code


def main() -> int:
    return run()

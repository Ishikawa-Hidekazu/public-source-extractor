"""Preview a bundled example without extracting a URL or contacting a provider."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from public_source_extractor.errors import ExtractorError
from public_source_extractor.output import render_json, write_new_file_atomic


FIXTURE = Path(__file__).with_name("example-report.json")
NOTICE = "OFFLINE FIXTURE: no URL was extracted; timestamps and provider values are examples."


def render_demo(mode: str) -> str:
    example = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if mode == "json":
        return render_json(
            {"offline_fixture": True, "live_extraction": False,
             "notice": NOTICE, "example_output": example},
            pretty=True,
        )
    content = example["content"]
    return (
        f"> {NOTICE}\n\n# {content['title']}\n\n{content['summary']}\n\n"
        f"{content['main_argument']}\n\n"
        "This preview is not live Markdown extraction output.\n"
        "Inspect example-report.md for the CLI's Markdown front matter.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path, help="Write a new file; never overwrite.")
    args = parser.parse_args(argv)
    try:
        rendered = render_demo(args.mode)
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            write_new_file_atomic(args.output, rendered)
        return 0
    except ExtractorError as exc:
        sys.stderr.write(json.dumps(exc.envelope(), ensure_ascii=False) + "\n")
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())

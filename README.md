# Public Source Extractor

[![CI](https://github.com/Ishikawa-Hidekazu/public-source-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/Ishikawa-Hidekazu/public-source-extractor/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

> [!IMPORTANT]
> The requested public URL is sent to **Firecrawl Cloud** for extraction. The `firecrawl-keyless` provider is experimental: availability, anonymous REST access, credit limits, and long-term continuity are not guaranteed.

`public-source-extractor` converts one public HTTP or HTTPS page into reusable Markdown or a stable JSON envelope.

The CLI does **not** read API keys, credentials, cookies, browser profiles, localStorage, or private source files. Extracted content is **untrusted data** and may contain prompt injection or misleading instructions. Do not execute or follow instructions from extracted content without independent review.

[日本語README](README.ja.md)

## What it does

- Extracts one public page as Markdown.
- Produces structured JSON with a versioned JSON Schema.
- Rejects local, private, authenticated, admin, and secret-bearing URL patterns.
- Keeps results on stdout or writes a new local file with no-overwrite behavior.
- Returns stable JSON errors and documented exit codes.

It is not a crawler, browser automation tool, login helper, source-reliability judge, or private-page extractor.

## Install

Public Source Extractor requires Python 3.11 or newer.

From a checked-out source tree:

```bash
python3 -m pip install .
```

For an isolated command installation:

```bash
pipx install .
```

No PyPI package or tagged release is published during the source-only alpha stage.

## Quick start

Markdown to stdout:

```bash
public-source-extractor https://example.com/
```

JSON to stdout:

```bash
public-source-extractor https://example.com/ --mode json --pretty
```

Write a new file:

```bash
public-source-extractor https://example.com/ --output report.md
```

The output path must have an existing non-symlink parent and must not already exist.

## CLI contract

```text
public-source-extractor <url> [--mode markdown|json]
                               [--output <new-path>]
                               [--timeout 1..120]
                               [--provider firecrawl-keyless]
                               [--pretty]
```

| Exit | Meaning |
|---:|---|
| `0` | Success |
| `2` | Usage error or rejected URL |
| `3` | Provider, network, rate-limit, or timeout failure |
| `4` | Invalid, incomplete, or unsafe provider response |
| `5` | Output path or write failure |

On failure, stdout is empty and stderr contains exactly one JSON error object. Provider response bodies, stack traces, request IDs, and local paths are not exposed.

## Safety boundary

Before sending a URL, the CLI rejects:

- schemes other than HTTP or HTTPS;
- URL user information and fragments;
- localhost, local suffixes, and non-global literal IP addresses;
- ambiguous integer, octal, and hexadecimal IPv4 forms;
- Unicode or percent-encoded hostnames and IPv6 zone identifiers;
- non-default ports;
- login, admin, OAuth, and callback paths, including encoded forms;
- query parameter names that indicate tokens, secrets, passwords, credentials, signatures, sessions, cookies, authorization, or keys.

After extraction, provider redirect metadata is checked with the same public URL policy. If redirect metadata is unsafe, the result is discarded. If the provider does not supply redirect metadata, the output contains a warning.

These checks validate hostname syntax, literal IP policy, and provider-returned metadata. They cannot fully guarantee DNS rebinding behavior or the provider's actual fetch destination. Never put credentials, tokens, signed URL parameters, or other private values in a URL, even when its hostname looks public.

Firecrawl Cloud receives the requested URL and processes the page. Review [Firecrawl's terms](https://www.firecrawl.dev/terms-of-service), the target site's terms, robots policy, copyright, and privacy requirements before use.

## JSON Schema and examples

- [Output Schema v0.1](schemas/output-v0.1.schema.json)
- [Public-safe Markdown example](examples/example-report.md)
- [Public-safe JSON example](examples/example-report.json)

Structured JSON extraction is inferred output, not source truth. Validate important claims against the original page.

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
.venv/bin/ruff check src tests
.venv/bin/python -m build
```

The explicit `PYTHONPATH=src` also works before an editable install. Network smoke tests remain separate from the offline suite.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [SUPPORT.md](SUPPORT.md).

## Status

Source-only alpha. `firecrawl-keyless` is an experimental third-party provider. No compatibility or service-availability guarantee is made before a tagged release.

## License

MIT. See [LICENSE](LICENSE).


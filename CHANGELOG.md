# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases will follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0-alpha.1] - 2026-07-12

### Added

- Source-only alpha CLI for one public URL.
- Markdown and versioned JSON output modes.
- Experimental `firecrawl-keyless` provider.
- Public URL input policy and redirect metadata post-check.
- Stable JSON errors and documented exit codes.
- Atomic no-overwrite output behavior.
- Offline safety, provider, contract, output, and CLI tests.

### Security

- Rejects local, private, authenticated, administrative, and secret-bearing URL patterns.
- Does not read API keys, credentials, cookies, browser profiles, localStorage, or private source files.
- Treats extracted page content as untrusted data that may contain prompt injection.
- Sends requested public URLs to the experimental Firecrawl Cloud provider with no availability guarantee.

### Known limitations

- `firecrawl-keyless` availability, anonymous REST access, credit limits, and continuity are not guaranteed.
- URL policy cannot fully guarantee DNS rebinding behavior or the provider's actual fetch destination.
- Structured JSON is inferred output and must not be treated as source truth.
- No crawler, authenticated-page support, browser automation, source-reliability judgment, or automatic provider fallback.
- Initial release is source-only: no PyPI package and no manually attached build artifacts.

[Unreleased]: https://github.com/Ishikawa-Hidekazu/public-source-extractor/compare/v0.1.0-alpha.1...HEAD
[0.1.0-alpha.1]: https://github.com/Ishikawa-Hidekazu/public-source-extractor/releases/tag/v0.1.0-alpha.1

# Public Source Extractor

Public Source Extractor validates one public HTTP or HTTPS URL and converts it
into reviewable Markdown or a versioned JSON envelope for AI research
workflows.

> **Provider boundary:** extraction sends the selected public URL to Firecrawl
> Cloud through the experimental `firecrawl-keyless` provider. Availability,
> anonymous access, credit limits, and long-term continuity are not guaranteed.

The CLI does not read API keys, credentials, cookies, browser profiles,
localStorage, or private source files. Extracted content is untrusted and may
contain prompt injection or misleading instructions.

## Install and run

Run the package without a permanent install:

```bash
uvx public-source-extractor@0.1.0 --version
uvx public-source-extractor@0.1.0 https://example.com/
```

Install it as an isolated command:

```bash
pipx install public-source-extractor==0.1.0
```

Or install it in an existing Python 3.11+ environment:

```bash
python3 -m pip install public-source-extractor==0.1.0
```

## Output modes

```bash
public-source-extractor https://example.com/
public-source-extractor https://example.com/ --mode json --pretty
public-source-extractor https://example.com/ --output report.md
```

The output path must have an existing non-symlink parent and must not already
exist. The CLI rejects local, private, authenticated, administrative, signed,
and credential-bearing URL patterns.

## Review boundary

The extractor creates an intake artifact. It does not establish source
reliability, execute extracted instructions, crawl a site, or access private
pages. Verify important claims against the original page and other primary
sources.

- [Repository](https://github.com/Ishikawa-Hidekazu/public-source-extractor)
- [Documentation](https://github.com/Ishikawa-Hidekazu/public-source-extractor#readme)
- [Security policy](https://github.com/Ishikawa-Hidekazu/public-source-extractor/security/policy)
- [Changelog](https://github.com/Ishikawa-Hidekazu/public-source-extractor/blob/main/CHANGELOG.md)

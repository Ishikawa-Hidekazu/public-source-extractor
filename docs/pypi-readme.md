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

This description belongs to the **unpublished 0.1.3 distribution candidate**.
No `v0.1.3` tag, GitHub Release or PyPI publication has been made. Test a built
wheel locally first:

```bash
python3 -m venv .candidate-venv
.candidate-venv/bin/python -m pip install /path/to/public_source_extractor-0.1.3-py3-none-any.whl
.candidate-venv/bin/public-source-extractor --version
```

The package-index commands below are for use **only after 0.1.3 publication
and independent fresh-install verification**. Until then, use the verified
published 0.1.2 installation guide in the repository README.

Run the package without a permanent install:

```bash
uvx public-source-extractor@0.1.3 --version
uvx public-source-extractor@0.1.3 https://example.com/
```

Install it as an isolated command:

```bash
pipx install public-source-extractor==0.1.3
```

Or install it in an existing Python 3.11+ environment:

```bash
python3 -m pip install public-source-extractor==0.1.3
```

## Output modes

Keep using `uvx` if you chose the no-permanent-install path. It does not add
the bare command to PATH; a previously installed command may be an older
version. Only use the bare command after a `pipx` or virtualenv installation
and a version check.

```bash
uvx public-source-extractor@0.1.3 https://example.com/
uvx public-source-extractor@0.1.3 https://example.com/ --mode json --pretty
uvx public-source-extractor@0.1.3 https://example.com/ --output report.md
```

The output path must have an existing non-symlink parent and must not already
exist. The CLI rejects local, private, authenticated, administrative, signed,
and credential-bearing URL patterns.

Save once, then inspect locally without another provider request:

```bash
uvx public-source-extractor@0.1.3 https://example.com/ \
  --mode json --output report.json &&
python3 -m json.tool report.json
```

`&&` keeps an extraction failure from being hidden by a successful downstream
pipeline. Stop and read stderr on failure. Provider failures create no output
file; an existing output path is refused before any provider call. Choose a
new name rather than deleting previous evidence. On a rate limit, stop the
current burst, wait, and use the original page if necessary; do not loop retries.

Re-run only the `python3` command to reuse the saved file. Keep `.source`
(requested/resolved URLs and fetch time), `.metadata`, `.provider`, `.warnings`
and inferred `.content` together. A local re-read is not a fresh extraction
or semantic verification. See the repository documentation for the full
error and exit-code contract.

## Review boundary

The extractor creates an intake artifact. It does not establish source
reliability, execute extracted instructions, crawl a site, or access private
pages. Verify important claims against the original page and other primary
sources.

Successful extraction is not semantic verification. Starting with `0.1.2`,
every JSON success includes `content_unverified` in `warnings`. Markdown includes
`content_verification: "unverified"` and a visible notice before provider content.
Version comparators, conditions, missing updates and source freshness still
require original-publisher review. Provider content is preserved, not silently
corrected, and existing saved artifacts are not rewritten.

- [Repository](https://github.com/Ishikawa-Hidekazu/public-source-extractor)
- [Documentation](https://github.com/Ishikawa-Hidekazu/public-source-extractor#readme)
- [Security policy](https://github.com/Ishikawa-Hidekazu/public-source-extractor/security/policy)
- [Changelog](https://github.com/Ishikawa-Hidekazu/public-source-extractor/blob/main/CHANGELOG.md)

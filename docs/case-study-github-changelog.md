# Case Study: Review One Official GitHub Changelog Page

This case study shows the narrow workflow that Public Source Extractor is
designed for: validate one public source, create a reviewable artifact, and
then compare important claims with the original page.

It is a reproducible live smoke test, not a fixture and not a provider uptime
guarantee.

## Source

- Publisher: GitHub
- Public URL: <https://github.blog/changelog/2026-08-11-per-model-token-breakdown-in-the-usage-report/>
- Reason for selection: public first-party release information with no login,
  signed query, private path, or user-specific data

The URL is sent to Firecrawl Cloud through the experimental
`firecrawl-keyless` provider.

## Reproduce The Extraction

Pin the latest verified published package so the package version is explicit.
This case study remains on `0.1.0a2` until stable `0.1.0` is publicly verified:

```bash
uvx public-source-extractor@0.1.0a2 \
  'https://github.blog/changelog/2026-08-11-per-model-token-breakdown-in-the-usage-report/' \
  --mode json --pretty > report.json
```

Inspect only the fields needed for review:

```bash
jq '{
  ok,
  source,
  title: .content.title,
  metadata,
  provider,
  warnings
}' report.json
```

## Verified Run

An isolated run on 2026-08-11 UTC returned exit code `0` and the following
contract-level evidence:

- `schema_version`: `0.1`
- requested and resolved URLs matched the public source URL
- source HTTP status: `200`
- content title identified the per-model token breakdown announcement
- provider: `firecrawl-keyless`
- provider access: `experimental`
- warning: `experimental_provider`

The provider reported five credits and the CLI measured approximately 8.6
seconds for this one run. Those values describe only that request and are not
a price, quota, latency, or availability promise.

## Human Review

The extraction summarized GitHub's new model-level usage fields and linked to
the billing reference. Before reusing that summary, review the original page
and confirm:

1. the feature applies to GitHub Copilot reporting rather than OpenAI Codex
   account usage;
2. the availability statement still matches the source;
3. related links are relevant to the current research question; and
4. no extracted instruction is being treated as trusted execution guidance.

The extractor creates an intake artifact. It does not establish source
reliability or replace review of the original page.

## Failure Boundary

If the provider returns `provider_rate_limited`, a timeout, or another exit code
`3` condition, stop the burst and retry later. Do not switch to a credential,
send a private URL, or add automatic retries to complete this case study.

## What This Demonstrates

- a pinned `uvx` command can create a structured artifact from one public page;
- requested and resolved URLs remain reviewable;
- provider status and warnings remain visible;
- important claims still require first-party verification; and
- the same workflow can be repeated without browser state or local credentials.

It does not demonstrate provider continuity, authenticated extraction, crawling,
or automatic source checking.

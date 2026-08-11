# Stable 0.1.0 Criteria

Stable `0.1.0` means the local CLI contract is ready for normal use. It does not
turn the experimental `firecrawl-keyless` provider into a stable or guaranteed
service.

No tag, GitHub Release, or PyPI upload is authorized by this document.

## Required Before Release

### Contract

- Keep one public HTTP or HTTPS URL per invocation.
- Keep Markdown and Output Schema v0.1 JSON modes compatible with `0.1.0a2`.
- Keep documented exit codes and one-error-object stderr behavior.
- Keep requested and resolved URL review fields.
- Keep no-overwrite local output behavior.

### Safety

- Continue rejecting private, local, authenticated, administrative, and
  secret-bearing URL patterns before provider submission.
- Continue post-checking provider redirect metadata with the same URL policy.
- Keep credentials, tokens, cookies, browser profiles, localStorage, and local
  private source files outside the runtime contract.
- Keep extracted content explicitly untrusted.
- Keep the Firecrawl Cloud transmission boundary visible before the first live
  command in both README files.

### Provider Boundary

- Keep `firecrawl-keyless` labeled experimental in the CLI, README files,
  package metadata, examples, and release notes.
- Preserve fail-stop handling for rate limits, timeouts, invalid responses, and
  unsafe redirect metadata.
- Do not add automatic retries, credential discovery, or provider fallback as
  a condition of `0.1.0`.
- Re-run selected public-source smoke tests without claiming uptime or quotas.

### Distribution

- Change package version from `0.1.0a2` to `0.1.0` only in the final release
  candidate.
- Map package `0.1.0` to tag `v0.1.0` and reject tag/version mismatches.
- Build wheel and sdist, run Twine checks, and test anonymous `uvx`, isolated
  `pipx`, and fresh-venv installs.
- Publish only through the existing GitHub Actions Trusted Publishing path.
- Never overwrite an existing PyPI version or attach local build artifacts
  manually.

### Evidence

- Pass the complete offline test suite on supported Python versions and both
  Ubuntu and macOS.
- Validate packaged and repository JSON Schemas.
- Keep the public fixture examples valid.
- Verify the repository-hosted GitHub Changelog case study and one failure-path
  smoke without recording provider response bodies or request identifiers.
- Complete one independent release-state QA before the explicit publication
  gate.

## Not Required For 0.1.0

- multiple providers;
- crawling or batch extraction;
- authenticated or private pages;
- browser automation;
- source reliability scoring;
- telemetry;
- a GUI, MCP server, or hosted API; or
- a provider availability guarantee.

These remain separate product decisions and must not delay a stable local CLI
contract without evidence of user demand.

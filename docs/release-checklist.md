# Release Checklist

This file records reusable release checks and evidence for published versions.

## `v0.1.0-alpha.2` candidate

### Contract

- [x] Package version `0.1.0a2` maps to tag `v0.1.0-alpha.2`.
- [x] README and release notes document the same install commands and safety boundary.
- [x] Markdown and JSON contracts remain unchanged.
- [x] `firecrawl-keyless` remains explicitly experimental.

### Distribution

- [x] PyPI project name is unregistered at candidate preparation time.
- [x] Publish workflow uses the dedicated `pypi` environment and job-level `id-token: write`.
- [x] No long-lived PyPI API token is referenced.
- [x] Release tag and package version are checked before build and upload.
- [x] The PyPI publishing action is pinned to a full commit SHA.
- [x] Wheel and sdist are built in the release workflow and checked with Twine.
- [ ] Configure the pending PyPI Trusted Publisher for the exact repository, workflow, and environment.
- [ ] Complete one independent pre-publication QA.
- [ ] Publish the GitHub prerelease and verify the PyPI upload.
- [ ] Verify anonymous `uvx`, `pipx`, and fresh-venv installs from PyPI.

### Failure policy

- PyPI versions are immutable and are never overwritten.
- If the upload is unusable, stop, document the failure, yank only when justified,
  and publish a new version after review.
- Do not delete or move a public tag as an automatic recovery action.

## `v0.1.0-alpha.1` record

## Contract

- [x] CLI help, exit codes, and error JSON match README.
- [x] Output Schema version matches generated JSON and examples.
- [x] Markdown and JSON examples contain public-safe synthetic data only.
- [x] Provider is described as `firecrawl-keyless` and `experimental`.
- [x] No availability, anonymous REST, credit, or continuity guarantee is stated.
- [x] Package version `0.1.0a1` maps to tag `v0.1.0-alpha.1`.

## Safety

- [x] URL policy and redirect metadata tests pass.
- [x] Prompt-injection and untrusted-content warning is visible near README top.
- [x] Firecrawl Cloud URL transmission is visible near README top.
- [x] No credential, cookie, browser profile, signed URL, private output, or internal document is tracked.
- [x] gitleaks and dependency review checks pass.
- [x] Secret scanning, push protection, CodeQL, and private vulnerability reporting are enabled.

## QA

- [x] Ubuntu and macOS pass on Python 3.11, 3.12, and 3.13.
- [x] Ruff passes.
- [x] 42 offline tests pass.
- [x] Normal isolated `python -m build` passes in CI and public-clone QA.
- [x] Fresh wheel install with `--no-deps` passes.
- [x] Packaged JSON Schema is present.
- [x] Public-safe Markdown and JSON smoke tests pass.
- [x] Fresh public clone QA passes.
- [x] Release notes and permanent README wording are visible from public `main` after merge.

## Repository

- [x] Repository is public under `Ishikawa-Hidekazu/public-source-extractor`.
- [x] Description, topics, and homepage are configured.
- [x] Default GitHub repository social preview is intentionally used for this alpha; no custom social image is required.
- [x] Branch protection and required checks are configured.
- [x] Community Profile is 100%.

## Distribution decisions

- [x] Release is a GitHub prerelease and source-only alpha.
- [x] GitHub-generated source archives are the only release downloads.
- [x] No locally built wheel or sdist is attached manually.
- [x] PyPI publishing is explicitly out of scope and remains disabled.
- [x] Release notes state the safety boundary and known limitations.

## Publication actions

- [x] Created and pushed annotated tag `v0.1.0-alpha.1` at the final release commit.
- [x] Published a GitHub prerelease from `docs/releases/v0.1.0-alpha.1.md` with no manual artifacts.

If either publication action fails, stop and report. Do not delete the release, delete the tag, or move the tag as an automatic recovery step.

## Post-alpha Distribution Decision

- [x] Verified `uvx` execution from the pinned public Git tag.
- [x] Kept clone, virtual environment, and `pipx` source installation as transparent fallbacks.
- [x] Kept PyPI publication disabled for the initial source-only alpha.
- [x] Opened a separate approved gate for package ownership, Trusted Publishing,
  provider continuity, and fresh install/uninstall QA.

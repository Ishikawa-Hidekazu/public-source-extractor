# Release Checklist

Release authorization for `v0.1.0-alpha.1` was granted after repository and
release-candidate QA. This file records completed evidence and current
distribution decisions.

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
- [x] Kept PyPI publication disabled while the experimental provider boundary and continuity are evaluated.
- [ ] Reconsider PyPI only after package ownership, trusted publishing, provider continuity, and fresh install/uninstall QA have a separate approved release gate.

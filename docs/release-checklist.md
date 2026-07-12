# Release Checklist

This checklist does not authorize a release. Repository publication, tags, GitHub releases, and PyPI publishing require explicit approval.

## Contract

- [ ] CLI help, exit codes, and error JSON match README.
- [ ] Output Schema version matches generated JSON and examples.
- [ ] Markdown and JSON examples contain public-safe synthetic data only.
- [ ] Provider is described as `firecrawl-keyless` and `experimental`.
- [ ] No availability, anonymous REST, credit, or continuity guarantee is stated.

## Safety

- [ ] URL policy and redirect metadata tests pass.
- [ ] Prompt-injection and untrusted-content warning is visible near README top.
- [ ] Firecrawl Cloud URL transmission is visible near README top.
- [ ] No credential, cookie, browser profile, signed URL, private output, or internal document is tracked.
- [ ] gitleaks and dependency review checks pass.

## QA

- [ ] Ubuntu and macOS pass on Python 3.11, 3.12, and 3.13.
- [ ] Ruff passes.
- [ ] Offline tests pass.
- [ ] Normal isolated `python -m build` passes in CI.
- [ ] Fresh wheel install with `--no-deps` passes.
- [ ] Packaged JSON Schema is present.
- [ ] Public-safe Markdown and JSON smoke tests pass.
- [ ] Fresh public clone QA passes.

## Publication

- [ ] Central approval covers repository creation and public visibility.
- [ ] Repository description, topics, homepage, and social preview are approved.
- [ ] Branch rules and required checks are configured.
- [ ] Release notes state source-only alpha limitations.
- [ ] PyPI remains disabled unless separately approved.


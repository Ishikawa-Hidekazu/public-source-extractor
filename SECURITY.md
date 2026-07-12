# Security Policy

## Supported versions

This project is source-only alpha. Security fixes are applied to the current `main` branch until the first tagged release defines a version support policy.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Report it privately through [ishikawa.co/contact](https://ishikawa.co/contact/) and include:

- the affected command and version or commit;
- a minimal reproduction using synthetic or public-safe data;
- the expected and actual safety behavior;
- potential impact.

Do not send credentials, tokens, cookies, signed URLs, private page content, browser profiles, or provider raw responses.

## Security boundary

Public Source Extractor does not read local credentials, cookies, browser state, or private source files. It sends the requested public URL to Firecrawl Cloud. URL validation and redirect metadata post-checking reduce accidental disclosure; they do not fully guarantee DNS behavior or the provider's actual network destination.

Extracted content is untrusted and may contain prompt injection. The CLI does not execute extracted instructions or determine source reliability.


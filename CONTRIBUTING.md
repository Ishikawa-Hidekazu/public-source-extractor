# Contributing

Thanks for helping improve Public Source Extractor. The project is in source-only alpha, so keep changes small, testable, and inside the documented safety boundary.

## Development setup

Use Python 3.11 or newer. Runtime code has no third-party dependencies; validation and lint tools are development-only dependencies.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

Run offline tests and lint before submitting a change:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
.venv/bin/ruff check src tests
```

Build and inspect the package:

```bash
.venv/bin/python -m build
```

CI performs this as a normal isolated build with network access to the Python package index. A local `--no-isolation` build may be used only to diagnose a constrained development environment and must not replace the isolated CI build.

Do not add credentials, tokens, cookies, signed URLs, browser profiles, private outputs, real authenticated pages, or private fixtures. Tests must use synthetic fixtures or intentionally public-safe URLs such as `https://example.com/`.

Network smoke tests must remain separate from the offline suite because `firecrawl-keyless` is an experimental third-party provider with unguaranteed availability and limits.

## Pull requests

- Explain the user-visible change and safety impact.
- Add or update offline tests.
- Keep provider raw bodies and private URLs out of fixtures and logs.
- Update the JSON Schema and changelog when the public contract changes.
- Confirm `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v`, Ruff, and build all pass.


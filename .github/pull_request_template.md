## Summary

- What changed?
- Why is it needed?

## Safety and contract impact

- Does this change URL validation, provider behavior, output, JSON Schema, error JSON, or exit codes?
- Does any new data leave the local machine?

## Verification

- [ ] `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v`
- [ ] `.venv/bin/ruff check src tests`
- [ ] `.venv/bin/python -m build`
- [ ] Fixtures and examples contain public-safe synthetic data only
- [ ] README, Schema, and changelog are updated when needed


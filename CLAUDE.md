## Commands

- Dev mode: `uv run --env-file .env secondbrain`

## Workflow

- Always write tests first when implementing features or fixing bugs (TDD).
- Before committing, ensure docs and `README.md` are updated.
- When creating new pages in `docs/`, also add them to the nav: section in `mkdocs.yml`.
- Always check log files when debugging.

## Notes

- Test env comes from the autouse fixtures in `tests/conftest.py` (`LOG_FILE`,
  `SECONDBRAIN_DIR`), not from a file — `[tool.pytest_env]` names `.env.test`, but it
  is gitignored and absent. Use `monkeypatch.setenv` rather than editing config.
- Google-style docstrings (used by `mkdocstrings` for API docs).
- Docs server logs: `mkdocs.log` (written by `scripts/serve_docs.py`). Check when debugging docs issues.
- Never start long-running servers (e.g., `serve_docs.py`, `mkdocs serve`). Use `uv run mkdocs build` to verify docs compile.
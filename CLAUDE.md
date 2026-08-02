## Commands

- Dev mode: `uv run --env-file .env second_brain`

## Workflow

- Always write tests first when implementing features or fixing bugs (TDD).
- Before committing, ensure docs and `README.md` are updated.
- When creating new pages in `docs/`, also add them to the nav: section in `mkdocs.yml`.
- Always check log files when debugging.

## Notes

- pytest-env auto-loads `.env.test` — don't set `LOG_LEVEL` manually in tests.
- Google-style docstrings (used by `mkdocstrings` for API docs).
- Docs server logs: `mkdocs.log` (written by `scripts/serve_docs.py`). Check when debugging docs issues.
- Never start long-running servers (e.g., `serve_docs.py`, `mkdocs serve`). Use `uv run mkdocs build` to verify docs compile.
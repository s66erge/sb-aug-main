# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Setup, CLI usage, env vars, and test/docs commands are in `README.md`; the module
graph and CLI surface are diagrammed in `docs/architecture.md`. This file covers only
what those don't say.

## Invariants that are easy to break

- **Environment is read lazily on every call, never cached at import time.**
  `notes_dir()` re-reads `SECONDBRAIN_DIR`; `configure_logging()` re-reads
  `LOG_LEVEL`/`LOG_FILE`. The test suite depends on this — `conftest.py` uses
  `monkeypatch.setenv` after import. Hoisting any of it into a module-level constant
  silently breaks tests.
- **The missing-notes-directory divergence is intentional, not an oversight.**
  `list` prints a message and exits 0; `show` writes to stderr and exits 1; `new`
  creates the directory. Don't "unify" these.
- **`slugify` preserves non-Latin scripts on purpose.** Latin accents fold via NFKD,
  but stripping everything non-ASCII would collapse every CJK title to `untitled`.
  There is a regression test for this.
- **Logging must never be why a command fails.** `configure_logging()` swallows
  `OSError` from the file sink and continues with console output only.

## Layering

`notes.py` (stdlib only) ← `app.py` ← `cli.py`. Imports point one way. New note
behavior belongs in `notes.py`, where it is testable without Click or loguru; keep
`cli.py` to argument parsing, echoing, and exit codes.

## Gotchas

- `[tool.pytest_env]` points at `.env.test`, which is gitignored and does not exist.
  That is fine — the fixtures set what tests need. Don't add the file expecting it to
  be the source of truth for test config.
- `scripts/serve_docs.py` exists only because `mkdocs serve` output needs to land in
  `mkdocs.log` for tooling to read; prefer it over calling `mkdocs serve` directly.
- `secondbrain-tour.html` is a tracked hand-written page, not build output — `site/`
  and `mkdocs.log` are generated and ignored.

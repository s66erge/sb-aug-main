# secondbrain

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd secondbrain
uv sync
```

## Usage

The CLI exposes three subcommands:

```bash
uv run secondbrain new "My brilliant idea"   # create a note
uv run secondbrain list                      # list notes (newest first)
uv run secondbrain show 1                    # print the contents of note 1
```

With the dev environment loaded:

```bash
uv run --env-file .env secondbrain new "My brilliant idea"
```

Via the Python module:

```bash
uv run python -m secondbrain new "My brilliant idea"
```

## Environment Variables

`.env.example` is the template for local configuration — copy it to `.env` for development:

```bash
cp .env.example .env
```

- `LOG_LEVEL` (default: `INFO`) — set to `DEBUG` in `.env` for verbose console output.
- `LOG_FILE` (default: `app.log` inside `SECONDBRAIN_DIR`) — path to the log file. If it
  cannot be opened, logging falls back to the console and the command still runs.
- `SECONDBRAIN_DIR` (default: `~/secondbrain/`) — directory where notes are stored.

`.env` is not auto-loaded; use `uv run --env-file .env` to load the dev environment explicitly.

### Log format

Console and file output share one compact, pipe-delimited line — no milliseconds, and the
level rendered as a single letter (`T`, `D`, `I`, `S`, `W`, `E`, `C`):

```
2026-08-01 20:56:47 | I | secondbrain.app:main:29 | Hello from secondbrain!
```

## Testing

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov
```

## Documentation

Preview docs locally:

```bash
uv run python scripts/serve_docs.py
```

Build static docs:

```bash
uv run mkdocs build
```

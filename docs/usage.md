# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

The CLI exposes three subcommands:

```bash
uv run secondbrain new "My brilliant idea"   # create a note
uv run secondbrain list                      # list notes (newest first)
uv run secondbrain show 1                    # print the contents of note 1
```

With dev settings loaded:

```bash
uv run --env-file .env secondbrain new "My brilliant idea"
```

Or as a Python module:

```bash
uv run python -m secondbrain new "My brilliant idea"
```

### Notes with a body

The first line of the argument is the note title; everything after the first newline is the
body. A literal `\n` is interpreted, so this works from any shell:

```bash
uv run secondbrain new "hello\nworld"
```

```markdown
# hello

world
```

Only the first line feeds the filename, so the note above lands in `2026-08-02-hello.md` —
the body never leaks into the name. A single-line argument still produces just the heading.

## Environment Variables

| Variable           | Default                       | Description                        |
|--------------------|-------------------------------|------------------------------------|
| `LOG_LEVEL`        | `INFO`                        | Console log level (DEBUG, INFO, …) |
| `LOG_FILE`         | `app.log` in `SECONDBRAIN_DIR`| Path to the log file               |
| `SECONDBRAIN_DIR`  | `~/secondbrain/`              | Directory where notes are stored   |

The log file defaults to the notes directory rather than the working directory, so
running the CLI from anywhere does not leave an `app.log` behind. If the log file
cannot be opened, the command still runs and logs to the console only.

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.

## Logging

Console and file handlers share one compact, pipe-delimited format:

```
2026-08-01 20:56:47 | I | secondbrain.app:main:29 | Hello from secondbrain!
```

Timestamps carry no milliseconds and the level is a single-letter code, so lines stay
column-aligned:

```text
"<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
"<level>{level.icon}</level> | "
"<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
"<level>{message}</level>"
```

The colour markup is stripped for non-colorized sinks, so `app.log` lines are byte-identical
to the console lines.

| Level      | Icon |
|------------|------|
| `TRACE`    | `T`  |
| `DEBUG`    | `D`  |
| `INFO`     | `I`  |
| `SUCCESS`  | `S`  |
| `WARNING`  | `W`  |
| `ERROR`    | `E`  |
| `CRITICAL` | `C`  |

"""CLI entry point using Click."""

from __future__ import annotations

import click
from loguru import logger

from secondbrain.app import configure_logging
from secondbrain.notes import create_note, notes_dir, read_note


@click.group()
def cli():
    """secondbrain -- capture and organise your thoughts."""
    configure_logging()


@cli.command()
@click.argument("title")
def new(title: str):
    r"""Create a new note from TITLE.

    The first line becomes the heading and names the file; anything after the
    first newline is written as the note body. A literal `\n` in the argument
    is interpreted as a newline, so `new "hello\nworld"` works from any shell.
    """
    base_dir = notes_dir()
    logger.debug("Creating note in {}", base_dir)
    # argv delivers a typed `\n` as the two characters `\` and `n`; only that
    # escape is interpreted, so non-ASCII titles pass through untouched.
    path = create_note(title.replace("\\n", "\n"), base_dir)
    logger.info("Created note: {}", path)
    click.echo(path)


@cli.command("list")
def list_notes():
    """List all notes in the notes directory."""
    base_dir = notes_dir()

    if not base_dir.is_dir():
        logger.warning("Notes directory does not exist: {}", base_dir)
        click.echo(f"Notes directory does not exist: {base_dir}")
        return

    files = sorted(base_dir.glob("*.md"), reverse=True)

    click.echo(f"Notes: {base_dir}")

    if not files:
        logger.info("No notes found in {}", base_dir)
        click.echo("No notes found.")
        return

    logger.debug("Found {} note(s) in {}", len(files), base_dir)
    for i, f in enumerate(files, 1):
        click.echo(f"{i}. {f.name}")


@cli.command()
@click.argument("number", type=int)
def show(number: int):
    """Display the contents of note NUMBER."""
    base_dir = notes_dir()

    if not base_dir.is_dir():
        logger.error("Notes directory does not exist: {}", base_dir)
        click.echo(f"Error: Notes directory does not exist: {base_dir}", err=True)
        raise SystemExit(1)

    files = sorted(base_dir.glob("*.md"), reverse=True)

    if not files:
        logger.error("No notes found in {}", base_dir)
        click.echo("Error: No notes found.", err=True)
        raise SystemExit(1)

    if number < 1 or number > len(files):
        logger.error("Note {} out of range ({}  available)", number, len(files))
        click.echo(
            f"Error: Note {number} not found. Only {len(files)} notes available.",
            err=True,
        )
        raise SystemExit(1)

    logger.debug("Showing note {}: {}", number, files[number - 1].name)
    click.echo(read_note(files[number - 1]))

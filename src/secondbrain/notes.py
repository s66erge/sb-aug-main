"""Business logic for note creation."""

from __future__ import annotations

import os
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path

DEFAULT_DIR_NAME = "secondbrain"


def notes_dir() -> Path:
    """Return the notes directory, from `SECONDBRAIN_DIR` or `~/secondbrain`.

    Read lazily on every call so the environment stays authoritative.
    """
    return Path(
        os.environ.get("SECONDBRAIN_DIR", str(Path.home() / DEFAULT_DIR_NAME))
    ).expanduser()


def slugify(title: str) -> str:
    """Convert a title string into a filename-safe slug.

    Latin accents are folded to their ASCII base (`Café` -> `cafe`); other
    scripts are kept as-is (`日本` -> `日本`) rather than dropped, so that
    non-Latin titles stay distinguishable instead of all slugging to the
    same fallback.
    """
    # NFKD splits `é` into `e` + combining accent, so dropping the combining
    # marks (category Mn) leaves the ASCII base letter behind.
    decomposed = unicodedata.normalize("NFKD", title)
    slug = "".join(c for c in decomposed if not unicodedata.combining(c))
    slug = slug.lower()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"[\s-]+", "-", slug)
    slug = slug.strip("-_")
    return slug or "untitled"


def split_title_body(text: str) -> tuple[str, str]:
    """Split note input into its title and body on the first newline.

    Only the first newline separates the two, so a multi-line body is kept
    intact. A body that is empty or only whitespace counts as no body at all.

    Blank lines and trailing whitespace are trimmed from the body, but its
    leading indentation is not — stripping that would turn the first line of an
    indented code block into a paragraph while leaving the rest indented.

    Args:
        text: The raw note input, with real newlines.

    Returns:
        A `(title, body)` pair. The title is stripped; the body keeps the
        indentation of its first line.
    """
    title, _, body = text.partition("\n")
    body = body.strip("\n").rstrip()
    return title.strip(), body if body.strip() else ""


def build_note_path(title: str, base_dir: Path, note_date: date) -> Path:
    """Build the full file path for a note, creating the directory if needed.

    If a file with the same name already exists, appends -1, -2, … to avoid
    overwriting.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(title)
    stem = f"{note_date.isoformat()}-{slug}"
    candidate = base_dir / f"{stem}.md"
    counter = 1
    while candidate.exists():
        candidate = base_dir / f"{stem}-{counter}.md"
        counter += 1
    return candidate


def create_note(
    text: str,
    base_dir: Path,
    now: datetime | None = None,
) -> Path:
    """Create a markdown note file and return its absolute path.

    The first line of `text` becomes the heading and is the only source of the
    filename slug; anything after the first newline is written as the body,
    separated by a blank line. There is no timestamp line — the note date
    already lives in the filename.

    Args:
        text: The note input. First line is the title, the rest is the body.
        base_dir: Directory to write the note into, created if missing.
        now: Timestamp supplying the filename date. Defaults to the current time.

    Returns:
        The resolved path of the note that was written.
    """
    now = now or datetime.now()
    title, body = split_title_body(text)
    path = build_note_path(title, base_dir, now.date())
    heading = f"# {title}".rstrip()
    content = f"{heading}\n\n{body}\n" if body else f"{heading}\n"
    path.write_text(content, encoding="utf-8")
    return path.resolve()


def read_note(path: Path) -> str:
    """Read a note's contents, matching the UTF-8 encoding used to write it."""
    return path.read_text(encoding="utf-8")

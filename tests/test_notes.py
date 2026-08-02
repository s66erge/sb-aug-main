"""Tests for the notes module (slugify, build_note_path, create_note)."""

from datetime import date, datetime
from pathlib import Path

import pytest

from secondbrain.notes import (
    build_note_path,
    create_note,
    notes_dir,
    read_note,
    slugify,
)

# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("My brilliant idea about caching", "my-brilliant-idea-about-caching"),
        ("Hello, World! @#$%", "hello-world"),
        ("too---many  spaces", "too-many-spaces"),
        ("--leading and trailing--", "leading-and-trailing"),
        ("", "untitled"),
        ("@#$%^&", "untitled"),
        ("cafe latte", "cafe-latte"),
        ("idea 42 is great", "idea-42-is-great"),
        ("Café über Ideen", "cafe-uber-ideen"),
        ("Ångström & naïve", "angstrom-naive"),
        ("日本の考え", "日本の考え"),
        ("Идея о кэше", "идея-о-кэше"),
        ("🎉🎉🎉", "untitled"),
    ],
    ids=[
        "basic",
        "special_chars",
        "collapsed_hyphens",
        "leading_trailing",
        "empty",
        "only_special",
        "unicode_ascii",
        "numbers_preserved",
        "latin_accents_folded",
        "more_latin_accents",
        "cjk_preserved",
        "cyrillic_preserved",
        "emoji_only",
    ],
)
def test_slugify(title, expected):
    assert slugify(title) == expected


def test_slugify_keeps_distinct_non_latin_titles_distinct():
    """Regression: non-Latin titles all collapsed to `untitled` and collided."""
    assert slugify("日本の考え") != slugify("キャッシュの話")


# ---------------------------------------------------------------------------
# notes_dir
# ---------------------------------------------------------------------------


def test_notes_dir_uses_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv("SECONDBRAIN_DIR", str(tmp_path / "elsewhere"))
    assert notes_dir() == tmp_path / "elsewhere"


def test_notes_dir_expands_tilde(tmp_path, monkeypatch):
    """`.env.example` ships `SECONDBRAIN_DIR=~/secondbrain/`, so `~` must expand."""
    monkeypatch.setenv("SECONDBRAIN_DIR", "~/mynotes")
    monkeypatch.setenv("HOME", str(tmp_path))  # what expanduser() consults
    assert notes_dir() == tmp_path / "mynotes"


def test_notes_dir_defaults_to_home(tmp_path, monkeypatch):
    monkeypatch.delenv("SECONDBRAIN_DIR", raising=False)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    assert notes_dir() == tmp_path / "secondbrain"


# ---------------------------------------------------------------------------
# build_note_path
# ---------------------------------------------------------------------------


def test_build_note_path_basic(tmp_path):
    result = build_note_path("My idea", tmp_path, date(2026, 3, 22))
    assert result == tmp_path / "2026-03-22-my-idea.md"


def test_build_note_path_creates_dir(tmp_path):
    nested = tmp_path / "sub" / "dir"
    result = build_note_path("Test", nested, date(2026, 1, 1))
    assert nested.is_dir()
    assert result == nested / "2026-01-01-test.md"


# ---------------------------------------------------------------------------
# create_note
# ---------------------------------------------------------------------------

FIXED_NOW = datetime(2026, 3, 22, 14, 30, 0)


def test_create_note_file_exists(tmp_path):
    path = create_note("Test idea", tmp_path, now=FIXED_NOW)
    assert path.is_file()


def test_create_note_content_heading(tmp_path):
    path = create_note("Test idea", tmp_path, now=FIXED_NOW)
    lines = path.read_text().splitlines()
    assert lines[0] == "# Test idea"


def test_create_note_content_timestamp(tmp_path):
    path = create_note("Test idea", tmp_path, now=FIXED_NOW)
    text = path.read_text()
    assert "2026-03-22T14:30:00" in text


def test_create_note_no_yaml_frontmatter(tmp_path):
    path = create_note("Test idea", tmp_path, now=FIXED_NOW)
    text = path.read_text()
    assert not text.startswith("---")


def test_create_note_returns_absolute_path(tmp_path):
    path = create_note("Test idea", tmp_path, now=FIXED_NOW)
    assert path.is_absolute()


def test_create_note_creates_directory(tmp_path):
    nested = tmp_path / "deep" / "dir"
    path = create_note("Test idea", nested, now=FIXED_NOW)
    assert nested.is_dir()
    assert path.is_file()


# ---------------------------------------------------------------------------
# duplicate-title handling
# ---------------------------------------------------------------------------


def test_build_note_path_appends_suffix_when_file_exists(tmp_path):
    original = build_note_path("idea", tmp_path, date(2026, 3, 22))
    original.write_text("first")
    second = build_note_path("idea", tmp_path, date(2026, 3, 22))
    assert second == tmp_path / "2026-03-22-idea-1.md"


def test_create_note_no_overwrite(tmp_path):
    path1 = create_note("My idea", tmp_path, now=FIXED_NOW)
    path2 = create_note("My idea", tmp_path, now=FIXED_NOW)
    assert path1 != path2
    assert path1.is_file()
    assert path2.is_file()
    assert path2.name.endswith("-1.md")


def test_create_note_unicode_titles_do_not_collide(tmp_path):
    """Two different CJK titles must not land in the same `untitled` slot."""
    path1 = create_note("日本の考え", tmp_path, now=FIXED_NOW)
    path2 = create_note("キャッシュの話", tmp_path, now=FIXED_NOW)
    assert path1.stem != path2.stem
    assert "untitled" not in path1.name
    assert "untitled" not in path2.name


# ---------------------------------------------------------------------------
# read_note
# ---------------------------------------------------------------------------


def test_read_note_roundtrips_unicode(tmp_path):
    path = create_note("Café über Ideen 日本", tmp_path, now=FIXED_NOW)
    assert "# Café über Ideen 日本" in read_note(path)


def test_read_note_is_utf8_regardless_of_locale(tmp_path):
    """`read_note` must not depend on the platform's default encoding."""
    path = tmp_path / "note.md"
    path.write_bytes(b"# Caf\xc3\xa9\n")  # UTF-8 bytes, written explicitly
    assert read_note(path) == "# Café\n"


def test_create_note_multiple_duplicates(tmp_path):
    path1 = create_note("Dup", tmp_path, now=FIXED_NOW)
    path2 = create_note("Dup", tmp_path, now=FIXED_NOW)
    path3 = create_note("Dup", tmp_path, now=FIXED_NOW)
    assert len({path1, path2, path3}) == 3
    assert path1.is_file() and path2.is_file() and path3.is_file()
    assert path2.name.endswith("-1.md")
    assert path3.name.endswith("-2.md")

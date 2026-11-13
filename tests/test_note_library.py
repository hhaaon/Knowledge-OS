
import pytest

from reader import Note
from note_library import (
    ALL_NOTES,
    list_folders,
    notes_in_folder,
    read_enhanced_note,
)


def sample_notes():
    return [
        Note("Areas/Ideas.md", "# Ideas"),
        Note(
            "Areas/Design rules/Design rules.md",
            "# Design rules",
        ),
        Note("Archive/Archive Index.md", "# Archive"),
        Note("Welcome.md", "# Welcome"),
    ]


def test_folder_index():
    folders = list_folders(sample_notes())

    assert ALL_NOTES in folders
    assert "Areas" in folders
    assert "Areas/Design rules" in folders
    assert "Archive" in folders


def test_browsing_includes_subfolders():
    selected = notes_in_folder(
        sample_notes(),
        "Areas",
    )

    assert len(selected) == 2
    assert all(
        note.relative_path.startswith("Areas/")
        for note in selected
    )


def test_read_enhanced_note(tmp_path):
    relative = "Areas/Ideas.md"

    target = (
        tmp_path
        / "_experiments"
        / "v2"
        / relative
    )

    target.parent.mkdir(parents=True)
    target.write_text(
        "# Enhanced Ideas",
        encoding="utf-8",
    )

    assert read_enhanced_note(
        tmp_path,
        relative,
    ) == "# Enhanced Ideas"

    assert read_enhanced_note(
        tmp_path,
        "Areas/Missing.md",
    ) is None


def test_reject_path_traversal(tmp_path):
    with pytest.raises(ValueError):
        read_enhanced_note(
            tmp_path,
            "../private.md",
        )


from pathlib import Path, PurePosixPath

from reader import Note


ALL_NOTES = "All notes"


def list_folders(notes: list[Note]) -> list[str]:
    """Build a folder index from existing note paths."""

    folders = set()

    for note in notes:
        parent = PurePosixPath(note.relative_path).parent

        while parent != PurePosixPath("."):
            folders.add(parent.as_posix())
            parent = parent.parent

    return [ALL_NOTES] + sorted(
        folders,
        key=str.casefold,
    )


def notes_in_folder(
    notes: list[Note],
    folder: str,
) -> list[Note]:
    """Include notes in the selected folder and subfolders."""

    if folder == ALL_NOTES:
        selected = notes
    else:
        prefix = folder.rstrip("/") + "/"
        selected = [
            note
            for note in notes
            if note.relative_path.startswith(prefix)
        ]

    return sorted(
        selected,
        key=lambda note: note.relative_path.casefold(),
    )


def read_enhanced_note(
    test_vault: Path,
    relative_path: str,
) -> str | None:
    """
    Read a V2 enhanced note when available.

    Return None when no enhanced version exists.
    Never create or modify files.
    """

    relative = PurePosixPath(relative_path)

    if (
        relative.is_absolute()
        or ".." in relative.parts
        or "\\" in relative_path
        or relative.suffix.lower() != ".md"
    ):
        raise ValueError("Invalid Markdown note path.")

    enhanced_root = (
        test_vault / "_experiments" / "v2"
    ).resolve()

    target = (
        enhanced_root / Path(*relative.parts)
    ).resolve()

    if not target.is_relative_to(enhanced_root):
        raise ValueError("Note path escapes enhanced vault.")

    if not target.is_file():
        return None

    return target.read_text(encoding="utf-8")

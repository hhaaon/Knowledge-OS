import pytest
from reader import load_notes


def test_loads_nested_markdown_and_ignores_obsidian(tmp_path):
    # Arrange
    nested = tmp_path / "Areas" / "Mental Models"
    nested.mkdir(parents=True)

    note = nested / "First Principle Thinking.md"
    note.write_text("Question assumptions.", encoding="utf-8")

    config = tmp_path / ".obsidian"
    config.mkdir()
    (config / "hidden.md").write_text(
        "Should not load.", encoding="utf-8"
    )

    # Act
    notes = load_notes(tmp_path)

    # Assert
    assert len(notes) == 1
    assert notes[0].relative_path == (
        "Areas/Mental Models/First Principle Thinking.md"
    )
    assert notes[0].content == "Question assumptions."
    assert note.read_text(encoding="utf-8") == (
        "Question assumptions."
    )

def test_invalid_vault_path(tmp_path):
    missing = tmp_path / "does-not-exist"

    with pytest.raises(NotADirectoryError):
        load_notes(missing)


import pytest

import note_enhancer


def test_original_is_preserved_and_target_not_overwritten(
    tmp_path,
    monkeypatch,
):
    original = tmp_path / "original"
    enhanced = tmp_path / "enhanced"

    relative = "Ideas/example.md"

    source = original / relative
    source.parent.mkdir(parents=True)

    source.write_text(
        "# Example\nOriginal important knowledge.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        note_enhancer,
        "enhance_markdown",
        lambda text: (
            "# Example\n"
            "Improved explanation.\n\n"
            "## Test Your Understanding\n"
            "- Explain the main idea.\n"
        ),
    )

    output = note_enhancer.enhance_one_note(
        original,
        enhanced,
        note_enhancer.Path(relative),
    )

    assert source.read_text(encoding="utf-8") == (
        "# Example\nOriginal important knowledge."
    )

    assert output.exists()
    assert "Improved explanation" in output.read_text(
        encoding="utf-8"
    )

    with pytest.raises(FileExistsError):
        note_enhancer.enhance_one_note(
            original,
            enhanced,
            note_enhancer.Path(relative),
        )

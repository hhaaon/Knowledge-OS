
import pytest

from note_enhancer_v2 import (
    build_learning_note,
    enhance_one_note_v2,
)


def test_builds_learning_note():
    original = (
        "**# Inversion**\n"
        "Reason backward using [[Mental Models|models]]."
    )

    enhanced = build_learning_note(
        original,
        [
            "What is inversion?",
            "Why might it be useful?",
            "How would you apply it?",
        ],
    )

    assert "# Inversion" in enhanced
    assert "using models." in enhanced
    assert "[[Mental Models" not in enhanced
    assert "## Test Your Understanding" in enhanced
    assert enhanced.count("?\n") == 3


def test_does_not_modify_or_overwrite(tmp_path, monkeypatch):
    import note_enhancer_v2

    original_root = tmp_path / "original"
    test_root = tmp_path / "test"

    relative = note_enhancer_v2.Path("Ideas/example.md")
    source = original_root / relative

    source.parent.mkdir(parents=True)

    original_text = "# Example\nImportant explanation.\n"
    source.write_text(original_text, encoding="utf-8")

    monkeypatch.setattr(
        note_enhancer_v2,
        "generate_questions",
        lambda text: [
            "Explain the idea.",
            "Why does it work?",
            "When is it useful?",
        ],
    )

    result = enhance_one_note_v2(
        original_root,
        test_root,
        relative,
    )

    assert result.exists()
    assert source.read_text(encoding="utf-8") == original_text

    with pytest.raises(FileExistsError):
        enhance_one_note_v2(
            original_root,
            test_root,
            relative,
        )

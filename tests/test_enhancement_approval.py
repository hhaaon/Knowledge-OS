
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import note_enhancer_v2 as enhancer
from note_library import read_approved_note


def test_generation_does_not_write_files(
    monkeypatch,
    tmp_path,
):
    def fake_chat(**kwargs):
        data = {
            "improved_markdown": "# Improved note\n\nClear explanation.",
            "questions": [
                "Explain the main idea.",
                "Give an example.",
                "What are the limitations?",
            ],
        }
        return SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps(data)
            )
        )

    monkeypatch.setattr(enhancer, "chat", fake_chat)
    monkeypatch.chdir(tmp_path)

    result = enhancer.propose_enhancement(
        "# Original note\n\nAn important idea."
    )

    assert "Improved note" in result
    assert "Test Your Understanding" in result
    assert list(tmp_path.iterdir()) == []


def test_approval_preserves_original_and_prevents_overwrite(
    tmp_path,
):
    original_root = tmp_path / "vault"
    enhanced_root = tmp_path / "enhanced"
    relative_path = Path("ideas/example.md")

    source = original_root / relative_path
    source.parent.mkdir(parents=True)
    source.write_text("Original note", encoding="utf-8")

    proposal = "# Improved example\n\nUseful explanation."

    assert not enhanced_root.exists()

    saved = enhancer.save_approved_enhancement(
        original_vault=original_root,
        test_vault=enhanced_root,
        relative_path=relative_path,
        enhanced_text=proposal,
        expected_original_text="Original note",
    )

    assert saved.read_text(encoding="utf-8") == proposal
    assert source.read_text(encoding="utf-8") == "Original note"

    assert (
        read_approved_note(enhanced_root, "ideas/example.md")
        == proposal
    )

    with pytest.raises(FileExistsError):
        enhancer.save_approved_enhancement(
            original_root,
            enhanced_root,
            relative_path,
            "Another version",
            "Original note",
        )


def test_changed_source_blocks_approval(tmp_path):
    original_root = tmp_path / "vault"
    enhanced_root = tmp_path / "enhanced"
    source = original_root / "example.md"

    original_root.mkdir()
    source.write_text("Updated note", encoding="utf-8")

    with pytest.raises(ValueError, match="changed"):
        enhancer.save_approved_enhancement(
            original_root,
            enhanced_root,
            Path("example.md"),
            "Old proposal",
            "Previous note",
        )

    assert not enhanced_root.exists()

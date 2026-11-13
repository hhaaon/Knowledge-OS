
import note_enhancer_v2

from batch_enhance import run_batch


def test_batch_preserves_originals_and_skips_existing(
    tmp_path,
    monkeypatch,
):
    original = tmp_path / "original"
    enhanced = tmp_path / "enhanced"

    notes = {
        "Ideas/a.md": "# A\nFirst idea.",
        "Ideas/b.md": "# B\nSecond idea.",
    }

    for name, content in notes.items():
        source = original / name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(content, encoding="utf-8")

    monkeypatch.setattr(
        note_enhancer_v2,
        "generate_questions",
        lambda text: [
            "Explain the main idea.",
            "Why is it important?",
            "How would you apply it?",
        ],
    )

    # Preview must not write anything.
    assert run_batch(original, enhanced, limit=1) == 0
    assert not enhanced.exists()

    # First execution enhances one note.
    assert run_batch(
        original, enhanced, limit=1, execute=True
    ) == 0

    first_output = (
        enhanced / "_experiments/v2/Ideas/a.md"
    )

    assert first_output.exists()
    original_enhancement = first_output.read_text(
        encoding="utf-8"
    )

    # Second execution must skip the existing note.
    assert run_batch(
        original, enhanced, limit=1, execute=True
    ) == 0

    assert first_output.read_text(
        encoding="utf-8"
    ) == original_enhancement

    assert (
        enhanced / "_experiments/v2/Ideas/b.md"
    ).exists()

    # Original files must remain unchanged.
    for name, content in notes.items():
        assert (original / name).read_text(
            encoding="utf-8"
        ) == content

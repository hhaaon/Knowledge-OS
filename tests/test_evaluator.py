
from chunker import Passage
from evaluator import build_evaluation_prompt


def test_build_evaluation_prompt():
    # Arrange
    situation = "I'm 23. Is it too early to start a business?"

    candidates = [
        (
            Passage(
                relative_path="Mental Models/Inversion.md",
                text="Think backward from failure to identify risks."
            ),
            0.85
        ),
        (
            Passage(
                relative_path="Mental Models/First Principles.md",
                text="Separate assumptions from facts."
            ),
            0.72
        )
    ]

    # Act
    prompt = build_evaluation_prompt(situation, candidates)

    # Assert: The situation is included
    assert situation in prompt

    # Assert: Each candidate has a unique citation ID
    assert "[P1]" in prompt
    assert "[P2]" in prompt

    # Assert: Source paths are preserved
    assert "Mental Models/Inversion.md" in prompt
    assert "Mental Models/First Principles.md" in prompt

    # Assert: Original evidence is preserved
    assert "Think backward from failure to identify risks." in prompt
    assert "Separate assumptions from facts." in prompt

    # Assert: The evaluator may reject all candidates
    assert "no useful connection was found" in prompt.lower()

    # Assert: Instructions discourage unsupported claims
    assert "Do not force connections." in prompt
    assert "Do not invent source evidence." in prompt

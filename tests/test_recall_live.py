
import os

import pytest

from recall_evaluator import evaluate_recall


QUESTION = (
    "Why can reasoning backward about failure "
    "produce more actionable guidance than "
    "reasoning forward about success?"
)

# Synthetic reference material created for testing.
# No personal notes or private vault required.
REFERENCE_NOTE = """
Inversion means reasoning backward from a goal.

Instead of only asking how to achieve success,
consider which actions could cause failure.

Failure conditions can be easier to identify
because they are often concrete and specific.
Success goals may be vague and difficult to define.

Identifying failure conditions helps a person
take practical steps to avoid preventable mistakes.

Inversion complements forward planning.
It does not replace the need for a positive goal.
"""


@pytest.mark.skipif(
    os.getenv("RUN_LLM_TESTS") != "1",
    reason="Live LLM tests are opt-in.",
)
@pytest.mark.parametrize(
    "answer,expected",
    [
        (
            "Failure analysis identifies specific risks "
            "and preventable mistakes, whereas success "
            "goals can be vague.",
            "correct",
        ),
        (
            "Because thinking about failure is easier.",
            "partial",
        ),
        (
            "Inversion means ignoring failures "
            "and focusing only on success.",
            "incorrect",
        ),
    ],
    ids=[
        "correct",
        "partial",
        "incorrect",
    ],
)
def test_recall_grading(answer, expected):
    feedback = evaluate_recall(
        question=QUESTION,
        learner_answer=answer,
        reference_note=REFERENCE_NOTE,
    )

    assert feedback.verdict == expected, (
        f"Expected {expected}, got {feedback.verdict}.\n"
        f"Feedback: {feedback.explanation}"
    )

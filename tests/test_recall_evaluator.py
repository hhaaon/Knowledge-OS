
import json
from types import SimpleNamespace

import pytest

import recall_evaluator


@pytest.mark.parametrize(
    "verdict",
    ["correct", "partial", "incorrect"],
)
def test_evaluation_returns_structured_feedback(
    monkeypatch,
    verdict,
):
    def fake_chat(**kwargs):
        assert kwargs["think"] is False
        return SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps({
                    "verdict": verdict,
                    "explanation": "Test explanation.",
                    "missing_or_incorrect": "",
                })
            )
        )

    monkeypatch.setattr(
        recall_evaluator,
        "chat",
        fake_chat,
    )

    result = recall_evaluator.evaluate_recall(
        question="What is inversion?",
        learner_answer="Thinking backward from failure.",
        reference_note="Inversion reasons backward.",
    )

    assert result.verdict == verdict
    assert result.explanation == "Test explanation."


def test_empty_answer_is_rejected():
    with pytest.raises(ValueError):
        recall_evaluator.evaluate_recall(
            question="What is inversion?",
            learner_answer="  ",
            reference_note="Inversion reasons backward.",
        )

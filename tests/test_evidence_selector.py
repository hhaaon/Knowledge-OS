
from types import SimpleNamespace

import evidence_selector
from chunker import Passage


def test_selects_only_useful_passage(monkeypatch):
    candidates = [
        (
            Passage(
                relative_path="Inversion.md",
                text="Identify risks by reasoning backward."
            ),
            0.85
        ),
        (
            Passage(
                relative_path="Spring.md",
                text="Spring initializes managed beans."
            ),
            0.80
        )
    ]

    def fake_chat(**kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(
                content='{"selected_ids": [1]}'
            )
        )

    monkeypatch.setattr(
        evidence_selector,
        "chat",
        fake_chat
    )

    result = evidence_selector.select_useful_passages(
        "Should I start a business at 23?",
        candidates
    )

    assert len(result) == 1
    assert result[0][0].relative_path == "Inversion.md"


def test_can_reject_all_passages(monkeypatch):
    candidates = [
        (
            Passage(
                relative_path="Spring.md",
                text="Spring initializes managed beans."
            ),
            0.90
        )
    ]

    def fake_chat(**kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(
                content='{"selected_ids": []}'
            )
        )

    monkeypatch.setattr(
        evidence_selector,
        "chat",
        fake_chat
    )

    result = evidence_selector.select_useful_passages(
        "What is Vietnam's current CPI?",
        candidates
    )

    assert result == []

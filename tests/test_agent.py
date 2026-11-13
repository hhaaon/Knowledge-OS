
from types import SimpleNamespace

import agent
from chunker import Passage


def test_official_cpi_requires_web_search(monkeypatch):
    question = (
        "What was Vietnam's official year-over-year "
        "CPI inflation rate for October 2026?"
    )

    candidates = [
        (
            Passage(
                relative_path="private.md",
                text="PRIVATE_NOTE_CONTENT"
            ),
            0.9
        )
    ]

    searches = []
    model_messages = []

    def fake_search(query):
        searches.append(query)

        return (
            "[W1] National Statistics Office\n"
            "URL: https://www.nso.gov.vn/en/cpi/\n"
            "Excerpt: October 2026 CPI increased "
            "5.09% year-on-year."
        )

    def fake_chat(**kwargs):
        model_messages.extend(kwargs["messages"])

        return SimpleNamespace(
            message=SimpleNamespace(
                content="October 2026 CPI was 5.09%."
            )
        )

    monkeypatch.setattr(
        agent, "search_web", fake_search
    )

    monkeypatch.setattr(
        agent, "chat", fake_chat
    )

    answer, sources = agent.run_agent(
        situation=question,
        candidates=candidates,
        allow_web=True
    )

    # Search must execute exactly once.
    assert searches == [question]

    # Private note content must not enter the search query.
    assert "PRIVATE_NOTE_CONTENT" not in searches[0]

    # The retrieved evidence must reach the model.
    assert any(
        "5.09%" in message["content"]
        for message in model_messages
    )

    assert "5.09%" in answer
    assert "nso.gov.vn" in sources

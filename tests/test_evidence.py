
import json
import pytest

from chunker import Passage
from evidence import validate_insights


def test_accepts_valid_evidence():
    candidates = [
        (
            Passage(
                "Inversion.md",
                "Think backward from failure."
            ),
            0.5
        )
    ]

    response = json.dumps({
        "insights": [{
            "passage_id": "P1",
            "quote": "Think backward from failure.",
            "application": "Identify business risks.",
            "limitation": "Does not predict success.",
            "next_step": "List major failure risks."
        }]
    })

    insights = validate_insights(response, candidates)

    assert len(insights) == 1
    assert insights[0]["passage_id"] == "P1"


def test_rejects_fabricated_quotation():
    candidates = [
        (
            Passage(
                "Inversion.md",
                "Think backward from failure."
            ),
            0.5
        )
    ]

    response = json.dumps({
        "insights": [{
            "passage_id": "P1",
            "quote": "Every entrepreneur will succeed.",
            "application": "Start a business.",
            "limitation": "None.",
            "next_step": "Launch now."
        }]
    })

    with pytest.raises(ValueError, match="Invalid source quotation"):
        validate_insights(response, candidates)

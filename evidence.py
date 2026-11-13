
import json

from chunker import Passage


def validate_insights(
    raw_response: str,
    candidates: list[tuple[Passage, float]]
) -> list[dict]:
    data = json.loads(raw_response)

    insights = data.get("insights")

    if not isinstance(insights, list) or len(insights) > 2:
        raise ValueError("Invalid insights collection")

    sources = {
        f"P{i}": passage.text
        for i, (passage, _) in enumerate(candidates, 1)
    }

    for insight in insights:
        if not isinstance(insight, dict):
            raise ValueError("Invalid insight structure")

        passage_id = insight.get("passage_id")
        quote = insight.get("quote")

        if passage_id not in sources:
            raise ValueError(
                f"Unknown source: {passage_id}"
            )

        if (
            not isinstance(quote, str)
            or not quote.strip()
            or quote not in sources[passage_id]
        ):
            raise ValueError(
                f"Invalid source quotation: {passage_id}"
            )

        for field in ("application", "limitation", "next_step"):
            value = insight.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Missing or invalid field: {field}")

    return insights

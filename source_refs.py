
import re


def referenced_passage_numbers(
    answer: str,
    candidate_count: int
) -> list[int]:
    """
    Find valid passage IDs mentioned in the answer.

    Example:
        "Inversion (P4) helps. See [P2]."
        -> [2, 4]

    Important:
        A mentioned passage is not necessarily
        evidence that supports the claim.
    """

    numbers = {
        int(match)
        for match in re.findall(
            r"(?<!\w)P([1-9]\d*)(?!\w)",
            answer
        )
    }

    return sorted(
        number
        for number in numbers
        if number <= candidate_count
    )

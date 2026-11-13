
from source_refs import referenced_passage_numbers


def test_extracts_references():
    answer = "Inversion (P4) helps. See [P2] and P4."

    assert referenced_passage_numbers(
        answer, 8
    ) == [2, 4]


def test_no_local_references():
    answer = (
        "Vietnam's CPI was 5.09%, "
        "according to official web research."
    )

    assert referenced_passage_numbers(
        answer, 8
    ) == []


def test_ignores_nonexistent_passages():
    answer = "See P1 and P99."

    assert referenced_passage_numbers(
        answer, 8
    ) == [1]

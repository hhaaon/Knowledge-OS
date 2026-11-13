
from reader import Note
from chunker import extract_passages



def test_extract_sections_without_blank_lines():
    note = Note(
        relative_path="Thinking.md",
        content=(
            "# First Principles\n"
            "Question assumptions.\n"
            "# The Process\n"
            "Separate facts from beliefs.\n"
        )
    )

    passages = extract_passages(note)

    assert len(passages) == 2
    assert passages[0].text == (
        "# First Principles\nQuestion assumptions."
    )
    assert passages[1].text == (
        "# The Process\nSeparate facts from beliefs."
    )


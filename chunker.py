from dataclasses import dataclass
from reader import Note
import re


@dataclass(frozen=True)
class Passage:
    relative_path: str
    text: str

def extract_passages(note: Note) -> list[Passage]:
    """
    Split a Markdown note into meaningful passages.

    Requirements:
    - Preserve the source note's relative path.
    - Ignore empty passages.
    - Keep original text unchanged within passages.
    - Do not modify the original note.
    """

    sections = re.split(
        r"(?=^#{1,6}[ \t]+)",
        note.content,
        flags=re.MULTILINE
    )

    passages = [
        Passage(note.relative_path, section.strip())
        for section in sections
        if section.strip()
    ]

    return passages

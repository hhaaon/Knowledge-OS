
from pathlib import Path

from ollama import chat

from config import (
    MODEL,
    VAULT_PATH as ORIGINAL_VAULT,
    TEST_VAULT,
)


ENHANCEMENT_PROMPT = """
You are enhancing a Markdown knowledge note to support
deep understanding and long-term retention.

Your approach must work across different subjects.

OBJECTIVE

Produce a note that helps the reader:
1. Understand the important knowledge accurately.
2. Reconstruct it later without reading the note.
3. Apply it correctly in new situations.

CONTENT FIDELITY

- Preserve the original meaning.
- Preserve important facts, examples, qualifications,
  equations, code, links, and source references.
- Never invent facts, citations, or quotations.
- Do not silently correct uncertain claims.
- Preserve distinctions between facts, opinions,
  hypotheses, and personal observations.
- If the original text is unclear, preserve that
  uncertainty rather than making up an explanation.

ENHANCEMENT

- Improve clarity and organization when beneficial.
- Use headings appropriate to the actual content.
- Explain relationships and reasoning clearly.
- Remove unnecessary repetition without losing meaning.
- Do not force every subject into the same template.
- Do not add irrelevant examples or analogies.
- Preserve Markdown and Obsidian-compatible syntax.

ACTIVE RECALL

At the end, add a section titled:

## Test Your Understanding

Include 2-4 meaningful questions appropriate
to this note.

Questions should encourage the reader to:
- Explain important ideas from memory.
- Reconstruct reasoning or mechanisms.
- Identify important limitations.
- Apply knowledge in a new situation, if appropriate.

Do not put the answers immediately after the questions.
The reader should attempt retrieval independently.

OUTPUT

Return only the enhanced Markdown document.
Do not include commentary or an outer Markdown code fence.
"""


def enhance_markdown(original_text: str) -> str:
    """Generate an enhanced Markdown draft using Ollama."""

    if not original_text.strip():
        raise ValueError("Cannot enhance an empty note.")

    response = chat(
        model=MODEL,
        think=False,
        options={
            "temperature": 0.2,
            "num_ctx": 8192,
        },
        messages=[
            {
                "role": "system",
                "content": ENHANCEMENT_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Enhance the following note:\n\n"
                    + original_text
                ),
            },
        ],
    )

    result = (response.message.content or "").strip()

    if not result:
        raise RuntimeError("The LLM returned an empty note.")

    return result + "\n"


def enhance_one_note(
    original_vault: Path,
    test_vault: Path,
    relative_path: Path,
) -> Path:
    """
    Enhance one note safely.

    Reads from the original vault.
    Writes a new file only in the test vault.
    Never overwrites an existing enhanced note.
    """

    original_root = original_vault.resolve()
    test_root = test_vault.resolve()

    if (
        test_root == original_root
        or test_root.is_relative_to(original_root)
    ):
        raise ValueError(
            "Test vault must be separate from the original."
        )

    source = (original_root / relative_path).resolve()
    target = (test_root / relative_path).resolve()

    if not source.is_relative_to(original_root):
        raise ValueError("Source path escapes original vault.")

    if not target.is_relative_to(test_root):
        raise ValueError("Target path escapes test vault.")

    if not source.is_file():
        raise FileNotFoundError(source)

    if source.suffix.lower() != ".md":
        raise ValueError("Only Markdown notes are supported.")

    if target.exists():
        raise FileExistsError(
            f"Enhanced note already exists: {target}"
        )

    original_text = source.read_text(encoding="utf-8")

    enhanced_text = enhance_markdown(original_text)

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Exclusive creation: never overwrite an existing file.
    with target.open("x", encoding="utf-8") as file:
        file.write(enhanced_text)

    return target


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhance one Markdown note."
    )

    parser.add_argument(
        "note",
        type=Path,
        help="Note path relative to the original vault.",
    )

    args = parser.parse_args()

    output = enhance_one_note(
        original_vault=ORIGINAL_VAULT,
        test_vault=TEST_VAULT,
        relative_path=args.note,
    )

    print(f"Enhanced note created: {output}")
    print("Original note remains unchanged.")


from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Note:
    relative_path: str
    content: str


def load_notes(vault_path: Path) -> list[Note]:
    if not vault_path.is_dir():
        raise NotADirectoryError(
            f"Vault directory not found: {vault_path}"
        )

    notes = []

    for path in sorted(vault_path.rglob("*.md")):
        relative_path = path.relative_to(vault_path)

        if ".obsidian" in relative_path.parts:
            continue

        if path.is_symlink() or not path.is_file():
            continue

        try:
            content = path.read_text(encoding="utf-8")

            notes.append(
                Note(
                    relative_path=relative_path.as_posix(),
                    content=content
                )
            )

        except (OSError, UnicodeDecodeError) as e:
            print(f"Skipping {relative_path}: {e}")

    return notes

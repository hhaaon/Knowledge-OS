
import argparse
from pathlib import Path

from note_enhancer_v2 import (
    ORIGINAL_VAULT,
    TEST_VAULT,
    enhance_one_note_v2,
)


def select_notes(
    original_vault: Path,
    test_vault: Path,
    limit: int,
) -> list[Path]:
    """Choose notes that have not been enhanced yet."""

    if limit < 1:
        raise ValueError("Limit must be positive.")

    source_root = original_vault.resolve()
    test_root = test_vault.resolve()

    if (
        source_root == test_root
        or source_root.is_relative_to(test_root)
        or test_root.is_relative_to(source_root)
    ):
        raise ValueError("Vaults must be separate.")

    if not source_root.is_dir():
        raise FileNotFoundError(source_root)

    selected = []

    for source in sorted(source_root.rglob("*.md")):
        relative_path = source.relative_to(source_root)

        # Ignore Obsidian settings and Git internals.
        if any(
            part in {".obsidian", ".git"}
            for part in relative_path.parts
        ):
            continue

        # Avoid following symbolic links.
        if source.is_symlink() or not source.is_file():
            continue

        target = (
            test_root
            / "_experiments"
            / "v2"
            / relative_path
        )

        # Existing enhancements must remain untouched.
        if target.exists() or target.is_symlink():
            continue

        selected.append(relative_path)

        if len(selected) == limit:
            break

    return selected


def run_batch(
    original_vault: Path,
    test_vault: Path,
    limit: int = 3,
    execute: bool = False,
) -> int:
    notes = select_notes(original_vault, test_vault, limit)

    if not notes:
        print("No eligible notes found.")
        return 0

    print(f"Selected {len(notes)} notes.")

    if not execute:
        for note in notes:
            print(f"[PREVIEW] {note}")

        print("\nNo files changed. Use --run to enhance.")
        return 0

    successes = 0
    failures = 0

    for note in notes:
        try:
            output = enhance_one_note_v2(
                original_vault,
                test_vault,
                note,
            )

            print(f"[OK] {output}")
            successes += 1

        except Exception as error:
            print(f"[FAILED] {note}: {error}")
            failures += 1

    print(
        f"\nComplete: {successes} created, "
        f"{failures} failed."
    )

    return failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Safely batch-enhance Markdown notes."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Generate notes instead of previewing.",
    )

    args = parser.parse_args()

    failures = run_batch(
        ORIGINAL_VAULT,
        TEST_VAULT,
        limit=args.limit,
        execute=args.run,
    )

    raise SystemExit(1 if failures else 0)

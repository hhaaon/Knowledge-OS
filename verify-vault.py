
from config import VAULT_PATH
from reader import load_notes


def main() -> int:
    """Verify that the configured knowledge vault is readable."""

    print("Knowledge OS — Vault Verification\n")

    if not VAULT_PATH.is_dir():
        print(f"ERROR: Vault directory not found: {VAULT_PATH}")
        print(
            "Configure KNOWLEDGE_OS_VAULT_PATH "
            "to point to your Markdown notes."
        )
        return 1

    try:
        notes = load_notes(VAULT_PATH)
    except OSError as error:
        print(f"ERROR: Failed to read vault: {error}")
        return 1

    print(f"Vault: {VAULT_PATH}")
    print(f"Markdown notes loaded: {len(notes)}")

    if not notes:
        print("WARNING: No readable Markdown notes found.")
        return 1

    print("\nVault verification successful.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

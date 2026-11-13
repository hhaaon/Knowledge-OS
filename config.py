import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

VAULT_PATH = Path(
    os.getenv(
        "KNOWLEDGE_OS_VAULT_PATH",
        str(PROJECT_ROOT / "local_data" / "vault"),
    )
).expanduser().resolve()

TEST_VAULT = Path(
    os.getenv(
        "KNOWLEDGE_OS_TEST_VAULT_PATH",
        str(PROJECT_ROOT / "local_data" / "enhanced"),
    )
).expanduser().resolve()

MODEL = os.getenv(
    "KNOWLEDGE_OS_MODEL",
    "qwen3.5:4b-q4_K_M",
)
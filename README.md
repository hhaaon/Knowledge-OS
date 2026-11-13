# Knowledge OS

**A local-first, AI-assisted personal knowledge management application.**

Knowledge OS helps you understand, organize, explore, and learn from knowledge stored in Markdown files.

The project currently supports Obsidian vaults and uses local language models for knowledge discovery, note enhancement, and active-recall evaluation.

## Features

- **Knowledge Discovery:** Ask questions and explore potentially relevant information from your existing notes.
- **Knowledge Library:** Browse notes by folder and read their contents.
- **AI Note Enhancement:** Generate learning-oriented versions of Markdown notes with active-recall questions.
- **Batch Enhancement:** Enhance multiple notes while preserving the originals.
- **Active Recall Evaluation:** Answer learning questions and receive AI-assisted feedback.
- **Optional Web Research:** Use Tavily to supplement local knowledge when internet research is enabled.

## Technology Stack

- Python 3.13
- Streamlit
- Ollama with Qwen
- Sentence Transformers
- NumPy
- Pydantic
- pytest
- Tavily (optional)

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd Knowledge-OS
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

These commands are for Windows PowerShell.

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Install and configure Ollama

Install Ollama from https://ollama.com.

Make sure the local model configured in `config.py` is available. The current default is:

```text
qwen3.5:4b-q4_K_M
```

### 5. Configure your knowledge vault

Set environment variables for the current PowerShell session:

```powershell
$env:KNOWLEDGE_OS_VAULT_PATH = "C:\path\to\your\vault"
$env:KNOWLEDGE_OS_TEST_VAULT_PATH = "C:\path\to\enhanced-notes"
```

Alternatively, the application defaults to `local_data/vault` and `local_data/enhanced` under the project directory.

The original vault is treated as read-only by the application. Enhanced notes are written to a separate directory.

### 6. Verify your vault

```powershell
python verify-vault.py
```

### 7. Start Knowledge OS

```powershell
streamlit run app.py
```

The Knowledge Library is available through Streamlit's page navigation.

### 8. Enhance notes

Preview a batch:

```powershell
python batch_enhance.py --limit 3
```

Generate enhanced notes:

```powershell
python batch_enhance.py --limit 3 --run
```

Enhance a specific note:

```powershell
python note_enhancer_v2.py "relative/path/to/note.md"
```

Existing enhanced notes are not automatically overwritten.

### 9. Practice active recall

```powershell
streamlit run review_app.py
```

The recall interface lets you select an enhanced note, answer a learning question, and review an LLM-generated assessment.

## Running Tests

Run automated tests:

```powershell
python -m pytest -q
```

Live LLM regression tests are opt-in because they require a running local model:

```powershell
$env:RUN_LLM_TESTS = "1"
python -m pytest tests/test_recall_live.py -v
Remove-Item Env:RUN_LLM_TESTS
```

## Privacy

Knowledge OS is designed for local-first use.

- The original Markdown vault is not modified by the current note-processing workflows.
- Note enhancement and recall evaluation use a local Ollama model.
- Internet research is optional and can send queries to Tavily.
- Users should not commit personal vault contents, API keys, or generated private notes to Git.

## Known Limitations

Knowledge OS is an early personal-use application.

- LLM answers and evaluations may contain errors.
- Generated insights require user verification.
- Active-recall results are not yet persisted.
- Spaced repetition is not implemented.
- Advanced knowledge-connection discovery remains experimental.
- Public hosting, authentication, and multi-user access are not supported.

## Project Status

**Early development — local-first personal application.**

The current focus is reliability, reproducible installation, and improving the usefulness of existing functionality.
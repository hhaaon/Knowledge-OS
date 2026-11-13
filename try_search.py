
from pathlib import Path
from collections import defaultdict
import re

import numpy as np
from sentence_transformers import SentenceTransformer

from reader import load_notes
from chunker import extract_passages
from evaluator import build_evaluation_prompt
from local_llm import generate_local
from config import VAULT_PATH


# Configuration
SITUATION = "I'm 23. Is it too early to start a business?"
MAX_CANDIDATES = 8


def select_candidates(passages, scores, limit=8):
    ranked_indices = np.argsort(scores)[::-1]

    candidates = []
    note_counts = defaultdict(int)

    for index in ranked_indices:
        passage = passages[index]
        path = passage.relative_path
        text = passage.text.strip()

        # Skip templates
        if path.startswith("Templates/"):
            continue

        # Skip creation-date-only passages
        if re.fullmatch(
            r"(?is)#{1,6}[ \t]+Date created\s*\n"
            r"\s*\d{1,2}[-/]\d{1,2}[-/]\d{4}",
            text
        ):
            continue

        # Maximum 2 passages per note
        if note_counts[path] >= 2:
            continue

        candidates.append((passage, float(scores[index])))
        note_counts[path] += 1

        if len(candidates) >= limit:
            break

    return candidates


def main():
    # 1. Read Obsidian vault
    notes = load_notes(VAULT_PATH)
    print(f"Loaded {len(notes)} notes")

    # 2. Extract passages
    passages = [
        passage
        for note in notes
        for passage in extract_passages(note)
    ]

    print(f"Extracted {len(passages)} passages")

    if not passages:
        print("No passages found.")
        return

    # 3. Generate embeddings
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    embeddings = model.encode_document(
        [p.text for p in passages],
        normalize_embeddings=True,
        show_progress_bar=True
    )

    # 4. Search by meaning
    query_embedding = model.encode_query(
        SITUATION,
        normalize_embeddings=True
    )

    scores = embeddings @ query_embedding

    # 5. Select candidate knowledge
    candidates = select_candidates(
        passages,
        scores,
        limit=MAX_CANDIDATES
    )

    if not candidates:
        print("No candidate passages found.")
        return

    print("\n=== Retrieved Knowledge ===")

    for i, (passage, score) in enumerate(candidates, 1):
        print(f"\nP{i}: {passage.relative_path}")
        print(f"Similarity: {score:.3f}")
        print(passage.text[:300])

    # 6. Build evaluation prompt
    prompt = build_evaluation_prompt(
        SITUATION,
        candidates
    )

    # 7. Ask local LLM
    print("\n=== Knowledge OS is thinking ===\n")

    answer = generate_local(prompt)

    # 8. Display result
    print("=== Knowledge OS Result ===\n")
    print(answer)


if __name__ == "__main__":
    main()

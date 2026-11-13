
import re

import streamlit as st
from sentence_transformers import SentenceTransformer

from reader import load_notes
from chunker import extract_passages
from try_search import VAULT_PATH, select_candidates
from evidence_selector import select_useful_passages
from source_refs import referenced_passage_numbers
from agent import run_agent


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Knowledge OS",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 Knowledge OS")

st.caption(
    "Use your knowledge to understand problems, "
    "make better decisions, and take action."
)


# ============================================================
# Load Obsidian Knowledge
# ============================================================

@st.cache_resource(show_spinner=False)
def load_knowledge():
    """
    Read Obsidian notes and prepare semantic embeddings.

    The original vault remains read-only.
    """

    notes = load_notes(VAULT_PATH)

    passages = [
        passage
        for note in notes
        for passage in extract_passages(note)
    ]

    if not passages:
        raise ValueError(
            "No Markdown passages found in the vault."
        )

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    embeddings = model.encode_document(
        [passage.text for passage in passages],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return model, passages, embeddings, len(notes)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header("Knowledge Base")

    if st.button(
        "Reload Obsidian vault",
        use_container_width=True,
    ):
        load_knowledge.clear()

        st.session_state.pop("discovery", None)
        st.session_state.pop("feedback", None)

        st.rerun()


with st.spinner("Loading your knowledge..."):
    model, passages, embeddings, note_count = load_knowledge()

with st.sidebar:
    st.caption(f"{note_count} Obsidian notes available")


# ============================================================
# Extract Web Sources Referenced in the Answer
# ============================================================

def get_referenced_web_sources(
    answer: str,
    web_sources: str,
) -> list[tuple[str, str]]:
    """
    Return web sources explicitly referenced in the answer.

    A citation is only a reference, not proof that
    the source supports the generated claim.
    """

    if not web_sources:
        return []

    results = []

    blocks = re.split(
        r"(?=^\[W\d+\]\s)",
        web_sources,
        flags=re.MULTILINE,
    )

    for block in blocks:

        header = re.search(
            r"^\[W(\d+)\]\s*(.+)$",
            block,
            flags=re.MULTILINE,
        )

        url_match = re.search(
            r"^URL:\s*(https?://\S+)",
            block,
            flags=re.MULTILINE,
        )

        if not header or not url_match:
            continue

        number = header.group(1)
        title = header.group(2).strip()
        url = url_match.group(1).strip()

        # Qwen may cite [W1] or include the source URL.
        referenced = (
            f"[W{number}]" in answer
            or url in answer
        )

        if referenced:
            results.append((title, url))

    # Remove duplicate URLs while preserving order.
    unique = []
    seen = set()

    for title, url in results:
        if url not in seen:
            unique.append((title, url))
            seen.add(url)

    return unique


# ============================================================
# User Input
# ============================================================

st.subheader("What would you like to understand?")

situation = st.text_area(
    "Your question or situation",
    placeholder=(
        "Example: I'm 23. Is it too early "
        "to start a business?"
    ),
    height=130,
    label_visibility="collapsed",
)

allow_web = st.checkbox(
    "Allow internet research",
    value=False,
    help=(
        "Knowledge OS may use Tavily to research "
        "information that your notes cannot provide. "
        "Search queries are sent to an external service."
    ),
)


# ============================================================
# Knowledge Discovery
# ============================================================

if st.button(
    "Find useful insights",
    type="primary",
    use_container_width=True,
):

    if not situation.strip():

        st.warning(
            "Please enter a question or describe "
            "your situation."
        )

    else:

        try:

            # ------------------------------------------------
            # 1. Retrieve candidate passages
            # ------------------------------------------------

            with st.spinner("Searching your knowledge..."):

                query_embedding = model.encode_query(
                    situation,
                    normalize_embeddings=True,
                )

                scores = embeddings @ query_embedding

                retrieved_candidates = select_candidates(
                    passages,
                    scores,
                    limit=8,
                )

            # ------------------------------------------------
            # 2. Select useful knowledge
            # ------------------------------------------------

            with st.spinner("Evaluating relevant knowledge..."):

                selected_candidates = select_useful_passages(
                    situation=situation,
                    candidates=retrieved_candidates,
                )

            # ------------------------------------------------
            # 3. Generate answer
            # ------------------------------------------------

            with st.spinner("Analyzing your question..."):

                answer, web_sources = run_agent(
                    situation=situation,
                    candidates=selected_candidates,
                    allow_web=allow_web,
                )

            # ------------------------------------------------
            # 4. Store discovery in session
            # ------------------------------------------------

            st.session_state["discovery"] = {
                "situation": situation,
                "answer": answer,
                "candidates": selected_candidates,
                "web_sources": web_sources,
            }

            # Clear previous evaluation.
            st.session_state.pop("feedback", None)

        except Exception as exc:

            st.error(
                "Knowledge OS couldn't complete "
                f"the request: {exc}"
            )


# ============================================================
# Display Discovery
# ============================================================

if "discovery" in st.session_state:

    discovery = st.session_state["discovery"]

    answer = discovery["answer"]
    candidates = discovery["candidates"]
    web_sources = discovery["web_sources"]

    st.divider()

    # --------------------------------------------------------
    # 1. Answer
    # --------------------------------------------------------

    st.subheader("💡 Answer")

    st.markdown(answer)

    # --------------------------------------------------------
    # 2. Find referenced knowledge
    # --------------------------------------------------------

    referenced_ids = referenced_passage_numbers(
        answer,
        len(candidates),
    )

    # --------------------------------------------------------
    # 3. Find referenced internet sources
    # --------------------------------------------------------

    referenced_web_sources = get_referenced_web_sources(
        answer,
        web_sources,
    )

    # --------------------------------------------------------
    # 4. Display only referenced Obsidian passages
    # --------------------------------------------------------

    if referenced_ids:

        st.subheader("📚 Supporting Knowledge")

        st.caption(
            "These notes were referenced in the answer. "
            "Their support for individual claims "
            "has not been independently verified."
        )

        for number in referenced_ids:

            passage, _ = candidates[number - 1]

            with st.expander(
                passage.relative_path
            ):
                st.code(
                    passage.text,
                    language="markdown",
                )

    # --------------------------------------------------------
    # 5. Display only referenced web sources
    # --------------------------------------------------------

    if referenced_web_sources:

        st.subheader("🌐 Research Sources")

        for title, url in referenced_web_sources:

            st.link_button(
                title,
                url,
            )

    elif web_sources:

        st.caption(
            "Internet research was performed, "
            "but the answer did not cite "
            "an identifiable source."
        )

    # --------------------------------------------------------
    # 6. Customer Feedback
    # --------------------------------------------------------

    st.divider()

    st.subheader("Was this answer useful?")

    feedback = st.radio(
        "Evaluate the answer",
        options=[
            "Very useful",
            "Somewhat useful",
            "Not useful",
        ],
        index=None,
        key="feedback",
        label_visibility="collapsed",
    )

    if feedback:

        st.success("Thank you for your feedback.")

        st.caption(
            "Your evaluation is stored "
            "for this session only."
        )

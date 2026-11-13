
import re

import streamlit as st

from config import VAULT_PATH, TEST_VAULT
from reader import load_notes
from note_library import read_enhanced_note
from recall_evaluator import evaluate_recall


def get_first_question(enhanced_text: str) -> str:
    """Extract the first question from an enhanced note."""

    sections = re.split(
        r"(?m)^## Test Your Understanding[ \t]*$",
        enhanced_text,
        maxsplit=1,
    )

    if len(sections) != 2:
        raise ValueError("Recall section not found.")

    for line in sections[1].splitlines():
        if line.startswith("#"):
            break

        match = re.match(
            r"^\s*\d+[.)]\s+(.+?)\s*$",
            line,
        )

        if match:
            return match.group(1)

    raise ValueError("No recall questions found.")


st.set_page_config(
    page_title="Knowledge OS — Recall",
    page_icon="🧠",
)

st.title("🧠 Knowledge Recall")
st.caption("Practice remembering your knowledge.")


# 1. Find notes that have enhanced versions.

try:
    original_notes = load_notes(VAULT_PATH)

    enhanced_root = (
        TEST_VAULT / "_experiments" / "v2"
    )

    available_notes = {
        note.relative_path: note
        for note in original_notes
        if (enhanced_root / note.relative_path).is_file()
    }

except OSError as error:
    st.error(f"Cannot load knowledge vault: {error}")
    st.stop()


if not available_notes:
    st.info(
        "No enhanced notes available yet. "
        "Enhance a note before starting a review."
    )
    st.stop()


# 2. Let the user select a note.

selected_path = st.selectbox(
    "Choose a note to review",
    options=sorted(available_notes),
)

selected_note = available_notes[selected_path]

try:
    enhanced_note = read_enhanced_note(
        TEST_VAULT,
        selected_path,
    )

    if enhanced_note is None:
        raise ValueError("Enhanced version not found.")

    question = get_first_question(enhanced_note)

except (OSError, ValueError) as error:
    st.error(f"Cannot prepare review: {error}")
    st.stop()


# 3. Clear previous feedback when switching notes.

review_context = (selected_path, question)

if st.session_state.get("review_context") != review_context:
    st.session_state["review_context"] = review_context

    for key in (
        "recall_result",
        "final_rating",
        "confirmed_rating",
    ):
        st.session_state.pop(key, None)


# 4. Recall from memory.

st.subheader("Recall from memory")
st.write(question)

answer = st.text_area(
    "Your answer",
    height=150,
    placeholder="Explain in your own words...",
    key=f"answer::{selected_path}",
)

if st.button(
    "Evaluate my answer",
    disabled=not answer.strip(),
):
    try:
        with st.spinner("Evaluating..."):
            feedback = evaluate_recall(
                question=question,
                learner_answer=answer.strip(),
                reference_note=selected_note.content,
            )

        st.session_state["recall_result"] = {
            "answer": answer.strip(),
            "feedback": feedback.model_dump(),
        }

        st.session_state["final_rating"] = feedback.verdict
        st.session_state.pop("confirmed_rating", None)

    except Exception as error:
        st.error(f"Evaluation failed: {error}")


# 5. Display feedback only for the submitted answer.

result = st.session_state.get("recall_result")

if result and result["answer"] == answer.strip():
    feedback = result["feedback"]

    st.subheader("LLM Feedback")

    st.write(
        f"**Assessment:** {feedback['verdict'].title()}"
    )

    st.write(feedback["explanation"])

    if feedback["missing_or_incorrect"]:
        st.write(
            "**Missing or incorrect:** "
            + feedback["missing_or_incorrect"]
        )

    with st.expander("Compare with the original note"):
        st.markdown(selected_note.content)

    st.subheader("Your final judgment")

    final_rating = st.radio(
        "How well did you remember?",
        options=("correct", "partial", "incorrect"),
        format_func=str.title,
        key="final_rating",
    )

    if st.button("Confirm assessment"):
        st.session_state["confirmed_rating"] = final_rating

    if "confirmed_rating" in st.session_state:
        st.success(
            "Confirmed: "
            + st.session_state["confirmed_rating"].title()
        )

        st.caption(
            "This result is stored in the current "
            "session only."
        )

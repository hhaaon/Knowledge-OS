
from pathlib import Path

import streamlit as st

from reader import load_notes
from note_library import (
    list_folders,
    notes_in_folder,
    read_enhanced_note,
    read_approved_note,
)
from note_enhancer_v2 import (
    propose_enhancement,
    save_approved_enhancement,
)
from try_search import VAULT_PATH
from note_enhancer import TEST_VAULT


PROPOSAL_KEY = "knowledge_library_enhancement_proposal"

st.set_page_config(
    page_title="Knowledge Library",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Knowledge Library")
st.caption("Browse, read, and improve your personal knowledge.")


@st.cache_data(show_spinner=False)
def get_library_notes(vault_path: str):
    return load_notes(Path(vault_path))


if st.button("Reload library"):
    get_library_notes.clear()
    st.session_state.pop(PROPOSAL_KEY, None)
    st.rerun()


try:
    notes = get_library_notes(str(VAULT_PATH))
except (OSError, ValueError) as error:
    st.error(f"Could not load your vault: {error}")
    st.stop()

st.caption(f"{len(notes)} notes available")

if not notes:
    st.info("No Markdown notes found.")
    st.stop()


# 1. Select a folder and note

folders = list_folders(notes)

selected_folder = st.selectbox(
    "Folder",
    options=folders,
)

folder_notes = notes_in_folder(notes, selected_folder)

if not folder_notes:
    st.info("No notes in this folder.")
    st.stop()

note_by_path = {
    note.relative_path: note
    for note in folder_notes
}

selected_path = st.selectbox(
    "Note",
    options=list(note_by_path),
)

selected_note = note_by_path[selected_path]


# 2. Clear proposals belonging to another note

draft = st.session_state.get(PROPOSAL_KEY)

if draft is not None:
    if (
        draft["path"] != selected_path
        or draft["original_text"] != selected_note.content
    ):
        st.session_state.pop(PROPOSAL_KEY, None)
        draft = None


# 3. Read existing versions

try:
    experimental_text = read_enhanced_note(
        TEST_VAULT,
        selected_path,
    )
except (OSError, UnicodeError, ValueError) as error:
    st.warning(f"Experimental version unavailable: {error}")
    experimental_text = None

try:
    approved_text = read_approved_note(
        TEST_VAULT,
        selected_path,
    )
except (OSError, UnicodeError, ValueError) as error:
    st.warning(f"Approved version unavailable: {error}")
    approved_text = None


# 4. Display selected version

versions = ["Original"]

if approved_text is not None:
    versions.append("Approved enhancement")

if experimental_text is not None:
    versions.append("Enhanced V2 (experiment)")

selected_version = st.radio(
    "Version",
    options=versions,
    horizontal=True,
)

st.divider()

st.subheader(Path(selected_path).stem)
st.caption(selected_path)

if selected_version == "Approved enhancement":
    displayed_text = approved_text
elif selected_version == "Enhanced V2 (experiment)":
    displayed_text = experimental_text
else:
    displayed_text = selected_note.content

if displayed_text and displayed_text.strip():
    st.markdown(displayed_text)
else:
    st.info("This note is empty.")


# 5. Enhancement workflow

st.divider()
st.subheader("✨ Enhance this note")
st.caption(
    "Generate an improved explanation and active-recall "
    "questions. Nothing is saved until you accept."
)

if st.session_state.pop("enhancement_saved", False):
    st.success("Approved enhancement saved successfully.")

if approved_text is not None:
    st.info(
        "This note already has an approved enhancement. "
        "Overwriting approved notes is not supported yet."
    )
else:
    if st.button(
        "Generate enhancement",
        disabled=(
            not selected_note.content.strip()
            or draft is not None
        ),
    ):
        try:
            with st.spinner("Generating enhancement proposal..."):
                proposed_text = propose_enhancement(
                    selected_note.content
                )

            st.session_state[PROPOSAL_KEY] = {
                "path": selected_path,
                "original_text": selected_note.content,
                "enhanced_text": proposed_text,
            }

            draft = st.session_state[PROPOSAL_KEY]

        except (ValueError, RuntimeError, Exception) as error:
            st.error(f"Enhancement generation failed: {error}")


# 6. Review and approve the proposal

if draft is not None and approved_text is None:
    st.markdown("### Review proposed changes")
    st.warning(
        "AI-generated improvements may contain mistakes. "
        "Review them before accepting."
    )

    original_col, proposed_col = st.columns(2)

    with original_col:
        st.markdown("**Original note**")

        with st.container(height=450):
            st.markdown(draft["original_text"])

    with proposed_col:
        st.markdown("**Proposed enhancement**")

        with st.container(height=450):
            st.markdown(draft["enhanced_text"])

    accept_col, reject_col = st.columns(2)

    with accept_col:
        if st.button(
            "Accept and save",
            type="primary",
            use_container_width=True,
        ):
            try:
                save_approved_enhancement(
                    original_vault=Path(VAULT_PATH),
                    test_vault=Path(TEST_VAULT),
                    relative_path=Path(selected_path),
                    enhanced_text=draft["enhanced_text"],
                    expected_original_text=draft["original_text"],
                )

            except (OSError, UnicodeError, ValueError) as error:
                st.error(f"Could not save enhancement: {error}")

            else:
                st.session_state.pop(PROPOSAL_KEY, None)
                st.session_state["enhancement_saved"] = True
                st.rerun()

    with reject_col:
        if st.button(
            "Reject",
            use_container_width=True,
        ):
            st.session_state.pop(PROPOSAL_KEY, None)
            st.rerun()

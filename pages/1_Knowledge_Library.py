
from pathlib import Path

import streamlit as st

from reader import load_notes
from note_library import (
    list_folders,
    notes_in_folder,
    read_enhanced_note,
)
from try_search import VAULT_PATH
from note_enhancer import TEST_VAULT


st.set_page_config(
    page_title="Knowledge Library",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Knowledge Library")
st.caption("Browse and read your personal knowledge.")


@st.cache_data(show_spinner=False)
def get_library_notes(vault_path: str):
    return load_notes(Path(vault_path))


if st.button("Reload library"):
    get_library_notes.clear()
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


# 1. Browse folders
folders = list_folders(notes)

selected_folder = st.selectbox(
    "Folder",
    options=folders,
)

# 2. Select a note
folder_notes = notes_in_folder(
    notes,
    selected_folder,
)

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


# 3. Look for an enhanced version
try:
    enhanced_text = read_enhanced_note(
        TEST_VAULT,
        selected_note.relative_path,
    )
except (OSError, UnicodeError, ValueError) as error:
    st.warning(f"Enhanced note unavailable: {error}")
    enhanced_text = None


# 4. Choose version
versions = ["Original"]

if enhanced_text is not None:
    versions.append("Enhanced V2")

selected_version = st.radio(
    "Version",
    options=versions,
    horizontal=True,
)

st.divider()

st.subheader(Path(selected_note.relative_path).stem)
st.caption(selected_note.relative_path)

if selected_version == "Enhanced V2":
    displayed_text = enhanced_text
else:
    displayed_text = selected_note.content

if displayed_text.strip():
    st.markdown(displayed_text)
else:
    st.info("This note is empty.")

import streamlit as st

# ---------- Page Config ----------
st.set_page_config(
    page_title="RepoMind RAG",
    page_icon="🔍",
    layout="centered",
)

# ---------- Session State ----------
if "history" not in st.session_state:
    st.session_state.history = []  # list of (question, answer) tuples

# ---------- Title ----------
st.title("🔍 RepoMind RAG")
st.caption("Ask questions about your codebase — locally or from a remote repository.")

st.divider()

# ---------- Input Section ----------
st.subheader("1. Choose Repository Source")

source_type_display = st.radio(
    "Method",
    options=["Local", "Remote"],
    horizontal=True,
    label_visibility="collapsed",
)
source_type = source_type_display.lower()  # "local" or "remote", matches IngestRequest

path = ""
url = None
branch = "main"

if source_type == "local":
    path = st.text_input("Local Path", placeholder="e.g. /home/user/my-project")
    branch = st.text_input("Branch (optional)", value="main")

else:  # remote
    path = st.text_input("Path", placeholder="e.g. /destination/folder")
    url = st.text_input("Repository URL", placeholder="e.g. https://github.com/user/repo.git")
    branch = st.text_input("Branch (optional)", value="main")

st.subheader("2. Ask Your Question")
question = st.text_area("Query", placeholder="Type your question about the codebase here...", height=100)

st.divider()

submit = st.button("Submit Query", use_container_width=True)

# ---------- Submit Logic ----------
if submit:
    if source_type == "local" and not path:
        st.warning("Please provide the local path.")
    elif source_type == "remote" and (not path or not url):
        st.warning("Please provide both the path and the repository URL.")
    elif not question.strip():
        st.warning("Please enter a query.")
    else:
        # Placeholder for actual RAG backend call.
        # Replace this block with requests.post() calls to your FastAPI
        # /ingest and /query endpoints, using the IngestRequest / QueryRequest
        # fields shown below.
        ingest_payload = {
            "source_type": source_type,
            "path": path,
            "url": url,
            "branch": branch or "main",
        }
        query_payload = {
            "question": question,
        }
        answer = (
            f"[Placeholder answer]\n\n"
            f"source_type: {ingest_payload['source_type']}\n"
            f"path: {ingest_payload['path']}\n"
            + (f"url: {ingest_payload['url']}\n" if source_type == "remote" else "")
            + f"branch: {ingest_payload['branch']}\n\n"
            f"This is where /query's 'answer' field will appear."
        )
        st.session_state.history.append((question, answer))

# ---------- Output Section ----------
if st.session_state.history:
    st.subheader("Output")
    latest_question, latest_answer = st.session_state.history[-1]

    st.markdown("**Your Question:**")
    st.info(latest_question)

    st.markdown("**Response:**")
    st.success(latest_answer)
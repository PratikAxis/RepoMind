import os
import requests
import streamlit as st

# ---------- Page Config ----------
st.set_page_config(
    page_title="RepoMind RAG",
    page_icon="🔍",
    layout="centered",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000").rstrip("/")

# ---------- Session State ----------
if "history" not in st.session_state:
    st.session_state.history = []  # list of (question, answer) tuples

if "ingested_repo" not in st.session_state:
    st.session_state.ingested_repo = None

# ---------- Sidebar / Backend Status ----------
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown(f"**Backend Endpoint:** `{BACKEND_URL}`")
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if res.status_code == 200:
            st.success("🟢 Backend Connected")
        else:
            st.warning(f"🟡 Backend Status Code: {res.status_code}")
    except Exception:
        st.error("🔴 Backend Disconnected")

    if st.button("Clear History"):
        st.session_state.history = []
        st.session_state.ingested_repo = None
        st.rerun()

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
        ingest_payload = {
            "source_type": source_type,
            "path": path,
            "url": url if source_type == "remote" else None,
            "branch": branch or "main",
        }
        query_payload = {
            "question": question,
        }

        current_repo_key = f"{source_type}:{path}:{url}:{branch}"
        ingest_success = True

        # Check if we need to run /ingest
        if st.session_state.ingested_repo != current_repo_key:
            with st.spinner("Ingesting codebase context..."):
                try:
                    ingest_res = requests.post(f"{BACKEND_URL}/ingest", json=ingest_payload, timeout=120)
                    if ingest_res.status_code == 200:
                        data = ingest_res.json()
                        st.session_state.ingested_repo = current_repo_key
                        st.toast(f"Ingestion successful! Loaded {data.get('documents_loaded', 0)} files, {data.get('chunks_created', 0)} chunks.", icon="✅")
                    else:
                        ingest_success = False
                        detail = ingest_res.json().get("detail", ingest_res.text)
                        st.error(f"Ingestion Failed ({ingest_res.status_code}): {detail}")
                except Exception as e:
                    ingest_success = False
                    st.error(f"Failed to connect to backend at {BACKEND_URL}: {str(e)}")

        if ingest_success:
            with st.spinner("Querying RAG model..."):
                try:
                    query_res = requests.post(f"{BACKEND_URL}/query", json=query_payload, timeout=120)
                    if query_res.status_code == 200:
                        answer_data = query_res.json()
                        answer = answer_data.get("answer", "No answer returned.")
                        st.session_state.history.append((question, answer))
                    else:
                        detail = query_res.json().get("detail", query_res.text)
                        st.error(f"Query Failed ({query_res.status_code}): {detail}")
                except Exception as e:
                    st.error(f"Failed to connect to backend at {BACKEND_URL}: {str(e)}")

# ---------- Output Section ----------
if st.session_state.history:
    st.subheader("Output")
    latest_question, latest_answer = st.session_state.history[-1]

    st.markdown("**Your Question:**")
    st.info(latest_question)

    st.markdown("**Response:**")
    st.success(latest_answer)

    if len(st.session_state.history) > 1:
        with st.expander("Previous Q&A History"):
            for idx, (q, a) in enumerate(reversed(st.session_state.history[:-1])):
                st.markdown(f"**Q:** {q}")
                st.markdown(f"**A:** {a}")
                st.divider()
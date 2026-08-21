import os
import requests
import streamlit as st

# ---------- Page Config ----------
st.set_page_config(
    page_title="RepoMind RAG",
    page_icon="",
    layout="wide",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000").rstrip("/")

# ---------- Session State ----------
if "history" not in st.session_state:
    st.session_state.history = []  # list of (question, answer) tuples

if "ingested_repo" not in st.session_state:
    st.session_state.ingested_repo = None

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Configuration")
    st.caption(f"Backend: {BACKEND_URL}")
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if res.status_code == 200:
            st.success("Backend connected")
        else:
            st.warning(f"Backend returned {res.status_code}")
    except Exception:
        st.error("Backend disconnected")

    st.divider()
    if st.button("Clear History"):
        st.session_state.history = []
        st.session_state.ingested_repo = None
        st.rerun()

# ---------- Title ----------
st.title("RepoMind")
st.caption("Ask questions about a GitHub repository and get answers from its indexed code context.")

st.divider()

# ---------- Repository Input ----------
with st.container():
    st.subheader("1. Choose Repository")

    url = st.text_input("Repository URL", placeholder="https://github.com/user/repo.git")
    clone_dir = st.text_input("Clone Directory", placeholder="/tmp/repos", value="/tmp/repos")
    branch = st.text_input("Branch", value="main")

# ---------- Question Input ----------
with st.container():
    st.subheader("2. Ask a Question")
    question = st.text_area(
        "Query",
        placeholder="Type your question about the codebase here...",
        height=110,
    )

    submit = st.button("Submit Query", use_container_width=True)

# ---------- Submit Logic ----------
if submit:
    if not url.strip():
        st.warning("Please provide the repository URL.")
    elif not clone_dir.strip():
        st.warning("Please provide a directory to clone the repository into.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        ingest_payload = {
            "url": url,
            "clone_dir": clone_dir,
            "branch": branch or "main",
        }
        query_payload = {"question": question}

        current_repo_key = f"{url}:{branch}"
        ingest_success = True

        # Only re-ingest if the repo/branch changed
        if st.session_state.ingested_repo != current_repo_key:
            with st.spinner("Cloning and indexing the repository..."):
                try:
                    ingest_res = requests.post(f"{BACKEND_URL}/ingest", json=ingest_payload, timeout=120)
                    if ingest_res.status_code == 200:
                        data = ingest_res.json()
                        st.session_state.ingested_repo = current_repo_key
                        st.success(
                            f"Repository ready. "
                            f"Loaded {data.get('documents_loaded', 0)} files, "
                            f"{data.get('chunks_created', 0)} chunks."
                        )
                    else:
                        ingest_success = False
                        detail = ingest_res.json().get("detail", ingest_res.text)
                        st.error(f"Ingestion failed: {detail}")
                except Exception as e:
                    ingest_success = False
                    st.error(f"Could not reach the backend: {e}")

        if ingest_success:
            with st.spinner("Generating answer..."):
                try:
                    query_res = requests.post(f"{BACKEND_URL}/query", json=query_payload, timeout=120)
                    if query_res.status_code == 200:
                        answer = query_res.json().get("answer", "No answer returned.")
                        st.session_state.history.append((question, answer))
                    else:
                        detail = query_res.json().get("detail", query_res.text)
                        st.error(f"Query failed: {detail}")
                except Exception as e:
                    st.error(f"Could not reach the backend: {e}")

# ---------- Answer Output ----------
if st.session_state.history:
    st.divider()
    st.subheader("Answer")
    latest_question, latest_answer = st.session_state.history[-1]

    st.markdown("**Question**")
    st.write(latest_question)

    st.markdown("**Response**")
    st.text_area("", latest_answer, height=180, label_visibility="collapsed")

    if len(st.session_state.history) > 1:
        with st.expander("Previous questions"):
            for q, a in reversed(st.session_state.history[:-1]):
                st.markdown("**Q:**")
                st.write(q)
                st.markdown("**A:**")
                st.write(a)
                st.divider()
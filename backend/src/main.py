from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT_DIR / ".env")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.configs.data_ingestion import load_remote_repo
from backend.configs.chunking import text_chunks
from backend.configs.embedding import get_embedding_model
from backend.configs.vector_store import init_vector_store
from backend.configs.generator import response_generator, get_llm

app = FastAPI(title="RepoMind RAG API", description="API to ingest codebases and query them using RAG.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "RepoMind Backend"}


@app.get("/debug")
async def debug():
    import sqlite3, sys, os
    try:
        import chromadb
        chroma_ver = chromadb.__version__
    except Exception as e:
        chroma_ver = str(e)
    return {
        "python_version": sys.version,
        "sqlite_version": sqlite3.sqlite_version,
        "chromadb_version": chroma_ver,
        "cwd": os.getcwd(),
    }


class IngestRequest(BaseModel):
    url: str           # GitHub/GitLab repo URL
    clone_dir: str     # Local directory to clone the repo into
    branch: str = "main"


class QueryRequest(BaseModel):
    question: str


@app.post("/ingest")
async def ingest_repo(request: IngestRequest):
    try:
        # 1. Clone repo and load documents
        docs = load_remote_repo(request.url, request.clone_dir, request.branch)

        if not docs:
            raise HTTPException(status_code=404, detail="No documents found. Check the URL and branch.")

        # 2. Split into chunks
        chunks = text_chunks(docs)

        # 3. Get embedding model
        embedding_model = get_embedding_model()

        # 4. Close old vector store if any (prevents SQLite lock)
        if hasattr(app.state, "vector_store") and app.state.vector_store is not None:
            try:
                app.state.vector_store._client.close()
            except Exception:
                pass
            app.state.vector_store = None
            import gc
            gc.collect()

        # 5. Build vector store and RAG chain
        vector_store = init_vector_store(chunks, embedding_model)
        app.state.vector_store = vector_store
        app.state.llm = get_llm()
        app.state.rag_chain = response_generator(vector_store, llm_instance=app.state.llm)

        return {
            "message": "Ingestion successful!",
            "documents_loaded": len(docs),
            "chunks_created": len(chunks),
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_repo(request: QueryRequest):
    if not hasattr(app.state, "rag_chain") or app.state.rag_chain is None:
        raise HTTPException(status_code=400, detail="RAG chain not initialized. Please call /ingest first.")

    try:
        response = app.state.rag_chain.invoke(request.question)
        return {"question": request.question, "answer": response}
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = str(e)
        msg_lower = error_msg.lower()
        if any(t in msg_lower for t in ["authentication", "invalid api key", "401", "unauthorized", "forbidden"]):
            raise HTTPException(status_code=503, detail=f"Groq API key issue: {error_msg}")
        if "not found" in msg_lower and "model" in msg_lower:
            raise HTTPException(status_code=404, detail=f"LLM model not found: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

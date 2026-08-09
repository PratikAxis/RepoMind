from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT_DIR / ".env")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from backend.configs.data_ingestion import load_remote_repo, load_local_repo
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



class IngestRequest(BaseModel):
    source_type: str  
    path: str
    url: Optional[str] = None
    branch: str = "main"

class QueryRequest(BaseModel):
    question: str

def _is_provider_auth_error(error: Exception) -> bool:
    message = str(error).lower()
    status_code = getattr(error, "status_code", None)
    if status_code in {401, 403}:
        return True
    return any(token in message for token in ["authentication", "invalid api key", "invalid_api_key", "401", "unauthorized", "forbidden", "api key"])


def _is_provider_config_error(error: Exception) -> bool:
    message = str(error).lower()
    return any(token in message for token in ["not configured", "groq_api_key", "langchain_groq"])


@app.post("/ingest")
async def ingest_repo(request: IngestRequest):
    try:
        # 1. Data Ingestion
        if request.source_type == "local":
            docs = load_local_repo(request.path, request.branch)
        elif request.source_type == "remote":
            if not request.url:
                raise HTTPException(status_code=400, detail="URL is required for remote source.")
            docs = load_remote_repo(request.url, request.path, request.branch)
        else:
            raise HTTPException(status_code=400, detail="Invalid source_type. Must be 'local' or 'remote'.")

        if not docs:
            raise HTTPException(status_code=404, detail="No documents found or failed to load repository. Check path/url.")

        # 2. Chunking
        chunks = text_chunks(docs)

        # 3. Embedding initialization
        embedding_model = get_embedding_model()

        # 4. Vector Store setup
        vector_store = init_vector_store(chunks, embedding_model)
        
        # Save vector store and chain to app state for querying
        app.state.vector_store = vector_store
        app.state.llm = get_llm()
        app.state.rag_chain = response_generator(vector_store, llm_instance=app.state.llm)

        return {
            "message": "Ingestion successful!", 
            "documents_loaded": len(docs),
            "chunks_created": len(chunks)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_repo(request: QueryRequest):
    if not hasattr(app.state, "rag_chain") or app.state.rag_chain is None:
        raise HTTPException(status_code=400, detail="RAG chain not initialized. Please call /ingest first.")
    
    try:
        # 5. Generation / Querying
        response = app.state.rag_chain.invoke(request.question)
        return {"question": request.question, "answer": response}
    except Exception as e:
        error_msg = str(e)
        if _is_provider_auth_error(e) or _is_provider_config_error(e):
            raise HTTPException(status_code=503, detail=f"Groq is not configured correctly. Please verify GROQ_API_KEY. Error: {error_msg}")
        if "not found" in error_msg.lower() and "model" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"LLM model not found. Please pull or select a valid model. Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


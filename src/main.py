from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from configs.data_ingestion import load_remote_repo, load_local_repo
from configs.chunking import text_chunks
from configs.embedding import get_embedding_model
from configs.vector_store import init_vector_store
from configs.generator import response_generator

app = FastAPI(title="RepoMind RAG API", description="API to ingest codebases and query them using RAG.")

class IngestRequest(BaseModel):
    source_type: str  
    path: str
    url: Optional[str] = None
    branch: str = "main"

class QueryRequest(BaseModel):
    question: str

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
        app.state.rag_chain = response_generator(vector_store)

        return {
            "message": "Ingestion successful!", 
            "documents_loaded": len(docs),
            "chunks_created": len(chunks)
        }
    
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
        if "Connection refused" in error_msg or "ConnectError" in error_msg:
            raise HTTPException(status_code=503, detail="Could not connect to Ollama. Please ensure Ollama is running and accessible at localhost:11434.")
        if "not found" in error_msg.lower() and "model" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"Ollama model not found. Please pull the required model (e.g., 'ollama pull phi3:mini'). Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


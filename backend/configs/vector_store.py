import os
import shutil
from pathlib import Path
from uuid import uuid4

import chromadb
from langchain_community.vectorstores import Chroma


def init_vector_store(chunks, embedding_model, persist_directory=None, collection_name='repo_collection'):
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata | {"chunk_id": i} for i, chunk in enumerate(chunks)]

    if persist_directory is None:
        persist_directory = os.path.join(os.getcwd(), 'repo_ChromaDB')

    persist_path = Path(persist_directory).expanduser().resolve()
    if persist_path.exists():
        try:
            shutil.rmtree(persist_path)
        except Exception:
            for child in persist_path.iterdir():
                if child.is_file():
                    child.unlink(missing_ok=True)
                else:
                    shutil.rmtree(child, ignore_errors=True)
            persist_path.mkdir(parents=True, exist_ok=True)
    persist_path.mkdir(parents=True, exist_ok=True)

    effective_collection_name = f"{collection_name}_{uuid4().hex[:8]}"

    vector_db = Chroma(
        collection_name=effective_collection_name,
        embedding_function=embedding_model,
        persist_directory=str(persist_path),
    )

    if texts:
        vector_db.add_texts(texts=texts, metadatas=metadatas)

    return vector_db
import shutil
from pathlib import Path

from langchain_community.vectorstores import Chroma


def init_vector_store(chunks, embedding_model, persist_directory='./repo_ChromaDB', collection_name='repo_collection'):
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata | {"chunk_id": i} for i, chunk in enumerate(chunks)]

    persist_path = Path(persist_directory).expanduser().resolve()
    persist_path.mkdir(parents=True, exist_ok=True)

    if persist_path.exists():
        for child in persist_path.iterdir():
            if child.name == collection_name:
                shutil.rmtree(child)

    vector_db = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=str(persist_path),
    )

    if texts:
        vector_db.add_texts(texts=texts, metadatas=metadatas)

    return vector_db
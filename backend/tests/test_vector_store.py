import tempfile
from pathlib import Path

from langchain_core.documents import Document

from langchain_core.embeddings import Embeddings
from typing import List

class SimpleEmbedding(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[float(len(text))] for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return [float(len(text))]
from backend.configs.vector_store import init_vector_store


class BigEmbedding:
    def embed_documents(self, texts):
        return [[0.0] * 384 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 384


import shutil

def test_init_vector_store_recreates_persisted_collection_for_new_embedding_dimensions():
    persist_directory = Path(__file__).resolve().parent / "test_chromadb"
    if persist_directory.exists():
        shutil.rmtree(persist_directory, ignore_errors=True)
    persist_directory.mkdir(parents=True, exist_ok=True)

    try:
        old_store = init_vector_store(
            [Document(page_content="old content", metadata={"source": "legacy"})],
            BigEmbedding(),
            persist_directory=str(persist_directory),
            collection_name="repo_collection",
        )
        assert old_store is not None

        # Explicitly release SQLite database locks
        try:
            old_store._client.close()
        except Exception:
            pass
        del old_store
        import gc
        gc.collect()

        new_store = init_vector_store(
            [Document(page_content="fresh content", metadata={"source": "new"})],
            SimpleEmbedding(),
            persist_directory=str(persist_directory),
            collection_name="repo_collection",
        )

        results = new_store.similarity_search("fresh content", k=1)
        assert len(results) == 1
        assert results[0].page_content == "fresh content"
    finally:
        if persist_directory.exists():
            shutil.rmtree(persist_directory, ignore_errors=True)

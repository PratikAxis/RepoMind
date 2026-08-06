import tempfile
from pathlib import Path

from langchain_core.documents import Document

from backend.configs.embedding import SimpleEmbedding
from backend.configs.vector_store import init_vector_store


class BigEmbedding:
    def embed_documents(self, texts):
        return [[0.0] * 384 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 384


def test_init_vector_store_recreates_persisted_collection_for_new_embedding_dimensions(tmp_path):
    persist_directory = tmp_path / "chromadb"
    persist_directory.mkdir(parents=True, exist_ok=True)

    old_store = init_vector_store(
        [Document(page_content="old content", metadata={"source": "legacy"})],
        BigEmbedding(),
        persist_directory=str(persist_directory),
        collection_name="repo_collection",
    )
    assert old_store is not None

    new_store = init_vector_store(
        [Document(page_content="fresh content", metadata={"source": "new"})],
        SimpleEmbedding(),
        persist_directory=str(persist_directory),
        collection_name="repo_collection",
    )

    results = new_store.similarity_search("fresh content", k=1)
    assert len(results) == 1
    assert results[0].page_content == "fresh content"

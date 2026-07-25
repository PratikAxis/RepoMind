from langchain_core.embeddings import Embeddings
from typing import List


class SimpleEmbedding(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[float(len(text))] for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return [float(len(text))]


def get_embedding_model():
    return SimpleEmbedding()
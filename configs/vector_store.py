from langchain_community.vectorstores import Chroma
from embedding import model

def init_vector_store(embedded_chunks):
    texts = [chunk.page_content for chunk in embedded_chunks]
    metadatas = [chunk.metadata | {"chunk_id": i} for i, chunk in enumerate(embedded_chunks)]

    vector_db = Chroma(
        collection_name='repo_collection', 
        embedding_function=model,
        persist_directory='./repo_ChromaDB' 
    )
    
    vector_db = vector_db.add_texts(texts=texts, metadatas=metadatas)
    return vector_db   
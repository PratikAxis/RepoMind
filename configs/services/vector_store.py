from langchain_community.vectorstores import Chroma
from configs.embedding import model

def init_vector_store(docs):
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata | {"chunk_id": i} for i, doc in enumerate(docs)]

    vector_db = Chroma(
        collection_name='repo_collection', 
        embedding_function=model,
        persist_directory='./repo_ChromaDB' 
    )
    
    vector_db.add_texts(texts=texts, metadatas=metadatas)
    return vector_db   
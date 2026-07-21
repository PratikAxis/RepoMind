from langchain_community.vectorstores import Chroma


def init_vector_store(chunks, embedding_model):
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata | {"chunk_id": i} for i, chunk in enumerate(chunks)]

    vector_db = Chroma(
        collection_name='repo_collection', 
        embedding_function=embedding_model,
        persist_directory='./repo_ChromaDB' 
    )
    
    vector_db.add_texts(texts=texts, metadatas=metadatas)

    return vector_db
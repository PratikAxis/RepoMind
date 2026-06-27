from langchain_community import vectorstores
from vectorized import init_vector_store

vectorstores = init_vector_store()

def retrieval(query):
    retriever_para = vectorstores.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": 4}
        )
    
    return retriever_para.invoke(query) 
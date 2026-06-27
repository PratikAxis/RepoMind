from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore[import]
from doc_load import load_local_repo 

def text_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
    )
    return splitter.split_documents(docs)  
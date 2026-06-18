from langchain.text_splitter import RecursiveCharacterTextSplitter
from doc_load import docs

def text_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1500,
        chunk_overlap=300,
    )

    chunks = splitter.split_text(docs)
    return chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

def text_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
    )
    return splitter.split_documents(docs)
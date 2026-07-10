from langchain_text_splitters import RecursiveCharacterTextSplitter

def text_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
    )
    return splitter.split_documents(docs)
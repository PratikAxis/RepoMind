from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore[import]
from configs.data_ingestion import load_local_repo, load_remote_repo

local_repo = load_local_repo() or []
remote_repo = load_remote_repo() or []

docs = local_repo+remote_repo

if not docs:
    raise ValueError("There is no doc fetch for chunking. Please put the correct source of code base.")

def text_chunks():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
    )
    return splitter.split_documents(docs)
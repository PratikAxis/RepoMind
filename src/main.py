from configs.data_ingestion import load_remote_repo, load_local_repo
from configs.chunking import text_chunks
from configs.embedding import chunk_embed
from configs.vector_store import init_vector_store
from configs.generator import generate_response

# Data Ingestion and Loading

if choice == "local_repo":
    load_local_repo(path, branch)
    
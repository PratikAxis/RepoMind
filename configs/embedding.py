from chunking import text_chunks
from sentence_transformers import SentenceTransformer   

model = SentenceTransformer('all-MiniLM-L6-v2')
chunks = text_chunks()

def chunk_embed(chunks):
    embedded_chunks = model.encode(chunks) 
    return embedded_chunks  
from sentence_transformers import SentenceTransformer   

model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_embed(chunks):
    return model.encode(chunks)   
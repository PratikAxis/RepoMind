from langchain_community.document_loaders import GitLoader
from pydantic import BaseModel
from pydantic_string_url import HttpUrl
import os
import shutil

class Source(BaseModel):
    path: str
    url: HttpUrl

def load_remote_repo(url: str, path: str, branch: str = "main"):
    if os.path.exists(path):
        shutil.rmtree(path)
        
    loader = GitLoader(
        clone_url=url, 
        repo_path=path, 
        branch=branch
    )
    
    docs = loader.load()
    return docs

def load_local_repo(path: str, branch: str = "main"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path {path} does not exist.")
        
    loader = GitLoader(
        repo_path=path, 
        branch=branch
    )
    docs = loader.load()
    return docs  
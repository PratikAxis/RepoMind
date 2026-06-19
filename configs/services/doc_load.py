from langchain_community.document_loaders import GitLoader
from pydantic import BaseModel
from pydantic_string_url import HttpUrl
from os import path
import shutil
from file_filters import codebase_file_filter

class Source(BaseModel):
    path: str
    url: HttpUrl


def load_remote_repo(url: str, path: str, branch: str = "main"):
    if path.exists(path):
        shutil.rmtree(path)
        
    loader = GitLoader(
        clone_url = url, 
        repo_path = path, 
        branch = branch,
        file_filter = codebase_file_filter 
    )
    
    docs = loader.load()
    return docs

def load_local_repo(path: str, branch: str = "main"):
    if not path.exists(path):
        raise FileNotFoundError(f"Path {path} does not exist.")
        
    loader = GitLoader(
        repo_path=path, 
        branch=branch,
        file_filter = codebase_file_filter
    )
    docs = loader.load()
    return docs  
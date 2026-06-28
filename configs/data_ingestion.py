from langchain_community.document_loaders import GitLoader
from pydantic import BaseModel
from pydantic_string_url import HttpUrl
from pathlib import Path
from services.file_filters import codebase_file_filter
from git import GitCommandError 

class Source(BaseModel):
    path: str
    url: HttpUrl

def load_remote_repo(url: str, path: str, branch: str = "main"):
    repo_path = Path(path)
    
    try:
        loader = GitLoader(
            clone_url=url, 
            repo_path=str(repo_path),
            branch=branch,
            file_filter=codebase_file_filter 
        )
        docs = loader.load()
        return docs
    
    except GitCommandError as e:
        print(f"Git error: {e}")
        return []
    
    except ValueError as e:
        print(f"Conflict: {e}")
        return []

def load_local_repo(path: str, branch: str = "main"):
    repo_path = Path(path)
    
    if not repo_path.exists():
        raise FileNotFoundError(f"Path {repo_path} does not exist.")
        
    if not (repo_path / ".git").exists():
        raise ValueError(f"Path {repo_path} is not a Git repository.")

    loader = GitLoader(
        repo_path=str(repo_path), 
        branch=branch,
        file_filter=codebase_file_filter
    )
    
    try:
        docs = loader.load()
        return docs
    
    except GitCommandError as e:
        print(f"Branch '{branch}' not found: {e}")
        return []   
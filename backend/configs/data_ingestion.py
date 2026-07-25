import os
from pydantic import BaseModel, HttpUrl
from pathlib import Path
from langchain_core.documents import Document
from backend.configs.services.file_filters import codebase_file_filter

class Source(BaseModel):
    path: str
    url: HttpUrl


def resolve_repo_path(path: str) -> Path:
    candidate = Path(path).expanduser().resolve()

    if candidate.exists():
        return candidate

    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
        candidate = candidate.resolve()
        if candidate.exists():
            return candidate

    # Allow access to the mounted workspace path inside the container.
    workspace_path = Path('/workspace')
    if workspace_path.exists():
        rel = os.path.relpath(candidate, Path('/'))
        mounted_candidate = workspace_path / rel
        if mounted_candidate.exists():
            return mounted_candidate

    return candidate

def load_remote_repo(url: str, path: str, branch: str = "main"):
    repo_path = Path(path)

    if repo_path.exists() and repo_path.is_dir() and any(repo_path.iterdir()):
        repo_name = url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        repo_path = repo_path / repo_name

    try:
        docs = []
        for file_path in repo_path.rglob('*'):
            if not file_path.is_file():
                continue
            if not codebase_file_filter(str(file_path)):
                continue
            try:
                content = file_path.read_text(encoding='utf-8')
            except Exception:
                continue
            relative_path = file_path.relative_to(repo_path)
            docs.append(Document(page_content=content, metadata={"source": str(relative_path)}))
        return docs
    except Exception as e:
        print(f"Error loading remote repo: {e}")
        return []

def load_local_repo(path: str, branch: str = "main"):
    repo_path = resolve_repo_path(path)
    
    if not repo_path.exists():
        raise FileNotFoundError(f"Path {repo_path} does not exist.")

    current = repo_path
    while current != current.parent:
        if (current / ".git").exists():
            repo_path = current
            break
        current = current.parent

    if not (repo_path / ".git").exists():
        raise ValueError(f"Path {repo_path} is not a Git repository.")

    docs = []
    try:
        for file_path in repo_path.rglob('*'):
            if not file_path.is_file():
                continue
            if not codebase_file_filter(str(file_path)):
                continue
            try:
                content = file_path.read_text(encoding='utf-8')
            except Exception:
                continue
            relative_path = file_path.relative_to(repo_path)
            docs.append(Document(page_content=content, metadata={"source": str(relative_path)}))
        return docs
    except Exception as e:
        print(f"Error loading local repo: {e}")
        return []
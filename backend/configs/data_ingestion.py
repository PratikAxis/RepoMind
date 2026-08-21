import subprocess
from pathlib import Path
from langchain_core.documents import Document
from backend.configs.services.file_filters import codebase_file_filter


def load_remote_repo(url: str, clone_dir: str, branch: str = "main") -> list[Document]:
    """
    Clone a remote Git repository and load all code files as Documents.

    Args:
        url:       The GitHub/GitLab URL of the repo (e.g. https://github.com/user/repo.git)
        clone_dir: Local directory where the repo will be cloned into.
        branch:    Branch to clone (default: "main").

    Returns:
        A list of LangChain Document objects, one per code file.
    """
    repo_name = url.rstrip("/").split("/")[-1].removesuffix(".git")
    target_path = Path(clone_dir).expanduser().resolve() / repo_name

    # Clone only if not already present
    if not target_path.exists():
        try:
            subprocess.run(
                ["git", "clone", "--branch", branch, url, str(target_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            print(f"Git clone failed: {exc.stderr}")
            return []

    # Walk files and load content
    docs = []
    for file_path in target_path.rglob("*"):
        if not file_path.is_file():
            continue
        if not codebase_file_filter(str(file_path)):
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue
        relative_path = file_path.relative_to(target_path)
        docs.append(Document(page_content=content, metadata={"source": str(relative_path)}))

    return docs
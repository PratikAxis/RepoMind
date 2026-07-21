import os

def codebase_file_filter(file_path: str) -> bool:
    """
    Filter for RAG ingestion. 

    ✅ Included:
        .py, .md, .txt, .html, .json, .yaml/.yml
        Special files: requirements.txt, Dockerfile

    ❌ Excluded:
        .ipynb, .png, .jpg, .jpeg, .gif, .svg, .csv
        Directories: node_modules/, .git/, __pycache__/, venv/, dist/, build/
    """

    # --- Excluded directories ---
    excluded_dirs = (
        "/node_modules/",
        "/.git/",
        "/__pycache__/",
        "/venv/",
        "/.venv/",
        "/dist/",
        "/build/",
        "/target/",
    )

    # --- Excluded extensions ---
    excluded_extensions = (
        ".ipynb",
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
        ".csv",
        ".pkl", ".bin", ".h5", ".pt", ".pth",   # model / binary blobs
        ".zip", ".tar", ".gz",
    )

    # --- Allowed extensions ---
    allowed_extensions = (
        ".py",
        ".md", ".rst",
        ".txt",
        ".html", ".htm",
        ".json",
        ".yaml", ".yml",
        ".js", ".ts", ".jsx", ".tsx",
        ".css", ".scss",
        ".go", ".java", ".cpp", ".c", ".h", ".rs", ".rb", ".php",
        ".sql", ".graphql", ".proto",
        ".toml", ".cfg", ".ini",
        ".sh", ".bash",
    )

    # --- Special filenames always allowed (no extension check) ---
    special_files = (
        "Dockerfile",
        "requirements.txt",
        "Makefile",
        ".env.example",
    )

    filename = os.path.basename(file_path)

    # Reject excluded directories
    if any(d in file_path for d in excluded_dirs):
        return False

    # Reject excluded extensions first (takes priority)
    if any(file_path.endswith(ext) for ext in excluded_extensions):
        return False

    # Always allow special named files
    if filename in special_files:
        return True

    # Allow only whitelisted extensions
    if not any(file_path.endswith(ext) for ext in allowed_extensions):
        return False

    return True
def codebase_file_filter(file_path: str) -> bool:
    allowed_extensions = (
        ".py", ".js", ".ts", ".jsx", ".tsx",
        ".go", ".java", ".cpp", ".c", ".h", ".rs", ".rb", ".php",
        ".md", ".rst", ".txt",
        ".yaml", ".yml", ".toml", ".json",
        ".ipynb",
        ".sql", ".graphql", ".proto", ".html", ".css", ".scss"
    )
    
    excluded_files = (
        "package-lock.json", "yarn.lock", "poetry.lock", "composer.lock",
        "tsconfig.tsbuildinfo", "package.json"
    )
    
    excluded_dirs = (
        "/node_modules/", "/venv/", "/__pycache__/", 
        "/dist/", "/build/", "/.git/", "/target/"
    )

    if any(dir_name in file_path for dir_name in excluded_dirs):
        return False
        
    if not file_path.endswith(allowed_extensions):
        return False
        
    if any(file_path.endswith(excluded) for excluded in excluded_files):
        return False
        
    return True
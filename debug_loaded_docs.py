"""
Debug script: Print all documents loaded from the Expensify GitHub repo.
Run from the RepoMind root: python debug_loaded_docs.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.configs.data_ingestion import load_remote_repo

REPO_URL = "https://github.com/PratikAxis/Expensify"
CLONE_PATH = "/tmp/expensify_debug_clone"

print(f"Loading repo: {REPO_URL}")
print(f"Clone target: {CLONE_PATH}")
print("-" * 60)

docs = load_remote_repo(url=REPO_URL, path=CLONE_PATH, branch="main")

if not docs:
    print("❌ NO DOCUMENTS LOADED — check git clone / branch name / file filter")
    sys.exit(1)

print(f"✅ Total documents loaded: {len(docs)}\n")
print("=" * 60)
print("FILE LIST (source metadata):")
print("=" * 60)

file_paths = sorted(set(doc.metadata.get("source", doc.metadata.get("file_path", "UNKNOWN")) for doc in docs))

# Key files to check for explicitly
key_files = [
    "Dockerfile",
    "requirements.txt",
    "README.md",
    "frontend/index.html",
    "backend/main.py",
    ".env.example",
    "docker-compose.yml",
    "docker-compose.yaml",
]

for fp in file_paths:
    print(f"  {fp}")

print("\n" + "=" * 60)
print("KEY FILE CHECK:")
print("=" * 60)

for key in key_files:
    found = any(fp.endswith(key) or key in fp for fp in file_paths)
    status = "✅ FOUND" if found else "❌ MISSING"
    print(f"  {status:12s}  {key}")

print("\n" + "=" * 60)
print("DOCUMENT PREVIEW (first 200 chars of each):")
print("=" * 60)
for doc in docs:
    src = doc.metadata.get("source", doc.metadata.get("file_path", "?"))
    preview = doc.page_content[:200].replace("\n", " ")
    print(f"\n📄 {src}")
    print(f"   {preview}...")

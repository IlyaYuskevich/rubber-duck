from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

BLOB_STORAGE = REPO_ROOT / "blob_storage"
BLOB_STORAGE.mkdir(parents=True, exist_ok=True)
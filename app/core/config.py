from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

UPLOAD_DIR = DATA_DIR / "uploads"
RAW_FILES_DIR = DATA_DIR / "raw_files"
VECTORS_DIR = DATA_DIR / "vectors"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_DIM = 384

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RAW_FILES_DIR.mkdir(parents=True, exist_ok=True)
VECTORS_DIR.mkdir(parents=True, exist_ok=True)

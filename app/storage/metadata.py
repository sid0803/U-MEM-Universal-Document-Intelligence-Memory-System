import json
from pathlib import Path
from typing import List, Dict

# -----------------------------
# Paths
# -----------------------------
METADATA_DIR = Path("data/metadata")
METADATA_DIR.mkdir(parents=True, exist_ok=True)

DOC_FILE = METADATA_DIR / "documents.json"
CHUNK_FILE = METADATA_DIR / "chunks.json"
CLUSTER_FILE = METADATA_DIR / "clusters.json"


# -----------------------------
# Internal helpers
# -----------------------------
def _safe_load(path: Path) -> List[Dict]:
    if not path.exists():
        return []

    try:
        content = path.read_text().strip()
        if not content:
            return []
        return json.loads(content)
    except Exception:
        # Corrupted or partial file → fail safe
        return []


def _atomic_write(path: Path, data: List[Dict]):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


# -----------------------------
# Documents
# -----------------------------
def load_documents() -> List[Dict]:
    return _safe_load(DOC_FILE)


def save_documents(documents: List[Dict]):
    _atomic_write(DOC_FILE, documents)


def add_document_metadata(doc: Dict):
    docs = load_documents()

    doc_ids = {d["doc_id"] for d in docs if "doc_id" in d}
    if doc.get("doc_id") in doc_ids:
        return  # prevent duplicate

    docs.append(doc)
    save_documents(docs)


def update_document(doc_id: str, updates: Dict):
    docs = load_documents()
    for d in docs:
        if d.get("doc_id") == doc_id:
            d.update(updates)
            break
    save_documents(docs)


# -----------------------------
# Chunks
# -----------------------------
def load_chunks() -> List[Dict]:
    return _safe_load(CHUNK_FILE)


def save_chunks(chunks: List[Dict]):
    _atomic_write(CHUNK_FILE, chunks)


def update_chunk(chunk_id: str, updates: Dict):
    chunks = load_chunks()
    for c in chunks:
        if c.get("chunk_id") == chunk_id:
            c.update(updates)
            break
    save_chunks(chunks)


# -----------------------------
# Clusters
# -----------------------------
def load_clusters() -> List[Dict]:
    return _safe_load(CLUSTER_FILE)


def save_clusters(clusters: List[Dict]):
    _atomic_write(CLUSTER_FILE, clusters)

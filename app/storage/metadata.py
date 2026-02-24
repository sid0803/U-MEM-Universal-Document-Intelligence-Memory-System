import json
import logging
import threading
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)
_lock = threading.Lock()

# ==========================================================
# Paths
# ==========================================================
METADATA_DIR = Path("data/metadata")
METADATA_DIR.mkdir(parents=True, exist_ok=True)

DOC_FILE = METADATA_DIR / "documents.json"
CHUNK_FILE = METADATA_DIR / "chunks.json"
CLUSTER_FILE = METADATA_DIR / "clusters.json"

# ==========================================================
# Safe Load / Persist
# ==========================================================
def _safe_load(path: Path) -> List[Dict]:
    if not path.exists():
        return []

    try:
        content = path.read_text().strip()
        if not content:
            return []

        data = json.loads(content)

        if not isinstance(data, list):
            raise ValueError("Root metadata must be a list")

        return data

    except Exception as e:
        logger.error("Corrupted metadata file %s. Resetting. Error: %s", path, e)
        path.unlink(missing_ok=True)
        return []


def _atomic_write(path: Path, data: List[Dict]):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def _require_fields(data: Dict, required: set, entity: str):
    if not required.issubset(data):
        raise ValueError(
            f"{entity} missing required fields: {required - set(data.keys())}"
        )

# ==========================================================
# DOCUMENTS
# ==========================================================
def load_documents() -> List[Dict]:
    return _safe_load(DOC_FILE)


def create_document(
    doc_id: str,
    original_name: str,
    file_type: str,
    num_chunks: int,
    user_id: str,
):
    document = {
        "doc_id": doc_id,
        "original_name": original_name,
        "file_type": file_type,
        "num_chunks": num_chunks,
        "user_id": user_id,
        "cluster_id": None,
        "created_at": None,
    }

    _require_fields(document, {"doc_id", "user_id"}, "Document")

    with _lock:
        docs = load_documents()
        if any(d["doc_id"] == doc_id for d in docs):
            return
        docs.append(document)
        _atomic_write(DOC_FILE, docs)


def update_document(doc_id: str, user_id: str, updates: Dict):
    with _lock:
        docs = load_documents()
        for d in docs:
            if d["doc_id"] == doc_id and d["user_id"] == user_id:
                d.update(updates)
                break
        _atomic_write(DOC_FILE, docs)

# ==========================================================
# CHUNKS
# ==========================================================
def load_chunks() -> List[Dict]:
    return _safe_load(CHUNK_FILE)


def save_chunks(chunks: List[Dict]):
    """
    Full overwrite (used by clustering)
    """
    with _lock:
        _atomic_write(CHUNK_FILE, chunks)


def add_chunks(chunks: List[Dict]):
    with _lock:
        existing = load_chunks()
        existing_ids = {c["chunk_id"] for c in existing}

        for chunk in chunks:
            _require_fields(chunk, {"chunk_id", "doc_id", "user_id"}, "Chunk")
            if chunk["chunk_id"] not in existing_ids:
                existing.append(chunk)

        _atomic_write(CHUNK_FILE, existing)

# ==========================================================
# CLUSTERS
# ==========================================================
def load_clusters() -> List[Dict]:
    return _safe_load(CLUSTER_FILE)


def save_clusters(clusters: List[Dict]):
    """
    Full overwrite (used by clustering)
    """
    with _lock:
        _atomic_write(CLUSTER_FILE, clusters)


def add_clusters(clusters: List[Dict]):
    with _lock:
        existing = load_clusters()
        existing_ids = {c["cluster_id"] for c in existing}

        for cluster in clusters:
            _require_fields(cluster, {"cluster_id", "user_id"}, "Cluster")
            if cluster["cluster_id"] not in existing_ids:
                existing.append(cluster)

        _atomic_write(CLUSTER_FILE, existing)

# ==========================================================
# Reset Utility (Testing Only)
# ==========================================================
def reset_metadata():
    with _lock:
        for path in [DOC_FILE, CHUNK_FILE, CLUSTER_FILE]:
            path.unlink(missing_ok=True)

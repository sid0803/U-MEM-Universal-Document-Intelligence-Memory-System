import json
from pathlib import Path

VECTOR_META_FILE = Path("data/vector_metadata.json")

def load_vector_metadata():
    if not VECTOR_META_FILE.exists():
        return []
    return json.loads(VECTOR_META_FILE.read_text())

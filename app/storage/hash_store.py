import json
from pathlib import Path

HASH_FILE = Path("data/vector_hashes.json")

if HASH_FILE.exists():
    hashes = set(json.loads(HASH_FILE.read_text()))
else:
    hashes = set()

def hash_exists(doc_hash: str) -> bool:
    return doc_hash in hashes

def add_hash(doc_hash: str):
    hashes.add(doc_hash)
    HASH_FILE.write_text(json.dumps(list(hashes), indent=2))
    
def delete_hash(doc_hash: str):
    if doc_hash in hashes:
        hashes.remove(doc_hash)
        HASH_FILE.write_text(json.dumps(list(hashes), indent=2))

from fastapi import APIRouter, HTTPException
from app.storage.metadata import load_metadata, delete_metadata
from app.storage.file_store import delete_file
from app.storage.hash_store import delete_hash
from app.storage.vector_store import rebuild_index

router = APIRouter()

@router.delete("/documents/{filename}")
def delete_document(filename: str):
    metadata = load_metadata()
    doc = next((d for d in metadata if d["filename"] == filename), None)

    if not doc:
        raise HTTPException(404, "Not found")

    delete_file(doc["path"])
    delete_metadata(filename)
    delete_hash(doc["hash"])
    rebuild_index(exclude_filename=filename)

    return {"message": "Deleted"}

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

from app.services.file_detector import detect_file_type
from app.services.extractor import extract_text
from app.services.classifier import classify_document_type, classify_subject
from app.services.hash_utils import generate_doc_hash
from app.storage.hash_store import hash_exists, add_hash
from app.services.embeddings import embed_text
from app.services.chunker import chunk_text
from app.services.text_normalizer import normalize_text


from app.storage.vector_store import add_document
from app.storage.metadata import (
    load_chunks,
    save_chunks,
    add_document_metadata
)

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILES_DIR = Path("data/raw_files")
RAW_FILES_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # 1️⃣ Save temp file
    temp_path = UPLOAD_DIR / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2️⃣ Detect & extract text
    file_type = detect_file_type(temp_path)
    extracted_text = extract_text(str(temp_path), file_type)

    if not extracted_text.strip():
        temp_path.unlink(missing_ok=True)
        raise HTTPException(400, "No extractable text found")

    # 3️⃣ Normalize + hash (dedup)
    normalized_text = normalize_text(extracted_text)
    doc_hash = generate_doc_hash(normalized_text)

    if hash_exists(doc_hash):
        temp_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=409,
            detail="Duplicate document detected (content already exists)"
        )

    # 4️⃣ Classify
    document_type = classify_document_type(extracted_text)
    subject = classify_subject(extracted_text, document_type)

    # 5️⃣ Move file to flat storage
    doc_id = str(uuid.uuid4())
    final_path = RAW_FILES_DIR / f"{doc_id}{temp_path.suffix}"
    shutil.move(str(temp_path), final_path)

    # 6️⃣ Store hash
    add_hash(doc_hash)

    # 7️⃣ Save document metadata
    add_document_metadata({
        "doc_id": doc_id,
        "original_name": file.filename,
        "path": str(final_path),
        "document_type": document_type,
        "subject": subject,
        "hash": doc_hash
    })

    # 8️⃣ Chunk the document
    chunks = chunk_text(extracted_text)
    chunk_metadata = load_chunks()

    # 9️⃣ Embed & store chunks
    for chunk_text_content in chunks:
        chunk_id = str(uuid.uuid4())

        embedding = embed_text(chunk_text_content)

        vector_id = add_document(
            embedding,
            meta={
                "chunk_id": chunk_id,
                "doc_id": doc_id
            }
        )

        chunk_metadata.append({
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "text": chunk_text_content,
            "vector_id": vector_id
        })

    # 🔟 Persist chunk metadata
    save_chunks(chunk_metadata)

    return {
        "status": "stored",
        "doc_id": doc_id,
        "filename": file.filename,
        "document_type": document_type,
        "subject": subject,
        "chunks_created": len(chunks)
    }

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import logging

from app.auth.dependencies import get_current_user
from app.storage.metadata import load_documents
from app.services.document_summarizer import summarize_document
from app.services.document_qa import answer_document_question
from app.core.security_utils import validate_ownership


router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger(__name__)


# ============================
# Request Models
# ============================

class QuestionRequest(BaseModel):
    question: str


# ============================
# List Documents
# ============================

@router.get("/")
def list_documents(current_user=Depends(get_current_user)):
    user_id = current_user["user_id"]

    try:
        docs = load_documents()
    except Exception:
        logger.exception("Failed to load documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load documents",
        )

    user_docs = [d for d in docs if d.get("user_id") == user_id]

    return {
        "count": len(user_docs),
        "documents": user_docs,
    }


# ============================
# Document Summary
# ============================

@router.post("/{doc_id}/summary")
def generate_summary(doc_id: str, current_user=Depends(get_current_user)):
    user_id = current_user["user_id"]

    try:
        docs = load_documents()
    except Exception:
        logger.exception("Failed to load documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load documents",
        )

    document = next((d for d in docs if d.get("doc_id") == doc_id), None)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    validate_ownership(document, user_id)

    try:
        return summarize_document(doc_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================
# Document Q&A (RAG)
# ============================

@router.post("/{doc_id}/qa")
def document_qa(
    doc_id: str,
    payload: QuestionRequest,
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]

    try:
        docs = load_documents()
    except Exception:
        logger.exception("Failed to load documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load documents",
        )

    document = next((d for d in docs if d.get("doc_id") == doc_id), None)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    validate_ownership(document, user_id)

    try:
        result = answer_document_question(
            doc_id=doc_id,
            user_id=user_id,
            question=payload.question,
        )
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

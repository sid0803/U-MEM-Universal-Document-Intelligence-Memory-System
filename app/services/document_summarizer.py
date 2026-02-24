from app.storage.metadata import load_chunks
from app.services.llm import ask_llm


def summarize_document(
    doc_id: str,
    user_id: str,
    max_chunks: int = 8,
    max_context_chars: int = 8000,
):
    """
    Generate LLM summary for a document.
    Limits chunk count and context size for safety.
    """

    chunks = load_chunks()

    # 🔐 Filter only this user's document
    doc_chunks = [
        c for c in chunks
        if c.get("doc_id") == doc_id
        and c.get("user_id") == user_id
    ]

    if not doc_chunks:
        raise ValueError("Document not found or no content available")

    # Optional: stable ordering
    doc_chunks = sorted(doc_chunks, key=lambda x: x.get("chunk_id", ""))

    selected_chunks = doc_chunks[:max_chunks]

    # Safely build context
    texts = [
        c.get("text", "")
        for c in selected_chunks
        if c.get("text")
    ]

    context = "\n\n".join(texts)

    if not context.strip():
        raise ValueError("Document contains no readable content")

    # Prevent extremely large prompts
    context = context[:max_context_chars]

    try:
        summary = ask_llm(
            context=context,
            question="Provide a concise summary of this document."
        )
    except Exception as e:
        raise RuntimeError(f"LLM summarization failed: {str(e)}")

    if not summary or not summary.strip():
        raise ValueError("LLM returned empty summary")

    return {
        "doc_id": doc_id,
        "summary": summary.strip(),
        "num_chunks_used": len(selected_chunks)
    }
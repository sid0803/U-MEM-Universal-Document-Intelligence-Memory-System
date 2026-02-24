from app.services.semantic_search import semantic_search
from app.services.llm import ask_llm


def answer_document_question(
    doc_id: str,
    user_id: str,
    question: str,
    top_k: int = 5
):
    """
    RAG-based document question answering.
    Supports both flat chunk format and matched_chunks format.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    # 1️⃣ Retrieve relevant chunks globally for the user
    results = semantic_search(
        query=question,
        user_id=user_id,
        top_k=top_k
    )

    # 2️⃣ Filter only this document
    results = [r for r in results if r.get("doc_id") == doc_id]

    if not results:
        raise ValueError("No relevant content found for this document")

    # 3️⃣ Extract text properly (support both formats)
    collected_text = []

    for r in results:
        # Case 1: flat structure
        if r.get("text"):
            collected_text.append(r["text"])

        # Case 2: structured search format (matched_chunks)
        if r.get("matched_chunks"):
            for chunk in r["matched_chunks"]:
                if chunk.get("text"):
                    collected_text.append(chunk["text"])

    context = "\n\n".join(collected_text)

    if not context.strip():
        raise ValueError("Document content is empty")

    # 4️⃣ Ask LLM
    answer = ask_llm(context=context, question=question)

    return {
        "doc_id": doc_id,
        "question": question,
        "answer": answer.strip(),
        "sources_used": len(collected_text),
    }

import os
import requests
import logging

logger = logging.getLogger(__name__)

# Use environment variable fallback
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"   # 🔥 changed localhost → 127.0.0.1
)

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")


def ask_llm(context: str, question: str) -> str:
    """
    Sends prompt to Ollama and returns model response.
    Raises RuntimeError on failure.
    """

    if not context or not context.strip():
        raise ValueError("Empty context provided to LLM")

    if not question or not question.strip():
        raise ValueError("Empty question provided to LLM")

    prompt = f"""
You are an AI assistant.
Answer ONLY using the context below.
If the answer is not in the context, say "Not found in documents".

Context:
{context}

Question:
{question}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=180   # slightly higher timeout for large docs
        )

        response.raise_for_status()

        data = response.json()

        # 🔥 safer parsing
        result = data.get("response", "").strip()

        if not result:
            logger.error("LLM returned empty response | raw=%s", data)
            raise RuntimeError("LLM returned empty response")

        return result

    except requests.exceptions.Timeout:
        logger.error("LLM request timed out")
        raise RuntimeError("LLM request timed out")

    except requests.exceptions.ConnectionError as e:
        logger.error("Ollama connection failed | url=%s | error=%s", OLLAMA_URL, str(e))
        raise RuntimeError("LLM service unavailable")

    except requests.exceptions.RequestException as e:
        logger.error("LLM HTTP error | %s", str(e))
        raise RuntimeError(f"LLM request failed: {str(e)}")

    except ValueError as e:
        logger.error("Invalid JSON response from LLM | %s", str(e))
        raise RuntimeError("Invalid LLM response format")

    except Exception as e:
        logger.exception("Unexpected LLM error")
        raise RuntimeError("Unexpected LLM failure") from e
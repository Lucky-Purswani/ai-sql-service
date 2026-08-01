# MistralAIEmbeddings is LangChain's wrapper around Mistral's embedding API endpoint.
# It handles the HTTP request, authentication, and response parsing for us.
from langchain_mistralai import MistralAIEmbeddings

# Import settings to safely access the API key (never hardcode it here).
from app.core.config import settings


# What is an "embedding"?
# An embedding is a way to represent text as a list of numbers (a vector) so that
# a computer can understand MEANING — not just match keywords.
#
# Example:
#   "employees who are late"    →  [0.12, -0.45, 0.87, ...]  (1024 numbers)
#   "staff with late_marks"     →  [0.11, -0.44, 0.88, ...]  (1024 very similar numbers)
#   "quarterly revenue report"  →  [-0.72, 0.33, -0.12, ...]  (1024 very different numbers)
#
# Because the vectors for similar phrases are CLOSE to each other in mathematical space,
# we can find the most relevant database tables by comparing vectors.
# This is the foundation of RAG (Retrieval-Augmented Generation).


# Initialize the Mistral embeddings model once at module load time.
# This creates a reusable client object. Creating it here (not inside the function)
# means we don't re-initialize it on every single call, which is more efficient.
embeddings = MistralAIEmbeddings(
    model=settings.MISTRAL_EMBED_MODEL,  # "mistral-embed" (free tier)
    api_key=settings.MISTRAL_API_KEY     # Passed securely from .env, never hardcoded
)


def get_embedding(text: str) -> list[float]:
    """
    Converts a plain text string into a 1024-dimensional vector embedding.

    Sends the text to the Mistral API and returns the resulting vector.
    This function is called in two different contexts:
      1. When STORING a schema: each table description is embedded and saved to NeonDB.
      2. When SEARCHING: the user's question is embedded to find similar table descriptions.

    Args:
        text: Any string — a table description or a user's question.

    Returns:
        A list of 1024 floats. Example: [-0.022, 0.036, 0.037, ...]
    """
    # embed_query() is LangChain's standard method for embedding a single string.
    # Under the hood, it makes a POST request to Mistral's /v1/embeddings API endpoint.
    return embeddings.embed_query(text)

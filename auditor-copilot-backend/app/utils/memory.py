from typing import Optional, List
from app.utils.vector_store import get_vector_store, add_documents_to_store


def get_recent_memory(agent: str, user_id: str, query: Optional[str] = None, k: int = 5, mode: Optional[str] = None) -> str:
    """Fetch recent conversation memory for an agent/user namespace.

    If query is provided, perform a similarity search; otherwise, return recent documents if available.
    Returns concatenated text snippets.
    """
    try:
        vectordb = get_vector_store(agent=agent, user_id=user_id, mode=mode)
    except Exception:
        # Unable to initialize vector store (e.g., chroma backend not available).
        # Fail gracefully and return empty memory so requests continue to work.
        return ""

    try:
        # Use a high k to get a broad range of history
        docs = vectordb.similarity_search(query or "", k=k)

        # For conversation history, we usually want chronological order, but vector search returns by relevance.
        # Without explicit timestamps in metadata, we rely on the search result order (most relevant first).
        
        snippets = [getattr(d, "page_content", getattr(d, "content", "")) for d in docs]
        return "\n\n".join(snippets)
    except Exception:
        return ""


def add_memory_text(agent: str, user_id: str, texts: List[str], mode: Optional[str] = None):
    """Add plain text items to the agent/user memory namespace."""
    # Wrap texts into simple Document-like objects expected by splitter
    from langchain.schema import Document

    # Store each text as its own document with memory metadata to improve retrieval
    docs = [Document(page_content=t, metadata={"source": "memory"}) for t in texts]
    try:
        add_documents_to_store(docs, agent=agent, user_id=user_id, mode=mode)
    except Exception:
        # Best-effort only: do not raise if memory persistence fails
        return

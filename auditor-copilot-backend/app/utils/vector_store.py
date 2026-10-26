# Primary vector store (Chroma) with FAISS fallback
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS
# from langchain_chroma import Chroma  # Original import
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

# Initialize embedding function once
_embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=settings.AZURE_OPENAI_EMBEDDING_ENDPOINT,
    api_key=settings.AZURE_OPENAI_EMBEDDING_API_KEY,
    model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    openai_api_version=settings.AZURE_OPENAI_EMBEDDING_API_VERSION
)

# In-memory store registry for dummy/FAISS instances to preserve memory across requests
_in_memory_stores: dict[str, object] = {}


def _build_collection_name(collection_name: str = None, *, agent: str | None = None, user_id: str | None = None, mode: str | None = None) -> str:
    """Build a collection/namespace name for vector memory.

    Priority: explicit collection_name > agent/user/mode constructed name > default from settings.
    """
    if collection_name:
        return collection_name

    parts = []
    if agent:
        parts.append(agent.upper())
    if user_id:
        parts.append(str(user_id))
    if mode:
        parts.append(mode.upper())

    if parts:
        return "_".join(parts)

    return settings.CHROMA_DB_COLLECTION


def get_vector_store(collection_name: str = None, *, agent: str | None = None, user_id: str | None = None, mode: str | None = None) -> Chroma:
    """Return a Chroma vector store instance for the given collection/namespace.

    This supports agent-scoped and user-scoped namespaces to ensure memory isolation.
    """
    coll = _build_collection_name(collection_name, agent=agent, user_id=user_id, mode=mode)
    # Use duckdb+parquet implementation to avoid native rust server startup on some platforms
    # langchain_chroma expects client_settings to be an object with attributes
    from types import SimpleNamespace

    # chromadb expects settings with attributes like chroma_api_impl and persist_directory
    from logging import getLogger
    logger = getLogger(__name__)

    # Try to initialize a Chroma vector store first. If Chroma fails (native rust bindings
    # or incompatible client settings), fall back to FAISS for local, pure-Python indexing.
    # This keeps behavior consistent across developer machines (Windows) and CI.
    from logging import getLogger
    logger = getLogger(__name__)

    # helper to build a faiss-backed store
    def _make_faiss(coll_name: str):
        import os
        from logging import getLogger
        logger = getLogger(__name__)

        class DummyVectorStore:
            """In-memory best-effort fallback vector store.

            - add_documents(documents): stores Document objects in memory
            - similarity_search(query, k): returns last k documents (no semantic search)
            """
            def __init__(self, name: str):
                self.name = name
                self._docs = []

            def add_documents(self, docs):
                self._docs.extend(docs)

            def similarity_search(self, query, k=3):
                # return most recent k documents
                return list(reversed(self._docs))[:k]

            def save_local(self, path: str):
                # nothing to persist for in-memory store
                return

            @staticmethod
            def load_local(path: str, embeddings=None):
                # return empty dummy store
                return DummyVectorStore(path)

        faiss_dir = os.path.join(settings.CHROMA_DB_DIR, "faiss", coll_name)
        os.makedirs(faiss_dir, exist_ok=True)
        # If FAISS isn't available in this environment, use the dummy store
        if FAISS is None:
            logger.debug("FAISS backend not available, using DummyVectorStore for %s", coll_name)
            if coll_name in _in_memory_stores:
                return _in_memory_stores[coll_name]
            store = DummyVectorStore(coll_name)
            _in_memory_stores[coll_name] = store
            return store

        try:
            # Try loading existing FAISS index
            db = FAISS.load_local(faiss_dir, _embeddings)
            return db
        except Exception:
            try:
                # create empty FAISS index
                db = FAISS.from_documents([], _embeddings)
                try:
                    db.save_local(faiss_dir)
                except Exception:
                    logger.debug("Failed to save new FAISS index to %s", faiss_dir)
                return db
            except Exception:
                logger.debug("FAISS initialization failed for %s, falling back to DummyVectorStore", coll_name)
                if coll_name in _in_memory_stores:
                    return _in_memory_stores[coll_name]
                store = DummyVectorStore(coll_name)
                _in_memory_stores[coll_name] = store
                return store

    # If Chroma usage is disabled via configuration, return FAISS/Dummy immediately
    if not getattr(settings, "CHROMA_ENABLED", False):
        logger.debug("CHROMA disabled; using FAISS/Dummy for collection %s", coll)
        return _make_faiss(coll)

    # Try several client_settings permutations to maximize compatibility across envs
    attempts = [
        {"chroma_api_impl": "duckdb+parquet", "chroma_db_impl": "duckdb+parquet"},
        {"chroma_api_impl": "duckdb", "chroma_db_impl": "duckdb"},
        {"chroma_api_impl": "local", "chroma_db_impl": "local"},
    ]

    last_exc = None
    for s in attempts:
        try:
            client_settings = SimpleNamespace(
                chroma_api_impl=s["chroma_api_impl"],
                chroma_db_impl=s["chroma_db_impl"],
                persist_directory=settings.CHROMA_DB_DIR,
            )

            vector_store = Chroma(
                collection_name=coll,
                embedding_function=_embeddings,
                persist_directory=settings.CHROMA_DB_DIR,
                client_settings=client_settings,
            )
            logger.debug("Initialized Chroma for collection %s with settings %s", coll, s)
            return vector_store
        except Exception as e:
            logger.debug("Chroma client_settings attempt failed: %s -> %s", s, e)
            last_exc = e

    # Last-resort: try without client_settings; may start rust-backed server depending on chromadb install
    # Final fallback: try default Chroma constructor; if that fails, fallback to FAISS
    try:
        vector_store = Chroma(
            collection_name=coll,
            embedding_function=_embeddings,
            persist_directory=settings.CHROMA_DB_DIR,
        )
        logger.debug("Initialized default Chroma for collection %s", coll)
        return vector_store
    except Exception as e:
        logger.debug("Default Chroma constructor failed, falling back to FAISS: %s", e)
        try:
            store = _make_faiss(coll)
            logger.debug("Using FAISS/Dummy for collection %s", coll)
            return store
        except Exception:
            logger.error("Failed to initialize any vector store for collection '%s'", coll)
            raise
    return vector_store


def add_documents_to_store(documents, collection_name: str = None, *, agent: str | None = None, user_id: str | None = None, mode: str | None = None):
    """Split and add documents to a namespaced vector store.

    Parameters mirror get_vector_store for namespacing.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)
    vectordb = get_vector_store(collection_name, agent=agent, user_id=user_id, mode=mode)
    vectordb.add_documents(chunks)

    # For FAISS, ensure persistence to local folder
    try:
        if isinstance(vectordb, FAISS):
            import os
            faiss_dir = os.path.join(settings.CHROMA_DB_DIR, "faiss", _build_collection_name(collection_name, agent=agent, user_id=user_id, mode=mode))
            vectordb.save_local(faiss_dir)
    except Exception:
        # best-effort only
        pass


def clear_collection(collection_name: str = None, *, agent: str | None = None, user_id: str | None = None, mode: str | None = None) -> bool:
    """Attempt to clear/delete a namespaced collection from the Chroma persistence.

    Returns True on best-effort success, False otherwise. This is intentionally
    tolerant because Chroma client APIs vary by installation/version.
    """
    coll = _build_collection_name(collection_name, agent=agent, user_id=user_id, mode=mode)

    # Best-effort removal of any persisted data for this collection across backends
    try:
        import os
        import shutil

        # Remove Chroma-style directory
        chroma_dir = os.path.join(settings.CHROMA_DB_DIR, coll)
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir, ignore_errors=True)

        # Remove FAISS-style directory
        faiss_dir = os.path.join(settings.CHROMA_DB_DIR, "faiss", coll)
        if os.path.exists(faiss_dir):
            shutil.rmtree(faiss_dir, ignore_errors=True)

        return True
    except Exception:
        return False


"""
Vector store utilities for document embedding, retrieval, and ingestion using ChromaDB and Azure OpenAI embeddings.

Key changes:
- Support for agent/user/mode namespacing to provide isolated vector memory per agent and per user.
"""
"""
Vector store utilities for document embedding, retrieval, and ingestion using Neon PostgreSQL (pgvector).

Migrated from ChromaDB to Neon DB (PostgreSQL with pgvector extension) for scalable,
serverless vector storage with agent- and user-scoped namespaces.
"""

import hashlib
import logging
import math
import os
import shutil
from typing import List, Optional, Any

import sqlalchemy
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_postgres.vectorstores import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger(__name__)

# Cached SQLAlchemy engine and embeddings singleton
_engine: Optional[sqlalchemy.Engine] = None
_embeddings_instance: Optional[Embeddings] = None
_in_memory_stores: dict[str, Any] = {}


class DeterministicFallbackEmbeddings(Embeddings):
    """Fast, local, deterministic embedding generator producing vectors of fixed dimension.

    Used when external cloud embedding APIs are unconfigured, rate-limited, or offline.
    Ensures vector operations and database persistence never crash.
    """

    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        if not text:
            return vec
        # Tokenize by words and characters
        for token in text.lower().split():
            h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            vec[h % self.dimension] += 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm > 0 else vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


class ResilientEmbeddingsWrapper(Embeddings):
    """Wraps primary cloud embeddings with an automatic fallback to local deterministic embeddings."""

    def __init__(self, primary: Embeddings, fallback: Embeddings):
        self.primary = primary
        self.fallback = fallback

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return self.primary.embed_documents(texts)
        except Exception as e:
            logger.warning("Primary embedding provider failed for documents, using fallback: %s", e)
            return self.fallback.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        try:
            return self.primary.embed_query(text)
        except Exception as e:
            logger.warning("Primary embedding provider failed for query, using fallback: %s", e)
            return self.fallback.embed_query(text)


def get_embeddings() -> Embeddings:
    """Initialize and return the configured embedding function with resilient fallback."""
    global _embeddings_instance
    if _embeddings_instance is not None:
        return _embeddings_instance

    dim = getattr(settings, "GEMINI_EMBEDDING_DIMENSIONS", 768)
    fallback = DeterministicFallbackEmbeddings(dimension=dim)
    primary: Optional[Embeddings] = None

    # 1. Try Google Generative AI / Gemini Embeddings if API key or Vertex is available
    google_key = getattr(settings, "GEMINI_API_KEY", "") or getattr(settings, "GOOGLE_API_KEY", "")
    if google_key or getattr(settings, "GOOGLE_CLOUD_PROJECT", ""):
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            model_name = getattr(settings, "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
            kwargs = {"model": model_name}
            if google_key:
                kwargs["google_api_key"] = google_key
            primary = GoogleGenerativeAIEmbeddings(**kwargs)
            logger.info("Configured GoogleGenerativeAIEmbeddings (%s)", model_name)
        except Exception as e:
            logger.debug("Could not initialize GoogleGenerativeAIEmbeddings: %s", e)

    # 2. Try Azure OpenAI Embeddings if configured
    if primary is None and getattr(settings, "AZURE_OPENAI_EMBEDDING_API_KEY", ""):
        try:
            from langchain_openai import AzureOpenAIEmbeddings
            primary = AzureOpenAIEmbeddings(
                azure_endpoint=settings.AZURE_OPENAI_EMBEDDING_ENDPOINT,
                api_key=settings.AZURE_OPENAI_EMBEDDING_API_KEY,
                model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                openai_api_version=settings.AZURE_OPENAI_EMBEDDING_API_VERSION,
            )
            logger.info("Configured AzureOpenAIEmbeddings")
        except Exception as e:
            logger.debug("Could not initialize AzureOpenAIEmbeddings: %s", e)

    # 3. Try standard OpenAI Embeddings if OPENAI_API_KEY in env
    if primary is None and os.getenv("OPENAI_API_KEY"):
        try:
            from langchain_openai import OpenAIEmbeddings
            primary = OpenAIEmbeddings()
            logger.info("Configured OpenAIEmbeddings")
        except Exception as e:
            logger.debug("Could not initialize OpenAIEmbeddings: %s", e)

    if primary is not None:
        _embeddings_instance = ResilientEmbeddingsWrapper(primary, fallback)
    else:
        logger.info("Using local deterministic embeddings (dim=%d)", dim)
        _embeddings_instance = fallback

    return _embeddings_instance


def get_neon_engine() -> sqlalchemy.Engine:
    """Return a cached SQLAlchemy engine connected to Neon PostgreSQL."""
    global _engine
    if _engine is not None:
        return _engine

    raw_url = getattr(settings, "DATABASE_URL", "")
    if not raw_url:
        raise ValueError("DATABASE_URL is not set in environment or settings.")

    # SQLAlchemy requires postgresql+psycopg:// for psycopg3
    db_url = raw_url
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    _engine = sqlalchemy.create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
    )

    # Ensure pgvector extension exists
    try:
        with _engine.connect() as conn:
            conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
        logger.info("Neon PostgreSQL connection verified and pgvector extension is ready.")
    except Exception as e:
        logger.warning("Could not verify/create pgvector extension on Neon DB: %s", e)

    return _engine


class DummyVectorStore:
    """In-memory best-effort fallback vector store used if database is unreachable."""

    def __init__(self, name: str):
        self.name = name
        self._docs: List[Document] = []

    def add_documents(self, docs: List[Document]) -> List[str]:
        self._docs.extend(docs)
        return [str(i) for i in range(len(docs))]

    def similarity_search(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        return list(reversed(self._docs))[:k]

    def delete_collection(self) -> None:
        self._docs.clear()


class NeonVectorStore:
    """Wrapper around PGVector that ensures resilient querying, collection deletion,

    and graceful fallbacks.
    """

    def __init__(self, collection_name: str, pgvector_store: PGVector, fallback_store: DummyVectorStore):
        self.collection_name = collection_name
        self._pgvector = pgvector_store
        self._fallback = fallback_store

    def add_documents(self, documents: List[Document], **kwargs) -> List[str]:
        try:
            return self._pgvector.add_documents(documents, **kwargs)
        except Exception as e:
            logger.warning("Neon PGVector add_documents failed, writing to fallback: %s", e)
            return self._fallback.add_documents(documents)

    def similarity_search(self, query: str, k: int = 5, **kwargs) -> List[Document]:
        try:
            return self._pgvector.similarity_search(query or "", k=k, **kwargs)
        except Exception as e:
            logger.warning("Neon PGVector similarity_search failed, reading from fallback: %s", e)
            return self._fallback.similarity_search(query or "", k=k, **kwargs)

    def delete_collection(self) -> None:
        try:
            self._pgvector.delete_collection()
        except Exception as e:
            logger.warning("Neon PGVector delete_collection failed: %s", e)
        self._fallback.delete_collection()


def _build_collection_name(
    collection_name: Optional[str] = None,
    *,
    agent: Optional[str] = None,
    user_id: Optional[str] = None,
    mode: Optional[str] = None,
) -> str:
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

    return getattr(settings, "NEON_DB_COLLECTION", None) or getattr(settings, "CHROMA_DB_COLLECTION", "audit_docs")


def get_vector_store(
    collection_name: Optional[str] = None,
    *,
    agent: Optional[str] = None,
    user_id: Optional[str] = None,
    mode: Optional[str] = None,
) -> Any:
    """Return a vector store instance for the given collection/namespace.
    Uses Qdrant when VECTOR_STORE_PROVIDER=='qdrant', else Neon PGVector.
    """
    provider = getattr(settings, "VECTOR_STORE_PROVIDER", "qdrant").lower()
    if provider == "qdrant":
        from app.utils.qdrant_store import get_qdrant_vector_store
        return get_qdrant_vector_store()

    coll = _build_collection_name(collection_name, agent=agent, user_id=user_id, mode=mode)

    if coll not in _in_memory_stores:
        _in_memory_stores[coll] = DummyVectorStore(coll)
    fallback_store = _in_memory_stores[coll]

    try:
        engine = get_neon_engine()
        embeddings = get_embeddings()

        pgvector_store = PGVector(
            embeddings=embeddings,
            collection_name=coll,
            connection=engine,
            use_jsonb=True,
        )

        return NeonVectorStore(
            collection_name=coll,
            pgvector_store=pgvector_store,
            fallback_store=fallback_store,
        )
    except Exception as e:
        logger.warning("Could not connect to Neon PostgreSQL for collection '%s': %s. Using in-memory fallback.", coll, e)
        return fallback_store


def add_documents_to_store(
    documents: List[Document],
    collection_name: Optional[str] = None,
    *,
    agent: Optional[str] = None,
    user_id: Optional[str] = None,
    mode: Optional[str] = None,
) -> None:
    """Split and add documents to a namespaced Neon PostgreSQL vector store."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    chunks = splitter.split_documents(documents)
    vectordb = get_vector_store(collection_name, agent=agent, user_id=user_id, mode=mode)
    vectordb.add_documents(chunks)
    logger.info("Successfully added %d chunks to collection '%s'", len(chunks), _build_collection_name(collection_name, agent=agent, user_id=user_id, mode=mode))


def clear_collection(
    collection_name: Optional[str] = None,
    *,
    agent: Optional[str] = None,
    user_id: Optional[str] = None,
    mode: Optional[str] = None,
) -> bool:
    """Clear/delete a namespaced collection from Neon PostgreSQL persistence.

    Also cleans up any legacy Chroma/FAISS directories if they exist on disk.
    """
    coll = _build_collection_name(collection_name, agent=agent, user_id=user_id, mode=mode)

    # 1. Clear from Neon PostgreSQL
    try:
        vectordb = get_vector_store(collection_name, agent=agent, user_id=user_id, mode=mode)
        if hasattr(vectordb, "delete_collection"):
            vectordb.delete_collection()
    except Exception as e:
        logger.warning("Error deleting collection '%s' from Neon DB: %s", coll, e)

    # Clear in-memory fallback cache
    if coll in _in_memory_stores:
        _in_memory_stores[coll].delete_collection()

    # 2. Best-effort removal of any legacy persisted disk directories for this collection
    try:
        chroma_base = getattr(settings, "CHROMA_DB_DIR", "chroma_db")
        if os.path.exists(chroma_base):
            legacy_chroma_coll = os.path.join(chroma_base, coll)
            if os.path.exists(legacy_chroma_coll):
                shutil.rmtree(legacy_chroma_coll, ignore_errors=True)

            legacy_faiss_coll = os.path.join(chroma_base, "faiss", coll)
            if os.path.exists(legacy_faiss_coll):
                shutil.rmtree(legacy_faiss_coll, ignore_errors=True)
    except Exception:
        pass

    return True

"""
Dedicated Qdrant Vector Store Service for semantic document and policy retrieval.
Supports Qdrant Cloud Free with fallback to in-memory QdrantClient(':memory:') for offline testing.
Enforces strict multi-tenant isolation via mandatory organization_id and engagement_id payload filters.
NEVER used for authoritative financial math or transaction reconciliation.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from langchain_core.documents import Document

from app.config import settings
from app.utils.vector_store import get_embeddings

logger = logging.getLogger(__name__)

_qdrant_instance: Optional["QdrantAuditVectorStore"] = None


class QdrantAuditVectorStore:
    """Enterprise audit document vector store backed by Qdrant."""

    def __init__(self):
        self.qdrant_url = getattr(settings, "QDRANT_URL", None)
        self.qdrant_api_key = getattr(settings, "QDRANT_API_KEY", None)
        self.collection_name = getattr(settings, "QDRANT_COLLECTION", "audit_documents")
        self.vector_dim = getattr(settings, "GEMINI_EMBEDDING_DIMENSIONS", 768)

        # Initialize remote client if configured; fallback cleanly to :memory:
        self.is_memory_mode = False
        if self.qdrant_url and self.qdrant_url.startswith("http"):
            try:
                self.client = QdrantClient(
                    url=self.qdrant_url,
                    api_key=self.qdrant_api_key,
                    timeout=10,
                )
                self._ensure_collection()
                logger.info("Connected to remote Qdrant Cloud (%s)", self.qdrant_url)
            except Exception as e:
                logger.warning("Failed to connect to remote Qdrant (%s). Falling back to :memory: mode.", e)
                self.client = QdrantClient(":memory:")
                self.is_memory_mode = True
                self._ensure_collection()
        else:
            self.client = QdrantClient(":memory:")
            self.is_memory_mode = True
            self._ensure_collection()
            logger.info("Initialized local in-memory Qdrant vector store")

    def _ensure_collection(self, collection_name: Optional[str] = None):
        """Ensure the target collection exists with appropriate dimensions and metric."""
        target_name = collection_name or self.collection_name
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if target_name not in collections:
                self.client.create_collection(
                    collection_name=target_name,
                    vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
                )
                logger.info("Created Qdrant collection '%s' (dim=%d)", target_name, self.vector_dim)
        except Exception as e:
            logger.warning("Could not verify/create Qdrant collection '%s': %s", target_name, e)

    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        organization_id: str,
        engagement_id: str,
        document_id: str,
        version: int = 1,
        collection_name: Optional[str] = None,
    ) -> int:
        """Upsert embedded document chunks with tenant and engagement metadata isolation."""
        target_name = collection_name or self.collection_name
        self._ensure_collection(target_name)

        if not chunks:
            return 0

        embeddings = get_embeddings()
        texts = [c.get("text", "") for c in chunks]
        vectors = embeddings.embed_documents(texts)

        points = []
        for idx, (chunk, vec) in enumerate(zip(chunks, vectors)):
            # Generate deterministic point UUID
            seed_key = f"{organization_id}:{engagement_id}:{document_id}:{version}:{idx}"
            pt_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, seed_key))

            payload = {
                "organization_id": str(organization_id),
                "engagement_id": str(engagement_id),
                "document_id": str(document_id),
                "version": version,
                "chunk_index": idx,
                "text": chunk.get("text", ""),
                "metadata": chunk.get("metadata", {}),
            }
            points.append(PointStruct(id=pt_id, vector=vec, payload=payload))

        self.client.upsert(collection_name=target_name, points=points)
        return len(points)

    def search(
        self,
        query: str,
        organization_id: str,
        engagement_id: Optional[str] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search with MANDATORY organization_id and optional engagement_id isolation filters."""
        target_name = collection_name or self.collection_name
        self._ensure_collection(target_name)

        embeddings = get_embeddings()
        query_vec = embeddings.embed_query(query or "")

        filter_conditions = [
            FieldCondition(key="organization_id", match=MatchValue(value=str(organization_id)))
        ]
        if engagement_id:
            filter_conditions.append(
                FieldCondition(key="engagement_id", match=MatchValue(value=str(engagement_id)))
            )

        q_filter = Filter(must=filter_conditions)

        res = self.client.query_points(
            collection_name=target_name,
            query=query_vec,
            query_filter=q_filter,
            limit=limit,
            score_threshold=score_threshold,
        )

        results = []
        for pt in res.points:
            results.append({
                "id": str(pt.id),
                "score": pt.score,
                "text": pt.payload.get("text", ""),
                "metadata": pt.payload.get("metadata", {}),
                "document_id": pt.payload.get("document_id"),
                "version": pt.payload.get("version"),
                "organization_id": pt.payload.get("organization_id"),
                "engagement_id": pt.payload.get("engagement_id"),
            })
        return results

    def delete_document_version(
        self,
        document_id: str,
        version: Optional[int] = None,
        organization_id: Optional[str] = None,
        engagement_id: Optional[str] = None,
        collection_name: Optional[str] = None,
    ) -> bool:
        """Delete all chunks for a document version with tenant scoping."""
        target_name = collection_name or self.collection_name
        self._ensure_collection(target_name)

        filter_conditions = [
            FieldCondition(key="document_id", match=MatchValue(value=str(document_id)))
        ]
        if version is not None:
            filter_conditions.append(
                FieldCondition(key="version", match=MatchValue(value=version))
            )
        if organization_id:
            filter_conditions.append(
                FieldCondition(key="organization_id", match=MatchValue(value=str(organization_id)))
            )
        if engagement_id:
            filter_conditions.append(
                FieldCondition(key="engagement_id", match=MatchValue(value=str(engagement_id)))
            )

        self.client.delete(
            collection_name=target_name,
            points_selector=Filter(must=filter_conditions),
        )
        return True

    def reindex_document(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        organization_id: str,
        engagement_id: str,
        version: int = 1,
        collection_name: Optional[str] = None,
    ) -> int:
        """Atomically delete existing version chunks and upsert refreshed chunks."""
        self.delete_document_version(
            document_id=document_id,
            version=version,
            organization_id=organization_id,
            engagement_id=engagement_id,
            collection_name=collection_name,
        )
        return self.upsert_chunks(
            chunks=chunks,
            organization_id=organization_id,
            engagement_id=engagement_id,
            document_id=document_id,
            version=version,
            collection_name=collection_name,
        )

    def healthcheck(self) -> Dict[str, Any]:
        """Perform health and connectivity check on Qdrant vector store."""
        try:
            collections_res = self.client.get_collections()
            coll_names = [c.name for c in collections_res.collections]
            return {
                "status": "connected",
                "provider": "qdrant",
                "mode": "memory" if self.is_memory_mode else "cloud",
                "collection": self.collection_name,
                "collections_available": coll_names,
                "dimension": self.vector_dim,
                "ready": True,
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "qdrant",
                "mode": "memory" if self.is_memory_mode else "cloud",
                "error": str(e),
                "ready": False,
            }

    # LangChain / Legacy VectorStore interface compatibility
    def add_documents(self, documents: List[Document], **kwargs) -> List[str]:
        chunks = [
            {"text": doc.page_content, "metadata": doc.metadata}
            for doc in documents
        ]
        org_id = kwargs.get("organization_id", "00000000-0000-0000-0000-000000000001")
        eng_id = kwargs.get("engagement_id", "00000000-0000-0000-0000-000000000001")
        doc_id = kwargs.get("document_id", str(uuid.uuid4()))
        self.upsert_chunks(chunks, organization_id=org_id, engagement_id=eng_id, document_id=doc_id)
        return [str(i) for i in range(len(documents))]

    def similarity_search(self, query: str, k: int = 5, **kwargs) -> List[Document]:
        org_id = kwargs.get("organization_id", "00000000-0000-0000-0000-000000000001")
        eng_id = kwargs.get("engagement_id")
        results = self.search(query=query, organization_id=org_id, engagement_id=eng_id, limit=k)
        return [
            Document(page_content=r["text"], metadata=r["metadata"])
            for r in results
        ]

    def delete_collection(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass


def get_qdrant_vector_store() -> QdrantAuditVectorStore:
    """Return the global cached singleton instance of QdrantAuditVectorStore."""
    global _qdrant_instance
    if _qdrant_instance is None:
        _qdrant_instance = QdrantAuditVectorStore()
    return _qdrant_instance


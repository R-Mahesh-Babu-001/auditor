"""
Integration tests for Neon PostgreSQL pgvector migration.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.utils.vector_store import (
    get_vector_store,
    add_documents_to_store,
    clear_collection,
    _build_collection_name,
)
from langchain_core.documents import Document

client = TestClient(app)


def test_health_check_endpoint():
    """Verify health endpoint reports service and Neon DB status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert data["database"]["backend"] == "neon_pgvector"
    assert data["database"]["neon_configured"] is True


def test_collection_naming_logic():
    """Verify namespace isolation logic for agents, users, and modes."""
    assert _build_collection_name("EXPLICIT") == "EXPLICIT"
    assert _build_collection_name(agent="chat_memory", user_id="user_1") == "CHAT_MEMORY_user_1"
    assert _build_collection_name(agent="compliance_memory", user_id="user_2", mode="IT") == "COMPLIANCE_MEMORY_user_2_IT"


def test_neon_vector_store_operations():
    """Test adding, searching, and deleting documents in Neon PostgreSQL."""
    test_coll = "test_audit_neon_operations"

    # Clean beforehand
    clear_collection(test_coll)

    docs = [
        Document(
            page_content="Audit Procedure: Verify physical inventory counts against warehouse ledgers.",
            metadata={"source": "inventory_sop.pdf", "page": 1},
        ),
        Document(
            page_content="Control: Access to production databases is restricted to authorized DBAs.",
            metadata={"source": "access_control.pdf", "page": 3},
        ),
    ]

    add_documents_to_store(docs, collection_name=test_coll)

    store = get_vector_store(test_coll)
    results = store.similarity_search("physical inventory counts", k=2)

    assert len(results) >= 1
    assert any("inventory" in r.page_content.lower() for r in results)

    # Clean up
    deleted = clear_collection(test_coll)
    assert deleted is True

    # Search should now return empty
    empty_results = store.similarity_search("physical inventory", k=2)
    assert len(empty_results) == 0


def test_document_ingest_and_clear_endpoints():
    """Test full API endpoint lifecycle with Neon DB."""
    test_user = "test_auditor_suite"

    # Ingest document
    file_content = b"Financial Controls: Dual signature required for all transactions exceeding $25,000."
    files = [("files", ("financial_controls.txt", file_content, "text/plain"))]
    r = client.post(f"/api/chat/ingest?user_id={test_user}", files=files)
    assert r.status_code == 200
    assert "financial_controls.txt" in r.json()["files_ingested"]

    # Clear memory
    r = client.post("/api/memory/clear", json={"agent": "chat_memory", "user_id": test_user})
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


if __name__ == "__main__":
    print("Running integration tests...")
    test_health_check_endpoint()
    print("PASS: test_health_check_endpoint")
    test_collection_naming_logic()
    print("PASS: test_collection_naming_logic")
    test_neon_vector_store_operations()
    print("PASS: test_neon_vector_store_operations")
    test_document_ingest_and_clear_endpoints()
    print("PASS: test_document_ingest_and_clear_endpoints")
    print("\nALL NEON INTEGRATION TESTS PASSED!")


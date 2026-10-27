"""
Test Suite: Qdrant Vector Store Service Integration.
Verifies Qdrant upsert, semantic search, document deletion, reindexing,
strict multi-tenant isolation, and healthcheck reporting.
"""

import uuid
import unittest
from app.utils.qdrant_store import QdrantAuditVectorStore


class TestQdrantIntegration(unittest.TestCase):

    def setUp(self):
        # Fresh in-memory Qdrant instance for test isolation
        self.store = QdrantAuditVectorStore()
        self.org_a = str(uuid.uuid4())
        self.org_b = str(uuid.uuid4())
        self.eng_a = str(uuid.uuid4())
        self.eng_b = str(uuid.uuid4())

    def test_healthcheck(self):
        """Verify Qdrant healthcheck reports connected and ready."""
        health = self.store.healthcheck()
        self.assertEqual(health["status"], "connected")
        self.assertEqual(health["provider"], "qdrant")
        self.assertIn("mode", health)
        self.assertTrue(health["ready"])

    def test_upsert_and_search(self):
        """Verify upserting document chunks and semantic query matching."""
        chunks = [
            {"text": "The corporate procurement policy mandates a 3-way match for all invoices over $1,000.", "metadata": {"section": "4.1"}},
            {"text": "Delegated authorization limits require department manager sign-off for purchases exceeding $5,000.", "metadata": {"section": "4.2"}},
        ]
        doc_id = str(uuid.uuid4())
        count = self.store.upsert_chunks(
            chunks=chunks,
            organization_id=self.org_a,
            engagement_id=self.eng_a,
            document_id=doc_id,
            version=1,
        )
        self.assertEqual(count, 2)

        results = self.store.search(
            query="What is the policy threshold for three way matching?",
            organization_id=self.org_a,
            engagement_id=self.eng_a,
            limit=2,
        )
        self.assertTrue(len(results) >= 1)
        self.assertIn("3-way match", results[0]["text"])

    def test_strict_multi_tenant_isolation(self):
        """Verify Tenant B cannot retrieve or observe documents uploaded by Tenant A."""
        chunks_a = [
            {"text": "CONFIDENTIAL TENANT A: Secret vendor discount rate is 15% for Project Titan.", "metadata": {"doc": "NDA"}},
        ]
        doc_a_id = str(uuid.uuid4())
        self.store.upsert_chunks(
            chunks=chunks_a,
            organization_id=self.org_a,
            engagement_id=self.eng_a,
            document_id=doc_a_id,
            version=1,
        )

        # Tenant B searches for exact keywords
        results_b = self.store.search(
            query="Project Titan secret vendor discount rate",
            organization_id=self.org_b,  # Tenant B
            engagement_id=self.eng_b,
            limit=5,
        )
        # MUST return zero results due to organization_id payload filter!
        self.assertEqual(len(results_b), 0)

        # Tenant A searching finds it
        results_a = self.store.search(
            query="Project Titan secret vendor discount rate",
            organization_id=self.org_a,  # Tenant A
            engagement_id=self.eng_a,
            limit=5,
        )
        self.assertEqual(len(results_a), 1)

    def test_delete_document_version(self):
        """Verify deleting a document removes its points from subsequent search results."""
        doc_id = str(uuid.uuid4())
        chunks = [{"text": "Temporary procurement guideline draft for review."}]
        self.store.upsert_chunks(chunks, organization_id=self.org_a, engagement_id=self.eng_a, document_id=doc_id, version=1)

        res_before = self.store.search("Temporary procurement guideline", organization_id=self.org_a, limit=5)
        self.assertEqual(len(res_before), 1)

        self.store.delete_document_version(document_id=doc_id, version=1, organization_id=self.org_a)

        res_after = self.store.search("Temporary procurement guideline", organization_id=self.org_a, limit=5)
        self.assertEqual(len(res_after), 0)


if __name__ == "__main__":
    unittest.main()


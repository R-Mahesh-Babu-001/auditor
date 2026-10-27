"""
Test Suite: Workpaper generation, facts packet hashing, and reviewer sign-off gate.
Verifies SHA-256 facts packet hashing, initial draft status, and requirement of Reviewer role for approval.
"""

import uuid
import unittest
from datetime import date, datetime
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.audit.workpapers import generate_structured_workpaper
from app.routers.workpapers import approve_workpaper
from app.routers.auth import OrganizationContext
from app.models import (
    AuditEngagement,
    AuditCriterion,
    AuditTestRun,
    AuditException,
    EvidenceFile,
    AuditDataset,
    Workpaper,
    WorkpaperVersion,
    WorkpaperExceptionLink,
    WorkpaperEvidenceLink,
)


class TestWorkpaperGeneration(unittest.TestCase):

    def setUp(self):
        self.org_id = uuid.uuid4()
        self.eng_id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        self.reviewer_id = uuid.uuid4()

    def test_workpaper_generation_and_facts_hashing(self):
        """Verify workpaper compiles facts packet, computes SHA-256 hash, and initializes in draft status."""
        mock_db = MagicMock()

        mock_eng = MagicMock(spec=AuditEngagement)
        mock_eng.id = self.eng_id
        mock_eng.organization_id = self.org_id
        mock_eng.engagement_code = "ENG-2026-P2P"
        mock_eng.name = "Q1 P2P Internal Audit"
        mock_eng.business_unit = "Supply Chain"
        mock_eng.objective = "Evaluate three-way matching effectiveness."
        mock_eng.period_start = date(2026, 1, 1)
        mock_eng.period_end = date(2026, 3, 31)

        mock_criterion = MagicMock(spec=AuditCriterion)
        mock_criterion.id = uuid.uuid4()
        mock_criterion.criterion_code = "CRIT-01"
        mock_criterion.title = "3-Way Match Policy"
        mock_criterion.requirement_text = "Invoices must match PO and GR within 1% tolerance."

        mock_tr = MagicMock(spec=AuditTestRun)
        mock_tr.id = uuid.uuid4()
        mock_tr.rule_id = uuid.uuid4()
        mock_tr.population_count = 150
        mock_tr.passed_count = 148
        mock_tr.exception_count = 2
        mock_tr.parameters_snapshot = {"tolerance_pct": 1.0}

        mock_exc1 = MagicMock(spec=AuditException)
        mock_exc1.id = uuid.uuid4()
        mock_exc1.exception_key = "3WAY-QTY-001"
        mock_exc1.exception_type = "quantity_variance"
        mock_exc1.severity = "high"
        mock_exc1.title = "Invoiced 100 vs Received 80"
        mock_exc1.description = "Billed 20 units above verified delivery."
        mock_exc1.observed_values = {"invoiced": 100, "received": 80}
        mock_exc1.expected_values = {"max": 80}

        mock_file = MagicMock(spec=EvidenceFile)
        mock_file.id = uuid.uuid4()
        mock_file.original_filename = "Procurement_Policy_v3.pdf"
        mock_file.evidence_category = "policy"

        mock_ds = MagicMock(spec=AuditDataset)
        mock_ds.id = uuid.uuid4()
        mock_ds.dataset_code = "DS-P2P-01"
        mock_ds.dataset_name = "P2P Transactions Q1"
        mock_ds.dataset_type = "invoices"
        mock_ds.version_number = 1
        mock_ds.row_count = 150
        mock_ds.valid_row_count = 150

        added_objects = []
        mock_db.add.side_effect = lambda obj: added_objects.append(obj)

        def query_model(model):
            mock_q = MagicMock()
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng
                return mock_q
            if model == AuditCriterion:
                mock_q.filter.return_value.all.return_value = [mock_criterion]
                return mock_q
            if model == AuditTestRun:
                mock_q.filter.return_value.order_by.return_value.all.return_value = [mock_tr]
                return mock_q
            if model == AuditException:
                mock_q.filter.return_value.all.return_value = [mock_exc1]
                return mock_q
            if model == EvidenceFile:
                mock_q.filter.return_value.all.return_value = [mock_file]
                return mock_q
            if model == AuditDataset:
                mock_q.filter.return_value.all.return_value = [mock_ds]
                return mock_q
            mock_q.filter.return_value.first.return_value = None
            mock_q.filter.return_value.all.return_value = []
            return mock_q

        mock_db.query.side_effect = query_model

        res = generate_structured_workpaper(
            db=mock_db,
            organization_id=self.org_id,
            engagement_id=self.eng_id,
            title="Procure-to-Pay Operational Testing Summary",
            user_id=self.user_id,
        )

        self.assertEqual(res["status"], "success")
        self.assertIsNotNone(res["input_snapshot_hash"])
        self.assertEqual(len(res["input_snapshot_hash"]), 64)  # Valid SHA-256 hex string
        self.assertEqual(res["review_status"], "pending_review")

        # Verify Workpaper created in draft status
        wps = [o for o in added_objects if isinstance(o, Workpaper)]
        self.assertEqual(len(wps), 1)
        self.assertEqual(wps[0].status, "draft")  # Non-negotiable: never auto-approve!

        # Verify WorkpaperVersion pending review
        versions = [o for o in added_objects if isinstance(o, WorkpaperVersion)]
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0].review_status, "pending_review")
        self.assertEqual(versions[0].input_snapshot_hash, res["input_snapshot_hash"])

    def test_reviewer_approval_gate(self):
        """Verify only users with Reviewer/Manager role can approve a workpaper."""
        mock_db = MagicMock()
        wp_id = uuid.uuid4()

        mock_wp = MagicMock(spec=Workpaper)
        mock_wp.id = wp_id
        mock_wp.organization_id = self.org_id
        mock_wp.status = "draft"
        mock_wp.workpaper_code = "WP-P2P-TEST"

        mock_version = MagicMock(spec=WorkpaperVersion)
        mock_version.workpaper_id = wp_id
        mock_version.organization_id = self.org_id
        mock_version.review_status = "pending_review"

        def query_model(model):
            mock_q = MagicMock()
            if model == Workpaper:
                mock_q.filter.return_value.first.return_value = mock_wp
                return mock_q
            if model == WorkpaperVersion:
                mock_q.filter.return_value.order_by.return_value.first.return_value = mock_version
                return mock_q
            return mock_q

        mock_db.query.side_effect = query_model

        # 1. Staff Auditor attempt to approve must be rejected with 403
        auditor_ctx = OrganizationContext(
            organization_id=self.org_id,
            user_id=self.user_id,
            role="auditor",
        )
        with self.assertRaises(HTTPException) as cm:
            from app.routers.auth import require_reviewer_role
            require_reviewer_role(auditor_ctx)
        self.assertEqual(cm.exception.status_code, 403)

        # 2. Reviewer / Manager approval succeeds
        reviewer_ctx = OrganizationContext(
            organization_id=self.org_id,
            user_id=self.reviewer_id,
            role="audit_manager",
        )
        res = approve_workpaper(
            workpaper_id=str(wp_id),
            req=None,
            ctx=reviewer_ctx,
            db=mock_db,
        )

        self.assertEqual(res["status"], "approved")
        self.assertEqual(mock_wp.status, "approved")
        self.assertEqual(mock_wp.approved_by, self.reviewer_id)
        self.assertEqual(mock_version.review_status, "approved")
        self.assertEqual(mock_version.reviewed_by, self.reviewer_id)


if __name__ == "__main__":
    unittest.main()


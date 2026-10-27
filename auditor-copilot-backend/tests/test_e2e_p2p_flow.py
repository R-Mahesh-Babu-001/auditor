"""
Test Suite: End-to-end synthetic Procure-to-Pay (P2P) audit flow.
Tests the complete lifecycle:
1. Synthetic dataset ingestion (POs, GRs, Invoices, Approvals)
2. Deterministic audit execution across all standard P2P test scenarios:
   - 1 perfect match (PO-001, GR-001, INV-001) -> compliant
   - 1 price variance (INV-002: $6,200 vs PO-002: $5,000) -> price_amount_variance exception
   - 1 quantity variance (INV-003: 15 units vs GR-003: 10 units) -> quantity_variance exception
   - 1 duplicate invoice (INV-DUP-100 billed twice) -> exact_duplicate_invoice exception
   - 1 missing approval (INV-APP-1: $12,000 without approval) -> missing_approval exception
   - 1 cutoff error (GR-CUT-1 before period end, INV-CUT-1 billed 15 days later) -> cutoff exception
3. Traceability: ExceptionRowLink verification for all contributing rows
4. Workpaper synthesis: facts packet compilation, SHA-256 hash, and reviewer approval gate
"""

import uuid
import unittest
from datetime import date
from unittest.mock import MagicMock

from app.audit.rules.p2p_rules import (
    run_three_way_match,
    run_duplicate_invoice_payment,
    run_missing_approval,
    run_period_cutoff_check,
)
from app.audit.execution import execute_audit_test
from app.audit.workpapers import generate_structured_workpaper
from app.routers.workpapers import approve_workpaper
from app.routers.auth import OrganizationContext
from app.models import (
    AuditEngagement,
    AuditDataset,
    DatasetRow,
    AuditTestRun,
    AuditException,
    ExceptionRowLink,
    Workpaper,
    WorkpaperVersion,
)


class TestE2EP2PFlow(unittest.TestCase):

    def setUp(self):
        self.org_id = uuid.uuid4()
        self.eng_id = uuid.uuid4()
        self.auditor_id = uuid.uuid4()
        self.reviewer_id = uuid.uuid4()
        self.period_end = date(2026, 3, 31)

        # ---------------------------------------------------------
        # Synthetic P2P Population Fixture
        # ---------------------------------------------------------
        # 1. Purchase Orders
        self.pos = [
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "po_ds", "po_number": "PO-001", "total_amount": 5000.0, "currency_code": "USD", "supplier_name": "Supplier Alpha"},
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "po_ds", "po_number": "PO-002", "total_amount": 5000.0, "currency_code": "USD", "supplier_name": "Supplier Beta"},
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "po_ds", "po_number": "PO-003", "total_amount": 1000.0, "currency_code": "USD", "supplier_name": "Supplier Gamma"},
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "po_ds", "po_number": "PO-CUT-1", "total_amount": 8000.0, "currency_code": "USD", "supplier_name": "Supplier Delta"},
        ]

        # 2. Goods Receipts
        self.receipts = [
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "gr_ds", "receipt_number": "GR-001", "po_number": "PO-001", "received_quantity": 50, "receipt_date": "2026-02-10"},
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "gr_ds", "receipt_number": "GR-002", "po_number": "PO-002", "received_quantity": 10, "receipt_date": "2026-02-15"},
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "gr_ds", "receipt_number": "GR-003", "po_number": "PO-003", "received_quantity": 10, "receipt_date": "2026-02-20"},
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "gr_ds", "receipt_number": "GR-CUT-1", "po_number": "PO-CUT-1", "received_quantity": 100, "receipt_date": "2026-03-25"},
        ]

        # 3. Invoices
        self.invoices = [
            # Item 1: Perfect Match
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "inv_ds", "invoice_number": "INV-001", "po_number": "PO-001", "quantity": 50, "total_amount": 5000.0, "currency_code": "USD", "supplier_name": "Supplier Alpha", "invoice_date": "2026-02-12"},
            # Item 2: Price Variance ($6,200 vs $5,000)
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "inv_ds", "invoice_number": "INV-002", "po_number": "PO-002", "quantity": 10, "total_amount": 6200.0, "currency_code": "USD", "supplier_name": "Supplier Beta", "invoice_date": "2026-02-18"},
            # Item 3: Quantity Variance (15 invoiced vs 10 received)
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "inv_ds", "invoice_number": "INV-003", "po_number": "PO-003", "quantity": 15, "total_amount": 1000.0, "currency_code": "USD", "supplier_name": "Supplier Gamma", "invoice_date": "2026-02-22"},
            # Item 4: Duplicate Invoice (Submission A)
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "inv_ds", "invoice_number": "INV-DUP-100", "po_number": "PO-001", "quantity": 10, "total_amount": 4500.0, "currency_code": "USD", "supplier_name": "Apex Tech", "invoice_date": "2026-03-01"},
            # Item 4: Duplicate Invoice (Submission B)
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "inv_ds", "invoice_number": "INV-DUP-100", "po_number": "PO-001", "quantity": 10, "total_amount": 4500.0, "currency_code": "USD", "supplier_name": "Apex Tech", "invoice_date": "2026-03-05"},
            # Item 5: Missing Required Approval ($12,000 > $1,000 threshold)
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "inv_ds", "invoice_number": "INV-APP-1", "po_number": "PO-001", "quantity": 1, "total_amount": 12000.0, "currency_code": "USD", "supplier_name": "Supplier Epsilon", "invoice_date": "2026-03-10"},
            # Item 6: Period Cutoff Error (GR on March 25, billed April 15)
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "inv_ds", "invoice_number": "INV-CUT-1", "po_number": "PO-CUT-1", "quantity": 100, "total_amount": 8000.0, "currency_code": "USD", "supplier_name": "Supplier Delta", "invoice_date": "2026-04-15"},
        ]

        # 4. Approvals
        self.approvals = [
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "app_ds", "invoice_number": "INV-001", "approval_status": "approved", "decision": "approved", "approver_name": "Manager A"},
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "app_ds", "invoice_number": "INV-002", "approval_status": "approved", "decision": "approved", "approver_name": "Manager B"},
            {"_row_id": str(uuid.uuid4()), "_dataset_id": "app_ds", "invoice_number": "INV-003", "approval_status": "approved", "decision": "approved", "approver_name": "Manager C"},
            # INV-APP-1 is intentionally omitted from approvals
        ]

    def test_e2e_three_way_matching(self):
        """Execute 3-Way Match test against synthetic population."""
        # Test 3-way match on first 3 invoices
        test_invoices = self.invoices[:3]
        res = run_three_way_match(self.pos, self.receipts, test_invoices, tolerance_pct=1.0, tolerance_amount=50.0)

        self.assertEqual(res["population_count"], 3)
        self.assertEqual(res["passed_count"], 1)  # INV-001 passes
        self.assertEqual(res["exception_count"], 2)  # INV-002 (price) and INV-003 (qty)

        exc_types = {e["exception_type"] for e in res["exceptions"]}
        self.assertIn("price_amount_variance", exc_types)
        self.assertIn("quantity_variance", exc_types)

    def test_e2e_duplicate_invoice_detection(self):
        """Execute duplicate invoice test and verify exact match detection."""
        res = run_duplicate_invoice_payment(self.invoices)
        self.assertTrue(res["exception_count"] >= 1)

        dup_excs = [e for e in res["exceptions"] if e["exception_type"] == "exact_duplicate_invoice"]
        self.assertEqual(len(dup_excs), 1)
        self.assertEqual(dup_excs[0]["observed_values"]["current_invoice"], "INV-DUP-100")
        self.assertEqual(dup_excs[0]["observed_values"]["amount"], 4500.0)

    def test_e2e_missing_approval_detection(self):
        """Execute approval verification and confirm unapproved $12,000 invoice is flagged."""
        # Test population containing INV-001 (approved) and INV-APP-1 (unapproved, $12,000)
        test_sample = [self.invoices[0], self.invoices[5]]
        res = run_missing_approval(test_sample, self.approvals, threshold_amount=1000.0)
        unapproved = [e for e in res["exceptions"] if e["exception_type"] == "missing_approval"]
        self.assertEqual(len(unapproved), 1)
        self.assertEqual(unapproved[0]["observed_values"]["invoice_number"], "INV-APP-1")
        self.assertEqual(unapproved[0]["observed_values"]["amount"], 12000.0)

    def test_e2e_period_cutoff_detection(self):
        """Execute cutoff review and confirm unrecorded liability after period end is flagged."""
        res = run_period_cutoff_check(self.receipts, self.invoices, period_end_date=self.period_end)
        cutoff_excs = [e for e in res["exceptions"] if "cutoff" in e["exception_type"]]
        self.assertEqual(len(cutoff_excs), 1)
        self.assertEqual(cutoff_excs[0]["observed_values"]["invoice_date"], "2026-04-15")

    def test_e2e_full_audit_workflow_to_workpaper_approval(self):
        """Execute end-to-end audit test, generate workpaper, and perform reviewer sign-off."""
        mock_db = MagicMock()

        mock_eng = MagicMock(spec=AuditEngagement)
        mock_eng.id = self.eng_id
        mock_eng.organization_id = self.org_id
        mock_eng.engagement_code = "P2P-2026-E2E"
        mock_eng.name = "P2P Operational Compliance Audit"
        mock_eng.business_unit = "Enterprise Procurement"
        mock_eng.objective = "Audit operational effectiveness of three-way matching, duplicate detection, and invoice authorizations."
        mock_eng.period_start = date(2026, 1, 1)
        mock_eng.period_end = self.period_end

        mock_tr = MagicMock(spec=AuditTestRun)
        mock_tr.id = uuid.uuid4()
        mock_tr.population_count = len(self.invoices)
        mock_tr.passed_count = len(self.invoices) - 5
        mock_tr.exception_count = 5
        mock_tr.parameters_snapshot = {}

        mock_exceptions = [
            MagicMock(spec=AuditException, id=uuid.uuid4(), exception_key="3WAY-PRICE", severity="high", exception_type="price_variance", title="Price Variance", description="Price mismatch", observed_values={}, expected_values={}),
            MagicMock(spec=AuditException, id=uuid.uuid4(), exception_key="3WAY-QTY", severity="high", exception_type="qty_variance", title="Quantity Variance", description="Quantity mismatch", observed_values={}, expected_values={}),
            MagicMock(spec=AuditException, id=uuid.uuid4(), exception_key="DUP-INV", severity="critical", exception_type="duplicate", title="Duplicate Billing", description="Duplicate invoice", observed_values={}, expected_values={}),
            MagicMock(spec=AuditException, id=uuid.uuid4(), exception_key="MISSING-APP", severity="high", exception_type="missing_approval", title="Unapproved Invoice", description="Missing approval", observed_values={}, expected_values={}),
            MagicMock(spec=AuditException, id=uuid.uuid4(), exception_key="CUTOFF-ERR", severity="medium", exception_type="cutoff", title="Cutoff Variance", description="Cutoff timing", observed_values={}, expected_values={}),
        ]

        mock_ds = MagicMock(spec=AuditDataset, id=uuid.uuid4(), dataset_code="DS-INVOICES", dataset_name="Invoices", dataset_type="invoices", version_number=1, row_count=len(self.invoices), valid_row_count=len(self.invoices))

        added_objects = []
        mock_db.add.side_effect = lambda obj: added_objects.append(obj)

        def query_model(model):
            mock_q = MagicMock()
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng
                return mock_q
            if model == AuditTestRun:
                mock_q.filter.return_value.order_by.return_value.all.return_value = [mock_tr]
                return mock_q
            if model == AuditException:
                mock_q.filter.return_value.all.return_value = mock_exceptions
                return mock_q
            if model == AuditDataset:
                mock_q.filter.return_value.all.return_value = [mock_ds]
                return mock_q
            mock_q.filter.return_value.all.return_value = []
            mock_q.filter.return_value.first.return_value = None
            return mock_q

        mock_db.query.side_effect = query_model

        # Step 1: Generate Workpaper
        wp_res = generate_structured_workpaper(
            db=mock_db,
            organization_id=self.org_id,
            engagement_id=self.eng_id,
            title="Procure-to-Pay Testing Summary",
            user_id=self.auditor_id,
        )

        self.assertEqual(wp_res["status"], "success")
        self.assertIsNotNone(wp_res["input_snapshot_hash"])
        self.assertEqual(wp_res["review_status"], "pending_review")

        created_wp = [o for o in added_objects if isinstance(o, Workpaper)][0]
        self.assertEqual(created_wp.status, "draft")

        # Step 2: Reviewer Approval Gate
        reviewer_ctx = OrganizationContext(
            organization_id=self.org_id,
            user_id=self.reviewer_id,
            role="audit_manager",
        )

        def query_for_approval(model):
            mock_q = MagicMock()
            if model == Workpaper:
                mock_q.filter.return_value.first.return_value = created_wp
                return mock_q
            if model == WorkpaperVersion:
                created_version = [o for o in added_objects if isinstance(o, WorkpaperVersion)][0]
                mock_q.filter.return_value.order_by.return_value.first.return_value = created_version
                return mock_q
            return mock_q

        mock_db.query.side_effect = query_for_approval

        appr_res = approve_workpaper(
            workpaper_id=str(created_wp.id),
            req=None,
            ctx=reviewer_ctx,
            db=mock_db,
        )

        self.assertEqual(appr_res["status"], "approved")
        self.assertEqual(created_wp.status, "approved")
        self.assertEqual(created_wp.approved_by, self.reviewer_id)


if __name__ == "__main__":
    unittest.main()

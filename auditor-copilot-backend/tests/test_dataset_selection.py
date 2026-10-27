"""
Test Suite: Dataset-specific selection and deterministic rule execution.
Verifies that audit tests strictly query and resolve typed datasets, reject missing or ambiguous datasets,
and maintain exact numerical precision without mixing records across collections.
"""

import uuid
import unittest
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, patch

from app.audit.execution import (
    RULE_SPECIFICATIONS,
    resolve_rule_spec,
    execute_audit_test,
)
from app.audit.rules.p2p_rules import run_three_way_match
from app.models import AuditDataset, AuditEngagement, DatasetRow


class TestDatasetSelection(unittest.TestCase):

    def test_rule_specifications_completeness(self):
        """Verify all standard audit rules define required dataset types."""
        expected_rules = [
            "P2P_THREE_WAY_MATCH",
            "P2P_DUPLICATE_INVOICE_PAYMENT",
            "P2P_MISSING_APPROVAL",
            "P2P_THRESHOLD_SPLITTING",
            "P2P_PO_INVOICE_MISMATCH",
            "P2P_PERIOD_CUTOFF",
            "P2P_BANK_CHANGE_TIMING",
            "P2P_SUPPLIER_MASTER_DUPLICATION",
            "P2P_SAMPLE_SELECTION",
            "ITGC_SOD_ANALYSIS",
            "VENDOR_ASSURANCE_REVIEW",
            "AI_GOVERNANCE_REVIEW",
        ]
        for rule_code in expected_rules:
            spec = resolve_rule_spec(rule_code)
            self.assertIsNotNone(spec, f"Rule spec missing for {rule_code}")
            self.assertIn("required_dataset_types", spec)
            self.assertTrue(len(spec["required_dataset_types"]) >= 1)

    def test_three_way_match_requires_three_distinct_types(self):
        """Verify 3-way match requires purchase_orders, goods_receipts, and invoices."""
        spec = resolve_rule_spec("P2P_THREE_WAY_MATCH")
        required = spec["required_dataset_types"]
        self.assertEqual(set(required), {"purchase_orders", "goods_receipts", "invoices"})

    def test_missing_dataset_type_error(self):
        """Verify execution returns MISSING_DATASET_TYPE when a required dataset type is not present."""
        mock_db = MagicMock()
        org_id = uuid.uuid4()
        eng_id = uuid.uuid4()

        # Engagement exists
        mock_eng = MagicMock()
        mock_eng.id = eng_id
        mock_eng.organization_id = org_id
        mock_eng.period_end = date(2026, 3, 31)

        # DB queries
        def query_side_effect(model):
            mock_q = MagicMock()
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng
                return mock_q
            if model == AuditDataset:
                # No datasets present
                mock_q.filter.return_value.all.return_value = []
                mock_q.filter.return_value.first.return_value = None
                return mock_q
            mock_q.filter.return_value.first.return_value = None
            mock_q.filter.return_value.all.return_value = []
            return mock_q

        mock_db.query.side_effect = query_side_effect

        res = execute_audit_test(
            db=mock_db,
            organization_id=org_id,
            engagement_id=eng_id,
            rule_code="P2P_THREE_WAY_MATCH",
        )

        self.assertEqual(res["status"], "failed")
        self.assertEqual(res["error_code"], "MISSING_DATASET_TYPE")
        self.assertIn("Missing required dataset type", res["error"])

    def test_ambiguous_dataset_selection_error(self):
        """Verify execution returns AMBIGUOUS_DATASET_SELECTION when multiple datasets of the same type exist without explicit selection."""
        mock_db = MagicMock()
        org_id = uuid.uuid4()
        eng_id = uuid.uuid4()

        mock_eng = MagicMock()
        mock_eng.id = eng_id
        mock_eng.organization_id = org_id

        # 2 distinct invoice datasets in same engagement
        inv_ds_1 = MagicMock(spec=AuditDataset)
        inv_ds_1.id = uuid.uuid4()
        inv_ds_1.dataset_name = "North America Invoices Q1"
        inv_ds_1.dataset_type = "invoices"

        inv_ds_2 = MagicMock(spec=AuditDataset)
        inv_ds_2.id = uuid.uuid4()
        inv_ds_2.dataset_name = "EMEA Invoices Q1"
        inv_ds_2.dataset_type = "invoices"

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng
                return mock_q
            if model == AuditDataset:
                # Returns multiple datasets for 'invoices'
                mock_q.filter.return_value.all.return_value = [inv_ds_1, inv_ds_2]
                return mock_q
            mock_q.filter.return_value.first.return_value = None
            mock_q.filter.return_value.all.return_value = []
            return mock_q

        mock_db.query.side_effect = query_side_effect

        res = execute_audit_test(
            db=mock_db,
            organization_id=org_id,
            engagement_id=eng_id,
            rule_code="P2P_DUPLICATE_INVOICE_PAYMENT",
        )

        self.assertEqual(res["status"], "failed")
        self.assertEqual(res["error_code"], "AMBIGUOUS_DATASET_SELECTION")
        self.assertIn("Multiple datasets found", res["error"])

    def test_explicit_selection_resolves_ambiguity(self):
        """Verify that passing selected_dataset_ids resolves ambiguous dataset candidates."""
        mock_db = MagicMock()
        org_id = uuid.uuid4()
        eng_id = uuid.uuid4()
        target_inv_id = uuid.uuid4()

        mock_eng = MagicMock()
        mock_eng.id = eng_id
        mock_eng.organization_id = org_id

        target_ds = MagicMock(spec=AuditDataset)
        target_ds.id = target_inv_id
        target_ds.dataset_name = "North America Invoices Q1"
        target_ds.dataset_type = "invoices"
        target_ds.version_number = 1
        target_ds.row_count = 1

        mock_row = MagicMock(spec=DatasetRow)
        mock_row.id = uuid.uuid4()
        mock_row.row_number = 1
        mock_row.normalized_data = {
            "invoice_number": "INV-NA-001",
            "supplier_name": "Acme Corp",
            "total_amount": 1500.0,
            "invoice_date": "2026-02-15",
        }
        mock_row.raw_data = mock_row.normalized_data

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng
                return mock_q
            if model == AuditDataset:
                mock_q.filter.return_value.first.return_value = target_ds
                return mock_q
            if model == DatasetRow:
                mock_q.filter.return_value.order_by.return_value.all.return_value = [mock_row]
                return mock_q
            mock_q.filter.return_value.first.return_value = None
            mock_q.filter.return_value.all.return_value = []
            return mock_q

        mock_db.query.side_effect = query_side_effect

        res = execute_audit_test(
            db=mock_db,
            organization_id=org_id,
            engagement_id=eng_id,
            rule_code="P2P_DUPLICATE_INVOICE_PAYMENT",
            selected_dataset_ids={"invoices": str(target_inv_id)},
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["population_count"], 1)
        self.assertEqual(res["exception_count"], 0)

    def test_decimal_numeric_precision(self):
        """Verify amount matching with tolerance handles decimal and float inputs accurately."""
        pos = [{"po_number": "PO-DEC-1", "total_amount": Decimal("1000.50"), "currency_code": "USD"}]
        receipts = [{"po_number": "PO-DEC-1", "received_quantity": 10}]
        # Invoice exactly 1% higher ($10.005) -> $1010.50. Under $50 threshold and <= 1.0%
        invoices = [{"invoice_number": "INV-DEC-1", "po_number": "PO-DEC-1", "quantity": 10, "total_amount": Decimal("1010.50"), "currency_code": "USD"}]

        res = run_three_way_match(pos, receipts, invoices, tolerance_pct=1.0, tolerance_amount=50.0)
        self.assertEqual(res["exception_count"], 0)
        self.assertEqual(res["passed_count"], 1)


if __name__ == "__main__":
    unittest.main()


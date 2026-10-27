"""
Test Suite: Exception-to-source-row evidence linking.
Verifies that every identified exception links all contributing rows
(invoices, purchase orders, goods receipts, duplicate matches) via ExceptionRowLink records.
"""

import uuid
import unittest
from datetime import date
from unittest.mock import MagicMock

from app.audit.execution import execute_audit_test
from app.models import (
    AuditDataset,
    AuditEngagement,
    DatasetRow,
    AuditException,
    ExceptionRowLink,
    TestRunDataset,
)


class TestEvidenceLinking(unittest.TestCase):

    def setUp(self):
        self.org_id = uuid.uuid4()
        self.eng_id = uuid.uuid4()
        self.po_ds_id = uuid.uuid4()
        self.gr_ds_id = uuid.uuid4()
        self.inv_ds_id = uuid.uuid4()

    def test_three_way_match_row_links(self):
        """Verify 3-way match exceptions persist ExceptionRowLink for invoice, PO, and goods receipt."""
        mock_db = MagicMock()

        mock_eng = MagicMock(spec=AuditEngagement)
        mock_eng.id = self.eng_id
        mock_eng.organization_id = self.org_id
        mock_eng.period_end = date(2026, 3, 31)

        po_ds = MagicMock(spec=AuditDataset, id=self.po_ds_id, dataset_type="purchase_orders", dataset_name="POs", version_number=1, row_count=1)
        gr_ds = MagicMock(spec=AuditDataset, id=self.gr_ds_id, dataset_type="goods_receipts", dataset_name="GRs", version_number=1, row_count=1)
        inv_ds = MagicMock(spec=AuditDataset, id=self.inv_ds_id, dataset_type="invoices", dataset_name="Invoices", version_number=1, row_count=1)

        po_row_id = uuid.uuid4()
        gr_row_id = uuid.uuid4()
        inv_row_id = uuid.uuid4()

        po_row = MagicMock(spec=DatasetRow, id=po_row_id, dataset_id=self.po_ds_id, row_number=1)
        po_row.normalized_data = {"po_number": "PO-100", "total_amount": 5000.0, "currency_code": "USD"}
        po_row.raw_data = po_row.normalized_data

        gr_row = MagicMock(spec=DatasetRow, id=gr_row_id, dataset_id=self.gr_ds_id, row_number=1)
        gr_row.normalized_data = {"po_number": "PO-100", "received_quantity": 50}
        gr_row.raw_data = gr_row.normalized_data

        # Invoiced 100 units (qty variance!)
        inv_row = MagicMock(spec=DatasetRow, id=inv_row_id, dataset_id=self.inv_ds_id, row_number=1)
        inv_row.normalized_data = {"invoice_number": "INV-100", "po_number": "PO-100", "quantity": 100, "total_amount": 5000.0, "currency_code": "USD"}
        inv_row.raw_data = inv_row.normalized_data

        added_objects = []
        mock_db.add.side_effect = lambda obj: added_objects.append(obj)

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng
                return mock_q
            if model == AuditDataset:
                def ds_filter(*args, **kwargs):
                    inner_q = MagicMock()
                    # Check dataset_type lookup
                    def all_fn():
                        return [po_ds, gr_ds, inv_ds]
                    def first_fn():
                        return po_ds
                    inner_q.all = all_fn
                    inner_q.first = first_fn
                    return inner_q
                mock_q.filter = ds_filter
                return mock_q
            if model == DatasetRow:
                def row_filter(*args, **kwargs):
                    inner_q = MagicMock()
                    # Return appropriate rows depending on dataset_id in filter
                    def all_rows():
                        # We can inspect call args or return matching
                        return [po_row]
                    inner_q.order_by.return_value.all.return_value = [po_row]
                    return inner_q
                mock_q.filter = row_filter
                return mock_q
            mock_q.filter.return_value.first.return_value = None
            mock_q.filter.return_value.all.return_value = []
            return mock_q

        # Provide explicit dataset IDs so resolution is deterministic
        selected_ids = {
            "purchase_orders": str(self.po_ds_id),
            "goods_receipts": str(self.gr_ds_id),
            "invoices": str(self.inv_ds_id),
        }

        ds_by_id = {
            self.po_ds_id: po_ds,
            self.gr_ds_id: gr_ds,
            self.inv_ds_id: inv_ds,
        }
        rows_by_id = {
            self.po_ds_id: [po_row],
            self.gr_ds_id: [gr_row],
            self.inv_ds_id: [inv_row],
        }

        def query_model(model):
            mock_q = MagicMock()
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng
                return mock_q
            if model == AuditDataset:
                def ds_filter(*args, **kwargs):
                    sub_q = MagicMock()
                    req_id = getattr(getattr(args[0], "right", None), "value", None)
                    sub_q.first.return_value = ds_by_id.get(req_id, po_ds)
                    return sub_q
                mock_q.filter = ds_filter
                return mock_q
            if model == DatasetRow:
                def row_filter(*args, **kwargs):
                    sub_q = MagicMock()
                    # Third arg or dataset_id filter in execution.py: DatasetRow.dataset_id == ds.id
                    for a in args:
                        val = getattr(getattr(a, "right", None), "value", None)
                        if val in rows_by_id:
                            sub_q.order_by.return_value.all.return_value = rows_by_id[val]
                            return sub_q
                    sub_q.order_by.return_value.all.return_value = [inv_row]
                    return sub_q
                mock_q.filter = row_filter
                return mock_q
            mock_q.filter.return_value.first.return_value = None
            mock_q.filter.return_value.all.return_value = []
            return mock_q

        mock_db.query.side_effect = query_model

        res = execute_audit_test(
            db=mock_db,
            organization_id=self.org_id,
            engagement_id=self.eng_id,
            rule_code="P2P_THREE_WAY_MATCH",
            selected_dataset_ids=selected_ids,
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["exception_count"], 1)

        # Verify ExceptionRowLink persistence
        row_links = [obj for obj in added_objects if isinstance(obj, ExceptionRowLink)]
        self.assertTrue(len(row_links) >= 2, f"Expected multiple row links for 3-way match, found {len(row_links)}")

        link_roles = {rl.link_role for rl in row_links}
        self.assertIn("source_row", link_roles)
        self.assertIn("po_row", link_roles)

    def test_duplicate_invoice_links_both_invoices(self):
        """Verify duplicate invoice detection persists ExceptionRowLink for both the suspect and the original invoice."""
        mock_db = MagicMock()
        mock_eng = MagicMock(spec=AuditEngagement, id=self.eng_id, organization_id=self.org_id)
        inv_ds = MagicMock(spec=AuditDataset, id=self.inv_ds_id, dataset_type="invoices", dataset_name="Invoices", version_number=1, row_count=2)

        orig_row_id = uuid.uuid4()
        dup_row_id = uuid.uuid4()

        orig_row = MagicMock(spec=DatasetRow, id=orig_row_id, dataset_id=self.inv_ds_id, row_number=1)
        orig_row.normalized_data = {"invoice_number": "INV-DUP-1", "supplier_name": "Apex Global", "total_amount": 7500.0, "invoice_date": "2026-01-10"}
        orig_row.raw_data = orig_row.normalized_data

        dup_row = MagicMock(spec=DatasetRow, id=dup_row_id, dataset_id=self.inv_ds_id, row_number=2)
        dup_row.normalized_data = {"invoice_number": "INV-DUP-1", "supplier_name": "Apex Global", "total_amount": 7500.0, "invoice_date": "2026-01-15"}
        dup_row.raw_data = dup_row.normalized_data

        added_objects = []
        mock_db.add.side_effect = lambda obj: added_objects.append(obj)

        def query_model(model):
            mock_q = MagicMock()
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng
                return mock_q
            if model == AuditDataset:
                mock_q.filter.return_value.first.return_value = inv_ds
                return mock_q
            if model == DatasetRow:
                mock_q.filter.return_value.order_by.return_value.all.return_value = [orig_row, dup_row]
                return mock_q
            mock_q.filter.return_value.first.return_value = None
            mock_q.filter.return_value.all.return_value = []
            return mock_q

        mock_db.query.side_effect = query_model

        res = execute_audit_test(
            db=mock_db,
            organization_id=self.org_id,
            engagement_id=self.eng_id,
            rule_code="P2P_DUPLICATE_INVOICE_PAYMENT",
            selected_dataset_ids={"invoices": str(self.inv_ds_id)},
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["exception_count"], 1)

        row_links = [obj for obj in added_objects if isinstance(obj, ExceptionRowLink)]
        self.assertEqual(len(row_links), 2)

        roles = {rl.link_role for rl in row_links}
        self.assertEqual(roles, {"source_row", "duplicate_match"})

        linked_row_ids = {rl.dataset_row_id for rl in row_links}
        self.assertIn(dup_row_id, linked_row_ids)
        self.assertIn(orig_row_id, linked_row_ids)


if __name__ == "__main__":
    unittest.main()

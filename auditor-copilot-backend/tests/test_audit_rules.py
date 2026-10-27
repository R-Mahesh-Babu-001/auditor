"""
Unit and functional tests for Deterministic Audit Engine:
- P2P Three-Way Match (Qty / Price / Tolerance / Completeness)
- Duplicate Invoice and Payment Detection
- Missing Approval Verification
- Cutoff and Threshold Splitting Risk Signals
- Reproducible Stratified Sampling
- ITGC Segregation of Duties (SoD) Conflicts
- Retained Leaver Access & Inactive Accounts
- Vendor Assurance & AI Governance Reviews
"""

import unittest
from datetime import datetime, date, timedelta, timezone
from app.audit.rules.p2p_rules import (
    run_three_way_match,
    run_duplicate_invoice_payment,
    run_missing_approval,
    run_threshold_splitting,
    run_reproducible_sample,
    run_po_invoice_mismatch,
    run_period_cutoff_check,
    run_bank_change_payment_timing,
    run_supplier_master_duplication,
)
from app.audit.rules.itgc_and_governance import (
    run_itgc_sod_analysis,
    run_vendor_assurance_review,
    run_ai_governance_review,
    SOD_CONFLICT_PAIRS,
)


class TestDeterministicAuditRules(unittest.TestCase):

    def test_three_way_match_perfect(self):
        """Verify that matching PO, Receipt, and Invoice produces no exceptions."""
        pos = [{"po_number": "PO-100", "total_amount": 5000.0, "currency_code": "USD"}]
        receipts = [{"po_number": "PO-100", "received_quantity": 100}]
        invoices = [{"invoice_number": "INV-100", "po_number": "PO-100", "quantity": 100, "total_amount": 5000.0, "currency_code": "USD"}]

        res = run_three_way_match(pos, receipts, invoices)
        self.assertEqual(res["exception_count"], 0)
        self.assertEqual(res["passed_count"], 1)

    def test_three_way_match_qty_mismatch(self):
        """Verify detection when invoiced quantity exceeds received quantity beyond tolerance."""
        pos = [{"po_number": "PO-101", "total_amount": 5000.0, "currency_code": "USD"}]
        receipts = [{"po_number": "PO-101", "received_quantity": 80}]
        # Invoiced 100, received only 80
        invoices = [{"invoice_number": "INV-101", "po_number": "PO-101", "quantity": 100, "total_amount": 5000.0, "currency_code": "USD"}]

        res = run_three_way_match(pos, receipts, invoices)
        self.assertEqual(res["exception_count"], 1)
        exc = res["exceptions"][0]
        self.assertEqual(exc["exception_type"], "quantity_variance")
        self.assertEqual(exc["severity"], "high")

    def test_three_way_match_price_mismatch(self):
        """Verify detection when invoice unit price exceeds PO price beyond tolerance."""
        pos = [{"po_number": "PO-102", "total_amount": 1000.0, "currency_code": "USD"}]
        receipts = [{"po_number": "PO-102", "received_quantity": 10}]
        # Invoiced at 1300 instead of 1000 (30% markup, >$50 diff)
        invoices = [{"invoice_number": "INV-102", "po_number": "PO-102", "quantity": 10, "total_amount": 1300.0, "currency_code": "USD"}]

        res = run_three_way_match(pos, receipts, invoices, tolerance_pct=1.0, tolerance_amount=50.0)
        self.assertEqual(res["exception_count"], 1)
        exc = res["exceptions"][0]
        self.assertEqual(exc["exception_type"], "price_amount_variance")
        self.assertEqual(exc["severity"], "medium")

    def test_duplicate_invoice_detection(self):
        """Verify detection of duplicate invoices for same vendor and invoice reference."""
        invoices = [
            {"supplier_name": "ACME Supplies", "invoice_number": "INV-9999", "total_amount": 5400.00, "invoice_date": "2026-03-01"},
            {"supplier_name": "ACME Supplies", "invoice_number": "INV-9999", "total_amount": 5400.00, "invoice_date": "2026-03-05"},
            {"supplier_name": "Other Vendor", "invoice_number": "INV-9999", "total_amount": 5400.00, "invoice_date": "2026-03-05"},
        ]

        res = run_duplicate_invoice_payment(invoices)
        self.assertEqual(res["exception_count"], 1)
        exc = res["exceptions"][0]
        self.assertEqual(exc["exception_type"], "exact_duplicate_invoice")
        self.assertEqual(exc["severity"], "critical")

    def test_missing_approval_check(self):
        """Verify flagging when high-value invoice lacks required approval record."""
        invoices = [
            {"invoice_number": "INV-LOW", "total_amount": 500.0, "approval_status": "none"},
            {"invoice_number": "INV-HIGH-APPROVED", "total_amount": 25000.0, "approval_status": "approved"},
            {"invoice_number": "INV-HIGH-UNAPPROVED", "total_amount": 35000.0, "approval_status": "pending"},
        ]
        events = [{"invoice_number": "INV-HIGH-APPROVED", "decision": "approved"}]

        res = run_missing_approval(invoices, events, threshold_amount=1000.0)
        self.assertEqual(res["exception_count"], 1)
        exc = res["exceptions"][0]
        self.assertEqual(exc["exception_type"], "missing_approval")
        self.assertEqual(exc["severity"], "high")

    def test_threshold_splitting_check(self):
        """Verify identification of structured split POs designed to evade approval limits."""
        # Split threshold is 10,000. Two invoices for $9,500 and $9,800 to same supplier.
        invoices = [
            {"invoice_number": "INV-SPLIT-1", "supplier_name": "Vendor Splitting", "total_amount": 9500.0, "invoice_date": "2026-03-01"},
            {"invoice_number": "INV-SPLIT-2", "supplier_name": "Vendor Splitting", "total_amount": 9800.0, "invoice_date": "2026-03-02"},
            {"invoice_number": "INV-NORMAL", "supplier_name": "Other Co", "total_amount": 3000.0, "invoice_date": "2026-03-01"},
        ]

        res = run_threshold_splitting(invoices, threshold=10000.0, buffer_pct=10.0)
        self.assertGreaterEqual(res["exception_count"], 1)
        exc = res["exceptions"][0]
        self.assertEqual(exc["exception_type"], "threshold_splitting_signal")

    def test_reproducible_stratified_sampling(self):
        """Verify stratified sampling produces deterministic samples across runs given same seed."""
        population = [
            {"id": f"REC-{i}", "total_amount": float(i * 100), "risk_tier": "high" if i % 3 == 0 else "low"}
            for i in range(100)
        ]

        sample_1 = run_reproducible_sample(population, sample_size=15, seed=42)
        sample_2 = run_reproducible_sample(population, sample_size=15, seed=42)

        self.assertEqual(len(sample_1["selected_records"]), 15)
        self.assertEqual(
            [x["id"] for x in sample_1["selected_records"]],
            [x["id"] for x in sample_2["selected_records"]]
        )

    def test_itgc_sod_analysis(self):
        """Verify ITGC Segregation of Duties conflicts, retained leaver access, and dormant accounts."""
        user_roles = [
            {
                "user_id": "USER-COMPLIANT",
                "email": "compliant@company.com",
                "roles": ["PO_CREATION"],
                "is_active": True,
                "last_login_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "user_id": "USER-CONFLICT",
                "email": "conflict@company.com",
                "roles": ["PO_CREATION", "INVOICE_APPROVAL"],
                "is_active": True,
                "last_login_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "user_id": "USER-LEAVER",
                "email": "terminated@company.com",
                "roles": ["VENDOR_MASTER_MAINTAIN"],
                "is_active": True,
                "last_login_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "user_id": "USER-DORMANT",
                "email": "dormant@company.com",
                "roles": ["PAYMENT_RELEASE"],
                "is_active": True,
                "last_login_at": (datetime.now(timezone.utc) - timedelta(days=120)).isoformat(),
            },
        ]

        leavers = [{"email": "terminated@company.com", "termination_date": "2026-01-15"}]

        res = run_itgc_sod_analysis(user_roles=user_roles, leavers=leavers, inactive_days_threshold=90)
        self.assertGreaterEqual(res["exception_count"], 3)

        types = {e["exception_type"] for e in res["exceptions"]}
        self.assertIn("segregation_of_duties_conflict", types)
        self.assertIn("retained_leaver_access", types)
        self.assertIn("dormant_active_account", types)

    def test_vendor_assurance_review(self):
        """Verify flagging when high-risk vendor lacks valid SOC reports."""
        vendors = [
            {"name": "Vendor A", "risk_tier": "low", "has_soc_report": False},
            {"name": "Cloud Host Alpha", "risk_tier": "critical", "has_soc_report": True, "soc_report_expiry": "2027-01-01"},
            {"name": "Payroll Outsourcer Beta", "risk_tier": "high", "has_soc_report": False},
        ]

        res = run_vendor_assurance_review(vendors)
        self.assertEqual(res["exception_count"], 1)
        self.assertEqual(res["exceptions"][0]["exception_type"], "missing_vendor_assurance")

    def test_ai_governance_review(self):
        """Verify flagging of undocumented shadow AI tools in corporate inventory."""
        ai_systems = [
            {
                "name": "Audit AI Helper",
                "system_owner": "Audit Lead",
                "business_purpose": "Audit workpaper drafting",
                "model_provider": "Google Gemini",
                "risk_tier": "medium",
                "approval_records": "Approved by CISO 2026-01-10",
                "monitoring_plan": "Monthly prompt and hallucination review",
            },
            {
                "name": "Shadow Scraper",
                "system_owner": None,
                "business_purpose": "Web parsing",
                "model_provider": "Unknown",
                "risk_tier": None,
            },
        ]

        res = run_ai_governance_review(ai_systems)
        self.assertGreaterEqual(res["exception_count"], 2)
        types = {e["exception_type"] for e in res["exceptions"]}
        self.assertIn("ai_governance_gap", types)

    def test_po_invoice_mismatch(self):
        """Verify flagging of missing PO, invalid PO references, and supplier mismatches."""
        pos = [{"po_number": "PO-VALID", "supplier_name": "Acme Corp", "total_amount": 5000.0}]
        invoices = [
            {"invoice_number": "INV-NO-PO", "po_number": "", "total_amount": 1500.0, "supplier_name": "Acme Corp"},
            {"invoice_number": "INV-BAD-PO", "po_number": "PO-NONEXISTENT", "total_amount": 1500.0, "supplier_name": "Acme Corp"},
            {"invoice_number": "INV-SUPP-MISMATCH", "po_number": "PO-VALID", "total_amount": 2000.0, "supplier_name": "Shady Vendor"},
            {"invoice_number": "INV-EXEMPT", "po_number": "", "total_amount": 50.0, "supplier_name": "Acme Corp"}, # Under exemption threshold
        ]

        res = run_po_invoice_mismatch(invoices, pos, exemption_threshold=250.0)
        self.assertEqual(res["exception_count"], 3)
        types = {e["exception_type"] for e in res["exceptions"]}
        self.assertIn("missing_purchase_order", types)
        self.assertIn("invalid_po_reference", types)
        self.assertIn("conflicting_supplier_linkage", types)

    def test_period_cutoff(self):
        """Verify period cutoff check identifies receipts in period with invoices billed post-period."""
        period_end = date(2026, 3, 31)
        receipts = [{"po_number": "PO-CUTOFF", "receipt_date": "2026-03-28"}] # Received in Q1
        invoices = [
            {"invoice_number": "INV-NORMAL-CUTOFF", "po_number": "PO-CUTOFF", "invoice_date": "2026-03-30"},
            {"invoice_number": "INV-UNRECORDED-LIAB", "po_number": "PO-CUTOFF", "invoice_date": "2026-04-15"}, # 15 days into Q2
        ]

        res = run_period_cutoff_check(receipts, invoices, period_end_date=period_end, window_days=15)
        self.assertEqual(res["exception_count"], 1)
        self.assertEqual(res["exceptions"][0]["exception_type"], "period_cutoff_unrecorded_liability")

    def test_bank_change_payment_timing(self):
        """Verify payments released within proximity window of vendor bank account change are flagged."""
        bank_events = [{"supplier_name": "Vendor A", "change_date": "2026-03-01"}]
        payments = [
            {"payment_reference": "PMT-SUSPECT", "supplier_name": "Vendor A", "amount": 85000.0, "payment_date": "2026-03-05"}, # 4 days after change
            {"payment_reference": "PMT-NORMAL", "supplier_name": "Vendor A", "amount": 5000.0, "payment_date": "2026-03-30"}, # 29 days after change
        ]

        res = run_bank_change_payment_timing(payments, bank_events, proximity_days=14)
        self.assertEqual(res["exception_count"], 1)
        self.assertEqual(res["exceptions"][0]["exception_type"], "high_risk_payment_post_bank_change")

    def test_supplier_master_duplication(self):
        """Verify identification of duplicate suppliers by tax ID, bank account, and normalized name."""
        suppliers = [
            {"id": "S1", "supplier_name": "Global Logistics Inc", "tax_id": "TAX-12345", "bank_account_number": "IBAN-987654321"},
            {"id": "S2", "supplier_name": "Logistics Global Sub", "tax_id": "TAX-12345", "bank_account_number": "IBAN-OTHER"}, # Duplicate Tax ID
            {"id": "S3", "supplier_name": "Independent Carrier", "tax_id": "TAX-99999", "bank_account_number": "IBAN-987654321"}, # Duplicate Bank
            {"id": "S4", "supplier_name": "Global  Logistics, Inc.", "tax_id": "TAX-77777", "bank_account_number": "IBAN-111111111"}, # Duplicate Name
            {"id": "S5", "supplier_name": "Clean Unique Supplier", "tax_id": "TAX-88888", "bank_account_number": "IBAN-222222222"},
        ]

        res = run_supplier_master_duplication(suppliers)
        self.assertEqual(res["exception_count"], 3)
        types = {e["exception_type"] for e in res["exceptions"]}
        self.assertIn("duplicate_supplier_tax_id", types)
        self.assertIn("duplicate_supplier_bank_account", types)
        self.assertIn("duplicate_supplier_name", types)


if __name__ == "__main__":
    unittest.main()

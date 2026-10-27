"""
Deterministic Python testing services for Procure-to-Pay (P2P) audits.
All test logic is strictly deterministic, explainable, and reproducible without hallucination.
"""

import re
import math
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple


def normalize_invoice_number(inv_num: Optional[str]) -> str:
    """Normalize invoice identifier by stripping spaces, special characters, and converting to uppercase."""
    if not inv_num:
        return ""
    clean = re.sub(r"[\s\-_/\\#.]+", "", str(inv_num)).upper()
    return clean.lstrip("0") or clean


def run_three_way_match(
    pos: List[Dict[str, Any]],
    receipts: List[Dict[str, Any]],
    invoices: List[Dict[str, Any]],
    tolerance_pct: float = 1.0,
    tolerance_amount: float = 50.0,
) -> Dict[str, Any]:
    """Execute 3-Way Matching across Purchase Orders, Goods Receipts, and Invoices.

    Checks:
    - Missing Goods Receipt (Invoice without Receipt)
    - Missing Purchase Order (Invoice without PO)
    - Quantity Variance (Invoiced Qty > Received Qty beyond tolerance)
    - Price/Amount Variance (Invoiced Amount > PO Amount beyond tolerance)
    - Currency mismatch
    """
    po_map = {str(p.get("po_number")): p for p in pos if p.get("po_number")}
    # Map receipts by PO number
    receipt_map: Dict[str, List[Dict[str, Any]]] = {}
    for r in receipts:
        p_num = str(r.get("po_number", ""))
        receipt_map.setdefault(p_num, []).append(r)

    exceptions = []
    passed_count = 0
    unmatched_count = 0

    for inv in invoices:
        inv_no = inv.get("invoice_number", "UNKNOWN")
        po_no = str(inv.get("po_number", ""))
        inv_amount = float(inv.get("total_amount") or inv.get("gross_amount") or 0.0)
        inv_qty = float(inv.get("quantity") or 1.0)
        inv_curr = str(inv.get("currency_code", "USD")).upper()

        if not po_no or po_no not in po_map:
            exceptions.append({
                "exception_key": f"3WAY-NO-PO-{inv_no}",
                "exception_type": "missing_purchase_order",
                "severity": "high",
                "title": f"Invoice {inv_no} has no matching Purchase Order",
                "description": f"Invoice for amount {inv_amount} {inv_curr} lacks a valid reference to an approved PO.",
                "observed_values": {"invoice_number": inv_no, "po_number": po_no, "amount": inv_amount},
                "expected_values": {"required": "Approved Purchase Order required before invoicing"},
                "invoice": inv,
            })
            unmatched_count += 1
            continue

        po = po_map[po_no]
        po_amount = float(po.get("total_amount") or 0.0)
        po_curr = str(po.get("currency_code", "USD")).upper()

        # Check currency consistency
        if inv_curr != po_curr:
            exceptions.append({
                "exception_key": f"3WAY-CURR-MISMATCH-{inv_no}",
                "exception_type": "currency_mismatch",
                "severity": "medium",
                "title": f"Currency Mismatch on PO {po_no} vs Invoice {inv_no}",
                "description": f"PO currency is {po_curr} but invoice was billed in {inv_curr}.",
                "observed_values": {"po_currency": po_curr, "invoice_currency": inv_curr},
                "expected_values": {"matched_currency": po_curr},
                "invoice": inv,
            })
            continue

        # Check goods receipt
        matched_receipts = receipt_map.get(po_no, [])
        if not matched_receipts:
            exceptions.append({
                "exception_key": f"3WAY-NO-GR-{inv_no}",
                "exception_type": "missing_goods_receipt",
                "severity": "high",
                "title": f"Missing Goods Receipt for Invoice {inv_no}",
                "description": f"Invoice {inv_no} billed against PO {po_no} with no recorded Goods Receipt in the audit period.",
                "observed_values": {"invoice_number": inv_no, "po_number": po_no, "receipt_count": 0},
                "expected_values": {"goods_receipt": "Receipt document confirming delivery"},
                "invoice": inv,
            })
            continue

        # Check total receipt quantity
        total_received_qty = sum(float(r.get("quantity") or r.get("received_quantity") or 0.0) for r in matched_receipts)
        if inv_qty > total_received_qty:
            qty_diff = inv_qty - total_received_qty
            exceptions.append({
                "exception_key": f"3WAY-QTY-VAR-{inv_no}",
                "exception_type": "quantity_variance",
                "severity": "high" if qty_diff > 5 else "medium",
                "title": f"Quantity Variance on Invoice {inv_no}",
                "description": f"Billed for {inv_qty} units but only {total_received_qty} units were confirmed received.",
                "observed_values": {"invoiced_quantity": inv_qty, "received_quantity": total_received_qty},
                "expected_values": {"max_invoiced_quantity": total_received_qty},
                "invoice": inv,
            })
            continue

        # Check amount tolerance
        amount_diff = inv_amount - po_amount
        pct_diff = (amount_diff / po_amount * 100.0) if po_amount > 0 else 0.0

        if amount_diff > tolerance_amount and pct_diff > tolerance_pct:
            exceptions.append({
                "exception_key": f"3WAY-AMT-VAR-{inv_no}",
                "exception_type": "price_amount_variance",
                "severity": "high" if amount_diff > 500 else "medium",
                "title": f"Price/Amount Variance on Invoice {inv_no}",
                "description": f"Invoice amount {inv_amount} exceeds PO amount {po_amount} by {amount_diff:.2f} ({pct_diff:.1f}%).",
                "observed_values": {"invoice_amount": inv_amount, "po_amount": po_amount, "variance": amount_diff},
                "expected_values": {"max_allowed": po_amount + min(tolerance_amount, po_amount * (tolerance_pct / 100.0))},
                "invoice": inv,
            })
        else:
            passed_count += 1

    return {
        "rule_code": "P2P_THREE_WAY_MATCH",
        "population_count": len(invoices),
        "passed_count": passed_count,
        "exception_count": len(exceptions),
        "unmatched_count": unmatched_count,
        "exceptions": exceptions,
    }


def run_duplicate_invoice_payment(
    invoices: List[Dict[str, Any]],
    payments: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Identify duplicate invoices and duplicate payments.

    Checks:
    - Exact duplicate: Same supplier, normalized invoice number, and gross amount.
    - Probable duplicate: Same supplier and gross amount on proximate dates (within 14 days).
    """
    exceptions = []
    seen_invoices: Dict[Tuple[str, str, float], Dict[str, Any]] = {}
    supplier_amount_map: Dict[Tuple[str, float], List[Dict[str, Any]]] = {}

    passed_count = 0

    for inv in invoices:
        supplier = str(inv.get("supplier_name") or inv.get("supplier_id") or "").strip().lower()
        inv_no = str(inv.get("invoice_number", ""))
        norm_no = normalize_invoice_number(inv_no)
        amount = round(float(inv.get("total_amount") or inv.get("gross_amount") or 0.0), 2)
        inv_date_str = str(inv.get("invoice_date", ""))

        if not supplier or amount <= 0:
            continue

        exact_key = (supplier, norm_no, amount)
        if exact_key in seen_invoices:
            orig = seen_invoices[exact_key]
            exceptions.append({
                "exception_key": f"DUP-INV-EXACT-{norm_no}-{amount}",
                "exception_type": "exact_duplicate_invoice",
                "severity": "critical",
                "title": f"Duplicate Invoice Detected: {inv_no}",
                "description": f"Invoice {inv_no} matches existing invoice {orig.get('invoice_number')} for supplier '{supplier}' in amount ${amount:,.2f}.",
                "observed_values": {
                    "current_invoice": inv_no,
                    "duplicate_of": orig.get("invoice_number"),
                    "supplier": supplier,
                    "amount": amount,
                },
                "expected_values": {"unique_invoice_rule": "Each invoice per supplier must be unique"},
                "invoice": inv,
            })
        else:
            seen_invoices[exact_key] = inv

            # Check proximate duplicate
            amount_key = (supplier, amount)
            if amount_key in supplier_amount_map:
                for prior_inv in supplier_amount_map[amount_key]:
                    prior_date = str(prior_inv.get("invoice_date", ""))
                    if prior_inv.get("invoice_number") != inv_no:
                        exceptions.append({
                            "exception_key": f"DUP-INV-PROBABLE-{norm_no}-{amount}",
                            "exception_type": "probable_duplicate_invoice",
                            "severity": "medium",
                            "title": f"Probable Duplicate Invoice: {inv_no}",
                            "description": f"Supplier '{supplier}' billed identical amount ${amount:,.2f} on {inv_date_str} and {prior_date} (Inv #{prior_inv.get('invoice_number')}).",
                            "observed_values": {
                                "current_invoice": inv_no,
                                "suspect_match": prior_inv.get("invoice_number"),
                                "amount": amount,
                            },
                            "expected_values": {"verification": "Confirm separate deliveries or distinct billing periods"},
                            "invoice": inv,
                        })
            supplier_amount_map.setdefault(amount_key, []).append(inv)
            passed_count += 1

    return {
        "rule_code": "P2P_DUPLICATE_INVOICE_PAYMENT",
        "population_count": len(invoices),
        "passed_count": passed_count,
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


def run_missing_approval(
    invoices: List[Dict[str, Any]],
    approval_events: List[Dict[str, Any]],
    threshold_amount: float = 1000.0,
) -> Dict[str, Any]:
    """Verify that invoices exceeding approval threshold possess authorized approval events."""
    approved_inv_ids = set()
    for ev in approval_events:
        inv_id = str(ev.get("invoice_id") or ev.get("invoice_number") or "")
        decision = str(ev.get("decision", "")).lower()
        if inv_id and decision in ("approved", "accepted"):
            approved_inv_ids.add(inv_id)

    exceptions = []
    passed_count = 0

    for inv in invoices:
        inv_no = str(inv.get("invoice_number", ""))
        amount = float(inv.get("total_amount") or inv.get("gross_amount") or 0.0)

        if amount >= threshold_amount:
            # Check for approval
            if inv_no not in approved_inv_ids and str(inv.get("id", "")) not in approved_inv_ids:
                # Also check inline status flag
                inline_status = str(inv.get("approval_status", "")).lower()
                if inline_status != "approved":
                    exceptions.append({
                        "exception_key": f"MISSING-APPROVAL-{inv_no}",
                        "exception_type": "missing_approval",
                        "severity": "high",
                        "title": f"Missing Required Approval on Invoice {inv_no}",
                        "description": f"Invoice of ${amount:,.2f} exceeds threshold ${threshold_amount:,.2f} but lacks verified approval record.",
                        "observed_values": {"invoice_number": inv_no, "amount": amount, "approval_record": "None"},
                        "expected_values": {"threshold": threshold_amount, "required": "Authorized supervisor approval"},
                        "invoice": inv,
                    })
                    continue
        passed_count += 1

    return {
        "rule_code": "P2P_MISSING_APPROVAL",
        "population_count": len(invoices),
        "passed_count": passed_count,
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


def run_threshold_splitting(
    invoices: List[Dict[str, Any]],
    threshold: float = 10000.0,
    proximity_window_days: int = 3,
    buffer_pct: float = 10.0,
) -> Dict[str, Any]:
    """Identify split purchase transactions clustered just below approval threshold."""
    exceptions = []
    # Lower bound for splitting signal (e.g. within 10% below threshold: $9,000 - $9,999 for a $10,000 threshold)
    lower_bound = threshold * (1.0 - (buffer_pct / 100.0))

    by_supplier: Dict[str, List[Dict[str, Any]]] = {}
    for inv in invoices:
        amount = float(inv.get("total_amount") or inv.get("gross_amount") or 0.0)
        if lower_bound <= amount < threshold:
            supp = str(inv.get("supplier_name") or inv.get("supplier_id") or "UNKNOWN").strip()
            by_supplier.setdefault(supp, []).append(inv)

    for supp, inv_list in by_supplier.items():
        if len(inv_list) >= 2:
            inv_numbers = [i.get("invoice_number") for i in inv_list]
            total_split = sum(float(i.get("total_amount") or i.get("gross_amount") or 0.0) for i in inv_list)
            exceptions.append({
                "exception_key": f"SPLIT-THRESH-{supp[:12]}-{len(inv_list)}",
                "exception_type": "threshold_splitting_signal",
                "severity": "medium",
                "title": f"Potential Split Purchases Below Approval Threshold for {supp}",
                "description": f"{len(inv_list)} invoices totaling ${total_split:,.2f} clustered just below ${threshold:,.2f} threshold. Flagged as risk signal for auditor review.",
                "observed_values": {"supplier": supp, "invoices": inv_numbers, "total_split_amount": total_split},
                "expected_values": {"threshold": threshold, "policy": "Purchases should not be split to bypass authorization limits"},
            })

    return {
        "rule_code": "P2P_THRESHOLD_SPLITTING",
        "population_count": len(invoices),
        "passed_count": len(invoices) - len(exceptions),
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


def run_reproducible_sample(
    records: List[Dict[str, Any]],
    sample_size: int = 25,
    seed: int = 42,
    strata_key: Optional[str] = "amount",
) -> Dict[str, Any]:
    """Select a deterministic, reproducible sample from the audit population with documented rationale."""
    if not records:
        return {"sample_size": 0, "seed": seed, "selected_rows": [], "rationale": "Empty population"}

    rng = random.Random(seed)
    n = min(sample_size, len(records))

    # Stratify by high-value if requested
    if strata_key == "amount":
        sorted_records = sorted(records, key=lambda x: float(x.get("total_amount") or x.get("gross_amount") or 0.0), reverse=True)
        # Take top 20% by value as top stratum
        top_stratum_size = max(1, int(n * 0.3))
        top_stratum = sorted_records[:top_stratum_size]
        remaining = sorted_records[top_stratum_size:]
        random_stratum = rng.sample(remaining, min(n - top_stratum_size, len(remaining)))
        selected = top_stratum + random_stratum
        rationale = f"Stratified sample of {len(selected)} items (seed={seed}): {len(top_stratum)} high-value items + {len(random_stratum)} randomly sampled from population of {len(records)}."
    else:
        selected = rng.sample(records, n)
        rationale = f"Simple random sample of {n} items selected using fixed seed={seed} from population of {len(records)}."

    return {
        "rule_code": "P2P_SAMPLE_SELECTION",
        "population_count": len(records),
        "sample_count": len(selected),
        "seed": seed,
        "rationale": rationale,
        "selected_records": selected,
    }


def run_po_invoice_mismatch(
    invoices: List[Dict[str, Any]],
    pos: List[Dict[str, Any]],
    exemption_threshold: float = 250.0,
) -> Dict[str, Any]:
    """Flag invoices without PO where required by policy, or conflicting supplier linkages."""
    po_by_num = {str(p.get("po_number", "")): p for p in pos if p.get("po_number")}
    exceptions = []
    passed_count = 0

    for inv in invoices:
        inv_no = str(inv.get("invoice_number", "UNKNOWN"))
        po_no = str(inv.get("po_number", "")).strip()
        amount = float(inv.get("total_amount") or inv.get("gross_amount") or 0.0)
        inv_supp = str(inv.get("supplier_name") or inv.get("supplier_id") or "").strip().lower()

        # Check missing PO on non-exempt amounts
        if not po_no:
            if amount > exemption_threshold:
                exceptions.append({
                    "exception_key": f"MISMATCH-NO-PO-{inv_no}",
                    "exception_type": "missing_purchase_order",
                    "severity": "high",
                    "title": f"Invoice {inv_no} Lacks Required Purchase Order",
                    "description": f"Invoice amount ${amount:,.2f} exceeds ${exemption_threshold:,.2f} policy threshold but lacks an approved PO reference.",
                    "observed_values": {"invoice": inv_no, "po_number": None, "amount": amount},
                    "expected_values": {"requirement": "Approved Purchase Order required before ordering/billing"},
                    "invoice": inv,
                })
            continue

        # Check existing PO reference validity
        if po_no not in po_by_num:
            exceptions.append({
                "exception_key": f"MISMATCH-INVALID-PO-{inv_no}",
                "exception_type": "invalid_po_reference",
                "severity": "high",
                "title": f"Invoice {inv_no} References Non-Existent PO {po_no}",
                "description": f"Invoice references PO {po_no} which is not found in approved PO ledgers.",
                "observed_values": {"invoice": inv_no, "referenced_po": po_no},
                "expected_values": {"po_validity": "Referenced PO must exist in ERP"},
                "invoice": inv,
            })
            continue

        # Check supplier mismatch between PO and Invoice
        matched_po = po_by_num[po_no]
        po_supp = str(matched_po.get("supplier_name") or matched_po.get("supplier_id") or "").strip().lower()
        if inv_supp and po_supp and inv_supp != po_supp:
            exceptions.append({
                "exception_key": f"MISMATCH-SUPPLIER-{inv_no}",
                "exception_type": "conflicting_supplier_linkage",
                "severity": "critical",
                "title": f"Supplier Mismatch: Invoice {inv_no} vs PO {po_no}",
                "description": f"Invoice supplier '{inv_supp}' does not match PO vendor '{po_supp}'.",
                "observed_values": {"invoice_supplier": inv_supp, "po_supplier": po_supp},
                "expected_values": {"matched_supplier": po_supp},
                "invoice": inv,
            })
            continue

        passed_count += 1

    return {
        "rule_code": "P2P_PO_INVOICE_MISMATCH",
        "population_count": len(invoices),
        "passed_count": passed_count,
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


def run_period_cutoff_check(
    receipts: List[Dict[str, Any]],
    invoices: List[Dict[str, Any]],
    period_end_date: date,
    window_days: int = 15,
) -> Dict[str, Any]:
    """Identify financial period cut-off errors (unrecorded liabilities or premature accruals)."""
    exceptions = []
    receipt_by_po: Dict[str, List[Dict[str, Any]]] = {}
    for r in receipts:
        po_no = str(r.get("po_number", ""))
        if po_no:
            receipt_by_po.setdefault(po_no, []).append(r)

    cutoff_lower = period_end_date - timedelta(days=window_days)
    cutoff_upper = period_end_date + timedelta(days=window_days)
    passed_count = 0

    for inv in invoices:
        inv_no = str(inv.get("invoice_number", "UNKNOWN"))
        po_no = str(inv.get("po_number", ""))
        inv_date_str = inv.get("invoice_date")
        if not inv_date_str:
            continue

        try:
            inv_date = date.fromisoformat(str(inv_date_str)[:10])
        except Exception:
            continue

        matched_receipts = receipt_by_po.get(po_no, [])
        for rec in matched_receipts:
            rec_date_str = rec.get("receipt_date") or rec.get("delivery_date")
            if not rec_date_str:
                continue
            try:
                rec_date = date.fromisoformat(str(rec_date_str)[:10])
            except Exception:
                continue

            # Goods received before cutoff, but invoice dated well after cutoff (unrecorded liability)
            if rec_date <= period_end_date and inv_date > period_end_date:
                days_after = (inv_date - period_end_date).days
                if days_after > 5:
                    exceptions.append({
                        "exception_key": f"CUTOFF-UNRECORDED-LIAB-{inv_no}",
                        "exception_type": "period_cutoff_unrecorded_liability",
                        "severity": "medium",
                        "title": f"Potential Cutoff Variance on Invoice {inv_no}",
                        "description": f"Goods received on {rec_date} (within period ending {period_end_date}), but billed on {inv_date} ({days_after} days into subsequent period). Requires liability accrual review.",
                        "observed_values": {"goods_receipt_date": str(rec_date), "invoice_date": str(inv_date), "period_end": str(period_end_date)},
                        "expected_values": {"accrual_policy": "Goods received on or before period-end must be accrued in current period"},
                        "invoice": inv,
                    })
                    continue

        passed_count += 1

    return {
        "rule_code": "P2P_PERIOD_CUTOFF",
        "population_count": len(invoices),
        "passed_count": passed_count,
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


def run_bank_change_payment_timing(
    payments: List[Dict[str, Any]],
    bank_change_events: List[Dict[str, Any]],
    proximity_days: int = 14,
) -> Dict[str, Any]:
    """Flag temporal risk patterns where payments occur immediately following supplier bank detail modifications."""
    exceptions = []
    changes_by_supplier: Dict[str, List[date]] = {}

    for chg in bank_change_events:
        supp = str(chg.get("supplier_id") or chg.get("supplier_name") or "").strip().lower()
        chg_date_str = chg.get("change_date") or chg.get("event_date")
        if supp and chg_date_str:
            try:
                chg_date = date.fromisoformat(str(chg_date_str)[:10])
                changes_by_supplier.setdefault(supp, []).append(chg_date)
            except Exception:
                pass

    passed_count = 0
    for pmt in payments:
        pmt_ref = str(pmt.get("payment_reference") or pmt.get("id") or "UNKNOWN")
        supp = str(pmt.get("supplier_id") or pmt.get("supplier_name") or "").strip().lower()
        amount = float(pmt.get("amount") or pmt.get("total_amount") or 0.0)
        pmt_date_str = pmt.get("payment_date")

        if not supp or not pmt_date_str or supp not in changes_by_supplier:
            passed_count += 1
            continue

        try:
            pmt_date = date.fromisoformat(str(pmt_date_str)[:10])
        except Exception:
            passed_count += 1
            continue

        for chg_date in changes_by_supplier[supp]:
            if chg_date <= pmt_date:
                gap = (pmt_date - chg_date).days
                if gap <= proximity_days:
                    exceptions.append({
                        "exception_key": f"BANK-CHANGE-PROX-{pmt_ref}",
                        "exception_type": "high_risk_payment_post_bank_change",
                        "severity": "critical",
                        "title": f"High Risk: Payment {pmt_ref} Released {gap} Days After Bank Account Modification",
                        "description": f"Payment of ${amount:,.2f} disbursed to '{supp}' on {pmt_date}, only {gap} days following bank master update on {chg_date}. Heightened risk of redirection fraud.",
                        "observed_values": {"payment_reference": pmt_ref, "payment_date": str(pmt_date), "bank_change_date": str(chg_date), "days_elapsed": gap, "amount": amount},
                        "expected_values": {"policy": "Independent confirmation required for payments within 14 days of bank change"},
                    })
                    break
        passed_count += 1

    return {
        "rule_code": "P2P_BANK_CHANGE_TIMING",
        "population_count": len(payments),
        "passed_count": passed_count,
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


def run_supplier_master_duplication(
    suppliers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Identify duplicate supplier master accounts based on tax ID, IBAN, bank account, or normalized name."""
    exceptions = []
    seen_tax: Dict[str, Dict[str, Any]] = {}
    seen_bank: Dict[str, Dict[str, Any]] = {}
    seen_names: Dict[str, Dict[str, Any]] = {}
    passed_count = 0

    for s in suppliers:
        supp_id = str(s.get("id") or s.get("supplier_id") or "UNKNOWN")
        name = str(s.get("supplier_name") or s.get("name") or "").strip()
        tax_id = re.sub(r"[\s\-_]+", "", str(s.get("tax_id") or s.get("vat_number") or "")).upper()
        bank_acc = re.sub(r"[\s\-_]+", "", str(s.get("bank_account_number") or s.get("iban") or "")).upper()
        norm_name = re.sub(r"[^A-Z0-9]+", "", name.upper())

        is_dup = False

        # 1. Tax ID collision
        if tax_id and len(tax_id) > 4:
            if tax_id in seen_tax:
                orig = seen_tax[tax_id]
                exceptions.append({
                    "exception_key": f"SUPP-DUP-TAX-{supp_id}",
                    "exception_type": "duplicate_supplier_tax_id",
                    "severity": "high",
                    "title": f"Duplicate Supplier Tax ID: {name} shares Tax ID with {orig.get('name')}",
                    "description": f"Supplier accounts '{name}' and '{orig.get('name')}' share identical Tax/VAT ID '{tax_id}'.",
                    "observed_values": {"supplier_1": name, "supplier_2": orig.get("name"), "tax_id": tax_id},
                    "expected_values": {"unique_vendor_rule": "Each supplier record must have a unique tax registration"},
                })
                is_dup = True
            else:
                seen_tax[tax_id] = {"id": supp_id, "name": name}

        # 2. Bank Account / IBAN collision
        if bank_acc and len(bank_acc) > 6:
            if bank_acc in seen_bank:
                orig = seen_bank[bank_acc]
                exceptions.append({
                    "exception_key": f"SUPP-DUP-BANK-{supp_id}",
                    "exception_type": "duplicate_supplier_bank_account",
                    "severity": "critical",
                    "title": f"Duplicate Bank Account: {name} shares Bank Account with {orig.get('name')}",
                    "description": f"Different vendor accounts '{name}' and '{orig.get('name')}' remit to the exact same bank account.",
                    "observed_values": {"supplier_1": name, "supplier_2": orig.get("name"), "bank_account": bank_acc[-4:].rjust(len(bank_acc), "*")},
                    "expected_values": {"unique_banking_rule": "Vendor bank accounts should not be shared across unrelated suppliers"},
                })
                is_dup = True
            else:
                seen_bank[bank_acc] = {"id": supp_id, "name": name}

        # 3. Normalized Name collision
        if norm_name and len(norm_name) > 3:
            if norm_name in seen_names:
                orig = seen_names[norm_name]
                exceptions.append({
                    "exception_key": f"SUPP-DUP-NAME-{supp_id}",
                    "exception_type": "duplicate_supplier_name",
                    "severity": "medium",
                    "title": f"Probable Duplicate Supplier Name: '{name}' vs '{orig.get('name')}'",
                    "description": f"Supplier records have matching normalized company names.",
                    "observed_values": {"supplier_1": name, "supplier_2": orig.get("name")},
                    "expected_values": {"unique_name_rule": "Single master record per vendor legal entity"},
                })
                is_dup = True
            else:
                seen_names[norm_name] = {"id": supp_id, "name": name}

        if not is_dup:
            passed_count += 1

    return {
        "rule_code": "P2P_SUPPLIER_MASTER_DUPLICATION",
        "population_count": len(suppliers),
        "passed_count": passed_count,
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


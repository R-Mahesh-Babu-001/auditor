"""
Dataset profiling, canonical field mapping, and truthful row normalization for audit datasets.
Enforces canonical dataset types, real row validation, and explainable error tracking.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, date

CANONICAL_DATASET_TYPES = [
    "purchase_orders",
    "goods_receipts",
    "invoices",
    "payments",
    "approvals",
    "suppliers",
    "user_access",
    "employee_directory",
    "ai_system_inventory",
]

# Required and critical fields by canonical dataset type
TYPE_REQUIRED_FIELDS: Dict[str, List[str]] = {
    "purchase_orders": ["po_number", "total_amount"],
    "goods_receipts": ["receipt_number", "po_number"],
    "invoices": ["invoice_number", "total_amount"],
    "payments": ["payment_reference", "total_amount"],
    "approvals": ["invoice_number", "approval_status"],
    "suppliers": ["supplier_name"],
    "user_access": ["email"],
    "employee_directory": ["email"],
    "ai_system_inventory": ["system_name"],
}

CANONICAL_P2P_FIELDS = {
    "supplier_name": ["supplier", "vendor", "vendor_name", "supplier_name", "payee", "company_name", "name"],
    "supplier_code": ["supplier_id", "vendor_id", "supplier_code", "vendor_num"],
    "tax_id": ["tax_id", "vat_number", "ein", "vat", "tax_number"],
    "bank_account_number": ["bank_account", "bank_account_number", "iban", "account_number", "bank_acc"],
    "po_number": ["po_number", "po_no", "purchase_order", "po", "order_id", "order_number"],
    "order_date": ["order_date", "po_date"],
    "invoice_number": ["invoice_number", "invoice_no", "inv_num", "inv_no", "bill_no", "invoice_id"],
    "invoice_date": ["invoice_date", "inv_date", "bill_date", "date"],
    "total_amount": ["total_amount", "amount", "invoice_amount", "gross_amount", "total", "net_amount", "payment_amount"],
    "currency_code": ["currency", "curr", "currency_code"],
    "quantity": ["quantity", "qty", "invoiced_qty", "ordered_qty"],
    "unit_price": ["unit_price", "rate", "price"],
    "receipt_number": ["receipt_number", "gr_number", "receipt_no", "goods_receipt", "gr_no", "delivery_note"],
    "receipt_date": ["receipt_date", "gr_date", "received_date", "delivery_date"],
    "received_quantity": ["received_qty", "qty_received", "received_quantity"],
    "payment_reference": ["payment_ref", "check_number", "payment_reference", "payment_id", "trans_id", "ref_no"],
    "payment_date": ["payment_date", "paid_date", "check_date", "disbursement_date"],
    "approval_status": ["approval_status", "status", "approved", "approval_state", "decision"],
    "approver_name": ["approver", "approver_name", "approved_by", "manager"],
    "approval_date": ["approval_date", "approved_at"],
    "email": ["email", "user_email", "mail", "user_id"],
    "roles": ["roles", "role", "permissions", "user_role", "entitlements"],
    "is_active": ["is_active", "active", "account_status", "enabled"],
    "last_login_at": ["last_login_at", "last_login", "last_active_date"],
    "system_name": ["system_name", "model_name", "ai_system", "application_name"],
}


def suggest_canonical_mappings(columns: List[str]) -> List[Dict[str, Any]]:
    """Propose canonical field mappings based on header name similarity and keywords."""
    mappings = []
    for col in columns:
        clean = col.lower().strip().replace(" ", "_")
        best_match = None
        confidence = 0.0

        for canon, aliases in CANONICAL_P2P_FIELDS.items():
            if clean == canon:
                best_match = canon
                confidence = 1.0
                break
            for alias in aliases:
                if alias == clean or alias in clean:
                    best_match = canon
                    confidence = 0.85
                    break
            if best_match:
                break

        mappings.append({
            "source_column": col,
            "canonical_field": best_match,
            "confidence": confidence,
            "mapping_status": "confirmed" if confidence >= 0.8 else ("proposed" if best_match else "unmapped"),
        })
    return mappings


def profile_dataset_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Profile tabular data rows: null counts, types, uniqueness, and preview sample values."""
    if not rows:
        return {"row_count": 0, "column_count": 0, "columns": {}}

    columns = list(rows[0].keys())
    col_profiles: Dict[str, Any] = {}

    for col in columns:
        values = [r.get(col) for r in rows]
        null_count = sum(1 for v in values if v is None or str(v).strip() in ("", "nan", "null", "none"))
        non_nulls = [v for v in values if v is not None and str(v).strip() not in ("", "nan", "null", "none")]
        unique_count = len(set(str(v) for v in non_nulls))

        # Infer data type
        inferred_type = "string"
        if non_nulls:
            first_val = str(non_nulls[0]).strip().replace("$", "").replace(",", "")
            if re.match(r"^-?\d+(\.\d+)?$", first_val):
                inferred_type = "numeric"
            elif re.match(r"^\d{4}-\d{2}-\d{2}", str(non_nulls[0]).strip()):
                inferred_type = "date"

        col_profiles[col] = {
            "source_column": col,
            "inferred_type": inferred_type,
            "null_count": null_count,
            "null_pct": round((null_count / len(rows) * 100.0), 1) if rows else 0,
            "unique_count": unique_count,
            "sample_values": non_nulls[:3],
        }

    return {
        "row_count": len(rows),
        "column_count": len(columns),
        "columns": col_profiles,
        "sample_rows": rows[:5],
    }


def normalize_row_to_canonical(
    row: Dict[str, Any],
    mapping: Dict[str, str],
    dataset_type: str = "invoices",
) -> Tuple[Dict[str, Any], List[str]]:
    """Normalize a raw data row to canonical fields and compute truthful validation errors."""
    norm: Dict[str, Any] = {}
    errors: List[str] = []

    # Map raw fields to canonical names
    for src_col, canon_field in mapping.items():
        if not canon_field or src_col not in row:
            continue
        val = row.get(src_col)

        # Parse amounts & quantities
        if "amount" in canon_field or canon_field in ("unit_price", "quantity", "received_quantity"):
            if val is not None and str(val).strip() != "":
                clean_num = str(val).replace("$", "").replace(",", "").strip()
                try:
                    norm[canon_field] = float(clean_num)
                except ValueError:
                    errors.append(f"Invalid numeric value '{val}' in column '{src_col}' for '{canon_field}'")
                    norm[canon_field] = None
            else:
                norm[canon_field] = None

        # Parse dates
        elif "date" in canon_field:
            if val is not None and str(val).strip() != "":
                val_str = str(val).strip()[:10]
                norm[canon_field] = val_str
            else:
                norm[canon_field] = None

        # Parse boolean flags
        elif canon_field in ("is_active", "approved"):
            if val is not None:
                str_val = str(val).strip().lower()
                norm[canon_field] = str_val in ("true", "1", "yes", "active", "approved")
            else:
                norm[canon_field] = True

        # Parse list values (e.g. roles)
        elif canon_field == "roles":
            if isinstance(val, list):
                norm[canon_field] = val
            elif isinstance(val, str) and val.strip():
                norm[canon_field] = [p.strip() for p in val.replace(";", ",").split(",") if p.strip()]
            else:
                norm[canon_field] = []

        else:
            norm[canon_field] = str(val).strip() if val is not None else None

    # Check required fields for this canonical dataset type
    required_fields = TYPE_REQUIRED_FIELDS.get(dataset_type, [])
    for rf in required_fields:
        val = norm.get(rf)
        if val is None or val == "" or str(val).lower() in ("nan", "null", "none"):
            errors.append(f"Missing mandatory field '{rf}' for dataset type '{dataset_type}'")

    return norm, errors

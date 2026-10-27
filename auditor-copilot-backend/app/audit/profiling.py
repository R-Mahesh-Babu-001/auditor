"""
Dataset profiling, canonical field mapping, and row normalization for audit datasets.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, date


CANONICAL_P2P_FIELDS = {
    "supplier_name": ["supplier", "vendor", "vendor_name", "supplier_name", "payee"],
    "supplier_code": ["supplier_id", "vendor_id", "supplier_code", "vendor_num"],
    "po_number": ["po_number", "po_no", "purchase_order", "po", "order_id"],
    "invoice_number": ["invoice_number", "invoice_no", "inv_num", "inv_no", "bill_no"],
    "invoice_date": ["invoice_date", "inv_date", "bill_date", "date"],
    "total_amount": ["total_amount", "amount", "invoice_amount", "gross_amount", "total", "net_amount"],
    "currency_code": ["currency", "curr", "currency_code"],
    "quantity": ["quantity", "qty", "invoiced_qty", "ordered_qty"],
    "unit_price": ["unit_price", "rate", "price"],
    "receipt_number": ["receipt_number", "gr_number", "receipt_no", "goods_receipt"],
    "receipt_date": ["receipt_date", "gr_date", "received_date"],
    "received_quantity": ["received_qty", "qty_received", "received_quantity"],
    "payment_reference": ["payment_ref", "check_number", "payment_reference", "payment_id"],
    "payment_date": ["payment_date", "paid_date", "check_date"],
    "approval_status": ["approval_status", "status", "approved", "approval_state"],
    "approver_name": ["approver", "approver_name", "approved_by"],
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
            "mapping_status": "proposed" if best_match else "unmapped",
        })
    return mappings


def profile_dataset_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Profile tabular data rows: nulls, types, duplicates, and suspicious formats."""
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
            first_val = str(non_nulls[0]).strip()
            if re.match(r"^-?\d+(\.\d+)?$", first_val):
                inferred_type = "numeric"
            elif re.match(r"^\d{4}-\d{2}-\d{2}", first_val):
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


def normalize_row_to_canonical(row: Dict[str, Any], mapping: Dict[str, str]) -> Tuple[Dict[str, Any], List[str]]:
    """Normalize a raw row into canonical P2P fields using verified column mapping."""
    norm: Dict[str, Any] = {}
    errors: List[str] = []

    for src_col, canon_field in mapping.items():
        if not canon_field or src_col not in row:
            continue
        val = row.get(src_col)

        # Parse amounts
        if "amount" in canon_field or canon_field in ("unit_price", "quantity", "received_quantity"):
            if val is not None and str(val).strip() != "":
                clean_num = str(val).replace("$", "").replace(",", "").strip()
                try:
                    norm[canon_field] = float(clean_num)
                except ValueError:
                    errors.append(f"Invalid numeric value '{val}' for column '{src_col}'")
                    norm[canon_field] = None
            else:
                norm[canon_field] = 0.0

        # Parse dates
        elif "date" in canon_field:
            if val is not None and str(val).strip() != "":
                val_str = str(val).strip()[:10]
                norm[canon_field] = val_str
            else:
                norm[canon_field] = None
        else:
            norm[canon_field] = str(val).strip() if val is not None else None

    return norm, errors


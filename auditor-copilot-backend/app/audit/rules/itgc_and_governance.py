"""
Deterministic test rules for IT General Controls (ITGC), Segregation of Duties (SoD),
Vendor Assurance, and AI Governance reviews.
"""

from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional, Set


# Standard P2P Segregation of Duties conflicting role pairs
SOD_CONFLICT_PAIRS = [
    ("PO_CREATION", "INVOICE_APPROVAL", "Cannot create purchase orders and approve vendor invoices"),
    ("VENDOR_MASTER_MAINTAIN", "PAYMENT_RELEASE", "Cannot maintain vendor bank/master records and release payments"),
    ("GOODS_RECEIPT_ENTRY", "INVOICE_PROCESSING", "Cannot record physical goods receipts and process invoice matching"),
    ("JOURNAL_ENTRY", "FINANCIAL_POSTING_APPROVE", "Cannot prepare and post journal vouchers without independent approval"),
]


def run_itgc_sod_analysis(
    user_roles: List[Dict[str, Any]],
    leavers: Optional[List[Dict[str, Any]]] = None,
    inactive_days_threshold: int = 90,
) -> Dict[str, Any]:
    """Audit IT General Controls: SoD conflicts, terminated user access, and inactive accounts."""
    exceptions = []
    now = datetime.now(timezone.utc)

    # Leaver set
    leaver_ids: Set[str] = set()
    if leavers:
        for l in leavers:
            uid = str(l.get("user_id") or l.get("email") or "").strip().lower()
            if uid:
                leaver_ids.add(uid)

    passed_count = 0

    for user in user_roles:
        uid = str(user.get("user_id") or user.get("email") or "")
        email = str(user.get("email", uid)).lower()
        roles = [r.strip().upper() for r in (user.get("roles") or user.get("permissions") or [])]
        is_active = bool(user.get("is_active", True))
        last_login_str = user.get("last_login_at")

        # 1. Leaver still active check
        if email in leaver_ids and is_active:
            exceptions.append({
                "exception_key": f"ITGC-LEAVER-ACTIVE-{uid}",
                "exception_type": "retained_leaver_access",
                "severity": "critical",
                "title": f"Terminated Employee '{email}' Retains Active System Access",
                "description": f"User was listed in trusted leaver register but account remains active in ERP/identity export.",
                "observed_values": {"user": email, "is_active": True},
                "expected_values": {"required": "Revoke access within 24 hours of separation"},
            })
            continue

        # 2. Inactive account check
        if is_active and last_login_str:
            try:
                if isinstance(last_login_str, str):
                    last_login = datetime.fromisoformat(last_login_str.replace("Z", "+00:00"))
                else:
                    last_login = last_login_str
                if last_login.tzinfo is None:
                    last_login = last_login.replace(tzinfo=timezone.utc)
                days_inactive = (now - last_login).days
                if days_inactive > inactive_days_threshold:
                    exceptions.append({
                        "exception_key": f"ITGC-INACTIVE-{uid}",
                        "exception_type": "dormant_active_account",
                        "severity": "medium",
                        "title": f"Dormant Account Active Beyond {inactive_days_threshold} Days: {email}",
                        "description": f"Account has been inactive for {days_inactive} days without deactivation or re-certification.",
                        "observed_values": {"days_inactive": days_inactive, "last_login": str(last_login)},
                        "expected_values": {"max_inactive_days": inactive_days_threshold},
                    })
            except Exception:
                pass

        # 3. Segregation of Duties check
        user_role_set = set(roles)
        for role_a, role_b, desc in SOD_CONFLICT_PAIRS:
            if role_a in user_role_set and role_b in user_role_set:
                exceptions.append({
                    "exception_key": f"ITGC-SOD-{uid}-{role_a}-{role_b}",
                    "exception_type": "segregation_of_duties_conflict",
                    "severity": "high",
                    "title": f"SoD Conflict: {email} Holds Both {role_a} and {role_b}",
                    "description": f"User possesses conflicting privileges: {desc}.",
                    "observed_values": {"user": email, "conflicting_roles": [role_a, role_b]},
                    "expected_values": {"segregation_policy": "Roles must be assigned to separate individuals or have mitigating controls"},
                })

        passed_count += 1

    return {
        "rule_code": "ITGC_SOD_CONFLICT",
        "population_count": len(user_roles),
        "passed_count": passed_count,
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


def run_vendor_assurance_review(vendors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify third-party assurance documentation (SOC reports, ISO certifications, questionnaires)."""
    exceptions = []
    today = date.today()

    for v in vendors:
        v_name = v.get("name") or v.get("vendor_name", "UNKNOWN")
        risk_tier = str(v.get("risk_tier", "medium")).lower()
        soc_expiry_str = v.get("soc_report_expiry")
        has_soc = bool(v.get("has_soc_report", False))

        if risk_tier in ("high", "critical"):
            if not has_soc:
                exceptions.append({
                    "exception_key": f"VENDOR-NO-SOC-{v_name[:12]}",
                    "exception_type": "missing_vendor_assurance",
                    "severity": "high",
                    "title": f"Missing SOC / Assurance Report for High-Risk Vendor: {v_name}",
                    "description": f"Vendor is classified as '{risk_tier}' risk tier but no valid SOC 1/2 report is on file.",
                    "observed_values": {"vendor": v_name, "risk_tier": risk_tier, "assurance_report": "None"},
                    "expected_values": {"requirement": "Annual independent SOC 1 / SOC 2 Type II report"},
                })
            elif soc_expiry_str:
                try:
                    exp = date.fromisoformat(str(soc_expiry_str))
                    if exp < today:
                        exceptions.append({
                            "exception_key": f"VENDOR-EXPIRED-SOC-{v_name[:12]}",
                            "exception_type": "expired_vendor_assurance",
                            "severity": "medium",
                            "title": f"Expired Assurance Report for Vendor: {v_name}",
                            "description": f"Assurance coverage expired on {exp} ({ (today - exp).days } days ago).",
                            "observed_values": {"vendor": v_name, "expired_date": str(exp)},
                            "expected_values": {"requirement": "Current unexpired assurance report covering audit period"},
                        })
                except Exception:
                    pass

    return {
        "rule_code": "VENDOR_ASSURANCE_REVIEW",
        "population_count": len(vendors),
        "passed_count": len(vendors) - len(exceptions),
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


def run_ai_governance_review(ai_systems: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify AI inventory completeness and governance compliance."""
    exceptions = []

    required_fields = [
        ("system_owner", "System Owner"),
        ("business_purpose", "Business Purpose Documentation"),
        ("model_provider", "Model / Algorithm Provider"),
        ("risk_tier", "Risk Classification"),
        ("approval_records", "Authorized Approval Record"),
        ("monitoring_plan", "Continuous Monitoring Plan"),
    ]

    for sys in ai_systems:
        name = sys.get("name") or sys.get("system_name", "UNKNOWN_AI_SYSTEM")
        for field_key, field_label in required_fields:
            val = sys.get(field_key)
            if not val:
                exceptions.append({
                    "exception_key": f"AI-GOV-MISSING-{name[:10]}-{field_key}",
                    "exception_type": "ai_governance_gap",
                    "severity": "medium",
                    "title": f"AI Governance Gap: Missing {field_label} for '{name}'",
                    "description": f"AI inventory item lacks required governance metadata '{field_label}'.",
                    "observed_values": {"system": name, "field": field_key, "value": None},
                    "expected_values": {"requirement": f"{field_label} must be documented and reviewed"},
                })

    return {
        "rule_code": "AI_GOVERNANCE_REVIEW",
        "population_count": len(ai_systems),
        "passed_count": len(ai_systems) - len(exceptions),
        "exception_count": len(exceptions),
        "exceptions": exceptions,
    }


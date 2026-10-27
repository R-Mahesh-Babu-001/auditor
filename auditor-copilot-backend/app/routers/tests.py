"""
Audit Tests and Test Execution router.
Executes deterministic audit tests against engagement datasets and records results in Neon DB.
"""

import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    AuditTestRuleTemplate,
    AuditTestRule,
    AuditTestRun,
    AuditEngagement,
)
from app.schemas import TestRunRequest
from app.routers.auth import get_default_context, get_current_context, OrganizationContext
from app.audit.execution import execute_audit_test

router = APIRouter(prefix="/tests", tags=["Audit Tests & Execution"])

STANDARD_TEST_TEMPLATES = [
    {
        "id": "tpl-p2p-3way",
        "rule_code": "P2P_THREE_WAY_MATCH",
        "template_code": "P2P_THREE_WAY_MATCH",
        "name": "Three-Way Matching (PO, Receipt, Invoice)",
        "description": "Deterministic comparison of PO, Goods Receipt, and Invoice quantities and amounts, enforcing percentage and monetary tolerance thresholds.",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {"tolerance_pct": 1.0, "tolerance_amount": 50.0},
        "required_dataset_types": ["purchase_orders", "goods_receipts", "invoices"],
    },
    {
        "id": "tpl-p2p-dup",
        "rule_code": "P2P_DUPLICATE_INVOICE_PAYMENT",
        "template_code": "P2P_DUPLICATE_INVOICE_PAYMENT",
        "name": "Duplicate Invoice & Payment Detection",
        "description": "Identification of exact duplicate invoice numbers/amounts and proximate-date duplicate billing amounts within 14 days.",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {"proximity_days": 14},
        "required_dataset_types": ["invoices", "payments"],
    },
    {
        "id": "tpl-p2p-appr",
        "rule_code": "P2P_MISSING_APPROVAL",
        "template_code": "P2P_MISSING_APPROVAL",
        "name": "Delegation of Authority (DOA) Approval Verification",
        "description": "Verification that invoices exceeding policy thresholds possess documented, authorized supervisory approval records.",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {"threshold_amount": 1000.0},
        "required_dataset_types": ["invoices", "approval_events"],
    },
    {
        "id": "tpl-p2p-mismatch",
        "rule_code": "P2P_PO_INVOICE_MISMATCH",
        "template_code": "P2P_PO_INVOICE_MISMATCH",
        "name": "PO & Invoice Linkage / Supplier Mismatch",
        "description": "Flags non-exempt invoices lacking approved purchase orders, non-existent PO references, or conflicting vendor linkages.",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {"exemption_threshold": 250.0},
        "required_dataset_types": ["invoices", "purchase_orders"],
    },
    {
        "id": "tpl-p2p-cutoff",
        "rule_code": "P2P_PERIOD_CUTOFF",
        "template_code": "P2P_PERIOD_CUTOFF",
        "name": "Financial Period Cut-Off Verification",
        "description": "Flags transactions where goods receipt occurred in current period but invoicing or posting was delayed into subsequent periods.",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {"window_days": 15},
        "required_dataset_types": ["goods_receipts", "invoices"],
    },
    {
        "id": "tpl-p2p-split",
        "rule_code": "P2P_THRESHOLD_SPLITTING",
        "template_code": "P2P_THRESHOLD_SPLITTING",
        "name": "Threshold Splitting & Structuring Risk Signals",
        "description": "Detects multiple purchases clustered just below procurement approval limits (e.g. $9,000–$9,999 for $10,000 threshold).",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {"threshold": 10000.0, "buffer_pct": 10.0},
        "required_dataset_types": ["invoices", "purchase_orders"],
    },
    {
        "id": "tpl-p2p-bank",
        "rule_code": "P2P_BANK_CHANGE_TIMING",
        "template_code": "P2P_BANK_CHANGE_TIMING",
        "name": "Bank Detail Modification / Payment Timing",
        "description": "Flags disbursements released within 14 days following vendor bank master modifications to prevent redirection fraud.",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {"proximity_days": 14},
        "required_dataset_types": ["payments", "supplier_master_changes"],
    },
    {
        "id": "tpl-p2p-supp-dup",
        "rule_code": "P2P_SUPPLIER_MASTER_DUPLICATION",
        "template_code": "P2P_SUPPLIER_MASTER_DUPLICATION",
        "name": "Supplier Master Duplication Review",
        "description": "Identifies duplicate supplier accounts sharing identical Tax IDs, IBANs, bank accounts, or normalized company names.",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {},
        "required_dataset_types": ["suppliers"],
    },
    {
        "id": "tpl-p2p-sample",
        "rule_code": "P2P_SAMPLE_SELECTION",
        "template_code": "P2P_SAMPLE_SELECTION",
        "name": "Reproducible Stratified Audit Sampling",
        "description": "Generates verifiable stratified audit samples (top 30% by value + random sample) preserving random seeds for examiners.",
        "category": "p2p",
        "domain": "p2p",
        "default_parameters": {"sample_size": 25, "seed": 42},
        "required_dataset_types": ["invoices"],
    },
]


@router.get("/templates")
def list_test_rule_templates(db: Session = Depends(get_db)):
    """List all available pre-built deterministic test rule templates."""
    db_templates = []
    try:
        db_templates = db.query(AuditTestRuleTemplate).filter(AuditTestRuleTemplate.enabled == True).all()
    except Exception:
        db_templates = []

    existing_codes = set()
    result = []

    for t in db_templates:
        existing_codes.add(t.rule_code)
        result.append({
            "id": str(t.id),
            "rule_code": t.rule_code,
            "template_code": t.rule_code,
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "domain": t.category or "p2p",
            "implementation_key": t.implementation_key,
            "default_parameters": t.default_parameters,
            "required_dataset_types": t.required_dataset_types,
        })

    # Include any standard templates not already stored in the DB
    for std in STANDARD_TEST_TEMPLATES:
        if std["rule_code"] not in existing_codes:
            result.append(std)

    return {"templates": result, "count": len(result)}


@router.get("/runs")
def list_test_runs(
    engagement_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List recent audit test runs with population, pass, and exception counts."""
    org, _ = get_default_context(db)
    query = db.query(AuditTestRun).filter(AuditTestRun.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(AuditTestRun.engagement_id == uuid.UUID(engagement_id))
        except ValueError:
            pass

    runs = query.order_by(AuditTestRun.created_at.desc()).limit(limit).all()
    results = []
    for r in runs:
        tpl_name = None
        if r.rule_id:
            rule = db.query(AuditTestRule).filter(AuditTestRule.id == r.rule_id).first()
            if rule:
                tpl_name = rule.name
        results.append({
            "id": str(r.id),
            "rule_id": str(r.rule_id) if r.rule_id else None,
            "template_name": tpl_name or "Audit Test Run",
            "rule_version": r.rule_version,
            "status": r.execution_status,
            "execution_status": r.execution_status,
            "total_records_tested": r.population_count,
            "population_count": r.population_count,
            "passed_count": r.passed_count,
            "exceptions_found": r.exception_count,
            "exception_count": r.exception_count,
            "result_summary": r.result_summary,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "created_at": r.started_at.isoformat() if r.started_at else None,
        })

    return {"runs": results, "count": len(results)}


@router.post("/run")
def trigger_audit_test(
    req: TestRunRequest,
    engagement_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Execute a deterministic audit test rule against the engagement dataset."""
    rule_code = req.rule_code or req.template_code
    if not rule_code:
        raise HTTPException(status_code=400, detail="rule_code or template_code is required.")

    # Resolve engagement
    eff_eng_str = engagement_id or req.engagement_id or (str(ctx.engagement_id) if ctx.engagement_id else None)
    eff_eng_uuid = None

    if eff_eng_str:
        try:
            eff_eng_uuid = uuid.UUID(str(eff_eng_str))
        except ValueError:
            pass

    if not eff_eng_uuid:
        # Get or create active engagement
        eng = db.query(AuditEngagement).filter(
            AuditEngagement.organization_id == ctx.organization_id,
            AuditEngagement.status == "in_progress",
        ).first()
        if not eng:
            eng = AuditEngagement(
                organization_id=ctx.organization_id,
                title="FY2026 Q1 Procure-to-Pay Engagement",
                audit_year=2026,
                status="in_progress",
                created_by=ctx.user_id,
            )
            db.add(eng)
            db.commit()
            db.refresh(eng)
        eff_eng_uuid = eng.id

    res = execute_audit_test(
        db=db,
        organization_id=ctx.organization_id,
        engagement_id=eff_eng_uuid,
        rule_code=rule_code,
        parameters=req.parameters or {},
        user_id=ctx.user_id,
    )

    if res.get("status") == "failed":
        raise HTTPException(status_code=500, detail=res.get("error", "Test execution failed."))

    # Return normalized response compatible with all callers
    pop_count = res.get("population_count", 0)
    exc_count = res.get("exception_count", 0)

    return {
        "message": f"Test '{rule_code}' executed successfully",
        "rule_code": rule_code,
        "test_run_id": str(res.get("test_run_id", "")),
        "records_tested": pop_count,
        "exceptions_found": exc_count,
        "population_count": pop_count,
        "exception_count": exc_count,
        "passed_count": res.get("passed_count", 0),
        "status": res.get("status", "completed"),
        "exceptions": res.get("exceptions", []),
    }

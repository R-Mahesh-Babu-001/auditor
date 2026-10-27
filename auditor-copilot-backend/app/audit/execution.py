"""
Execution orchestrator for deterministic audit tests and exception persistence in Neon DB.
"""

import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import (
    AuditTestRule,
    AuditTestRun,
    AuditException,
    DatasetRow,
    AuditDataset,
    ExceptionRowLink,
    AuditEventLog,
)
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
)


def execute_audit_test(
    db: Session,
    organization_id: uuid.UUID,
    engagement_id: uuid.UUID,
    rule_code: str,
    parameters: Optional[Dict[str, Any]] = None,
    user_id: Optional[uuid.UUID] = None,
) -> Dict[str, Any]:
    """Execute the specified audit test rule against engagement datasets and persist results to Neon DB."""
    params = parameters or {}

    # Find or create test rule record
    rule = db.query(AuditTestRule).filter(
        AuditTestRule.organization_id == organization_id,
        AuditTestRule.engagement_id == engagement_id,
        AuditTestRule.rule_code == rule_code,
    ).first()

    if not rule:
        rule = AuditTestRule(
            organization_id=organization_id,
            engagement_id=engagement_id,
            rule_code=rule_code,
            name=rule_code.replace("_", " ").title(),
            version_number=1,
            parameters=params,
            status="approved",
            created_by=user_id,
        )
        db.add(rule)
        db.flush()

    # Create test run record
    test_run = AuditTestRun(
        organization_id=organization_id,
        engagement_id=engagement_id,
        rule_id=rule.id,
        rule_version=rule.version_number,
        execution_status="running",
        requested_by=user_id,
        started_at=datetime.utcnow(),
        parameters_snapshot=params,
        input_snapshot={},
        result_summary={},
        population_count=0,
        passed_count=0,
        exception_count=0,
        skipped_count=0,
    )
    db.add(test_run)
    db.flush()

    # Retrieve dataset rows for this engagement
    rows = db.query(DatasetRow).filter(
        DatasetRow.organization_id == organization_id,
        DatasetRow.engagement_id == engagement_id,
    ).order_by(DatasetRow.row_number).all()

    # Extract normalized or raw data dicts
    records = []
    row_id_map = {}
    for r in rows:
        data = r.normalized_data if r.normalized_data else r.raw_data
        data_copy = dict(data)
        data_copy["_row_id"] = str(r.id)
        records.append(data_copy)
        row_id_map[str(r.id)] = r

    # Execute deterministic rule based on rule_code
    code = rule_code.upper()
    result: Dict[str, Any] = {}

    try:
        if "THREE_WAY" in code or code == "P2P_THREE_WAY_MATCH":
            tol_pct = float(params.get("tolerance_pct", 1.0))
            tol_amt = float(params.get("tolerance_amount", 50.0))
            result = run_three_way_match(records, records, records, tolerance_pct=tol_pct, tolerance_amount=tol_amt)

        elif "DUPLICATE" in code or code == "P2P_DUPLICATE_INVOICE_PAYMENT":
            result = run_duplicate_invoice_payment(records)

        elif "APPROVAL" in code or code == "P2P_MISSING_APPROVAL":
            thresh = float(params.get("threshold_amount", 1000.0))
            result = run_missing_approval(records, records, threshold_amount=thresh)

        elif "SPLITTING" in code or code == "P2P_THRESHOLD_SPLITTING":
            thresh = float(params.get("threshold", 10000.0))
            result = run_threshold_splitting(records, threshold=thresh)

        elif "PO_INVOICE_MISMATCH" in code or "MISMATCH" in code:
            exemption = float(params.get("exemption_threshold", 250.0))
            result = run_po_invoice_mismatch(records, records, exemption_threshold=exemption)

        elif "CUTOFF" in code or code == "P2P_PERIOD_CUTOFF":
            period_end = date.today()
            if params.get("period_end_date"):
                try:
                    period_end = date.fromisoformat(str(params["period_end_date"]))
                except Exception:
                    pass
            result = run_period_cutoff_check(records, records, period_end_date=period_end)

        elif "BANK_CHANGE" in code or code == "P2P_BANK_CHANGE_TIMING":
            prox_days = int(params.get("proximity_days", 14))
            result = run_bank_change_payment_timing(records, records, proximity_days=prox_days)

        elif "SUPPLIER_MASTER" in code or "SUPPLIER_DUP" in code:
            result = run_supplier_master_duplication(records)

        elif "SAMPLE" in code or code == "P2P_SAMPLE_SELECTION":
            sample_size = int(params.get("sample_size", 25))
            seed = int(params.get("seed", 42))
            result = run_reproducible_sample(records, sample_size=sample_size, seed=seed)

        elif "SOD" in code or "ITGC" in code:
            result = run_itgc_sod_analysis(records)

        elif "VENDOR" in code:
            result = run_vendor_assurance_review(records)

        elif "AI" in code:
            result = run_ai_governance_review(records)

        else:
            # Default to duplicate invoice test
            result = run_duplicate_invoice_payment(records)

        # Update test run metrics
        test_run.execution_status = "completed"
        test_run.completed_at = datetime.utcnow()
        test_run.population_count = result.get("population_count", len(records))
        test_run.passed_count = result.get("passed_count", 0)
        test_run.exception_count = result.get("exception_count", len(result.get("exceptions", [])))
        test_run.result_summary = {
            "summary": f"{test_run.exception_count} exceptions identified out of {test_run.population_count} records tested.",
            "rule_code": rule_code,
        }

        # Persist discovered exceptions
        for exc in result.get("exceptions", []):
            db_exc = AuditException(
                organization_id=organization_id,
                engagement_id=engagement_id,
                test_run_id=test_run.id,
                exception_key=exc.get("exception_key", str(uuid.uuid4())),
                exception_type=exc.get("exception_type", "general_exception"),
                title=exc.get("title", "Audit Exception"),
                description=exc.get("description", ""),
                severity=exc.get("severity", "medium"),
                status="flagged",
                expected_values=exc.get("expected_values", {}),
                observed_values=exc.get("observed_values", {}),
                rationale=exc.get("rationale"),
            )
            db.add(db_exc)

        # Log audit event
        event = AuditEventLog(
            organization_id=organization_id,
            engagement_id=engagement_id,
            actor_user_id=user_id,
            event_type="test_run_completed",
            entity_type="audit_test_runs",
            entity_id=test_run.id,
            action=f"Executed test {rule_code}: {test_run.exception_count} exceptions",
            event_metadata={"rule_code": rule_code, "exceptions": test_run.exception_count},
        )
        db.add(event)
        db.commit()

        return {
            "status": "success",
            "test_run_id": str(test_run.id),
            "rule_code": rule_code,
            "population_count": test_run.population_count,
            "passed_count": test_run.passed_count,
            "exception_count": test_run.exception_count,
            "exceptions": result.get("exceptions", []),
        }

    except Exception as e:
        db.rollback()
        test_run.execution_status = "failed"
        test_run.error_summary = str(e)
        test_run.completed_at = datetime.utcnow()
        db.commit()
        return {
            "status": "failed",
            "error": str(e),
            "test_run_id": str(test_run.id),
        }


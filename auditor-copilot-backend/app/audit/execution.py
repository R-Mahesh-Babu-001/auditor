"""
Execution orchestrator for deterministic audit tests and exception persistence in Neon DB.
Enforces dataset-specific selection, typed row collections, and complete exception-to-source-row evidence linking.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import (
    AuditTestRule,
    AuditTestRun,
    AuditException,
    DatasetRow,
    AuditDataset,
    TestRunDataset,
    ExceptionRowLink,
    ExceptionEvidenceLink,
    AuditEventLog,
    AuditEngagement,
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

# Rule specifications defining canonical codes, names, and required dataset types
RULE_SPECIFICATIONS: Dict[str, Dict[str, Any]] = {
    "P2P_THREE_WAY_MATCH": {
        "canonical_code": "P2P_THREE_WAY_MATCH",
        "name": "Three-Way Matching (PO vs GR vs Invoice)",
        "required_dataset_types": ["purchase_orders", "goods_receipts", "invoices"],
    },
    "P2P_DUPLICATE_INVOICE_PAYMENT": {
        "canonical_code": "P2P_DUPLICATE_INVOICE_PAYMENT",
        "name": "Duplicate Invoice & Payment Detection",
        "required_dataset_types": ["invoices"],
        "optional_dataset_types": ["payments"],
    },
    "P2P_MISSING_APPROVAL": {
        "canonical_code": "P2P_MISSING_APPROVAL",
        "name": "Missing Required Invoice Approval",
        "required_dataset_types": ["invoices", "approvals"],
    },
    "P2P_THRESHOLD_SPLITTING": {
        "canonical_code": "P2P_THRESHOLD_SPLITTING",
        "name": "Purchase Threshold Splitting Detection",
        "required_dataset_types": ["invoices"],
    },
    "P2P_PO_INVOICE_MISMATCH": {
        "canonical_code": "P2P_PO_INVOICE_MISMATCH",
        "name": "PO to Invoice Mismatch & Supplier Validation",
        "required_dataset_types": ["invoices", "purchase_orders"],
    },
    "P2P_PERIOD_CUTOFF": {
        "canonical_code": "P2P_PERIOD_CUTOFF",
        "name": "Period Cut-off & Unrecorded Liabilities Review",
        "required_dataset_types": ["goods_receipts", "invoices"],
    },
    "P2P_BANK_CHANGE_TIMING": {
        "canonical_code": "P2P_BANK_CHANGE_TIMING",
        "name": "Payment Proximity to Vendor Bank Account Modification",
        "required_dataset_types": ["payments", "suppliers"],
    },
    "P2P_SUPPLIER_MASTER_DUPLICATION": {
        "canonical_code": "P2P_SUPPLIER_MASTER_DUPLICATION",
        "name": "Supplier Master Data Deduplication",
        "required_dataset_types": ["suppliers"],
    },
    "P2P_SAMPLE_SELECTION": {
        "canonical_code": "P2P_SAMPLE_SELECTION",
        "name": "Reproducible Stratified Audit Sampling",
        "required_dataset_types": ["invoices"],
    },
    "ITGC_SOD_ANALYSIS": {
        "canonical_code": "ITGC_SOD_ANALYSIS",
        "name": "Segregation of Duties & Terminated User Access",
        "required_dataset_types": ["user_access"],
        "optional_dataset_types": ["employee_directory"],
    },
    "VENDOR_ASSURANCE_REVIEW": {
        "canonical_code": "VENDOR_ASSURANCE_REVIEW",
        "name": "Third-Party Vendor Assurance & Risk Review",
        "required_dataset_types": ["suppliers"],
    },
    "AI_GOVERNANCE_REVIEW": {
        "canonical_code": "AI_GOVERNANCE_REVIEW",
        "name": "AI System Inventory & Governance Evaluation",
        "required_dataset_types": ["ai_system_inventory"],
    },
}


def resolve_rule_spec(code: str) -> Dict[str, Any]:
    """Resolve incoming rule code or alias to its canonical specification."""
    clean = code.upper().strip()
    if clean in RULE_SPECIFICATIONS:
        return RULE_SPECIFICATIONS[clean]

    # Substring / alias resolution
    if "THREE_WAY" in clean or "3WAY" in clean:
        return RULE_SPECIFICATIONS["P2P_THREE_WAY_MATCH"]
    if "DUPLICATE" in clean:
        return RULE_SPECIFICATIONS["P2P_DUPLICATE_INVOICE_PAYMENT"]
    if "APPROVAL" in clean:
        return RULE_SPECIFICATIONS["P2P_MISSING_APPROVAL"]
    if "SPLITTING" in clean:
        return RULE_SPECIFICATIONS["P2P_THRESHOLD_SPLITTING"]
    if "MISMATCH" in clean:
        return RULE_SPECIFICATIONS["P2P_PO_INVOICE_MISMATCH"]
    if "CUTOFF" in clean:
        return RULE_SPECIFICATIONS["P2P_PERIOD_CUTOFF"]
    if "BANK_CHANGE" in clean:
        return RULE_SPECIFICATIONS["P2P_BANK_CHANGE_TIMING"]
    if "SUPPLIER" in clean:
        return RULE_SPECIFICATIONS["P2P_SUPPLIER_MASTER_DUPLICATION"]
    if "SAMPLE" in clean:
        return RULE_SPECIFICATIONS["P2P_SAMPLE_SELECTION"]
    if "SOD" in clean or "ITGC" in clean:
        return RULE_SPECIFICATIONS["ITGC_SOD_ANALYSIS"]
    if "VENDOR" in clean:
        return RULE_SPECIFICATIONS["VENDOR_ASSURANCE_REVIEW"]
    if "AI" in clean:
        return RULE_SPECIFICATIONS["AI_GOVERNANCE_REVIEW"]

    # Fallback default
    return {
        "canonical_code": clean,
        "name": clean.replace("_", " ").title(),
        "required_dataset_types": ["invoices"],
    }


def execute_audit_test(
    db: Session,
    organization_id: uuid.UUID,
    engagement_id: uuid.UUID,
    rule_code: Optional[str] = None,
    template_code: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    selected_dataset_ids: Optional[Dict[str, str]] = None,
    dataset_ids: Optional[List[str]] = None,
    user_id: Optional[uuid.UUID] = None,
    created_by_user_id: Optional[uuid.UUID] = None,
    rule_id: Optional[uuid.UUID] = None,
) -> Dict[str, Any]:
    """Execute the specified audit test rule against explicitly resolved engagement datasets
    and persist results and row-level evidence links to Neon DB.
    """
    effective_code = rule_code or template_code or "P2P_THREE_WAY_MATCH"
    effective_user_id = user_id or created_by_user_id
    params = parameters or {}
    spec = resolve_rule_spec(effective_code)
    canonical_code = spec["canonical_code"]
    required_types = spec.get("required_dataset_types", ["invoices"])
    optional_types = spec.get("optional_dataset_types", [])

    # Validate engagement belongs to caller's organization
    engagement = db.query(AuditEngagement).filter(
        AuditEngagement.id == engagement_id,
        AuditEngagement.organization_id == organization_id,
    ).first()
    if not engagement:
        return {
            "status": "failed",
            "error_code": "ENGAGEMENT_NOT_FOUND",
            "error": f"Engagement '{engagement_id}' not found for active organization.",
        }

    # Find or create test rule record
    rule = db.query(AuditTestRule).filter(
        AuditTestRule.organization_id == organization_id,
        AuditTestRule.engagement_id == engagement_id,
        AuditTestRule.rule_code == canonical_code,
    ).first()

    if not rule:
        rule = AuditTestRule(
            organization_id=organization_id,
            engagement_id=engagement_id,
            rule_code=canonical_code,
            name=spec.get("name", canonical_code.replace("_", " ").title()),
            version_number=1,
            parameters=params,
            status="approved",
            created_by=effective_user_id,
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
        requested_by=effective_user_id,
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

    # -------------------------------------------------------------
    # 1. Dataset Resolution: Resolve distinct datasets per required type
    # -------------------------------------------------------------
    resolved_datasets: Dict[str, AuditDataset] = {}
    selected_ds_map = dict(selected_dataset_ids) if selected_dataset_ids else {}

    # If dataset_ids list provided without mapping, attempt to map by dataset_type
    if dataset_ids and not selected_ds_map:
        for ds_id_str in dataset_ids:
            try:
                ds = db.query(AuditDataset).filter(
                    AuditDataset.id == uuid.UUID(str(ds_id_str)),
                    AuditDataset.organization_id == organization_id,
                    AuditDataset.engagement_id == engagement_id,
                ).first()
                if ds:
                    selected_ds_map[ds.dataset_type] = str(ds.id)
            except Exception:
                pass

    for dtype in required_types:
        # Check explicit user selection first
        if dtype in selected_ds_map:
            ds_id_val = selected_ds_map[dtype]
            try:
                ds_uuid = uuid.UUID(str(ds_id_val))
            except (ValueError, TypeError):
                test_run.execution_status = "failed"
                test_run.error_code = "INVALID_DATASET_ID"
                test_run.error_summary = f"Invalid dataset UUID '{ds_id_val}' specified for '{dtype}'."
                test_run.completed_at = datetime.utcnow()
                db.commit()
                return {
                    "status": "failed",
                    "error_code": "INVALID_DATASET_ID",
                    "error": test_run.error_summary,
                    "test_run_id": str(test_run.id),
                }

            ds = db.query(AuditDataset).filter(
                AuditDataset.id == ds_uuid,
                AuditDataset.organization_id == organization_id,
                AuditDataset.engagement_id == engagement_id,
            ).first()
            if not ds:
                test_run.execution_status = "failed"
                test_run.error_code = "DATASET_NOT_FOUND"
                test_run.error_summary = f"Selected dataset '{ds_id_val}' for required type '{dtype}' was not found in this engagement."
                test_run.completed_at = datetime.utcnow()
                db.commit()
                return {
                    "status": "failed",
                    "error_code": "DATASET_NOT_FOUND",
                    "error": test_run.error_summary,
                    "test_run_id": str(test_run.id),
                }
            resolved_datasets[dtype] = ds
        else:
            # Auto-resolve from engagement datasets
            candidates = db.query(AuditDataset).filter(
                AuditDataset.organization_id == organization_id,
                AuditDataset.engagement_id == engagement_id,
                AuditDataset.dataset_type == dtype,
            ).all()

            if len(candidates) == 0:
                # Check if there is exactly 1 dataset in the entire engagement and rule requires only 1 dataset
                all_ds = db.query(AuditDataset).filter(
                    AuditDataset.organization_id == organization_id,
                    AuditDataset.engagement_id == engagement_id,
                ).all()
                if len(all_ds) == 1 and len(required_types) == 1:
                    resolved_datasets[dtype] = all_ds[0]
                else:
                    test_run.execution_status = "failed"
                    test_run.error_code = "MISSING_DATASET_TYPE"
                    test_run.error_summary = (
                        f"Missing required dataset type '{dtype}' for audit test '{canonical_code}'. "
                        f"Please upload and validate a '{dtype}' dataset first."
                    )
                    test_run.completed_at = datetime.utcnow()
                    db.commit()
                    return {
                        "status": "failed",
                        "error_code": "MISSING_DATASET_TYPE",
                        "error": test_run.error_summary,
                        "test_run_id": str(test_run.id),
                    }
            elif len(candidates) == 1:
                resolved_datasets[dtype] = candidates[0]
            else:
                # Ambiguous selection: multiple datasets of the same type exist!
                candidate_names = [f"'{c.dataset_name}' ({c.id})" for c in candidates]
                test_run.execution_status = "failed"
                test_run.error_code = "AMBIGUOUS_DATASET_SELECTION"
                test_run.error_summary = (
                    f"Multiple datasets found for required type '{dtype}': {', '.join(candidate_names)}. "
                    f"Please explicitly specify which dataset to test in 'selected_dataset_ids'."
                )
                test_run.completed_at = datetime.utcnow()
                db.commit()
                return {
                    "status": "failed",
                    "error_code": "AMBIGUOUS_DATASET_SELECTION",
                    "error": test_run.error_summary,
                    "test_run_id": str(test_run.id),
                }

    # Also resolve optional dataset types if present
    for opt_type in optional_types:
        if opt_type in selected_ds_map:
            try:
                opt_ds = db.query(AuditDataset).filter(
                    AuditDataset.id == uuid.UUID(str(selected_ds_map[opt_type])),
                    AuditDataset.organization_id == organization_id,
                    AuditDataset.engagement_id == engagement_id,
                ).first()
                if opt_ds:
                    resolved_datasets[opt_type] = opt_ds
            except Exception:
                pass
        else:
            opt_cands = db.query(AuditDataset).filter(
                AuditDataset.organization_id == organization_id,
                AuditDataset.engagement_id == engagement_id,
                AuditDataset.dataset_type == opt_type,
            ).all()
            if len(opt_cands) == 1:
                resolved_datasets[opt_type] = opt_cands[0]

    # -------------------------------------------------------------
    # 2. Fetch Typed Collections strictly by resolved dataset_id
    # -------------------------------------------------------------
    typed_records: Dict[str, List[Dict[str, Any]]] = {}
    total_population = 0

    for dtype, ds in resolved_datasets.items():
        rows = db.query(DatasetRow).filter(
            DatasetRow.organization_id == organization_id,
            DatasetRow.engagement_id == engagement_id,
            DatasetRow.dataset_id == ds.id,
        ).order_by(DatasetRow.row_number).all()

        records = []
        for r in rows:
            data = r.normalized_data if r.normalized_data else r.raw_data
            data_copy = dict(data)
            data_copy["_row_id"] = str(r.id)
            data_copy["_dataset_id"] = str(ds.id)
            data_copy["_row_number"] = r.row_number
            records.append(data_copy)

        typed_records[dtype] = records
        total_population += len(records)

    # -------------------------------------------------------------
    # 3. Execute Deterministic Rule with Typed Collections
    # -------------------------------------------------------------
    try:
        result: Dict[str, Any] = {}

        if canonical_code == "P2P_THREE_WAY_MATCH":
            tol_pct = float(params.get("tolerance_pct", 1.0))
            tol_amt = float(params.get("tolerance_amount", 50.0))
            result = run_three_way_match(
                pos=typed_records.get("purchase_orders", []),
                receipts=typed_records.get("goods_receipts", []),
                invoices=typed_records.get("invoices", []),
                tolerance_pct=tol_pct,
                tolerance_amount=tol_amt,
            )

        elif canonical_code == "P2P_DUPLICATE_INVOICE_PAYMENT":
            result = run_duplicate_invoice_payment(
                invoices=typed_records.get("invoices", []),
                payments=typed_records.get("payments"),
            )

        elif canonical_code == "P2P_MISSING_APPROVAL":
            thresh = float(params.get("threshold_amount", 1000.0))
            result = run_missing_approval(
                invoices=typed_records.get("invoices", []),
                approval_events=typed_records.get("approvals", []),
                threshold_amount=thresh,
            )

        elif canonical_code == "P2P_THRESHOLD_SPLITTING":
            thresh = float(params.get("threshold", 10000.0))
            result = run_threshold_splitting(
                invoices=typed_records.get("invoices", []),
                threshold=thresh,
            )

        elif canonical_code == "P2P_PO_INVOICE_MISMATCH":
            exemption = float(params.get("exemption_threshold", 250.0))
            result = run_po_invoice_mismatch(
                invoices=typed_records.get("invoices", []),
                pos=typed_records.get("purchase_orders", []),
                exemption_threshold=exemption,
            )

        elif canonical_code == "P2P_PERIOD_CUTOFF":
            period_end = engagement.period_end or date.today()
            if params.get("period_end_date"):
                try:
                    period_end = date.fromisoformat(str(params["period_end_date"]))
                except Exception:
                    pass
            result = run_period_cutoff_check(
                receipts=typed_records.get("goods_receipts", []),
                invoices=typed_records.get("invoices", []),
                period_end_date=period_end,
            )

        elif canonical_code == "P2P_BANK_CHANGE_TIMING":
            prox_days = int(params.get("proximity_days", 14))
            result = run_bank_change_payment_timing(
                payments=typed_records.get("payments", []),
                bank_change_events=typed_records.get("suppliers", []),
                proximity_days=prox_days,
            )

        elif canonical_code == "P2P_SUPPLIER_MASTER_DUPLICATION":
            result = run_supplier_master_duplication(
                suppliers=typed_records.get("suppliers", []),
            )

        elif canonical_code == "P2P_SAMPLE_SELECTION":
            sample_size = int(params.get("sample_size", 25))
            seed = int(params.get("seed", 42))
            # Primary population is invoices or first resolved dataset
            pop_records = typed_records.get("invoices") or next(iter(typed_records.values()), [])
            result = run_reproducible_sample(
                records=pop_records,
                sample_size=sample_size,
                seed=seed,
            )

        elif canonical_code == "ITGC_SOD_ANALYSIS":
            result = run_itgc_sod_analysis(
                user_roles=typed_records.get("user_access", []),
                leavers=typed_records.get("employee_directory"),
            )

        elif canonical_code == "VENDOR_ASSURANCE_REVIEW":
            result = run_vendor_assurance_review(
                suppliers=typed_records.get("suppliers", []),
            )

        elif canonical_code == "AI_GOVERNANCE_REVIEW":
            result = run_ai_governance_review(
                ai_systems=typed_records.get("ai_system_inventory", []),
            )

        else:
            pop_records = next(iter(typed_records.values()), [])
            result = run_duplicate_invoice_payment(invoices=pop_records)

        # -------------------------------------------------------------
        # 4. Persist Test Run Metrics & Dataset Links
        # -------------------------------------------------------------
        test_run.execution_status = "completed"
        test_run.completed_at = datetime.utcnow()
        test_run.population_count = result.get("population_count", total_population)
        test_run.passed_count = result.get("passed_count", 0)
        test_run.exception_count = result.get("exception_count", len(result.get("exceptions", [])))
        test_run.result_summary = {
            "summary": f"{test_run.exception_count} exceptions identified out of {test_run.population_count} records tested.",
            "rule_code": canonical_code,
            "datasets_tested": {dtype: str(ds.id) for dtype, ds in resolved_datasets.items()},
        }
        test_run.input_snapshot = {
            "datasets": [
                {
                    "dataset_id": str(ds.id),
                    "dataset_name": ds.dataset_name,
                    "dataset_type": ds.dataset_type,
                    "version_number": ds.version_number,
                    "row_count": ds.row_count,
                }
                for ds in resolved_datasets.values()
            ],
            "parameters": params,
        }

        # Persist TestRunDataset associations
        for dtype, ds in resolved_datasets.items():
            existing_tr_ds = db.query(TestRunDataset).filter(
                TestRunDataset.organization_id == organization_id,
                TestRunDataset.engagement_id == engagement_id,
                TestRunDataset.test_run_id == test_run.id,
                TestRunDataset.dataset_id == ds.id,
            ).first()
            if not existing_tr_ds:
                db.add(TestRunDataset(
                    organization_id=organization_id,
                    engagement_id=engagement_id,
                    test_run_id=test_run.id,
                    dataset_id=ds.id,
                    dataset_version=ds.version_number or 1,
                ))

        # -------------------------------------------------------------
        # 5. Persist Discovered Exceptions & ExceptionRowLink (Fix 3)
        # -------------------------------------------------------------
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
            db.flush()

            # Helper to link a record safely
            def link_record(rec: Optional[Dict[str, Any]], link_role: str):
                if not rec or not rec.get("_row_id") or not rec.get("_dataset_id"):
                    return
                try:
                    r_id = uuid.UUID(str(rec["_row_id"]))
                    d_id = uuid.UUID(str(rec["_dataset_id"]))
                    existing_link = db.query(ExceptionRowLink).filter(
                        ExceptionRowLink.organization_id == organization_id,
                        ExceptionRowLink.engagement_id == engagement_id,
                        ExceptionRowLink.exception_id == db_exc.id,
                        ExceptionRowLink.dataset_id == d_id,
                        ExceptionRowLink.dataset_row_id == r_id,
                    ).first()
                    if not existing_link:
                        db.add(ExceptionRowLink(
                            organization_id=organization_id,
                            engagement_id=engagement_id,
                            exception_id=db_exc.id,
                            dataset_id=d_id,
                            dataset_row_id=r_id,
                            link_role=link_role,
                        ))
                except Exception:
                    pass

            # Link all contributing records
            # 1. Primary invoice / transaction record
            link_record(exc.get("invoice"), "source_row")
            # 2. Prior invoice in duplicate detection
            link_record(exc.get("prior_invoice"), "duplicate_match")
            # 3. Associated Purchase Order
            link_record(exc.get("po"), "po_row")
            # 4. Associated Goods Receipts
            recs = exc.get("receipts") or exc.get("receipt")
            if recs:
                if isinstance(recs, dict):
                    recs = [recs]
                for r in recs:
                    link_record(r, "receipt_row")
            # 5. Associated Supplier
            link_record(exc.get("supplier"), "supplier_row")
            link_record(exc.get("prior_supplier"), "duplicate_match")
            # 6. Associated Payment
            link_record(exc.get("payment"), "payment_row")
            # 7. Associated User / Account
            link_record(exc.get("user_role"), "user_account_row")
            # 8. Associated AI System
            link_record(exc.get("ai_system"), "ai_system_row")

        # Log audit event
        event = AuditEventLog(
            organization_id=organization_id,
            engagement_id=engagement_id,
            actor_user_id=effective_user_id,
            event_type="test_run_completed",
            entity_type="audit_test_runs",
            entity_id=test_run.id,
            event_metadata={
                "action": f"Executed test {canonical_code}: {test_run.exception_count} exceptions",
                "rule_code": canonical_code,
                "exceptions": test_run.exception_count,
                "population": test_run.population_count,
                "datasets": {dtype: str(ds.id) for dtype, ds in resolved_datasets.items()},
            },
        )
        db.add(event)
        db.commit()

        return {
            "status": "success",
            "test_run_id": str(test_run.id),
            "rule_code": canonical_code,
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

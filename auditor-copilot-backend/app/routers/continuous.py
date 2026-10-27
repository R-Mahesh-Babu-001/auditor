"""
Router for Continuous Auditing, recurring rule execution, and automated alert monitoring.
Stores scheduled rules in audit_test_rules with parameters JSONB in Neon PostgreSQL.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.db.session import get_db
from app.routers.auth import get_current_context, OrganizationContext
from app.models.tests import AuditTestRule, AuditTestRuleTemplate, AuditTestRun
from app.audit.execution import execute_audit_test

router = APIRouter(prefix="/continuous", tags=["Continuous Auditing"])


class ConfigureContinuousRuleRequest(BaseModel):
    engagement_id: Optional[uuid.UUID] = None
    template_id: uuid.UUID
    name: str
    frequency: str = "daily"  # daily, weekly, monthly, real_time
    cron_expression: Optional[str] = "0 0 * * *"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    alert_channel: Optional[str] = "dashboard"


class TriggerRunRequest(BaseModel):
    dataset_ids: Optional[List[uuid.UUID]] = None


@router.get("/rules")
def list_continuous_rules(
    engagement_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """List continuous monitoring configurations."""
    query = db.query(AuditTestRule).filter(
        AuditTestRule.organization_id == ctx.organization_id
    )
    eff_eng = engagement_id or ctx.engagement_id
    if eff_eng:
        query = query.filter(AuditTestRule.engagement_id == eff_eng)

    rules = query.all()
    results = []
    for r in rules:
        params = r.parameters or {}
        if params.get("continuous_enabled", True):
            tpl = db.query(AuditTestRuleTemplate).filter(AuditTestRuleTemplate.id == r.template_id).first()
            results.append({
                "id": str(r.id),
                "rule_code": r.rule_code,
                "name": r.name,
                "template_name": tpl.name if tpl else None,
                "domain": tpl.domain if tpl else "p2p",
                "frequency": params.get("frequency", "daily"),
                "cron_expression": params.get("cron_expression", "0 0 * * *"),
                "parameters": params,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

    return {"continuous_rules": results, "count": len(results)}


@router.post("/rules")
def create_continuous_rule(
    req: ConfigureContinuousRuleRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Enable or schedule a continuous audit rule monitoring job."""
    eff_eng = req.engagement_id or ctx.engagement_id
    if not eff_eng:
        raise HTTPException(status_code=400, detail="engagement_id is required")

    tpl = db.query(AuditTestRuleTemplate).filter(AuditTestRuleTemplate.id == req.template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Rule template not found")

    full_params = dict(req.parameters)
    full_params.update({
        "continuous_enabled": True,
        "frequency": req.frequency,
        "cron_expression": req.cron_expression,
        "alert_channel": req.alert_channel,
    })

    rule = AuditTestRule(
        organization_id=ctx.organization_id,
        engagement_id=eff_eng,
        template_id=tpl.id,
        rule_code=f"{tpl.template_code}_CONT_{uuid.uuid4().hex[:6].upper()}",
        name=req.name,
        version_number=1,
        parameters=full_params,
        status="active",
        created_by=ctx.user_id,
        approved_by=ctx.user_id,
        approved_at=datetime.utcnow(),
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    return {
        "message": "Continuous rule scheduled successfully",
        "rule": {
            "id": str(rule.id),
            "rule_code": rule.rule_code,
            "name": rule.name,
            "frequency": req.frequency,
            "status": rule.status,
        }
    }


@router.post("/rules/{rule_id}/trigger")
def trigger_continuous_evaluation(
    rule_id: uuid.UUID,
    req: TriggerRunRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Manually invoke a continuous audit rule check now."""
    rule = db.query(AuditTestRule).filter(
        AuditTestRule.id == rule_id,
        AuditTestRule.organization_id == ctx.organization_id,
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Continuous rule not found")

    tpl = db.query(AuditTestRuleTemplate).filter(AuditTestRuleTemplate.id == rule.template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Rule template not found")

    try:
        run = execute_audit_test(
            db=db,
            organization_id=ctx.organization_id,
            engagement_id=rule.engagement_id,
            template_code=tpl.template_code,
            rule_id=rule.id,
            parameters=rule.parameters,
            dataset_ids=req.dataset_ids,
            created_by_user_id=ctx.user_id,
        )
        return {
            "message": "Continuous rule executed successfully",
            "test_run_id": str(run.id),
            "records_tested": run.total_records_tested,
            "exceptions_found": run.exceptions_found,
            "status": run.status,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")


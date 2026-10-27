"""
Authentication and Organization context router for Audit Copilot.
Resolves actor identity, tenant organization, and user roles securely using JWT tokens.
Enforces multi-tenant isolation (401 unauthenticated, 403 unauthorized cross-tenant/role gates).
"""

import uuid
import jwt
from typing import Optional, Any, Dict
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.models.organization import (
    Organization,
    AppUser,
    OrganizationMembership,
    AuditEngagement,
)
from app.schemas import TokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication & Context"])


class OrganizationContext:
    """Context object representing the authenticated user and organization."""
    def __init__(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        engagement_id: Optional[uuid.UUID] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
    ):
        self.organization_id = organization_id
        self.user_id = user_id
        self.role = role
        self.engagement_id = engagement_id
        self.email = email
        self.full_name = full_name


DEFAULT_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEFAULT_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token with user, org, and role claims."""
    to_encode = data.copy()
    expire_minutes = getattr(settings, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 1440)
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=expire_minutes))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    secret_key = getattr(settings, "JWT_SECRET_KEY", "auditready-default-secret-key-change-in-production")
    algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify signature and expiration of JWT token, returning decoded payload."""
    secret_key = getattr(settings, "JWT_SECRET_KEY", "auditready-default-secret-key-change-in-production")
    algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Authentication token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")


def get_default_context(db: Session) -> tuple[Any, Any]:
    """Ensure default organization and auditor user exist for development/fallback."""
    try:
        org = db.query(Organization).filter(Organization.slug == "default-org").first()
        if not org:
            org = Organization(
                name="Default Enterprise Audit Org",
                slug="default-org",
                status="active",
                settings={"default_currency": "USD", "compliance_framework": "IIA_IPPF_COSO"},
            )
            db.add(org)
            db.flush()

        user = db.query(AppUser).filter(AppUser.email == "lead.auditor@enterprise.internal").first()
        if not user:
            user = AppUser(
                email="lead.auditor@enterprise.internal",
                full_name="Lead Internal Auditor",
                status="active",
                auth_provider="system",
            )
            db.add(user)
            db.flush()

        membership = db.query(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org.id,
            OrganizationMembership.user_id == user.id,
        ).first()
        if not membership:
            membership = OrganizationMembership(
                organization_id=org.id,
                user_id=user.id,
                role="audit_manager",
                status="active",
            )
            db.add(membership)
            db.commit()

        return org, user
    except Exception:
        class MockOrg:
            id = DEFAULT_ORG_ID
            name = "Default Enterprise Audit Org"
            slug = "default-org"

        class MockUser:
            id = DEFAULT_USER_ID
            email = "lead.auditor@enterprise.internal"
            full_name = "Lead Internal Auditor"

        return MockOrg(), MockUser()


def get_current_context(
    authorization: Optional[str] = Header(None),
    x_engagement_id: Optional[str] = Header(None, alias="X-Engagement-Id"),
    db: Session = Depends(get_db),
) -> OrganizationContext:
    """Authoritative context resolver for user identity, tenant, and engagement.

    Enforces Bearer JWT verification. In production or strict mode, rejects unauthenticated
    requests with HTTP 401. Rejects cross-tenant access with HTTP 403.
    """
    app_env = getattr(settings, "APP_ENV", "development").lower()
    is_testing = getattr(settings, "TESTING", False)

    # 1. Bearer Token Verification
    if authorization:
        parts = authorization.strip().split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid Authorization header format. Expected 'Bearer <token>'."
            )
        token = parts[1]
        payload = verify_access_token(token)

        user_id_str = payload.get("sub") or payload.get("user_id")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token payload missing subject identifier.")

        try:
            user_uuid = uuid.UUID(str(user_id_str))
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid user UUID in token.")

        user = db.query(AppUser).filter(AppUser.id == user_uuid).first()
        if not user or user.status != "active":
            raise HTTPException(status_code=401, detail="User account not found or inactive.")

        # Determine organization and role from membership
        token_org_id = payload.get("org_id") or payload.get("organization_id")
        membership_query = db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.status == "active",
        )
        if token_org_id:
            try:
                membership_query = membership_query.filter(
                    OrganizationMembership.organization_id == uuid.UUID(str(token_org_id))
                )
            except ValueError:
                pass

        membership = membership_query.first()
        if not membership:
            raise HTTPException(
                status_code=403,
                detail="User does not have an active membership in the designated organization."
            )

        org_id = membership.organization_id
        role = payload.get("role") or membership.role
        email = user.email
        full_name = user.full_name

    else:
        # No token provided
        if app_env == "production" or is_testing:
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Please provide a valid Bearer token."
            )

        # Development environment fallback only
        org, user = get_default_context(db)
        org_id = org.id
        user_uuid = user.id
        role = "audit_manager"
        try:
            membership = db.query(OrganizationMembership).filter(
                OrganizationMembership.organization_id == org.id,
                OrganizationMembership.user_id == user.id,
            ).first()
            if membership:
                role = membership.role
        except Exception:
            pass
        email = getattr(user, "email", "lead.auditor@enterprise.internal")
        full_name = getattr(user, "full_name", "Lead Internal Auditor")

    # 2. Engagement Context & Cross-Tenant Access Verification
    eff_eng_id: Optional[uuid.UUID] = None
    if x_engagement_id:
        try:
            requested_eng_uuid = uuid.UUID(x_engagement_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid X-Engagement-Id UUID format.")

        eng = db.query(AuditEngagement).filter(AuditEngagement.id == requested_eng_uuid).first()
        if not eng:
            raise HTTPException(status_code=404, detail="Requested engagement was not found.")

        # STRICT TENANT ISOLATION CHECK
        if eng.organization_id != org_id:
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Engagement belongs to another organization."
            )

        eff_eng_id = eng.id
    else:
        # Default to latest active engagement in user's organization if none specified
        try:
            eng = db.query(AuditEngagement).filter(
                AuditEngagement.organization_id == org_id,
                AuditEngagement.status == "in_progress",
            ).order_by(AuditEngagement.created_at.desc()).first()
            if eng:
                eff_eng_id = eng.id
        except Exception:
            pass

    return OrganizationContext(
        organization_id=org_id,
        user_id=user_uuid,
        role=role,
        engagement_id=eff_eng_id,
        email=email,
        full_name=full_name,
    )


def require_reviewer_role(context: OrganizationContext = Depends(get_current_context)) -> OrganizationContext:
    """Role gate requiring Manager, Reviewer, or Org Admin privileges (e.g. for sign-off/approval)."""
    allowed_roles = {"audit_manager", "reviewer", "admin", "org_admin", "lead_auditor"}
    if context.role.lower() not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden: Reviewer or Manager role required. Current role '{context.role}' cannot perform this action.",
        )
    return context


def require_admin_role(context: OrganizationContext = Depends(get_current_context)) -> OrganizationContext:
    """Role gate requiring Organization Administrator privileges."""
    allowed_roles = {"admin", "org_admin"}
    if context.role.lower() not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden: Administrator role required. Current role '{context.role}' cannot perform this action.",
        )
    return context


@router.post("/token", response_model=TokenResponse)
@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    req: TokenRequest,
    db: Session = Depends(get_db),
):
    """Authenticate auditor or manager and return a signed JWT access token."""
    email_clean = req.email.lower().strip()
    user = db.query(AppUser).filter(AppUser.email == email_clean).first()

    if not user:
        # In non-production, auto-create authorized user for seamless testing
        app_env = getattr(settings, "APP_ENV", "development").lower()
        if app_env != "production":
            org, _ = get_default_context(db)
            user = AppUser(
                email=email_clean,
                full_name=email_clean.split("@")[0].replace(".", " ").title(),
                status="active",
                auth_provider="local",
            )
            db.add(user)
            db.flush()

            # Determine role based on email or default to auditor
            assigned_role = "audit_manager" if "manager" in email_clean or "lead" in email_clean else "auditor"
            membership = OrganizationMembership(
                organization_id=org.id,
                user_id=user.id,
                role=assigned_role,
                status="active",
            )
            db.add(membership)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(status_code=401, detail="Invalid email or credentials.")

    if user.status != "active":
        raise HTTPException(status_code=401, detail="User account is deactivated.")

    # Retrieve user's active membership
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.status == "active",
    ).first()

    org_id = membership.organization_id if membership else DEFAULT_ORG_ID
    role = membership.role if membership else "auditor"

    expire_minutes = getattr(settings, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 1440)
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "org_id": str(org_id),
        "role": role,
    })

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expire_minutes * 60,
        user_id=str(user.id),
        email=user.email,
        role=role,
        organization_id=str(org_id),
    )


@router.get("/me")
def get_current_user_profile(
    context: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Return the verified user identity, tenant organization, and authorized roles."""
    org = db.query(Organization).filter(Organization.id == context.organization_id).first()
    org_name = org.name if org else "Default Enterprise Audit Org"

    return {
        "user_id": str(context.user_id),
        "email": context.email or "lead.auditor@enterprise.internal",
        "full_name": context.full_name or "Lead Internal Auditor",
        "organization_id": str(context.organization_id),
        "organization_name": org_name,
        "role": context.role,
        "engagement_id": str(context.engagement_id) if context.engagement_id else None,
    }

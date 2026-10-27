"""
Test Suite: Authentication and Authorization Security.
Verifies JWT Bearer token generation, verification, 401 unauthenticated,
403 cross-tenant isolation, role gates, and protection against client-supplied identity spoofing.
"""

import uuid
import unittest
from datetime import timedelta
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.routers.auth import (
    create_access_token,
    verify_access_token,
    get_current_context,
    require_reviewer_role,
    require_admin_role,
    OrganizationContext,
)
from app.models.organization import (
    AppUser,
    OrganizationMembership,
    AuditEngagement,
)


class TestAuthSecurity(unittest.TestCase):

    def setUp(self):
        self.user_id = uuid.uuid4()
        self.org_id = uuid.uuid4()
        self.eng_id = uuid.uuid4()

    def test_jwt_token_generation_and_verification(self):
        """Verify signed JWT token roundtrip preserves claims."""
        token = create_access_token({
            "sub": str(self.user_id),
            "email": "lead.auditor@enterprise.internal",
            "org_id": str(self.org_id),
            "role": "audit_manager",
        })
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 20)

        payload = verify_access_token(token)
        self.assertEqual(payload["sub"], str(self.user_id))
        self.assertEqual(payload["email"], "lead.auditor@enterprise.internal")
        self.assertEqual(payload["org_id"], str(self.org_id))
        self.assertEqual(payload["role"], "audit_manager")

    def test_expired_jwt_rejected_with_401(self):
        """Verify expired JWT tokens are rejected with HTTP 401."""
        expired_token = create_access_token(
            {"sub": str(self.user_id), "org_id": str(self.org_id)},
            expires_delta=timedelta(seconds=-10),
        )
        with self.assertRaises(HTTPException) as cm:
            verify_access_token(expired_token)
        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn("expired", cm.exception.detail.lower())

    def test_tampered_jwt_rejected_with_401(self):
        """Verify invalid or tampered JWT tokens are rejected with HTTP 401."""
        tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.bogus_signature"
        with self.assertRaises(HTTPException) as cm:
            verify_access_token(tampered_token)
        self.assertEqual(cm.exception.status_code, 401)

    def test_unauthenticated_request_rejected_in_production(self):
        """Verify missing authorization header in production environment is rejected with HTTP 401."""
        mock_db = MagicMock()
        with unittest.mock.patch("app.routers.auth.settings.APP_ENV", "production"):
            with self.assertRaises(HTTPException) as cm:
                get_current_context(authorization=None, x_engagement_id=None, db=mock_db)
            self.assertEqual(cm.exception.status_code, 401)
            self.assertIn("Authentication required", cm.exception.detail)

    def test_cross_tenant_engagement_access_blocked_with_403(self):
        """Verify accessing an engagement belonging to another tenant is blocked with HTTP 403."""
        mock_db = MagicMock()
        tenant_a_org_id = uuid.uuid4()
        tenant_b_org_id = uuid.uuid4()
        tenant_b_eng_id = uuid.uuid4()

        # Token belongs to Tenant A user
        token = create_access_token({
            "sub": str(self.user_id),
            "org_id": str(tenant_a_org_id),
            "role": "auditor",
        })

        # User in db
        mock_user = MagicMock(spec=AppUser)
        mock_user.id = self.user_id
        mock_user.status = "active"
        mock_user.email = "auditor_a@tenant-a.com"
        mock_user.full_name = "Auditor A"

        mock_membership = MagicMock(spec=OrganizationMembership)
        mock_membership.organization_id = tenant_a_org_id
        mock_membership.user_id = self.user_id
        mock_membership.role = "auditor"
        mock_membership.status = "active"

        # Requested engagement belongs to Tenant B!
        mock_eng_b = MagicMock(spec=AuditEngagement)
        mock_eng_b.id = tenant_b_eng_id
        mock_eng_b.organization_id = tenant_b_org_id

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == AppUser:
                mock_q.filter.return_value.first.return_value = mock_user
                return mock_q
            if model == OrganizationMembership:
                mock_q.filter.return_value.first.return_value = mock_membership
                return mock_q
            if model == AuditEngagement:
                mock_q.filter.return_value.first.return_value = mock_eng_b
                return mock_q
            mock_q.filter.return_value.first.return_value = None
            return mock_q

        mock_db.query.side_effect = query_side_effect

        with self.assertRaises(HTTPException) as cm:
            get_current_context(
                authorization=f"Bearer {token}",
                x_engagement_id=str(tenant_b_eng_id),
                db=mock_db,
            )

        self.assertEqual(cm.exception.status_code, 403)
        self.assertIn("another organization", cm.exception.detail.lower())

    def test_role_gate_reviewer_vs_auditor(self):
        """Verify that staff auditors cannot approve workpapers while managers/reviewers can."""
        auditor_ctx = OrganizationContext(
            organization_id=self.org_id,
            user_id=self.user_id,
            role="auditor",
        )
        with self.assertRaises(HTTPException) as cm:
            require_reviewer_role(auditor_ctx)
        self.assertEqual(cm.exception.status_code, 403)
        self.assertIn("Reviewer or Manager role required", cm.exception.detail)

        # Reviewer context succeeds
        reviewer_ctx = OrganizationContext(
            organization_id=self.org_id,
            user_id=self.user_id,
            role="audit_manager",
        )
        approved_ctx = require_reviewer_role(reviewer_ctx)
        self.assertEqual(approved_ctx.role, "audit_manager")


if __name__ == "__main__":
    unittest.main()


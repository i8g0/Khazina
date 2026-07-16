"""Role and organization permission dependency tests (Sprint 8.1)."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.permissions import require_org_role, require_role
from app.db.models.enums import UserRole


def _user(*, role: UserRole, organization_id: uuid.UUID | None = None) -> MagicMock:
    user = MagicMock()
    user.role = role.value
    user.organization_id = organization_id or uuid.uuid4()
    return user


def test_require_role_allows_equal_or_higher_rank() -> None:
    dependency = require_role(UserRole.EXECUTIVE)
    executive = _user(role=UserRole.EXECUTIVE)
    admin = _user(role=UserRole.ADMIN)

    assert dependency(executive) is executive
    assert dependency(admin) is admin


def test_require_role_rejects_lower_rank() -> None:
    dependency = require_role(UserRole.EXECUTIVE)
    analyst = _user(role=UserRole.ANALYST)

    with pytest.raises(HTTPException) as exc_info:
        dependency(analyst)

    assert exc_info.value.status_code == 403


def test_require_org_role_rejects_foreign_organization() -> None:
    org_id = uuid.uuid4()
    dependency = require_org_role(UserRole.ANALYST)
    outsider = _user(role=UserRole.ADMIN, organization_id=uuid.uuid4())

    with pytest.raises(HTTPException) as exc_info:
        dependency(org_id, outsider)

    assert exc_info.value.status_code == 403


def test_require_org_role_allows_member_with_sufficient_role() -> None:
    org_id = uuid.uuid4()
    dependency = require_org_role(UserRole.EXECUTIVE)
    member = _user(role=UserRole.EXECUTIVE, organization_id=org_id)

    assert dependency(org_id, member) is member


def test_require_role_rejects_invalid_role_value() -> None:
    dependency = require_role(UserRole.ANALYST)
    invalid = _user(role=UserRole.ANALYST)
    invalid.role = "superuser"

    with pytest.raises(HTTPException) as exc_info:
        dependency(invalid)

    assert exc_info.value.status_code == 403

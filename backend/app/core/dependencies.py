from collections.abc import Callable
from typing import Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status

from app.core.security import decode_access_token

ROLE_NAMES = {"super_admin", "org_admin", "staff", "medical_team", "patient_portal"}


async def get_current_user(request: Request) -> dict[str, Any]:
    claims = getattr(request.state, "token_claims", None)
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return claims


def require_roles(roles: list[str]) -> Callable:
    invalid_roles = set(roles) - ROLE_NAMES
    if invalid_roles:
        raise ValueError(f"Unknown role(s): {', '.join(sorted(invalid_roles))}")

    async def check_role(claims: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        if claims.get("role") not in roles and claims.get("role") != "super_admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return claims

    return check_role


def authenticated_user_id(claims: dict[str, Any]) -> UUID:
    try:
        return UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication claims") from exc

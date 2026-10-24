from uuid import UUID, uuid4

import pyotp
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field as PydanticField
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.core.dependencies import authenticated_user_id, get_current_user
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.models import Tenant, User

router = APIRouter()


class SignupRequest(BaseModel):
    tenant_name: str = PydanticField(min_length=2, max_length=200)
    full_name: str = PydanticField(min_length=1, max_length=200)
    email: EmailStr
    password: str = PydanticField(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    tenant_id: UUID
    email: EmailStr
    password: str
    totp_code: str | None = PydanticField(default=None, min_length=6, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: UUID
    tenant_name: str
    user_role: str
    user_name: str


class TotpVerifyRequest(BaseModel):
    code: str = PydanticField(min_length=6, max_length=8)


async def set_current_tenant(session: AsyncSession, tenant_id: UUID) -> None:
    await session.execute(
        text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )


async def create_user_session(request: Request, user: User) -> str:
    token = create_access_token(user_id=user.id, tenant_id=user.tenant_id, role=user.role)
    token_id = decode_access_token(token)["jti"]
    session_key = f"auth-session:{token_id}"
    redis = request.app.state.redis
    await redis.setex(
        session_key,
        settings.jwt_access_token_expire_minutes * 60,
        str(user.id),
    )
    return token


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: SignupRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    tenant_id = uuid4()
    await set_current_tenant(session, tenant_id)
    tenant = Tenant(tenant_id=tenant_id, name=body.tenant_name)
    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=body.email.lower(),
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role="org_admin",
    )
    session.add_all([tenant, user])
    await session.flush()
    return TokenResponse(
        access_token=await create_user_session(request, user),
        tenant_id=tenant_id,
        tenant_name=tenant.name,
        user_role=user.role,
        user_name=user.full_name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    await set_current_tenant(session, body.tenant_id)
    result = await session.execute(
        select(User).where(User.tenant_id == body.tenant_id, User.email == body.email.lower())
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.totp_enabled:
        if not body.totp_code or not user.totp_secret:
            raise HTTPException(status_code=401, detail="Two-factor code required")
        if not pyotp.TOTP(user.totp_secret).verify(body.totp_code, valid_window=1):
            raise HTTPException(status_code=401, detail="Invalid two-factor code")

    tenant_result = await session.execute(select(Tenant).where(Tenant.tenant_id == body.tenant_id))
    tenant = tenant_result.scalar_one()
    return TokenResponse(
        access_token=await create_user_session(request, user),
        tenant_id=user.tenant_id,
        tenant_name=tenant.name,
        user_role=user.role,
        user_name=user.full_name,
    )


@router.post("/2fa/setup")
async def setup_two_factor(
    claims: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    user_id = authenticated_user_id(claims)
    result = await session.execute(
        select(User).where(User.id == user_id, User.tenant_id == UUID(claims["tenant_id"]))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    secret = pyotp.random_base32()
    user.totp_secret = secret
    user.totp_enabled = False
    await session.flush()
    return {
        "secret": secret,
        "provisioning_uri": pyotp.TOTP(secret).provisioning_uri(
            name=user.email, issuer_name="AponCare"
        ),
    }


@router.post("/2fa/verify")
async def verify_two_factor(
    body: TotpVerifyRequest,
    claims: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, bool]:
    user_id = authenticated_user_id(claims)
    result = await session.execute(
        select(User).where(User.id == user_id, User.tenant_id == UUID(claims["tenant_id"]))
    )
    user = result.scalar_one_or_none()
    if user is None or not user.totp_secret:
        raise HTTPException(status_code=400, detail="Set up two-factor authentication first")
    if not pyotp.TOTP(user.totp_secret).verify(body.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid two-factor code")
    user.totp_enabled = True
    await session.flush()
    return {"enabled": True}


@router.post("/logout")
async def logout(
    request: Request,
    claims: dict = Depends(get_current_user),
) -> dict[str, bool]:
    token_id = claims.get("jti")
    if not token_id:
        raise HTTPException(status_code=401, detail="Invalid authentication claims")
    await request.app.state.redis.delete(f"auth-session:{token_id}")
    return {"logged_out": True}

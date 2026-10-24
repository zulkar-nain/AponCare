import logging
from collections.abc import AsyncIterator

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from jwt import InvalidTokenError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.security import decode_access_token

logger = logging.getLogger(__name__)
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class TenantSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        token = None
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ").strip()
        elif authorization:
            return JSONResponse({"detail": "Invalid authorization scheme"}, status_code=401)

        claims = None
        if token:
            try:
                claims = decode_access_token(token)
            except (InvalidTokenError, KeyError, ValueError) as exc:
                logger.info("Rejected invalid access token")
                return JSONResponse({"detail": "Invalid or expired access token"}, status_code=401)
            try:
                if not claims.get("jti") or not await request.app.state.redis.exists(
                    f"auth-session:{claims['jti']}"
                ):
                    return JSONResponse({"detail": "Session expired"}, status_code=401)
            except RedisError:
                logger.exception("Session store unavailable")
                return JSONResponse({"detail": "Authentication service unavailable"}, status_code=503)

        async with SessionFactory() as session:
            request.state.db_session = session
            request.state.token_claims = claims
            try:
                async with session.begin():
                    if claims:
                        await session.execute(
                            text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
                            {"tenant_id": claims["tenant_id"]},
                        )
                    response = await call_next(request)
                    if response.status_code >= 400:
                        await session.rollback()
                    return response
            except Exception:
                logger.exception("Request failed during tenant-scoped database transaction")
                raise
            finally:
                request.state.db_session = None


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    session = getattr(request.state, "db_session", None)
    if session is None:
        raise HTTPException(status_code=500, detail="Database request session unavailable")
    yield session

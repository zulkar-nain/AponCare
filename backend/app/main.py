import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from logtail import LogtailHandler
from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.api.v1 import auth, patients, prescriptions
from app.core.config import settings
from app.core.database import TenantSessionMiddleware, engine

logger = logging.getLogger("aponcare")
logger.setLevel(logging.INFO)
if settings.betterstack_source_token:
    logger.addHandler(
        LogtailHandler(
            source_token=settings.betterstack_source_token,
            host=settings.betterstack_ingesting_host,
        )
    )
else:
    logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(settings.redis_url, decode_responses=True, protocol=2)
    await redis.ping()
    app.state.redis = redis
    try:
        yield
    finally:
        await redis.aclose()
        await engine.dispose()


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.startswith("/api/v1/auth/"):
            redis: Redis = request.app.state.redis
            client_ip = request.client.host if request.client else "unknown"
            key = f"rate-limit:auth:{client_ip}"
            try:
                count = await redis.incr(key)
                if count == 1:
                    await redis.expire(key, 60)
            except RedisError:
                logger.exception("Authentication rate limiter unavailable")
                return JSONResponse(
                    {"detail": "Authentication service unavailable"}, status_code=503
                )
            if count > 20:
                return JSONResponse({"detail": "Too many authentication requests"}, status_code=429)
        return await call_next(request)


app = FastAPI(title="AponCare HMIS API", version="0.1.0", lifespan=lifespan)
app.add_middleware(TenantSessionMiddleware)
app.add_middleware(AuthRateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.info("Request validation failed for %s", request.url.path)
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error for %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(prescriptions.router, prefix="/api/v1/prescriptions", tags=["prescriptions"])

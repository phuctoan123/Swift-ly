"""FastAPI application entry point."""


import uuid, time, sys, logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.config import get_settings
from app.database import engine
from app.dependencies import close_redis_client, get_redis_client
from app.routers import health, urls, auth, analytics

settings = get_settings()

def setup_logging():
    log_level_num = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level_num,
    )
    
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.EventRenamer("message"),
    ]
    
    if settings.is_production:
        processors.append(structlog.processors.dict_tracebacks)
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level_num),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

setup_logging()
log = structlog.get_logger()

# ── Metrics ────────────────────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup và shutdown events."""
    # Startup
    log.info("app_starting", env=settings.app_env, version=settings.app_version)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        log.info("database_connected")
    except Exception as e:
        log.error("database_connection_failed", error=str(e))

    try:
        redis = await get_redis_client()
        await redis.ping()
        log.info("redis_connected")
    except Exception as e:
        log.warning("redis_connection_failed", error=str(e))

    yield

    # Shutdown
    log.info("app_shutting_down")
    await engine.dispose()
    await close_redis_client()
    log.info("app_stopped")


# ── App Instance ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="URL Shortener API",
    description=(
        "A high-performance URL shortener service. "
        "Shorten long URLs, track analytics, and manage your links."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next) -> Response:
    """
    Sinh X-Request-ID cho mỗi request và đo latency.
    Request ID được gắn vào response header và structured log.
    """
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    # Gắn request_id vào request state để dùng trong handlers
    request.state.request_id = request_id

    response: Response = await call_next(request)

    duration_s = time.perf_counter() - start_time
    duration_ms = duration_s * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

    # Update metrics
    endpoint = request.url.path
    if endpoint != "/metrics":
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration_s)

    log.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
        request_id=request_id,
    )

    return response


# ── Exception Handlers ─────────────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    # Pydantic v2 error ctx có thể chứa Exception objects — cần convert sang string
    serializable_errors = []
    for error in errors:
        err_copy = dict(error)
        if "ctx" in err_copy and isinstance(err_copy["ctx"], dict):
            err_copy["ctx"] = {
                k: str(v) if isinstance(v, Exception) else v
                for k, v in err_copy["ctx"].items()
            }
        # Convert tuple loc to list for JSON serialization
        err_copy["loc"] = list(err_copy.get("loc", []))
        serializable_errors.append(err_copy)

    first_error = serializable_errors[0] if serializable_errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", [])[1:])
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": first_error.get("msg", "Validation error"),
            "field": field or None,
            "details": serializable_errors,
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc) -> JSONResponse:
    log.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/v1", tags=["Health"])
app.include_router(auth.router)
app.include_router(urls.router, tags=["URLs"])
app.include_router(analytics.router)

@app.get("/metrics", tags=["Observability"])
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

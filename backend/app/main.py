from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.business.bootstrap import initialize_business_engines
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.middleware.request_logging import RequestLoggingMiddleware
from app.core.middleware.security_headers import SecurityHeadersMiddleware
from app.db.session import check_database_connection
from app.observability.health import check_system_health
from app.observability.structured_log import log_pipeline_event

logger = get_logger(__name__)

_DEMO_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    initialize_business_engines()
    health = check_system_health()
    log_pipeline_event(
        logger,
        "startup",
        status=health.status,
        message=f"database={health.database.status} ai={health.ai.status}",
    )
    try:
        check_database_connection()
    except Exception as exc:
        logger.warning("Database connectivity check failed at startup: %s", exc)
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_DEMO_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
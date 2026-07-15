from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.business.bootstrap import initialize_business_engines
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.middleware.security_headers import SecurityHeadersMiddleware

logger = get_logger(__name__)

_DEMO_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    initialize_business_engines()
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
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import settings

logger = structlog.get_logger()


def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("cpl_startup", app_env=settings.app_env, service="cpl")
    yield
    logger.info("cpl_shutdown", service="cpl")


app = FastAPI(
    title="Common Product Layer",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "cpl"}


@app.get("/ready")
async def ready():
    from app.db.engine import check_db_connection

    if check_db_connection():
        return {"application": "ready", "database": "reachable"}
    return JSONResponse(
        status_code=503,
        content={"application": "ready", "database": "unreachable"},
    )

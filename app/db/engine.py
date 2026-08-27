from contextlib import contextmanager

import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings

logger = structlog.get_logger()

engine = create_engine(
    str(settings.database_url),
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
    echo=settings.db_echo,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def transaction():
    """Transactional context manager: commit on success, rollback on exception."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
        logger.debug("transaction_committed")
    except Exception:
        session.rollback()
        logger.debug("transaction_rolled_back")
        raise
    finally:
        session.close()


@contextmanager
def session_scope():
    """Session scope where caller controls commit/rollback explicitly."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def check_db_connection() -> bool:
    """Check if PostgreSQL is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True
    except Exception as exc:
        logger.warning("database_connection_failed", error=str(exc))
        return False

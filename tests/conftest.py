import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# APP_ENV=test is only needed transiently here, to seed the app-wide
# Settings singleton (app.config.settings) at import time below. A regular
# pytest fixture can't run before a module-level import, so we use pytest's
# own MonkeyPatch class directly and undo it immediately after the import.
# This keeps the override scoped to the singleton's construction instead of
# leaking APP_ENV=test into the rest of the session (which previously broke
# tests/unit/test_config.py, since fresh Settings() calls there picked up
# the same ambient env var).
_env_patch = pytest.MonkeyPatch()
_env_patch.setenv("APP_ENV", "test")

from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402

_env_patch.undo()


@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)


@pytest.fixture(scope="session")
def db_engine():
    url = str(settings.database_url)
    engine = create_engine(url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

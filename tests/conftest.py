import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://test:test@localhost/test")

from app.db.base import Base
from app.main import app

# Import all models to register them in Base.metadata
from app.cpl.models.contact import Contact
from app.cpl.models.contact_point import ContactPoint
from app.cpl.models.account import Account
from app.cpl.models.asset import Asset
from app.cpl.models.asset_identifier import AssetIdentifier
from app.cpl.models.contact_asset_relationship import ContactAssetRelationship
from app.cpl.models.case import Case
from app.cpl.models.case_participant import CaseParticipant
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.case_event import CaseEvent
from app.cpl.models.asset_identity_resolution import AssetIdentityResolution
from app.cpl.models.external_reference import ExternalReference
from app.automotive.models.vehicle_detail import VehicleDetail

from app.db.engine import check_db_connection


@pytest.fixture(scope="session")
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def db_engine():
    from app.db.engine import engine
    return engine


@pytest.fixture(scope="session", autouse=True)
def migrate_db(db_engine):
    """Run Alembic migrations once per test session if PostgreSQL is available."""
    if check_db_connection():
        from alembic.config import Config
        from alembic import command
        with db_engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS cpl"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS automotive"))
            conn.commit()
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", str(db_engine.url))
        command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

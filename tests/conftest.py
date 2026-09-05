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
from app.cpl.models.identity_operation import IdentityOperation
from app.cpl.models.merge_proposal import MergeProposal
from app.cpl.models.contact_point_verification import ContactPointVerification
from app.cpl.models.contact_creation_request import ContactCreationRequest
from app.cpl.models.canonical_asset_identity_decision import CanonicalAssetIdentityDecision
from app.cpl.models.asset_merge_request import AssetMergeRequest
from app.cpl.models.canonical_relationship_decision import CanonicalRelationshipDecision
from app.cpl.models.relationship_mutation_request import RelationshipMutationRequest
from app.cpl.models.domain_projection import DomainProjection
from app.cpl.models.asset_creation_request import AssetCreationRequest
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


@pytest.fixture
def full_authority():
    """AuthorityContext holding every B3 authority class — used by tests
    that are not specifically exercising authority-denial behavior."""
    from app.cpl.identity.authority import Authority, AuthorityContext

    return AuthorityContext(
        granted=frozenset(
            {
                Authority.READ_IDENTITY,
                Authority.RESOLVE_IDENTITY,
                Authority.CREATE_CONTACT,
                Authority.MANAGE_CONTACT_POINT,
                Authority.VERIFY_CONTACT_POINT,
                Authority.ATTACH_ACCOUNT,
                Authority.MANAGE_ACCOUNT,
                Authority.ASSESS_DUPLICATE,
                Authority.PROPOSE_MERGE,
                Authority.AUTHORIZE_MERGE,
                Authority.EXECUTE_MERGE,
            }
        ),
        actor_reference="test-suite",
    )


@pytest.fixture
def full_b4_authority():
    """AuthorityContext holding every B4 Asset authority class."""
    from app.cpl.assets.authority import AssetAuthority
    from app.cpl.identity.authority import AuthorityContext

    return AuthorityContext(
        granted=frozenset(
            {
                AssetAuthority.READ_ASSET,
                AssetAuthority.CREATE_ASSET,
                AssetAuthority.MANAGE_ASSET_IDENTIFIER,
                AssetAuthority.CONSUME_IDENTITY_RESOLUTION,
                AssetAuthority.ADMIT_ASSET_MERGE,
                AssetAuthority.EXECUTE_ASSET_MERGE,
                AssetAuthority.CORRECT_ASSET_IDENTITY,
                AssetAuthority.MANAGE_RELATIONSHIP,
            }
        ),
        actor_reference="test-suite",
    )

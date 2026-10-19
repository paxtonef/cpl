import importlib
import os
import pytest

from alembic.config import Config
from alembic import command

from app.db.engine import check_db_connection


def test_migration_module_imports():
    for name in ["001_bootstrap", "002_create_contacts", "003_create_contact_points",
                 "004_create_accounts", "005_create_assets", "006_create_asset_identifiers",
                 "007_create_contact_asset_relationships", "008_create_vehicle_details",
                 "009_create_cases", "010_create_case_participants", "011_create_runner_executions",
                 "012_create_runner_artifacts", "013_create_case_events",
                 "014_create_asset_identity_resolutions", "015_create_external_references",
                 "016_add_current_state_pointers", "017_add_record_versions",
                 "018_add_indexes_and_hardening"]:
        mod = importlib.import_module(f"migrations.versions.{name}")
        assert hasattr(mod, "upgrade")
        assert hasattr(mod, "downgrade")


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_alembic_upgrade_head():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_alembic_current():
    alembic_cfg = Config("alembic.ini")
    command.current(alembic_cfg)


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_schemas_exist(db_engine):
    from sqlalchemy import inspect
    inspector = inspect(db_engine)
    schemas = inspector.get_schema_names()
    assert "cpl" in schemas
    assert "automotive" in schemas


def test_b6_migration_module_imports():
    """B6 forward migration (027) is importable and well-formed —
    added alongside, not replacing, the existing 001-018 check above."""
    mod = importlib.import_module("migrations.versions.027_create_b6_execution_artifact_governance")
    assert hasattr(mod, "upgrade")
    assert hasattr(mod, "downgrade")
    assert mod.revision == "027"
    assert mod.down_revision == "026"


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_migration_head_is_029():
    """Historical migrations remain unchanged; 029 is the current
    forward-only migration head."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    from alembic.script import ScriptDirectory
    script = ScriptDirectory.from_config(alembic_cfg)
    assert script.get_current_head() == "029"


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_029_owner_attested_unverified_freshness_state():
    """B2 source-veracity correction: the new state is accepted, the
    default no longer asserts verification, and an unsupported
    VERIFIED_CURRENT (verified_at NULL) is re-labelled by the migration."""
    from sqlalchemy import text
    from app.db.engine import engine
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    with engine.connect() as conn:
        chk = conn.execute(text(
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
            "WHERE conname = 'mfr_knowledge_documents_freshness_chk'"
        )).scalar()
        assert "OWNER_ATTESTED_UNVERIFIED" in chk
        default = conn.execute(text(
            "SELECT column_default FROM information_schema.columns "
            "WHERE table_schema='cpl' AND table_name='manufacturer_knowledge_documents' "
            "AND column_name='freshness_status'"
        )).scalar()
        assert "OWNER_ATTESTED_UNVERIFIED" in default

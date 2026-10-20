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
def test_migration_head_is_031():
    """Historical migrations remain unchanged; 031 (REQ-B5-116) is the
    current forward-only migration head."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    from alembic.script import ScriptDirectory
    script = ScriptDirectory.from_config(alembic_cfg)
    assert script.get_current_head() == "031"


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


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_030_identifier_redaction_schema_round_trip(db_engine):
    """030 adds only schema (REQ-B6-091): the redaction mark, the trace
    table and the widened decision type; down and up again cleanly while no
    artifact has been expurgated."""
    from sqlalchemy import inspect
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    inspector = inspect(db_engine)
    assert "redaction_status" in {c["name"] for c in inspector.get_columns("runner_artifacts", schema="cpl")}
    assert "runner_artifact_redactions" in inspector.get_table_names(schema="cpl")
    command.downgrade(alembic_cfg, "029")
    inspector = inspect(db_engine)
    assert "runner_artifact_redactions" not in inspector.get_table_names(schema="cpl")
    command.upgrade(alembic_cfg, "head")
    assert "runner_artifact_redactions" in inspect(db_engine).get_table_names(schema="cpl")


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_031_case_deletion_trace_schema_round_trip(db_engine):
    """031 adds only the trace table of REQ-B5-116 (no foreign key altered,
    no trigger); down and up again cleanly while no Case has been deleted."""
    from sqlalchemy import inspect, text
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    assert "case_deletions" in inspect(db_engine).get_table_names(schema="cpl")
    with db_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal")).scalar() == 0
    command.downgrade(alembic_cfg, "030")
    assert "case_deletions" not in inspect(db_engine).get_table_names(schema="cpl")
    command.upgrade(alembic_cfg, "head")
    assert "case_deletions" in inspect(db_engine).get_table_names(schema="cpl")

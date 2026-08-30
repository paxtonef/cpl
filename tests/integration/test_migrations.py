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

import importlib
import subprocess
import sys

from sqlalchemy import inspect

from app.db.engine import engine


def test_migration_bootstrap_imports():
    mod = importlib.import_module("migrations.versions.001_bootstrap")
    assert hasattr(mod, "upgrade")
    assert hasattr(mod, "downgrade")


def test_alembic_upgrade_head():
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Alembic upgrade failed: {result.stderr}"


def test_alembic_current():
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "current"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "001" in result.stdout, f"Expected revision 001, got: {result.stdout}"


def test_schemas_exist():
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    inspector = inspect(engine)
    schemas = inspector.get_schema_names()
    assert "cpl" in schemas
    assert "automotive" in schemas

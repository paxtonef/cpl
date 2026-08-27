import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.fixture
def isolated_settings(monkeypatch, tmp_path):
    """Force Settings() to ignore the real repo .env file (and any ambient
    APP_ENV from other fixtures/tests) so these tests observe only the env
    vars they explicitly set.

    Settings currently declares its config via the deprecated inner
    `class Config`, but pydantic-settings normalizes that into
    `Settings.model_config` (a plain dict) at class-definition time —
    mutating the inner `Config` class afterwards has no effect, since
    nothing reads it again at instantiation. `model_config` is therefore
    the actual live source of truth regardless of which syntax the source
    uses, so it's patched directly here. If app/config.py is migrated to
    `model_config = SettingsConfigDict(...)` directly, this fixture needs
    no changes — it already targets the right attribute.
    """
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.setitem(
        Settings.model_config, "env_file", str(tmp_path / "nonexistent.env")
    )


def test_settings_load_with_valid_database_url(monkeypatch, isolated_settings):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/cpl_test")
    s = Settings()
    assert s.app_env == "development"
    assert str(s.database_url).startswith("postgresql://")


def test_settings_validation_fails_without_database_url(monkeypatch, isolated_settings):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "database_url" in str(exc_info.value)

# LOG_DEPLOY.md — CPL (Common Product Layer) B1 Bootstrap

**Date:** 2026-08-27
**Skill:** devops-qa-deploy
**Environment:** Sandboxed Linux container (Ubuntu 24.04, Python 3.12.3)

## 1. Summary

FastAPI + PostgreSQL backend bootstrap (B1 phase). Exposes `/health` and
`/ready`, uses Alembic for schema migrations, SQLAlchemy 2.0 for
transactions, and structlog for JSON logging. Domain services (`app/cpl/*`,
`app/automotive/*`, `app/adapters/*`) are placeholders for later phases.

## 2. Secret Scan (Phase 1)

```
grep -rniE "(api[_-]?key|secret|password|token|aws_access|private_key)\s*=\s*['\"a-zA-Z0-9]{6,}" .
```
No real secrets found. Only placeholder credentials in `.env.example`
(`cpl_user` / `cpl_pass`), which are safe, non-production defaults intended
to be copied into a local `.env`.

## 3. Docker Decision

**Docker was planned but unavailable in this execution sandbox** (no Docker
daemon on the network-restricted container). PostgreSQL 16 was installed
directly via `apt-get install postgresql postgresql-contrib` instead,
started with `pg_ctlcluster 16 main start`, since `archive.ubuntu.com` /
`security.ubuntu.com` were reachable. This is a sandbox-specific
workaround; on a normal machine with Docker available, use:

```bash
docker run -d --name cpl-db -e POSTGRES_USER=cpl_user \
  -e POSTGRES_PASSWORD=cpl_pass -e POSTGRES_DB=cpl_db \
  -p 5432:5432 postgres:16
```

## 4. Environment Variables (`.env`)

| Variable | Meaning | Test value used | Impact if missing |
|---|---|---|---|
| `APP_ENV` | Deployment environment label | `development` | Cosmetic only (logging) |
| `LOG_LEVEL` | structlog level | `INFO` | Defaults to INFO |
| `DATABASE_URL` | PostgreSQL DSN | `postgresql://cpl_user:cpl_pass@localhost:5432/cpl_db` | App fails to start — `Settings()` raises `ValidationError` (required field) |
| `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` | SQLAlchemy pool sizing | `5` / `10` | Falls back to defaults |
| `DB_ECHO` | SQL echo logging | `false` | Falls back to `false` |
| `VIR_ENDPOINT`, `PGDR_ENDPOINT`, `VIR_TIMEOUT`, `PGDR_TIMEOUT` | Future runner adapters | unset | Unused in B1 |

No real secrets used — `cpl_pass` is a local-only, throwaway test password.

## 5. Bug Found & Fixed (Phase 6 — trivial, config-only)

**`pyproject.toml` — setuptools multi-package discovery failure.**
`pip install -e ".[dev]"` failed with *"Multiple top-level packages
discovered in a flat-layout: ['app', 'migrations']"*. Fixed by adding:
```toml
[tool.setuptools.packages.find]
include = ["app*", "migrations*"]
```
This is packaging metadata only — no application or business logic changed.

## 6. Bug Found & Fixed (Phase 6 — approved test-plumbing repair)

**`tests/conftest.py` / `tests/unit/test_config.py` — test isolation bug.**
A module-level `os.environ.setdefault("APP_ENV", "test")` in `conftest.py`
leaked `APP_ENV=test` for the whole session, and `Settings.Config.env_file
= ".env"` meant the "missing `DATABASE_URL` must raise" unit test could
never actually observe a missing value, since the real repo `.env` always
supplied one.

Fix (approved by user, scoped to test code only):
- Removed the module-level `os.environ.setdefault`; replaced with a
  `pytest.MonkeyPatch()` scoped tightly around the one import that needs
  it (the `app.config.settings` singleton construction), undone
  immediately after.
- Added an `isolated_settings` fixture in `tests/unit/test_config.py` that
  clears `APP_ENV` and patches `Settings.model_config["env_file"]` to a
  nonexistent path, so `Settings()` calls in that file only see env vars
  the test explicitly sets.
- **Note:** `app/config.py` currently declares config via the deprecated
  inner `class Config`. pydantic-settings normalizes that into
  `Settings.model_config` (a dict) at class-definition time — patching the
  inner `Config` class afterwards has no effect, only `model_config` does.
  Confirmed via `Settings.model_config`. If `app/config.py` is later
  migrated to `model_config = SettingsConfigDict(...)`, this fixture needs
  no changes, since it already targets `model_config` directly.

No application logic was changed — only `tests/conftest.py` and
`tests/unit/test_config.py`.

## 7. Test Results (Phase 5)

```
$ .venv/bin/pytest tests/ -v
======================== 16 passed, 3 warnings in 2.31s ========================
```
16/16 tests pass (2 unit, 14 integration) against a live PostgreSQL 16
instance with schemas `cpl` / `automotive` and the `pgcrypto` extension
created by `alembic upgrade head`.

## 8. Smoke Test (Phase 5)

Run within a single shell session (background processes are not preserved
across separate tool invocations in this sandbox):

```
GET /health          -> 200 {"status":"ok","service":"cpl"}
GET /ready (DB up)   -> 200 {"application":"ready","database":"reachable"}
GET /ready (DB down) -> 503 {"application":"ready","database":"unreachable"}
GET /ready (DB back) -> 200 {"application":"ready","database":"reachable"}
```
Exit code 0 for all checks.

## 9. install.sh Validation (Phase 7a)

```
$ bash install.sh /tmp/test-install
$ cd /tmp/test-install
$ .venv/bin/alembic upgrade head     # OK
$ .venv/bin/pytest tests/ -v         # 16 passed
```
Validated end-to-end into a clean directory, exit code 0.

## 10. Launch Command

```bash
bash install.sh ~/cpl
# ensure PostgreSQL is running with cpl_user/cpl_pass/cpl_db (see install.sh output)
cd ~/cpl
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
```

## 11. Known Limitations

- No Docker available in this execution sandbox; PostgreSQL was installed
  directly via apt instead. `install.sh` assumes a reachable PostgreSQL —
  it does not bundle or start one.
- Async DB access, RBAC, and runner adapter implementations are
  deliberately out of scope for B1 (per `B1_IMPLEMENTATION_REPORT.md`).
- `app/config.py` still triggers a `PydanticDeprecatedSince20` warning for
  using the inner `class Config` — not fixed here since it's application
  code and wasn't part of the approved scope.

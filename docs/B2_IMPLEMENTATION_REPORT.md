# B2 Implementation Report

## Repository
- Branch: main
- Starting B1 baseline: B1 closed
- B2 adds: M002–M018 migrations + 14 SQLAlchemy models + P01–P20/N01–N24 tests

## Repair R1 (2026-08-28)
- **M016**: Removed duplicate `add_column` for `vehicle_details.source_resolution_id` (column already created in M008). FK constraint creation preserved. Downgrade synchronized.
- **pyproject.toml**: Restored `[tool.setuptools.packages.find]` with `include = ["app*", "migrations*"]` (B1 packaging regression).
- **G-B2-07**: Corrected from PASS to UNPROVEN (was not execution-demonstrated).

## Migrations Created
| Migration | Content |
|-----------|---------|
| 001 | pgcrypto + cpl + automotive schemas (B1 preserved) |
| 002 | cpl.contacts + constraints + indexes |
| 003 | cpl.contact_points + partial unique (active primary) |
| 004 | cpl.accounts + provider identity unique |
| 005 | cpl.assets (without current pointer) |
| 006 | cpl.asset_identifiers + confidence/validity checks |
| 007 | cpl.contact_asset_relationships + partial unique (active) |
| 008 | automotive.vehicle_details |
| 009 | cpl.cases (without current pointer) |
| 010 | cpl.case_participants + partial unique (active role) |
| 011 | cpl.runner_executions + idempotency partial unique |
| 012 | cpl.runner_artifacts + hash pair check |
| 013 | cpl.case_events |
| 014 | cpl.asset_identity_resolutions |
| 015 | cpl.external_references |
| 016 | current-state pointers (assets, cases) + vehicle_details FK only |
| 017 | record_version (BigInteger) on contacts, assets, relationships, cases |
| 018 | consolidation / no-op |

## Tables Created
cpl.contacts, cpl.contact_points, cpl.accounts, cpl.assets, cpl.asset_identifiers,
cpl.contact_asset_relationships, cpl.cases, cpl.case_participants,
cpl.runner_executions, cpl.runner_artifacts, cpl.case_events,
cpl.asset_identity_resolutions, cpl.external_references,
automotive.vehicle_details

## Constraints Created
- CHECK: contact_type, contact_status, self-merge, merged target
- CHECK: point_type, verification_status, validity
- CHECK: account_status
- CHECK: asset_status
- CHECK: identifier_status, confidence range, validity
- CHECK: relationship_status, validity
- CHECK: case_status, closed_at required
- CHECK: participant_status, time order
- CHECK: execution_status, self-parent, time order, completed_at required
- CHECK: artifact_status, self-supersession, hash pair coherence
- CHECK: resolution_status, confidence range, self-supersession
- UNIQUE: (auth_provider, provider_subject_id)
- UNIQUE: (reference_system, reference_type, reference_value)
- Partial UNIQUE: one active primary point per type
- Partial UNIQUE: one active relationship per contact/asset/type
- Partial UNIQUE: one active participant per case/contact/role
- Partial UNIQUE: runner_type + idempotency_key

## Indexes Created
All operational indexes from DDL spec distributed across M002–M014 + M016.

## B1 Regression
- test_config.py: preserved
- test_health.py: preserved
- test_db.py: adapted to avoid Base.metadata.create_all (circular FKs)
- test_transactions.py: preserved
- /health, /ready semantics: unchanged

## Warnings
- OBS-B1-01/02/03: carried forward, not repaired

## Deviations
- None

## Blockers
- **BLOCKER-01**: ENVIRONMENT_BLOCKER — PostgreSQL server unavailable in current sandbox. All DB-dependent verification remains BLOCKED until execution in a PostgreSQL 14+ environment.

## Traceability
Every B2 requirement maps to a migration file and a test function.

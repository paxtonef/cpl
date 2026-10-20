# B6 amendment — REQ-B6-091: governed expurgation of vehicle identifiers

Date: 2026-10-20. Branch `cpl-conservation-plaque` (from `cpl-source-veracity-029` @ `bc09253`).
Migration `030`. Code: `app/cpl/runners/redaction.py`, operator command `app/cpl/runners/redaction_command.py`.
Tests: `tests/integration/test_b6_redaction.py`, `tests/integration/test_migrations.py`.

The frozen requirement object (`B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1.md`, frozen commit `855f3c7`) is not
edited. This amendment adds one named requirement and states, for each of REQ-B6-053 to 059, the narrow exception
it opens. Every other artifact, and every other field of an eligible artifact, keeps the frozen requirements
unchanged.

## REQ-B6-091 — Expurgation of vehicle identifiers from `vir_resolution` artifacts

`CORRECTION / RETENTION` | Authority: CPL (governed operation), operator | Object: RunnerArtifact

**Statement.** CPL SHALL provide exactly one code path, `redact_artifact_identifiers`, that removes the vehicle
identifiers (plate `identifiers.registration_number`, VIN `identifiers.vin`) from the payload of an artifact whose
`artifact_type` and `schema_name` are both `vir_resolution`. It SHALL:

1. remove only those identifiers, at the locations of VIR's `VehicleIdentityResolution` schema listed in the module
   docstring (retained identity, alternative and set-aside candidates, field evidence and their sources,
   contradictions, clarification choices, provenance of a set-aside candidate, and the raw provider field documented
   as carrying a VIN); each value becomes null, every structure, field path, source, method, contradiction, internal
   reference and the registration country stay;
2. keep the artifact row, its `artifact_id`, `execution_id`, `artifact_status`, classification and
   `supersedes_artifact_id`;
3. set `redaction_status = 'REDACTED'`;
4. keep the registration-time hash as a historical trace (`runner_artifact_redactions.original_content_hash`) and
   recompute `content_hash` over the payload as persisted;
5. record a governed decision `ARTIFACT_REDACTION` and one `runner_artifact_redactions` row: date, operation
   (`VEHICLE_IDENTIFIER_REDACTION`), operation id, reason (closed list: `RETENTION_POLICY`,
   `DATA_SUBJECT_REQUEST`), opaque operator reference, removed locations by name — never a removed value, never a
   copy of the removed content;
6. be idempotent (an artifact already expurgated, or holding no identifier, is left as it is: no new decision, no
   new record);
7. treat in the same operation every artifact linked by supersession, in either direction, so that no older or
   newer version keeps the values; all or nothing;
8. refuse (CONFLICT, nothing written) an artifact whose content no longer matches its hash, or whose mark and record
   disagree: an unauthorized alteration is never laundered by an expurgation.

The integrity check (`classify_integrity`, `audit_integrity`) SHALL distinguish `ORIGINAL_INTACT` (no mark, no
record, hash matches), `REDACTED_AUTHORIZED` (mark, record, hash matches the recorded remaining-content hash, no
identifier left) and `UNAUTHORIZED_ALTERATION` (anything else), besides `NO_HASH_RECORDED`.

The operator command simulates by default (no write without `--executer`), prints counts and artifact identifiers
only, and decides no period (`--avant` is a date given by the operator).

**Out of scope.** No per-record encryption, no new key system, no decided retention period, no expurgation of real
data by this change, no trigger, no other artifact type. The product removes the identifiers before registering a
new `vir_resolution` artifact, with the same function (PI `cpl_registration._persist_vir_resolution`).

**Verification.** INTEGRATION TEST (`test_b6_redaction.py`): every location emptied and everything else kept;
idempotence; chain of three versions; the three integrity classes with failure injection; authority, reason and
operator checks; command in simulation then execution. Migration round trip (`test_migrations.py`).

## Exceptions opened in REQ-B6-053 to 059

| Requirement | Unchanged for every other artifact | Exception, for a `vir_resolution` artifact expurgated under REQ-B6-091 only |
|---|---|---|
| REQ-B6-053 (hash required inline) | yes | still hashed: the hash pair is recomputed, never left empty |
| REQ-B6-054 (what is hashed) | yes | `content_hash` is over the payload as persisted after expurgation; the registration hash survives only as the trace `original_content_hash` |
| REQ-B6-055 (mismatch flagged) | yes | a mismatch with the remaining-content hash is `UNAUTHORIZED_ALTERATION`; an expurgation never corrects a mismatch (refused) |
| REQ-B6-056 (hash ≠ truth) | yes | unchanged: neither hash says anything about domain validity |
| REQ-B6-057 (supersession relation canonical) | yes | unchanged: no link or status is set or changed; consistency query still empty |
| REQ-B6-058 (row retained in full) | yes | the row is retained; its payload loses the identifiers only — the one content change permitted outside supersession |
| REQ-B6-059 (correction categories distinguished) | yes | a fourth audit category, `ARTIFACT_REDACTION`, distinct from metadata and content correction; never a domain correction (REQ-B6-060 unchanged) |

REQ-B6-060 and REQ-B6-061 are unchanged: the expurgation corrects no domain assertion, and it is preceded by a
governed decision in the same transaction.

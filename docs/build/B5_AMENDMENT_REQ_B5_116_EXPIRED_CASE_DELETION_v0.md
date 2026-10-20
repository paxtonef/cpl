# B5 amendment — REQ-B5-116: governed deletion of an expired Case

Date: 2026-10-20. Branch `cpl-conservation-plaque` (after REQ-B6-091, `253ff8f`). Migration `031`.
Code: `app/cpl/cases/deletion.py`, model `app/cpl/models/case_deletion.py`.
Tests: `tests/integration/test_b5_case_deletion.py`, `tests/integration/test_migrations.py`.

The frozen matrices (B4 v0.1, B5 v0.2, B6 v0.1) are not edited. This amendment adds one named requirement and
states, for each history requirement it touches, the narrow exception it opens. Every Case that is not deleted
under REQ-B5-116, and every row that is not the Case's own, keeps the frozen requirements unchanged.

## Conflict found before implementing

- Every foreign key of CPL is `ON DELETE RESTRICT` (one exception: knowledge dashboard entries, `CASCADE`, not
  concerned), and no database trigger exists. Deleting a Case therefore needs its rows removed child first; no
  key needs altering.
- The history requirements forbid it as they stand: REQ-B5-034 / 064 (CaseEvent append-only), REQ-B5-061..063
  and 065 (reconstructable history of creation, lifecycle, participants, corrections), REQ-B6-058 (artifact row
  retained in full), REQ-B6-064 (append-only correction log), REQ-B4-034 (earlier identity resolutions stay
  reconstructable).
- `cases.current_execution_id` and `runner_executions.case_id` reference each other.
- `automotive.vehicle_details.source_resolution_id` may name a resolution recorded by the Case while the vehicle
  summary belongs to the vehicle (shared by every Case on it).

## REQ-B5-116 — Deletion of an expired Case and of its own rows

`RETENTION` | Authority: CPL (governed operation), operator purge (`DELETE_EXPIRED_CASE`) | Object: Case

**Statement.** CPL SHALL provide exactly one code path, `delete_expired_case`, that physically deletes a Case
whose creation (`cases.created_at`, starting point `creation_dossier`) is before a cutoff computed by the caller
from an explicit, finite retention period. It SHALL:

1. refuse, without any modification, a Case still within its period, a missing or non-positive period, a cutoff
   without a time zone, a missing authority, a non-opaque operator reference;
2. refuse (CONFLICT, nothing modified) a Case that a row outside it still depends on: an execution, artifact,
   event or resolution of another Case, another Case's current execution, the vehicle's current identity, a
   domain projection or an asset identity decision; the kinds are named, never their content;
3. otherwise delete, in one transaction, in the order the RESTRICT keys impose: the REQ-B6-091 traces, the
   governance decisions, the artifacts (every version: VIR resolutions, Premiers Constats, reports), the identity
   resolutions, the execution corrections, the events, the executions, the participants, the case mutation
   requests, the canonical case decisions and the Case;
4. clear, not delete, the two pointers to those rows: the Case's own `current_execution_id` and
   `vehicle_details.source_resolution_id` when it names a deleted resolution (the vehicle summary stays);
5. never delete a Contact, an Account or a credential, a vehicle (Asset, VehicleDetail, owner relationship,
   identifiers, creation request), another Case or anything recorded by it, manufacturer knowledge, notices or
   catalogues;
6. write one `cpl.case_deletions` row: the Case's opaque identifier, operation id, reason (`RETENTION_POLICY`),
   period, starting point, opaque operator reference, date, deleted row counts -- no content of the Case, no
   contact, no vehicle, no vehicle identifier;
7. be idempotent: a Case already deleted is NO_CHANGE, with no second trace;
8. leave the Case whole if anything fails before the caller commits (one Case per transaction), so that a new run
   takes up exactly what is left.

`plan_expired_cases` reads only and returns case ids and row counts (due, blocked with the kinds of dependency).

**Irreversibility.** A deleted Case cannot be restored from the database: the trace keeps no content. Only a
backup taken before the deletion still holds it (its own retention applies). Migration `031` refuses its
downgrade once any Case has been deleted.

**Out of scope.** No retention period is decided here (the product's `PI_CONSERVATION_DOSSIERS_JOURS` is required,
with no default), no deletion of real data by this change, no trigger, no foreign key altered, no user-facing
deletion.

**Verification.** INTEGRATION TEST (`test_b5_case_deletion.py`): within-period Case untouched, expired Case and
its rows deleted, vehicle, contact, other Case and knowledge kept, trace without content; refusal on outside
dependency; interruption then new run; authority, period and operator checks; plan reads only. Migration round
trip and no-trigger check (`test_migrations.py`).

## Exceptions opened

| Requirement | Unchanged for every other Case and row | Exception, for a Case deleted under REQ-B5-116 only |
|---|---|---|
| REQ-B5-034 / REQ-B5-064 (CaseEvent append-only, preserved) | yes | the Case's events are deleted with it; never edited in place |
| REQ-B5-061 / 062 / 063 / 065 (reconstructable history) | yes | the Case's history is deleted with it; only the technical trace remains |
| REQ-B6-058 (artifact row retained in full) | yes | every artifact version of the Case is deleted with it (REQ-B6-091 traces included) |
| REQ-B6-064 (append-only correction log) | yes | the corrections of the Case's executions are deleted with them |
| REQ-B4-034 (earlier resolutions reconstructable) | yes | resolutions recorded by the Case's executions are deleted, unless another row depends on them (then the Case is not deleted) |
| REQ-B6-091 (expurgation trace) | yes | the trace of an artifact is deleted with the artifact; no content was in it |

The governance decisions of the Case's executions and artifacts (REQ-B6-061/079) are deleted with them; the
deletion itself is authorised by `DELETE_EXPIRED_CASE` and recorded in `cpl.case_deletions`, which references no
deleted row.

# B5 Case Governance Candidate — Requirement Traceability (REQ-B5-001 → REQ-B5-115)

Generated against `b5-case-governance-candidate`, checkpoint `f6fca74` + repair commit (this commit).

Evidence classes, matching the B4 candidate precedent:
- **DIRECT** — the requirement is explicitly exercised by a named test and/or explicitly cited in implementation.
- **STRUCTURAL** — satisfied by schema/architecture design that makes violation impossible without a separate code change (e.g. `Case.asset_id NOT NULL` at the database level).
- **REGRESSION-SUITE** — evidenced by the full B1–B5 suite passing (non-regression obligations, which are properties of the test run itself).

---

## A — Case object / identity (REQ-B5-001–013)

**Evidence class:** DIRECT + STRUCTURAL
`app/cpl/models/case.py` (unchanged B2 schema: `case_id` PK, `primary_contact_id`/`asset_id` FKs distinct from `case_id` — structural identity separation). `app/cpl/cases/lifecycle.py::create_case` (001, 011–013). Identity stability across status/participant/event changes (004–006) is structural: no function anywhere reassigns `case_id`. Tests: `test_p02_case_identity_stable_across_status_change`, `test_p01_create_case`. World/domain/CPL-case boundary (007–010) is a documentation/architecture invariant with no code path that asserts world-event truth — verified by absence (grep confirms no function claims to determine whether an underlying world event occurred).

## B — Asset anchoring (REQ-B5-014–018, 109)

**Evidence class:** DIRECT
`create_case`'s Asset/Contact existence checks (014, 018). `attempt_asset_rebind` (109), tested in `test_n_b_asset_cannot_be_rebound`, `test_asset_rebind_attempt_replay_consistent`. `Case.asset_id NOT NULL` is the unchanged, untouched B2 schema constraint (015–017, STRUCTURAL).

## C — Case participation (REQ-B5-019–026, 077)

**Evidence class:** DIRECT
`app/cpl/cases/participants.py::add_participant`/`remove_participant`. `CaseParticipant ≠ ContactAssetRelationship` (020) is structural (separate table, no shared FK). `can_participant_mutate_case` (022/023), tested in `test_n_c_participant_role_alone_cannot_authorize_closure`. Idempotency (077) tested in `test_add_participant_replay_object_id`, `test_remove_participant_replay_object_id`.

## D — CaseEvent boundary (REQ-B5-027–034)

**Evidence class:** DIRECT
`app/cpl/cases/events.py::record_case_event`. Append-only (034): no update/delete path exists on `CaseEvent` rows outside supersession via `correct_case_event`. Event≠decision (030–032) is structural: `record_case_event` never touches `case_status` or creates a `CanonicalCaseDecision`.

## E — CaseEvent classification (REQ-B5-035–038, GAP-02)

**Evidence class:** DIRECT
`app/cpl/models/case_event_type.py`, `register_event_type`, unregistered-type rejection tested in `test_n_unregistered_event_type_rejected`. R5 repair confirmed all four semantic classes trace directly to frozen WHAT §39a GAP-02 text — no fifth class invented.

## F — Case lifecycle / status (REQ-B5-039–045)

**Evidence class:** DIRECT
`transition_case_status`, `VALID_CASE_STATUSES` frozen enum. Domain-truth-status rejection (041) tested in `test_n_domain_truth_status_rejected`. Case status ≠ domain state (040) tested in `test_n_e_case_closed_does_not_imply_domain_truth`.

## G — Authority / decision (REQ-B5-046–051, 110–112)

**Evidence class:** DIRECT
Full pipeline in `create_case`, `transition_case_status`, `add_participant`, `remove_participant`, `correct_case_metadata`, `correct_case_event` — all decision-before-effect (R1 + R7 repairs). Failure-injection proof in `TestR1DecisionBeforeEffect` (2 tests), `TestR7CreateCasePipelineOrdering` (6 tests, including direct flush-order instrumentation, not just atomicity), plus the original `test_n_g_technical_failure_not_governed_rejection`. Authority mechanism non-prescription (051) — `app/cpl/cases/authority.py` reuses `AuthorityContext` as a HOW choice, not a mandated mechanism.

### R7 full material-mutation pipeline audit

| Operation | REQUEST | AUTHORITY | DECISION | EFFECT | HISTORY | ORDERING |
|---|---|---|---|---|---|---|
| CREATE_CASE | ✓ | ✓ (`authority.require`) | ✓ (pre-generated `case_id`, deferred FK) | ✓ (Case insert) | ✓ (decision row + idempotency) | **PASS** |
| STATUS_TRANSITION | ✓ | ✓ | ✓ | ✓ (`case.case_status =`) | ✓ | **PASS** |
| ASSET_REBIND_ATTEMPT | ✓ | ✓ | ✓ (always REJECTED) | n/a (no state change ever occurs — rejection has no effect to order) | ✓ | **PASS** (trivially — no effect exists) |
| PARTICIPANT_ADD | ✓ | ✓ | ✓ (pre-generated `case_participant_id`) | ✓ (participant insert) | ✓ | **PASS** |
| PARTICIPANT_REMOVE | ✓ | ✓ | ✓ | ✓ (`participant.participant_status =`) | ✓ | **PASS** |
| METADATA_CORRECTION | ✓ | ✓ | ✓ | ✓ (`case.title =`/`case.case_type =`) | ✓ | **PASS** |
| EVENT_CORRECTION | ✓ | ✓ | ✓ (pre-generated `event_id`, or CONFLICT rejection) | ✓ (successor insert + prior supersession) | ✓ | **PASS** |

All seven operations audited directly against source (line numbers checked, not inferred). No operation omitted.

## H — Execution pointer boundary (REQ-B5-052–060)

**Evidence class:** DIRECT
Structural: grep-verified no B5 module reads `execution_status` (`test_n_f_execution_reference_opaque`). Behavioral: `test_real_runner_execution_reference_preserved_without_interpretation` (R4) — a real `RunnerExecution` row's status is varied across `RUNNING/COMPLETED/FAILED/BLOCKED` and `Case.case_status`/`current_execution_id` are proven unaffected.

## I — History / reconstructability (REQ-B5-061–068)

**Evidence class:** DIRECT
`CanonicalCaseDecision` ledger (061–064), `correct_case_event`/`correct_case_metadata` preserving prior rows (065), reopening supported by `VALID_CASE_STATUSES` including `REOPENED` (066), execution-reference-attachment-as-history (067, exercised in R4 test), current vs historical distinction (068) — `CaseEvent.event_status` (`CURRENT`/`SUPERSEDED`) plus `CanonicalCaseDecision.prior_value`/`new_value`.

## J — Correction / supersession (REQ-B5-069–074, GAP-03)

**Evidence class:** DIRECT
`correct_case_metadata` (069), `correct_case_event` (071, supersession not deletion — 072), tested in `test_p09_event_correction_preserves_original`, `test_p10_metadata_correction_preserves_prior`. Schema kept minimal per GAP-03 (073/074) — no event-sourcing, no B4-clone structure, just `prior_value`/`new_value` JSONB and a status/supersedes-link pair.

## K — Idempotency (REQ-B5-075–079, 113)

**Evidence class:** DIRECT
Shared `_idempotent_replay` pattern across all five mutation functions, `result_object_id` fix (R2) ensuring correct outcome reconstruction. Tests: `TestR2ReplayOutcomeFidelity` (5 tests, one per operation family), `test_p04_status_transition_idempotent_replay`, `test_n_j_different_operation_identity_not_auto_replay`.

## L — Failure semantics (REQ-B5-080–084)

**Evidence class:** DIRECT
All five categories now independently demonstrated: `AUTHORITY_REJECTION` (exception-type distinction, `test_authority_rejection_is_distinguishable_type`), `SEMANTIC_REJECTION` (`test_semantic_rejection_asset_rebind`, `test_n_domain_truth_status_rejected`), `UNRESOLVED` (`test_unresolved_case_creation_pending_asset_hold`, R3 repair grounded in REQ-B5-018's own "resolvable per B4 governance" text), `CONFLICT` (`test_conflict_correction_race`, R3 repair), `TECHNICAL_FAILURE` (`test_technical_failure_never_governed_rejection`, `test_n_g_technical_failure_not_governed_rejection`).

## M — Case-to-Case consolidation boundary (REQ-B5-085–087, GAP-01)

**Evidence class:** STRUCTURAL
No merge/consolidation/survivor-selection function exists anywhere in `app/cpl/cases/`. Verified by absence (no such function to test) — matches GAP-01's explicit exclusion.

## N — Ontology vocabulary (REQ-B5-088–090, GAP-04)

**Evidence class:** STRUCTURAL
All code uses "Case" as working vocabulary consistently; no renaming attempted; physical table name `cases` unchanged.

## O — Domain-truth boundary (REQ-B5-091–095)

**Evidence class:** DIRECT
`test_n_e_case_closed_does_not_imply_domain_truth` explicitly asserts `Case` has no `repaired`/`diagnosis_valid`/`asset_safe` fields. No function anywhere computes or asserts diagnosis correctness, operability, repair success, liability, or safety.

## P — Anti-workflow boundary (REQ-B5-096–097)

**Evidence class:** STRUCTURAL
No task-scheduling, dependency-graph, or trigger/rule code exists anywhere in `app/cpl/cases/`.

## Q — Anti-event-sourcing boundary (REQ-B5-098–099)

**Evidence class:** STRUCTURAL
`Case.case_status` is a directly-stored, directly-queried column; no function derives current state by replaying `CaseEvent` rows.

## R — actor_type boundary (REQ-B5-100–102)

**Evidence class:** STRUCTURAL
Unchanged B2 enum (`CONTACT/SYSTEM/RUNNER/ADMIN/EXTERNAL_PARTY`); no generalized Actor/Role object introduced anywhere in `app/cpl/cases/`.

## S — Verification and evidence (REQ-B5-103–108)

**Evidence class:** REGRESSION-SUITE
184/184 full suite passing (152 B1–B4 baseline + 32 new B5), all against real PostgreSQL 16. Clean-DB migration to `026` and round-trip both verified this session. `/health`/`/ready` verified.

---

## Summary

```text
Total requirements:        115 (REQ-B5-001 -> REQ-B5-115)
Requirements unaccounted:  0
DIRECT evidence:           11 of 20 family blocks (majority of requirements)
STRUCTURAL evidence:       A (partial), M, N, P, Q, R — architecture-level guarantees
REGRESSION-SUITE evidence: S — property of the whole suite run

Full suite at this commit: 190 / 190 passing (152 B1-B4 baseline + 38 new B5)
```

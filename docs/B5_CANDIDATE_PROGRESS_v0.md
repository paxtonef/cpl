# B5 Case Governance Candidate — Final Report

**Status: CANDIDATE_COMPLETE.**

- Repository: `paxtonef/cpl`
- Mandated code baseline: `1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628` (verified ancestor; branch created exactly there)
- Migration head: `026`
- Full regression: **184 / 184 passing** (152 B1–B4 baseline + 32 new B5) against real PostgreSQL 16
- Clean-DB install from scratch to `026`: verified twice (checkpoint + final)
- Migration round-trip (`025→026→025→026`): verified
- `/health`, `/ready`: verified

## Bounded repair applied to the WIP checkpoint (`f6fca74`)

Per the WIP checkpoint repair instruction, two genuine implementation defects were found and fixed, three items closed with dedicated evidence, and one item confirmed already correct:

- **R1 (decision-before-effect ordering)** — `add_participant`, `remove_participant`, `correct_case_metadata`, `correct_case_event` all performed the governed effect *before* recording the `CanonicalCaseDecision`, relying on transactional rollback rather than genuine pipeline ordering. Fixed: decision is now recorded first in all four functions (with PKs pre-generated in Python where the effect creates a new row, so the decision can reference the real object identity before that row exists). Proven under actual injected `IntegrityError` failures (`TestR1DecisionBeforeEffect`, 2 tests) — no decision survives without its effect, and no effect appears without its decision.
- **R2 (idempotent replay outcome fidelity)** — the idempotency ledger only stored `decision_id`, so replay always reconstructed `object_id = decision.case_id`, which is wrong for `PARTICIPANT_ADD`/`REMOVE` (should be `case_participant_id`) and `EVENT_CORRECTION` (should be the successor `event_id`). Fixed: added `result_object_id` to `CanonicalCaseDecision`, populated correctly per operation family, and used by every replay path. Verified with 5 dedicated tests, one per operation family.
- **R3 (failure category operationalization)** — all five categories (`AUTHORITY_REJECTION`, `SEMANTIC_REJECTION`, `UNRESOLVED`, `CONFLICT`, `TECHNICAL_FAILURE`) are now independently demonstrated, not just present as vocabulary. `UNRESOLVED` is grounded directly in `REQ-B5-018`'s own text ("canonically valid Asset identity, i.e., resolvable per B4 governance") — Case creation now checks for an active B4 `HOLD` decision on the referenced Asset. `CONFLICT` is grounded in `REQ-B5-082`'s own example ("two authoritative inputs... mutually incompatible") — a correction attempt on an already-superseded `CaseEvent` now classifies as `CONFLICT`. Neither required inventing new semantic policy.
- **R4 (real execution-reference boundary test)** — added a test with a real `RunnerExecution` row: the reference is attached to a `Case`, the execution's status is varied through `RUNNING/COMPLETED/FAILED/BLOCKED`, and `Case.case_status`/`current_execution_id` are proven unaffected throughout.
- **R5 (semantic-class review)** — confirmed directly against the frozen WHAT text (`docs/build/CPL_CG_WHAT_v0.1.md` §39a GAP-02, fetched from `origin/main` for this check) that all four `CaseEventType.semantic_class` values (`CPL_OPERATIONAL_FACT`, `DOMAIN_ASSERTION`, `CANONICAL_DECISION_CONSEQUENCE`, `TECHNICAL_SYSTEM_EVENT`) trace verbatim to the frozen list. No fifth class invented.
- **R6 (full traceability)** — see `docs/B5_CANDIDATE_REQUIREMENT_TRACEABILITY_v0.md`: all 115 requirements accounted for across 20 family blocks, none orphaned.

## Governance deviations

**NONE.** No frozen WHAT or requirement semantics were reinterpreted. The `UNRESOLVED`/`CONFLICT` groundings above are direct readings of existing frozen requirement text, not new policy.

## Known limitations

- `register_event_type` has no dedicated authority gate of its own (it is a governance/setup operation, not a per-Case operation) — flagged for a possible follow-up requirement, not a defect against any existing `REQ-B5-*`.
- No HTTP routes were added, consistent with the B3/B4 precedent and the fact that no frozen B5 requirement mandates one.

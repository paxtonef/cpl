# B5 Case Governance Candidate — Final Report (post-R7)

**Status: CANDIDATE_COMPLETE.**

- Repository: `paxtonef/cpl`
- Mandated code baseline: `1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628` (verified ancestor; branch created exactly there)
- Migration head: `026`
- Full regression: **190 / 190 passing** (152 B1–B4 baseline + 38 new B5) against real PostgreSQL 16
- Clean-DB install from scratch to `026`: verified three times (checkpoint, R1-R6 repair, R7 repair)
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

## R7 — found by independent inspection of commit `00cdfee`, not by this candidate's own audit

An independent review of the previous candidate (`00cdfeee3c9cfafb316d2f610b948841b4e2414b`) found that **`create_case()` still violated decision-before-effect** — it inserted the `Case` row and flushed it, then recorded the `CanonicalCaseDecision` afterward. The R1 repair correctly fixed the four functions explicitly named at the time (`add_participant`, `remove_participant`, `correct_case_metadata`, `correct_case_event`), and `transition_case_status` was already compliant, but `create_case` itself was never re-audited and slipped through.

**Root cause:** `CanonicalCaseDecision.case_id` has a FK into `cases.case_id`, so the decision could not previously be recorded before the Case row existed — my original implementation therefore had to create the Case first out of apparent necessity.

**Fix:** `Case.case_id` is now pre-generated in Python before either row is written. `CanonicalCaseDecision.case_id`'s FK was changed to `DEFERRABLE INITIALLY DEFERRED` — Postgres now checks the constraint at COMMIT time rather than immediately, so the decision INSERT (referencing the not-yet-existent Case row) succeeds, and the Case row is inserted afterward in the same transaction. Verified directly against the live database (`pg_constraint.condeferrable = t`, `condeferred = t`), not just asserted. This is a constraint-timing change only — it does not weaken referential integrity at commit, and does not touch any frozen semantic.

**Verification added:** `tests/integration/test_b5_r7_create_ordering.py`, 6 tests covering exactly the mandated scenarios — including one that instruments `session.flush()` to record which table is touched in which order, proving actual execution sequence rather than inferring it from atomicity alone.

**Full material-mutation audit performed** (not limited to previously-named functions): all seven B5 governed operations (`CREATE_CASE`, `STATUS_TRANSITION`, `ASSET_REBIND_ATTEMPT`, `PARTICIPANT_ADD`, `PARTICIPANT_REMOVE`, `METADATA_CORRECTION`, `EVENT_CORRECTION`) checked directly against source line numbers — see the audit table in `docs/B5_CANDIDATE_REQUIREMENT_TRACEABILITY_v0.md`. All seven: **PASS**.

## Governance deviations

**NONE.** No frozen WHAT or requirement semantics were reinterpreted. The `UNRESOLVED`/`CONFLICT` groundings above are direct readings of existing frozen requirement text, not new policy.

## Known limitations

- **AUTHORITY_REJECTION mechanism note (for independent verification):** authority denial is signaled by raising `AuthorityDeniedError` (an exception), while `SEMANTIC_REJECTION`/`UNRESOLVED`/`CONFLICT`/`TECHNICAL_FAILURE` are returned as typed `CaseResult.outcome` values. This is a deliberate, B3/B4-consistent choice (the same module's own docstring already documents `AuthorityDeniedError` as "a genuine precondition failure, distinct from a domain outcome"), and REQ-B5-080 only requires the five categories be *distinguishable*, not that they share one representation mechanism. This candidate does not independently re-verify that reading against the frozen requirement text beyond the test name — that check is left explicitly to independent DevOps verification, since it is exactly the kind of thing this candidate should not be trusted to self-certify.

- `register_event_type` has no dedicated authority gate of its own (it is a governance/setup operation, not a per-Case operation) — flagged for a possible follow-up requirement, not a defect against any existing `REQ-B5-*`.
- No HTTP routes were added, consistent with the B3/B4 precedent and the fact that no frozen B5 requirement mandates one.

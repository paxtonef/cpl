# B5 Case Governance Candidate — Progress Report (WIP Checkpoint)

**Status: IN PROGRESS — NOT COMPLETE.** This is a WIP checkpoint, not `CANDIDATE_COMPLETE`. No claim of full 115/115 traceability is made.

- Repository: `paxtonef/cpl`
- Mandated code baseline: `1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628` (verified ancestor of governance HEAD, branch created exactly there)
- Migration head at this checkpoint: `026`
- Full regression: **171/171 passing** (152 B1–B4 baseline + 19 new B5) against real PostgreSQL 16
- Clean-DB install from scratch to `026`: verified
- Migration round-trip (`025→026→025→026`): verified
- `/health`, `/ready`: both verified

## Implemented and test-verified this checkpoint

| Area | REQ range (approx.) | Status |
|---|---|---|
| Case creation (Contact + valid Asset required, idempotent) | 001–018 | implemented, tested |
| Case identity stability across status/participant/event changes | 002–006 | implemented, tested |
| Case status transitions, governed enum only, no domain-truth statuses | 039–045 | implemented, tested (rejected `REPAIRED` as invalid status) |
| Canonical decision pipeline (request→authority→decision→effect→history) | 046–051, 110–112 | implemented; **verified under actual injected DB failure** (SAVEPOINT + forced `IntegrityError` — no partial transition, no decision without effect) |
| Asset anchoring / post-creation rebinding prohibition | 014–018, 109 | implemented, tested — `attempt_asset_rebind` always returns `SEMANTIC_REJECTION`, never mutates `asset_id` |
| CaseParticipant add/remove, idempotent | 019–026, 077 | implemented, tested — structurally proven role alone never grants authority (`can_participant_mutate_case` never reads `participant_role`) |
| CaseEvent recording with governed, definition-time semantic classification | 027–038, 115 | implemented, tested — unregistered `event_type` rejected with `SEMANTIC_REJECTION` |
| `occurred_at` vs `created_at` independent representation | 114 | implemented, tested (event occurred yesterday, recorded today, both reconstructable) |
| CaseEvent correction by supersession (never destructive) | 069–072 | implemented, tested — original row preserved verbatim, marked `SUPERSEDED` |
| Case metadata correction (title/case_type) preserving prior value | 069 | implemented, tested |
| Idempotency (status transition, participant add) | 075–079 | implemented, tested (same key → replay; different key, same payload → distinct) |
| Failure-category distinction (`SEMANTIC_REJECTION` vs `TECHNICAL_FAILURE`) | 080–084 | partially tested — `SEMANTIC_REJECTION` and technical-failure-as-exception both verified; `AUTHORITY_REJECTION`/`UNRESOLVED`/`CONFLICT` categories exist in schema but have no dedicated positive test yet |
| Execution Governance boundary (no `execution_status` interpretation anywhere in B5 code) | 052–060 | implemented — verified structurally (source-code grep confirms no B5 module reads `RunnerExecution.execution_status`); no dedicated behavioral test with a real `RunnerExecution` row yet |
| Non-regression B1–B4 | 200-equivalent | 152/152 original tests still pass unmodified |

## NOT done yet — explicitly deferred, not silently dropped

- **`AUTHORITY_REJECTION`, `UNRESOLVED`, `CONFLICT` outcome categories** (REQ-B5-080–082): schema supports them (`rejection_category` CHECK constraint includes all four), but no service function currently produces `UNRESOLVED` or `CONFLICT` — these categories are architecturally available but not yet exercised by any real code path or test.
- **Idempotent replay outcome retrieval for CaseEvent correction and participant removal** (REQ-B5-113): implemented for status transitions and Case creation; not yet added to `correct_case_event`/`remove_participant`'s idempotency check paths beyond the generic ledger lookup (the ledger mechanism is shared and should work, but no dedicated test proves it for these two operations specifically).
- **Full requirement-by-requirement traceability matrix** for all 115 requirements — only ~28 are explicitly cited in code comments; the rest are covered implicitly by the same architecture but not individually documented.
- **B5-specific test coverage for GAP-01 exclusion** (no Case merge exists — true by absence, but no test explicitly asserts "no merge function exists" the way B4's identifier-equality tests did).
- **Real `RunnerExecution` row integration test** — `current_execution_id`/`CaseEvent.execution_id` fields exist and are nullable-preservable, but no test has actually populated a real `RunnerExecution` row and confirmed B5 code correctly ignores its status while preserving the reference.

## Known limitations

- `register_event_type` is a bare governance/setup function with no authority gate of its own (it's meant to be an administrative registration step, not a per-Case operation) — this may need an explicit authority requirement in a follow-up pass.
- No HTTP routes were added, consistent with the B3/B4 precedent and the fact that no frozen B5 requirement mandates one.

## Governance deviations

**NONE.** No frozen WHAT or requirement semantics were reinterpreted. All implementation choices (event-type registry as a separate table rather than a payload flag, decision ledger's `prior_value`/`new_value` JSONB as the generic correction-history mechanism rather than per-table supersession columns) are HOW decisions within GAP-02/GAP-03's explicitly-open bounds.

## This is not yet a candidate for independent verification

No `CANDIDATE_SHA` is being declared as final. Traceability is far short of 115/115. Further implementation work is needed before this reaches the completion gate defined in the Execution Mandate (§26–27).

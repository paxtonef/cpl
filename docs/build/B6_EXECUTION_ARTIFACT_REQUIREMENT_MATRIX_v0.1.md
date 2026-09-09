# B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1

## 1. Executive repair status

This is a **bounded repair** of `B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.md` (commit `6cf1892`), applying
exactly the twelve repairs instructed by `B6_EXECUTION_ARTIFACT_REQUIREMENT_CHALLENGE_v0.md` (commit
`647a915`) — `R-B6-R01` through `R-B6-R12` — retrieved and applied from their exact committed text, re-fetched
fresh from GitHub for this repair rather than reconstructed from memory. It is not a new requirements
analysis. Every requirement that passed Challenge cleanly is reproduced unchanged; nothing was rewritten for
style, terminology, or speculative completeness.

```text
ALL TWELVE REPAIRS: APPLIED
NEW ISSUES DISCOVERED DURING REPAIR: NONE
REPAIR_REGRESSION_CHECK: PASS
REQUIREMENTS_STATUS: RECHALLENGE_READY
REQUIREMENTS FREEZE: NOT GRANTED
```

---

## 2. Canonical baselines

```text
Governance HEAD (this repair's baseline):    647a91543dc4f72627370c29d111c897662816f9
Frozen WHAT:                                    docs/build/CPL_EA_WHAT_v0.1.md @ e7d5184204340840cccd97bf3811de73c756784849
Freeze + Admission:                                docs/build/CPL_EA_WHAT_FREEZE_AND_ADMISSION_v0.md @ 3092d7c69e59191fdfc945304fd71d5a8bf0b08d
Original Requirement Matrix (v0):                     docs/build/B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.md @ 6cf1892c720473094a4cab25aa0a2be7fcccae05
Requirement Challenge:                                    docs/build/B6_EXECUTION_ARTIFACT_REQUIREMENT_CHALLENGE_v0.md @ 647a91543dc4f72627370c29d111c897662816f9
CPL software baseline (unchanged):                            2ac075daea7d162825ed73ded0c7548011242a8f
Migration head (unchanged):                                      026
```

Baseline re-verified via `git ls-remote` immediately before drafting this repair; HEAD confirmed unchanged at
`647a91543dc4f72627370c29d111c897662816f9`. Both source documents (Matrix v0 and Challenge v0) were re-
fetched fresh from GitHub at their exact committed SHAs for this repair — R-B6-R01 through R-B6-R12 were read
from the actual committed Challenge file, not recalled from the conversation that produced it.

---

## 3. Repair authority and scope

Authorized scope: apply exactly `R-B6-R01`–`R-B6-R12` as instructed. No other requirement may be altered.
No WHAT-level semantics may be touched. No implementation, schema, or migration change is authorized. This
repair does not conduct a Re-Challenge and does not grant Requirements Freeze.

---

## 4. Preservation discipline

**75 of the 87 v0 requirements are unaffected by any of the twelve repairs and are carried forward
byte-identical to v0.** They are not reproduced in full here (see §22's design note) to avoid the exact
failure mode §4 of the repair instruction warns against — rewriting for its own sake. Their authoritative
text remains `B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.md`. Nine requirements were amended in place
(touched by exactly one repair each, or in `REQ-B6-072`'s case two: `R-B6-R04` and part of `R-B6-R10`). Two
requirements were retired and split into eleven successors. Three wholly new requirements were added.

---

## 5. Original matrix inventory

```text
v0 total:            87 requirements (REQ-B6-001–087)
Unaffected by repair:   76
Amended in place:          9   (REQ-B6-013, 015, 023, 057, 066, 072, 073, 074, 082)
Retired (split):              2   (REQ-B6-008, REQ-B6-032)
```

---

## 6. R-B6-R01 repair — REQ-B6-057 canonical-authority designation

**Exact committed repair instruction:** *"Affected: REQ-B6-057. Problem: no canonical-authority designation
between `artifact_status = SUPERSEDED` and `supersedes_artifact_id`. Required change: designate the relation
canonical, status derived; add consistency-check acceptance test. Source: RC-B6-01. Count change: none
(amends existing requirement)."*

**REQ-B6-057 (repaired)** `IMPLEMENTATION / WHAT DIVERGENCE — RESOLVED AT REQUIREMENTS LEVEL` — SUPERSEDED
status is derived from the supersedes_artifact_id relation
Source: schema (`runner_artifacts_status_chk` includes `SUPERSEDED`; `supersedes_artifact_id` self-FK, both
migration 012); WHAT §16 | Authority: CPL | Object: RunnerArtifact
Statement: The live schema encodes supersession two ways at once: a status value (`artifact_status =
'SUPERSEDED'`, set on the OLD artifact) and a link (`supersedes_artifact_id`, set on the NEW artifact,
pointing backward). Requirements designate `supersedes_artifact_id` — the relational fact, directly
inspectable and already the WHAT-acknowledged substrate (§16) — as **canonical**. `artifact_status =
SUPERSEDED` is a **derived, denormalized projection** of that relation: it SHALL hold if and only if at least
one other `RunnerArtifact` row's `supersedes_artifact_id` references this artifact's `artifact_id`, and SHALL
NEVER be treated as authoritative in its own right. Neither field SHALL be settable independently of the
other by ordinary application code (unchanged from v0). Any consistency check or repair procedure that finds
the two disagreeing SHALL resolve the disagreement by recomputing `artifact_status` from the relation —
never the reverse.
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST (setting one without the other is rejected or
impossible via the governed write path); **CONSISTENCY TEST (new)** — a query joining artifacts on
`supersedes_artifact_id` against `artifact_status` finds zero mismatches across the full table, and a
manually induced mismatch (e.g., via direct DB manipulation in a test environment) is repaired only by
recomputing status from the relation, never by editing the relation to match status.
Acceptance: Coordinated write enforced AND the canonical-authority consistency query returns zero mismatches
| Failure: The two drift, OR any procedure treats `artifact_status` as authoritative over
`supersedes_artifact_id`
Notes: Resolves `RC-B6-01`. This does not touch the WHAT's supersession semantics (§16) — the WHAT is silent
on `artifact_status` entirely, so designating a canonical mechanical authority between two schema fields is a
Requirements-level coordination decision, not a WHAT reinterpretation.

---

## 7. R-B6-R02 repair — idempotency concurrent-insert race

**Exact committed repair instruction:** *"Affected: §13 (new). Problem: concurrent-insert race unaddressed.
Required change: new requirement specifying catch-and-retrieve behavior on constraint-violation race. Source:
RC-B6-02. Count change: +1 requirement."*

**REQ-B6-088 (new)** `IDEMPOTENCY` — Concurrent-insert race resolves to retrieval, never a raw error
Source: WHAT §17 (BS-EA-03); schema (`runner_executions_idempotency_uq`, migration 011) | Authority: CPL |
Object: RunnerExecution
Statement: When two or more requests concurrently attempt to materialize a `RunnerExecution` with the same
`(runner_type, idempotency_key)`, exactly one insert SHALL succeed and every other concurrent insert SHALL
fail against `runner_executions_idempotency_uq`. Every writer whose insert fails this way SHALL catch the
constraint violation and re-read the now-existing row, then apply REQ-B6-036/037's same-intent/conflict
comparison (via REQ-B6-038) against it exactly as if it had observed the row before attempting to write. No
writer SHALL surface the raw constraint-violation error to its caller as a final outcome.
Verification: INTEGRATION TEST — concurrent-submission test, two simultaneous callers submitting identical
`(runner_type, idempotency_key, case_id, asset_id, execution_purpose)`
Acceptance: Exactly one canonical `RunnerExecution` row exists, and both callers observe REQ-B6-036's
retrieval outcome, never a raw database error | Failure: A caller receives a raw constraint-violation error,
or two rows are created
Notes: Resolves `RC-B6-02`. Does not alter REQ-B6-035's scope statement or REQ-B6-036/037's comparison logic
— it specifies only the mechanical recovery path for the race those requirements already anticipated but did
not fully specify.

---

## 8. R-B6-R03 repair — authority-collapse resolution (REQ-B6-015)

**Exact committed repair instruction:** *"Affected: REQ-B6-015. Problem: authority-collapse tension with
REQ-B6-077. Required change: rewrite to clarify automatic, rule-bound decision satisfies the decision-record
requirement, distinguished from admission-type decisions in the audit trail. Source: RC-B6-03. Count change:
none (amends existing requirement)."*

**REQ-B6-015 (repaired)** `AUTHORITY` — Runner-reported transitions satisfy the decision requirement via
automatic, rule-bound acceptance
Source: WHAT §8, §9; EA-CI03, EA-CI13 | Authority: CPL (representation), domain runner (report only) | Object:
RunnerExecution
Statement: A runner's self-reported completion/failure signal triggers an `execution_status` transition only
through an **automatic, rule-bound governed decision**: CPL accepts a well-formed runner report as sufficient
grounds to transition representation state, without a human or additional-authority approval step. This
automatic acceptance **satisfies** REQ-B6-077's requirement that every transition carry a governed decision
record — it does not exempt the transition from that requirement, it fulfills it by rule rather than by
manual evaluation. The resulting decision record SHALL be distinguishable in the audit trail from an
admission-type decision (REQ-B6-076) — e.g., via a distinct `decision_type` or equivalent marker — confirming
it was automatic and rule-bound rather than manually approved. This SHALL NOT be read as elevating the
runner's report to a canonical governance decision in the admission sense (see REQ-B6-016); it remains
representation-only and carries no domain-truth weight.
Verification: DOMAIN-BOUNDARY REVIEW; INTEGRATION TEST (every runner-reported transition has a decision
record; that record's type is distinguishable from an admission-type decision's type)
Acceptance: A decision record is present and distinguishable for every runner-reported transition | Failure:
No decision record exists for a runner-reported transition (violates REQ-B6-077), or the record is
indistinguishable from an admission-type decision (reintroduces the ambiguity this repair closes)
Notes: Resolves `RC-B6-03` / `AUTHORITY_BOUNDARY = FAIL`. This version reconciles with REQ-B6-077 rather than
contradicting it — no new Authority object is introduced; the repair distinguishes decision *kinds*, not new
decision-making entities.

---

## 9. R-B6-R04 repair — REQ-B6-072 EA-CI08/09 traceability

**Exact committed repair instruction:** *"Affected: REQ-B6-072. Problem: EA-CI08/09 uncited despite
substantive coverage. Required change: add citations, add explicit CaseEvent≠RunnerArtifact sentence. Source:
RC-B6-04. Count change: none."*

**REQ-B6-072 (repaired)** `COMPATIBILITY` — Case boundary consumed, not altered
Source: WHAT §20; **EA-CI08, EA-CI09** | Authority: B5 (Case), CPL (execution, referenced) | Object:
RunnerExecution, RunnerArtifact
Statement: `Case.current_execution_id` and `CaseEvent.execution_id` SHALL be consumed exactly as B5's own
`REPAIR-01` scoped them — opaque, execution-governance-owned references. No requirement in this matrix SHALL
alter B5 `Case` semantics. **`CaseEvent` and `RunnerArtifact` remain distinct concepts even where one
references the other (EA-CI09): a `CaseEvent` is Case-level append-only narrative history; a `RunnerArtifact`
is an execution-produced object governed by this Build Unit; neither is a substitute for or equivalent to the
other, even when a `CaseEvent` references a `RunnerExecution` or its artifacts.**
Verification: REGRESSION TEST (existing B5 test suite unaffected) | Acceptance: Unaffected | Failure: A B5
test fails or B5 semantics require change
Notes: If B6 implementation is later found to require a B5 semantic change, that requirement chain SHALL be
marked `GOVERNANCE_CONFLICT` and stopped, not resolved here — none identified in this matrix. Resolves
`RC-B6-04`'s `EA-CI08`/`EA-CI09` citation gap. This requirement is also extended by `R-B6-R10` (§15 below)
with a `case_id` FK-RESTRICT preservation clause.

---

## 10. R-B6-R05 repair — REQ-B6-082 citation correction

**Exact committed repair instruction:** *"Affected: REQ-B6-082. Problem: mislabeled source citation. Required
change: correct label from 'WHAT §36' to the correct instruction reference. Source: RC-B6-05. Count change:
none."*

**REQ-B6-082 (repaired)** `INTEGRITY` — Produced vs. canonically registered, distinguished
Source: **Requirements Construction Instruction §36** (produced-vs-registered distinction) — corrected from
the original mislabeling as "WHAT §36"; the frozen WHAT contains no §36 | Authority: CPL | Object:
RunnerArtifact
Statement: An artifact produced or emitted by a runner but not yet canonically registered (REQ-B6-078) SHALL
be distinguishable, in any observable system state, from a canonically registered `RunnerArtifact`; the two
SHALL NOT share representation such that an unregistered artifact could be mistaken for a governed one.
Verification: INTEGRATION TEST | Acceptance: Distinguishable | Failure: Not distinguishable
Notes: Resolves `RC-B6-05`. Content unchanged — this was a citation-label defect only, not a substantive
error.

---

## 11. R-B6-R06 repair — runner_executions_time_chk classification

**Exact committed repair instruction:** *"Affected: REQ-B6-013 (or new sibling). Problem:
`runner_executions_time_chk` unclassified. Required change: name and classify the constraint ALIGNED with a
preservation requirement. Source: RC-B6-06. Count change: +1 requirement (or 0 if folded into REQ-B6-013)."*
Folded into REQ-B6-013 (the explicitly permitted 0-count option), keeping it alongside its sibling constraint.

**REQ-B6-013 (repaired)** `INTEGRITY` — Time-ordering and completion constraints are preserved, not
re-invented
Source: existing constraints `runner_executions_completed_at_chk` and **`runner_executions_time_chk`**
(migration 011); both classified ALIGNED per §31 | Authority: CPL | Object: RunnerExecution
Statement: The existing constraint that `execution_status = 'COMPLETED'` requires `completed_at IS NOT NULL`
SHALL be preserved by any Requirements-level transition logic (REQ-B6-009). **Likewise, the existing
constraint `runner_executions_time_chk` (`completed_at IS NULL OR started_at IS NULL OR completed_at >=
started_at`) SHALL be preserved: Requirements SHALL NOT introduce a code path that can set `completed_at`
earlier than `started_at`.** Requirements SHALL NOT introduce a code path that can set `COMPLETED` without
populating `completed_at`, even redundantly with the DB constraints.
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST (application-level attempt to set `COMPLETED`
without `completed_at` fails; application-level attempt to set `completed_at` earlier than `started_at` fails
— both before or at the DB layer)
Acceptance: No path bypasses either constraint | Failure: A path exists that violates either (e.g., via a
different connection role or a migration-level constraint drop)
Notes: This requirement exists because Requirements MUST NOT silently assume an executable fact continues to
hold — both time-related constraints must be named and preserved explicitly. Resolves `RC-B6-06`.

---

## 12. R-B6-R07 repair — schema_name/schema_version governance

**Exact committed repair instruction:** *"Affected: §11/§12 (new). Problem: schema_name/schema_version
ungoverned. Required change: new requirement defining the fields and their role in structural validation.
Source: RC-B6-07. Count change: +1 requirement."*

**REQ-B6-089 (new)** `INTEGRITY` — schema_name/schema_version govern structural validation
Source: schema (`schema_name`, `schema_version`, both `NOT NULL`, migration 012); WHAT §19
(Requirements-level, structural-validation meaning of `VALIDATED`) | Authority: CPL | Object: RunnerArtifact
Statement: `schema_name` and `schema_version` together SHALL identify the declared payload contract an
artifact's `payload` claims to conform to — `schema_name` naming the contract, `schema_version` naming its
version. A `RunnerArtifact` transitions to `artifact_status = VALIDATED` (REQ-B6-032) only if its `payload` is
checked against the schema/type definition registered under its declared `(schema_name, schema_version)` pair
and found conformant. An artifact declaring a `(schema_name, schema_version)` pair with no registered
definition SHALL NOT be able to reach `VALIDATED` — it SHALL transition to `REJECTED` (REQ-B6-033, structural
reason: unknown schema).
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST (an artifact declaring an unregistered
`schema_name`/`schema_version` pair cannot reach `VALIDATED`; an artifact with a conformant payload against a
registered pair does)
Acceptance: `VALIDATED` is reachable only via an objective check against a named, registered schema
definition | Failure: `VALIDATED` is reachable without such a check, or left to implementer discretion
Notes: Resolves `RC-B6-07`. Does not prescribe the registration mechanism for schema definitions (a schema
registry table, a versioned file set, or otherwise) — that choice is HOW.

---

## 13. R-B6-R08 repair — REQ-B6-023 zero-artifact completeness

**Exact committed repair instruction:** *"Affected: REQ-B6-023. Problem: COMPLETED+zero-artifact case not
explicitly named. Required change: expand case (a) to cover both failure-path and design-path zero-artifact
scenarios. Source: RC-B6-08. Count change: none."*

**REQ-B6-023 (repaired)** `RELATION` — Zero, one, or many artifacts per execution
Source: WHAT §11, §24 (BS-EA-01, RESOLVED) | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: A single `RunnerExecution` SHALL support zero, one, or many `RunnerArtifact` rows without any
Build-Unit-imposed upper bound; no requirement in this matrix SHALL force a single-output runner model.
Verification: INTEGRATION TEST, three cases: **(a) execution with zero artifacts — covering BOTH (a-i) a
non-terminal or `FAILED` execution where technical failure occurred before any output was produced, AND
(a-ii) a `COMPLETED` execution that legitimately produces no artifact by design (e.g., a side-effect-only
runner outcome) — both are valid, non-anomalous states, not merely the failure-path case**; (b) execution
with exactly one artifact; (c) execution with multiple, independently identified artifacts
Acceptance: All three cases succeed, including both (a-i) and (a-ii) explicitly | Failure: Any case is
structurally blocked, or a `COMPLETED` execution with zero artifacts is flagged as anomalous
Notes: BS-EA-01 is RESOLVED at WHAT level; this requirement is the mechanism-level closure, not a semantic
reopening. Resolves `RC-B6-08`.

---

## 14. R-B6-R09 repair — atomicity split (REQ-B6-008, REQ-B6-032)

**Exact committed repair instruction:** *"Affected: REQ-B6-008, REQ-B6-032. Problem: multi-obligation
bundling. Required change: split into per-value sub-requirements. Source: RC-B6-09. Count change: +9 (2
requirements become 11)."* The Challenge offered two split conventions; this repair uses the
**lettered-suffix convention** (`REQ-B6-008a…g`) explicitly named as an option, since it preserves traceable
lineage to the retired parent without consuming eleven fresh sequential slots. Per §11 of the repair
instruction, a retired requirement remains traceably recorded — both parent IDs are kept below, marked
`RETIRED — SPLIT`, not deleted.

**REQ-B6-008 — RETIRED, SPLIT into REQ-B6-008a–g.** Original statement and classification preserved here for
traceability: *"The existing executable `execution_status` vocabulary — `CREATED`, `QUEUED`, `RUNNING`,
`COMPLETED`, `FAILED`, `BLOCKED`, `CANCELLED` — SHALL be adopted as the governed vocabulary..."* Retired
because it bundled seven independently verifiable per-value obligations under one ID (Challenge §7,
Atomicity).

**REQ-B6-008a** `ONTOLOGY-CONFORMANCE` — execution_status = CREATED
Source: WHAT §23 | Authority: CPL | Object: RunnerExecution
Statement: `CREATED` is a pre-terminal representation state (materialized, not yet queued/running) — ALIGNED,
no domain overlap.
Verification: STATIC SCHEMA INSPECTION | Acceptance: Mapping documented | Failure: Undocumented
Notes: Split from REQ-B6-008 per R-B6-R09.

**REQ-B6-008b** `ONTOLOGY-CONFORMANCE` — execution_status = QUEUED
Source: WHAT §23 | Authority: CPL | Object: RunnerExecution
Statement: `QUEUED` is a pre-terminal representation state — ALIGNED, no domain overlap.
Verification: STATIC SCHEMA INSPECTION | Acceptance: Mapping documented | Failure: Undocumented
Notes: Split from REQ-B6-008 per R-B6-R09.

**REQ-B6-008c** `ONTOLOGY-CONFORMANCE` — execution_status = RUNNING
Source: WHAT §23 | Authority: CPL | Object: RunnerExecution
Statement: `RUNNING` is a pre-terminal representation state — ALIGNED, no domain overlap.
Verification: STATIC SCHEMA INSPECTION | Acceptance: Mapping documented | Failure: Undocumented
Notes: Split from REQ-B6-008 per R-B6-R09.

**REQ-B6-008d** `ONTOLOGY-CONFORMANCE` — execution_status = COMPLETED
Source: WHAT §8, §23; EA-CI03 | Authority: CPL | Object: RunnerExecution
Statement: `COMPLETED` is ALIGNED, subject to REQ-B6-007's non-interpretation discipline (means only that the
runner reported finishing, never that its conclusion was accepted).
Verification: STATIC SCHEMA INSPECTION; DOMAIN-BOUNDARY REVIEW | Acceptance: Mapping documented and
non-interpretation discipline confirmed | Failure: Either absent
Notes: Split from REQ-B6-008 per R-B6-R09.

**REQ-B6-008e** `ONTOLOGY-CONFORMANCE` — execution_status = FAILED
Source: WHAT §8, §23; EA-CI02, EA-CI03 | Authority: CPL | Object: RunnerExecution
Statement: `FAILED` is ALIGNED, subject to REQ-B6-007's non-interpretation discipline and REQ-B6-067's
prohibition on representing domain-negative results as `FAILED`.
Verification: STATIC SCHEMA INSPECTION; DOMAIN-BOUNDARY REVIEW | Acceptance: Mapping documented | Failure:
Undocumented, or domain-negative results found mapped to FAILED
Notes: Split from REQ-B6-008 per R-B6-R09.

**REQ-B6-008f** `ONTOLOGY-CONFORMANCE` — execution_status = CANCELLED
Source: WHAT §23 ("cancellation, only if supported") | Authority: CPL | Object: RunnerExecution
Statement: `CANCELLED` REQUIRES REQUIREMENT-LEVEL SEMANTICS; WHAT §23 lists cancellation as "only if
supported" and this matrix confirms it IS supported. Full semantics defined at REQ-B6-011.
Verification: STATIC SCHEMA INSPECTION; cross-check against REQ-B6-011 | Acceptance: Mapping documented and
consistent with REQ-B6-011 | Failure: Inconsistent or undocumented
Notes: Split from REQ-B6-008 per R-B6-R09.

**REQ-B6-008g** `ONTOLOGY-CONFORMANCE` — execution_status = BLOCKED
Source: WHAT §23 (not named in the illustrative list) | Authority: CPL | Object: RunnerExecution
Statement: `BLOCKED` REQUIRES REQUIREMENT-LEVEL SEMANTICS; not named in WHAT §23's illustrative list at all.
Full semantics defined at REQ-B6-012.
Verification: STATIC SCHEMA INSPECTION; cross-check against REQ-B6-012 | Acceptance: Mapping documented and
consistent with REQ-B6-012 | Failure: Inconsistent or undocumented
Notes: Split from REQ-B6-008 per R-B6-R09.

**REQ-B6-032 — RETIRED, SPLIT into REQ-B6-032a–d.** Original statement preserved here for traceability:
*"Each of the four existing values SHALL be assigned a Requirements-level meaning consistent with
REQ-B6-031..."* Retired because it bundled four independently verifiable per-value obligations under one ID.

**REQ-B6-032a** `ONTOLOGY-CONFORMANCE` — artifact_status = CREATED
Source: schema (migration 012); WHAT §19 | Authority: CPL | Object: RunnerArtifact
Statement: `CREATED` = persisted, not yet structurally checked.
Verification: STATIC SCHEMA INSPECTION | Acceptance: Mapping documented | Failure: Undocumented
Notes: Split from REQ-B6-032 per R-B6-R09.

**REQ-B6-032b** `ONTOLOGY-CONFORMANCE` — artifact_status = VALIDATED
Source: schema (migration 012); WHAT §19; REQ-B6-089 | Authority: CPL | Object: RunnerArtifact
Statement: `VALIDATED` = passed CPL-side structural validation per REQ-B6-089's `schema_name`/`schema_version`
mechanism — explicitly NOT domain acceptance.
Verification: STATIC SCHEMA INSPECTION; DOMAIN-BOUNDARY REVIEW; cross-check against REQ-B6-089 | Acceptance:
Mapping documented, no domain-acceptance language | Failure: Either fails
Notes: Split from REQ-B6-032 per R-B6-R09.

**REQ-B6-032c** `ONTOLOGY-CONFORMANCE` — artifact_status = SUPERSEDED
Source: schema (migration 012); WHAT §16; REQ-B6-057 (repaired) | Authority: CPL | Object: RunnerArtifact
Statement: `SUPERSEDED` is governed entirely by REQ-B6-057 (repaired): a derived projection of the
`supersedes_artifact_id` relation, never independently authoritative.
Verification: Cross-check against REQ-B6-057's consistency test | Acceptance: Consistent | Failure:
Inconsistent
Notes: Split from REQ-B6-032 per R-B6-R09. Canonical-authority ambiguity closed by R-B6-R01 (§6 above).

**REQ-B6-032d** `ONTOLOGY-CONFORMANCE` — artifact_status = REJECTED
Source: schema (migration 012); WHAT §19; REQ-B6-033 | Authority: CPL (structural), NOT domain | Object:
RunnerArtifact
Statement: `REJECTED` is governed entirely by REQ-B6-033: structural rejection only, never domain rejection.
Verification: Cross-check against REQ-B6-033 | Acceptance: Consistent | Failure: Inconsistent
Notes: Split from REQ-B6-032 per R-B6-R09.

---

## 15. R-B6-R10 repair — FK RESTRICT substrate classification

**Exact committed repair instruction:** *"Affected: substrate classification (new). Problem: three FK
RESTRICT behaviors unclassified. Required change: new requirement (or extension) naming and classifying them
ALIGNED. Source: RC-B6-10. Count change: +1 requirement (or 0 if folded into existing
REQ-B6-072/073/074)."* Folded into the three named requirements (the explicitly permitted 0-count option).
`case_id`'s RESTRICT clause was added to REQ-B6-072 under §9 above (R-B6-R04); the remaining two are added
here.

**REQ-B6-073 (repaired)** `COMPATIBILITY` — Asset boundary preserved
Source: WHAT §21 | Authority: B4 (Asset), CPL (execution, referenced) | Object: RunnerExecution
Statement: `RunnerExecution.asset_id` SHALL remain a reference only, structurally identical to `Case.asset_id`.
This Build Unit SHALL NOT merge Assets, determine physical Asset sameness, select a canonical Asset survivor,
redefine Asset identifiers, or override VIR's physical-identity determination authority. **The existing
`ondelete=RESTRICT` behavior on `RunnerExecution.asset_id` (migration 011) is preserved and classified
ALIGNED: an `Asset` referenced by an existing `RunnerExecution` cannot be deleted while that reference exists;
this is intentional B6-relevant behavior, not incidental implementation detail.**
Verification: REGRESSION TEST (existing B4 test suite unaffected); DOMAIN-BOUNDARY REVIEW; **STATIC SCHEMA
INSPECTION (RESTRICT behavior confirmed)**
Acceptance: Unaffected, no boundary violation, RESTRICT confirmed intentional | Failure: Any of the three
fails
Notes: Resolves the `asset_id` portion of `RC-B6-10`.

**REQ-B6-074 (repaired)** `COMPATIBILITY` — Contact/initiator boundary preserved
Source: WHAT §22 | Authority: B3 (Contact) | Object: RunnerExecution
Statement: `initiated_by_contact_id` SHALL continue to use B3 `Contact` exclusively; this Build Unit SHALL NOT
introduce a generalized Actor/Role concept. **The existing `ondelete=RESTRICT` behavior on
`RunnerExecution.initiated_by_contact_id` (migration 011) is preserved and classified ALIGNED: a `Contact`
referenced as an initiator of an existing `RunnerExecution` cannot be deleted while that reference exists;
this is intentional B6-relevant behavior.**
Verification: REGRESSION TEST (existing B3 test suite unaffected); STATIC SCHEMA INSPECTION (no new
actor/role table introduced; RESTRICT behavior confirmed)
Acceptance: All three confirmed | Failure: Any fails
Notes: Resolves the `initiated_by_contact_id` portion of `RC-B6-10`. Combined with REQ-B6-072's `case_id`
clause and REQ-B6-073's `asset_id` clause above, all three previously-unclassified RESTRICT behaviors are now
named and classified ALIGNED — `RC-B6-10` fully closed.

---

## 16. R-B6-R11 repair — classification mandatoriness and validation taxonomy

**Exact committed repair instruction:** *"Affected: REQ-B6-026 (or new). Problem: classification
mandatoriness/validation-taxonomy undefined. Required change: new requirement or acceptance-criterion
expansion. Source: RC-B6-11. Count change: +1 requirement."* The Challenge's own count-change note fixes this
at +1 regardless of the "(or new)" hedge — implemented as a new requirement, REQ-B6-026 itself left
unchanged.

**REQ-B6-090 (new)** `CLASSIFICATION` — Dimension mandatoriness and validation-failure taxonomy
Source: WHAT §11 (mechanism is Requirements/HOW; mandatoriness is a Requirements-level operational question);
this challenge's own §16 test (validation taxonomy) | Authority: CPL | Object: RunnerArtifact
Statement: All three classification dimensions (REQ-B6-026: semantic function, production/lifecycle role,
consumption/presentation role) SHALL be mandatory at artifact registration (REQ-B6-078) — no dimension MAY be
left unset on a canonically registered `RunnerArtifact`. Registration-time validation of a submitted
classification SHALL distinguish exactly five outcomes: (1) **INVALID VALUE** — a value not in the
dimension's defined vocabulary (REQ-B6-027/028); (2) **UNSUPPORTED VALUE** — a syntactically valid but
not-yet-enabled value for this Build Unit; (3) **CONTRADICTORY COMBINATION** — a combination of dimension
values the mechanism defines as mutually exclusive, if any such combination is ever defined (none is defined
by this matrix at this time — REQ-B6-026 requires the three dimensions to coexist freely, so this outcome is
currently unreachable by design, not silently ignored); (4) **MISSING REQUIRED DIMENSION** — any of the three
dimensions left unset; (5) **VALID** — all three dimensions set to defined, supported, non-contradictory
values. Only outcome (5) SHALL permit registration to proceed; outcomes (1)–(4) SHALL cause registration to
be rejected with an outcome-specific, distinguishable reason.
Verification: INTEGRATION TEST, one case per outcome (5 cases)
Acceptance: Each of the five outcomes is independently reachable and distinguishable | Failure: Two outcomes
collapse into the same observable result, or an incomplete classification is silently accepted
Notes: Resolves `RC-B6-11`. Confirms — rather than silently ignores — that "optional dimension" (one of the
Challenge's five named failure modes) is inapplicable to this matrix's classification model, since all three
dimensions are mandatory by this requirement.

---

## 17. R-B6-R12 repair — failure-model five-category disposition

**Exact committed repair instruction:** *"Affected: REQ-B6-066. Problem: B5's five-category adaptation left
unaddressed despite being a named WHAT-level open question. Required change: expand to explicitly disposition
all five categories. Source: RC-B6-12. Count change: none."*

**REQ-B6-066 (repaired)** `FAILURE` — Distinct observable failure categories, with explicit B5-adaptation
disposition
Source: WHAT §23 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: The system SHALL make the following distinguishable, per REQ-B6-008a–g's vocabulary mapping:
execution not authorized (pre-materialization rejection, REQ-B6-009 "no row" case); execution `BLOCKED`
(REQ-B6-012); technical execution failure (`FAILED`); execution completion (`COMPLETED`); artifact structural
invalidity (`REJECTED`, REQ-B6-033); integrity failure (REQ-B6-055); and any domain-level rejection, which is
explicitly out-of-B6 and SHALL NOT be represented in any of the above vocabularies (REQ-B6-060 analogue for
execution). **Per WHAT §23's explicit open question of whether B5's five-category failure discipline
(`AUTHORITY_REJECTION`/`SEMANTIC_REJECTION`/`UNRESOLVED`/`CONFLICT`/`TECHNICAL_FAILURE`) applies unchanged or
needs adaptation, this Build Unit resolves it as follows, distinguishing execution-level from artifact-level
applicability rather than adopting the five categories uniformly: `AUTHORITY_REJECTION` maps to the
pre-materialization "no row" case (REQ-B6-076) at the execution level; it has no artifact-level analogue since
artifact registration is never authority-rejected in the same admission sense. `TECHNICAL_FAILURE` maps to
`FAILED` at the execution level; it has no distinct artifact-level analogue beyond `REJECTED`.
`SEMANTIC_REJECTION` maps to `REJECTED` on `RunnerArtifact` (REQ-B6-033) — well-formed content that fails a
structural rule; it has no execution-level analogue, since a semantically-rejectable act at the execution
level is already covered by the pre-materialization authority-rejection case. `UNRESOLVED` maps to `BLOCKED`
(REQ-B6-012) at the execution level; it has no artifact-level analogue, since artifact registration
(REQ-B6-078) is not defined as an optionally-pending decision in this Build Unit. `CONFLICT` maps to the
idempotency conflict outcome (REQ-B6-037) at the execution level; it has no dedicated artifact-level analogue
at this time — no competing-claim scenario for artifact registration has been identified as needing one; if
one is discovered later, it is a new gap to be raised through governance, not silently assumed absent by this
requirement.**
Verification: NEGATIVE TEST, one per category — confirm each is independently distinguishable and that domain
rejection cannot be represented; **TRACEABILITY REVIEW confirming all five B5-derived categories have an
explicit B6 disposition, not merely the two previously covered**
Acceptance: All distinguishable, domain rejection unrepresentable, and all five categories from WHAT §23's
named question have an explicit, on-record disposition | Failure: Two collapse into one, domain rejection
leaks into a category, or any of the five categories remains undispositioned
Notes: Resolves `RC-B6-12`. This closes WHAT §23's own named open question rather than leaving it implicit.

---

## 18. Authority-boundary repair result

```text
AUTHORITY_BOUNDARY: REPAIRED
```

`REQ-B6-015` (repaired, §8 above) no longer collapses `RUNNER REPORT = CANONICAL DECISION`. It now explicitly
states that the runner-report-triggered transition satisfies `REQ-B6-077`'s decision-record requirement
through an automatic, rule-bound decision, distinguishable in the audit trail from an admission-type decision.
`REQ-B6-077` is unchanged and remains satisfied — every transition, including runner-reported ones, still
requires a decision record; the repair clarifies *how* that record is generated for the runner-reported case,
not whether it exists. Re-checked the full authority chain: requester ≠ initiator ≠ runner reporter ≠ CPL
representation authority ≠ domain authority, with `REPORTER ≠ AUTHORITY`, `INITIATOR ≠ AUTHORITY`, and `CPL
REPRESENTATION AUTHORITY ≠ DOMAIN TRUTH AUTHORITY` all holding after repair. No new Authority object was
introduced.

---

## 19. Idempotency repair result

```text
IDEMPOTENCY_CONTRACT: REPAIRED
```

`REQ-B6-088` (new, §7 above) closes the concurrency gap. Combined with the unchanged `REQ-B6-035`–`042`, an
implementer now has explicit, non-inventable coverage of: key scope, duplicate submission (same intent),
conflict (different intent), the definition of "materially different intent," NULL-key behavior, retry's
relation to idempotency, the `idempotency_key ≠ identity` prohibition, **and concurrent-insert recovery**.
`runner_executions_idempotency_uq` remains preserved unaltered; the implementation-fact/ontological-definition
distinction is preserved (`REQ-B6-088` governs mechanical recovery behavior only, it does not touch what
`RunnerExecution` identity *is*).

---

## 20. REQ-B6-057 repair result

```text
REQ-B6-057: REPAIRED
```

Canonical authority is now designated: `supersedes_artifact_id` is canonical, `artifact_status = SUPERSEDED`
is derived. The two named invalid states (`SUPERSEDED` with no referencing relation; a relation with
inconsistent status) are now governed by an explicit consistency test with a defined repair direction (status
recomputed from relation, never the reverse). This does not alter the WHAT's supersession semantics (§16),
which remains silent on `artifact_status` — the repair is a Requirements-level coordination decision only.

---

## 21. EA-CI08/09 traceability repair

```text
EA-CI08: now cited (REQ-B6-072)
EA-CI09: now cited (REQ-B6-072)
```

Both invariants are now explicitly cited in `REQ-B6-072`, with `EA-CI09`'s `CaseEvent ≠ RunnerArtifact`
distinction stated as an explicit sentence, not merely implied by the surrounding text. See §26 for the full
recomputed coverage table.

---

## 22. Updated full requirement matrix

**Design note on this section's scope:** Per the Preservation Rule (§4 of the repair instruction — "PASS ≠
INVITATION TO IMPROVE"), the 76 requirements untouched by any of the twelve repairs are not reproduced here;
doing so would be exactly the "rewrite for speculative completeness" the repair instruction prohibits. Their
authoritative full text remains `B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.md`. This section is the
complete **index** of the v0.1 matrix — every ID, its status, and where its authoritative text now lives.

```text
REQ-B6-001–007   UNCHANGED — full text in v0
REQ-B6-008       RETIRED — SPLIT into REQ-B6-008a–g (§14 above)
REQ-B6-008a–g    NEW — full text §14 above
REQ-B6-009–012   UNCHANGED — full text in v0
REQ-B6-013       MODIFIED — full text §11 above
REQ-B6-014       UNCHANGED — full text in v0
REQ-B6-015       MODIFIED — full text §8 above
REQ-B6-016–022   UNCHANGED — full text in v0
REQ-B6-023       MODIFIED — full text §13 above
REQ-B6-024–031   UNCHANGED — full text in v0
REQ-B6-032       RETIRED — SPLIT into REQ-B6-032a–d (§14 above)
REQ-B6-032a–d    NEW — full text §14 above
REQ-B6-033–056   UNCHANGED — full text in v0
REQ-B6-057       MODIFIED — full text §6 above
REQ-B6-058–065   UNCHANGED — full text in v0
REQ-B6-066       MODIFIED — full text §17 above
REQ-B6-067–071   UNCHANGED — full text in v0
REQ-B6-072       MODIFIED — full text §9 above
REQ-B6-073       MODIFIED — full text §15 above
REQ-B6-074       MODIFIED — full text §15 above
REQ-B6-075–081   UNCHANGED — full text in v0
REQ-B6-082       MODIFIED — full text §10 above
REQ-B6-083–087   UNCHANGED — full text in v0
REQ-B6-088       NEW — full text §7 above
REQ-B6-089       NEW — full text §12 above
REQ-B6-090       NEW — full text §16 above
```

```text
V0.1 ACTIVE REQUIREMENT COUNT: 99
  76 unchanged + 9 modified-in-place + 14 new (3 standalone + 11 split-derived)
  (2 original IDs retired as split-parents, preserved above for traceability, not counted as active)
```

---

## 23. BS-EA-01..06 accounting

Unaffected by any of the twelve repairs — no repair touched a `BS-EA` disposition directly, though `RC-B6-01`
and `RC-B6-02` strengthen `BS-EA-03`'s and the supersession-adjacent portion of `BS-EA-04`'s closure quality.
Carried forward exactly as v0 left them:

```text
BS-EA-01: RESOLVED (mechanism-level closure) — unaffected
BS-EA-02: REPAIRED, ungoverned — unaffected, still open at WHAT level by design
BS-EA-03: Operational contract now MORE completely closed (concurrency gap closed by REQ-B6-088)
BS-EA-04: Unaffected in its four-value mapping; SUPERSEDED's canonical-authority gap (adjacent territory) now closed
BS-EA-05: OPEN — unaffected, still honestly not fully closed
BS-EA-06: CLOSED FOR CPL'S WHAT — unaffected
```

```text
BS-EA-01..06: 6/6 ACCOUNTED FOR (unchanged from v0; no disposition silently altered)
```

---

## 24. EA-WG accounting

Unaffected by any of the twelve repairs.

```text
EA-WG-01: still deferred to HOW via RM-B6-01 — unaffected
EA-WG-02: still deferred to HOW — unaffected
EA-WG-03: still deferred via RM-B6-03 — unaffected
EA-WG-01..03: 3/3 ACCOUNTED FOR (unchanged)
```

---

## 25. EA-WRC accounting

Unaffected by any of the twelve repairs.

```text
EA-WRC-01: closed operationally via REQ-B6-002 (unchanged) — unaffected
EA-WRC-02: closed operationally via REQ-B6-041 (unchanged) — unaffected
EA-WRC-01/02: 2/2 ACCOUNTED FOR (unchanged, PASS per Challenge §39)
```

---

## 26. RM-B6-01..03 disposition

Per §20 of the repair instruction, none of the twelve repairs required promoting or silently resolving these.
Carried forward exactly as the Challenge confirmed them:

```text
RM-B6-01 (artifact_type mapping):        NON_BLOCKING — unaffected, still open, still correctly non-blocking
RM-B6-02 (parent_execution_id code audit): NON_BLOCKING — unaffected
RM-B6-03 (ExternalReference reuse):          NON_BLOCKING — unaffected
```

---

## 27. Challenge finding closure table

| Finding | Severity | Affected REQ-B6 ID(s) | Repair ID | v0 defect | v0.1 change | Acceptance test | Status |
|---|---|---|---|---|---|---|---|
| RC-B6-01 | MAJOR | REQ-B6-057 | R-B6-R01 | No canonical authority between status and relation | Relation designated canonical, status derived; consistency test added | Zero mismatches in join query; repairs always recompute status from relation | CLOSED |
| RC-B6-02 | MAJOR | §13 (new) | R-B6-R02 | Concurrent-insert race unaddressed | REQ-B6-088 added: catch-and-retrieve on constraint violation | Concurrent test yields one row, no raw error to either caller | CLOSED |
| RC-B6-03 | MAJOR | REQ-B6-015, 077 | R-B6-R03 | Authority collapse (runner report = decision) | REQ-B6-015 rewritten: automatic rule-bound decision satisfies REQ-B6-077 | Every transition has a distinguishable decision record | CLOSED |
| RC-B6-04 | MODERATE | REQ-B6-072 | R-B6-R04 | EA-CI08/09 uncited | Citations + CaseEvent≠RunnerArtifact sentence added | Recomputed coverage shows both cited (§28) | CLOSED |
| RC-B6-05 | MINOR | REQ-B6-082 | R-B6-R05 | Mislabeled "WHAT §36" citation | Relabeled to Requirements Construction Instruction §36 | Citation resolves to a real section | CLOSED |
| RC-B6-06 | MODERATE | REQ-B6-013 | R-B6-R06 | runner_executions_time_chk unclassified | Folded into REQ-B6-013, classified ALIGNED | Constraint named with preservation requirement | CLOSED |
| RC-B6-07 | MODERATE | REQ-B6-032 (dep.) | R-B6-R07 | schema_name/schema_version ungoverned | REQ-B6-089 added | VALIDATED reachable only via objective schema check | CLOSED |
| RC-B6-08 | MINOR | REQ-B6-023 | R-B6-R08 | COMPLETED+zero-artifact case unnamed | Case (a) expanded to (a-i)/(a-ii) | Integration test confirms COMPLETED+zero-artifact accepted | CLOSED |
| RC-B6-09 | MINOR | REQ-B6-008, 032 | R-B6-R09 | Multi-obligation bundling | Split into REQ-B6-008a–g, 032a–d | Each enum value independently testable | CLOSED |
| RC-B6-10 | MINOR | (substrate) | R-B6-R10 | 3 FK RESTRICT behaviors unclassified | Folded into REQ-B6-072/073/074, classified ALIGNED | Delete-while-referenced confirmed blocked for all three | CLOSED |
| RC-B6-11 | MODERATE | REQ-B6-026 (ext.) | R-B6-R11 | Classification mandatoriness/taxonomy undefined | REQ-B6-090 added | 5 validation outcomes independently reachable | CLOSED |
| RC-B6-12 | MODERATE | REQ-B6-066 | R-B6-R12 | B5's 5-category adaptation left open | All 5 categories explicitly dispositioned | All 5 have on-record disposition | CLOSED |

```text
ALL 12 FINDINGS: CLOSED. 0 PARTIAL. 0 FAILED.
```

---

## 28. Repair traceability table

| Repair | Exact source finding | Exact affected requirement(s) | Repair type | Change made | Requirement IDs after repair | Frozen source | Acceptance test | Result |
|---|---|---|---|---|---|---|---|---|
| R-B6-R01 | RC-B6-01 | REQ-B6-057 | REQUIREMENT REWRITE | Canonical-authority designation + consistency test | REQ-B6-057 | WHAT §16 | Zero-mismatch consistency query | APPLIED |
| R-B6-R02 | RC-B6-02 | §13 (new) | NEW DERIVED REQUIREMENT | Concurrency recovery rule | REQ-B6-088 | WHAT §17, schema | Concurrent-submission integration test | APPLIED |
| R-B6-R03 | RC-B6-03 | REQ-B6-015 | REQUIREMENT REWRITE | Automatic rule-bound decision clarification | REQ-B6-015 | WHAT §8/9/25, EA-CI03/13 | Decision-record distinguishability test | APPLIED |
| R-B6-R04 | RC-B6-04 | REQ-B6-072 | TRACEABILITY REPAIR | Added EA-CI08/09 citations + sentence | REQ-B6-072 | WHAT §28 | Recomputed coverage table | APPLIED |
| R-B6-R05 | RC-B6-05 | REQ-B6-082 | TRACEABILITY REPAIR | Corrected citation label | REQ-B6-082 | — | Citation resolves | APPLIED |
| R-B6-R06 | RC-B6-06 | REQ-B6-013 | REQUIREMENT REWRITE | Named + classified time_chk | REQ-B6-013 | schema (migration 011) | Constraint preservation test | APPLIED |
| R-B6-R07 | RC-B6-07 | REQ-B6-032 (dep.) | NEW DERIVED REQUIREMENT | Defined schema_name/schema_version role | REQ-B6-089 | schema, WHAT §19 | Objective schema-check test | APPLIED |
| R-B6-R08 | RC-B6-08 | REQ-B6-023 | ACCEPTANCE-CRITERION REPAIR | Expanded zero-artifact case | REQ-B6-023 | WHAT §11/24 | COMPLETED+zero-artifact acceptance test | APPLIED |
| R-B6-R09 | RC-B6-09 | REQ-B6-008, 032 | REQUIREMENT SPLIT | 2 IDs retired, split into 11 | REQ-B6-008a–g, 032a–d | this challenge §7 | Per-value independent testability | APPLIED |
| R-B6-R10 | RC-B6-10 | (substrate) | TRACEABILITY REPAIR | Named + classified 3 RESTRICT behaviors | REQ-B6-072, 073, 074 | schema (migration 011) | Delete-while-referenced test | APPLIED |
| R-B6-R11 | RC-B6-11 | REQ-B6-026 (ext.) | NEW DERIVED REQUIREMENT | Mandatoriness + 5-way validation taxonomy | REQ-B6-090 | WHAT §11 | 5-outcome integration test | APPLIED |
| R-B6-R12 | RC-B6-12 | REQ-B6-066 | ACCEPTANCE-CRITERION REPAIR | Explicit 5-category disposition | REQ-B6-066 | WHAT §23 | All 5 categories dispositioned | APPLIED |

No repair disappeared. All twelve applied.

---

## 29. Regression self-check

```text
NEW_ISSUE_DISCOVERED_DURING_REPAIR: NONE
```

No unexpected issue was found while applying the twelve repairs; each stayed within the exact bounds its
Challenge finding specified.

```text
REPAIR_REGRESSION_CHECK = PASS
```

Verified none of the twelve repairs altered:

- **RunnerExecution ontology** — REQ-B6-015's rewrite touches decision-record mechanics only, not §6a
  identity. Untouched.
- **RunnerArtifact ontology** — REQ-B6-057's rewrite adds canonical-authority coordination, not a
  redefinition of what a RunnerArtifact is (§10). Untouched.
- **Artifact multidimensional classification** — REQ-B6-090 adds mandatoriness and a validation taxonomy but
  explicitly preserves the three dimensions' independence and confirms no contradictory combination is
  currently defined. Untouched.
- **parent_execution_id boundary** — Not referenced by any of the twelve repairs. Untouched.
- **Case boundary** — REQ-B6-072's extension adds citations and a RESTRICT clause; no B5 semantic change.
  Untouched.
- **Asset boundary** — REQ-B6-073's extension adds a RESTRICT clause; no B4 semantic change. Untouched.
- **B3 identity boundary** — REQ-B6-074's extension adds a RESTRICT clause; no Actor/Role concept introduced.
  Untouched.
- **VIR authority** — Not referenced by any repair. Untouched.
- **PGDR authority** — Not referenced by any repair. Untouched.
- **Generic-workflow exclusion** — REQ-B6-088 (concurrency) is scoped strictly to insert-race recovery, no
  scheduling/orchestration concept introduced. Untouched.
- **Generic-lineage exclusion** — No repair references `parent_execution_id` or introduces a lineage concept.
  Untouched.

---

## 30. Recomputed coverage statistics

Recomputed from the v0.1 matrix directly, not copied from v0's (partially incorrect) self-report.

```text
TOTAL REQUIREMENTS: 99
TRACEABLE: 99/99

ACTIVE EA-CI: 19
ACTIVE EA-CI FULLY COVERED: 19/19
```

| Invariant | Citing requirement(s) after repair | Coverage |
|---|---|---|
| EA-CI01 | REQ-B6-001, 068 | FULL |
| EA-CI02 | REQ-B6-008e, 067, 068 | FULL |
| EA-CI03 | REQ-B6-008d, 009, 015, 067 | FULL |
| EA-CI04 | REQ-B6-016, 031, 033, 069 | FULL |
| EA-CI05 | REQ-B6-026 | FULL |
| EA-CI06 | REQ-B6-018, 019, 021, 056 | FULL |
| EA-CI07 | REQ-B6-024 | FULL (unchanged — no repair targeted this; adequate, not upgraded) |
| **EA-CI08** | **REQ-B6-072 (repaired)** | **FULL — was MISSING, now closed by R-B6-R04** |
| **EA-CI09** | **REQ-B6-072 (repaired)** | **FULL — was MISSING, now closed by R-B6-R04** |
| EA-CI10 | REQ-B6-014 | FULL |
| EA-CI11 | REQ-B6-031, 048, 056 | FULL |
| EA-CI12 | REQ-B6-062 | FULL |
| EA-CI13 | REQ-B6-015 (repaired), 016, 060, 069 | FULL |
| EA-CI14 | — (retired, merged into EA-CI03) | FULL by design |
| EA-CI15 | REQ-B6-016, 069 | FULL |
| EA-CI16 | REQ-B6-003, 041 | FULL |
| EA-CI17 | REQ-B6-006, 043 | FULL |
| EA-CI18 | REQ-B6-001, 002, 003, 006, 041 | FULL |
| EA-CI19 | REQ-B6-026 | FULL |

```text
BS-EA-01..06: 6/6 ACCOUNTED FOR
EA-WG-01..03: 3/3 ACCOUNTED FOR
EA-WRC-01/02: 2/2 ACCOUNTED FOR
```

19/19 is now independently justified by actual per-requirement citations (verifiable by direct grep of the
repaired file), not asserted — this is the correction of v0's overclaimed statistic that the Challenge caught.
`EA-CI07`'s coverage remains adequate-but-thin (only REQ-B6-024 cites it, not the more directly relevant
REQ-B6-023) — this was not among the twelve authorized repairs and is therefore left untouched per the
bounded-repair discipline, not silently improved.

---

## 31. Re-Challenge readiness

```text
REQUIREMENTS_STATUS = RECHALLENGE_READY
```

All twelve repairs applied and closed. No regression found. No new issue discovered during repair. The
recomputed 19/19 EA-CI coverage is independently verifiable, not asserted. `AUTHORITY_BOUNDARY`,
`IDEMPOTENCY_CONTRACT`, and `REQ-B6-057` — the three blocking findings — are each REPAIRED with a concrete
mechanism, not merely reworded.

```text
REQUIREMENTS FREEZE: NOT GRANTED
```

Per §28 of the repair instruction, this remains true even with all twelve repairs successful — an independent
targeted Re-Challenge of exactly `R-B6-R01`–`R-B6-R12` (not a full re-challenge of all 99 requirements) is
required before Freeze can be considered.

---

## 32. Recommended next governance action

```text
B6_EXECUTION_ARTIFACT_REQUIREMENT_RECHALLENGE_v0.1
```

---

## B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1

```text
GOVERNANCE BASELINE:
  647a91543dc4f72627370c29d111c897662816f9

FROZEN WHAT:
  docs/build/CPL_EA_WHAT_v0.1.md

FROZEN WHAT COMMIT:
  e7d51842043408cccd97bf3811de73c756784849

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

MIGRATION HEAD:
  026

ORIGINAL MATRIX:
  87 requirements

R-B6-R01:
  APPLIED

R-B6-R02:
  APPLIED

R-B6-R03:
  APPLIED

R-B6-R04:
  APPLIED

R-B6-R05:
  APPLIED

R-B6-R06:
  APPLIED

R-B6-R07:
  APPLIED

R-B6-R08:
  APPLIED

R-B6-R09:
  APPLIED

R-B6-R10:
  APPLIED

R-B6-R11:
  APPLIED

R-B6-R12:
  APPLIED

CHALLENGE FINDINGS CLOSED:
  12/12

V0.1 REQUIREMENT COUNT:
  99

TRACEABILITY:
  99/99

ACTIVE EA-CI COVERAGE:
  19/19

AUTHORITY BOUNDARY:
  REPAIRED

IDEMPOTENCY CONTRACT:
  REPAIRED

REQ-B6-057:
  REPAIRED

RM-B6-01:
  NON_BLOCKING

RM-B6-02:
  NON_BLOCKING

RM-B6-03:
  NON_BLOCKING

REPAIR REGRESSION CHECK:
  PASS

REQUIREMENTS STATUS:
  RECHALLENGE_READY

REQUIREMENTS FREEZE:
  NOT GRANTED

EXECUTION MANDATE:
  NOT AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED

NEXT GOVERNANCE ACTION:
  B6_EXECUTION_ARTIFACT_REQUIREMENT_RECHALLENGE_v0.1
```

**STOP.** This artifact does not conduct the Re-Challenge, does not reopen any requirement that passed
Challenge cleanly, does not modify the frozen WHAT, does not freeze requirements, and creates no Execution
Mandate, candidate branch, schema change, migration, or CPL/VIR/PGDR code change.

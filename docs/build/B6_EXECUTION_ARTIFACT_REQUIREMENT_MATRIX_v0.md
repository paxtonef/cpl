# B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0

## 1. Executive summary

This matrix derives the requirement set necessary to implement and verify the frozen
`B6_EXECUTION_ARTIFACT_GOVERNANCE` WHAT. It does not reinterpret the WHAT. Every requirement traces to a
WHAT section, a candidate invariant (`EA-CI`), a `BS-EA` disposition assigned to Requirements, an `EA-WG`
gap, an `EA-WRC` finding, or an existing executable constraint that must be governed without contradicting
the WHAT. Requirements resolve **operational** questions the WHAT deliberately left open (scope of a key,
duplicate behavior, transition validity, mechanism choice where the WHAT says "Requirements/HOW"); they do
not resolve **conceptual** questions the WHAT already froze (what a `RunnerExecution` *is*, whether
artifact classification is multidimensional, whether `idempotency_key` is identity).

The live schema (migrations 011/012, extracted at commit `3092d7c` via full repository archive, not
reconstructed from memory) surfaced one genuine tension not visible from the WHAT text alone: the executable
`artifact_status` CHECK constraint already includes a `SUPERSEDED` value, sitting alongside the schema-level
`supersedes_artifact_id` link the WHAT names as the supersession substrate. This matrix classifies that
overlap explicitly (§18) rather than silently picking one mechanism.

Total requirements: 87 (`REQ-B6-001`–`087`). No arbitrary target was set; this is the count produced by
working section-by-section through the WHAT's own scope. See §32 for coverage statistics.

---

## 2. Canonical baselines

```text
Governance HEAD:              3092d7c69e59191fdfc945304fd71d5a8bf0b08d
CPL software baseline:         2ac075daea7d162825ed73ded0c7548011242a8f
Migration head:                  026
Frozen WHAT:                       docs/build/CPL_EA_WHAT_v0.1.md @ e7d5184204340840cccd97bf3811de73c756784849
WHAT Re-Challenge:                    docs/build/CPL_EA_WHAT_RECHALLENGE_v0.1.md @ 3eb76f115a9052a2a2861a71180e56f25a571981
Freeze + Admission:                      docs/build/CPL_EA_WHAT_FREEZE_AND_ADMISSION_v0.md @ 3092d7c69e59191fdfc945304fd71d5a8bf0b08d
Build Unit:                                 B6_EXECUTION_ARTIFACT_GOVERNANCE — ADMITTED
Requirements construction:                     AUTHORIZED
Implementation:                                   NOT AUTHORIZED
```

Baseline re-verified via `git ls-remote` against the real GitHub repository immediately before drafting
this matrix; HEAD confirmed unchanged at `3092d7c69e59191fdfc945304fd71d5a8bf0b08d` both before and after
the drafting session.

---

## 3. Frozen WHAT sources consulted

`CPL_EA_WHAT_v0.1.md` §§1–30 (full document read, not excerpted from memory); `CPL_EA_WHAT_RECHALLENGE_v0.1.md`
§§16–20 (`EA-WRC-01`, `EA-WRC-02`, final verdict); `migrations/versions/011_create_runner_executions.py` and
`012_create_runner_artifacts.py` (exact DDL, extracted from repository archive at the frozen commit — not
guessed from the resume's field-name summary).

---

## 4. Requirements methodology

For every WHAT section that leaves an operational question open, this matrix asks three questions in order:

1. **Is this question already answered by an existing executable constraint** (CHECK, FK, unique index)? If
   yes, the requirement's job is to *preserve* that constraint's behavior and make it testable, not invent a
   new one.
2. **Is this question explicitly assigned to Requirements** by a `BS-EA`/`EA-WG` disposition or a WHAT
   passage saying "Requirements/HOW"? If yes, resolve it here, at the operational level only.
3. **Would resolving this question require assigning meaning the WHAT withheld** (e.g., `parent_execution_id`
   semantics, `artifact_status`'s domain-acceptance reading)? If yes, this matrix issues a *negative*
   requirement instead — a requirement that a certain meaning must NOT be assigned — and defers the positive
   question to a later WHAT-level action.

---

## 5. Traceability model

Each requirement below states its `Source` (document + section/invariant/gap identifier) inline. Three
consolidated traceability tables appear at §27–§29: `BS-EA-01..06`, `EA-WG-01..03`, `EA-WRC-01/02`. A
requirement with no traceable source is malformed per this methodology and would be struck before Freeze;
none below lacks one.

---

## 6. RunnerExecution identity requirements

**REQ-B6-001** `IDENTITY` — Identity independent of request/input
Source: WHAT §6a; EA-CI18, EA-CI01 | Authority: CPL (representation only) | Object: RunnerExecution
Statement: A materialized `RunnerExecution` row's identity (`execution_id`) SHALL be independent of the
request that produced it and independent of that request's input payload; two executions with identical
input are two distinct identities unless REQ-B6-004 (governed replay) applies.
Verification: STATIC SCHEMA INSPECTION (PK independent of payload columns); INTEGRATION TEST (two identical
requests, no replay rule active, yield two distinct `execution_id`s)
Acceptance: Test produces two distinct UUIDs for two identical, non-replayed requests | Failure: A single
`execution_id` is reused or derived from request/input content
Notes: None

**REQ-B6-002** `IDENTITY` — Identity independent of Case, Asset, and runner type
Source: WHAT §6a; EA-CI18 (as clarified by EA-WRC-01's note that Asset/artifact were named in the identity
mandate but omitted from §6a's negation list — treated here as in-scope regardless of the documentation gap)
| Authority: CPL | Object: RunnerExecution
Statement: `execution_id` SHALL NOT be derived from, or made functionally interchangeable with, `case_id`,
`asset_id`, or `runner_type`; same-Case, same-Asset, or same-runner-type SHALL NOT by themselves establish
execution identity equivalence.
Verification: INTEGRATION TEST (same case_id + asset_id + runner_type, distinct requests → distinct
execution_id, absent a replay rule)
Acceptance: Distinct rows produced | Failure: Any code path treats (case_id, asset_id, runner_type) as a
de-facto execution key
Notes: Closes the EA-WRC-01 documentation gap operationally, without amending the WHAT text itself

**REQ-B6-003** `IDENTITY` — Identity independent of artifact and idempotency key
Source: WHAT §6a, §17; EA-CI18, EA-CI16 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: `execution_id` SHALL NOT be derived from any `RunnerArtifact.artifact_id` it produces, and SHALL
NOT be derived from or aliased to `idempotency_key`. The reverse direction is separately required at
REQ-B6-018.
Verification: STATIC SCHEMA INSPECTION (no FK/derivation path from artifact_id or idempotency_key into
execution_id); TRACEABILITY REVIEW
Acceptance: No such derivation path exists | Failure: Any lookup treats idempotency_key or an artifact_id as
sufficient to construct or substitute for execution_id
Notes: Direct implementation of the WHAT's explicit `IDEMPOTENCY KEY ≠ RUNNEREXECUTION IDENTITY` boundary

**REQ-B6-004** `RELATION` — New attempt vs. governed replay retrieval
Source: WHAT §6a | Authority: CPL | Object: RunnerExecution
Statement: A new execution attempt SHALL receive a new `execution_id` unless an explicit, named governed
rule establishes that the operation is a replay retrieval of an already-existing `RunnerExecution`. Absent
such a named rule, the default outcome SHALL be creation of a new `RunnerExecution`.
Verification: INTEGRATION TEST; TRACEABILITY REVIEW (every replay path in code must cite a named rule)
Acceptance: No un-cited code path returns an existing execution instead of creating a new one | Failure: An
implicit or undocumented replay occurs
Notes: The only governed replay rule this matrix currently defines is the idempotency-key duplicate-
submission rule at REQ-B6-036; any future replay rule requires the same explicit-naming discipline

**REQ-B6-005** `IDENTITY` — Observable distinction of the four identity scenarios
Source: WHAT §6a, §17 | Authority: CPL | Object: RunnerExecution
Statement: The system SHALL make the following four scenarios independently observable (via response shape,
audit log, or equivalent): (A) new execution attempt; (B) replay retrieval of an existing execution; (C)
duplicate submission (same idempotency scope, materially different intent — see REQ-B6-038); (D) retry that
creates a new execution attempt after a prior technical failure.
Verification: INTEGRATION TEST, one case per scenario | Acceptance: All four scenarios produce distinguishable
observable outcomes | Failure: Two or more scenarios are indistinguishable to a caller
Notes: Does not mandate specific response fields — mechanism is HOW

**REQ-B6-006** `NEGATIVE / PROHIBITION` — Retry not defined through parent_execution_id
Source: WHAT §18; EA-CI17, EA-CI18 (BS-EA-02) | Authority: CPL | Object: RunnerExecution
Statement: Retry (REQ-B6-005 scenario D) SHALL NOT be defined, detected, or inferred through
`parent_execution_id`. Retry identity discipline is governed exclusively by REQ-B6-001–005 and, where
applicable, the idempotency contract (§13).
Verification: STATIC SCHEMA INSPECTION, TRACEABILITY REVIEW (no retry logic reads parent_execution_id)
Acceptance: No such dependency exists | Failure: Any retry-detection logic branches on parent_execution_id
Notes: Cross-referenced at §14 (parent_execution_id negative requirements)

---

## 7. Execution lifecycle requirements

**REQ-B6-007** `LIFECYCLE` — execution_status represents representation state only
Source: WHAT §8; EA-CI02, EA-CI03 | Authority: CPL (representation), NOT domain | Object: RunnerExecution
Statement: `execution_status` SHALL represent only the state of the CPL-governed execution representation.
No value of `execution_status` SHALL be documented, surfaced, or coded as evidence that a runner's domain
conclusion was correct, accepted, or true.
Verification: STATIC SCHEMA INSPECTION (enum semantics doc); DOMAIN-BOUNDARY REVIEW
Acceptance: Documentation and code comments for every enum value state the representation-only meaning |
Failure: Any value's documented meaning implies domain acceptance
Notes: None

**REQ-B6-008** `ONTOLOGY-CONFORMANCE` — Governing the existing 7-value vocabulary
Source: WHAT §23 (vocabulary is Requirements-phase) | Authority: CPL | Object: RunnerExecution
Statement: The existing executable `execution_status` vocabulary — `CREATED`, `QUEUED`, `RUNNING`,
`COMPLETED`, `FAILED`, `BLOCKED`, `CANCELLED` (per `runner_executions_status_chk`, migration 011) — SHALL be
adopted as the governed vocabulary for this Build Unit, classified per §31's discipline rather than assumed
correct merely because it exists in code.
Classification: `CREATED`/`QUEUED`/`RUNNING` — ALIGNED (pre-terminal representation states, no domain
overlap); `COMPLETED`/`FAILED` — ALIGNED, subject to REQ-B6-007's non-interpretation discipline;
`CANCELLED` — REQUIRES REQUIREMENT-LEVEL SEMANTICS (WHAT §23 lists cancellation as "only if supported"; this
matrix confirms it IS supported and requires REQ-B6-011 below); `BLOCKED` — REQUIRES REQUIREMENT-LEVEL
SEMANTICS (not named in WHAT §23's illustrative list at all; requires REQ-B6-012 below).
Verification: STATIC SCHEMA INSPECTION | Acceptance: Every one of the 7 values has an explicit, WHAT-
conformant semantic mapping before Freeze | Failure: A value ships without one
Notes: This requirement itself performs the §31 classification; it does not defer it to the gap register,
because the DDL was available and inspected directly

**REQ-B6-009** `LIFECYCLE` — Valid transition table
Source: WHAT §8, §9 (Requirements-level); EA-CI03 | Authority: CPL | Object: RunnerExecution
Statement: Requirements define the following minimum valid-transition set over the 7-value vocabulary:
`CREATED → QUEUED | RUNNING | BLOCKED | CANCELLED | FAILED`; `QUEUED → RUNNING | BLOCKED | CANCELLED |
FAILED`; `RUNNING → COMPLETED | FAILED | BLOCKED | CANCELLED`; `BLOCKED → RUNNING | CANCELLED | FAILED`;
`COMPLETED`, `FAILED`, `CANCELLED` are terminal (no outbound transition). Any transition not in this set
SHALL be rejected.
Verification: INTEGRATION TEST (each listed transition succeeds; each terminal state rejects all outbound
attempts) | Acceptance: Transition table enforced at the write path | Failure: A non-listed transition
succeeds, or a terminal state accepts a further transition
Notes: This table is a Requirements-level minimum; HOW may implement it via CHECK constraint, application
logic, or a state-machine library

**REQ-B6-010** `LIFECYCLE` — Repeated transition requests are idempotent, not erroring
Source: WHAT §9 (Requirements-level, "whether repeated transition requests are replay/idempotent or
invalid") | Authority: CPL | Object: RunnerExecution
Statement: A transition request that would move `execution_status` to the value it already holds SHALL be
treated as an idempotent no-op (success, no state change, no error), not as an invalid transition.
Verification: INTEGRATION TEST | Acceptance: Repeating an already-applied transition returns success without
mutating history | Failure: Repetition errors or is logged as a distinct transition event
Notes: None

**REQ-B6-011** `LIFECYCLE` — CANCELLED semantics
Source: WHAT §23 ("cancellation, only if supported") | Authority: CPL, initiated by governed request only |
Object: RunnerExecution
Statement: `CANCELLED` SHALL represent that CPL's governed representation was terminated before runner
completion, at the request of a governed actor or a governed system rule (e.g., authority revocation) — it
SHALL NOT represent, and SHALL NOT be inferred from, the runner reporting a domain-negative result.
Verification: DOMAIN-BOUNDARY REVIEW; INTEGRATION TEST (cancellation only reachable via an explicit governed
cancel action, never inferred from runner response content)
Acceptance: No code path sets CANCELLED from runner response parsing | Failure: Runner output content drives
a CANCELLED transition
Notes: Distinguishes CANCELLED from FAILED (technical) and from any future domain-rejection representation
(explicitly out of B6 scope per REQ-B6-060)

**REQ-B6-012** `LIFECYCLE` — BLOCKED semantics
Source: WHAT §23 (nearest analogue: "execution not authorized" / conceptual distinctions listed but not
frozen to exact vocabulary) | Authority: CPL | Object: RunnerExecution
Statement: `BLOCKED` SHALL represent that a materialized `RunnerExecution` exists but cannot proceed pending
a governed precondition (e.g., authority not yet granted, a dependency not yet satisfied that is itself
CPL-governed) — it SHALL NOT represent a technical failure (`FAILED`) and SHALL NOT represent a runner-
reported domain state.
Verification: DOMAIN-BOUNDARY REVIEW; TRACEABILITY REVIEW (every BLOCKED-setting code path names its
precondition)
Acceptance: Every BLOCKED transition is traceable to a named, CPL-governed precondition | Failure: BLOCKED is
set from ambiguous or domain-originated signals
Notes: `BLOCKED` was not in the WHAT's illustrative list (§23); this requirement is the operational closure
of that gap, staying within the WHAT's conceptual boundary (technical/representation state only)

**REQ-B6-013** `INTEGRITY` — completed_at enforcement is preserved, not re-invented
Source: existing constraint `runner_executions_completed_at_chk` (migration 011); classified ALIGNED per §31
| Authority: CPL | Object: RunnerExecution
Statement: The existing constraint that `execution_status = 'COMPLETED'` requires `completed_at IS NOT NULL`
SHALL be preserved by any Requirements-level transition logic (REQ-B6-009); Requirements SHALL NOT introduce
a code path that can set `COMPLETED` without populating `completed_at`, even redundantly with the DB
constraint.
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST (application-level attempt to set COMPLETED without
completed_at fails before or at the DB layer)
Acceptance: No path bypasses the constraint | Failure: A path exists that violates it (e.g., via a different
connection role or a migration-level constraint drop)
Notes: This requirement exists because Requirements MUST NOT silently assume an executable fact continues to
hold — it must be named and preserved explicitly, per this instruction's own discipline

---

## 8. Execution authority requirements

**REQ-B6-014** `AUTHORITY` — Initiator distinct from authority
Source: WHAT §22; EA-CI10 | Authority: CPL (attribution only) | Object: RunnerExecution
Statement: Recording `initiated_by_contact_id` SHALL NOT itself authorize the execution. Authorization SHALL
be a separate, explicitly governed decision (REQ-B6-076).
Verification: DOMAIN-BOUNDARY REVIEW; INTEGRATION TEST (an execution record with an initiator but no
authority decision cannot reach RUNNING)
Acceptance: RUNNING is unreachable without a separate authority decision | Failure: Initiator presence alone
permits progression to RUNNING
Notes: None

**REQ-B6-015** `AUTHORITY` — Runner report distinct from canonical governance decision
Source: WHAT §8, §9; EA-CI03, EA-CI13 | Authority: CPL (representation), domain runner (report only) |
Object: RunnerExecution
Statement: A runner's self-reported completion/failure signal SHALL be recorded as `execution_status` only;
it SHALL NOT, by itself, constitute a canonical governance decision requiring separate authority-gated
approval — recording the report and governing the representation transition are the same act at this layer.
Verification: DOMAIN-BOUNDARY REVIEW | Acceptance: No redundant "approve the runner's report" governance
step is introduced where the WHAT does not require one | Failure: An unjustified extra approval gate is added
Notes: Prevents over-engineering a governance layer the WHAT does not call for

**REQ-B6-016** `AUTHORITY` — CPL representation authority distinct from domain truth authority
Source: WHAT §9; EA-CI04, EA-CI13, EA-CI15 | Authority: CPL (representation), VIR/PGDR (domain truth) |
Object: RunnerExecution, RunnerArtifact
Statement: No mutation governed by this Build Unit SHALL require, imply, or be conditioned on CPL's agreement
with the runner's domain conclusion; CPL's authority is limited to admitting, transitioning, and correcting
the *representation*.
Verification: DOMAIN-BOUNDARY REVIEW across all mutation paths | Acceptance: No mutation path branches on
domain-conclusion correctness | Failure: One does
Notes: Cross-referenced at §21

**REQ-B6-017** `AUTHORITY` — Authority boundary specified per mutation type
Source: WHAT §9, §22, §25 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: For each governed mutation type (execution admission, lifecycle transition, artifact registration,
artifact correction/supersession), Requirements SHALL name the required authority boundary (see §23) before
Freeze; no mutation type SHALL ship without one named.
Verification: TRACEABILITY REVIEW | Acceptance: All four mutation types have a named authority boundary
(REQ-B6-076–079) | Failure: One is missing
Notes: None

---

## 9. RunnerArtifact identity requirements

**REQ-B6-018** `IDENTITY` — Identity independent of payload, hash, type, classification, execution, storage
Source: WHAT §10; EA-CI06 | Authority: CPL | Object: RunnerArtifact
Statement: `artifact_id` SHALL be independent of `payload` content, `content_hash`, `artifact_type`, any
classification dimension value (§11), the producing `execution_id`, and any storage location or external
reference. Same content hash, same payload, or same execution SHALL NOT by themselves establish artifact
identity equivalence.
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST (two artifacts with identical payload/hash from the
same execution receive distinct artifact_ids unless explicitly deduplicated by a named rule — no such rule
exists in this Build Unit)
Acceptance: Distinct IDs produced | Failure: Any dedup-by-content behavior exists without a named governing
rule
Notes: None

**REQ-B6-019** `IDENTITY` — Content hash is integrity evidence, not identity
Source: WHAT §10; EA-CI06 | Authority: CPL | Object: RunnerArtifact
Statement: `content_hash` (paired with `hash_algorithm` per `runner_artifacts_hash_pair_chk`) SHALL be treated
exclusively as integrity evidence (§17). No code path SHALL use `content_hash` as a lookup key for artifact
identity or as a substitute primary key.
Verification: STATIC SCHEMA INSPECTION (no unique index on content_hash exists; none SHALL be added for
identity purposes) | Acceptance: Confirmed | Failure: A content_hash-keyed lookup path is added for identity
purposes
Notes: None

**REQ-B6-020** `INTEGRITY` — Hash pairing constraint preserved
Source: existing constraint `runner_artifacts_hash_pair_chk` (migration 012); ALIGNED per §31 | Authority:
CPL | Object: RunnerArtifact
Statement: The existing both-null-or-both-not-null pairing of `hash_algorithm`/`content_hash` SHALL be
preserved; Requirements SHALL NOT introduce a write path that populates one without the other.
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST | Acceptance: No such path exists | Failure: One
exists
Notes: None

**REQ-B6-021** `IDENTITY` — Identity stable across supersession
Source: WHAT §16; EA-CI06 | Authority: CPL | Object: RunnerArtifact
Statement: A superseding artifact SHALL receive a new, distinct `artifact_id`; it SHALL NOT inherit, alias,
or overwrite the superseded artifact's `artifact_id`. The relation is expressed solely via
`supersedes_artifact_id` on the new row.
Verification: STATIC SCHEMA INSPECTION (`runner_artifacts_not_self_superseded_chk` already prevents self-
reference; confirms this direction) | Acceptance: Distinct IDs, correct backlink direction | Failure:
Identity reuse across supersession
Notes: None

**REQ-B6-022** `RELATION` — execution_id required, no orphan artifacts
Source: schema (migration 012, `execution_id NOT NULL`, FK RESTRICT) | Authority: CPL | Object: RunnerArtifact
Statement: Every `RunnerArtifact` SHALL reference an existing `RunnerExecution` via `execution_id`; no
artifact SHALL exist without an owning execution. This is already enforced by `NOT NULL` + FK; this
requirement makes it a governed, tested Requirements-level fact rather than an incidental schema property.
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST (write without execution_id rejected)
Acceptance: Rejected as expected | Failure: A code path bypasses the constraint (e.g., via raw SQL)
Notes: Directly answers §40 ("artifact without execution") — answer is NO, by existing enforced constraint

---

## 10. Execution ↔ Artifact multiplicity requirements

**REQ-B6-023** `RELATION` — Zero, one, or many artifacts per execution
Source: WHAT §11, §24 (BS-EA-01, RESOLVED) | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: A single `RunnerExecution` SHALL support zero, one, or many `RunnerArtifact` rows without any
Build-Unit-imposed upper bound; no requirement in this matrix SHALL force a single-output runner model.
Verification: INTEGRATION TEST, three cases: (a) execution with zero artifacts (e.g., technical failure
before output); (b) execution with exactly one artifact; (c) execution with multiple, independently
identified artifacts
Acceptance: All three cases succeed | Failure: Any case is structurally blocked
Notes: BS-EA-01 is RESOLVED at WHAT level; this requirement is the mechanism-level closure, not a semantic
reopening

**REQ-B6-024** `RELATION` — Multiple artifacts remain independently governed
Source: WHAT §11, §24; EA-CI07 | Authority: CPL | Object: RunnerArtifact
Statement: Where one execution produces multiple artifacts, each SHALL have independent identity (§9),
independent classification (§11), independent provenance (§15), independent integrity treatment (§17), and
independent correction/supersession eligibility (§18) — no shared-state shortcut SHALL couple their lifecycles.
Verification: INTEGRATION TEST (correcting/superseding one of several sibling artifacts does not affect the
others) | Acceptance: Sibling artifacts unaffected | Failure: A correction cascades unintentionally
Notes: None

**REQ-B6-025** `NEGATIVE / PROHIBITION` — No reification of ExecutionArtifactRelation as a new object
Source: WHAT §24 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: The 1:N relationship between `RunnerExecution` and `RunnerArtifact` SHALL continue to be expressed
solely via `RunnerArtifact.execution_id`; this Requirements phase SHALL NOT introduce a new join table or
relation object.
Verification: STATIC SCHEMA INSPECTION | Acceptance: No such object is introduced | Failure: One is
Notes: None

---

## 11. Artifact classification requirements

**REQ-B6-026** `CLASSIFICATION` — Three independent, coexisting dimensions
Source: WHAT §11; EA-CI05, EA-CI19 | Authority: CPL | Object: RunnerArtifact
Statement: Artifact classification SHALL be represented along exactly three dimensions — (A) semantic
function, (B) production/lifecycle role, (C) consumption/presentation role — each independently settable, none
forcing exclusivity with the others.
Verification: STATIC SCHEMA INSPECTION (mechanism permits independent per-dimension values); INTEGRATION TEST
(the canonical PGDR combination `FINAL` + `DOMAIN DETERMINATION CARRIER` + non-`PRODUCT_DISPLAYABLE` is
representable without contradiction)
Acceptance: Combination representable | Failure: Dimensions are mutually exclusive in the chosen mechanism
Notes: None

**REQ-B6-027** `CLASSIFICATION` — Minimum vocabulary, dimension A (semantic function)
Source: WHAT §11 | Authority: CPL | Object: RunnerArtifact
Statement: Dimension A SHALL support, at minimum: execution output carrier; execution evidence carrier;
domain assertion carrier; domain determination carrier; technical/operational material.
Verification: STATIC SCHEMA INSPECTION | Acceptance: All five values representable | Failure: One is missing
Notes: Additional values MAY be added later without WHAT amendment, since §11 does not freeze exhaustiveness

**REQ-B6-028** `CLASSIFICATION` — Minimum vocabulary, dimensions B and C
Source: WHAT §11 | Authority: CPL | Object: RunnerArtifact
Statement: Dimension B SHALL support, at minimum, `INTERMEDIATE` and `FINAL`. Dimension C SHALL support, at
minimum, `INTERNAL` and `PRODUCT_DISPLAYABLE`.
Verification: STATIC SCHEMA INSPECTION | Acceptance: Both minimum sets representable | Failure: Either is
incomplete
Notes: None

**REQ-B6-029** `NEGATIVE / PROHIBITION` — Payload format does not define semantic class
Source: WHAT §11, §14 | Authority: CPL | Object: RunnerArtifact
Statement: `payload`'s JSON structure or `artifact_type`'s string value SHALL NOT be used as an implicit
default for, or substitute for, dimension A classification. Classification SHALL be an explicit, separately
set value.
Verification: TRACEABILITY REVIEW (no code path infers dimension A from payload shape or artifact_type
string alone) | Acceptance: None found | Failure: One found
Notes: `artifact_type` (existing schema column) is reconciled with dimension A at REQ-B6-030, not treated as
its automatic source

**REQ-B6-030** `ONTOLOGY-CONFORMANCE` — Reconciling artifact_type with the classification model
Source: schema (migration 012, `artifact_type NOT NULL`); WHAT §11 | Authority: CPL | Object: RunnerArtifact
Statement: Requirements SHALL state explicitly, before Freeze, whether the existing free-text `artifact_type`
column maps to dimension A (with a defined, closed value set), is retired in favor of the new mechanism, or
coexists with a documented, non-overlapping purpose (e.g., a coarse runner-facing label distinct from CPL's
classification). This matrix does not resolve which — see RM-B6-01.
Verification: TRACEABILITY REVIEW at Freeze | Acceptance: An explicit choice is documented | Failure: The
column's relationship to dimension A remains undocumented at Freeze
Notes: Open item — see Gap Register §31

---

## 12. artifact_status requirements

**REQ-B6-031** `NEGATIVE / PROHIBITION` — No domain-acceptance reading
Source: WHAT §19 (BS-EA-04); EA-CI04, EA-CI11 | Authority: CPL | Object: RunnerArtifact
Statement: No value of `artifact_status` SHALL be documented or coded as meaning that the artifact's domain
content was accepted as true. This applies to every one of the four existing enum values without exception.
Verification: DOMAIN-BOUNDARY REVIEW | Acceptance: No such documented meaning exists | Failure: One does
Notes: None

**REQ-B6-032** `ONTOLOGY-CONFORMANCE` — Governing the existing 4-value vocabulary
Source: schema (`runner_artifacts_status_chk`, migration 012: `CREATED`, `VALIDATED`, `SUPERSEDED`,
`REJECTED`); WHAT §19 | Authority: CPL | Object: RunnerArtifact
Statement: Each of the four existing values SHALL be assigned a Requirements-level meaning consistent with
REQ-B6-031: `CREATED` = persisted, not yet structurally checked; `VALIDATED` = passed CPL-side structural
validation (schema/type conformance of `payload`, per `schema_name`/`schema_version`) — explicitly NOT domain
acceptance; `SUPERSEDED` = see REQ-B6-057 (interacts with §18's correction model — flagged, not silently
adopted); `REJECTED` = see REQ-B6-033.
Verification: STATIC SCHEMA INSPECTION; DOMAIN-BOUNDARY REVIEW | Acceptance: All four values mapped and
documented | Failure: Any value ships without an explicit, WHAT-conformant meaning
Notes: This is the §31 classification act for `artifact_status`

**REQ-B6-033** `NEGATIVE / PROHIBITION` — REJECTED is structural, never domain rejection
Source: WHAT §19; EA-CI04 | Authority: CPL (structural), NOT domain | Object: RunnerArtifact
Statement: `REJECTED` SHALL mean only that CPL declined to canonically register the artifact for a structural
reason (e.g., schema/type validation failure at the JSONB boundary, per REQ-B6-040 in §18). `REJECTED` SHALL
NOT be set, inferred, or documented as meaning that a domain authority rejected the artifact's content; any
domain-level rejection is represented entirely outside `artifact_status`, per WHAT §16 category D/E.
Verification: DOMAIN-BOUNDARY REVIEW; TRACEABILITY REVIEW (every REJECTED-setting path names a structural
failure reason) | Acceptance: All such paths do | Failure: One sets REJECTED from a domain signal
Notes: This is the genuine ambiguity surfaced by reading the live DDL directly — `REJECTED` is not named or
discussed anywhere in the WHAT text, and without this requirement it would be the most likely value to drift
into a domain-acceptance meaning the WHAT explicitly prohibits

**REQ-B6-034** `LIFECYCLE` — artifact_status transition table
Source: WHAT §19 (HOW-adjacent, scoped operational) | Authority: CPL | Object: RunnerArtifact
Statement: Requirements define the minimum valid-transition set: `CREATED → VALIDATED | REJECTED`;
`VALIDATED → SUPERSEDED`; `REJECTED` and `SUPERSEDED` are terminal. Transitions not in this set SHALL be
rejected.
Verification: INTEGRATION TEST | Acceptance: Table enforced | Failure: A non-listed transition succeeds
Notes: `SUPERSEDED` reachable only from `VALIDATED`, consistent with REQ-B6-057's requirement that only a
registered (validated) artifact can be superseded

---

## 13. Idempotency / replay / retry requirements

**REQ-B6-035** `IDEMPOTENCY` — Scope bound to the enforced constraint
Source: WHAT §17 (BS-EA-03); schema (`runner_executions_idempotency_uq`, migration 011) | Authority: CPL |
Object: RunnerExecution
Statement: `idempotency_key`'s uniqueness scope SHALL be exactly `(runner_type, idempotency_key)`, matching
the existing partial unique index (`WHERE idempotency_key IS NOT NULL`); Requirements SHALL NOT widen the
scope to include `case_id` or `asset_id`, nor narrow it below the enforced constraint, without a separate,
explicitly reviewed migration decision.
Verification: STATIC SCHEMA INSPECTION | Acceptance: Scope matches | Failure: Requirements logic assumes a
different scope than the DB enforces
Notes: None

**REQ-B6-036** `IDEMPOTENCY` — Duplicate-submission behavior (same key, same intent)
Source: WHAT §17 | Authority: CPL | Object: RunnerExecution
Statement: A submission with `(runner_type, idempotency_key)` matching an existing row, where the request
represents the same governed operation intent, SHALL retrieve the existing `RunnerExecution` (replay per
REQ-B6-004) rather than error or attempt a duplicate insert.
Verification: INTEGRATION TEST | Acceptance: Existing row returned, no new row created | Failure: A duplicate-
key insert is attempted at the application layer (relying on the DB constraint to fail) instead of retrieving
Notes: "Same governed operation intent" is operationalized at REQ-B6-038

**REQ-B6-037** `IDEMPOTENCY` — Conflict behavior (same key, incompatible intent)
Source: WHAT §17 | Authority: CPL | Object: RunnerExecution
Statement: A submission with `(runner_type, idempotency_key)` matching an existing row, where the request's
governed operation intent materially differs from the existing row's (per REQ-B6-038's comparison), SHALL be
rejected with an explicit conflict outcome — SHALL NOT silently retrieve the mismatched existing row and SHALL
NOT silently overwrite it.
Verification: INTEGRATION TEST | Acceptance: Explicit conflict response | Failure: Silent retrieval or
overwrite
Notes: None

**REQ-B6-038** `IDEMPOTENCY` — Defining "materially different intent"
Source: WHAT §17 (Requirements must resolve operational scope, not conceptual identity) | Authority: CPL |
Object: RunnerExecution
Statement: For the purpose of REQ-B6-036/037, two submissions sharing `(runner_type, idempotency_key)` SHALL
be compared on: `case_id`, `asset_id`, `execution_purpose`. Identical values on all three = same intent
(REQ-B6-036 applies). Any difference = conflict (REQ-B6-037 applies). Request payload content beyond these
fields is explicitly NOT part of this comparison (payload is opaque per REQ-B6-018/033-adjacent discipline).
Verification: INTEGRATION TEST, both branches | Acceptance: Comparison implemented exactly as specified |
Failure: Comparison uses a different field set without a documented reason
Notes: This is a genuine Requirements-level operational decision — the WHAT does not specify it, and this
matrix picks the minimum defensible comparison set rather than leaving it to HOW

**REQ-B6-039** `IDEMPOTENCY` — NULL key means no deduplication
Source: schema (partial index `WHERE idempotency_key IS NOT NULL`); WHAT §17 | Authority: CPL | Object:
RunnerExecution
Statement: Where `idempotency_key IS NULL`, no deduplication SHALL be attempted or implied; every such
submission SHALL create a new `RunnerExecution`.
Verification: INTEGRATION TEST | Acceptance: Confirmed | Failure: Any code path attempts dedup despite a NULL
key
Notes: None

**REQ-B6-040** `IDEMPOTENCY` — Retry relation to idempotency
Source: WHAT §17 | Authority: CPL | Object: RunnerExecution
Statement: A retry (new attempt after prior technical failure, REQ-B6-005 scenario D) that reuses the same
`idempotency_key` as the failed attempt SHALL be governed by REQ-B6-036/037 exactly as any other duplicate
submission — retry is not a special case that bypasses the idempotency contract.
Verification: INTEGRATION TEST (retry with same key against a FAILED prior row) | Acceptance: Governed
identically to REQ-B6-036/037 | Failure: A retry-specific bypass exists
Notes: A retry with a NEW idempotency_key is simply REQ-B6-039 (new row), no special case needed

**REQ-B6-041** `NEGATIVE / PROHIBITION` — idempotency_key never identity
Source: WHAT §17; EA-CI16, EA-CI18; EA-WRC-02 | Authority: CPL | Object: RunnerExecution
Statement: No Requirements-level or downstream logic SHALL treat `idempotency_key` as equivalent to
`RunnerExecution` identity, request identity, or domain-operation identity — restated here as a standalone,
independently testable requirement precisely because `EA-WRC-02` found this boundary under-registered
(present only in WHAT body prose, not mirrored as its own invariant bullet).
Verification: TRACEABILITY REVIEW | Acceptance: No such treatment found | Failure: Found
Notes: Closes `EA-WRC-02` operationally without amending the WHAT's invariant registry

**REQ-B6-042** `TRACEABILITY` — BS-EA-03 Requirements-level closure statement
Source: WHAT §17, §26 (BS-EA-03: SEMANTIC CORE PARTIALLY RESOLVED IN WHAT + OPERATIONAL CONTRACT OPEN FOR
REQUIREMENTS) | Authority: CPL | Object: RunnerExecution
Statement: REQ-B6-035 through REQ-B6-041 constitute this Requirements phase's complete closure of `BS-EA-03`'s
operational-contract portion. The semantic core (`idempotency_key ≠ RunnerExecution identity`) remains WHAT-
level and is not reopened by any of the above.
Verification: TRACEABILITY REVIEW | Acceptance: Confirmed at Freeze | Failure: N/A (bookkeeping requirement)
Notes: See §27 traceability table

---

## 14. parent_execution_id negative requirements

**REQ-B6-043** `NEGATIVE / PROHIBITION` — No canonical semantics assigned
Source: WHAT §18 (BS-EA-02); EA-CI17 | Authority: CPL | Object: RunnerExecution
Statement: `parent_execution_id` SHALL NOT be interpreted, documented, or relied upon by this Build Unit's
Requirements as proof of: retry, replay, continuation, delegation, dependency, correction, or derivation.
Verification: TRACEABILITY REVIEW across all requirements in this matrix (self-check: none of REQ-B6-001–087
depends on parent_execution_id meaning) | Acceptance: Confirmed | Failure: Any requirement is found to depend
on it
Notes: This is the umbrella requirement; REQ-B6-006 and REQ-B6-044 are its specific applications

**REQ-B6-044** `INTEGRITY` — Existing self-reference constraint preserved, not over-interpreted
Source: schema (`runner_executions_not_self_parent_chk`, migration 011); WHAT §18 | Authority: CPL | Object:
RunnerExecution
Statement: The existing constraint preventing `parent_execution_id = execution_id` SHALL be preserved as a
structural-integrity rule only (an execution cannot be its own parent); this SHALL NOT be read as evidence
that the field has acquired lineage semantics.
Verification: STATIC SCHEMA INSPECTION | Acceptance: Constraint preserved, no semantic claim added | Failure:
Documentation or code treats the constraint as semantic confirmation of a lineage model
Notes: None

**REQ-B6-045** `TRACEABILITY` — Divergence-recording obligation
Source: WHAT §18; this instruction §18 ("If implementation relies on such semantics, record IMPLEMENTATION /
GOVERNANCE DIVERGENCE. Do NOT repair that divergence in this artifact.") | Authority: CPL | Object:
RunnerExecution
Statement: If, during Requirements construction or later Challenge, any existing code is found to rely on
`parent_execution_id` for retry/continuation/lineage behavior, that finding SHALL be recorded as
`IMPLEMENTATION / GOVERNANCE DIVERGENCE` in the gap register (§31) and SHALL NOT be silently repaired within
this Requirements artifact.
Verification: TRACEABILITY REVIEW (no such usage found in migrations 001–026 or the two migration files
inspected directly) | Acceptance: None found in the schema layer inspected | Failure: Found and unrecorded
Notes: Application-layer code (outside `migrations/`) was not inspected in this session — see RM-B6-02

---

## 15. Provenance requirements

**REQ-B6-046** `PROVENANCE` — Minimum execution provenance
Source: WHAT §15 | Authority: CPL | Object: RunnerExecution
Statement: Minimum recorded provenance per `RunnerExecution`: `runner_type`, `runner_version`, `created_at`
(generation time), `initiated_by_contact_id` (where non-null). All four already exist in schema (migration
011) and SHALL be preserved as the provenance baseline.
Verification: STATIC SCHEMA INSPECTION | Acceptance: All four present and populated per their nullability |
Failure: One is absent from the governed provenance definition
Notes: ALIGNED per §31 — no new field required

**REQ-B6-047** `PROVENANCE` — Minimum artifact provenance
Source: WHAT §15 | Authority: CPL | Object: RunnerArtifact
Statement: Minimum recorded provenance per `RunnerArtifact`: producing `execution_id`, `created_at`,
`hash_algorithm`/`content_hash` pair (integrity, §17), `supersedes_artifact_id` (supersession lineage, where
applicable). All exist in schema (migration 012).
Verification: STATIC SCHEMA INSPECTION | Acceptance: Present | Failure: Absent
Notes: ALIGNED per §31

**REQ-B6-048** `NEGATIVE / PROHIBITION` — Provenance never validity
Source: WHAT §15; EA-CI11 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: No documentation, API, or code path SHALL present provenance data (§46/§47) as establishing content
validity or domain correctness. `PRODUCED BY` SHALL be distinguished from `DERIVED FROM`; `USED AS INPUT` SHALL
be distinguished from `SUPERSEDES`; `REFERENCES` SHALL be distinguished from `PRODUCED BY` — none of these
relation types SHALL be collapsed into one another.
Verification: DOMAIN-BOUNDARY REVIEW; TRACEABILITY REVIEW | Acceptance: All four relation types remain
distinguishable in any audit view produced | Failure: Two are collapsed
Notes: None

**REQ-B6-049** `TRACEABILITY` — EA-WG-03 resolution (ExternalReference reuse)
Source: WHAT §27 (EA-WG-03) | Authority: CPL | Object: RunnerArtifact, ExternalReference (B4)
Statement: Requirements SHALL determine, explicitly, whether B4's existing `ExternalReference` primitive is
reused for artifact source-reference provenance (the open dimension named in WHAT §15) or whether a new,
non-duplicating reference concept is required. This matrix does not resolve the choice — see RM-B6-03 — but
requires the choice be made and documented before Freeze.
Verification: TRACEABILITY REVIEW at Freeze | Acceptance: Explicit choice documented | Failure: Undocumented
at Freeze
Notes: Open item — see Gap Register §31

---

## 16. VIR → PGDR handoff provenance requirements

**REQ-B6-050** `DOMAIN-BOUNDARY` — B6 guarantees identity/provenance only, not transformation
Source: WHAT §14 (BS-EA-06, CLOSED FOR CPL'S WHAT) | Authority: CPL (representation), integration layer
(transformation, out of B6 scope) | Object: RunnerExecution, RunnerArtifact
Statement: This Build Unit SHALL guarantee: stable identity and provenance for VIR `RunnerExecution`/
`RunnerArtifact` rows; stable identity and provenance for PGDR `RunnerExecution`/`RunnerArtifact` rows; and,
if REQ-B6-049 resolves to reuse `ExternalReference`, an optional referencing link between them. It SHALL NOT
guarantee, construct, or specify the selection/transformation logic that produces PGDR's
`DiagnosticIdentityContext` input from VIR material — that responsibility is explicitly DOMAIN INTEGRATION,
outside B6.
Verification: TRACEABILITY REVIEW | Acceptance: No requirement in this matrix specifies transformation logic |
Failure: One does
Notes: None

**REQ-B6-051** `NEGATIVE / PROHIBITION` — No direct artifact-to-artifact coupling
Source: WHAT §14 | Authority: CPL | Object: RunnerArtifact
Statement: No requirement in this matrix SHALL imply or require a direct schema-level coupling between a VIR
artifact and a PGDR artifact; the WHAT's own evidence (`PGDR-ID-001`) establishes that PGDR consumes a
projection, not a raw VIR artifact.
Verification: TRACEABILITY REVIEW | Acceptance: No such coupling required by any requirement | Failure: One
requires it
Notes: None

**REQ-B6-052** `TRACEABILITY` — BS-EA-05 disposition carried forward
Source: WHAT §15, §26 (BS-EA-05: OPEN) | Authority: CPL | Object: RunnerArtifact
Statement: `BS-EA-05` (no handoff-provenance field for VIR→PGDR) is closed at the Requirements level only to
the extent REQ-B6-049/050 establish (identity/provenance guarantee, mechanism choice pending); it is NOT
fully closed by this matrix and SHALL be re-carried into the Challenge with this exact status, not silently
marked resolved.
Verification: TRACEABILITY REVIEW | Acceptance: Status accurately carried at Challenge | Failure: Silently
marked resolved
Notes: None

---

## 17. Integrity requirements (content hash)

**REQ-B6-053** `INTEGRITY` — When hash is required
Source: schema (`hash_algorithm`/`content_hash` nullable pair, migration 012); WHAT §15 | Authority: CPL |
Object: RunnerArtifact
Statement: Content hash SHALL be required (both fields populated) for any artifact whose `payload` is stored
inline by CPL; it MAY be absent (both fields NULL) only for an artifact that is a reference to externally
stored content not embedded in `payload` (§37) — the existing pair-nullable design already permits this,
Requirements formalize the condition.
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST | Acceptance: Inline-payload artifacts always hash-
paired; reference-only artifacts may omit both | Failure: An inline-payload artifact ships without a hash
Notes: None

**REQ-B6-054** `INTEGRITY` — What material is hashed
Source: WHAT §15 (Requirements-level) | Authority: CPL | Object: RunnerArtifact
Statement: Where present, `content_hash` SHALL be computed over the exact `payload` JSONB content as
persisted, using the algorithm named in `hash_algorithm`; it SHALL NOT be computed over a subset,
transformation, or external representation of the payload.
Verification: INTEGRATION TEST (hash recomputation over stored payload matches stored content_hash)
Acceptance: Match | Failure: Mismatch
Notes: None

**REQ-B6-055** `INTEGRITY` — Mismatch behavior
Source: WHAT §15 (Requirements-level) | Authority: CPL | Object: RunnerArtifact
Statement: If a stored `content_hash` is found not to match a recomputation over the stored `payload` (e.g.,
during an integrity audit), the artifact SHALL be flagged via an explicit integrity-failure indicator; it
SHALL NOT be silently corrected, silently ignored, or silently treated as REJECTED (structural rejection has
a different meaning, per REQ-B6-033).
Verification: FAILURE-INJECTION TEST (corrupt stored payload, run integrity audit) | Acceptance: Flagged
distinctly | Failure: Silently handled or conflated with REJECTED
Notes: None

**REQ-B6-056** `NEGATIVE / PROHIBITION` — Hash never establishes semantic validity or domain truth
Source: WHAT §15; EA-CI06, EA-CI11 | Authority: CPL | Object: RunnerArtifact
Statement: A matching `content_hash` SHALL NOT be documented or used as evidence that the artifact's content is
semantically valid or domain-true — it establishes only that the stored bytes are unaltered since hashing.
Verification: DOMAIN-BOUNDARY REVIEW | Acceptance: No such claim exists | Failure: One does
Notes: None

---

## 18. Artifact correction / supersession requirements

**REQ-B6-057** `IMPLEMENTATION / WHAT DIVERGENCE — FLAGGED` — SUPERSEDED status vs. supersedes_artifact_id link
Source: schema (`runner_artifacts_status_chk` includes `SUPERSEDED`; `supersedes_artifact_id` self-FK, both
migration 012); WHAT §16 | Authority: CPL | Object: RunnerArtifact
Statement: The live schema encodes supersession two ways at once: a status value (`artifact_status =
'SUPERSEDED'`, set on the OLD artifact) and a link (`supersedes_artifact_id`, set on the NEW artifact,
pointing backward). Requirements SHALL treat these as one coordinated write, not two independent facts that
could drift out of sync: whenever a new artifact's `supersedes_artifact_id` is set, the referenced artifact's
`artifact_status` SHALL transition to `SUPERSEDED` in the same governed operation (see REQ-B6-080,
atomicity). Neither field SHALL be settable independently of the other by ordinary application code.
Verification: STATIC SCHEMA INSPECTION; INTEGRATION TEST (setting one without the other is rejected or
impossible via the governed write path) | Acceptance: Coordinated write enforced | Failure: The two can drift
(e.g., a SUPERSEDED-status artifact with no referencing supersedes_artifact_id, or vice versa)
Notes: This divergence was not visible from the WHAT text or the resume's field summary — it required reading
the actual CHECK constraint. Classified `IMPLEMENTATION / WHAT DIVERGENCE` because the WHAT names only the
link as substrate (§16) and does not mention the status value at all; this requirement resolves it at
Requirements level by making the two mechanisms coordinated rather than competing, without inventing new WHAT
semantics (supersession's *meaning* is unchanged, only its *mechanical coordination* is specified)

**REQ-B6-058** `CORRECTION` — Supersession is additive, not deletion
Source: WHAT §16 | Authority: CPL | Object: RunnerArtifact
Statement: A superseded `RunnerArtifact` row SHALL be retained in full, never deleted, regardless of
`artifact_status` value.
Verification: STATIC SCHEMA INSPECTION (no DELETE path exists for artifact rows in this Build Unit); FK
`ondelete=RESTRICT` on `supersedes_artifact_id` already prevents deleting a referenced row | Acceptance:
Preserved | Failure: A delete path is introduced
Notes: ALIGNED per §31 — existing FK behavior already enforces this

**REQ-B6-059** `CORRECTION` — Metadata vs. content vs. classification correction, distinguished
Source: WHAT §16 | Authority: CPL | Object: RunnerArtifact
Statement: Requirements SHALL distinguish, in the audit trail, three CPL-governable correction categories on
`RunnerArtifact`: (a) metadata correction (e.g., a classification-dimension value, §11); (b) content
correction (opaque payload correction via full supersession, REQ-B6-057); (c) not applicable here — semantic-
classification correction is a metadata correction (category a), not a separate category. Domain-assertion
and domain-determination correction (WHAT §16 categories D/E) SHALL NOT be represented as either.
Verification: DOMAIN-BOUNDARY REVIEW; TRACEABILITY REVIEW | Acceptance: Categories distinguishable in audit
output | Failure: Conflated
Notes: None

**REQ-B6-060** `NEGATIVE / PROHIBITION` — Domain-result correction stays outside B6
Source: WHAT §16 category D/E; EA-CI13 | Authority: VIR/PGDR (domain), NOT CPL | Object: RunnerArtifact
Statement: This Build Unit SHALL NOT provide a correction mechanism for domain assertions or domain
determinations carried in artifact payloads; such corrections, if they occur, happen entirely within VIR's or
PGDR's own domain and SHALL surface in CPL only as an ordinary new artifact via the standard registration path
(REQ-B6-081), never as a "correction" record.
Verification: DOMAIN-BOUNDARY REVIEW | Acceptance: No domain-correction mechanism exists | Failure: One does
Notes: None

**REQ-B6-061** `TRACEABILITY` — Governed decision required for correction/supersession
Source: WHAT §25 (artifact supersession/correction — LIKELY requires governed decision, mirroring B5's
`EVENT_CORRECTION` pattern) | Authority: CPL | Object: RunnerArtifact
Statement: Every supersession event (REQ-B6-057) SHALL require a governed decision record before the
canonical effect (status/link update) is applied; the exact decision-object shape (unified vs. separate table,
mirroring B5's discretion) is deferred to HOW.
Verification: INTEGRATION TEST (supersession without a preceding decision record is rejected) | Acceptance:
Rejected as expected | Failure: Supersession succeeds without one
Notes: EA-WG-02-adjacent — object shape is HOW, requirement (that a decision must exist) is Requirements

---

## 19. Execution correction / history requirements

**REQ-B6-062** `NEGATIVE / PROHIBITION` — No rewriting of historical occurrence
Source: WHAT §16 (R-EA-W05); EA-CI12 | Authority: CPL | Object: RunnerExecution
Statement: No mechanism introduced by this Build Unit SHALL allow a historical `RunnerExecution` row to be
rewritten as if a different execution occurred. This holds even though, unlike `RunnerArtifact`,
`RunnerExecution` has no dedicated schema-level correction/supersession field.
Verification: STATIC SCHEMA INSPECTION (no such field exists, none SHALL be added for this purpose without a
new WHAT-level repair); TRACEABILITY REVIEW | Acceptance: No such mechanism exists | Failure: One is added
Notes: None

**REQ-B6-063** `CORRECTION` — Permitted execution correction classes
Source: WHAT §16 | Authority: CPL | Object: RunnerExecution
Statement: Requirements permit exactly three classes of `RunnerExecution` correction: (A) correction of non-
occurrence metadata where governance permits (e.g., a mis-recorded `execution_purpose` free-text field); (B)
append/history-preserving correction of misrepresented execution metadata (implemented as an append-only
correction log — see REQ-B6-064); (C) a genuinely new attempt, which is always a NEW `RunnerExecution` (§6),
never a correction of a prior one.
Verification: TRACEABILITY REVIEW | Acceptance: Only these three classes exist in the governed mechanism |
Failure: A fourth is introduced
Notes: None

**REQ-B6-064** `CORRECTION` — Append-only correction log required
Source: WHAT §16 (R-EA-W05, "the exact mechanism for (B) is explicitly a Requirements/HOW decision") |
Authority: CPL | Object: RunnerExecution
Statement: Category-B correction (REQ-B6-063) SHALL be implemented as an append-only log of correction events
referencing the corrected `RunnerExecution`, never as in-place mutation of the original row's historical
field values. The original values SHALL remain reconstructable from the log.
Verification: STATIC SCHEMA INSPECTION (mechanism is append-only); HISTORY-RECONSTRUCTION TEST (original value
recoverable after a correction) | Acceptance: Recoverable | Failure: Not recoverable, or original value is
overwritten in place
Notes: This is the Requirements-level resolution of R-EA-W05's residual "mechanism remains Requirements/HOW"
note — chosen here as append-only-log, consistent with the pattern already used for artifact supersession

**REQ-B6-065** `HISTORY` — Reconstructability, scoped
Source: WHAT §16 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: History SHALL be reconstructable sufficiently to answer: `RunnerExecution` identity and lifecycle
transitions (§7–9); produced `RunnerArtifact`s (§10); artifact supersession/correction (§18); and any governed
provenance relation established under §15/§16. It SHALL NOT require reconstructing a generic "attempt lineage"
via `parent_execution_id` (§14).
Verification: HISTORY-RECONSTRUCTION TEST, one per listed category | Acceptance: All reconstructable except
the explicitly excluded lineage inference | Failure: A listed category is not reconstructable, or lineage
inference is attempted
Notes: None

---

## 20. Failure-model requirements

**REQ-B6-066** `FAILURE` — Distinct observable failure categories
Source: WHAT §23 | Authority: CPL | Object: RunnerExecution
Statement: The system SHALL make the following distinguishable, per REQ-B6-008's vocabulary mapping: execution
not authorized (pre-materialization rejection, REQ-B6-009 "no row" case); execution `BLOCKED`
(REQ-B6-012); technical execution failure (`FAILED`); execution completion (`COMPLETED`); artifact structural
invalidity (`REJECTED`, REQ-B6-033); integrity failure (REQ-B6-055); and any domain-level rejection, which is
explicitly out-of-B6 and SHALL NOT be represented in any of the above vocabularies (REQ-B6-060 analogue for
execution).
Verification: NEGATIVE TEST, one per category — confirm each is independently distinguishable and that domain
rejection cannot be represented | Acceptance: All distinguishable, domain rejection unrepresentable | Failure:
Two collapse into one, or domain rejection leaks into a category
Notes: None

**REQ-B6-067** `NEGATIVE / PROHIBITION` — Domain rejection never collapsed into execution failure
Source: WHAT §23; EA-CI02, EA-CI03 | Authority: CPL, NOT domain | Object: RunnerExecution
Statement: A runner's domain-level negative determination (e.g., "vehicle identity could not be established"
or "no fault found") SHALL NOT set `execution_status = FAILED`; such an execution, having technically
completed, SHALL be represented as `COMPLETED`, with the domain-negative content carried only in the produced
`RunnerArtifact`'s opaque payload.
Verification: DOMAIN-BOUNDARY REVIEW; INTEGRATION TEST | Acceptance: Confirmed | Failure: `FAILED` is set from
domain-negative content
Notes: Direct application of `EXECUTION FAILED ≠ DOMAIN ASSERTION FALSE`

**REQ-B6-068** `FAILURE` — No artifact does not imply domain-negative result
Source: WHAT §23; EA-CI01, EA-CI02 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: An execution reaching `COMPLETED` with zero produced artifacts SHALL NOT, by that fact alone, be
interpreted or documented as a domain-negative result; absence of artifacts is a representation fact, not a
domain conclusion.
Verification: DOMAIN-BOUNDARY REVIEW | Acceptance: No such interpretation documented | Failure: One is
Notes: None

---

## 21. Domain-authority boundary requirements

**REQ-B6-069** `DOMAIN-BOUNDARY` — No inference of domain validity from representation facts
Source: WHAT §9, §12, §13; EA-CI04, EA-CI13, EA-CI15 | Authority: VIR/PGDR (domain), NOT CPL | Object:
RunnerExecution, RunnerArtifact
Statement: B6 SHALL NOT infer domain validity from any of: execution completion, artifact existence, artifact
classification, content hash match, `artifact_status` value, or provenance data. All are representation facts
only.
Verification: DOMAIN-BOUNDARY REVIEW across every requirement in this matrix that touches these six signals
Acceptance: No inference found | Failure: One found
Notes: Consolidates REQ-B6-007, 012, 031, 048, 056, 067, 068 into one explicit cross-cutting statement

**REQ-B6-070** `DOMAIN-BOUNDARY` — VIR identity authority preserved
Source: WHAT §12 | Authority: VIR | Object: RunnerArtifact (VIR-originated)
Statement: No API, report, or view produced under this Build Unit SHALL present a stored VIR artifact's
content as a CPL-endorsed vehicle-identity conclusion.
Verification: DOMAIN-BOUNDARY REVIEW of all VIR-facing output surfaces | Acceptance: None found | Failure:
Found
Notes: None

**REQ-B6-071** `DOMAIN-BOUNDARY` — PGDR diagnostic authority preserved
Source: WHAT §13 | Authority: PGDR | Object: RunnerArtifact (PGDR-originated)
Statement: No API, report, or view produced under this Build Unit SHALL present a stored PGDR artifact's
content as a CPL-endorsed diagnosis.
Verification: DOMAIN-BOUNDARY REVIEW of all PGDR-facing output surfaces | Acceptance: None found | Failure:
Found
Notes: None

---

## 22. Case / Asset / Identity compatibility requirements

**REQ-B6-072** `COMPATIBILITY` — Case boundary consumed, not altered
Source: WHAT §20 | Authority: B5 (Case), CPL (execution, referenced) | Object: RunnerExecution
Statement: `Case.current_execution_id` and `CaseEvent.execution_id` SHALL be consumed exactly as B5's own
`REPAIR-01` scoped them — opaque, execution-governance-owned references. No requirement in this matrix SHALL
alter B5 `Case` semantics.
Verification: REGRESSION TEST (existing B5 test suite unaffected) | Acceptance: Unaffected | Failure: A B5 test
fails or B5 semantics require change
Notes: If B6 implementation is later found to require a B5 semantic change, that requirement chain SHALL be
marked `GOVERNANCE_CONFLICT` and stopped, not resolved here — none identified in this matrix

**REQ-B6-073** `COMPATIBILITY` — Asset boundary preserved
Source: WHAT §21 | Authority: B4 (Asset), CPL (execution, referenced) | Object: RunnerExecution
Statement: `RunnerExecution.asset_id` SHALL remain a reference only, structurally identical to `Case.asset_id`.
This Build Unit SHALL NOT merge Assets, determine physical Asset sameness, select a canonical Asset survivor,
redefine Asset identifiers, or override VIR's physical-identity determination authority.
Verification: REGRESSION TEST (existing B4 test suite unaffected); DOMAIN-BOUNDARY REVIEW | Acceptance:
Unaffected, no boundary violation | Failure: Either fails
Notes: None

**REQ-B6-074** `COMPATIBILITY` — Contact/initiator boundary preserved
Source: WHAT §22 | Authority: B3 (Contact) | Object: RunnerExecution
Statement: `initiated_by_contact_id` SHALL continue to use B3 `Contact` exclusively; this Build Unit SHALL NOT
introduce a generalized Actor/Role concept.
Verification: REGRESSION TEST (existing B3 test suite unaffected); STATIC SCHEMA INSPECTION (no new
actor/role table introduced) | Acceptance: Both confirmed | Failure: Either fails
Notes: None

**REQ-B6-075** `COMPATIBILITY` — Runner type/version is provenance, not platform expansion
Source: WHAT §9 (implicit — runner type/version as provenance dimension, §15) | Authority: CPL | Object:
RunnerExecution
Statement: `runner_type`/`runner_version` representation SHALL remain limited to provenance recording (§15);
this Build Unit SHALL NOT introduce a runner registry, package registry, capability marketplace, scheduler, or
orchestrator.
Verification: STATIC SCHEMA INSPECTION; TRACEABILITY REVIEW | Acceptance: None of the prohibited objects
introduced | Failure: One is
Notes: Cross-referenced at §25 (negative-scope)

---

## 23. Canonical decision / governed-effect requirements

**REQ-B6-076** `AUTHORITY` — Execution admission requires a governed decision
Source: WHAT §25 ("execution admission — LIKELY requires governed authority evaluation") | Authority: CPL |
Object: RunnerExecution
Statement: Materialization of a `RunnerExecution` row (i.e., the request-to-execution boundary, §7) SHALL
require a preceding governed authority decision; a rejected decision SHALL leave no `RunnerExecution` row
(REQ-B6-009's "no row" branch).
Verification: INTEGRATION TEST | Acceptance: No row created without a preceding decision | Failure: One is
Notes: None

**REQ-B6-077** `AUTHORITY` — Lifecycle transition requires a governed decision
Source: WHAT §25 ("execution lifecycle transition — LIKELY requires governed decision, mirroring B5's
STATUS_TRANSITION pattern") | Authority: CPL | Object: RunnerExecution
Statement: Every `execution_status` transition in the table at REQ-B6-009 SHALL require a governed decision
record, mirroring B5's `STATUS_TRANSITION` pattern.
Verification: INTEGRATION TEST | Acceptance: Transition without a decision record is rejected | Failure: One
succeeds without
Notes: Duplicates/confirms REQ-B6-016's authority-boundary requirement for this specific mutation type, as
required by §17 of this instruction ("for every mutation... specify the required authority boundary")

**REQ-B6-078** `AUTHORITY` — Artifact registration requires a governed decision
Source: WHAT §25 ("artifact registration — LIKELY requires governed decision, possibly lighter-weight") |
Authority: CPL | Object: RunnerArtifact
Statement: Canonical registration of a `RunnerArtifact` (the produced-vs-registered boundary, §36) SHALL
require a governed decision, which MAY be lighter-weight than execution admission (e.g., automatic approval
conditioned on structural validation passing) but SHALL NOT be absent.
Verification: INTEGRATION TEST | Acceptance: No artifact registered without a decision, however lightweight |
Failure: One is
Notes: None

**REQ-B6-079** `AUTHORITY` — Artifact correction/supersession requires a governed decision
Source: WHAT §25 (duplicated at REQ-B6-061) | Authority: CPL | Object: RunnerArtifact
Statement: See REQ-B6-061 — restated here to satisfy this section's mandate to enumerate the authority
boundary for all four mutation types named in WHAT §25.
Verification: See REQ-B6-061 | Acceptance: See REQ-B6-061 | Failure: See REQ-B6-061
Notes: Cross-reference, not a duplicate obligation

---

## 24. Atomicity / consistency requirements

**REQ-B6-080** `INTEGRITY` — Observable consistency, execution↔artifact and status↔supersession
Source: WHAT §7, §24; this instruction §34 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: The following SHALL be externally observable as atomic (no intermediate inconsistent state visible
to any reader, regardless of underlying transaction technology): (a) `RunnerExecution` creation together with
its governing decision (REQ-B6-076); (b) an `execution_status` transition together with its governing decision
(REQ-B6-077); (c) `RunnerArtifact` registration together with its governing decision (REQ-B6-078); (d) a
supersession's `supersedes_artifact_id` write together with the referenced artifact's `SUPERSEDED` status
transition (REQ-B6-057).
Verification: FAILURE-INJECTION TEST (simulate a crash between the two halves of each pair; confirm no reader
observes only one half) | Acceptance: No partial state observable in any injected-failure case | Failure: One
observed
Notes: Does not prescribe transaction technology — requirement is externally observable consistency only

**REQ-B6-081** `INTEGRITY` — Retry/replay cannot duplicate canonical effects
Source: WHAT §17; this instruction §33/§35 | Authority: CPL | Object: RunnerExecution, RunnerArtifact
Statement: A retried or replayed governed operation (per REQ-B6-004, REQ-B6-036, REQ-B6-040) SHALL NOT produce
a second canonical effect (a second `RunnerExecution` row, a second `RunnerArtifact` row, or a second decision
record) for what the governing rule treats as the same operation.
Verification: INTEGRATION TEST (replay/retry, confirm single canonical effect) | Acceptance: Single effect |
Failure: Duplicate effect
Notes: None

**REQ-B6-082** `INTEGRITY` — Produced vs. canonically registered, distinguished
Source: WHAT §36 (this instruction) | Authority: CPL | Object: RunnerArtifact
Statement: An artifact produced or emitted by a runner but not yet canonically registered (REQ-B6-078) SHALL
be distinguishable, in any observable system state, from a canonically registered `RunnerArtifact`; the two
SHALL NOT share representation such that an unregistered artifact could be mistaken for a governed one.
Verification: INTEGRATION TEST | Acceptance: Distinguishable | Failure: Not distinguishable
Notes: None

---

## 25. Negative-scope requirements

**REQ-B6-083** `NEGATIVE / PROHIBITION` — Consolidated exclusion list
Source: WHAT §5 | Authority: CPL | Object: whole Build Unit
Statement: This Build Unit SHALL NOT become, and no requirement in this matrix SHALL move it toward becoming:
a universal workflow engine; a universal job scheduler; an agent orchestration platform; a generic task
system; a generic event bus; a generic evidence ontology; a generic artifact repository; a universal state
engine; a generalized Actor/Role system; a knowledge graph; a domain ontology; a domain-truth engine; a
frontend; a billing system; a runner registry / package manager; a capability marketplace; or an internals
model of VIR or PGDR.
Verification: TRACEABILITY REVIEW of the full matrix against this list | Acceptance: No requirement introduces
any listed object | Failure: One does
Notes: Cross-referenced throughout (REQ-B6-025 join-table prohibition, REQ-B6-075 registry prohibition,
REQ-B6-074 Actor/Role prohibition, REQ-B6-050/051/078 domain-truth/internals prohibitions)

**REQ-B6-084** `NEGATIVE / PROHIBITION` — No generic execution lineage graph
Source: WHAT §18, §24 | Authority: CPL | Object: RunnerExecution
Statement: No concept named "execution lineage" or "execution continuation relation" SHALL be introduced into
the candidate ontology by this Requirements phase; `parent_execution_id` remains opaque per §14 of this matrix.
Verification: TRACEABILITY REVIEW | Acceptance: No such concept introduced | Failure: One is
Notes: Restates REQ-B6-043 at the ontology level rather than the field-usage level

---

## 26. Regression requirements

**REQ-B6-085** `REGRESSION` — B3/B4/B5 test suites remain valid
Source: this instruction §43 | Authority: N/A (process requirement) | Object: whole repository
Statement: Existing B3 identity tests, B4 asset/relationship tests, and B5 Case Governance tests SHALL remain
valid and passing after this Build Unit's eventual implementation; none SHALL require modification to
accommodate B6.
Verification: REGRESSION TEST (full existing suite run) | Acceptance: All pass unmodified | Failure: Any
requires modification or fails
Notes: None

**REQ-B6-086** `REGRESSION` — Migration history immutable
Source: this instruction §43, §44 | Authority: N/A (process requirement) | Object: migrations/versions/
Statement: Migrations 001–026 SHALL NOT be rewritten, reordered, or altered by this Build Unit's eventual
implementation; B6 additions SHALL take the form of new forward migrations only (027+), during implementation,
not during this Requirements phase.
Verification: STATIC SCHEMA INSPECTION (diff of migrations/ directory pre/post) | Acceptance: 001–026 byte-
identical | Failure: Any is altered
Notes: This Requirements artifact itself makes zero code or migration changes, per its own STOP condition

**REQ-B6-087** `REGRESSION` — Software baseline and migration head preserved by this artifact
Source: this instruction §44 | Authority: N/A (process requirement) | Object: whole repository
Statement: Drafting and freezing this Requirements matrix SHALL NOT alter `2ac075daea7d162825ed73ded0c7548011242a8f`
(software baseline) or migration head `026`. Verified true as of this artifact: baseline confirmed unchanged
via `git ls-remote` immediately before and will be re-confirmed via independent fresh clone after this
artifact's commit is pushed.
Verification: TRACEABILITY REVIEW (baseline check protocol, this Build Unit's own materialization procedure)
Acceptance: Unchanged pre/post | Failure: Changed
Notes: None

---

## 27. BS-EA-01 → 06 traceability

| Gap ID | Frozen WHAT disposition | Requirement(s) resolving it | Remaining disposition | Fully covered? |
|---|---|---|---|---|
| BS-EA-01 | RESOLVED (0:N multiplicity) | REQ-B6-023, 024, 025 | Mechanism-level closure only; semantics stay RESOLVED at WHAT level | YES |
| BS-EA-02 | REPAIRED — substrate acknowledged, semantics ungoverned | REQ-B6-006, 043, 044, 045 (all negative) | Explicitly NOT resolved positively; may resurface at WHAT level per REQ-B6-068 pattern | YES (as a negative-requirement set) |
| BS-EA-03 | SEMANTIC CORE PARTIALLY RESOLVED, operational contract open | REQ-B6-035–042 | CLOSED at Requirements level (operational contract only; semantic core stays WHAT-level) | YES |
| BS-EA-04 | PARTIALLY ADDRESSED (domain-acceptance reading prohibited) | REQ-B6-031–034 | CLOSED at Requirements level for the four existing enum values | YES |
| BS-EA-05 | OPEN | REQ-B6-049, 050, 052 | Still OPEN — mechanism choice (ExternalReference reuse) pending, carried to RM-B6-03 | PARTIALLY (explicitly not fully closed, per REQ-B6-052) |
| BS-EA-06 | CLOSED FOR CPL'S WHAT | REQ-B6-050, 051 | Recorded closed, not reopened | YES |

## 28. EA-WG traceability

| Gap ID | WHAT classification | Disposition in this matrix |
|---|---|---|
| EA-WG-01 | OPEN — HOW, non-blocking | Deferred to HOW explicitly via REQ-B6-030 (RM-B6-01); Requirements confirms the *need* for a per-dimension mechanism choice (REQ-B6-026) but does not make the choice |
| EA-WG-02 | OPEN — HOW, non-blocking | Deferred to HOW; Requirements confirms a governed decision is required for each mutation type (REQ-B6-076–079, REQ-B6-061) without prescribing unified vs. separate object shape |
| EA-WG-03 | OPEN — REQUIREMENTS, non-blocking | Confirmed as requiring resolution before Freeze via REQ-B6-049; specific choice deferred to RM-B6-03, not silently resolved |

## 29. EA-WRC-01/02 traceability

| Finding | RECHALLENGE disposition | Action taken here |
|---|---|---|
| EA-WRC-01 | MINOR, non-blocking; §6a's negation list omits Asset/artifact though the mandate named them; "optional future documentation polish" | Closed operationally (not textually, since this matrix cannot amend the frozen WHAT) via REQ-B6-002, which explicitly extends the identity-independence discipline to Asset and artifact |
| EA-WRC-02 | MINOR, non-blocking; `idempotency_key ≠ RunnerExecution identity` stated in body prose but not mirrored as a standalone EA-CI bullet | Closed operationally via REQ-B6-041, a standalone, independently testable requirement restating exactly this boundary |

Both findings were "optional future documentation polish" per the Re-Challenge — neither required Requirements
action to remain non-blocking. This matrix chose to close both operationally anyway, since doing so cost two
requirements and removes any risk of the gap being exploited during implementation.

---

## 30. Full requirement matrix (index)

```text
§6  RunnerExecution identity            REQ-B6-001–006   (6)
§7  Execution lifecycle                  REQ-B6-007–013   (7)
§8  Execution authority                   REQ-B6-014–017   (4)
§9  RunnerArtifact identity                REQ-B6-018–022   (5)
§10 Execution↔Artifact multiplicity          REQ-B6-023–025   (3)
§11 Artifact classification                    REQ-B6-026–030   (5)
§12 artifact_status                              REQ-B6-031–034   (4)
§13 Idempotency/replay/retry                       REQ-B6-035–042   (8)
§14 parent_execution_id negative                     REQ-B6-043–045   (3)
§15 Provenance                                          REQ-B6-046–049   (4)
§16 VIR→PGDR handoff provenance                           REQ-B6-050–052   (3)
§17 Integrity (content hash)                                REQ-B6-053–056   (4)
§18 Artifact correction/supersession                          REQ-B6-057–061   (5)
§19 Execution correction/history                                REQ-B6-062–065   (4)
§20 Failure model                                                  REQ-B6-066–068   (3)
§21 Domain-authority boundary                                        REQ-B6-069–071   (3)
§22 Case/Asset/Identity compatibility                                   REQ-B6-072–075   (4)
§23 Canonical decision/governed-effect                                     REQ-B6-076–079   (4)
§24 Atomicity/consistency                                                     REQ-B6-080–082   (3)
§25 Negative-scope                                                               REQ-B6-083–084   (2)
§26 Regression                                                                       REQ-B6-085–087   (3)
                                                                                    -----
TOTAL                                                                                87   REQ-B6-001–087
```

---

## 31. Requirement gap register

**RM-B6-01**
Description: Whether the existing `artifact_type` free-text column maps to classification dimension A, is
retired, or coexists with a distinct documented purpose is unresolved.
Source: REQ-B6-030
Severity: MODERATE
Blocking: NOT for Challenge; YES for Requirements Freeze
Why the WHAT does not already answer it: §11 explicitly defers exact classification mechanism to
Requirements/HOW and does not mention `artifact_type` by name at all.
What must be resolved before Requirements Freeze: an explicit mapping decision, documented with reasoning,
covering all existing and anticipated `artifact_type` values.

**RM-B6-02**
Description: Application-layer code (outside `migrations/versions/`) was not inspected in this session; it is
therefore unconfirmed whether any existing runner-orchestration or VIR/PGDR-integration code already relies on
`parent_execution_id` for retry/continuation/lineage behavior, which would constitute an `IMPLEMENTATION /
GOVERNANCE DIVERGENCE` per §18 of this instruction.
Source: REQ-B6-045
Severity: MODERATE (if such reliance exists, it must be recorded, not repaired, before Freeze)
Blocking: NOT for Challenge; YES for Requirements Freeze if found
Why the WHAT does not already answer it: the WHAT deliberately leaves the field's meaning ungoverned; whether
code has already assigned it meaning is an empirical, not a governance, question.
What must be resolved before Requirements Freeze: a code-level search of application/service code (not just
migrations) for `parent_execution_id` usage, with any finding recorded per the divergence protocol.

**RM-B6-03**
Description: Whether B4's `ExternalReference` primitive is reused for artifact source-reference provenance (VIR
→PGDR handoff, `BS-EA-05`) or a new reference concept is needed remains an open choice.
Source: REQ-B6-049, REQ-B6-050, REQ-B6-052
Severity: LOW (does not block Challenge; `BS-EA-05` was already OPEN at WHAT level and this matrix does not
regress that status)
Blocking: NOT for Challenge; YES for Requirements Freeze
Why the WHAT does not already answer it: `EA-WG-03` explicitly classifies this as OPEN — REQUIREMENTS, not
frozen by the WHAT.
What must be resolved before Requirements Freeze: inspect B4's `ExternalReference` schema/usage directly (not
yet done in this session) and decide reuse vs. new concept.

No item above is classified `WHAT_CONFLICT_DISCOVERED`. `REQ-B6-057` (the `SUPERSEDED`-status /
`supersedes_artifact_id` overlap) was resolved within this matrix rather than placed in the gap register,
because it was resolvable at the *operational coordination* level (REQ-B6-057's "one coordinated write") without
touching the WHAT's conceptual meaning of supersession — it therefore did not meet the bar for
`WHAT_CONFLICT_DISCOVERED` or for deferral to the gap register.

---

## 32. Coverage statistics

```text
TOTAL REQUIREMENTS:              87
TRACEABLE:                         87/87
ACTIVE EA-CI COVERAGE:               19/19  (EA-CI01–13, 15–19 cited directly; EA-CI14 covered via EA-CI03
                                              per its own retirement — no requirement cites EA-CI14 independently)
BS-EA-01..06:                          ALL ACCOUNTED FOR (5 fully covered, 1 — BS-EA-05 — explicitly partial,
                                                            not silently closed)
EA-WG-01..03:                             ALL ACCOUNTED FOR (all 3 explicitly deferred with reasoning, none
                                                                silently resolved)
EA-WRC-01/02:                                ACCOUNTED FOR (both closed operationally)
REQUIREMENT-LEVEL GAPS:                        3  (RM-B6-01, RM-B6-02, RM-B6-03)
WHAT CONFLICTS DISCOVERED:                        0
DOMAIN AUTHORITY BOUNDARY:                          PRESERVED
B3/B4/B5 REGRESSION BOUNDARY:                          PRESERVED
```

---

## 33. Challenge readiness

```text
REQUIREMENTS_STATUS: CHALLENGE_READY
```

Reasoning: all frozen WHAT sections relevant to B6 have requirement coverage (§6–§27 fully traced); all 19
active invariants are cited; `BS-EA-01..06` are accounted for with one honestly-partial closure (`BS-EA-05`)
rather than a false-complete claim; `EA-WG-01..03` are accounted for without silent HOW-level resolution;
`EA-WRC-01/02` are accounted for; no requirement invents new ontology (verified via REQ-B6-084's self-check and
the negative-requirement discipline applied throughout §14, §21, §25); the idempotency operational contract is
explicit (§13); `parent_execution_id` remains semantically unassigned (§14); artifact classification remains
multidimensional (§11); `RunnerExecution` identity remains independent from idempotency (REQ-B6-003, 041);
domain authority remains outside CPL (§21); correction preserves history (§18, §19); B3/B4/B5 remain untouched
(§22, §26). Three gap-register items remain open and are explicitly non-blocking for Challenge but blocking for
Freeze.

---

## 34. Recommended next governance action

```text
B6_EXECUTION_ARTIFACT_REQUIREMENT_CHALLENGE_v0
```

---

## FINAL SUMMARY

```text
B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0
===========================================

GOVERNANCE BASELINE:
  3092d7c69e59191fdfc945304fd71d5a8bf0b08d

FROZEN WHAT:
  docs/build/CPL_EA_WHAT_v0.1.md

FROZEN WHAT COMMIT:
  e7d51842043408cccd97bf3811de73c756784849

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

MIGRATION HEAD:
  026

BUILD UNIT:
  B6_EXECUTION_ARTIFACT_GOVERNANCE

TOTAL REQUIREMENTS:
  87

TRACEABILITY:
  87/87

ACTIVE EA-CI COVERAGE:
  19/19

BS-EA-01..06:
  ALL ACCOUNTED FOR

EA-WG:
  ALL ACCOUNTED FOR

EA-WRC-01/02:
  ACCOUNTED FOR

REQUIREMENT-LEVEL GAPS:
  3

WHAT CONFLICTS DISCOVERED:
  0

DOMAIN AUTHORITY BOUNDARY:
  PRESERVED

B3/B4/B5 REGRESSION BOUNDARY:
  PRESERVED

REQUIREMENTS STATUS:
  CHALLENGE_READY

REQUIREMENTS FREEZE:
  NOT GRANTED

EXECUTION MANDATE:
  NOT AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED

NEXT GOVERNANCE ACTION:
  B6_EXECUTION_ARTIFACT_REQUIREMENT_CHALLENGE_v0
```

## 56. STOP

**STOP.** This artifact does not challenge, repair, or freeze these requirements. No Execution Mandate. No
candidate branch. No schema modification. No migration. No code modification to CPL, VIR, or PGDR.

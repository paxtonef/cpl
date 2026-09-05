# CPL — B5 Case Governance Requirement Matrix v0.1

**System:** Common Product Layer — CPL
**Build Unit:** B5 — Case Governance
**Artifact:** Requirement Matrix
**Version:** v0.1
**Status:** BOUNDED REPAIR REVISION — NOT ACCEPTED — NOT FROZEN
**Governance HEAD at production:** `a621128f2f9b778812804e14c75590c5fe5b7196`
**Source matrix (v0):** SHA `8b2d231912de6fe7ac5b955eb2d14de277966eb0`
**Source challenge:** `docs/build/B5_CASE_GOVERNANCE_REQUIREMENT_CHALLENGE_v0.md` — SHA `a621128f2f9b778812804e14c75590c5fe5b7196`
**Challenge verdict:** `REPAIR_REQUIRED` (0 blocking, 8 non-blocking, 0 WHAT conflicts)
**Frozen WHAT:** UNCHANGED — `f53fce8f0c79aa3b5f041a964883ab8283671584`
**Implementation authorization:** NONE

---

## 0a. Repair scope

This revision is limited to the eight authorized findings:

```text
RM-B5-01  Authority mechanism de-prescription
RM-B5-02  Asset rebinding policy
RM-B5-03  Execution status/success-failure deduplication
RM-B5-04  Failure category testability
RM-B5-05  Pipeline atomicity
RM-B5-06  Idempotent replay outcome retrieval
RM-B5-07  Event occurrence time vs recording time
RM-B5-08  CaseEvent classification determinability
```

All other surviving `v0` requirements remain unchanged. Existing requirement identifiers `REQ-B5-001`–`108` are preserved except where a repair explicitly modifies a specific requirement's text (RM-B5-01, 03, 04, 05); new requirements are appended after `REQ-B5-108`.

---

## 1. Purpose

This matrix converts the frozen B5 Case Governance WHAT into atomic, testable, traceable requirements. It MUST NOT invent new semantics, expand the frozen scope (`Case`, `CaseParticipant`, `CaseEvent` only), absorb Execution Governance (`RunnerExecution`, `RunnerArtifact`), or silently resolve `GAP-01`→`GAP-04` beyond their frozen open-but-non-blocking status.

---

# 2. Requirement families

```text
A  Case object / identity
B  Asset anchoring
C  Case participation
D  CaseEvent boundary
E  CaseEvent classification (GAP-02)
F  Case lifecycle / status
G  Authority / decision
H  Execution pointer boundary
I  History / reconstructability
J  Correction / supersession (GAP-03)
K  Idempotency
L  Failure semantics
M  Case-to-Case consolidation boundary (GAP-01)
N  Ontology vocabulary (GAP-04)
O  Domain-truth boundary
P  Anti-workflow boundary
Q  Anti-event-sourcing boundary
R  actor_type boundary
S  Verification and evidence
```

---

# 3. A — Case object / identity

### REQ-B5-001
Category: Identity | Verification: UNIT, POSTGRESQL
The system MUST represent a Case as a persistent CPL identity (`case_id`) distinct from the physical/domain matter it concerns.

### REQ-B5-002
Category: Identity | Verification: UNIT
Case identity MUST NOT be derived from or dependent upon Asset identity.

### REQ-B5-003
Category: Identity | Verification: UNIT
Case identity MUST NOT be derived from or dependent upon Contact identity.

### REQ-B5-004
Category: Identity | Verification: UNIT
Case identity MUST remain stable across `case_status` transitions.

### REQ-B5-005
Category: Identity | Verification: UNIT
Case identity MUST remain stable across `CaseParticipant` addition, change, or removal.

### REQ-B5-006
Category: Identity | Verification: UNIT
Case identity MUST remain stable across `CaseEvent` accumulation.

### REQ-B5-007
Category: Boundary | Verification: STATIC, ADVERSARIAL
A Case's existence MUST NOT be interpreted or represented as proof that an underlying world event occurred (`WORLD MATTER ≠ CPL CASE`).

### REQ-B5-008
Category: Boundary | Verification: STATIC, ADVERSARIAL
A Case's existence MUST NOT be interpreted or represented as a CPL-asserted domain truth (`DOMAIN ASSERTION ≠ CPL CASE`).

### REQ-B5-009
Category: Boundary | Verification: STATIC
No operation MAY collapse the distinction `WORLD MATTER ≠ DOMAIN ASSERTION ≠ CPL CASE` into a single representation.

### REQ-B5-010
Category: Boundary | Verification: ADVERSARIAL
A Case MUST NOT be interpreted as a workflow instance requiring CPL-level task/step orchestration semantics.

### REQ-B5-011
Category: Identity | Verification: UNIT, POSTGRESQL
Case creation MUST require a valid, existing primary Contact identity (`primary_contact_id`).

### REQ-B5-012
Category: Identity | Verification: INTEGRATION
`CaseEvent` recording for a non-existent Case MUST NOT implicitly create that Case.

### REQ-B5-013
Category: Identity | Verification: UNIT
Case identity MUST remain distinct from any RunnerExecution identity referenced via `current_execution_id`.

---

# 4. B — Asset anchoring

### REQ-B5-014
Category: Boundary | Verification: POSTGRESQL, MIGRATION
Case creation MUST require a valid, existing Asset identity (`asset_id`). `Case.asset_id` MUST remain `NOT NULL`.

### REQ-B5-015
Category: Boundary | Verification: ADVERSARIAL
The implementation MUST NOT permit Asset-less Case creation.

### REQ-B5-016
Category: Boundary | Verification: ADVERSARIAL
The implementation MUST NOT permit Contact-only Case creation (a Case with no associated Asset).

### REQ-B5-017
Category: Boundary | Verification: STATIC, REGRESSION
Requirements and implementation MUST NOT silently relax `Case.asset_id NOT NULL`. Asset-optional Case remains OUT OF SCOPE for this Build Unit; any discovered need for it MUST be raised as `WHAT_REVISION_REQUIRED`, not implemented.

### REQ-B5-018
Category: Boundary | Verification: UNIT
Case creation MUST require the referenced Asset to be a canonically valid Asset identity (i.e., resolvable per B4 governance) at creation time.

---

# 5. C — Case participation

### REQ-B5-019
Category: Participation | Verification: UNIT, POSTGRESQL
The system MUST support attaching one or more `CaseParticipant` records to a Case.

### REQ-B5-020
Category: Participation | Verification: STATIC
`CaseParticipant` MUST remain semantically distinct from `ContactAssetRelationship`; a `CaseParticipant` record MUST NOT be treated as establishing or implying a durable structural relationship.

### REQ-B5-021
Category: Participation | Verification: UNIT
`CaseParticipant.participant_role` MUST be recorded as a governed-extensible classification, not a closed universal enum.

### REQ-B5-022
Category: Boundary | Verification: ADVERSARIAL
Being recorded as a `CaseParticipant` MUST NOT, by itself, authorize any Case mutation.

### REQ-B5-023
Category: Boundary | Verification: ADVERSARIAL
Participant role MUST NOT be conflated with authority: `ROLE ≠ AUTHORITY ≠ PERMISSION ≠ IDENTITY` MUST hold as an operational distinction, not merely a documentation note.

### REQ-B5-024
Category: Participation | Verification: UNIT
The system MUST distinguish participant existence (the fact of being recorded) from participant capacity (`participant_role`) from participant authority (a separate governed check).

### REQ-B5-025
Category: Participation | Verification: HISTORY
The system MUST support recording when a participation began (`joined_at`) and, where applicable, ended (`left_at`), without implying this constitutes a general valid-time claim about the external world.

### REQ-B5-026
Category: Participation | Verification: UNIT
A Contact MAY simultaneously hold a durable `ContactAssetRelationship` (B4) and a `CaseParticipant` record for the same Case without either implying or requiring the other.

---

# 6. D — CaseEvent boundary

### REQ-B5-027
Category: Event | Verification: UNIT, POSTGRESQL
The system MUST support recording a `CaseEvent` as an append-oriented representation of something reported, recorded, or produced within a Case's context.

### REQ-B5-028
Category: Boundary | Verification: ADVERSARIAL
A `CaseEvent`'s existence MUST NOT be interpreted as proof that the underlying world event objectively occurred (`WORLD EVENT ≠ CASE EVENT`).

### REQ-B5-029
Category: Boundary | Verification: ADVERSARIAL
A `CaseEvent`'s existence MUST NOT be interpreted as CPL-asserted validation of the domain assertion it records (`DOMAIN ASSERTION ≠ CASE EVENT`).

### REQ-B5-030
Category: Boundary | Verification: STATIC
`CaseEvent` MUST remain semantically distinct from a canonical Case decision: an event records history; it does not itself authorize a state transition.

### REQ-B5-031
Category: Boundary | Verification: ADVERSARIAL
A recorded `CaseEvent` MUST NOT be treated as having retroactively authorized the transition it describes.

### REQ-B5-032
Category: Boundary | Verification: STATIC
The system MUST preserve `REQUEST ≠ DECISION ≠ EVENT` as three distinguishable representations for any governed Case transition.

### REQ-B5-033
Category: Event | Verification: UNIT
`CaseEvent` MUST retain an `actor_type` and actor reference sufficient to identify who/what is recorded as acting (see family R).

### REQ-B5-034
Category: Event | Verification: HISTORY
`CaseEvent` records MUST be append-only; the implementation MUST NOT overwrite or delete a previously recorded `CaseEvent` in place.

---

# 7. E — CaseEvent classification (GAP-02)

### REQ-B5-035
Category: Classification | Verification: STATIC, TRACEABILITY
The system MUST prevent `event_type` + `payload` from functioning as an undifferentiated semantic truth container — i.e., the representation MUST make it possible to determine, for any given `CaseEvent`, at minimum whether it is a CPL operational fact or a recorded domain assertion.

### REQ-B5-036
Category: Classification | Verification: UNIT
The minimum operational requirement to satisfy REQ-B5-035 is that `CaseEvent.event_type` values be governed (defined and documented per Case Governance, not free-form arbitrary strings), even though no closed universal enum is mandated by the frozen WHAT.

### REQ-B5-037
Category: Classification | Verification: ADVERSARIAL
No `CaseEvent` MAY be represented as a canonical-decision consequence unless a corresponding governed decision exists (see family G); classification MUST NOT allow an event alone to masquerade as a decision outcome.

### REQ-B5-038
Category: Classification | Verification: TRACEABILITY
Acceptance evidence MUST demonstrate at least one CPL-operational-fact event (e.g. participant added) and one domain-assertion event (e.g. a reported diagnosis) that remain distinguishable under REQ-B5-035/036.

**Note:** GAP-02 remains OPEN. REQ-B5-035→038 establish the minimum testable boundary without mandating a specific classification schema (e.g. a dedicated `event_class` column); the exact representation remains a HOW decision for implementation, consistent with the frozen WHAT's refusal to pre-design it.

---

# 8. F — Case lifecycle / status

### REQ-B5-039
Category: Lifecycle | Verification: UNIT, POSTGRESQL
The system MUST preserve the existing `case_status` values (`OPEN, IN_PROGRESS, WAITING_FOR_USER, WAITING_FOR_EXTERNAL_INFORMATION, RESOLVED, CLOSED, REOPENED, CANCELLED`) as the current governed enum unless a separately authorized repair changes it.

### REQ-B5-040
Category: Boundary | Verification: ADVERSARIAL
`Case.case_status = CLOSED` MUST NOT be interpreted or represented as implying any domain-truth conclusion (e.g. "Asset repaired," "Asset safe," "diagnosis valid," "claim approved," "domain matter resolved").

### REQ-B5-041
Category: Boundary | Verification: STATIC
The system MUST NOT introduce domain-truth-laden status values (e.g. `REPAIRED`, `SAFE`, `DIAGNOSED`, `ELIGIBLE`, `APPROVED`) into `case_status`.

### REQ-B5-042
Category: Lifecycle | Verification: UNIT
The system MUST enforce the existing constraint that `case_status = CLOSED` requires `closed_at` to be set.

### REQ-B5-043
Category: Lifecycle | Verification: INTEGRATION
The system MUST support the lifecycle transitions implied by the existing enum (at minimum: open→in-progress, open/in-progress→waiting states, →resolved, →closed, closed→reopened, →cancelled), each as a governed operation (see family G).

### REQ-B5-044
Category: Boundary | Verification: ADVERSARIAL
The system MUST NOT require or introduce generic workflow semantics (ordered steps, task dependencies, a transition graph, deadlines, automation triggers) to support Case lifecycle transitions.

### REQ-B5-045
Category: Lifecycle | Verification: UNIT
`Case.title` and `case_type` MUST remain governed-extensible (not closed enums), consistent with the frozen WHAT's refusal to make CPL authoritative over domain case-type ontology.

---

# 9. G — Authority / decision

### REQ-B5-046
Category: Authority | Verification: AUTHORITY, ADVERSARIAL
Material Case mutations (status transitions, participant addition/removal, correction) MUST require governed authority evaluation before taking effect.

### REQ-B5-047 [REPAIRED — v0.1, RM-B5-05]
Category: Authority | Verification: UNIT, ADVERSARIAL
A material governed Case operation MUST enter authority evaluation before any canonical effect is applied. (The remaining pipeline stages — decision-before-effect, effect-produces-trace, and failure-non-fabrication — are stated as independently atomic requirements: REQ-B5-110, REQ-B5-111, REQ-B5-112.)

### REQ-B5-048
Category: Authority | Verification: TRACEABILITY
For each material Case operation, the requirements process MUST explicitly determine whether an independent canonical decision object is required; not every data write requires one (e.g. recording a `CaseEvent` of a routine, non-status-affecting nature MAY not require a separate decision object — this determination is made per-operation, not assumed uniformly).

### REQ-B5-049
Category: Authority | Verification: AUTHORITY
The following are classified as requiring a governed canonical decision: Case status transitions (`case_status` changes), `CaseParticipant` addition/removal, and any correction to previously recorded Case or CaseEvent data.

### REQ-B5-050
Category: Authority | Verification: AUTHORITY
The following are classified as NOT requiring an independent canonical decision object, provided authority is still checked: Case creation (governed by REQ-B5-011/014/018's existence checks plus authority), and routine `CaseEvent` recording that does not itself alter `case_status`.

### REQ-B5-051 [REPAIRED — v0.1, RM-B5-01]
Category: Authority | Verification: AUTHORITY, ADVERSARIAL
A governed authority-checking mechanism MUST exist for B5 operations requiring authority evaluation. The mechanism MUST preserve `ROLE ≠ AUTHORITY ≠ PERMISSION ≠ IDENTITY` and MUST be testable independently of participant role. This requirement does NOT mandate a specific implementation class or service (e.g. it does not require reuse of B3/B4's `AuthorityContext`); reuse of existing CPL authority infrastructure is permitted and recommended, not semantically required by this Build Unit. B5 MUST NOT introduce a new or parallel authorization engine beyond whatever single mechanism it adopts.

---

# 10. H — Execution pointer boundary

### REQ-B5-052 [REPAIRED — v0.1, RM-B5-03]
Category: Boundary | Verification: STATIC, ADVERSARIAL
`Case.current_execution_id` and `CaseEvent.execution_id` MAY be stored and preserved by B5 as opaque references. B5 MUST NOT interpret or govern raw `RunnerExecution` lifecycle/status semantics.

### REQ-B5-053
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT derive Case authority from `RunnerExecution` state.

### REQ-B5-054
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT gate any Case lifecycle transition on execution semantics (e.g. a Case MUST NOT be automatically closed because its `current_execution_id` execution completed).

### REQ-B5-055 [REPAIRED — v0.1, RM-B5-03]
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT derive, promote, or represent execution success/failure as a B5-governed Case fact, regardless of how such execution outcome is represented by Execution Governance. This is distinct from REQ-B5-052 (raw execution status interpretation): REQ-B5-052 prohibits reading `RunnerExecution` status at all; this requirement prohibits any Case-level fact being *derived* from that status even if it were read.

### REQ-B5-056
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT interpret `parent_execution_id` or any execution lineage semantics.

### REQ-B5-057
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT correct or supersede `RunnerExecution` records.

### REQ-B5-058
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT derive domain truth from the mere presence or outcome of a referenced execution.

### REQ-B5-059
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT claim complete execution-history navigation; historical reconstruction of `RunnerExecution`/`RunnerArtifact` content belongs to Execution Governance.

### REQ-B5-060
Category: Boundary | Verification: TRACEABILITY
Acceptance evidence MUST demonstrate that a Case with a `current_execution_id` pointing to an execution in any status (including a hypothetical `FAILED` status) does not cause B5 to expose any inferred Case-level fact derived from that status.

---

# 11. I — History / reconstructability

### REQ-B5-061
Category: History | Verification: HISTORY, POSTGRESQL
The system MUST preserve reconstructable history for Case creation.

### REQ-B5-062
Category: History | Verification: HISTORY
The system MUST preserve reconstructable history for Case lifecycle (`case_status`) changes.

### REQ-B5-063
Category: History | Verification: HISTORY
The system MUST preserve reconstructable history for `CaseParticipant` addition, change, and removal where authorized.

### REQ-B5-064
Category: History | Verification: HISTORY
The system MUST preserve every recorded `CaseEvent` as part of Case history (append-only, per REQ-B5-034).

### REQ-B5-065
Category: History | Verification: HISTORY
The system MUST support historical reconstruction of a governed correction (see family J) without erasing the pre-correction state.

### REQ-B5-066
Category: History | Verification: HISTORY
Where a Case lifecycle reversal (e.g. `CLOSED → REOPENED`) is permitted by the existing enum, the system MUST preserve the history of both the original transition and the reversal.

### REQ-B5-067
Category: History | Verification: HISTORY
The system MUST support recording that an execution reference was later attached to a Case (`current_execution_id` set after Case creation) as part of reconstructable history.

### REQ-B5-068
Category: History | Verification: UNIT
Current Case view (present state) and historical Case reconstruction (state at a prior point, or the sequence of changes) MUST be distinct, independently queryable properties.

---

# 12. J — Correction / supersession (GAP-03)

### REQ-B5-069
Category: Correction | Verification: HISTORY, ADVERSARIAL
The system MUST support correction of Case metadata (e.g. `title`, `case_type`) such that the correction does not silently overwrite the prior value without preserving it as reconstructable history.

### REQ-B5-070
Category: Correction | Verification: HISTORY, ADVERSARIAL
The system MUST support correction of `CaseParticipant` records with the same history-preservation property.

### REQ-B5-071
Category: Correction | Verification: HISTORY, ADVERSARIAL
The system MUST support correction of a previously recorded `CaseEvent` (e.g. a `DIAGNOSIS_REPORTED` event later found to have been recorded incorrectly) such that the original event remains reconstructable and the correction is distinguishable from the original.

### REQ-B5-072
Category: Correction | Verification: ADVERSARIAL
`CORRECTION ≠ HISTORY DELETION` MUST hold for every correction path in this Build Unit — no correction operation may delete or destructively overwrite the record being corrected.

### REQ-B5-073
Category: Correction | Verification: STATIC
The requirements process MAY require new schema (e.g. a supersession-linkage column analogous to `RunnerArtifact.supersedes_artifact_id`) to satisfy REQ-B5-069→072, since current `Case`/`CaseEvent` schema does not yet provide this substrate.

### REQ-B5-074
Category: Correction | Verification: STATIC
This Build Unit MUST NOT pre-design or mandate: universal event sourcing, a generic correction engine, or a wholesale copy of B4's `CanonicalAssetIdentityDecision`-style structure, merely to satisfy REQ-B5-069→072. The minimum sufficient mechanism is a requirements/implementation decision.

**Note:** GAP-03 remains OPEN. REQ-B5-069→074 establish the semantic obligation (correction preserves history) as testable without pre-deciding the schema shape.

---

# 13. K — Idempotency

### REQ-B5-075
Category: Idempotency | Verification: IDEMPOTENCY, ADVERSARIAL
Replaying the same governed Case-creation request MUST NOT create a duplicate Case.

### REQ-B5-076
Category: Idempotency | Verification: IDEMPOTENCY, ADVERSARIAL
Replaying the same governed Case-status-transition request MUST NOT create a duplicate canonical transition.

### REQ-B5-077
Category: Idempotency | Verification: IDEMPOTENCY, ADVERSARIAL
Replaying the same governed `CaseParticipant` addition/removal request MUST NOT create a duplicate canonical transition.

### REQ-B5-078
Category: Idempotency | Verification: IDEMPOTENCY
Idempotency identity MUST be established by governed request/operation identity, not by payload similarity alone (`SAME PAYLOAD ≠ SAME OPERATION IDENTITY`).

### REQ-B5-079
Category: Idempotency | Verification: ADVERSARIAL
Two distinct governed requests with identical payload content (e.g. two separate `CaseParticipant` additions with the same role for the same Contact, issued under different governed operation identities) MAY legitimately produce two distinct outcomes; the system MUST NOT silently collapse them into one merely because their content matches.

---

# 14. L — Failure semantics

### REQ-B5-080 [REPAIRED — v0.1, RM-B5-04]
Category: Outcome | Verification: ADVERSARIAL
The system MUST distinguish authority rejection (operation denied due to insufficient authority) from semantic rejection (operation denied due to invalid Case state). **Boundary example:** an authorized policy evaluation explicitly denying a Case-close request MUST classify as `AUTHORITY_REJECTION`, never as `TECHNICAL_FAILURE`. **Boundary example:** a Case-close request that violates a frozen B5 semantic constraint (e.g. an attempted post-creation `asset_id` rebinding per REQ-B5-018a) MUST classify as `SEMANTIC_REJECTION`, not `AUTHORITY_REJECTION`.

### REQ-B5-081 [REPAIRED — v0.1, RM-B5-04]
Category: Outcome | Verification: ADVERSARIAL
The system MUST distinguish an unresolved condition (e.g. an operation that cannot yet proceed) from a semantic rejection (an operation that will never be valid as requested). **Boundary example:** a required governing fact that cannot yet be determined, with no contradiction present, MUST classify as `UNRESOLVED`, never as a rejection.

### REQ-B5-082 [REPAIRED — v0.1, RM-B5-04]
Category: Outcome | Verification: ADVERSARIAL
The system MUST distinguish a conflict (e.g. concurrent conflicting Case mutations) from a technical failure (e.g. database unavailability). **Boundary example:** two mutually incompatible authoritative inputs/decisions MUST classify as `CONFLICT`, never as `UNRESOLVED` or `TECHNICAL_FAILURE`. **Boundary example:** a database unavailable during an otherwise admissible operation MUST classify as `TECHNICAL_FAILURE` and MUST NOT create a canonical negative decision (cross-reference REQ-B5-083).

### REQ-B5-083
Category: Outcome | Verification: ADVERSARIAL
Technical failure MUST NOT be silently represented as a governed negative decision (e.g. a database timeout MUST NOT be recorded as "Case mutation rejected").

### REQ-B5-084
Category: Outcome | Verification: ADVERSARIAL
A failed write MUST NOT fabricate canonical history — no `CaseEvent` or decision record may be created describing a transition that did not actually take effect.

---

# 15. M — Case-to-Case consolidation boundary (GAP-01)

### REQ-B5-085
Category: Boundary | Verification: STATIC, ADVERSARIAL
The system MUST NOT introduce Case merge, Case survivor selection, Case consolidation, Case-to-Case supersession, or duplicate-Case resolution semantics.

### REQ-B5-086
Category: Boundary | Verification: STATIC
`SAME UNDERLYING MATTER ≠ SAME CPL CASE` MUST be preserved — two Cases concerning what may later be determined to be the same operational matter MUST remain two distinct, independently governed Cases under this Build Unit.

### REQ-B5-087
Category: Boundary | Verification: TRACEABILITY
If implementation discovers that Case consolidation is required to satisfy any other frozen requirement, the correct response is `WHAT_REVISION_REQUIRED` — this Requirement Matrix does not authorize inventing consolidation semantics to resolve such a discovery.

**Note:** GAP-01 remains OPEN, explicitly excluded from this Build Unit's scope.

---

# 16. N — Ontology vocabulary (GAP-04)

### REQ-B5-088
Category: Boundary | Verification: STATIC
Requirements and implementation MUST use "Case" as the currently admitted Build Unit vocabulary, matching the physical table name (`cases`), without this usage constituting a claim that "Case" is the final, permanent canonical ontology name.

### REQ-B5-089
Category: Boundary | Verification: STATIC
This Requirement Matrix MUST NOT require schema or table renaming merely to settle the ontology-vocabulary question.

### REQ-B5-090
Category: Boundary | Verification: STATIC
`PHYSICAL TABLE NAME ≠ CANONICAL ONTOLOGY NAME` remains an open question; no requirement in this matrix may declare it resolved.

**Note:** GAP-04 remains OPEN, non-blocking for requirements purposes per REQ-B5-088.

---

# 17. O — Domain-truth boundary

### REQ-B5-091
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT decide or represent as CPL-authoritative: diagnosis correctness.

### REQ-B5-092
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT decide or represent as CPL-authoritative: vehicle/Asset operability.

### REQ-B5-093
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT decide or represent as CPL-authoritative: repair success.

### REQ-B5-094
Category: Boundary | Verification: ADVERSARIAL
B5 MUST NOT decide or represent as CPL-authoritative: insurance liability, regulatory eligibility, or technical safety determinations.

### REQ-B5-095
Category: Boundary | Verification: STATIC
Domain-owned assertions MAY be represented within `CaseEvent.payload` or equivalent, but their presence MUST NOT be interpreted as CPL having independently established their truth.

---

# 18. P — Anti-workflow boundary

### REQ-B5-096
Category: Boundary | Verification: STATIC, ADVERSARIAL
B5 MUST NOT require or implement a BPMN engine, generic task scheduler, dependency-graph engine, trigger/rule orchestration system, or generic work-item platform to function.

### REQ-B5-097
Category: Boundary | Verification: ADVERSARIAL
Case lifecycle governance (family F) MUST be satisfiable without any of the mechanisms in REQ-B5-096.

---

# 19. Q — Anti-event-sourcing boundary

### REQ-B5-098
Category: Boundary | Verification: ADVERSARIAL
`CaseEvent` history MUST NOT be required as the sole mechanism from which current Case state (`case_status` and other current fields) must be derived; `case_status` remains an independently stored, directly queryable current-state field.

### REQ-B5-099
Category: Boundary | Verification: STATIC
Event history and canonical current state MAY coexist without one being derived exclusively from the other.

---

# 20. R — actor_type boundary

### REQ-B5-100
Category: Boundary | Verification: STATIC
The existing `actor_type` enum (`CONTACT, SYSTEM, RUNNER, ADMIN, EXTERNAL_PARTY`) is inherited B2 implementation, not automatically canonical CPL ontology.

### REQ-B5-101
Category: Boundary | Verification: STATIC
Requirements MUST NOT introduce a generalized Actor/Role object or hierarchy to satisfy `CaseEvent`/`CaseParticipant` actor-attribution needs.

### REQ-B5-102
Category: Boundary | Verification: TRACEABILITY
If the existing `actor_type` enum is found insufficient for a specific, bounded operational need during requirements refinement, the correct response is a bounded enum-value repair proposal, not a generalized Actor model.

---

# 21. S — Verification and evidence

### REQ-B5-103
Category: Verification | Verification: REGRESSION
The candidate MUST execute the complete accepted B1–B4 regression suite against real PostgreSQL without weakening any existing assertion.

### REQ-B5-104
Category: Verification | Verification: MIGRATION
The candidate MUST demonstrate clean migration from the accepted B4 head to the new B5 head, on a fresh database.

### REQ-B5-105
Category: Verification | Verification: MIGRATION
The candidate MUST demonstrate migration round-trip (upgrade → downgrade → upgrade) without corruption, if downgrades are implemented.

### REQ-B5-106
Category: Verification | Verification: POSTGRESQL
All persistence, authority, idempotency, correction, and history requirements in this matrix MUST be verified against real PostgreSQL; mock-only verification is insufficient for database behavior.

### REQ-B5-107
Category: Verification | Verification: TRACEABILITY
The implementation MUST provide requirement coverage evidence for `REQ-B5-001` → `REQ-B5-107` (this matrix); no requirement may silently disappear.

### REQ-B5-108
Category: Verification | Verification: REGRESSION
`/health` and `/ready` (including PostgreSQL-unavailable failure behavior) MUST NOT regress.

---

# 21a. T — Repair-introduced requirements [ADDED — v0.1]

### REQ-B5-109 [ADDED — v0.1, RM-B5-02]
Category: Boundary | Verification: ADVERSARIAL, POSTGRESQL
After Case creation, `Case.asset_id` MUST NOT be changed to reference a different Asset under B5 Case Governance. Verification MUST include: (1) a Case created with Asset A; (2) an attempted update of `asset_id` to Asset B; (3) confirmation the operation is rejected; (4) confirmation historical and current Case identity remain anchored to Asset A. If future business semantics require Case-to-different-Asset rebinding, that requires separate governance/WHAT authorization — this requirement does not authorize inventing Case merge, Case migration, or Asset survivor semantics to satisfy any such future need.

### REQ-B5-110 [ADDED — v0.1, RM-B5-05]
Category: Authority | Verification: UNIT, ADVERSARIAL
Where a material governed Case operation requires a canonical decision, the decision MUST be established before the governed effect is applied.

### REQ-B5-111 [ADDED — v0.1, RM-B5-05]
Category: Authority | Verification: HISTORY, ADVERSARIAL
A successfully applied governed Case effect MUST produce sufficient trace/history to reconstruct the decision/effect relationship.

### REQ-B5-112 [ADDED — v0.1, RM-B5-05]
Category: Authority | Verification: ADVERSARIAL
Failure at one pipeline stage (authority evaluation, canonical decision, effect, or history/trace) MUST NOT fabricate completion of a later stage.

### REQ-B5-113 [ADDED — v0.1, RM-B5-06]
Category: Idempotency | Verification: IDEMPOTENCY, ADVERSARIAL
When an already-processed governed operation is replayed using the same operation identity, the system MUST return or make deterministically retrievable the canonical outcome of the original operation. The replay MUST NOT create a second canonical effect, fabricate a new result, or silently return a no-op without allowing recovery of the original outcome. **Adversarial test:** operation O executes successfully; the caller does not receive or loses the response; the caller retries O using the same operation identity; the system MUST return or expose the original canonical outcome, and only one canonical effect MUST exist.

### REQ-B5-114 [ADDED — v0.1, RM-B5-07]
Category: History | Verification: HISTORY, POSTGRESQL
`CaseEvent.occurred_at` and `CaseEvent.created_at` MUST remain independently representable and independently queryable. The system MUST NOT silently normalize or overwrite one with the other. **Verification example:** an event that occurred yesterday but is recorded today MUST show `occurred_at` = yesterday and `created_at` = today, with both values reconstructable.

### REQ-B5-115 [ADDED — v0.1, RM-B5-08]
Category: Classification | Verification: STATIC, TRACEABILITY
Every governed `CaseEvent.event_type` definition MUST have a documented/determinable semantic class (per the `WORLD EVENT ≠ DOMAIN ASSERTION ≠ CPL OPERATIONAL FACT ≠ CANONICAL DECISION CONSEQUENCE` distinction). The semantic class MUST be determinable at definition time and verifiable without interpreting arbitrary payload contents. This requirement does not mandate a new database column, ontology table, enum expansion, or specific storage mechanism — GAP-02 remains open on mechanism. **Adversarial test:** given `DIAGNOSIS_REPORTED` and `CASE_CLOSED`, a reviewer MUST be able to determine that these belong to different semantic categories without guessing from payload content.

---

# 22. Requirement count

```text
REQ-B5-001 → REQ-B5-115
```

**115 requirements** (108 from `v0`, of which 7 were repaired in place — `REQ-B5-047`, `051`, `052`, `055`, `080`, `081`, `082` — and 7 new requirements appended: `REQ-B5-109` → `115`).

---

# 23. Traceability table

| Requirement range | Frozen WHAT source | Semantic obligation |
|---|---|---|
| 001–013 | WHAT §6–8 (Case identity, world/assertion boundary) | Case is a stable, non-world-asserting CPL identity |
| 014–018 | WHAT §9 (REPAIR-03, Asset anchoring) | `asset_id NOT NULL`; Asset-optional out of scope |
| 019–026 | WHAT §12–14 (CaseParticipant boundary) | Participation ≠ durable relationship; role ≠ authority |
| 027–034 | WHAT §15–16 (CaseEvent boundary) | Event ≠ world fact ≠ decision |
| 035–038 | WHAT §39a GAP-02 | Minimum classification boundary, non-blocking |
| 039–045 | WHAT §11 (Case status boundary) | Case status ≠ domain state |
| 046–051 | WHAT §24–27 (Authority/decision pattern) | Governed decision pattern, applied selectively |
| 052–060 | WHAT §21a (REPAIR-01, execution pointer boundary) | Opaque reference discipline |
| 061–068 | WHAT §30 (current/historical navigation) | Reconstructable history |
| 069–074 | WHAT §28–29, §39a GAP-03 | Correction ≠ deletion; schema TBD |
| 075–079 | WHAT §31 (idempotency) | Governed replay safety |
| 080–084 | WHAT F19-equivalent outcome discipline (by analogy to B3/B4, applied fresh to Case) | Technical failure ≠ governed rejection |
| 085–087 | WHAT §39a GAP-01 | Case merge/consolidation excluded |
| 088–090 | WHAT §39a GAP-04 | Ontology vocabulary open |
| 091–095 | WHAT §32 (domain boundary) | No domain-truth authority |
| 096–097 | WHAT §33 (anti-workflow) | No workflow engine |
| 098–099 | WHAT §34 (anti-event-sourcing) | No universal event sourcing |
| 100–102 | WHAT §18–19 (OSQ-03, actor_type) | Inherited, not frozen ontology |
| 103–108 | Mandate-level verification obligations (B3/B4 precedent) | Evidence discipline |

No frozen WHAT obligation is orphaned; no requirement expands scope beyond `Case`/`CaseParticipant`/`CaseEvent`.

---

# 24. Open-gap table

```text
GAP-01
Status: OPEN / NON-BLOCKING
Requirement impact: REQ-B5-085..087 explicitly exclude Case
merge/consolidation; no requirement depends on it being resolved.

GAP-02
Status: OPEN / NON-BLOCKING
Requirement impact: REQ-B5-035..038 establish a minimum testable
classification boundary without mandating a specific mechanism;
requirements do not depend on further resolution.

GAP-03
Status: OPEN / NON-BLOCKING
Requirement impact: REQ-B5-069..074 establish the semantic
correction obligation; the requirements process may determine
new schema is needed downstream (Requirement Challenge/repair
territory), but this matrix itself is not blocked by the
unresolved schema shape.

GAP-04
Status: OPEN / NON-BLOCKING
Requirement impact: REQ-B5-088..090 use "Case" pragmatically
without resolving the naming question; no requirement depends
on its resolution.
```

No gap forced `REQUIREMENTS_BLOCKED_BY_WHAT_GAP`.

---

# 25. Quality gate self-check

```text
QG-01  Every frozen B5 semantic boundary has coverage           PASS
QG-02  No requirement expands the frozen WHAT                    PASS
QG-03  No requirement silently resolves GAP-01..04                PASS (see §24)
QG-04  No requirement absorbs Execution Governance                PASS (family H is exclusionary by design)
QG-05  No requirement turns Case into workflow                    PASS (family P)
QG-06  No requirement turns CaseEvent into event sourcing          PASS (family Q)
QG-07  No requirement grants B5 domain-truth authority             PASS (family O)
QG-08  Material mutations have explicit authority semantics        PASS (family G)
QG-09  Correction/history requirements sufficient for reconstruction PASS (families I, J)
QG-10  Idempotency requirements independently testable              PASS (family K)
QG-11  Current/historical views remain distinguishable               PASS (REQ-B5-068)
QG-12  Technical failure distinct from governed rejection             PASS (family L)
QG-13  Every requirement has verification criteria                    PASS (Verification field on each)
QG-14  Every requirement has traceability                              PASS (§23)
QG-15  No duplicate requirements with different wording                 PASS (reviewed)
```

---

# 26. Build Structure protection

`B5_CASE_GOVERNANCE → Execution Governance` ordering is preserved. `RunnerExecution` and `RunnerArtifact` are not absorbed; family H (execution pointer boundary) is exclusionary by construction — every requirement in it prohibits B5 from governing execution semantics, none authorizes it.

---

# 27. Governance status

```text
B5 Case Governance WHAT
  FROZEN

B5 Requirement Matrix v0
  PRODUCED
  CHALLENGED
  REPAIR_REQUIRED

B5 Requirement Matrix v0.1
  PRODUCED
  115 requirements effective
  8/8 repairs incorporated
  PROPOSED FOR REQUIREMENT RE-CHALLENGE

B5 Requirement Matrix
  NOT YET FROZEN

Execution Mandate
  NOT AUTHORIZED

Implementation
  NOT AUTHORIZED
```

---

# 27a. Repair traceability matrix [ADDED — v0.1]

| Finding | Affected REQ | Repair | Repaired/new REQ | Frozen source | Closure criterion |
|---|---|---|---|---|---|
| RM-B5-01 | REQ-B5-051 | Remove mandated `AuthorityContext` class reference | REQ-B5-051 (repaired) | WHAT §18/§24 | No mandatory implementation-class reference remains |
| RM-B5-02 | Family B | Add explicit rebinding prohibition | REQ-B5-109 (new) | WHAT §9 (REPAIR-03) | Explicit requirement forbids post-creation `asset_id` mutation |
| RM-B5-03 | REQ-B5-052, 055 | Differentiate raw-status vs derived-fact levels | REQ-B5-052, 055 (repaired) | WHAT §21a (REPAIR-01) | No semantic duplication remains |
| RM-B5-04 | REQ-B5-080–082 | Add concrete boundary examples | REQ-B5-080, 081, 082 (repaired) | Outcome discipline (B3/B4-analogous, B5-grounded) | Each category has ≥1 concrete pass/fail example |
| RM-B5-05 | REQ-B5-047 | Split pipeline into atomic stages | REQ-B5-047 (repaired), 110, 111, 112 (new) | WHAT §24–27 | Pipeline stages independently testable |
| RM-B5-06 | Family K | Add replay-outcome-retrieval requirement | REQ-B5-113 (new) | WHAT §31 | Replay outcome retrieval explicit and testable |
| RM-B5-07 | (orphaned) | Add `occurred_at`/`created_at` requirement | REQ-B5-114 (new) | WHAT §17 | Requirement traces directly to WHAT §17, testable |
| RM-B5-08 | REQ-B5-035–038 | Add classification-determinability requirement | REQ-B5-115 (new) | WHAT §39a GAP-02 | Class-collapse detectable, mechanism remains open |

**All eight findings CLOSED IN TEXT.** This does not mean the repaired matrix is accepted — acceptance requires independent re-challenge.

---

# 27b. Non-regression [ADDED — v0.1]

```text
Case identity:                  UNCHANGED
Asset anchoring:                PRESERVED, STRENGTHENED (REQ-B5-109 rebinding prohibition)
CaseParticipant boundary:       UNCHANGED
CaseEvent boundary:              UNCHANGED
Case status ≠ domain state:      UNCHANGED
Execution Governance boundary:  UNCHANGED (REQ-B5-052/055 clarified, not weakened)
History/correction:              UNCHANGED
Anti-workflow:                   UNCHANGED
Anti-event-sourcing:              UNCHANGED
Domain truth boundary:            UNCHANGED
```

No repaired or added requirement changes B5 scope.

---

# 28. Final summary

```text
B5_CASE_GOVERNANCE_REQUIREMENT_MATRIX_v0.1
==========================================

SOURCE MATRIX:
  8b2d231912de6fe7ac5b955eb2d14de277966eb0

SOURCE CHALLENGE:
  a621128f2f9b778812804e14c75590c5fe5b7196

RM-B5-01:
  INCORPORATED

RM-B5-02:
  INCORPORATED

RM-B5-03:
  INCORPORATED

RM-B5-04:
  INCORPORATED

RM-B5-05:
  INCORPORATED

RM-B5-06:
  INCORPORATED

RM-B5-07:
  INCORPORATED

RM-B5-08:
  INCORPORATED

TOTAL REQUIREMENTS:
  115

REQUIREMENT RANGE:
  REQ-B5-001 .. REQ-B5-115

FROZEN WHAT:
  UNCHANGED

BUILD UNIT:
  B5_CASE_GOVERNANCE

EXECUTION GOVERNANCE:
  EXCLUDED

IMPLEMENTATION:
  NOT AUTHORIZED

MATRIX STATUS:
  REPAIRED
  NOT YET ACCEPTED
  NOT YET FROZEN

NEXT AUTHORIZED ARTIFACT:
  B5_CASE_GOVERNANCE_REQUIREMENT_RECHALLENGE_v0.1.md
```

**END — CPL B5 Case Governance Requirement Matrix v0.1**

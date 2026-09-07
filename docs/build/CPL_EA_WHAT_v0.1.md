# CPL_EA_WHAT_v0.1

## Pre-admission identity

```text
Provisional identity:  CPL_EA
Expanded:                CPL Execution / Artifact Governance
Status:                    BOUNDED REPAIR REVISION — NOT ACCEPTED — NOT FROZEN
```

This is a **pre-admission identity only**. It is not `B6`. No admission is implied or performed by this artifact.

---

## 0a. Repair scope

This revision repairs **only** the five findings from `CPL_EA_WHAT_CHALLENGE_v0.md`:

```text
R-EA-W01  RunnerExecution identity criterion (§6)
R-EA-W02  Artifact classification dimensions (§11)
R-EA-W03  History / parent_execution_id tension (§16/§18)
R-EA-W04  Idempotency implementation/WHAT divergence (§17)
R-EA-W05  Execution correction asymmetry (§16)
```

All other sections, decisions, exclusions, and unaffected invariants (`EA-CI01`–`04`, `06`–`11`, `13`–`15`) remain **byte-unchanged** from `v0` (commit `3a775a5f2b589dd7e526733bcff3c65edf84f4b9`). No Build Unit scope expansion. No new major primitive introduced.

```text
Governance baseline for this repair:  ed1d18099a5e6cb09758522e739f4178eec62c27
```

---

## 1. Executive definition

This WHAT defines — conceptually, not implementationally — the minimum common governance capability required to represent runner execution and its produced artifacts across VIR, PGDR, and future runner systems, without CPL becoming authority over domain truth, workflow orchestration, or runner internals. It transforms the accepted Build Structure Challenge into a challengeable conceptual definition. It does not resolve `BS-EA-01` through `06`; it carries each forward explicitly, as this instruction requires.

---

## 2. Canonical baselines

```text
Governance HEAD (this repair's baseline):  ed1d18099a5e6cb09758522e739f4178eec62c27
Canonical CPL software baseline:  2ac075daea7d162825ed73ded0c7548011242a8f
Migration head:                    026

Completed Build Units:
  B1 — Repository & Environment Bootstrap
  B2 — Database Foundation
  B3 — Identity
  B4 — Asset + Relationship
  B5 — Case Governance
B5:  CLOSED

Product-Gap Structuring:      6bacabf2d4ac6fca0630c7e7b883840cabda6eca
Build Structure Challenge:    0f79e1df07fa1761488857e06c96cb01a78ed763
Pre-admission WHAT v0:         3a775a5f2b589dd7e526733bcff3c65edf84f4b9
WHAT Challenge v0:              ed1d18099a5e6cb09758522e739f4178eec62c27

Build Structure verdict:       BUILD_STRUCTURE_ACCEPTED
EG-01:                          CONFIRMED_WITH_REPAIR
UNIT_COHESION:                   PASS
CPL_MINIMUM_FOR_VIR_PGDR_REACHED:  YES_AFTER_THIS_UNIT
POST_UNIT_CPL_BLOCKER:              NONE

WHAT Challenge v0 verdict:           WHAT_REPAIR_REQUIRED
REQUIREMENTS_READINESS (pre-repair):  REPAIR_REQUIRED
Required repairs:                      R-EA-W01, R-EA-W02, R-EA-W03,
                                       R-EA-W04, R-EA-W05
```

---

## 3. Build Unit purpose

To govern the existing, currently ungoverned B2-era substrate — `RunnerExecution` and `RunnerArtifact` — the same way B3 governed `Contact`, B4 governed `Asset`, and B5 governed `Case`: adding stable identity, authority-gated material transitions, idempotency where warranted, and correction/history discipline, without inventing new schema objects beyond what already exists, and without absorbing domain meaning from VIR or PGDR.

---

## 4. Scope

```text
IN SCOPE:
  RunnerExecution
  RunnerArtifact
  the semantic relation between them
  their attachment to already-governed Case (B5) and Asset (B4)
  their attribution to an initiating Contact (B3)
```

Nothing else. No new CPL primitive is introduced by this WHAT.

---

## 5. Explicit exclusions

```text
universal workflow engine        universal job scheduler
agent orchestration platform     generic task system
generic event bus                 generic evidence ontology
generic artifact repository        universal state engine
generalized Actor/Role system       knowledge graph
domain ontology                      domain-truth engine
frontend                              billing
VIR internals                          PGDR internals
runner registry / package manager       capability marketplace
```

None of these is demonstrated as necessary by the Build Structure Challenge evidence. None is introduced here.

---

## 6. RunnerExecution definition

> A `RunnerExecution` is a stable CPL representation of one bounded attempt to invoke a runner (an external system such as VIR or PGDR) within a governed context (a `Case`), recording that the invocation occurred, its lifecycle status, and its provenance — nothing about whether the runner's domain conclusion was correct.

**What it is NOT:**

```text
NOT Case (a Case may span zero, one, or many executions — B5, unaffected)
NOT CaseEvent (CaseEvent is append-only narrative history; RunnerExecution
  is a stateful, evolving record with its own lifecycle)
NOT a runner request in isolation (§7)
NOT a runner authorization decision
NOT a runner definition/capability descriptor
NOT a workflow, business process, or domain operation
NOT a domain result or diagnostic truth
NOT a vehicle-state assertion
NOT a task-scheduler job — no evidence found (§Build Structure Challenge
  §23) of any orchestration, queuing, or dependency-graph need
```

### 6a. Identity criterion [ADDED — v0.1, R-EA-W01]

A `RunnerExecution` is **a distinct governed occurrence of execution by a runner capability, materialized as its own execution instance and historical identity.** Its identity is the identity of that execution occurrence/instance — nothing else:

```text
SAME REQUEST        ≠  SAME RUNNEREXECUTION
SAME INPUT            ≠  SAME RUNNEREXECUTION
SAME CASE               ≠  SAME RUNNEREXECUTION
SAME RUNNER TYPE           ≠  SAME RUNNEREXECUTION
SAME DOMAIN INTENT            ≠  SAME RUNNEREXECUTION
```

Different execution attempts are different `RunnerExecution` identities **unless** a governed rule explicitly establishes replay retrieval of an already-existing execution rather than creation of a new attempt:

```text
REPLAY RETRIEVAL OF EXISTING EXECUTION  ≠  NEW EXECUTION ATTEMPT
```

This WHAT does not define database identity mechanics (the existing `execution_id` primary key is sufficient evidence that a mechanism already exists; this section states the *conceptual* criterion the mechanism must satisfy, not the mechanism itself). `idempotency_key` is explicitly **not** the ontological identity of `RunnerExecution` — see §17.

---

## 7. Execution instance vs. request

```text
EXECUTION REQUEST ≠ RUNNER EXECUTION
```

A request to invoke a runner may be rejected (authority denial, semantic rejection, technical failure at the request boundary) without any `RunnerExecution` ever being materialized. This WHAT does not mandate a particular persistence sequence — that is a Requirements/HOW decision. It only prevents treating "a request was made" as proof that "an execution occurred." Conflating the two would let an unauthorized or rejected request masquerade as a governed execution record, which this WHAT explicitly forbids.

---

## 8. Execution status

Execution status represents the state of the **common execution representation only**:

```text
EXECUTION COMPLETED  ≠  DOMAIN RESULT ACCEPTED
EXECUTION FAILED      ≠  DOMAIN ASSERTION FALSE
EXECUTION SUCCESS      ≠  DOMAIN SUCCESS
```

`execution_status = COMPLETED` means "the runner reported that its invocation finished" — never "the runner's conclusion was correct, accepted, or true." This mirrors the exact distinction B5 already froze for `Case` status (`CASE STATUS ≠ DOMAIN STATE`) and REQ-B5-052's execution-status non-interpretation boundary, applied here on the producing side rather than the consuming side. Exact status vocabulary is a Requirements-phase decision; this WHAT establishes only the semantic boundary the vocabulary must respect.

---

## 9. Runner / domain authority

```text
DOMAIN DETERMINES DOMAIN TRUTH
CPL GOVERNS COMMON CANONICAL REPRESENTATION
```

CPL may govern: execution identity, execution representation, common lifecycle semantics, provenance, the replay/retry distinction (where established, §16), artifact attachment, history, and correction/supersession where admissible (§22).

CPL must NOT become authority over: VIR's identity conclusions, PGDR's diagnostic conclusions, domain acceptance of either, domain-specific validation, or runner-internal algorithmic truth.

---

## 10. RunnerArtifact definition

> A `RunnerArtifact` is a stable CPL representation of an artifact produced, emitted, or referenced in relation to a `RunnerExecution` — an opaque, versioned, identity-bearing container, never itself the authority over what its contents mean.

`RunnerArtifact` is NOT automatically: domain truth, an accepted domain assertion, a canonical domain determination, evidence, a report, a diagnosis, an identity determination, a user-facing document, or a technical log. Each of these may be a **semantic class** an artifact belongs to (§11) — none is an inherent property of the object type itself.

```text
ARTIFACT IDENTITY  ≠  ARTIFACT SEMANTIC CLASS  ≠  ARTIFACT CONTENT  ≠  DOMAIN MEANING
```

All four are distinct and must not be collapsed.

---

## 11. Artifact classification model [REPAIRED — v0.1, R-EA-W02]

The Build Structure Challenge found (§10 of that document, sharpened with direct evidence of PGDR's own dual output — `GaragePreparationReport` vs. `UserSummary`) that a single execution may legitimately produce artifacts of genuinely different semantic character. `v0`'s classification list mixed independent dimensions (semantic function, production position, technical purpose, presentation role) into one flat, apparently-mutually-exclusive taxonomy — the WHAT Challenge (`EA-WC-02`) found this a genuine repair target, not merely stylistic.

Artifact classification is **not necessarily single-valued**. At conceptual level, distinguish at least three coexisting dimensions:

**A. Semantic function** — execution output carrier; execution evidence carrier; domain assertion carrier; domain determination carrier; technical/operational material.

**B. Production / lifecycle role** — intermediate; final.

**C. Consumption / presentation role** — internal; product-displayable.

These dimensions **may coexist**. An artifact may therefore simultaneously be `FINAL` + `DOMAIN DETERMINATION CARRIER` + `PRODUCT-DISPLAYABLE` without contradiction — exactly PGDR's own `GaragePreparationReport` (final, domain-assertion-carrying, and, unlike `UserSummary`, primarily internal/technician-facing rather than product-displayable in the consumer sense).

```text
ARTIFACT CLASSIFICATION IS NOT NECESSARILY SINGLE-VALUED
SEMANTIC FUNCTION  ≠  LIFECYCLE POSITION
SEMANTIC FUNCTION  ≠  PRESENTATION ROLE
LIFECYCLE POSITION  ≠  PRESENTATION ROLE
```

No exact enum values are frozen here. Requirements may later determine the minimum enforceable vocabulary per dimension. This WHAT freezes only the **orthogonality** of the dimensions — that a single flat classification cannot correctly represent an artifact's semantic character.

```text
PAYLOAD FORMAT  ≠  SEMANTIC CLASS
JSON  ≠  ONTOLOGY
ARTIFACT TYPE STRING  ≠  DOMAIN AUTHORITY
```

The exact mechanism (a registry table, an enum per dimension, something else) is explicitly a Requirements/HOW decision — B5's `CaseEventType` registry is available evidence of one working precedent for a single-dimension case, not a mandate to copy it unchanged for a multidimensional model.

---

## 12. VIR artifact boundary

```text
VIR RunnerExecution
        ↓
VIR-produced artifact
        ↓
artifact may carry/reference VIR's determination
        ↓
CPL governs artifact identity/provenance/history
        ↓
VIR remains authority over the domain meaning of that determination
```

```text
VIR ARTIFACT STORED  ≠  VIR DETERMINATION ACCEPTED BY CPL
```

CPL does not become vehicle-identity authority merely by storing VIR's output. This preserves the exact chain the Build Structure Challenge traced in its VIR artifact test (§11 of that document): CPL governs only from "runner output" onward, never re-deriving or validating the identity itself.

---

## 13. PGDR artifact boundary

```text
PGDR RunnerExecution
        ↓
PGDR-produced artifact
        ↓
artifact may carry diagnosis/recommendation/assertion
        ↓
CPL governs representation
        ↓
PGDR remains domain authority
```

```text
STORING PGDR OUTPUT  ≠  CPL MAKING THE DIAGNOSIS
```

This is structurally identical to how B4's `DomainProjection` already holds `VehicleDetail` content without CPL adjudicating it — no new pattern is invented, an existing one is extended to a new object.

---

## 14. VIR → PGDR handoff boundary

```text
Case
  ↓
VIR RunnerExecution
  ↓
VIR RunnerArtifact(s)
  ↓
[integration layer selects/transforms relevant domain material]
  ↓
PGDR RunnerExecution
  ↓
PGDR RunnerArtifact(s)
```

Direct artifact-to-artifact coupling is **not** frozen here — the Build Structure Challenge found concrete evidence (PGDR's own `PGDR-ID-001`: "Input contract only — PGDR never reconstructs VIR logic") that PGDR consumes a *projection* (`DiagnosticIdentityContext`'s shape), not a raw VIR artifact. The construction of that projection belongs to an integration layer that does not yet exist anywhere and is explicitly out of this WHAT's scope (see `BS-EA-06` disposition, §26).

---

## 15. Provenance

Minimum common provenance dimensions, distinguished from validity:

```text
producing RunnerExecution      runner type/version
generation time                  artifact identity
content integrity                 source reference (open — see BS-EA-05, §26)
supersession lineage
```

```text
PROVENANCE  ≠  VALIDITY
TRACEABILITY  ≠  AUTHORITY
```

---

## 16. History / correction / supersession [REPAIRED — v0.1, R-EA-W03, R-EA-W05]

Execution history must be reconstructable sufficiently to distinguish: `RunnerExecution` identity, recorded lifecycle transitions, produced `RunnerArtifact`s, artifact supersession/correction, and **explicit provenance relations that have governed semantics**. It does **not** require generic execution lineage reconstruction.

```text
HISTORY RECONSTRUCTABILITY  ≠  MANDATORY EVENT-SOURCING ARCHITECTURE
EXECUTION HISTORY  ≠  EXECUTION LINEAGE GRAPH
HISTORICAL RECONSTRUCTABILITY DOES NOT IMPLY SEMANTIC INTERPRETATION OF parent_execution_id
```

`v0`'s original text required distinguishing "execution attempts where conceptually distinct" — the WHAT Challenge (`EA-WC-04`) found this presupposes a criterion for attempt-distinctness that only `parent_execution_id` could plausibly supply, directly contradicting §18's deliberate opacity of that field. This is now narrowed: history reconstructability applies to `RunnerExecution` identity (§6a) and governed relations only — never to an inferred "attempt lineage" derived from `parent_execution_id`.

`RunnerArtifact` already has schema-level supersession substrate (`supersedes_artifact_id`). This WHAT establishes the conceptual distinctions that substrate must respect:

```text
SUPERSESSION  ≠  DELETION
CORRECTION  ≠  MUTATING HISTORY
NEW ARTIFACT  ≠  NEW EXECUTION
```

**Correction boundary**, distinguishing five candidate correction targets:

```text
A. execution representation        — CPL MAY govern (common representation concern) — see below
B. artifact metadata                 — CPL MAY govern
C. artifact content                   — CPL MAY govern (still opaque payload correction,
                                         not adjudication of what it means)
D. domain assertion                    — domain-governed, NOT CPL
E. domain determination                 — domain-governed, NOT CPL
```

```text
CORRECTING CPL REPRESENTATION  ≠  CORRECTING DOMAIN TRUTH
```

**Execution correction asymmetry, named explicitly [R-EA-W05]:** unlike `RunnerArtifact`, `RunnerExecution` currently has **no** schema-level correction/supersession substrate (no self-referential field analogous to `supersedes_artifact_id`). A historical `RunnerExecution` represents an execution *occurrence* — the occurrence itself must never be rewritten as if a different execution happened:

```text
HISTORICAL EXECUTION OCCURRENCE  ≠  MUTABLE DOMAIN FACT
CORRECTION OF EXECUTION REPRESENTATION  ≠  REWRITING EXECUTION HISTORY
```

Conceptually permitted, without inventing a generic `RunnerExecution` supersession model unless future evidence requires one:

```text
A. correction of non-occurrence metadata where governance permits
B. append/history-preserving correction of misrepresented execution metadata
C. a genuinely new attempt is a NEW RunnerExecution (§6a), never a correction
   of the prior one
D. domain-result correction happens entirely outside RunnerExecution
   semantics (VIR's or PGDR's own domain, never CPL's)
```

```text
NEW EXECUTION ATTEMPT  →  NEW RUNNEREXECUTION
METADATA CORRECTION DOES NOT AUTOMATICALLY  →  NEW RUNNEREXECUTION

CORRECTING EXECUTION REPRESENTATION  ≠  CORRECTING VIR DETERMINATION
CORRECTING EXECUTION REPRESENTATION  ≠  CORRECTING PGDR DIAGNOSIS
```

The exact mechanism for (B) is explicitly a Requirements/HOW decision, not designed here.

---

## 17. Replay / retry / idempotency treatment [REPAIRED — v0.1, R-EA-W04]

```text
REPLAY  ≠  RETRY
SAME REQUEST  ≠  SAME EXECUTION
SAME INPUT  ≠  SAME EXECUTION
SAME EXECUTION  ≠  SAME ARTIFACT
```

**Implementation fact acknowledged, not treated as absent:** the current CPL software baseline (`2ac075d`) enforces uniqueness through an existing database constraint, `runner_executions_idempotency_uq` — a partial unique index on `(runner_type, idempotency_key) WHERE idempotency_key IS NOT NULL`. The WHAT Challenge (`EA-WC-01`) correctly found `v0`'s original framing ("necessity and exact semantics remain unproven... not assumed necessary") could not stand unqualified against this executable fact: the key is not "merely present," it is already actively enforced.

```text
IMPLEMENTATION FACT  ≠  FROZEN SEMANTIC MEANING
```

The existence of the unique index alone does **not** establish that `idempotency_key` means execution identity, retry identity, request identity, domain-operation identity, or payload identity — all of these remain distinct from it:

```text
IDEMPOTENCY KEY  ≠  RUNNEREXECUTION IDENTITY
IDEMPOTENCY KEY  ≠  INPUT IDENTITY
IDEMPOTENCY KEY  ≠  DOMAIN OPERATION IDENTITY
```

**Minimum conceptual interpretation frozen by this WHAT:** `idempotency_key` is an existing execution-operation deduplication / replay-control mechanism whose precise scope and replay contract must be defined before requirements freeze. Requirements may specify: scope, uniqueness domain, behavior on duplicate submission, retrieval behavior, conflict behavior, and relationship with retry — but Requirements must **not** invent what `RunnerExecution` itself is (§6a already fixes that independently of this field).

```text
BS-EA-03 = SEMANTIC CORE PARTIALLY RESOLVED IN WHAT
           + OPERATIONAL CONTRACT OPEN FOR REQUIREMENTS
```

---

## 18. parent_execution_id treatment [REPAIRED — v0.1, R-EA-W03]

**Carrying forward `BS-EA-02` explicitly, not resolved here.** This WHAT does NOT interpret `parent_execution_id` as retry, child execution, delegation, continuation, correction, orchestration, or workflow dependency. The Build Structure Challenge found genuine, non-invented evidence (VIR's `ClarifyResolutionUseCase`: new `resolution_id`, preserved `request_id`) suggesting "continuation/refinement" is the best-supported candidate reading — but evidence supporting a *plausible* reading is not the same as establishing the *canonical* one.

```text
PARENT POINTER EXISTS  ≠  PARENT SEMANTICS ARE KNOWN
```

Until a demonstrated product/common need establishes a specific relation, `parent_execution_id` is:

```text
EXISTING SUBSTRATE
+
SEMANTICALLY UNGOVERNED BY CPL_EA v0.1
```

It must **not** be used as canonical proof of any of the following:

```text
retry            replay
continuation       delegation
dependency           correction
derivation
```

No concept such as "execution lineage" or "execution continuation relation" is introduced into the candidate ontology (§24) at this stage; the field remains semantically opaque, non-authoritative implementation substrate for this Build Unit, exactly as the Build Structure Challenge's own admission rule permits (`SCHEMA FIELD EXISTS ≠ SEMANTIC GOVERNANCE REQUIRED NOW`).

---

## 19. artifact_status treatment

**Carrying forward `BS-EA-04` explicitly, not resolved here.** `artifact_status`'s current four candidate readings (persistence / structural validation / publication / domain acceptance) are not distinguished by existing schema or by any evidence found. This WHAT prohibits the domain-acceptance reading outright:

```text
ARTIFACT STATUS  ≠  DOMAIN VALIDITY
```

unless a domain authority explicitly establishes that meaning **outside CPL** — CPL never assigns it. Exact status values remain a Requirements-phase decision.

---

## 20. Case boundary

B5 remains CLOSED. This WHAT does not reopen it.

```text
CASE  ≠  RUNNER EXECUTION
CASE STATUS  ≠  EXECUTION STATUS
CASE EVENT  ≠  RUNNER ARTIFACT
CASE HISTORY  ≠  EXECUTION HISTORY
```

`Case.current_execution_id` and `CaseEvent.execution_id` — already scoped by B5's own `REPAIR-01` as opaque, execution-governance-owned references — are the designed attachment point. This candidate consumes that boundary; it does not alter B5 semantics.

---

## 21. Asset boundary

```text
EXECUTION REFERENCES ASSET  ≠  EXECUTION OWNS ASSET IDENTITY
```

Execution Governance must not: merge Assets, determine physical identity, override VIR's physical-identity determination authority, or create/alter `ContactAssetRelationship` semantics. B4 remains fully authoritative for canonical Asset identity governance; `RunnerExecution.asset_id` is a reference, structurally identical to `Case.asset_id`'s existing, already-accepted relationship to B4.

---

## 22. Identity / initiator boundary

```text
INITIATOR  ≠  AUTHORITY
CONTACT IDENTITY  ≠  RUNNER ROLE
RUNNER ROLE  ≠  DOMAIN AUTHORITY
```

`RunnerExecution.initiated_by_contact_id` uses existing B3 identity/authority substrate exclusively. No generalized Actor/Role concept is introduced — the Build Structure Challenge found (§18 of that document) that VIR itself has no Contact concept whatsoever, meaning CPL's own B3 `Contact` is already sufficient to represent "who initiated this," with no demonstrated gap.

---

## 23. Failure boundary

```text
TECHNICAL EXECUTION FAILURE  ≠  DOMAIN REJECTION
NO ARTIFACT  ≠  DOMAIN NEGATIVE RESULT
```

Conceptual distinctions to be preserved (exact vocabulary is Requirements-phase, not frozen here): execution not authorized; execution not started; technical execution failure; execution completion; artifact production; artifact structural failure; domain rejection of output. This mirrors — without copying verbatim — the five-category discipline B5 already validated (`AUTHORITY_REJECTION/SEMANTIC_REJECTION/UNRESOLVED/CONFLICT/TECHNICAL_FAILURE`); whether the same five apply unchanged here or need adaptation is a Requirements question.

---

## 24. Candidate ontology

```text
RunnerExecution              — DEFINED (§6)
RunnerArtifact                 — DEFINED (§10)
ExecutionArtifactRelation       — the 1:N relationship between them (§26, BS-EA-01) —
                                  conceptually acknowledged, not separately reified as
                                  a new object; expressed via RunnerArtifact.execution_id,
                                  already present in schema
ArtifactSemanticClass            — the classification concept required by §11 —
                                  conceptually necessary; exact representation (new
                                  object vs. attribute vs. registry) is Requirements/HOW
ExecutionProvenance                — conceptually necessary (§15); not a new schema object,
                                  expressed via existing RunnerExecution fields
ArtifactProvenance                   — conceptually necessary (§15); likewise expressed
                                  via existing RunnerArtifact fields plus the open
                                  BS-EA-05 question
ExecutionLineage                       — NOT INTRODUCED. §18 explicitly declines to
                                  reify parent_execution_id's meaning into a named
                                  ontology concept at this stage.
```

Every included concept has: a definition (above), an identity boundary (existing PK columns), an authority boundary (§9), a lifecycle boundary (§8, §16), a relationship to existing CPL objects (§20–22), and explicit non-equivalences (throughout). No concept is included merely for architectural completeness.

---

## 25. Canonical decision question

Whether Execution/Artifact Governance requires canonical decision objects analogous to B3–B5's pattern is tested per-operation, not assumed uniformly:

```text
execution admission                — LIKELY requires governed authority evaluation
                                       (material creation of a CPL-tracked record)
execution lifecycle transition       — LIKELY requires governed decision, mirroring
                                       B5's STATUS_TRANSITION pattern
artifact registration                  — LIKELY requires governed decision (material
                                       creation), though possibly lighter-weight than
                                       execution admission
artifact supersession/correction         — LIKELY requires governed decision, mirroring
                                       B5's EVENT_CORRECTION pattern
```

"Likely" is deliberate — this WHAT identifies the conceptual need for a decision pattern without prescribing the exact object shape (a single unified decision table vs. separate ones, JSONB prior/new-value vs. typed columns) — that is a Requirements/HOW decision, following the exact same discretion B5's own WHAT exercised over its `CanonicalCaseDecision` design.

---

## 26. BS-EA-01 → 06 disposition [UPDATED — v0.1]

| Finding | Original concern | v0 treatment | Challenge finding | v0.1 treatment | Current status | Next phase | Freeze-blocking? |
|---|---|---|---|---|---|---|---|
| BS-EA-01 | RunnerArtifact is 1:N (0:N) with RunnerExecution | §11 acknowledged multiplicity | RESOLVED — exact multiplicity 0:N confirmed | Unchanged; multiplicity language preserved via repaired §11's classification model | RESOLVED | REQUIREMENTS (mechanism only) | NO |
| BS-EA-02 | `parent_execution_id` meaning underdetermined | §18 left opaque | REPAIR_REQUIRED — tension with §16's history language | §16 narrowed (R-EA-W03); §18 gained explicit prohibition list | REPAIRED — existing substrate, semantic interpretation explicitly outside CPL_EA v0.1 unless future demonstrated need | WHAT (may resurface) / REQUIREMENTS | NO |
| BS-EA-03 | `idempotency_key` necessity unproven | §17 left fully open | REPAIR_REQUIRED — contradicted by enforced unique index | §17 repaired (R-EA-W04): implementation fact acknowledged, semantic core partially resolved, operational contract open | SEMANTIC CORE PARTIALLY RESOLVED IN WHAT + OPERATIONAL CONTRACT OPEN FOR REQUIREMENTS | REQUIREMENTS | NO |
| BS-EA-04 | `artifact_status` ambiguous, risk of domain-truth collapse | §19 domain-acceptance reading prohibited | CORRECTLY_DEFERRED — no divergence found | Unchanged | PARTIALLY ADDRESSED (boundary set, exact meaning open) | REQUIREMENTS | NO |
| BS-EA-05 | No handoff-provenance field for VIR→PGDR | §15/§14 need acknowledged | CORRECTLY_DEFERRED | Unchanged | OPEN | REQUIREMENTS / HOW | NO |
| BS-EA-06 | No direct VIR→PGDR artifact dependency; projection belongs to a not-yet-existing integration layer | §14 classified outside CPL authority | CORRECTLY_DEFERRED | Unchanged | CLOSED FOR CPL'S WHAT (correctly out of scope) | DOMAIN INTEGRATION | NO (not a CPL concern at all) |

No inherited finding was renamed, silently resolved, or dropped.

---

## 27. New open questions (WHAT-level) [UPDATED — v0.1]

```text
EA-WG-01
Should artifact classification (§11) be represented as a registry
object (mirroring B5's CaseEventType) or an attribute-level mechanism
— now per-dimension, given R-EA-W02's multidimensional model?
Classification: OPEN — HOW. The dimension-mixing problem that
previously entangled this question (per the WHAT Challenge) is now
resolved by R-EA-W02; the mechanism choice itself remains open and
freeze-non-blocking.

EA-WG-02
Should execution admission and artifact registration share one
canonical decision object (mirroring B5's single
CanonicalCaseDecision covering multiple decision_types) or use
separate objects?
Classification: OPEN — HOW. Not freeze-blocking. Unchanged.

EA-WG-03
Does the existing B4 ExternalReference primitive have any role to
play in artifact provenance (§15, BS-EA-05), or is a new reference
concept needed?
Classification: OPEN — REQUIREMENTS. Not freeze-blocking. Unchanged.
```

None of these three is freeze-blocking: Requirements can proceed on each without inventing new WHAT-level semantic policy, only HOW-level representation choices.

---

## 28. Candidate invariants [REPAIRED — v0.1: EA-CI05, 12, 16, 17 rewritten; EA-CI14 retired as redundant; EA-CI18, 19 added]

```text
EA-CI01
Execution ≠ Request. A rejected request may leave no RunnerExecution.

EA-CI02
Execution ≠ Domain Result. RunnerExecution never carries a domain
conclusion.

EA-CI03
Execution Status ≠ Domain Result Status. COMPLETED means the runner
reported finishing, never that its conclusion was accepted.

EA-CI04
Artifact ≠ Domain Truth. A RunnerArtifact's existence never
constitutes CPL's endorsement of its content.

EA-CI05 [REWRITTEN — v0.1, R-EA-W02]
Artifact classification is multidimensional, not single-valued.
Semantic function ≠ lifecycle position ≠ presentation role. An
artifact's JSON content format does not by itself establish any of
these three; nor does establishing one dimension establish the
others.

EA-CI06
Content Hash ≠ Artifact Identity. Identity is the artifact's own
stable identifier, never derived from its content hash.

EA-CI07
Same Execution ≠ One Artifact. A single execution may legitimately
produce multiple, semantically distinct artifacts.

EA-CI08
Case ≠ Execution. A Case may exist independent of any execution and
may span multiple executions (B5, unaffected).

EA-CI09
CaseEvent ≠ RunnerArtifact. Case-level append-only history and
execution-produced artifacts are distinct concepts, even where one
references the other.

EA-CI10
Initiator ≠ Authority. Recording who initiated an execution never by
itself authorizes the execution.

EA-CI11
Provenance ≠ Validity. Tracing where an artifact came from never
establishes that its content is correct.

EA-CI12 [REWRITTEN — v0.1, R-EA-W05]
Correction ≠ History Deletion, asymmetrically applied. Artifact
correction/supersession has existing schema substrate
(supersedes_artifact_id); RunnerExecution has none. A historical
RunnerExecution occurrence must never be rewritten as if a different
execution happened — correction of execution representation ≠
rewriting execution history, and this holds even though (unlike
RunnerArtifact) no dedicated schema field yet exists to enforce it.

EA-CI13
CPL Representation ≠ Domain Determination. Storing VIR's or PGDR's
output in a governed container never makes CPL the author of that
output's conclusion.

EA-CI14 — RETIRED AS REDUNDANT [v0.1]
("Runner Completed ≠ Diagnosis True") merged into EA-CI03, which
already covers this as a general principle; EA-CI14 was a narrower
restatement of the same rule using a PGDR-specific example. Retired
identifier preserved here for traceability; not silently deleted.

EA-CI15
Storage of VIR/PGDR output ≠ CPL domain authority. Neither vehicle
identity nor diagnostic conclusions become CPL-determined facts merely
by being persisted through this Build Unit.

EA-CI16 [REWRITTEN — v0.1, R-EA-W04]
Schema field presence ≠ semantic governance requirement — EXCEPT
where an executable constraint already enforces behavior. An
inherited B2 column does not, by merely existing, obligate this WHAT
to assign it meaning now — but an inherited B2 CONSTRAINT (such as
runner_executions_idempotency_uq) is an implementation fact that must
be acknowledged, even though it still does not by itself define
RunnerExecution's ontological identity (see EA-CI18, §17).

EA-CI17 [REWRITTEN — v0.1, R-EA-W03]
Parent pointer existence ≠ parent semantics known, AND execution
history ≠ generic execution lineage. Preserving parent_execution_id's
opacity is a governed position; the history-reconstructability
requirement (§16) has been narrowed so it no longer presupposes any
answer about what the parent pointer means.

EA-CI18 [ADDED — v0.1, R-EA-W01]
RunnerExecution identity ≠ request identity ≠ input identity ≠ domain
operation identity ≠ Case identity ≠ runner-type identity. A new
execution attempt is a new RunnerExecution, unless a governed rule
explicitly establishes replay retrieval of an already-existing
execution rather than creation of a new attempt.

EA-CI19 [ADDED — v0.1, R-EA-W02]
Artifact semantic function ≠ artifact lifecycle role ≠ artifact
presentation role. These three classification dimensions may coexist
on a single artifact without contradiction; none subsumes another.
```

Seventeen invariants — no arbitrary target count was set; this is the set the challenge's evidence and this WHAT's own reasoning actually produced.

---

## 28a. Repair traceability [ADDED — v0.1]

| Repair ID | Challenge finding | Target section | Change made | Affected invariant(s) | Result | Residual issue |
|---|---|---|---|---|---|---|
| R-EA-W01 | EA-WC-03 (no identity criterion) | §6 | Added §6a explicit identity criterion; new EA-CI18 | EA-CI01, 07, 17; new EA-CI18 | APPLIED | None |
| R-EA-W02 | EA-WC-02 (dimension-mixing) | §11 | Replaced flat list with 3 orthogonal dimensions (semantic function, lifecycle role, presentation role); EA-CI05 rewritten; new EA-CI19 | EA-CI05; new EA-CI19 | APPLIED | Exact per-dimension vocabulary remains Requirements (EA-WG-01, unblocked not resolved) |
| R-EA-W03 | EA-WC-04 (§16/§18 tension) | §16, §18 | Narrowed §16's history requirement to exclude attempt-lineage inference; added explicit prohibition list to §18; EA-CI17 rewritten | EA-CI17 | APPLIED | None |
| R-EA-W04 | EA-WC-01 (idempotency divergence) | §17 | Acknowledged `runner_executions_idempotency_uq` by name; froze minimum conceptual interpretation; EA-CI16 rewritten | EA-CI16 | APPLIED | Operational contract (scope confirmation, duplicate/conflict behavior) remains Requirements |
| R-EA-W05 | EA-WC-05 (execution correction asymmetry) | §16 | Named the RunnerExecution/RunnerArtifact correction-substrate asymmetry explicitly; EA-CI12 rewritten | EA-CI12 | APPLIED | Exact execution-side correction mechanism remains Requirements/HOW |

All five repairs applied with explicit textual evidence in the sections above; none merely asserted in this table without a corresponding change.

---

## 29. CPL stopping condition

```text
CPL_MINIMUM_FOR_VIR_PGDR_REACHED = YES_AFTER_THIS_UNIT
```

carried forward as a construction constraint, subject to successful: WHAT acceptance → freeze/admission → requirements → build → verification → integration → closure. This WHAT introduces no requirement whose sole purpose is general CPL completeness. If this candidate is eventually built and closed, absent newly discovered blocking evidence, CPL construction for the current VIR/PGDR product should **stop**, and work should move to VIR/PGDR integration → Product/API → Frontend → operational product. This does not declare CPL permanently complete.

```text
POST_EA_COMMON_BLOCKER = NONE
```

unchanged from the Build Structure Challenge and the WHAT Challenge; the five bounded repairs applied here reveal no new common blocker.

---

## 30. Requirements-readiness self-check and re-challenge readiness

Self-check only — this is not a declaration of acceptance. Could Requirements now be written without inventing: `RunnerExecution` identity (§6a now states it explicitly); artifact classification dimensions (§11 now states three orthogonal dimensions explicitly); history vs. lineage semantics (§16/§18 tension now resolved by narrowing); minimum idempotency meaning (§17 now acknowledges the enforced constraint and freezes a minimum interpretation); execution correction semantics (§16 now names the asymmetry explicitly, even though the mechanism remains open)?

```text
WHAT_STATUS = RECHALLENGE_READY
```

This is **not** a declaration that the WHAT is accepted or frozen. It means the five bounded repairs are textually present and traceable (§28a), and the document is a legitimate target for a **targeted** re-challenge verifying only `R-EA-W01`–`05`, not a full re-challenge of the entire document.

---

## FINAL STATE

```text
CPL_EA_WHAT_v0.1
================

GOVERNANCE BASELINE:
  ed1d18099a5e6cb09758522e739f4178eec62c27

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

R-EA-W01:
  APPLIED

R-EA-W02:
  APPLIED

R-EA-W03:
  APPLIED

R-EA-W04:
  APPLIED

R-EA-W05:
  APPLIED

RUNNEREXECUTION IDENTITY:
  DEFINED (§6a)

ARTIFACT CLASSIFICATION DIMENSIONS:
  DEFINED (§11 — three orthogonal dimensions)

parent_execution_id:
  OPAQUE (§18, explicit prohibition list added)

idempotency_key:
  EXISTING ENFORCED SUBSTRATE ACKNOWLEDGED
  + MINIMUM SEMANTIC CORE DEFINED (§17)

EXECUTION CORRECTION:
  DEFINED (§16 — asymmetry with RunnerArtifact named explicitly)

BS-EA-01..06:
  ALL ACCOUNTED FOR (§26)

EA-WG GAPS:
  ALL ACCOUNTED FOR (§27)

CANDIDATE INVARIANTS:
  19 (EA-CI01..13, 15..19; EA-CI14 retired as redundant, merged into
  EA-CI03, identifier preserved for traceability)

POST-EA COMMON BLOCKER:
  NONE

CPL_MINIMUM_FOR_VIR_PGDR_REACHED:
  YES_AFTER_THIS_UNIT

WHAT STATUS:
  RECHALLENGE_READY

BUILD UNIT:
  NOT ADMITTED

B6:
  NOT ASSIGNED

REQUIREMENTS:
  NOT AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED

NEXT GOVERNANCE ACTION:
  CPL_EA_WHAT_RECHALLENGE_v0.1
```

**STOP.** No re-challenge performed in this artifact, no Build Unit admission, no B6 assignment, no WHAT freeze, no requirements, no Execution Mandate, no schema modification, no migrations, no code modification (CPL/VIR/PGDR).

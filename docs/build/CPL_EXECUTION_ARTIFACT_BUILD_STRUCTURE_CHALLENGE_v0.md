# CPL_EXECUTION_ARTIFACT_BUILD_STRUCTURE_CHALLENGE_v0

## 1. Executive verdict

```text
PRIMARY VERDICT:     BUILD_STRUCTURE_ACCEPTED
EG-01:                 CONFIRMED_WITH_REPAIR
RUNNEREXECUTION_COMMON_GOVERNANCE_REQUIRED:  YES
RUNNERARTIFACT_COMMON_GOVERNANCE_REQUIRED:    YES
UNIT_COHESION:                                  PASS
CPL_MINIMUM_FOR_VIR_PGDR_REACHED:  YES_AFTER_THIS_UNIT
```

The hypothesis survives adversarial testing, but not unchanged. Three genuine, concrete findings repair it: (1) `RunnerArtifact` is demonstrably a **one-to-many** relationship with `RunnerExecution`, not one-to-one — PGDR's own real output already produces two semantically distinct artifacts (`GaragePreparationReport`, `UserSummary`) from a single diagnostic run, evidence the Product-Gap investigation's classification finding didn't go far enough to state explicitly; (2) `parent_execution_id` now has real, non-invented candidate evidence — VIR's `ClarifyResolutionUseCase` generates a new `resolution_id` while preserving `request_id`, suggesting "continuation/refinement" over "retry," but this remains a WHAT-level decision, correctly deferrable; (3) `idempotency_key` is currently unexercised by any real need in either system — neither VIR nor PGDR has any retry-safety concept today, which bounds (but does not eliminate) what Build Unit admission can assume about it.

None of these findings block Structuring. All are WHAT-phase questions, correctly left open per this challenge's own admission rule.

---

## 2. Evidence baselines

```text
CPL software:      2ac075daea7d162825ed73ded0c7548011242a8f (independently re-checked out this pass)
CPL governance:     6bacabf2d4ac6fca0630c7e7b883840cabda6eca (independently confirmed via origin/main)
VIR:                 a342aba7cc2fc517621f4fc79c3191bdfdc9e10b (real commit, re-cloned this pass)
PGDR:                 0580b1a5ba5867a607a33197372fcaf4164f0fb6 (real commit, re-cloned this pass)
```

VIR and PGDR were treated as read-only throughout; no modification was made to either.

---

## 3. Hypothesis under challenge

`EG-HYPOTHESIS`: `RunnerExecution` and `RunnerArtifact` form one minimal coherent common governance unit that must be constructed before the minimum VIR/PGDR product can proceed. Tested across necessity, commonality, cohesion, semantic sufficiency, dependency correctness, product relevance, and premature-generalization risk, per §3 of the mandate.

---

## 4. Necessity findings

Testing the four alternatives (§5 of the mandate) against actual repository evidence:

**A. VIR/PGDR manage executions internally.** Rejected on evidence: VIR already has its own execution-adjacent record (`VehicleIdentityResolution`, SQLite-persisted) but it is VIR-scoped, has no `Case`/`Asset` linkage, and PGDR has *zero* persistence (`persistence.required: false`, confirmed directly in `runner_execution_contract.yaml`). If each system manages its own execution record, there is structurally no way to answer "what executions happened for this Case" — the exact capability the product journey (Product-Gap §10, step 14: "historical case/result reconstructable") requires and currently lacks.

**B. Product integration layer manages executions.** A genuinely viable alternative, not dismissed lightly. Failure mode found: if the integration layer (not CPL) owns execution tracking, then the VIR-integration code and the PGDR-integration code would each independently need to build an identical shape (which runner, which Case/Asset, what status, what artifact) — real, demonstrated duplication risk, since both integrations solve the exact same tracking problem against the exact same CPL-side anchors (`Case`, `Asset`, `Contact`). This is the same reasoning that justified B3/B4/B5 (a capability common to more than one consumer, adjacent to already-governed CPL objects) — not asserted by analogy alone, but because the *specific* duplication was traced concretely above.

**C. `Case` + `CaseEvent` already provide sufficient representation.** Rejected on direct evidence: `Case` is per-matter, not per-attempt (a single diagnostic Case may span multiple VIR/PGDR executions); `CaseEvent` is append-only history (B5, `event_status: CURRENT/SUPERSEDED` only) with no live execution-status concept (`RUNNING`/`COMPLETED`/`FAILED` has no `CaseEvent` equivalent). Forcing execution tracking into `CaseEvent` would require either (i) treating a stateful, evolving execution as a sequence of immutable events with no canonical "current status" field — awkward and untested — or (ii) reopening B5 to add exactly what `RunnerExecution` already has. B5 is CLOSED (§18 below); this alternative is rejected without touching it.

**D. `RunnerExecution` is necessary as a common object.** Confirmed by elimination of A and C, and by the concrete duplication risk found against B.

```text
RUNNEREXECUTION_COMMON_GOVERNANCE_REQUIRED = YES
```

---

## 5. RunnerExecution ontology findings

Testing what `RunnerExecution` actually represents, against its own schema (`app/cpl/models/runner_execution.py`, unchanged since migration `011`) and against VIR/PGDR's real behavior:

- **Not a request** — no request-payload field exists; `execution_purpose` is a nullable free-text label, not a captured request body.
- **Not a result** — that is `RunnerArtifact`'s role; `RunnerExecution` has no output field.
- **Not a domain determination** — nothing in the schema asserts vehicle identity or diagnosis; `execution_status` is a CPL-lifecycle enum (`CREATED/QUEUED/RUNNING/COMPLETED/FAILED/BLOCKED/CANCELLED`), not a domain-truth enum.
- **Is an execution instance/attempt record** — `execution_id`, `runner_type`, `runner_version`, `started_at`/`completed_at`, `execution_status` together describe exactly one invocation of one runner, nothing more. This is a stable, non-domain-specific meaning: it holds for a VIR call and a PGDR call identically, without needing to know anything about vehicles or diagnostics.

```text
REQUEST ≠ AUTHORIZATION ≠ EXECUTION ≠ RESULT ≠ DOMAIN DETERMINATION
```
holds cleanly: `RunnerExecution` is only the third of these five. `RunnerArtifact` is the fourth. Neither is the fifth — domain determination lives entirely inside VIR's `VehicleIdentityResolution`/PGDR's `DiagnosticCaseState`, never in CPL.

`RUNNER EXECUTION ≠ CASE`, `≠ CASE EVENT`, `≠ DOMAIN OPERATION`, `≠ DOMAIN RESULT` — all confirmed, no collapse found.

**Verdict: stable common meaning exists without domain-specific interpretation.** No report required under this section's failure condition.

---

## 6. Execution authority/status findings

Testing whether CPL can govern execution representation without becoming authority over domain meaning:

- **Who may request/initiate execution:** a CPL-governed decision (authority-gated, following the B3/B4/B5 pattern) — this is squarely CPL's business, since it is "may this Contact cause a CPL-tracked execution to be recorded," not "is this diagnosis correct."
- **Who determines whether execution occurred:** ambiguous by design, and correctly so — CPL records that a runner was invoked; whether the *runner itself* actually ran correctly is the runner's own concern (VIR/PGDR), reported back via `execution_status`.
- **Who determines execution success/failure:** here is the real boundary risk. `execution_status = COMPLETED` must mean "the runner reported completion," never "the runner's output is correct/accepted." Tested directly: VIR's own `resolution_status` (`resolved/ambiguous/contradictory/...`) is a *separate* concept from HTTP-level success — a VIR call can return HTTP 200 (technical success) while resolving to `contradictory` (a poor domain outcome). `RunnerExecution.execution_status = COMPLETED` must map to the former, never the latter.
- **Who may retry/cancel/supersede:** not currently answerable from schema alone — no service layer exists. This is a genuine open question, correctly deferred to WHAT (not a structuring blocker, since the *existence* of `RunnerExecution` does not require this to be pre-decided).

```text
EXECUTION STATUS ≠ DOMAIN RESULT STATUS
EXECUTION SUCCESS ≠ DOMAIN SUCCESS
```
Both hold, provided the future WHAT states this explicitly (the same discipline B4 (`CI04/05`) and B5 (`CG-CI02`) each had to name as a frozen invariant, not leave implicit).

---

## 7. parent_execution_id findings

**New, concrete evidence found this pass**, not present in the Product-Gap investigation: VIR's `ClarifyResolutionUseCase.execute()` (`src/vir/application/clarify_resolution.py`) re-runs `ResolutionEngine.resolve()`, which **always generates a brand-new `resolution_id`** (`src/vir/domain/resolution.py:91`, `uuid.uuid4()`-based, unconditional) — while explicitly preserving the original `request_id` across the call (`new_resolution.request_id = resolution.request_id`). This is a real, observed pattern: one stable "conversation" identity (`request_id`) spanning multiple distinct "attempt" identities (`resolution_id`), where each later attempt is a *refinement* of an earlier one using the same underlying request, not a blind retry of identical input.

This is suggestive, non-invented evidence that `parent_execution_id` — if it is ever governed — most plausibly represents **continuation/refinement** (an execution that supersedes or builds on a prior one within the same logical session) rather than pure retry-after-failure or an arbitrary execution graph. PGDR provides no comparable evidence (its `resume` CLI command "only echoes a JSON file back — not a real session-resumption feature," confirmed directly in `runner_execution_contract.yaml`; its `DiagnosticLoop` iterates within a single process, never spawning multiple runner invocations).

```text
SCHEMA FIELD EXISTS ≠ SEMANTIC GOVERNANCE REQUIRED NOW
```
holds: the field can remain present-but-opaque for Build Unit admission. This challenge does not resolve OSQ-02; it narrows it with real evidence for the future WHAT to use, without freezing an answer here.

---

## 8. Replay/retry/idempotency findings

Direct search of both repositories (`grep -rln "idempotency|idempotent"`) returns **zero results in either VIR or PGDR.** Neither system has any concept of a retry-safe operation identity today — VIR generates a fresh `resolution_id` on every call including clarifications; PGDR generates a fresh `--request-id` (timestamp-based) on every CLI invocation with no dedup mechanism.

```text
SAME OPERATION IDENTITY ≠ SAME EXECUTION ATTEMPT
REPLAY ≠ RETRY
RETRY ≠ CHILD EXECUTION
SAME INPUT ≠ SAME EXECUTION
SAME EXECUTION ≠ SAME RESULT
```
All hold as distinct concepts. **Finding:** since neither consuming system currently exercises idempotency at all, `RunnerExecution.idempotency_key` cannot be justified today by a demonstrated concrete need (unlike B3/B4/B5's idempotency requirements, each grounded in an actual replay scenario the WHAT process could point to). The minimum semantic decision required before admission: whether `idempotency_key` should be **governed from day one** (proactive, matching the B3/B4/B5 precedent) or **explicitly deferred** (since no current consumer needs it) — a genuine, open WHAT-phase choice, not resolved here.

---

## 9. RunnerArtifact necessity findings

Testing the five alternatives (§10 of the mandate):

**A. Outputs remain entirely domain-owned.** Rejected on the sharpest evidence in this entire challenge: PGDR has **zero persistence**. If CPL does not provide somewhere for PGDR's output to live, it is lost the instant the CLI process exits — this is not a hypothetical risk, it is PGDR's actual, current, confirmed behavior.

**B. CPL stores only opaque external references.** Insufficient alone for PGDR (there is no external store to reference — PGDR has none). Viable for VIR (which does have its own SQLite store) but would leave PGDR's output with no home at all.

**C. `RunnerArtifact` is common canonical representation.** Confirmed as necessary for PGDR by A's rejection; viable for VIR as a governed reference-plus-mirror.

**D. `RunnerArtifact` is only execution evidence.** Too narrow — PGDR's `GaragePreparationReport` is not mere evidence-of-execution, it is the primary deliverable the whole system exists to produce.

**E. Different artifact classes are required.** **Confirmed necessary** — see §10 below.

```text
RUNNERARTIFACT_COMMON_GOVERNANCE_REQUIRED = YES
```

---

## 10. Artifact classification findings

The Product-Gap investigation's `GAP-C02` finding (no `CaseEventType`-equivalent classification for `artifact_type`) is confirmed and **sharpened with new evidence**: PGDR's own real, current output already splits into two structurally and semantically distinct objects from a **single diagnostic run**:

```text
GaragePreparationReport   — technician-facing: symptom_summary, evidence_index,
                              systems_to_examine, contradictions, limitations
                              (structured diagnostic evidence carrier)

UserSummary                — consumer-facing: urgency, main_observations,
                              next_actions, disclaimer
                              (product display data, not a determination carrier)
```

This means the artifact-classification gap is not merely "one execution → one under-classified artifact" but **"one execution → multiple artifacts of genuinely different semantic class,"** demonstrated by a real system's real output shape, not hypothesized. `RunnerArtifact.execution_id` being a plain (non-unique) FK already structurally permits this 1:N relationship — no schema change is implied, only a governance gap (classification) sharper than previously stated.

```text
PAYLOAD ≠ SEMANTIC CLASS
JSON ≠ ONTOLOGY
ARTIFACT ≠ DOMAIN TRUTH
```
All confirmed to hold; none collapsed by this finding.

---

## 11. VIR artifact test

```text
WORLD / VEHICLE FACT
        ↓ (VIR-owned)
VIR OBSERVATION / INPUT      — VehicleIdentityRequest (registration, VIN, manual)
        ↓ (VIR-owned)
VIR DETERMINATION             — VehicleIdentityResolution (resolution_status,
                                  vehicle_identity, confidence)
        ↓ (VIR-owned)
RUNNER OUTPUT                  — same object, or the purpose-built
                                  DiagnosticIdentityContext handoff DTO
                                  (src/vir/domain/models.py:255)
        ↓ (CPL MAY govern from here)
CPL REPRESENTATION              — a RunnerArtifact wrapping the resolution/handoff
                                  payload, opaque, versioned via schema_name/
                                  schema_version
        ↓ (product-owned)
PRODUCT DISPLAY
```

VIR owns every transition up to and including "runner output." CPL governs only the *container* from that point — never re-derives or re-validates the vehicle identity itself. `DOMAIN DETERMINES DOMAIN TRUTH; CPL GOVERNS COMMON CANONICAL REPRESENTATION` holds cleanly: nothing in `RunnerArtifact`'s schema (`payload` opaque JSONB, `schema_name`/`schema_version` for interpretation) requires CPL to parse or validate VIR's determination.

---

## 12. PGDR artifact test

```text
observation/symptom            — PGDR-owned (complaint_parser, DiagnosticLoop)
evidence                        — PGDR-owned (EvidenceMapper)
diagnostic inference             — PGDR-owned (HypothesisScorer)
candidate cause/conclusion        — PGDR-owned, GGM-governed (PGDR's own separate
                                    epistemic governance — out of CPL scope entirely,
                                    confirmed §6 of the Product-Gap report)
recommendation                    — PGDR-owned (report_builder.py)
execution output                  — GaragePreparationReport + UserSummary (two classes)
stored artifact                    — MISSING today (zero persistence); this is exactly
                                    what a governed RunnerArtifact would provide
product presentation                — UserSummary specifically; a distinct class from
                                    GaragePreparationReport, per §10 above
```

```text
PGDR OUTPUT ≠ RUNNERARTIFACT SEMANTIC AUTHORITY
STORING A DIAGNOSIS ≠ CPL MAKING THE DIAGNOSIS
```
Both hold: a `RunnerArtifact` containing PGDR's `GaragePreparationReport` payload would be exactly analogous to `DomainProjection` (B4) holding `VehicleDetail` data — CPL persists a container, never adjudicates the diagnostic content within it.

---

## 13. Artifact identity/status findings

Testing against the actual schema (`app/cpl/models/runner_artifact.py`):

```text
SAME CONTENT HASH ≠ SAME ARTIFACT       — content_hash is optional (nullable pair
                                           with hash_algorithm), identity is the PK
                                           artifact_id, not the hash. Holds correctly.
SAME PAYLOAD ≠ SAME ARTIFACT             — two artifacts could coincidentally share
                                           payload content without being the same
                                           row; artifact_id remains the identity.
SAME EXECUTION ≠ ONE ARTIFACT            — confirmed necessary by §10's finding
                                           (PGDR's own 1:N evidence).
SUPERSESSION ≠ DELETION                   — supersedes_artifact_id (self-FK) already
                                           exists in schema, exactly mirroring B4/B5's
                                           supersession pattern.
CORRECTION ≠ MUTATION OF HISTORY           — no service layer exists yet to test this
                                           behaviorally, but the schema shape (self-FK
                                           supersession) is structurally consistent
                                           with preserving prior rows, same as
                                           RunnerArtifact already does for itself and
                                           as B5 established for CaseEvent.
```

**Stable artifact identity is necessary for the minimum product** — without it, "which report did the user actually receive" and "was this later corrected" both become unanswerable, and both are concrete product needs (history/follow-up, per the original journey).

---

## 14. Artifact status findings

`artifact_status` (`CREATED/VALIDATED/SUPERSEDED/REJECTED`) tested against the five candidate meanings (§15 of mandate):

- **Persistence state** — partially (`CREATED` maps to "row exists").
- **Validation state** — partially (`VALIDATED`/`REJECTED` suggest a structural check, e.g. "does this payload conform to `schema_name`/`schema_version`").
- **Domain acceptance / canonicality** — explicitly **not** justified by any evidence found; nothing in VIR or PGDR's actual behavior implies CPL should adjudicate whether a diagnostic conclusion is "accepted" as domain-true. Using `VALIDATED` to mean "the runner's diagnosis was correct" would violate `ARTIFACT STATUS → DOMAIN TRUTH` and must be explicitly excluded in the future WHAT.
- **Publication/lifecycle state** — plausible, unconfirmed by current evidence (no product-display gating logic exists anywhere yet).

**Finding:** `artifact_status`'s exact meaning is under-specified relative to the four candidate readings, and the WHAT must pick one explicitly (most likely: structural validation state, never domain acceptance) rather than let implementation default to whichever meaning is convenient.

---

## 15. Provenance/integrity findings

Testing minimum common provenance against actual schema and actual system behavior:

```text
producing RunnerExecution    — already the FK, NOT NULL. Necessary and present.
runner type/version           — already on RunnerExecution (runner_type/runner_version),
                                not duplicated on RunnerArtifact. Sufficient via join.
production time                — created_at exists on both tables.
content hash                    — optional, present when needed (e.g. VIR's
                                immutable resolution payload); PGDR's evolving
                                report content may reasonably omit it.
source/input references          — NOT currently in schema; no field captures
                                "which VIR artifact did this PGDR execution consume."
supersession lineage              — present (supersedes_artifact_id).
domain provenance                  — payload-internal, correctly left to VIR/PGDR's
                                own domain models, not CPL schema.
external references                 — CPL already has ExternalReference (B4);
                                reuse should be considered, not re-invented,
                                in the future WHAT.
```

```text
CONTENT INTEGRITY ≠ SEMANTIC VALIDITY
PROVENANCE ≠ TRUTH
TRACEABILITY ≠ AUTHORITY
```
All hold. **Gap found:** no "source artifact" reference field exists for the VIR→PGDR handoff case specifically (§19 below expands on this).

---

## 16. Execution↔Artifact cohesion analysis

Testing the four alternatives (§17 of the mandate), explicitly **not** inferring cohesion from the FK alone:

- **Semantic dependency:** confirmed independent of the FK — an artifact is meaningless without knowing *which invocation* produced it (this is a semantic fact about what an artifact *is*, not merely a database constraint).
- **Authority dependency:** the same authority context that permitted the execution should reasonably extend to artifacts it produces — tested, no counter-evidence found requiring separate authority.
- **Lifecycle dependency:** `RunnerArtifact` cannot outlive the meaningfulness of its `RunnerExecution` (if the execution itself were ever corrected/retried, its artifacts' status is directly implicated) — genuine coupling, not FK-derived.
- **History dependency:** reconstructing "what happened" for a Case requires both objects together; neither alone answers the historical question completely.
- **Product dependency:** confirmed — every journey step needing either object (§10 of the Product-Gap report) needs both together (an execution without ever producing/attempting an artifact is not a scenario found anywhere in VIR or PGDR's actual behavior).
- **Testability:** governing `RunnerExecution` alone and leaving `RunnerArtifact` ungoverned would repeat exactly the B5-and-`current_execution_id` problem (a governed object with an ungoverned pointer into unversioned territory) — this time *within* the same candidate unit rather than across a Build Unit boundary, which is a stronger argument for cohesion than B5's Case/Execution split had for separation.
- **Ability to freeze one without inventing semantics for the other:** tested directly — attempting to freeze `RunnerExecution` alone would leave `artifact_status`'s domain-acceptance ambiguity (§14) and the 1:N multiplicity (§10) as immediately-adjacent unresolved questions that the same WHAT process would need to revisit almost immediately. No clean freeze boundary was found between them.

```text
FOREIGN KEY DEPENDENCY ≠ BUILD UNIT COHESION
```
Explicitly not the basis for this conclusion — the semantic/lifecycle/product/testability dependencies above are.

**Verdict: Alternative A (`Execution / Artifact Governance` as one unit) — PASS.** Alternatives B/C (sequential split) and D (only one required) are both rejected on the evidence above.

```text
UNIT_COHESION = PASS
```

---

## 17. Case boundary analysis

B5 is CLOSED; tested for any actual contradiction, not merely re-litigated:

```text
CASE ≠ EXECUTION                 — confirmed, no collapse found anywhere in this challenge
CASE STATUS ≠ EXECUTION STATUS    — confirmed; B5's REQ-B5-052 already explicitly
                                    prohibits B5 from interpreting execution status,
                                    and this challenge found no code or design
                                    pressure to violate that from the execution side
CASE EVENT ≠ RUNNER ARTIFACT       — confirmed distinct; a CaseEvent could reference
                                    an execution/artifact (execution_id already exists
                                    on CaseEvent) without becoming one
CASE HISTORY ≠ EXECUTION HISTORY    — confirmed distinct concerns
```

`Case.current_execution_id` and `CaseEvent.execution_id` (both established by B5's REPAIR-01 as opaque, execution-governance-owned references) are exactly the intended attachment point for this candidate unit — not a boundary violation, the designed handoff.

```text
No GOVERNANCE_CONFLICT_FOUND.
```

---

## 18. Asset/Identity boundary analysis

`RunnerExecution.asset_id` (existing FK, NOT NULL) tested against B4's frozen invariant (`DOMAIN DETERMINES PHYSICAL IDENTITY; CPL GOVERNS CANONICAL IDENTITY`): recording that an execution concerns a given, already-resolved `Asset` does not merge, reinterpret, or establish anything about that Asset's identity — it merely references an existing canonical identity, exactly as `Case.asset_id` already does. No new Asset authority is introduced; no B4 boundary is touched.

`RunnerExecution.initiated_by_contact_id` (existing FK, nullable) tested against B3: sufficient as-is. VIR itself has **no Contact concept whatsoever** (confirmed directly, §5 of the Product-Gap report, reconfirmed by direct grep this pass — zero hits for `owner|contact|user_id|driver` in VIR's request/resolution models). This means the *only* place "who initiated this" can be represented is CPL-side, using the Contact CPL already governs. No generalized Actor/Role ontology is required or suggested by any evidence found — the concrete need (attribute an execution to a Contact) is already fully satisfiable by B3.

---

## 19. Failure/correction findings

Testing whether the ten candidate failure/outcome distinctions (§21 of the mandate) can be governed without CPL acquiring domain authority: yes, structurally, by the same pattern B5 already validated for its five failure categories (`AUTHORITY_REJECTION/SEMANTIC_REJECTION/UNRESOLVED/CONFLICT/TECHNICAL_FAILURE`). The distinction that matters most here, newly sharpened by evidence: **"artifact invalid structurally" vs "domain rejected result"** must never collapse — the former is CPL/schema-level (does the payload match `schema_name`/`schema_version`), the latter is entirely outside CPL's authority (was PGDR's diagnosis wrong). No exact vocabulary is frozen here, correctly deferred to WHAT.

**Correction/supersession:** `RunnerExecution` has no existing self-referential correction mechanism beyond `parent_execution_id` (whose meaning remains open, §7). `RunnerArtifact` already has `supersedes_artifact_id`. Testing `CORRECTED DOMAIN RESULT = REWRITTEN EXECUTION HISTORY`: rejected — a corrected PGDR diagnosis should produce a *new*, superseding `RunnerArtifact` (mirroring B5's `CaseEvent` correction pattern exactly), never a rewrite of the original `RunnerExecution` row or the original artifact's payload. `NEW ARTIFACT = NEW EXECUTION` also rejected — nothing in VIR or PGDR's behavior suggests a corrected result requires re-invoking the runner; a human-initiated correction of an already-produced artifact is a distinct operation from a fresh execution.

---

## 20. VIR→PGDR handoff findings

Testing the proposed chain against actual PGDR input-contract evidence (`src/pgdr/models.py:34`: *"Input contract only — the PGDR never reconstructs VIR logic"*): PGDR does **not** consume a `RunnerArtifact` directly, and does not need VIR's full resolution payload. It needs exactly the shape VIR's own `DiagnosticIdentityContext` already defines (`resolution_id`, `identity_status`, `vehicle` dict, `diagnostic_constraints` dict) — a **projection**, not the raw artifact.

```text
Case
 ↓ (CPL, if built)
VIR RunnerExecution + RunnerArtifact   — CPL governs container; VIR determines content
 ↓ (NOT direct artifact-to-artifact — a projection)
[projection matching DiagnosticIdentityContext's shape]  — INTEGRATION LAYER responsibility,
                                                             not CPL, not VIR, not PGDR alone
 ↓
PGDR RunnerExecution + RunnerArtifact  — CPL governs container; PGDR determines content
```

Explicit classification:

```text
CPL:                stores/governs the container on both ends (if the unit is built)
VIR:                 determines and exposes DiagnosticIdentityContext (already built)
PGDR:                 consumes only the projection shape, never raw VIR artifacts
INTEGRATION LAYER:     owns constructing the projection from a VIR artifact/resolution
                       and feeding it to PGDR's input contract — this is genuinely
                       new code that belongs to neither CPL nor VIR nor PGDR as they
                       exist today
PRODUCT LAYER:          owns triggering the whole sequence from a user action
```

No direct artifact-to-artifact dependency was invented or found necessary.

---

## 21. Product sufficiency test

```text
POST_UNIT_CPL_BLOCKER = NONE
```

Every gap discovered in this challenge (`artifact_status` ambiguity, `parent_execution_id` meaning, `idempotency_key` policy, source-artifact provenance field for handoff) is a WHAT-phase or HOW-phase question about *how to govern* `RunnerExecution`/`RunnerArtifact`, not evidence of a *separate*, additional CPL capability still missing. No third object, no generalized Actor/Evidence/State/Organization concept, and no reopening of B1–B5 was found necessary anywhere in this pass.

---

## 22. CPL stopping test

```text
CPL_MINIMUM_FOR_VIR_PGDR_REACHED = YES_AFTER_THIS_UNIT
```

After Execution/Artifact Governance is built (as one unit, per §16), CPL construction should STOP for the current VIR/PGDR product, and construction should move to the demonstrated domain/integration gaps (VIR/PGDR-caller integration, the projection layer identified in §20, status-vocabulary reconciliation) and product gaps (application API, frontend) already catalogued in the Product-Gap report. This does not mean CPL is complete permanently — only that no further *common* capability was found blocking this specific product.

---

## 23. Premature-generalization findings

Searched specifically for drift toward each of the ten listed anti-patterns (§26 of the mandate). None found:

- No evidence anywhere supports a universal job scheduler, workflow engine, or orchestration platform — `RunnerExecution` has no step/task/dependency concept, and nothing in VIR or PGDR's actual behavior requires one (both are single-invocation, non-orchestrated).
- No universal event bus — `CaseEvent` (B5, closed) already covers append-only history; this candidate does not duplicate or extend it into a bus.
- No generic agent framework, generic evidence system, generic state machine, generic artifact repository, knowledge graph, or domain-truth engine — every schema field investigated maps to a concrete, demonstrated need (execution attempt tracking, result container), not a speculative future capability.

**Clean bill on premature generalization.**

---

## 24. Gap register

```text
BS-EA-01
Description: RunnerArtifact is 1:N with RunnerExecution, demonstrated by
  PGDR's real dual-output (GaragePreparationReport + UserSummary), not
  merely hypothesized.
Evidence: src/pgdr/models.py:228,253 (PGDR repo, 0580b1a)
Severity: NON-BLOCKING (schema already supports 1:N via non-unique FK)
Blocking: NO
Affected object: RunnerArtifact
Semantic consequence: artifact_type classification must account for
  multiple co-produced artifact classes per execution, not one.
Required disposition: WHAT must state this explicitly rather than
  assume 1:1.
Phase: WHAT

BS-EA-02
Description: parent_execution_id has real candidate evidence
  (continuation/refinement, from VIR's clarify pattern) but no frozen
  meaning.
Evidence: src/vir/application/clarify_resolution.py,
  src/vir/domain/resolution.py:91 (VIR repo, a342aba)
Severity: NON-BLOCKING
Blocking: NO (field may remain opaque for admission)
Affected object: RunnerExecution
Semantic consequence: none yet — deferred
Required disposition: WHAT must resolve OSQ-02 using this evidence,
  not invent a fresh interpretation
Phase: WHAT

BS-EA-03
Description: idempotency_key has no demonstrated current consumer need
  in either VIR or PGDR.
Evidence: zero grep hits for idempotency/idempotent in either repo
Severity: NON-BLOCKING
Blocking: NO
Affected object: RunnerExecution
Semantic consequence: WHAT must decide proactive-governance vs
  explicit-deferral, not default silently to either.
Phase: WHAT

BS-EA-04
Description: artifact_status's four candidate meanings
  (persistence/validation/domain-acceptance/publication) are not
  distinguished by current schema or evidence; domain-acceptance
  reading must be explicitly excluded.
Evidence: app/cpl/models/runner_artifact.py (CPL repo, 2ac075d)
Severity: NON-BLOCKING but IMPORTANT
Blocking: NO
Affected object: RunnerArtifact
Semantic consequence: risk of ARTIFACT STATUS -> DOMAIN TRUTH collapse
  if left unaddressed at WHAT time
Phase: WHAT

BS-EA-05
Description: no schema field captures "which artifact/resolution fed
  this execution" for the VIR->PGDR handoff case specifically (source
  reference provenance).
Evidence: app/cpl/models/runner_artifact.py — no such field exists
Severity: NON-BLOCKING
Blocking: NO
Affected object: RunnerArtifact (or RunnerExecution)
Semantic consequence: handoff traceability would be incomplete without
  it, but the field's exact shape is a HOW decision
Phase: REQUIREMENTS / HOW

BS-EA-06
Description: no direct VIR->PGDR artifact dependency exists or should
  exist; a projection-construction responsibility belongs to an
  integration layer that does not yet exist anywhere.
Evidence: src/pgdr/models.py:34 (PGDR-ID-001), DiagnosticIdentityContext
  shape (VIR, src/vir/domain/models.py:255)
Severity: NON-BLOCKING for CPL; BLOCKING for product automation
Blocking: NO (for CPL Structuring); YES (for the actual product,
  but outside CPL's authority)
Affected object: none in CPL
Semantic consequence: none for CPL's WHAT
Phase: DOMAIN INTEGRATION
```

No `BS-EA` finding was classified as STRUCTURING-blocking.

---

## 25. Final verdict

```text
PRIMARY VERDICT: BUILD_STRUCTURE_ACCEPTED
```

The hypothesis survives falsification attempts across all seven tested dimensions (necessity, commonality, cohesion, semantic sufficiency, dependency correctness, product relevance, premature-generalization absence). Six non-blocking findings (`BS-EA-01`–`06`) sharpen it with new, concretely-grounded evidence beyond what the Product-Gap investigation found — none reject it, none require reopening B1–B5, none require rejecting the unit or splitting it.

---

## 26. Recommended next governance action

```text
NEXT BUILD UNIT STRUCTURE = ACCEPTED FOR PRE-ADMISSION WHAT

Define a pre-admission WHAT — CPL_EA_WHAT_v0 — for Execution/Artifact
Governance, explicitly required to address BS-EA-01 through BS-EA-05
as named open questions (not silently resolved), carrying forward the
concrete evidence this challenge found (VIR's continuation pattern for
parent_execution_id; PGDR's dual-output for artifact multiplicity;
zero current idempotency need in either system) rather than starting
from the schema alone.
```

This is a recommendation only; not executed by this challenge.

---

## FINAL SUMMARY

```text
CPL_EXECUTION_ARTIFACT_BUILD_STRUCTURE_CHALLENGE_v0
===================================================

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

GOVERNANCE BASELINE:
  6bacabf2d4ac6fca0630c7e7b883840cabda6eca

VIR BASELINE:
  a342aba7cc2fc517621f4fc79c3191bdfdc9e10b

PGDR BASELINE:
  0580b1a5ba5867a607a33197372fcaf4164f0fb6

EG-01:
  CONFIRMED_WITH_REPAIR

RUNNEREXECUTION COMMON GOVERNANCE:
  YES

RUNNERARTIFACT COMMON GOVERNANCE:
  YES

UNIT COHESION:
  PASS

BLOCKING STRUCTURING GAPS:
  0

WHAT-PHASE GAPS:
  5 (BS-EA-01, 02, 03, 04, 05)

DOMAIN-INTEGRATION-PHASE GAPS:
  1 (BS-EA-06)

POST-UNIT CPL BLOCKER:
  NONE

CPL_MINIMUM_FOR_VIR_PGDR_REACHED:
  YES_AFTER_THIS_UNIT

PRIMARY VERDICT:
  BUILD_STRUCTURE_ACCEPTED

NEXT GOVERNANCE ACTION:
  Define pre-admission WHAT (CPL_EA_WHAT_v0) for Execution/Artifact
  Governance, carrying forward BS-EA-01..05 as named open questions

BUILD UNIT:
  NOT ADMITTED

B6:
  NOT ASSIGNED

IMPLEMENTATION:
  NOT AUTHORIZED
```

**STOP.** No pre-admission WHAT, B6 assignment, requirements, schema modification, migration, code modification (CPL/VIR/PGDR), or candidate branch was produced by this challenge.

# CPL_EA_WHAT_CHALLENGE_v0

## 1. Executive verdict

```text
PRIMARY VERDICT: WHAT_REPAIR_REQUIRED
```

`CPL_EA_WHAT_v0`'s core ontology survives adversarial testing — `RunnerExecution`/`RunnerArtifact` remain coherent, distinct, non-domain-leaking concepts, unit cohesion holds, no B5/B4/B3 conflict was found. But this challenge found **one significant implementation/WHAT divergence** and **four smaller but genuine gaps**, all repairable without rejecting the candidate. Most notably: the WHAT treats `idempotency_key`'s semantics as fully open (`BS-EA-03`), but a real, executable database constraint — a partial unique index scoped by `(runner_type, idempotency_key)` — already exists in the B2 migration and was never checked against the WHAT's claim. This is exactly the kind of divergence this challenge was instructed to hunt for, and it was found by inspecting the raw migration, not the ORM model alone (the model doesn't declare it).

---

## 2. Evidence baselines

```text
Governance baseline:        3a775a5f2b589dd7e526733bcff3c65edf84f4b9
CPL software baseline:       2ac075daea7d162825ed73ded0c7548011242a8f
Build Structure Challenge:    0f79e1df07fa1761488857e06c96cb01a78ed763
Pre-admission WHAT:            3a775a5f2b589dd7e526733bcff3c65edf84f4b9
```

VIR/PGDR were re-consulted only where genuinely needed (§22, §23 below); no modification made to either.

---

## 3. Challenge methodology

Direct re-inspection of: the committed `CPL_EA_WHAT_v0.md` text; the raw Alembic migrations `011`/`012` (not just the SQLAlchemy models, which do not declare index-level constraints); the seven primary falsification questions (§3 of the mandate); all 17 invariants individually; all six inherited `BS-EA` findings; all three new `EA-WG` questions.

---

## 4. RunnerExecution identity/lifecycle challenge

**Identity criterion — genuine gap found.** The WHAT (§6) defines what `RunnerExecution` *represents* but never states what makes two rows the *same* vs. *different* execution. The trivial answer (`execution_id`, the existing PK) is never written down. This matters because §18's "continuation" evidence (VIR's clarify pattern) could be misread by a future Requirements author as implying a continuation is *the same logical execution continuing*, when the correct reading — consistent with VIR's own behavior of minting a wholly new `resolution_id` — is that a continuation is a **different** `RunnerExecution`, related only via the opaque parent pointer. Left unstated, this ambiguity is exactly what `EA-CI01`/`07`/`17` need a stated identity criterion to anchor. **Finding: `EA-WC-03` (see gap register).**

**Lifecycle distinctions** (`CREATED≠STARTED≠COMPLETED≠ARTIFACT PRODUCED≠DOMAIN RESULT VALID`) — tested against the actual schema's `execution_status` enum and `CheckConstraint`s: all four hold cleanly and are independently enforceable (the `completed_at IS NOT NULL` check already structurally separates "reached COMPLETED" from any artifact or domain claim). **No repair needed here.**

---

## 5. Request/authorization/execution challenge

Tested whether the WHAT's `REQUEST ≠ AUTHORIZATION ≠ EXECUTION` boundary is usable or merely stated. A request can exist without execution (rejected before materialization); authorization can exist without execution (approved but not yet acted on); execution can exist after prior rejection was corrected. CPL does not model authorization as a persisted object anywhere in this candidate — consistent with B3/B4/B5's own precedent (`AuthorityContext` is a checker, never a stored row). **This is `VALID MINIMALITY`, not a missing blocking primitive** — no evidence anywhere in VIR, PGDR, or the existing B3–B5 pattern suggests authorization needs its own persisted representation.

---

## 6. Execution status challenge

```text
EXECUTION_STATUS_SEMANTIC_CORE = STABLE
```

The existing `execution_status` enum (`CREATED/QUEUED/RUNNING/COMPLETED/FAILED/BLOCKED/CANCELLED`) is domain-neutral by direct inspection — no value references vehicles, diagnoses, or any domain concept. This is the same clean-by-construction result the original Product-Gap investigation found for `Case.case_status`. Common lifecycle semantics across VIR, PGDR, and a hypothetical future runner (§28 below) hold without becoming a generic job engine, because the enum only describes the *fact of invocation progress*, never task decomposition, scheduling, or dependency ordering.

---

## 7. RunnerArtifact identity challenge

Tested against actual schema: `artifact_id` (PK) is identity; `content_hash` is optional integrity evidence (nullable pair with `hash_algorithm`); `supersedes_artifact_id` is a self-FK. Content change without a new `artifact_id` would violate `EA-CI06`'s own stated principle (identity is not derived from content) — but nothing in the schema *prevents* an implementation from mutating payload in place under the same `artifact_id`, since no immutability constraint exists at the DB level. This is a **soft gap**: the WHAT states the principle (`CORRECTION ≠ MUTATION OF HISTORY`) but the underlying schema has no structural enforcement of it — enforcement would have to come entirely from service-layer discipline (matching exactly how B5 enforces `CaseEvent` append-only-ness purely in code, not via a DB trigger). Not a rejection — this is consistent with established CPL precedent — but worth naming explicitly rather than leaving implicit. Folded into `EA-WC-05` below.

---

## 8. Artifact classification challenge

**Major finding, as anticipated by the mandate's own §9–10.** Testing the WHAT's illustrative candidate class list (`execution output, execution evidence, domain assertion carrier, domain determination carrier, technical artifact, intermediate artifact, final artifact, product-display artifact`) for orthogonality:

```text
"technical artifact"              — CONTENT FUNCTION dimension
"intermediate" / "final"            — LIFECYCLE POSITION dimension
"domain assertion/determination carrier" — SEMANTIC FUNCTION dimension
"product-display artifact"            — PRESENTATION ROLE dimension
"execution output" / "execution evidence" — PRODUCTION ROLE dimension (loosely)
```

These are **not mutually exclusive, not hierarchical, not composable as stated** — a single real artifact (e.g. PGDR's `GaragePreparationReport`) is simultaneously "final" (lifecycle), "domain assertion carrier" (semantic function), and arguably "technical" in the loose sense of being structured evidence. The WHAT's own §11 marks this list "illustrative only," which avoids freezing a broken taxonomy, but does **not** flag that the list itself already exhibits the dimension-mixing problem the mandate specifically asked this challenge to check for. This is a genuine, actionable gap, not merely a stylistic one — a Requirements author reading §11 as-is could reasonably attempt to build one flat enum from this list and immediately hit the mixing problem.

```text
ARTIFACT_CLASSIFICATION_MODEL = REPAIR_REQUIRED
```

**Finding: `EA-WC-02` (see gap register).**

---

## 9. Artifact/assertion/evidence distinctions

`ARTIFACT ≠ ASSERTION` — confirmed usable: an artifact (e.g. `GaragePreparationReport`) demonstrably contains multiple diagnostic claims (`symptom_summary`, `contradictions`, `unresolved_questions` — all list-typed in PGDR's actual model), directly confirming "one artifact, many assertions" is real, not hypothetical. No evidence found of the reverse (one assertion spread across multiple artifacts) in either VIR or PGDR's current behavior.

`ARTIFACT ≠ EVIDENCE` — tested against generalized-Evidence temptation: no evidence found in VIR or PGDR justifying a generalized Evidence ontology. PGDR has its own domain-internal `Evidence` concept (`src/pgdr/domain/evidence.py`) that never needs to leave PGDR's boundary — it's fully absorbed before anything reaches `RunnerArtifact`. Correctly excluded, consistent with the Build Structure Challenge's own premature-generalization finding.

---

## 10. BS-EA-01 challenge (1:N multiplicity)

Re-tested the five scenarios (execution fails before artifact; produces logs+result; produces intermediate+final; produces referenced external artifact; produces no persistent output):

```text
BS-EA-01 = RESOLVED
```

**Exact conceptual multiplicity: 0:N** (not 1:N as the WHAT's §11 heading implies without stating the zero case explicitly). The WHAT's substantive treatment (§11, §24) already correctly avoids assuming 1:1; this challenge confirms the conceptual multiplicity is sound, modulo naming the zero case explicitly — folded into the classification repair, not a separate blocking finding.

---

## 11. BS-EA-02 challenge (parent_execution_id)

**Genuine tension found between two sections of the same document.** §16 of the WHAT requires history to "distinguish execution attempts where conceptually distinct." This presupposes a criterion for what makes two `RunnerExecution` rows "attempts of the same thing" — precisely the question §18 explicitly declines to answer (`parent_execution_id` left opaque). Testing the mandate's own decisive question: *would Requirements touching execution history necessarily assign semantics to this field?* **Yes** — a testable history requirement like "the system must reconstruct which prior attempt a given execution continues" cannot be written without first deciding what "continues" means, which is exactly `parent_execution_id`'s undetermined meaning.

```text
BS-EA-02 = REPAIR_REQUIRED
```

(Downgraded from the WHAT's own `RESOLVED_OUT_OF_SCOPE`-equivalent framing.) **Finding: `EA-WC-04` (see gap register).**

---

## 12. BS-EA-03 challenge (idempotency_key)

**The most significant finding in this challenge.** Direct inspection of `migrations/versions/011_create_runner_executions.py` (not the SQLAlchemy model, which omits this) reveals:

```sql
CREATE UNIQUE INDEX runner_executions_idempotency_uq
  ON cpl.runner_executions (runner_type, idempotency_key)
  WHERE idempotency_key IS NOT NULL;
```

This is **real, executable, already-enforced database behavior** that directly answers several of the mandate's own §15 questions: the key is scoped **per `runner_type`** (not per Case, not globally, not per-request); duplicate `(runner_type, idempotency_key)` pairs are already rejected by Postgres itself, not merely a future intention. The WHAT's §17 states idempotency's "necessity and exact semantics... remain unproven" and explicitly declines to freeze the column's necessity "merely because it exists" — but this is not a case of a column merely existing; it is a case of a **constraint already being enforced**, which is a materially stronger executable commitment than a bare nullable column.

```text
IMPLEMENTATION / WHAT DIVERGENCE FOUND
BS-EA-03 = REPAIR_REQUIRED (reclassified from OPEN)
```

**Finding: `EA-WC-01` (see gap register), CONFLICT with `EA-CI16`'s general framing as applied to this specific field.**

---

## 13. BS-EA-04 challenge (artifact_status)

Re-checked `artifact_status`'s actual CHECK constraint (`CREATED/VALIDATED/SUPERSEDED/REJECTED`) against the WHAT's prohibition (`ARTIFACT STATUS ≠ DOMAIN VALIDITY`). None of the four values is literally domain-truth-laden (no `DIAGNOSIS_CORRECT`, no `IDENTITY_CONFIRMED`), but `VALIDATED` remains genuinely ambiguous exactly as the WHAT itself already flagged — the schema is silent on which of the WHAT's candidate readings (structural validation vs. domain acceptance) `VALIDATED` was originally intended to mean.

```text
BS-EA-04 = CORRECTLY_DEFERRED
```

No divergence found here — the WHAT's own acknowledged uncertainty matches the schema's actual ambiguity; this is honest deferral, not evasion. **No repair required for this one.**

---

## 14. BS-EA-05 challenge (handoff provenance)

Re-tested against actual VIR/PGDR interfaces (`DiagnosticIdentityContext`, PGDR's `PGDR-ID-001` input-contract-only design). Confirmed: PGDR needs a **projection**, not a whole VIR artifact, not a raw execution reference, not selected VIR fields pulled ad hoc. This is `INPUT PROVENANCE ≠ ARTIFACT DEPENDENCY` and `DATA DEPENDENCY ≠ EXECUTION PARENTAGE`, both holding cleanly. Provenance for this specific handoff belongs to the **integration layer**, not CPL, not VIR, not PGDR alone — matching the WHAT's own §14 disposition exactly. **No repair required.**

---

## 15. BS-EA-06 challenge

Retrieved verbatim from the Build Structure Challenge (confirmed matching, not paraphrased) and confirmed faithfully carried forward in the WHAT's §14/§26 without alteration.

```text
BS-EA-06 = CORRECTLY_DEFERRED
```

---

## 16. New WHAT gap challenge

```text
EA-WG-01 (classification mechanism: registry vs. attribute)
  Challenged: does this genuinely not require inventing semantics?
  Given §8's finding (dimension-mixing), this question is now
  entangled with EA-WC-02 — the mechanism question cannot be
  meaningfully answered until the dimension question is repaired.
  Reclassified: NON_BLOCKING for admission, but its resolution now
  depends on EA-WC-02's repair, not independent.

EA-WG-02 (one decision object vs. separate)
  Challenged: genuinely a HOW question, no semantic policy required
  to leave open. NON_BLOCKING, unchanged.

EA-WG-03 (does ExternalReference cover artifact provenance)
  Challenged: genuinely a Requirements-phase investigation question,
  not semantic policy. NON_BLOCKING, unchanged.
```

---

## 17. Execution↔Artifact cohesion re-challenge

Re-tested from scratch, not merely re-confirmed: can `RunnerExecution` be frozen independently? Testing against the newly-found idempotency constraint (§12) — the unique index is on `RunnerExecution` alone, entirely independent of `RunnerArtifact`'s existence, which if anything *strengthens* the case that `RunnerExecution` has its own independently coherent identity/constraint surface. Can `RunnerArtifact` exist without `RunnerExecution`? No — `execution_id` remains `NOT NULL`, unchanged. Does provenance require both in one unit? Yes, confirmed again — an artifact's provenance is meaningless without its producing execution.

```text
UNIT_COHESION = PASS
```

Unchanged from the Build Structure Challenge's verdict; no new evidence found to overturn it.

---

## 18. Provenance and lineage challenge

Tested the six candidate relations (`PRODUCED BY, DERIVED FROM, USED AS INPUT, REFERENCES, SUPERSEDES, COPIED FROM`) against the WHAT's actual text: the WHAT's §15 only names "producing RunnerExecution" and "supersession lineage" explicitly — it does not distinguish `DERIVED FROM` from `USED AS INPUT` from `REFERENCES`, all three of which are plausible readings of the still-open `BS-EA-05` handoff-provenance question. This is not a new blocking finding — it is the same gap already captured as `BS-EA-05`/`EA-WG-03`, not a fresh one requiring separate registration.

**Execution lineage:** re-tested whether any lineage relation (`retry-of, continuation-of, delegated-from, spawned-by, depends-on, corrects, replays`) is actually *required* for the minimum VIR/PGDR product. Finding: **no** — nothing in VIR or PGDR's current behavior requires CPL to represent execution lineage as a first-class relation; VIR's own continuation pattern is fully internal to VIR (a new `resolution_id`, no cross-system lineage claim). Confirms the WHAT's own restraint in §24 (declining to introduce `ExecutionLineage` as a named ontology concept). **Correct, no repair.**

---

## 19. Correction/supersession challenge

```text
HISTORICAL EXECUTION FACT MUST NOT BE REWRITTEN AS IF A DIFFERENT EXECUTION OCCURRED
```
holds as a principle. But tested against actual schema support: `RunnerArtifact` has `supersedes_artifact_id`; `RunnerExecution` has **no equivalent field at all**. `EA-CI12` asserts correction applies to "execution or artifact representation" as if both were symmetric, but only one has structural backing. This is not fatal — B5's own `CaseEvent` correction also relies on service-layer discipline rather than a dedicated schema field for the *decision* trail (the decision ledger pattern) — but the WHAT should say this explicitly rather than let the asymmetry pass silently.

**Finding: `EA-WC-05` (see gap register).**

---

## 20. Canonical decision challenge

Re-tested each of the five candidate transitions against the mandate's own question (would absence of canonical decision objects make authority/history unverifiable?):

```text
Execution registration           — YES, canonical decision needed (material creation)
Execution lifecycle transition     — YES, needed (mirrors B5's STATUS_TRANSITION)
Artifact registration                — LIKELY, but arguably lighter — an artifact's
                                      "decision" could be subsumed into the producing
                                      execution's own decision trail rather than a
                                      separate object (genuinely undetermined, correctly
                                      left open by the WHAT)
Artifact correction/supersession       — YES, needed (mirrors B5's EVENT_CORRECTION)
```

```text
CANONICAL_DECISION_MODEL = PARTIALLY_REQUIRED
```

This matches the WHAT's own §25 "likely" framing — re-tested and confirmed reasonable, not rejected. The WHAT correctly avoids copying B4/B5's exact decision-object shape mechanically.

---

## 21. Authority challenge

Testing all eleven authority questions from §27 of the mandate against the WHAT's actual boundary statements: no mixed authority found. `REPORTER ≠ AUTHORITY` (a runner reporting `COMPLETED` never grants itself CPL authority), `PRODUCER ≠ CANONICAL GOVERNANCE AUTHORITY` (VIR/PGDR producing an artifact never makes either the CPL governance authority over its own container), `CPL AUTHORITY OVER REPRESENTATION ≠ CPL AUTHORITY OVER DOMAIN MEANING` — all three hold cleanly across every tested dimension (execution existence/identity/lifecycle, artifact existence/identity/classification/integrity, correction of CPL representation vs. domain meaning/validity). **No repair required.**

---

## 22. VIR leakage test

Re-inspected VIR's actual domain vocabulary (VIN validity, registration identity, physical sameness, confidence, identity resolution, source hierarchy) against the WHAT's text: none of these concepts appears anywhere in `CPL_EA_WHAT_v0.md`. The WHAT never requires CPL to understand what makes a VIN valid or two vehicles physically the same — all such semantics remain entirely on VIR's side of the `RunnerArtifact` boundary. **Clean. No leakage found.**

---

## 23. PGDR leakage test

Same test against PGDR's vocabulary (symptoms, faults, causes, diagnostic confidence, repair recommendation, repair success, machine/diagnostic state): none appears in the WHAT. `execution_status` (CPL-side) is never conflated with PGDR's own `SessionState`/`DiagnosticCaseState` (PGDR-side) anywhere in the document. **Clean. No leakage found.**

---

## 24. VIR→PGDR handoff re-challenge

Re-verified against actual code (`src/vir/api/routes.py`'s `handoff/diagnostic` endpoint, `src/pgdr/models.py`'s `VehicleIdentityContext`) that the current real mechanism is: VIR exposes a purpose-built HTTP response object; PGDR accepts a manually-constructed CLI-flag equivalent of that same shape. Neither a file, nor a database object, nor a `Case`, nor an `Asset` currently carries this handoff — it is presently **human-mediated**. The WHAT correctly does not pretend this human-mediated mechanism is the permanent ontology — §14 explicitly defers the projection-construction responsibility to a not-yet-existing integration layer. **No repair required; the WHAT's honesty about current-vs-future mechanism holds.**

---

## 25. Case/B2 compatibility analysis

```text
Case.current_execution_id       — ALIGNED WITH WHAT (opaque per B5 REPAIR-01,
                                    consumed not redefined)
CaseEvent.execution_id           — ALIGNED WITH WHAT
RunnerExecution.case_id          — ALIGNED WITH WHAT (§20 of WHAT)
RunnerExecution.asset_id          — ALIGNED WITH WHAT (§21)
RunnerExecution.initiated_by_contact_id — ALIGNED WITH WHAT (§22)
RunnerExecution.runner_type/version — ALIGNED WITH WHAT (§6, no domain content)
RunnerExecution.execution_status  — ALIGNED WITH WHAT (§8)
RunnerExecution.parent_execution_id — UNDER-GOVERNED BUT COMPATIBLE, tension
                                    noted (EA-WC-04)
RunnerExecution.idempotency_key    — SEMANTICALLY AMBIGUOUS relative to the WHAT's
                                    own framing; CONFLICTS with WHAT's "open"
                                    characterization given the enforced unique
                                    index (EA-WC-01)
RunnerArtifact.execution_id         — ALIGNED WITH WHAT
RunnerArtifact.artifact_type          — SEMANTICALLY AMBIGUOUS (EA-WC-02)
RunnerArtifact.artifact_status         — SEMANTICALLY AMBIGUOUS, but CORRECTLY
                                    flagged as such by the WHAT itself (§13)
RunnerArtifact.content_hash/hash_algorithm — ALIGNED WITH WHAT
RunnerArtifact.supersedes_artifact_id       — ALIGNED WITH WHAT
```

No field found to `CONFLICT WITH WHAT` outright (in the sense of making the WHAT unimplementable) — the two flagged ambiguities (`idempotency_key`, `artifact_type`) require the WHAT text itself to change, not the schema.

---

## 26. EA-CI01→EA-CI17 individual challenge table

| # | Restated | Prevents | Tested against | Contradicts another EA-CI? | Contradicts B3/4/5? | Verdict |
|---|---|---|---|---|---|---|
| 01 | Execution ≠ Request | rejected requests masquerading as governed records | schema (no request object exists) | No | No | PASS |
| 02 | Execution ≠ Domain Result | execution row carrying domain conclusions | RunnerExecution schema (no domain field) | Overlaps 13/14/15 | No | PASS (redundant cluster, non-blocking) |
| 03 | Execution Status ≠ Domain Result Status | status misuse as domain verdict | execution_status enum (domain-neutral) | No | Mirrors B5 pattern | PASS |
| 04 | Artifact ≠ Domain Truth | artifact existence read as CPL endorsement | RunnerArtifact schema | Overlaps 13/15 | No | PASS (redundant cluster, non-blocking) |
| 05 | Payload ≠ Semantic Class | format mistaken for meaning | artifact_type ambiguity (§8) | No | No | INSUFFICIENT — states the negative but doesn't prevent the found dimension-mixing (EA-WC-02) |
| 06 | Content Hash ≠ Artifact Identity | hash-based identity confusion | content_hash nullable pair | No | No | PASS |
| 07 | Same Execution ≠ One Artifact | 1:1 assumption | PGDR dual-output evidence | No | No | PASS |
| 08 | Case ≠ Execution | conflating matter with attempt | Case/RunnerExecution schema | No | Consistent with B5 | PASS |
| 09 | CaseEvent ≠ RunnerArtifact | history-vs-artifact confusion | CaseEvent/RunnerArtifact schema | No | Consistent with B5 | PASS |
| 10 | Initiator ≠ Authority | attribution mistaken for permission | initiated_by_contact_id nullable | No | Mirrors B5 pattern | PASS |
| 11 | Provenance ≠ Validity | traceability mistaken for correctness | §15 of WHAT | No | No | PASS |
| 12 | Correction ≠ History Deletion | destructive rewrite | RunnerExecution has NO correction substrate (§19) | No | Mirrors B4/B5 | INSUFFICIENT — asymmetry with RunnerArtifact unacknowledged (EA-WC-05) |
| 13 | CPL Representation ≠ Domain Determination | CPL claiming authorship of stored content | §12/13 of WHAT | Overlaps 02/04/15 | No | PASS (redundant cluster) |
| 14 | Runner Completed ≠ Diagnosis True | status-as-truth (PGDR example) | narrower restatement of 03 | Redundant with 03 | No | REDUNDANT |
| 15 | Storage ≠ CPL domain authority | storing = adjudicating | §12/13 of WHAT | Overlaps 02/04/13 | No | PASS (redundant cluster) |
| 16 | Schema field presence ≠ semantic governance required | column-existence-as-mandate | idempotency_key (§12) | No | No | CONFLICT as applied — the general principle survives, but its specific application to idempotency_key is contradicted by the enforced unique index (EA-WC-01) |
| 17 | Parent pointer existence ≠ parent semantics known | premature parent_execution_id interpretation | §11 above (history/parent tension) | No | No | INSUFFICIENT alone — needs §16/§18 tension resolved to be practically usable (EA-WC-04) |

**Summary: 10 PASS, 2 REDUNDANT (non-blocking), 3 INSUFFICIENT, 1 CONFLICT-as-applied, 0 outright FAIL.**

---

## 27. Missing invariant analysis

One genuinely missing invariant identified: nothing in the current 17 explicitly states **execution identity stability** (mirroring `EA-WC-03`) — e.g. "a RunnerExecution's execution_id never changes meaning to represent a different attempt." Recommended as a repair-time addition, not registered as a separate blocking gap since it folds into `EA-WC-03`'s repair.

No other missing invariant found among the candidates the mandate suggested (0:N multiplicity is covered by `EA-CI07`; producer-vs-authority by `EA-CI10`; historical immutability by `EA-CI12`, albeit insufficiently as noted).

---

## 28. Premature/under-generalization analysis

**Premature generalization:** re-swept the WHAT text for the ten listed anti-patterns — none found, consistent with the Build Structure Challenge's own clean result. No new drift introduced between the Challenge and the WHAT.

**Under-generalization:** tested against one abstract plausible runner (document transformation — e.g. a hypothetical "DOCX-to-structured-data" runner). Core semantics hold without modification: `runner_type = "DOC_TRANSFORM"`, execution status lifecycle identical, artifact classification need (structured output vs. technical log) identical in kind to VIR/PGDR's own split. No VIR/PGDR-specific vocabulary was found baked into the WHAT's conceptual definitions (§6, §10) — the domain-specific detail lives entirely in the *examples* (§12, §13), never in the definitions themselves. **Model remains appropriately general, not overfit to VIR/PGDR.**

---

## 29. Requirements-readiness verdict

```text
REQUIREMENTS_READINESS = REPAIR_REQUIRED
```

Per the decisive test: could a separate team write a complete requirement matrix without inventing answers? For identity (artifact side), authority, cardinality, provenance, correction (artifact side), canonical decision — **yes**, largely ready. For **execution identity stability** (never explicitly stated), **idempotency scope** (WHAT's framing contradicted by existing enforced constraint), **artifact classification dimensionality** (mixed, unacknowledged), and **execution-side correction** (asymmetric with artifact-side, unacknowledged) — **no**, a Requirements author would have to invent policy in each of these four places today. This is precisely the strict standard requested: if requirements-writing would force silent invention anywhere, the WHAT is not yet ready, regardless of how much of it *is* solid.

---

## 30. CPL stopping-condition verdict

```text
POST_EA_COMMON_BLOCKER = NONE
```

None of this challenge's five findings (`EA-WC-01`–`05`) constitutes a *missing capability* — all five are refinements/repairs to the *existing* candidate's own text, not evidence of an additional, separate CPL blocker. The stopping condition itself is not challenged by this pass.

```text
CPL_MINIMUM_FOR_VIR_PGDR_REACHED = CONDITIONAL
```

(Downgraded from `YES_AFTER_THIS_UNIT` to `CONDITIONAL` only because the *unit itself* is not yet repair-complete — once `EA-WC-01`–`05` are addressed in a `v0.1`, the original `YES_AFTER_THIS_UNIT` framing is expected to hold again, pending re-challenge.)

---

## 31. Challenge gap register

```text
EA-WC-01
Description: idempotency_key already has an enforced partial unique
  index scoped by (runner_type, idempotency_key), contradicting the
  WHAT's "necessity/semantics remain unproven" framing.
Evidence: migrations/versions/011_create_runner_executions.py,
  runner_executions_idempotency_uq
Severity: SIGNIFICANT
Blocking: YES (for Requirements-readiness)
Affected concept: RunnerExecution idempotency
Affected invariant(s): EA-CI16 (as applied to this field)
Required repair: WHAT must acknowledge the existing constraint and
  take an explicit position (accept the scope, or flag it as a
  repair candidate for schema itself)
Repair phase: WHAT

EA-WC-02
Description: illustrative artifact-classification candidate list
  mixes at least four independent taxonomic dimensions without
  acknowledging it.
Evidence: CPL_EA_WHAT_v0.md §11; PGDR's GaragePreparationReport
  exhibiting multiple dimensions simultaneously
Severity: SIGNIFICANT
Blocking: YES
Affected concept: RunnerArtifact semantic classification
Affected invariant(s): EA-CI05 (insufficient alone)
Required repair: explicitly flag dimension-mixing risk in the
  candidate list, or restrict it to one dimension
Repair phase: WHAT

EA-WC-03
Description: no explicit RunnerExecution identity criterion stated.
Evidence: CPL_EA_WHAT_v0.md §6 (definition present, identity absent)
Severity: MODERATE
Blocking: YES (small fix, but Requirements-blocking as stated)
Affected concept: RunnerExecution
Affected invariant(s): supports EA-CI01/07/17; none directly states it
Required repair: state execution_id as identity; clarify continuation
  produces a distinct execution, not the same one
Repair phase: WHAT

EA-WC-04
Description: §16 (history reconstructability) presupposes
  "distinct execution attempts" are identifiable, which depends on
  parent_execution_id's meaning — explicitly left undetermined by
  §18. Internal tension between two sections.
Evidence: CPL_EA_WHAT_v0.md §16 vs §18
Severity: MODERATE
Blocking: YES
Affected concept: RunnerExecution history; parent_execution_id
Affected invariant(s): EA-CI17 (insufficient alone)
Required repair: narrow §16's language, or explicitly acknowledge
  the dependency and defer both together
Repair phase: WHAT

EA-WC-05
Description: EA-CI12 asserts correction≠deletion applies symmetrically
  to execution and artifact representation, but only RunnerArtifact
  has existing schema-level correction substrate
  (supersedes_artifact_id); RunnerExecution has none.
Evidence: app/cpl/models/runner_execution.py vs runner_artifact.py
Severity: MODERATE
Blocking: NO (Requirements/HOW may resolve without new WHAT policy,
  provided the asymmetry is named)
Affected concept: RunnerExecution correction
Affected invariant(s): EA-CI12 (insufficient alone)
Required repair: name the asymmetry explicitly; do not imply
  execution-side correction is structurally solved
Repair phase: WHAT (naming only) / HOW (mechanism)
```

Four of five findings are blocking for Requirements-readiness specifically (not for the ontology's survival); one is non-blocking but should still be named.

---

## 32. Required repairs

```text
R-EA-W01
Target section: §17 (idempotency_key)
Problem: EA-WC-01 — WHAT's "open" framing contradicted by existing
  enforced unique index.
Required semantic change: state explicitly that (runner_type,
  idempotency_key) uniqueness is already an executable constraint;
  take a position on whether this scope is accepted as the frozen
  minimum or flagged as a schema-repair candidate.
Affected invariant(s): EA-CI16
Acceptance test: v0.1's §17 cites runner_executions_idempotency_uq
  by name and states a position on it.

R-EA-W02
Target section: §11 (artifact classification)
Problem: EA-WC-02 — dimension-mixing in the illustrative list.
Required semantic change: explicitly flag the multi-dimensionality
  risk, or restrict the illustrative list to a single dimension.
Affected invariant(s): EA-CI05
Acceptance test: v0.1's §11 either names the dimensions separately
  or explicitly disclaims the list as multi-dimensional and
  provisional.

R-EA-W03
Target section: §6 (RunnerExecution definition)
Problem: EA-WC-03 — no stated identity criterion.
Required semantic change: add explicit identity statement
  (execution_id is identity; continuation produces a distinct
  execution).
Affected invariant(s): supports EA-CI01/07/17
Acceptance test: v0.1's §6 contains an explicit "what makes two rows
  the same/different execution" statement.

R-EA-W04
Target section: §16 vs §18
Problem: EA-WC-04 — internal tension between history-reconstruction
  requirement and parent_execution_id opacity.
Required semantic change: narrow §16 or explicitly acknowledge and
  defer the dependency alongside §18.
Affected invariant(s): EA-CI17
Acceptance test: v0.1 resolves or explicitly names this tension
  rather than leaving it implicit.

R-EA-W05
Target section: §16 (correction), re: EA-CI12
Problem: EA-WC-05 — unacknowledged asymmetry between RunnerExecution
  (no correction substrate) and RunnerArtifact (has one).
Required semantic change: name the asymmetry explicitly; do not
  imply execution-side correction is already structurally supported.
Affected invariant(s): EA-CI12
Acceptance test: v0.1 explicitly states execution-side correction
  mechanism is an open Requirements/HOW question.
```

The next artifact is `CPL_EA_WHAT_v0.1.md`, not produced here.

---

## 33. Final verdict

```text
PRIMARY VERDICT: WHAT_REPAIR_REQUIRED
```

---

## 34. Recommended next governance action

```text
Produce CPL_EA_WHAT_v0.1.md, incorporating R-EA-W01 through R-EA-W05
as bounded repairs, preserving all unaffected sections and all
invariants not named above unchanged, followed by a targeted
re-challenge (not a full re-challenge) verifying only the five
repairs.
```

---

## FINAL SUMMARY

```text
CPL_EA_WHAT_CHALLENGE_v0
========================

GOVERNANCE BASELINE:
  3a775a5f2b589dd7e526733bcff3c65edf84f4b9

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

RUNNEREXECUTION ONTOLOGY:
  REPAIR (identity criterion missing — EA-WC-03)

RUNNERARTIFACT ONTOLOGY:
  REPAIR (classification dimension-mixing — EA-WC-02)

ARTIFACT CLASSIFICATION:
  REPAIR_REQUIRED

UNIT COHESION:
  PASS

CANONICAL DECISION MODEL:
  PARTIALLY_REQUIRED

EA-CI01..17:
  PASS: 10
  REPAIR: 0
  REDUNDANT: 2 (EA-CI14; cluster EA-CI02/04/13/15 noted but not
    individually failed)
  CONFLICT: 1 (EA-CI16, as applied to idempotency_key)
  INSUFFICIENT: 3 (EA-CI05, EA-CI12, EA-CI17)

BS-EA-01:
  RESOLVED

BS-EA-02:
  REPAIR_REQUIRED

BS-EA-03:
  REPAIR_REQUIRED

BS-EA-04:
  CORRECTLY_DEFERRED

BS-EA-05:
  CORRECTLY_DEFERRED (unchanged)

BS-EA-06:
  CORRECTLY_DEFERRED

NEW CHALLENGE GAPS:
  5 (EA-WC-01..05)

REQUIREMENTS READINESS:
  REPAIR_REQUIRED

POST-EA COMMON BLOCKER:
  NONE

CPL_MINIMUM_FOR_VIR_PGDR_REACHED:
  CONDITIONAL (pending v0.1 repair)

PRIMARY VERDICT:
  WHAT_REPAIR_REQUIRED

REQUIRED REPAIRS:
  5 (R-EA-W01..05)

NEXT GOVERNANCE ACTION:
  Produce CPL_EA_WHAT_v0.1.md incorporating R-EA-W01..05

BUILD UNIT:
  NOT ADMITTED

B6:
  NOT ASSIGNED

REQUIREMENTS:
  NOT AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED
```

**STOP.** No repair of `CPL_EA_WHAT_v0` performed in this artifact, no `v0.1` produced, no WHAT freeze, no Build Unit admission, no B6 assignment, no requirements, no Execution Mandate, no schema/code modification (CPL/VIR/PGDR).

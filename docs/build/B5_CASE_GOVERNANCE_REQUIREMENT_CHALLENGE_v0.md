# CPL — B5 Case Governance Requirement Challenge v0

**System:** Common Product Layer — CPL
**Build Unit:** B5 — Case Governance
**Artifact:** Requirement Challenge
**Version:** v0
**Status:** CHALLENGE COMPLETED
**Target matrix SHA:** `8b2d231912de6fe7ac5b955eb2d14de277966eb0`
**Frozen WHAT SHA:** `f53fce8f0c79aa3b5f041a964883ab8283671584`
**Implementation authorization:** NONE

---

## 1. Challenge purpose

This challenge attempts to falsify `REQ-B5-001` → `REQ-B5-108` against the frozen B5 Case Governance WHAT. It does not ask whether the requirements are reasonable; it asks whether they are complete, atomic, testable, traceable, non-expansive, and whether they could pass while the system remains semantically wrong.

Verified directly against the committed matrix text, and cross-checked against the actual materialized `CaseEvent`/`Case` schema at `1bb3c724...` where relevant (not just against the WHAT's prose).

---

## 2. Challenge — Coverage

Family-by-family:

```text
A  Case identity                    COVERED (001-013)
B  Asset anchoring                  COVERED WITH GAP (014-018) — see RM-B5-02
C  CaseParticipant                  COVERED (019-026)
D  CaseEvent boundary                COVERED (027-034)
E  CaseEvent classification         COVERED, UNDER-SPECIFIED (035-038) — see §21
F  Case lifecycle/status             COVERED (039-045)
G  Authority/canonical decisions    COVERED WITH DEFECT (046-051) — see RM-B5-01, RM-B5-05
H  Execution-pointer boundary        COVERED (052-060)
I  History/reconstructability        COVERED (061-068)
J  Correction/supersession           COVERED (069-074)
K  Idempotency                       COVERED WITH MINOR GAP (075-079) — see RM-B5-06
L  Failure semantics                 COVERED, TESTABILITY DEFECT (080-084) — see RM-B5-04
M  Case-to-Case consolidation excl.  COVERED (085-087)
N  Ontology-name boundary            COVERED (088-090)
O  Domain-truth boundary              COVERED (091-095)
P  Anti-workflow boundary             COVERED (096-097)
Q  Anti-event-sourcing boundary       COVERED (098-099)
R  actor_type boundary                COVERED (100-102)
```

**One frozen WHAT obligation was found entirely uncovered** — see RM-B5-07 below (WHAT §17, `occurred_at` vs recording-time distinction).

---

## 3. Challenge — Atomicity

Reviewed all 108 against the two-independent-failure-modes rule.

Most requirements are correctly atomic (e.g. `REQ-B5-004`–`006` correctly split identity-stability into three separate triggers rather than one combined claim).

**One finding:** `REQ-B5-047` bundles a five-stage pipeline (request → authority → decision → effect → history) into a single requirement. This can fail in multiple independent ways (authority evaluated but no decision recorded; decision recorded but no history trace) and by the stated rule should normally be split. **However**, this exact pattern-level requirement shape has direct precedent in the accepted `B4_REQUIREMENT_MATRIX` (`REQ-B4-049` and neighbors), which also states the pipeline holistically rather than per-stage. Classified as a bounded, non-blocking finding rather than a structural defect — see RM-B5-05.

---

## 4. Challenge — Testability

Scanned all 108 for vague terms (`appropriate`, `valid`, `correct`, `sufficient`, `meaningful`, `securely`, `properly`, `relevant`) programmatically, then manually reviewed each hit.

Most hits are either operationally defined in context (`REQ-B5-018`'s "canonically valid" is explicitly glossed as "resolvable per B4 governance") or false positives (`REQ-B5-057`'s "correct" is a verb, not the adjective).

**One genuine finding:** `REQ-B5-080`–`082` (family L) name five outcome categories (authority rejection, semantic rejection, unresolved, conflict, technical failure) but do not give each category a crisp boundary test within the requirement text itself — see RM-B5-04.

---

## 5. Challenge — Traceability

Checked every requirement against a legitimate frozen source (§23's traceability table was independently re-derived, not merely trusted).

**One genuine finding:** `REQ-B5-051` ("The reused `AuthorityContext` mechanism (B3/B4) MUST be the authority-checking mechanism for B5") is traceable only to *inherited pattern reasoning*, not to any frozen WHAT clause that names `AuthorityContext` or mandates mechanism reuse. The WHAT (§18, §24) requires that authority be evaluated and kept distinct from role — it does not require a *specific implementation class* be reused. This is exactly the `REUSABLE GOVERNANCE PATTERN ≠ AUTOMATIC B5 REQUIREMENT` failure mode this challenge was instructed to hunt for. See RM-B5-01.

No orphan requirements (traceable only to another requirement) were found. No requirement was found justified solely by B3/B4 precedent without independent B5 semantic grounding, **except** `REQ-B5-051` above.

---

## 6. Challenge — WHAT expansion

Searched all 108 for: Asset-optional Case, Contact-only Case, generalized Matter/Occurrence/Evidence/Actor/Role, generic State engine, generic workflow, Organization/Membership, Execution Governance absorption, domain-specific VIR/PGDR logic.

**None found.** `REQ-B5-015`–`017` explicitly reinforce the Asset-anchoring boundary rather than eroding it. `REQ-B5-101` explicitly forbids a generalized Actor/Role object. `REQ-B5-085` explicitly forbids Case merge/consolidation. No requirement expands scope beyond `Case`/`CaseParticipant`/`CaseEvent`.

---

## 7. Challenge — Execution Governance boundary

Re-tested every requirement touching `current_execution_id`/`execution_id`/`RunnerExecution`/`RunnerArtifact` (family H, `REQ-B5-052`–`060`, plus `REQ-B5-013`, `067`) against the nine prohibited behaviors.

All nine are explicitly, individually prohibited across `REQ-B5-052`–`059`. `REQ-B5-067` (recording that an execution reference was later attached) was tested specifically for boundary violation: it requires tracking *that* the Case-side pointer changed, not interpreting *what the execution did* — does not violate the boundary.

**No violation found.** Execution Governance boundary: **PASS**.

---

## 8. Challenge — Asset anchoring

**Adversarial test A** (Contact-only Case): `REQ-B5-016` explicitly forbids this. **PASS.**

**Adversarial test B** (remove `asset_id` after creation, i.e. set to NULL): structurally impossible given the `NOT NULL` constraint reinforced by `REQ-B5-014`. **PASS** (enforced at schema level, not merely by convention).

**Adversarial test C** (rebind Case to a *different* Asset post-creation): **no requirement in the matrix addresses this.** `REQ-B5-014`–`018` only govern the creation-time requirement. Nothing states whether `Case.asset_id` may later be changed to point at a different, still-valid Asset. This is not structurally prevented by the `NOT NULL` constraint (a non-null value can still be updated to a different non-null value) and is not addressed by any other requirement. Per the mandate's own instruction ("do not invent the answer"), this is flagged as a genuine gap — see RM-B5-02.

---

## 9. Challenge — CaseParticipant

Adversarial scenario: Contact C is a `CaseParticipant` with role `TECHNICIAN` — does this alone authorize C to close the Case?

`REQ-B5-022` directly answers: "Being recorded as a `CaseParticipant` MUST NOT, by itself, authorize any Case mutation." **PASS**, explicit and correctly worded (not merely implied).

`CaseParticipant ≠ ContactAssetRelationship` (`REQ-B5-020`) and `ROLE ≠ AUTHORITY ≠ PERMISSION ≠ IDENTITY` (`REQ-B5-023`) are both present and stated as operational distinctions, not merely documentation notes. **PASS.**

---

## 10. Challenge — CaseEvent semantics

Tested `CASE_OPENED`, `DOCUMENT_RECEIVED`, `DIAGNOSIS_REPORTED`, `REPAIR_REPORTED_COMPLETE`, `CASE_CLOSED` against `REQ-B5-035`–`038`.

`REQ-B5-035` establishes the core anti-collapse obligation. `REQ-B5-036` requires governed (non-arbitrary) `event_type` values — this prevents free-text chaos but does **not**, on its own, guarantee that two governed event types cannot both be miscategorized into the wrong semantic class, since no field or mechanism ties an `event_type` value to one of the four classes. This is a genuine, bounded under-specification — see §21 (GAP-02 classification) and is folded into the findings as part of the family E assessment, not a separate blocking finding since GAP-02 is explicitly frozen as open/non-blocking.

---

## 11. Challenge — Event vs decision

Tested the `request close → authority → decision → status change → CASE_CLOSED event` chain against `REQ-B5-030`–`032`, `046`–`050`.

`REQ-B5-049` classifies status transitions as requiring a governed canonical decision. `REQ-B5-030`/`031` prevent the event from being read backward as authorization. No collapse found; no duplicate-authority state found; no event/decision disagreement-without-conflict-handling scenario is left unaddressed (family L's conflict category, `REQ-B5-082`, covers this, subject to RM-B5-04's testability note).

**PASS**, subject to the already-noted testability defect in family L.

---

## 12. Challenge — Case status vs domain state

Re-tested `REQ-B5-040`/`041` against `REPAIRED`, `SAFE`, `DIAGNOSED`, `APPROVED`, `ELIGIBLE`, and "resolved in the physical world." All explicitly named as forbidden in `REQ-B5-041`'s example list or covered by `REQ-B5-040`'s general prohibition. **PASS.**

---

## 13. Challenge — Authority

Checked for both under-governance and over-governance.

**Under-governance:** none found — `REQ-B5-046` requires authority evaluation for all listed material mutations, and `REQ-B5-049` is explicit about which operations require a canonical decision object.

**Over-governance:** none found — `REQ-B5-050` explicitly exempts Case creation and routine event recording from requiring an independent decision object, correctly avoiding forcing trivial persistence through unnecessary machinery.

**One finding carried forward from §5:** `REQ-B5-051`'s mechanism-mandate (RM-B5-01).

---

## 14. Challenge — Correction/supersession

Tested against wrong-metadata, wrong-participant-role, erroneous-event, corrected-event, and reopened-Case scenarios.

`REQ-B5-069`–`072` cover metadata, participant, and event correction with the history-preservation property. `REQ-B5-073`/`074` correctly avoid prematurely designing the schema (no B4-clone mandate, no event-sourcing mandate). **PASS** — B5 semantics (not B4 precedent) justify the correction obligation itself; only the *possible* mechanism references B4 for illustration, which `REQ-B5-074` explicitly disclaims as mandatory.

---

## 15. Challenge — Idempotency

**Adversarial A** (same operation ID, same payload, replay): `REQ-B5-075`–`077` cover this for creation, status transition, and participant changes. **PASS.**

**Adversarial B** (different operation IDs, identical payload): `REQ-B5-079` directly addresses this, explicitly permitting two distinct outcomes. **PASS.**

**Adversarial C** (technical retry after uncertain response — deterministic verification of resulting state): **not explicitly addressed.** The matrix requires non-duplication (`REQ-B5-075`–`077`) but does not explicitly require that a replay return the *outcome of the original operation* (as opposed to merely not duplicating it silently) — a caller retrying after an uncertain response has no explicitly-required way to deterministically learn what happened. Minor, bounded gap — see RM-B5-06.

---

## 16. Challenge — Failure semantics

**Adversarial** (database unavailable during Case close attempt): `REQ-B5-083` requires this not be silently represented as a governed negative decision, and `REQ-B5-084` requires no fabricated history. Correctly prevents both a fabricated canonical denial and a fabricated canonical close. **PASS** on the specific adversarial scenario.

**Adversarial** (authority denies close — must not be reported as technical failure): `REQ-B5-080` distinguishes authority rejection from other categories, but as noted in RM-B5-04, the category *boundaries* are not crisply operationalized within the requirement text — the outcome-level distinction exists, but a reviewer cannot mechanically verify "this specific failure was correctly categorized" without additional interpretation.

---

## 17. Challenge — History and navigation

Tested participant-joined-then-left, status-changed, Case-reopened, event-corrected, execution-reference-attached-later, and metadata-corrected scenarios against `REQ-B5-061`–`068`.

All six scenarios have explicit coverage. `REQ-B5-068` explicitly requires current view and historical reconstruction to be distinct, independently queryable properties — this is the correct target property, not merely an implementation suggestion. **PASS.**

---

## 18. Challenge — GAP-01 (Case consolidation)

`REQ-B5-085`–`087` were re-tested for accidental authorization of merge/survivor-selection/consolidation/supersession/duplicate-resolution. None found. `SAME UNDERLYING MATTER ≠ SAME CPL CASE` is explicit. No requirement in the matrix cannot function without consolidation semantics — `WHAT_CONFLICT` is **not** triggered.

---

## 19. Challenge — GAP-02 (CaseEvent classification)

Classification:

```text
UNDER-SPECIFIED
```

As found in §10 above: the semantic-class distinction is stated as an obligation (`REQ-B5-035`) but the mechanism requirement (`REQ-B5-036`, governed `event_type` values) does not itself guarantee classes stay separable — it only prevents free-text chaos. This is bounded and repairable without inventing new ontology (e.g. a repair could require that each governed `event_type` value's semantic class be documented/determinable, without mandating a schema column).

---

## 20. Challenge — GAP-03 (correction substrate)

`REQ-B5-069`–`074` state semantic outcomes (correction ≠ deletion) while correctly leaving HOW open. `REQ-B5-073` states schema MAY be required without designing it; `REQ-B5-074` explicitly disclaims premature over-design (no "create table X with columns Y/Z" found anywhere). **Correctly handled — no finding.**

---

## 21. Challenge — GAP-04 (ontology vocabulary)

`REQ-B5-088`–`090` correctly avoid introducing a rename project, correctly permit "Case" as working vocabulary post-admission, and correctly refuse to declare the naming question resolved. **Correctly handled — no finding.**

---

## 22. Challenge — Anti-workflow

Searched for ordered steps, task dependencies, scheduler, deadlines, process triggers, workflow graph, conditional routing, BPMN semantics. **None found.** `REQ-B5-096`/`097` explicitly close this. **PASS.**

---

## 23. Challenge — Anti-event-sourcing

Searched for any requirement equivalent to "CaseEvent log is sole authoritative state, current state must be rebuilt by replay." **None found.** `REQ-B5-098` explicitly preserves `case_status` as an independently queryable current-state field, not derived from event replay. **PASS.**

---

## 24. Challenge — actor_type

Tested human-acting-for-organization, external professional, government authority, AI/runner, internal system, unidentified external source against `REQ-B5-100`–`102`.

The matrix correctly avoids treating the enum as canonical ontology (`REQ-B5-100`) and correctly avoids introducing a generalized Actor model (`REQ-B5-101`). `REQ-B5-102` correctly defers the bounded-deficiency question to requirements refinement rather than resolving it here (matches the WHAT Challenge's own earlier finding that the enum is "repairable, not sufficient as-is" — this matrix does not claim otherwise). **No finding — correctly bounded.**

---

## 25. Challenge — Schema/HOW leakage

Reviewed all 108 for prescribed table/column/index/endpoint/service-class names beyond what is already frozen (`case_status` values, `asset_id NOT NULL`, `current_execution_id`/`execution_id` field names — all inherited from the frozen WHAT/schema, hence `NECESSARY_CONSTRAINT`, not leakage).

**One finding**, already identified: `REQ-B5-051` prescribes a specific implementation class (`AuthorityContext`) — classified `HOW_LEAKAGE`, not `NECESSARY_CONSTRAINT`, since the frozen WHAT never names this mechanism. See RM-B5-01.

---

## 26. Challenge — Verification quality

All 108 requirements carry a `Verification:` field with at least one declared class from the required set. Spot-checked twenty requirements across families for plausibility of the declared verification class against the requirement's actual content — all were found appropriate (e.g. `REQ-B5-014` correctly declares `POSTGRESQL, MIGRATION` for a `NOT NULL` constraint check). No mock-only persistence verification was declared for any database-semantics requirement. **PASS.**

---

## 27. Challenge — Duplication/contradiction

**One finding:** `REQ-B5-052` ("B5 MUST NOT interpret RunnerExecution status") and `REQ-B5-055` ("B5 MUST NOT determine or represent execution success/failure as a B5-governed fact") substantially overlap — determining success/failure from a status field is an instance of interpreting that status. Not a contradiction, but a near-duplicate that should be consolidated or explicitly differentiated during repair. See RM-B5-03.

No contradictions (requirement A authorizing what requirement B forbids) were found. No case of the same term used for two different semantics was found.

---

## 28. Challenge — Coverage completeness (final sweep)

Re-derived the traceability table independently against the frozen WHAT's numbered sections rather than trusting the matrix's own §23 table.

**One uncovered frozen obligation found:** WHAT §17 ("Event time") explicitly requires that "reported occurrence time ≠ CPL recording time" not be silently conflated, and explicitly instructs "requirements must determine whether the distinction requires extension" if only one currently exists in schema. Direct schema inspection (`app/cpl/models/case_event.py` at the mandated baseline) confirms `CaseEvent` already has **both** `occurred_at` and `created_at` columns — meaning the distinction the WHAT worried about is already structurally available, and yet **no requirement in the matrix tests, requires, or even mentions this distinction.** This is a genuine, real, currently-orphaned WHAT obligation. See RM-B5-07.

---

## 29. Required findings

### RM-B5-01
**Severity:** NON-BLOCKING
**Classification:** HOW_LEAKAGE, TRACEABILITY_DEFECT
**Affected requirements:** REQ-B5-051
**Frozen source:** WHAT §18/§24 (authority must be evaluated, distinct from role — no specific mechanism named)
**Problem:** Requirement mandates reuse of the specific `AuthorityContext` implementation class from B3/B4, which the frozen WHAT never names as mandatory.
**Why it matters:** Prescribes HOW without demonstrated semantic necessity; violates the "reusable governance pattern ≠ automatic requirement" principle this challenge was specifically instructed to test.
**Required repair:** Reword to require a governed authority-checking mechanism distinct from role/participation (the semantic property), without mandating the specific class name. Reuse of `AuthorityContext` may be *recommended* in commentary, not *required* by the WHAT-traceable requirement text.
**Closure criterion:** Requirement text contains no mandatory reference to a specific implementation class.

### RM-B5-02
**Severity:** NON-BLOCKING
**Classification:** COVERAGE_GAP
**Affected requirements:** Family B (REQ-B5-014–018)
**Frozen source:** WHAT §9 (REPAIR-03, Asset anchoring) — silent on post-creation mutability
**Problem:** No requirement states whether `Case.asset_id` may be rebound to a different Asset after creation.
**Why it matters:** This is a real operational question (adversarial test C) left completely unaddressed; an implementer would have to guess.
**Required repair:** Add one explicit requirement stating the current policy — recommended: prohibit post-creation rebinding under this Build Unit (consistent with Case identity stability, family A), with any future need for rebinding raised as a separate governance question rather than implemented silently.
**Closure criterion:** A requirement exists explicitly permitting or forbidding `asset_id` mutation after Case creation.

### RM-B5-03
**Severity:** NON-BLOCKING
**Classification:** DUPLICATION
**Affected requirements:** REQ-B5-052, REQ-B5-055
**Frozen source:** WHAT §21a (REPAIR-01)
**Problem:** Substantial semantic overlap between "MUST NOT interpret RunnerExecution status" and "MUST NOT determine execution success/failure."
**Why it matters:** Redundant requirements inflate the matrix without adding independently testable coverage, and could be repaired inconsistently if only one is touched in a future revision.
**Required repair:** Consolidate into one requirement, or explicitly differentiate (e.g. one about raw status values, one about derived success/failure semantics) if a genuine distinction is intended.
**Closure criterion:** The two requirements either merge into one or state a clearly non-overlapping distinction.

### RM-B5-04
**Severity:** NON-BLOCKING
**Classification:** TESTABILITY_DEFECT
**Affected requirements:** REQ-B5-080, REQ-B5-081, REQ-B5-082
**Frozen source:** Outcome-discipline obligation (analogous to B3/B4 F19, applied fresh to Case)
**Problem:** The five failure categories (authority rejection, semantic rejection, unresolved, conflict, technical failure) are named but not given crisp per-category boundary criteria within the requirement text.
**Why it matters:** A reviewer cannot mechanically determine, from the requirement text alone, whether a given implementation categorized a specific failure correctly.
**Required repair:** Add a short operational example or boundary test per category, mirroring the concrete adversarial examples already used elsewhere in this matrix (e.g. family H's `REQ-B5-060`).
**Closure criterion:** Each of the five categories has at least one concrete pass/fail example in the requirement text.

### RM-B5-05
**Severity:** NON-BLOCKING
**Classification:** ATOMICITY_DEFECT
**Affected requirements:** REQ-B5-047
**Frozen source:** WHAT §24–27
**Problem:** Bundles a five-stage pipeline into one requirement with multiple independent failure modes.
**Why it matters:** Could pass a superficial review while one pipeline stage is actually broken.
**Required repair:** Either split into per-stage requirements, or explicitly accept as a pattern-level requirement (consistent with `B4_REQUIREMENT_MATRIX`'s `REQ-B4-049` precedent) with a note explaining why the holistic form is intentional.
**Closure criterion:** Either split, or an explicit rationale is added referencing the B4 precedent.

### RM-B5-06
**Severity:** NON-BLOCKING
**Classification:** IDEMPOTENCY_DEFECT
**Affected requirements:** Family K (REQ-B5-075–079)
**Frozen source:** WHAT §31
**Problem:** No requirement explicitly obligates the system to return the outcome of the original operation on replay (only non-duplication is required).
**Why it matters:** A caller retrying after an uncertain response has no explicitly-required deterministic way to learn the actual resulting state.
**Required repair:** Add a requirement that a replayed request MUST return (or make retrievable) the outcome of the original governed operation.
**Closure criterion:** Such a requirement exists and is independently testable.

### RM-B5-07
**Severity:** NON-BLOCKING
**Classification:** COVERAGE_GAP
**Affected requirements:** None (orphaned obligation — no requirement currently exists)
**Frozen source:** WHAT §17 ("Event time")
**Problem:** The WHAT's explicit `occurred_at ≠ recorded_at` distinction has zero requirement coverage, despite the underlying `CaseEvent` schema already providing both columns (`occurred_at`, `created_at`) at the mandated baseline.
**Why it matters:** A frozen, explicitly-named WHAT obligation is currently untested and unenforced by this matrix — the cheapest possible repair (the schema already supports it) is being left on the table.
**Required repair:** Add a requirement (or small family) requiring that `CaseEvent.occurred_at` and `CaseEvent.created_at` remain independently queryable and are never silently conflated, with a verification example (e.g. an event recorded today about something that occurred yesterday).
**Closure criterion:** At least one requirement traces to WHAT §17 and is independently testable.

### RM-B5-08
**Severity:** NON-BLOCKING
**Classification:** OPEN_GAP_MISHANDLING (partial — under-specification, not mishandling in the prohibited-expansion sense)
**Affected requirements:** REQ-B5-035–038
**Frozen source:** WHAT §39a, GAP-02
**Problem:** GAP-02 coverage is present but under-specified (see §19 above) — governed `event_type` values alone do not guarantee the four semantic classes remain separable.
**Why it matters:** The frozen distinction (`WORLD EVENT ≠ DOMAIN ASSERTION ≠ CPL OPERATIONAL FACT ≠ CANONICAL DECISION CONSEQUENCE`) could still collapse in practice even with this matrix satisfied.
**Required repair:** Add a requirement that each governed `event_type` value's semantic class be documented/determinable at definition time, without mandating a specific schema column (preserving GAP-02's open status on the mechanism question).
**Closure criterion:** A requirement exists that makes class-collapse detectable/preventable without resolving GAP-02's mechanism question.

---

## 30. Finding summary by classification

```text
HOW_LEAKAGE              1  (RM-B5-01)
COVERAGE_GAP              2  (RM-B5-02, RM-B5-07)
DUPLICATION                1  (RM-B5-03)
TESTABILITY_DEFECT          1  (RM-B5-04)
ATOMICITY_DEFECT             1  (RM-B5-05)
IDEMPOTENCY_DEFECT            1  (RM-B5-06)
OPEN_GAP_MISHANDLING (partial) 1  (RM-B5-08)
TRACEABILITY_DEFECT          1  (overlaps RM-B5-01)

TOTAL FINDINGS: 8
BLOCKING: 0
NON-BLOCKING: 8
WHAT_CONFLICT: 0
```

All eight findings are bounded and repairable without touching the frozen WHAT — none requires new semantics, none requires reopening `CPL_CG_WHAT_v0.1`.

---

## 31. Final acceptance gate assessment

```text
All frozen WHAT obligations covered:        NO (RM-B5-07 orphaned obligation)
No blocking atomicity defect:               PASS (RM-B5-05 is non-blocking)
No blocking testability defect:             PASS (RM-B5-04 is non-blocking)
Traceability complete:                       NO (RM-B5-01 mechanism-mandate untraceable)
No WHAT expansion:                          PASS
No unresolved WHAT conflict:                PASS
Execution Governance excluded:              PASS
Asset anchoring preserved:                  PASS, WITH GAP (RM-B5-02)
Authority semantics sufficient:              PASS, WITH DEFECT (RM-B5-01)
Correction/history semantics sufficient:    PASS
Idempotency testable:                        PASS, WITH GAP (RM-B5-06)
Failure semantics distinct:                  PASS, WITH TESTABILITY DEFECT (RM-B5-04)
Open gaps bounded correctly:                 PASS, WITH UNDER-SPECIFICATION (RM-B5-08)
No domain-truth leakage:                     PASS
No workflow/event-sourcing contamination:    PASS
No blocking contradictions:                  PASS
Implementation derivable without guessing:    NOT YET — RM-B5-02 and RM-B5-01 would force guessing
```

Because at least two conditions genuinely fail (full coverage, complete traceability) and their absence would force an implementer to guess, `REQUIREMENTS_ACCEPTED` is not warranted. All eight findings are bounded, non-blocking in the sense of not requiring WHAT revision, and repairable in a single targeted revision — matching the criteria for `REPAIR_REQUIRED`.

---

## 32. Final summary

```text
B5_CASE_GOVERNANCE_REQUIREMENT_CHALLENGE_v0
===========================================

TARGET MATRIX:
  8b2d231912de6fe7ac5b955eb2d14de277966eb0

REQUIREMENTS CHALLENGED:
  108

RANGE:
  REQ-B5-001 .. REQ-B5-108

FROZEN WHAT:
  f53fce8f0c79aa3b5f041a964883ab8283671584

BUILD UNIT:
  B5_CASE_GOVERNANCE

BLOCKING FINDINGS:
  0

NON-BLOCKING FINDINGS:
  8

WHAT CONFLICTS:
  0

EXECUTION BOUNDARY:
  PASS

TRACEABILITY:
  FAIL (1 defect: RM-B5-01)

ATOMICITY:
  PASS (1 non-blocking note: RM-B5-05)

TESTABILITY:
  FAIL (1 defect: RM-B5-04)

NON-EXPANSION:
  PASS

FINAL VERDICT:
  REPAIR_REQUIRED
```

---

## 33. Authorized repair scope for v0.1

```text
RM-B5-01  Authority mechanism de-prescription
RM-B5-02  Asset rebinding policy
RM-B5-03  Execution-status/success-failure deduplication
RM-B5-04  Failure-category boundary examples
RM-B5-05  REQ-B5-047 split or explicit rationale
RM-B5-06  Idempotent-replay outcome retrieval
RM-B5-07  occurred_at / created_at distinction requirement (new, traces to WHAT §17)
RM-B5-08  CaseEvent classification determinability requirement
```

Expected repaired range: `REQ-B5-001` → `REQ-B5-108` preserved where unaffected, plus a small number of new requirements (RM-B5-02, 04, 06, 07, 08 each imply at least one addition), likely landing in the `108`–`115` range. Requirement count is not itself a governance target.

---

## 34. Stop condition

**STOP.** This challenge does not repair the matrix, does not produce `v0.1`, does not freeze requirements, does not create an Execution Mandate, does not touch migrations, production code, tests, or a candidate branch.

**END — CPL B5 Case Governance Requirement Challenge v0**

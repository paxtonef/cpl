# CPL — B5 Case Governance
# Requirement Re-Challenge v0.1

```text
Status:
  TARGETED RE-CHALLENGE

Target:
  docs/build/B5_CASE_GOVERNANCE_REQUIREMENT_MATRIX_v0.1.md

Canonical target SHA:
  ed815665af88871d742019465521555f88a3257e

Source matrix v0:
  8b2d231912de6fe7ac5b955eb2d14de277966eb0

Requirement Challenge v0:
  a621128f2f9b778812804e14c75590c5fe5b7196

Challenge verdict:
  REPAIR_REQUIRED

Repairs under re-challenge:
  RM-B5-01 .. RM-B5-08
```

This is not a repeat of the full original Requirement Challenge. It verifies: (1) closure of `RM-B5-01`→`08`, (2) non-regression, (3) freeze readiness. It does not perform requirements freeze.

```text
Repair presence ≠ repair correctness.
Repair correctness ≠ requirements acceptance.
Requirements acceptance ≠ requirements freeze.
```

Verified directly against the committed text at `ed81566`, not against the developer's description of it.

---

## 1. RM-B5-01 — Authority mechanism de-prescription

Repaired `REQ-B5-051` text confirmed: requires only the semantic property (governed authority-checking, `ROLE ≠ AUTHORITY ≠ PERMISSION ≠ IDENTITY`, independent testability from role) and explicitly states it "does NOT mandate a specific implementation class or service (e.g. it does not require reuse of B3/B4's `AuthorityContext`)." Searched the full requirement text and found no residual mandatory reference to `AuthorityContext`, a specific B3/B4 class, or any named service/interface.

**Adversarial test:** could an implementation satisfy B5 using a different governed authority-checking mechanism while preserving all frozen semantics? **Yes** — nothing in the repaired text ties the obligation to a specific class.

```text
RM-B5-01 CLOSED
```

---

## 2. RM-B5-02 — Post-creation Asset rebinding

`REQ-B5-109` states the exact policy: `Case.asset_id` MUST NOT change post-creation. The mandated adversarial test (create with Asset A, attempt update to Asset B, expect rejection) is embedded verbatim in the requirement's own verification steps. Checked for invented mechanism: the requirement explicitly disclaims Case merge, Case migration, survivor-selection logic, and generic reassignment — none appear anywhere in its text.

```text
RM-B5-02 CLOSED
```

---

## 3. RM-B5-03 — Execution status / success-failure duplication

`REQ-B5-052` (raw status interpretation) and `REQ-B5-055` (derived Case-level fact) are now explicitly differentiated, with `REQ-B5-055`'s text directly stating the distinction from `REQ-B5-052`.

**Test A** ("implementation reads raw `execution.status` merely to display it, without deriving Case success — which requirement applies?"): `REQ-B5-052` applies — reading/exposing the raw status value is exactly the "interpret ... raw RunnerExecution lifecycle/status semantics" it prohibits; `REQ-B5-055` does not apply since no Case-level fact is derived.

**Test B** ("implementation stores `CASE_EXECUTION_SUCCESSFUL` as B5 truth from another service's outcome — which requirement applies?"): `REQ-B5-055` applies directly — this is exactly "deriv[ing]/promot[ing] ... execution success/failure ... as a B5-governed Case fact."

The two tests resolve to different requirements — coverage is genuinely distinct, not merely relabeled.

```text
RM-B5-03 CLOSED
```

---

## 4. RM-B5-04 — Failure category testability

All five categories now carry a boundary example in `REQ-B5-080`–`083`. Re-tested the five mandated scenarios:

- Authority policy denies Case close → `REQ-B5-080`'s first example matches exactly (`AUTHORITY_REJECTION`, not `TECHNICAL_FAILURE`).
- Asset rebinding attempt → `REQ-B5-080`'s second example matches (`SEMANTIC_REJECTION`, not `AUTHORITY_REJECTION`).
- Governing fact not yet determinable → `REQ-B5-081` matches (`UNRESOLVED`, never a rejection).
- Two incompatible authoritative inputs → `REQ-B5-082`'s first example matches (`CONFLICT`, never `UNRESOLVED`/`TECHNICAL_FAILURE`).
- PostgreSQL unavailable → `REQ-B5-082`'s second example matches (`TECHNICAL_FAILURE`, no canonical negative decision).

**One genuine defect found while re-verifying:** `REQ-B5-080`'s second boundary example cites `REQ-B5-018a` — **an identifier that does not exist anywhere in the matrix.** The Asset-rebinding requirement was correctly implemented as `REQ-B5-109` (per RM-B5-02), but this cross-reference inside `REQ-B5-080` was never updated to match. Confirmed by direct search: `grep "### REQ-B5-018a"` returns no defined requirement.

This does not undermine the *substance* of `REQ-B5-080`'s boundary example (the semantic classification it describes is correct), but a reference to a phantom requirement ID is a genuine, concrete defect that would confuse an implementer or verifier trying to trace the example.

```text
RM-B5-04 CLOSED (substance)
NEW DEFECT FOUND: dangling reference to non-existent REQ-B5-018a — see RM-B5-09 below
```

---

## 5. RM-B5-05 — Pipeline atomicity

`REQ-B5-047` was narrowed to a single stage (authority-before-effect) and correctly cross-references the three new atomic stage requirements. Tested the four mandated challenge scenarios:

- **A** (authority evaluated, decision not persisted): covered by `REQ-B5-110` ("decision MUST be established before the governed effect is applied") — independently testable without reference to `REQ-B5-047`.
- **B** (decision persisted, effect not applied): also covered by `REQ-B5-110`'s ordering requirement combined with `REQ-B5-112`'s non-fabrication clause.
- **C** (effect applied, history/trace missing): covered by `REQ-B5-111` directly.
- **D** (early-stage failure causes later-stage success marker to appear): covered by `REQ-B5-112` directly.

Each of the four scenarios maps to a distinct, independently checkable requirement. The cross-reference inside `REQ-B5-047` to `REQ-B5-110`/`111`/`112` was verified correct (unlike the `REQ-B5-018a` defect above).

```text
RM-B5-05 CLOSED
```

---

## 6. RM-B5-06 — Idempotent replay outcome retrieval

`REQ-B5-113`'s adversarial test is the mandated scenario verbatim (operation succeeds, response lost, retry, outcome must be returned/exposed, only one canonical effect exists). The requirement explicitly rejects "silently return[ing] a no-op without allowing recovery of the original outcome" — directly closing the "do nothing on replay" loophole the re-challenge was instructed to reject. `SAME PAYLOAD ≠ SAME OPERATION IDENTITY` remains preserved via unaffected `REQ-B5-078`/`079` (untouched by this repair, confirmed still present).

```text
RM-B5-06 CLOSED
```

---

## 7. RM-B5-07 — occurred_at vs created_at

`REQ-B5-114` traces directly to WHAT §17 (confirmed via the matrix's own traceability table). The mandated test (occurred yesterday, recorded today, both timestamps independently reconstructable) is embedded as the requirement's own verification example. No new timestamp fields were introduced — the requirement correctly uses the existing `occurred_at`/`created_at` columns already present in the materialized schema.

```text
RM-B5-07 CLOSED
```

---

## 8. RM-B5-08 — CaseEvent classification determinability

`REQ-B5-115` requires semantic-class determinability at definition time without interpreting payload, and explicitly disclaims mandating a new database column, ontology table, enum expansion, or specific storage mechanism — `GAP-02` remains open on mechanism as required. The mandated test (`DIAGNOSIS_REPORTED` vs `CASE_CLOSED` distinguishable without payload guessing) is the requirement's own adversarial test.

```text
RM-B5-08 CLOSED
```

---

## 9. New requirements review (REQ-B5-109 → 115)

| REQ | Justified by | Traceable | Atomic | Testable | Duplicate? | HOW leakage? | New ontology? | Execution absorption? |
|---|---|---|---|---|---|---|---|---|
| 109 | RM-B5-02 | WHAT §9 | Yes | Yes | No | No | No | No |
| 110 | RM-B5-05 | WHAT §24–27 | Yes | Yes | No | No | No | No |
| 111 | RM-B5-05 | WHAT §24–27 | Yes | Yes | No | No | No | No |
| 112 | RM-B5-05 | WHAT §24–27 | Yes | Yes | **Partial — see below** | No | No | No |
| 113 | RM-B5-06 | WHAT §31 | Yes | Yes | No | No | No | No |
| 114 | RM-B5-07 | WHAT §17 | Yes | Yes | No | No | No | No |
| 115 | RM-B5-08 | WHAT §39a | Yes | Yes | No | No | No | No |

**Partial duplication finding:** `REQ-B5-112` ("failure at one pipeline stage MUST NOT fabricate completion of a later stage") and the pre-existing, unaffected `REQ-B5-084` ("a failed write MUST NOT fabricate canonical history") overlap conceptually — both prohibit fabricating success after a failure, at different granularities (pipeline-stage-specific vs. general write-failure). Not identical, not contradictory, but close enough to warrant a note. Non-blocking; recommend either cross-referencing them explicitly or consolidating in a future revision.

```text
NEW_REQUIREMENTS PASS, WITH ONE NON-BLOCKING NOTE (REQ-B5-084/112 overlap)
```

---

## 10. Non-regression

Independently re-confirmed via diff that `v0.1` is byte-identical to `v0` outside the 32 hunks the repair touched (header, §4 family B addition, §51, §52/55, §80–82, §47, new family T, count/traceability/governance/summary sections). Since NR-01 through NR-16 test sections/invariants outside the touched areas (with NR-02/NR-08 partially touching repaired areas but only strengthened, not weakened), all pass by construction plus direct spot-check:

```text
NR-01  Case remains stable CPL operational context        PASS (untouched)
NR-02  Case.asset_id remains mandatory                     PASS (unchanged NOT NULL + strengthened by REQ-B5-109)
NR-03  CaseParticipant not equal ContactAssetRelationship   PASS (untouched)
NR-04  ROLE, AUTHORITY, PERMISSION, IDENTITY kept distinct   PASS (untouched, also reaffirmed in repaired REQ-B5-051)
NR-05  WORLD EVENT, DOMAIN ASSERTION, CASE EVENT distinct    PASS (untouched)
NR-06  CaseEvent not equal Canonical Case Decision            PASS (untouched)
NR-07  CASE STATUS not equal DOMAIN STATE                      PASS (untouched)
NR-08  Execution Governance remains excluded                   PASS (REQ-B5-052/055 repair clarifies, does not weaken, the boundary)
NR-09  No domain-truth authority gained by B5                   PASS (untouched)
NR-10  No generic workflow introduced                             PASS (untouched)
NR-11  No universal event sourcing introduced                      PASS (untouched)
NR-12  No generalized Actor/Role ontology introduced                 PASS (untouched, REQ-B5-051 repair does not introduce one)
NR-13  GAP-01 remains unresolved/non-blocking                         PASS (family M untouched)
NR-14  GAP-02 mechanism remains open                                    PASS (REQ-B5-115 explicitly preserves this)
NR-15  GAP-03 substrate HOW remains implementation-open                  PASS (family J untouched)
NR-16  GAP-04 ontology/table-name distinction preserved                    PASS (family N untouched)
```

```text
NON_REGRESSION PASS
```

---

## 11. Traceability re-check

All 115 requirements were checked for a legitimate frozen source. `RM-B5-01`'s original traceability defect (mandating `AuthorityContext` without WHAT justification) is removed — `REQ-B5-051` now traces only to the semantic obligation. `RM-B5-07`'s orphaned WHAT §17 obligation is now covered by `REQ-B5-114`. No new orphan requirements were created among `109`–`115` (each traces to its originating `RM-B5-0X` finding, which itself traces to a frozen WHAT clause). No requirement relies solely on B3/B4 precedent without independent B5 justification.

**However:** the dangling `REQ-B5-018a` reference inside `REQ-B5-080` (§4 above) is itself a traceability defect — a citation that resolves to nothing. This is new, introduced by the repair process itself (the requirement was drafted referencing an intermediate identifier that was later renumbered to `REQ-B5-109`, and the cross-reference was never updated).

```text
TRACEABILITY FAIL — one dangling reference (REQ-B5-018a should be REQ-B5-109)
```

---

## 12. Coverage re-check

```text
Asset anchoring / rebinding:              COVERED (REQ-B5-109)
Authority mechanism, no HOW leakage:      COVERED (REQ-B5-051, repaired)
Failure categories testable:               COVERED (REQ-B5-080-083), subject to the dangling-reference defect
Idempotent replay outcome:                 COVERED (REQ-B5-113)
occurred_at / created_at:                  COVERED (REQ-B5-114)
CaseEvent classification determinability:  COVERED (REQ-B5-115)
```

Final sweep: no frozen WHAT obligation was found entirely uncovered (the one obligation the original challenge found orphaned — WHAT §17 — is now covered).

```text
COVERAGE COMPLETE, SUBJECT TO ONE TRACEABILITY DEFECT NOTED ABOVE
```

---

## 13. New finding from this re-challenge

### RM-B5-09
**Severity:** NON-BLOCKING (trivial, single-line fix)
**Classification:** TRACEABILITY_DEFECT / DANGLING_REFERENCE
**Affected requirement:** REQ-B5-080
**Problem:** Cites `REQ-B5-018a` as the source of its second boundary example (Asset-rebinding semantic rejection). `REQ-B5-018a` does not exist in the matrix; the actual Asset-rebinding requirement is `REQ-B5-109`.
**Why it matters:** A dangling cross-reference undermines the traceability discipline this matrix otherwise maintains rigorously; an implementer or verifier following the citation would find nothing.
**Required repair:** Change `REQ-B5-018a` to `REQ-B5-109` in `REQ-B5-080`'s text.
**Closure criterion:** The citation resolves to an existing requirement.

---

## 14. Freeze-readiness gate

```text
RM-B5-01 closed:                 YES
RM-B5-02 closed:                 YES
RM-B5-03 closed:                 YES
RM-B5-04 closed:                 YES (substance), but see RM-B5-09
RM-B5-05 closed:                 YES
RM-B5-06 closed:                 YES
RM-B5-07 closed:                 YES
RM-B5-08 closed:                 YES
NEW_REQUIREMENTS:                PASS (one non-blocking overlap note)
NON_REGRESSION:                  PASS
TRACEABILITY:                    FAIL (RM-B5-09 dangling reference)
COVERAGE:                        COMPLETE
WHAT conflict:                   NONE
B5 scope expansion:               NONE
Execution Governance absorption:  NONE
```

Because `TRACEABILITY` genuinely fails (a citation to a non-existent requirement ID), `REQUIREMENTS_ACCEPTED` cannot be honestly returned even though all eight original findings are substantively closed. The defect is trivial — a one-line correction — but it is real, and an implementer following `REQ-B5-080` as written would hit a dead reference.

---

## 15. Final verdict

```text
REPAIR_REQUIRED
```

Bounded to exactly one finding: `RM-B5-09` (fix the dangling `REQ-B5-018a` to `REQ-B5-109` reference in `REQ-B5-080`). No other repair is authorized or required. This does not reopen `RM-B5-01`→`08`, which are all independently confirmed closed.

---

## 16. Output summary

```text
B5_CASE_GOVERNANCE_REQUIREMENT_RECHALLENGE_v0.1
===============================================

TARGET MATRIX:
  ed815665af88871d742019465521555f88a3257e

REQUIREMENTS:
  115

RANGE:
  REQ-B5-001 .. REQ-B5-115

RM-B5-01:
  CLOSED

RM-B5-02:
  CLOSED

RM-B5-03:
  CLOSED

RM-B5-04:
  CLOSED

RM-B5-05:
  CLOSED

RM-B5-06:
  CLOSED

RM-B5-07:
  CLOSED

RM-B5-08:
  CLOSED

NEW REQUIREMENTS:
  PASS

NON-REGRESSION:
  PASS

TRACEABILITY:
  FAIL

COVERAGE:
  COMPLETE

WHAT CONFLICT:
  NONE

EXECUTION GOVERNANCE BOUNDARY:
  PRESERVED

NEW FINDING:
  RM-B5-09 (dangling reference REQ-B5-018a should be REQ-B5-109 in REQ-B5-080)

FINAL VERDICT:
  REPAIR_REQUIRED
```

---

## 17. Stop condition

**STOP.** This re-challenge does not modify Matrix v0.1, does not produce v0.2, does not freeze requirements, does not create an Execution Mandate, does not touch migrations, production code, tests, or a candidate branch.

If `REPAIR_REQUIRED` is resolved by a trivial `v0.2` correcting only `RM-B5-09`, the expectation is that a narrow re-verification of that single citation (not a full third challenge) would be sufficient before requirements freeze readiness is reaffirmed.

**END — CPL B5 Case Governance Requirement Re-Challenge v0.1**

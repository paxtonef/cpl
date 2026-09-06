# CPL — B5 Case Governance Requirements Freeze v0

## Purpose

This artifact performs the explicit governance act that freezes the accepted B5 Case Governance requirement set. It does not modify the requirements themselves. It distinguishes `REQUIREMENTS_ACCEPTED` (a verification finding, already established) from `REQUIREMENTS_FROZEN` (a governance act, performed here).

---

## 1. Canonical baselines

```text
Governance HEAD before this freeze:
  17415bbd1469bf25748d6a9e4850e4ad86404d35

Build Unit:
  B5_CASE_GOVERNANCE

Frozen WHAT:
  f53fce8f0c79aa3b5f041a964883ab8283671584

WHAT Re-Challenge:
  e9618ee88a1a9d9898daee5f5f8830875267a8b0

WHAT Freeze / Admission:
  85cb0b18876faf81eb89906236b87e959056a66a

Requirement Matrix v0:
  8b2d231912de6fe7ac5b955eb2d14de277966eb0

Requirement Challenge v0:
  a621128f2f9b778812804e14c75590c5fe5b7196

Requirement Matrix v0.1:
  ed815665af88871d742019465521555f88a3257e

Requirement Re-Challenge v0.1:
  e953605a10be8c18b9d67d28a6b74266e6916dbb

Requirement Matrix v0.2:
  a36d9e8c2ca7a435e9cd7e1ec97ee38fcc0f9ad3

Requirement Re-Challenge v0.2:
  17415bbd1469bf25748d6a9e4850e4ad86404d35

Final challenge verdict:
  REQUIREMENTS_ACCEPTED

Requirement count:
  115

Requirement range:
  REQ-B5-001 .. REQ-B5-115

Findings:
  RM-B5-01 .. RM-B5-09 ALL CLOSED
```

---

## 2. Freeze subject

The canonical frozen B5 requirement set is:

```text
docs/build/B5_CASE_GOVERNANCE_REQUIREMENT_MATRIX_v0.2.md

Commit:
  a36d9e8c2ca7a435e9cd7e1ec97ee38fcc0f9ad3

Requirements:
  REQ-B5-001 .. REQ-B5-115

Total:
  115
```

No earlier Requirement Matrix revision is canonical after this freeze. `v0` and `v0.1` remain historical governance evidence only.

---

## 3. Freeze decision

```text
B5_CASE_GOVERNANCE REQUIREMENTS:
  ACCEPTED
  FROZEN

Canonical requirement baseline:
  a36d9e8c2ca7a435e9cd7e1ec97ee38fcc0f9ad3

Canonical requirement range:
  REQ-B5-001 .. REQ-B5-115
```

The frozen requirements may now be used as the normative source for the B5 Execution Mandate.

---

## 4. Freeze invariant

```text
FROZEN WHAT
        +
FROZEN REQUIREMENTS
        =
AUTHORIZED BASIS FOR EXECUTION MANDATE
```

But:

```text
REQUIREMENTS FREEZE
        ≠
IMPLEMENTATION AUTHORIZATION
```

No production implementation begins merely because requirements are frozen. The next governance act is issuance of the Execution Mandate.

---

## 5. Change control

After freeze, no B5 requirement may be:

```text
silently rewritten
removed
renumbered
weakened
strengthened
semantically reinterpreted
replaced by implementation convenience
```

Any discovered semantic defect must trigger governed change control. Classify future issues as one of:

```text
IMPLEMENTATION_DEFECT
REQUIREMENT_AMBIGUITY
REQUIREMENT_CONFLICT
WHAT_CONFLICT
GOVERNANCE_DEVIATION
```

Do not silently repair frozen requirements during implementation.

---

## 6. Frozen semantic boundaries

The freeze preserves all accepted B5 boundaries.

B5 governs:

```text
Case
CaseParticipant
CaseEvent
```

B5 does NOT govern:

```text
RunnerExecution lifecycle
RunnerArtifact semantics
generalized Occurrence
generalized Evidence
generalized Actor/Role
generic State engine
Organization/Membership
workflow/BPMN
universal event sourcing
domain-specific VIR/PGDR truth
```

---

## 7. Asset anchoring

Freeze explicitly preserves:

```text
Case.asset_id MUST remain mandatory.
```

Current B5 policy: Case is Asset-anchored. Post-creation rebinding to a different Asset is prohibited under the B5 frozen requirements. Asset-optional Case remains OUT OF SCOPE. Future change requires separate governance authorization.

---

## 8. Execution Governance boundary

Freeze explicitly preserves:

```text
Case.current_execution_id
CaseEvent.execution_id
```

are Case-side references only under B5. B5 MUST NOT govern:

```text
execution status
execution lifecycle
execution success/failure semantics
execution lineage
parent_execution_id
RunnerExecution correction/supersession
RunnerArtifact governance
complete execution history
```

Execution Governance remains a subsequent Build Unit.

---

## 9. Authority boundary

Freeze preserves:

```text
ROLE ≠ AUTHORITY ≠ PERMISSION ≠ IDENTITY
```

B5 requires governed authority evaluation where required. The frozen requirements do NOT mandate a particular implementation class such as `AuthorityContext`.

---

## 10. CaseEvent semantics

Freeze preserves:

```text
WORLD EVENT ≠ DOMAIN ASSERTION ≠ CPL OPERATIONAL FACT ≠ CANONICAL DECISION CONSEQUENCE
```

Each governed `CaseEvent.event_type` must have a determinable semantic class. The implementation mechanism remains open. No mandatory `semantic_class` database column is implied by freeze.

---

## 11. Event time

Freeze preserves:

```text
CaseEvent.occurred_at ≠ CaseEvent.created_at
```

Occurrence/report time and CPL recording time are independently representable and queryable. They MUST NOT be silently conflated.

---

## 12. Case status boundary

Freeze preserves:

```text
CASE STATUS ≠ DOMAIN OBJECT STATUS ≠ WORLD STATE
```

Closing a Case does NOT mean: Asset repaired; Asset safe; diagnosis correct; work successful; claim approved; physical-world issue resolved.

---

## 13. History / correction

Freeze preserves:

```text
CORRECTION ≠ HISTORY DELETION
```

Current operational state and historical reconstruction must remain distinct and reconstructable. The exact persistence mechanism remains HOW.

---

## 14. Idempotency

Freeze preserves:

```text
SAME PAYLOAD ≠ SAME OPERATION IDENTITY
```

Replay of the same governed operation identity must avoid duplicate canonical effect, and return or make deterministically retrievable the original outcome.

---

## 15. Failure semantics

Freeze preserves distinct outcomes:

```text
AUTHORITY_REJECTION
SEMANTIC_REJECTION
UNRESOLVED
CONFLICT
TECHNICAL_FAILURE
```

Technical failure MUST NOT fabricate a governed negative decision or a successful canonical effect.

---

## 16. Open gaps

The following remain intentionally bounded/open and are NOT silently resolved by freeze:

```text
GAP-01  Case consolidation / Case merge.
GAP-02  Exact CaseEvent semantic-class storage mechanism.
GAP-03  Exact correction/supersession substrate HOW.
GAP-04  Physical table vocabulary vs canonical ontology vocabulary.
```

```text
OPEN ≠ UNCONTROLLED
```

These gaps cannot be used to expand implementation beyond the frozen requirements.

---

## 17. Requirements acceptance evidence

```text
Initial challenge:
  REPAIR_REQUIRED

RM-B5-01 .. RM-B5-08:
  repaired in Matrix v0.1

Targeted Re-Challenge v0.1:
  RM-B5-01 .. RM-B5-08 CLOSED
  RM-B5-09 discovered

Matrix v0.2:
  RM-B5-09 repaired

Targeted Re-Challenge v0.2:
  REQUIREMENTS_ACCEPTED

Final state:
  RM-B5-01 .. RM-B5-09: ALL CLOSED

Traceability:                PASS
Requirement-set integrity:   PASS
Non-regression:              PASS
Execution boundary:          PRESERVED
WHAT conflict:                NONE
```

---

## 18. Execution Mandate authorization

Upon this freeze:

```text
B5 Execution Mandate production becomes AUTHORIZED.
```

This does NOT itself authorize coding. Correct transition:

```text
WHAT_FROZEN
        ↓
REQUIREMENTS_FROZEN
        ↓
EXECUTION_MANDATE_AUTHORIZED
        ↓
EXECUTION_MANDATE_ISSUED
        ↓
BUILD_ALLOWED
```

Therefore:

```text
B5_EXECUTION_MANDATE:
  AUTHORIZED FOR PRODUCTION
  NOT YET ISSUED

B5_IMPLEMENTATION:
  NOT AUTHORIZED
```

---

## 19. Canonical state after freeze

```text
B5_CASE_GOVERNANCE_REQUIREMENTS_FREEZE_v0
=========================================

BUILD UNIT:
  B5_CASE_GOVERNANCE

WHAT:
  FROZEN

FROZEN WHAT:
  f53fce8f0c79aa3b5f041a964883ab8283671584

REQUIREMENT MATRIX:
  B5_CASE_GOVERNANCE_REQUIREMENT_MATRIX_v0.2

FROZEN REQUIREMENT BASELINE:
  a36d9e8c2ca7a435e9cd7e1ec97ee38fcc0f9ad3

REQUIREMENTS:
  115

RANGE:
  REQ-B5-001 .. REQ-B5-115

REQUIREMENT ACCEPTANCE EVIDENCE:
  17415bbd1469bf25748d6a9e4850e4ad86404d35

RM-B5-01..09:
  ALL CLOSED

REQUIREMENTS STATE:
  ACCEPTED
  FROZEN

EXECUTION GOVERNANCE:
  EXCLUDED

B5 EXECUTION MANDATE:
  AUTHORIZED FOR PRODUCTION
  NOT YET ISSUED

B5 IMPLEMENTATION:
  NOT AUTHORIZED

NEXT AUTHORIZED ARTIFACT:
  B5_CASE_GOVERNANCE_EXECUTION_MANDATE_v0.md
```

## 20. Stop condition

**STOP.** Do not create the Execution Mandate in the same task. Do not create a candidate branch, modify code, modify migrations, modify tests, or reinterpret the frozen requirements.

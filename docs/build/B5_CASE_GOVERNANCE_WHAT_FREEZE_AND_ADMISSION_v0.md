# CPL — B5 Case Governance WHAT Freeze and Build Unit Admission v0

## Purpose

This artifact performs the formal transition:

```text
CPL_CG
  PRE-ADMISSION
        ↓
B5_CASE_GOVERNANCE
  ADMITTED
  WHAT_FROZEN
  REQUIREMENTS AUTHORIZED
```

It does exactly three things: declares the accepted WHAT canonical, admits the Build Unit as `B5`, and authorizes the Requirements phase. It does **not** produce requirements and does **not** authorize implementation.

---

## 1. Canonical baselines

```text
Governance HEAD before this freeze:
  e9618ee88a1a9d9898daee5f5f8830875267a8b0

Accepted WHAT:
  docs/build/CPL_CG_WHAT_v0.1.md
  SHA: f53fce8f0c79aa3b5f041a964883ab8283671584

Re-Challenge:
  docs/build/CPL_CG_WHAT_RECHALLENGE_v0.1.md
  SHA: e9618ee88a1a9d9898daee5f5f8830875267a8b0

Re-Challenge verdict:
  WHAT_ACCEPTED

Re-Challenge findings:
  REPAIR-01 CLOSED
  REPAIR-02 CLOSED
  REPAIR-03 CLOSED
  REPAIR-04 CLOSED
  NON-REGRESSION PASS
  Case/Execution split PRESERVED
  Build Structure PRESERVED
  GAP-01..04 NON-BLOCKING
```

---

## 2. Freeze decision

The semantic content of `docs/build/CPL_CG_WHAT_v0.1.md` is frozen as the canonical WHAT for `B5_CASE_GOVERNANCE`. The accepted WHAT is no longer merely pre-admission material.

```text
CPL_CG_WHAT_v0.1
  WHAT_ACCEPTED
        ↓
B5_CASE_GOVERNANCE
  WHAT_FROZEN
  BUILD_UNIT_ADMITTED
```

---

## 3. Build Unit identity

```text
BUILD UNIT:
  B5_CASE_GOVERNANCE

Canonical semantic name:
  Case Governance

Previous pre-admission identifier:
  CPL_CG
```

The pre-admission artifacts (`CPL_CG_WHAT_v0.md`, `CPL_CG_WHAT_CHALLENGE_v0.md`, `CPL_CG_WHAT_v0.1.md`, `CPL_CG_WHAT_RECHALLENGE_v0.1.md`) remain part of governance history and MUST NOT be renamed or rewritten.

---

## 4. Frozen scope

The frozen B5 Build Unit governs the existing CPL Case surface:

```text
Case
CaseParticipant
CaseEvent
```

It excludes:

```text
RunnerExecution
RunnerArtifact
generalized Occurrence
generalized Evidence
generalized Actor/Role
generic State engine
Organization/Membership
workflow/BPMN engine
universal event sourcing
frontend
billing
domain-specific VIR/PGDR semantics
```

`RunnerExecution` and `RunnerArtifact` remain assigned to the later Execution Governance Build Unit.

---

## 5. Frozen structural decision

The canonical build ordering is:

```text
B5_CASE_GOVERNANCE
        ↓
EXECUTION_GOVERNANCE
```

This ordering is justified by semantic/governance boundary dependency, **not** merely by schema foreign keys.

```text
SCHEMA DEPENDENCY
  ≠
SEMANTIC DEPENDENCY
  ≠
GOVERNANCE DEPENDENCY
  ≠
BUILD-ORDER DEPENDENCY
```

---

## 6. Frozen execution-pointer boundary

Within B5 Case Governance:

```text
Case.current_execution_id
CaseEvent.execution_id
```

remain opaque references.

B5 MUST NOT govern:

```text
RunnerExecution lifecycle
RunnerExecution status semantics
execution lineage
parent_execution_id semantics
execution correction/supersession
execution-domain truth
full execution-history navigation
```

These belong to the later Execution Governance Build Unit.

---

## 7. Frozen Asset anchoring

Current B5 Case semantics are Asset-anchored.

```text
Case.asset_id remains NOT NULL.
```

Asset-optional Case is OUT OF SCOPE for B5. The B5 requirements phase MUST NOT relax this constraint unless a separately authorized future WHAT changes the semantic boundary.

---

## 8. Open but non-blocking gaps

The following remain explicitly OPEN and NON-BLOCKING:

```text
GAP-01
Case-to-Case consolidation / merge semantics

GAP-02
CaseEvent semantic classification mechanism

GAP-03
Case / CaseEvent correction-supersession substrate shape

GAP-04
canonical ontology vocabulary vs physical table name
```

```text
OPEN
  ≠
UNCONTROLLED
```

Requirements may refine implementation obligations only within the frozen semantic boundary. Requirements MUST NOT silently decide a new WHAT. If a GAP requires semantic expansion, the requirements process must raise `GOVERNANCE_DEVIATION`/`WHAT_REVISION_REQUIRED` rather than invent the answer.

---

## 9. Requirements authorization

Upon successful materialization of this freeze:

```text
AUTHORIZED:
B5 Case Governance Requirement Matrix generation
```

Naming convention now becomes:

```text
B5_CASE_GOVERNANCE_...
```

Expected next artifact:

```text
docs/build/B5_CASE_GOVERNANCE_REQUIREMENT_MATRIX_v0.md
```

Requirements may:

```text
operationalize frozen semantics
define verification criteria
identify schema/service requirements
specify correction/history mechanisms where permitted
define CaseEvent classification obligations if needed
```

Requirements may NOT:

```text
expand B5 ontology
make Asset optional
absorb RunnerExecution/RunnerArtifact governance
create generic workflow/event/state/actor systems
redefine B1-B4 semantics
resolve open WHAT questions through silent design choices
```

---

## 10. Implementation status

Implementation remains:

```text
NOT AUTHORIZED
```

No candidate branch. No schema change. No migration. No production code. No test implementation.

Required sequence:

```text
B5 WHAT Freeze / Admission
        ↓
B5 Requirement Matrix
        ↓
Requirement Challenge
        ↓
Repair / Re-Challenge if needed
        ↓
Requirements Freeze
        ↓
Execution Mandate
        ↓
Build
```

---

## 11. Canonical status after freeze

```text
B5_CASE_GOVERNANCE

Build Unit:
  ADMITTED

WHAT:
  ACCEPTED
  FROZEN

Requirements:
  AUTHORIZED TO DEFINE
  NOT YET FROZEN

Implementation:
  NOT AUTHORIZED

Execution Governance:
  SUBSEQUENT BUILD UNIT
  NOT YET AUTHORIZED
```

---

## 12. Prohibitions

DO NOT:

```text
edit CPL_CG_WHAT_v0.1.md
edit CPL_CG_WHAT_RECHALLENGE_v0.1.md
rename historical CPL_CG artifacts
generate requirements inside this freeze artifact
modify schema
create migrations
modify production code
create candidate branch
begin Execution Governance
merge Case and Execution Governance
silently resolve GAP-01..04 beyond the frozen WHAT
```

---

## 13. Final status

```text
B5_CASE_GOVERNANCE
================================

SOURCE WHAT:
  f53fce8f0c79aa3b5f041a964883ab8283671584

SOURCE RE-CHALLENGE:
  e9618ee88a1a9d9898daee5f5f8830875267a8b0

RE-CHALLENGE VERDICT:
  WHAT_ACCEPTED

BUILD UNIT:
  B5_CASE_GOVERNANCE

BUILD UNIT STATUS:
  ADMITTED

WHAT STATUS:
  FROZEN

REQUIREMENTS:
  AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED

NEXT AUTHORIZED ARTIFACT:
  B5_CASE_GOVERNANCE_REQUIREMENT_MATRIX_v0.md
```

## 14. Stop condition

**STOP.** Do not create the Requirement Matrix in the same task.

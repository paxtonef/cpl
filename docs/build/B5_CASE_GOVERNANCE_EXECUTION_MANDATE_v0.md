# CPL — B5 Case Governance Execution Mandate v0

## Purpose

This artifact authorizes implementation of the already-frozen B5 Case Governance WHAT and Requirements. It does not redesign B5, does not reinterpret frozen requirements, and does not absorb Execution Governance.

---

## 1. Canonical governance state

```text
Governance HEAD:
  57efa8e57dce2021a7e94969ff6e4036ff24ccf6

Build Unit:
  B5_CASE_GOVERNANCE

WHAT state:
  FROZEN

Frozen WHAT source:
  f53fce8f0c79aa3b5f041a964883ab8283671584

WHAT acceptance evidence:
  e9618ee88a1a9d9898daee5f5f8830875267a8b0

WHAT Freeze / Build Unit Admission:
  85cb0b18876faf81eb89906236b87e959056a66a

Requirements state:
  ACCEPTED
  FROZEN

Frozen Requirement Matrix:
  docs/build/B5_CASE_GOVERNANCE_REQUIREMENT_MATRIX_v0.2.md

Frozen requirement baseline:
  a36d9e8c2ca7a435e9cd7e1ec97ee38fcc0f9ad3

Requirement acceptance evidence:
  17415bbd1469bf25748d6a9e4850e4ad86404d35

Requirements Freeze:
  57efa8e57dce2021a7e94969ff6e4036ff24ccf6

Requirement count:
  115

Requirement range:
  REQ-B5-001 .. REQ-B5-115

RM-B5-01 .. RM-B5-09:
  ALL CLOSED
```

---

## 2. Build authorization

Upon issuance of this Execution Mandate:

```text
B5 IMPLEMENTATION:
  AUTHORIZED
```

Authorized candidate branch:

```text
b5-case-governance-candidate
```

The implementation team MAY now construct a candidate satisfying `REQ-B5-001` .. `REQ-B5-115` against the frozen B5 WHAT and frozen requirements. This authorization applies ONLY to `B5_CASE_GOVERNANCE`.

---

## 3. Build baseline

The coding system MUST build from the canonical CPL software baseline, not from an arbitrary governance HEAD.

```text
Canonical pre-B5 software baseline:
  1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628
```

This is the integrated B4 software baseline.

```text
Current migration head:
  025
```

The governance commits after B4 are normative documentation and MUST be available for the build, but MUST NOT be mistaken for an already implemented software baseline. Therefore:

```text
GOVERNANCE HEAD
  57efa8e57dce2021a7e94969ff6e4036ff24ccf6

≠

CODE BUILD BASELINE
  1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628
```

The candidate branch MUST preserve access to the frozen governance artifacts while basing implementation changes on the existing B4 software state.

---

## 4. Authorized implementation scope

B5 governs only:

```text
1. Case
2. CaseParticipant
3. CaseEvent
```

Implementation may include the minimum required changes to: models; migrations; repositories; services; domain/application logic; authority evaluation integration; idempotency support; history/correction support; semantic classification support; verification/test infrastructure; traceability artifacts.

ONLY where required by `REQ-B5-001` .. `REQ-B5-115`.

---

## 5. Existing B2 substrate

Existing schema objects already include: `Case`, `CaseParticipant`, `CaseEvent`, `RunnerExecution`, `RunnerArtifact`.

B5 MUST govern the existing Case-side substrate. Do NOT replace it with a newly invented generic Occurrence model. Do NOT introduce a parallel Case primitive merely because the old B2 objects were weakly governed.

```text
The build objective is:

UNGOVERNED / UNDER-GOVERNED EXISTING CASE SUBSTRATE
        ↓
B5-GOVERNED CASE SUBSTRATE
```

---

## 6. Execution Governance exclusion

The following remain OUT OF SCOPE:

```text
RunnerExecution lifecycle
RunnerExecution status semantics
RunnerExecution success/failure semantics
RunnerExecution lineage
parent_execution_id governance
RunnerExecution correction/supersession
RunnerArtifact governance
complete execution history
```

`Case.current_execution_id` and `CaseEvent.execution_id` may be preserved and used only as B5-side opaque references according to the frozen requirements.

```text
REFERENCE EXISTS
  ≠
EXECUTION VALIDATED
  ≠
DOMAIN ASSERTION VALIDATED
```

---

## 7. Case Asset anchoring

Implementation MUST preserve `Case.asset_id NOT NULL`. Every B5 Case is Asset-anchored. Post-creation rebinding of a Case from Asset A to Asset B is prohibited.

Implementation MUST NOT silently introduce: nullable `Case.asset_id`; Contact-only Case; Case-to-Case merge; Case Asset reassignment workflow; Asset survivor selection. Any such requirement is outside this mandate.

---

## 8. Case identity

Case has stable CPL identity. Case identity MUST remain distinct from: Asset identity; Contact identity; external identifiers; domain assertions; CaseEvent identity; RunnerExecution identity.

A Case MUST NOT acquire a new CPL identity merely because: metadata changes; status changes; participants change; events are added; correction occurs; execution reference changes.

---

## 9. CaseParticipant

Preserve `CaseParticipant ≠ ContactAssetRelationship`. Participation is Case-scoped. Being a participant does NOT itself authorize Case mutation.

Preserve `ROLE ≠ AUTHORITY ≠ PERMISSION ≠ IDENTITY`. Do NOT generalize B5 into an Actor/Role platform.

---

## 10. CaseEvent

CaseEvent remains an append-oriented CPL Case representation. Preserve `WORLD EVENT ≠ DOMAIN ASSERTION ≠ CPL OPERATIONAL FACT ≠ CANONICAL DECISION CONSEQUENCE`.

CaseEvent MUST NOT become a universal event primitive. Each governed `event_type` must have a determinable semantic class. The exact implementation mechanism is HOW. Do NOT require a generic event ontology unless independently required by the frozen requirements.

---

## 11. Event time

Implementation MUST preserve independently `CaseEvent.occurred_at` and `CaseEvent.created_at`.

```text
OCCURRENCE / REPORTED TIME
  ≠
CPL RECORDING TIME
```

Example required in verification: event occurred yesterday, event recorded today. Both values remain distinguishable and queryable.

---

## 12. Case lifecycle

Case status is CPL operational metadata.

```text
CASE STATUS
  ≠
DOMAIN STATE
  ≠
WORLD STATE
```

A Case marked `CLOSED` does NOT mean: Asset repaired; Asset safe; diagnosis correct; repair successful; claim approved; real-world matter resolved. No domain truth may be inferred from Case lifecycle alone.

---

## 13. Governed authority

Material Case mutations requiring authority MUST pass governed authority evaluation. The implementation MAY reuse existing CPL authority infrastructure where appropriate. It MUST NOT treat participant role, `actor_type`, or request source as sufficient authority by themselves. No specific implementation class is mandated by the frozen WHAT.

---

## 14. Canonical operation pipeline

Where a governed material Case mutation requires a canonical decision, the implementation must preserve the accepted logical sequence:

```text
REQUEST / INTENT
        ↓
AUTHORITY EVALUATION
        ↓
CANONICAL DECISION
        ↓
GOVERNED EFFECT
        ↓
HISTORY / TRACE
```

Failure at an earlier stage MUST NOT fabricate completion of a later stage. Examples: authority denial → no fabricated successful decision; decision persistence failure → no fabricated effect; effect failure → no fabricated successful history.

---

## 15. Failure semantics

Implementation MUST distinguish: `AUTHORITY_REJECTION`, `SEMANTIC_REJECTION`, `UNRESOLVED`, `CONFLICT`, `TECHNICAL_FAILURE`.

Examples: authority policy denies close → `AUTHORITY_REJECTION`; attempt to rebind Case Asset → `SEMANTIC_REJECTION`; required governing fact not determinable → `UNRESOLVED`; two authoritative inputs incompatible → `CONFLICT`; database unavailable → `TECHNICAL_FAILURE`.

Technical failure MUST NOT be represented as governed rejection.

---

## 16. Idempotency

Material governed operations must support replay discipline.

```text
SAME PAYLOAD
  ≠
SAME OPERATION IDENTITY
```

Replay of an already completed operation using the same operation identity MUST avoid duplicate canonical effect, and return or make deterministically retrievable the original outcome. Different operation identity with identical payload MUST NOT automatically be treated as replay.

---

## 17. History and correction

Implementation MUST preserve `CORRECTION ≠ DELETION OF HISTORY`. Current operational state and historical reconstruction must remain distinct. Corrections must preserve sufficient provenance to reconstruct prior state and subsequent correction. Do NOT introduce destructive history rewriting.

---

## 18. Open gap discipline

The following remain intentionally unresolved at semantic level:

```text
GAP-01  Case consolidation / merge
GAP-02  exact storage mechanism for CaseEvent semantic classification
GAP-03  exact correction/supersession persistence mechanism
GAP-04  canonical vocabulary vs physical table naming
```

Implementation may choose HOW only where the frozen requirements permit implementation freedom. Implementation MUST NOT convert an open mechanism question into new semantic policy.

---

## 19. Migration discipline

```text
Current migration head:
  025
```

Any B5 migrations MUST be: forward-only; additive or safely transformational; reversible where the project migration policy requires it; compatible with existing B1–B4 data model semantics. Historical migrations MUST NOT be edited. New migration numbers must follow `025` sequentially. The developer MUST report final migration head.

---

## 20. Test requirements

The candidate MUST include verification sufficient to demonstrate `REQ-B5-001` .. `REQ-B5-115`.

Existing B1–B4 regression suite MUST remain passing. Last verified pre-B5 regression baseline: **152 / 152**.

The candidate MUST NOT weaken or delete prior tests to obtain a pass. Real PostgreSQL verification is mandatory for persistence semantics. Mock-only verification is insufficient.

---

## 21. Required adversarial tests

At minimum verify:

```text
A. Case identity remains stable after lifecycle changes.
B. Case.asset_id cannot be changed Asset A → Asset B.
C. CaseParticipant role alone cannot authorize Case closure.
D. CaseEvent does not become canonical decision authority.
E. CASE_CLOSED does not imply repaired/safe/successful.
F. Case can record opaque execution reference without interpreting execution status.
G. Technical DB failure is not recorded as governed rejection.
H. Same operation identity replay does not duplicate canonical effect.
I. Replay makes original outcome deterministically retrievable.
J. Same payload under different operation identity is not automatically replay.
K. occurred_at and created_at may differ.
L. CaseEvent semantic class is determinable without arbitrary payload interpretation.
M. Correction preserves historical reconstruction.
N. Execution Governance semantics are not introduced.
```

---

## 22. Traceability

The developer MUST produce traceability from `REQ-B5-001` .. `REQ-B5-115` to implementation, tests, and migration/schema changes where applicable. No requirement may be silently omitted.

Final candidate report MUST state `115 / 115 requirements traced` or identify an explicit governance deviation.

---

## 23. Governance deviation rule

If implementation discovers that a frozen requirement is ambiguous, contradictory, impossible, semantically incomplete, or in conflict with frozen WHAT:

STOP that affected implementation path. Report `GOVERNANCE_DEVIATION`. Do NOT reinterpret the requirement in code. Do NOT silently change requirement meaning. Do NOT modify frozen governance artifacts from the candidate branch.

---

## 24. Developer Build Plan

Before coding, developer must produce an internal Build Plan covering: affected components; anticipated migrations; service/repository changes; authority handling; idempotency implementation; correction/history implementation; tests; dependency risks; scope exclusions.

Build Plan is execution planning. It MUST NOT redefine WHAT or Requirements.

---

## 25. Candidate branch

Authorized branch: `b5-case-governance-candidate`. No implementation work may be merged directly into main. Candidate branch must remain independently retrievable.

---

## 26. Candidate completion gate

Before handoff to DevOps, developer must provide: candidate SHA; candidate tree SHA; branch name; base SHA; migration head; changed-file list; test count; test result; PostgreSQL version/environment; requirement traceability count; governance deviations, if any; known limitations, if any.

---

## 27. Required candidate status

Developer may return only one build status: `CANDIDATE_COMPLETE`, `BUILD_BLOCKED`, `GOVERNANCE_DEVIATION`.

`CANDIDATE_COMPLETE` requires: implementation complete; tests pass; real PostgreSQL verification pass; 115/115 traceability; no unresolved governance deviation; candidate SHA pinned.

---

## 28. Independent verification

`CANDIDATE_COMPLETE` does NOT mean `ACCEPTED`. The candidate must be handed to independent DevOps verification. DevOps must independently retrieve the exact candidate SHA and verify: SHA/tree identity; clean checkout; migrations; real PostgreSQL; B1–B4 regression; B5 tests; authority behavior; idempotency; history/correction; failure semantics; temporal distinction; execution boundary; adversarial scenarios; requirement traceability.

---

## 29. DevOps verdicts

Independent DevOps may return: `ACCEPT_CANDIDATE`, `REPAIR_REQUIRED`, `REJECT_CANDIDATE`, `GOVERNANCE_DEVIATION`. Developer may NOT self-issue `ACCEPT_CANDIDATE`.

---

## 30. Merge prohibition

Do NOT merge candidate into main before `ACCEPT_CANDIDATE` from independent verification.

```text
Candidate SHA
  ≠
verified SHA
  ≠
integrated main SHA
```

even if candidate SHA is ultimately the verified content.

---

## 31. Integration

After independent `ACCEPT_CANDIDATE`, integration into main becomes authorized. Integration must preserve: governance artifacts on main; accepted candidate implementation; zero unauthorized implementation delta.

If no-fast-forward merge is required because governance main advanced after code baseline, verify candidate-to-integrated implementation delta explicitly.

---

## 32. Closure

Integration does NOT itself close B5. After successful integration and regression verification, a B5 Closure artifact is required. Only B5 Closure may declare `B5_CASE_GOVERNANCE CLOSED` and authorize structuring of the next Build Unit.

---

## 33. Authorized state transition

This Execution Mandate performs:

```text
REQUIREMENTS_FROZEN
        ↓
EXECUTION_MANDATE_ISSUED
        ↓
BUILD_ALLOWED
```

It does NOT perform: `BUILD_COMPLETE`, `VERIFY_ACCEPT`, `INTEGRATED`, `CLOSED`.

---

## 34. Final mandate summary

```text
B5_CASE_GOVERNANCE_EXECUTION_MANDATE_v0
=======================================

BUILD UNIT:
  B5_CASE_GOVERNANCE

GOVERNANCE HEAD:
  57efa8e57dce2021a7e94969ff6e4036ff24ccf6

CODE BUILD BASELINE:
  1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628

FROZEN WHAT:
  f53fce8f0c79aa3b5f041a964883ab8283671584

FROZEN REQUIREMENTS:
  a36d9e8c2ca7a435e9cd7e1ec97ee38fcc0f9ad3

REQUIREMENTS:
  115

RANGE:
  REQ-B5-001 .. REQ-B5-115

MIGRATION BASELINE:
  025

AUTHORIZED CANDIDATE BRANCH:
  b5-case-governance-candidate

EXECUTION GOVERNANCE:
  EXCLUDED

EXECUTION MANDATE:
  ISSUED

B5 IMPLEMENTATION:
  AUTHORIZED

MERGE TO MAIN:
  NOT AUTHORIZED

NEXT EXECUTION STATE:
  BUILD_ALLOWED
```

## 35. Stop condition

**STOP.** Do not implement B5 in the same task, create the candidate branch, modify production code, modify migrations, modify tests, perform candidate verification, or merge anything into main.

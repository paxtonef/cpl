# CPL_EA_WHAT_FREEZE_AND_ADMISSION_v0

## 1. Governance decision

```text
WHAT_FREEZE:            GRANTED
BUILD_UNIT_ADMISSION:   GRANTED
```

Required consistency check (§21 of the governing instruction) performed against the actual committed lineage, not from memory:

```text
v0.1 exists at stated lineage:                         CONFIRMED
Re-Challenge references v0.1:                            CONFIRMED
Re-Challenge verdict = WHAT_RECHALLENGE_ACCEPTED:          CONFIRMED
WHAT_FREEZE_READINESS = READY:                              CONFIRMED
REQUIREMENTS_READINESS = READY:                               CONFIRMED
R-EA-W01..05 all CLOSED:                                        CONFIRMED
No governance conflict recorded:                                 CONFIRMED
UNIT_COHESION = PASS:                                              CONFIRMED
POST_EA_COMMON_BLOCKER = NONE:                                       CONFIRMED
CPL_MINIMUM_FOR_VIR_PGDR_REACHED = YES_AFTER_THIS_UNIT:                CONFIRMED
```

All conditions pass. Freeze and admission proceed.

---

## 2. Canonical baselines

```text
Governance HEAD (input):          3eb76f115a9052a2a2861a71180e56f25a571981
Canonical CPL software baseline:  2ac075daea7d162825ed73ded0c7548011242a8f
Migration head:                    026
```

---

## 3. Evidence lineage

```text
Product-Gap Structuring:      6bacabf2d4ac6fca0630c7e7b883840cabda6eca
Build Structure Challenge:    0f79e1df07fa1761488857e06c96cb01a78ed763 (BUILD_STRUCTURE_ACCEPTED)
Pre-admission WHAT v0:          3a775a5f2b589dd7e526733bcff3c65edf84f4b9
WHAT Challenge:                  ed1d18099a5e6cb09758522e739f4178eec62c27 (WHAT_REPAIR_REQUIRED)
Repaired WHAT v0.1:               e7d51842043408cccd97bf3811de73c756784849
Targeted Re-Challenge:             3eb76f115a9052a2a2861a71180e56f25a571981 (WHAT_RECHALLENGE_ACCEPTED)
```

---

## 4. Frozen WHAT identification

```text
Canonical frozen WHAT:
  docs/build/CPL_EA_WHAT_v0.1.md

at commit:
  e7d51842043408cccd97bf3811de73c756784849
```

The Re-Challenge does not replace the WHAT — it is the acceptance evidence that authorizes freezing `v0.1`. The frozen artifact is `v0.1` itself.

---

## 5. Build Unit admission

```text
CPL_EA (pre-admission candidate)
        ↓
WHAT accepted
        ↓
WHAT frozen
        ↓
Build Unit admitted
        ↓
B6_EXECUTION_ARTIFACT_GOVERNANCE
```

Pre-admission artifacts are **not** retroactively renamed. Their historical names remain `CPL_EA_*` exactly as committed.

---

## 6. B6 canonical identity

```text
Build Unit:            B6 — Execution / Artifact Governance
Canonical identifier:  B6_EXECUTION_ARTIFACT_GOVERNANCE
```

---

## 7. B6 purpose

B6 provides the minimum common CPL governance required to represent bounded runner execution instances and their produced artifacts while preserving the authority boundary between common canonical representation and domain truth. B6 governs the common representation of `RunnerExecution` and `RunnerArtifact`, and only the semantic relations required by the frozen WHAT.

---

## 8. Frozen scope

```text
IN SCOPE:
  RunnerExecution
  RunnerArtifact
  the semantic relation between them
  their attachment to already-governed Case (B5) and Asset (B4)
  their attribution to an initiating Contact (B3)
```

---

## 9. Explicit exclusions

B6 does NOT become authority over:

```text
VIR vehicle-identity determination      PGDR diagnosis
domain assertions                        domain determinations
domain result validity                    runner internals
workflow orchestration                     scheduling
generic agent execution                     generic evidence
product presentation semantics
```

Preserved:

```text
DOMAIN DETERMINES DOMAIN TRUTH
CPL GOVERNS COMMON CANONICAL REPRESENTATION
```

---

## 10. RunnerExecution boundary

`RunnerExecution` is a stable CPL representation of a distinct governed runner execution occurrence/instance (`v0.1` §6, §6a). Frozen distinctions:

```text
EXECUTION ≠ REQUEST
EXECUTION ≠ AUTHORIZATION
EXECUTION ≠ CASE
EXECUTION ≠ CASE EVENT
EXECUTION ≠ DOMAIN OPERATION
EXECUTION ≠ DOMAIN RESULT

NEW EXECUTION ATTEMPT → NEW RUNNEREXECUTION
```

subject to governed replay retrieving an already-existing execution rather than creating a new attempt.

---

## 11. RunnerArtifact boundary

`RunnerArtifact` is a stable CPL representation of an artifact associated with a `RunnerExecution` under the frozen WHAT (`v0.1` §10). Preserved:

```text
ARTIFACT ≠ DOMAIN TRUTH
ARTIFACT ≠ ASSERTION
ARTIFACT ≠ EVIDENCE
PAYLOAD ≠ SEMANTIC CLASS
CONTENT HASH ≠ ARTIFACT IDENTITY
PROVENANCE ≠ VALIDITY
```

`v0.1` is referenced as authoritative; not restated in full here.

---

## 12. Artifact classification boundary

The WHAT freezes the conceptual orthogonality of artifact classification dimensions (`v0.1` §11, repaired via `R-EA-W02`):

```text
SEMANTIC FUNCTION ≠ PRODUCTION / LIFECYCLE ROLE ≠ CONSUMPTION / PRESENTATION ROLE
```

This does NOT freeze exact enum vocabulary. That operational vocabulary may be determined during Requirements within this frozen semantic boundary.

---

## 13. Existing-substrate treatment

```text
EXISTING SCHEMA ≠ FROZEN ONTOLOGY
```

But executable constraints discovered during WHAT investigation are not ignored. In particular, `runner_executions_idempotency_uq` is an existing enforced implementation fact (independently re-verified against the actual migration during both the WHAT Challenge and its Re-Challenge, not merely asserted).

---

## 14. idempotency disposition

The frozen WHAT establishes:

```text
IDEMPOTENCY KEY ≠ RUNNEREXECUTION IDENTITY
IDEMPOTENCY KEY ≠ INPUT IDENTITY
IDEMPOTENCY KEY ≠ DOMAIN OPERATION IDENTITY
```

The exact operational idempotency contract (scope confirmation, duplicate-submission behavior, retrieval behavior, conflict behavior, retry interaction) remains Requirements work.

---

## 15. parent_execution_id disposition

Frozen: `parent_execution_id` is existing substrate but is **not** assigned canonical B6 semantics by the frozen WHAT. It must not be treated as canonical proof of any of:

```text
retry            replay
continuation       delegation
dependency           correction
derivation
```

```text
PARENT POINTER EXISTS ≠ PARENT SEMANTICS ARE KNOWN
```

Requirements may not silently invent those semantics.

---

## 16. History/correction boundary

```text
EXECUTION HISTORY ≠ GENERIC EXECUTION LINEAGE
CORRECTION OF EXECUTION REPRESENTATION ≠ REWRITING HISTORICAL EXECUTION OCCURRENCE
```

A genuine new execution attempt requires a new `RunnerExecution`. Representation correction must preserve historical truth. Domain-result correction remains outside B6 domain authority.

---

## 17. Frozen invariant registry reference

The candidate invariant registry is frozen exactly as represented in `docs/build/CPL_EA_WHAT_v0.1.md` §28 — not reconstructed here from memory, not renumbered:

```text
Active invariants:  19 (EA-CI01..13, 15..19)
Retired:             EA-CI14, merged into EA-CI03 (retirement explicit,
                     not silently restored, not silently deleted)
```

`v0.1` itself is the canonical source for the exact invariant text.

---

## 18. BS-EA / EA-WG disposition

Carried forward exactly as `v0.1` and its accepted Re-Challenge established — not reinterpreted here:

```text
BS-EA-01  RESOLVED (0:N multiplicity confirmed)
BS-EA-02  REPAIRED — existing substrate, semantic interpretation
          explicitly outside CPL_EA v0.1 unless future demonstrated need
BS-EA-03  SEMANTIC CORE PARTIALLY RESOLVED IN WHAT + OPERATIONAL
          CONTRACT OPEN FOR REQUIREMENTS
BS-EA-04  PARTIALLY ADDRESSED — domain-acceptance reading excluded;
          exact meaning REQUIREMENTS
BS-EA-05  OPEN — semantic need acknowledged, no field designed;
          REQUIREMENTS / HOW
BS-EA-06  CLOSED FOR CPL'S WHAT — correctly out of CPL's authority;
          DOMAIN INTEGRATION

EA-WG-01  OPEN — HOW (mechanism choice; dimension-mixing entanglement
          resolved by R-EA-W02)
EA-WG-02  OPEN — HOW
EA-WG-03  OPEN — REQUIREMENTS
```

No later phase may reinterpret frozen WHAT semantics. Requirements may resolve Requirements-level questions; HOW may resolve HOW-level questions; Domain Integration may resolve domain-integration questions; Product may resolve product questions.

---

## 19. EA-WRC-01/02 treatment

Carried forward exactly as recorded in `CPL_EA_WHAT_RECHALLENGE_v0.1.md`:

```text
EA-WRC-01  NON-BLOCKING (§6a's identity-negation list omits explicit
           mention of Asset/artifact; no practical ambiguity found)
EA-WRC-02  NON-BLOCKING (idempotency-identity non-equivalence present
           in body prose but not mirrored as a standalone invariant
           bullet)
```

Not silently repaired in this artifact. Not promoted to blockers without new evidence.

---

## 20. Requirements authorization

```text
REQUIREMENTS_CONSTRUCTION: AUTHORIZED
```

This authorizes creation of `B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.md`. Requirements must derive from `CPL_EA_WHAT_v0.1`, its frozen invariant registry, and the explicitly deferred Requirements-level questions named above — not invented independently of them.

---

## 21. Implementation prohibition

```text
IMPLEMENTATION:      NOT AUTHORIZED
EXECUTION_MANDATE:    NOT AUTHORIZED
CANDIDATE_BRANCH:      NOT AUTHORIZED
SCHEMA_CHANGE:          NOT AUTHORIZED
MIGRATION:               NOT AUTHORIZED
CODE_CHANGE:              NOT AUTHORIZED
```

Requirements must first be constructed, challenged, repaired if necessary, re-challenged, and frozen — the same full cycle B5's Case Governance requirements went through.

---

## 22. Software-baseline preservation

```text
Canonical CPL software baseline:  2ac075daea7d162825ed73ded0c7548011242a8f (UNCHANGED)
Migration head:                    026 (UNCHANGED)
```

This governance act does not modify the software baseline.

```text
GOVERNANCE HEAD ≠ SOFTWARE BASELINE
```

---

## 23. CPL stopping condition

```text
CPL_MINIMUM_FOR_VIR_PGDR_REACHED = YES_AFTER_THIS_UNIT
```

Meaning: if B6 is successfully requirements-frozen → mandated → built → independently verified → integrated → closed, and no new evidence establishes another COMMON blocker, then CPL construction for the current VIR/PGDR product **stops**. The next construction frontier becomes: VIR integration → PGDR integration → Product/API → Frontend → Operational VIR/PGDR product. This does not declare CPL permanently complete — future demonstrated common needs may reopen CPL construction through a new governance action.

---

## 24. Governance lineage

```text
6bacabf2d4ac6fca0630c7e7b883840cabda6eca
  Product-Gap Structuring
        ↓
0f79e1df07fa1761488857e06c96cb01a78ed763
  Build Structure Challenge
        ↓
3a775a5f2b589dd7e526733bcff3c65edf84f4b9
  WHAT v0
        ↓
ed1d18099a5e6cb09758522e739f4178eec62c27
  WHAT Challenge
        ↓
e7d51842043408cccd97bf3811de73c756784849
  WHAT v0.1
        ↓
3eb76f115a9052a2a2861a71180e56f25a571981
  WHAT Re-Challenge
        ↓
<THIS FREEZE + ADMISSION COMMIT>
```

---

## 25. Admission boundary

Admission means: B6 exists as a governed Build Unit. Admission does NOT mean: requirements exist; implementation exists; schema is correct; existing `RunnerExecution` code is accepted; existing `RunnerArtifact` code is accepted; B6 is complete; CPL is complete.

```text
ONTOLOGY ACCEPTANCE ≠ IMPLEMENTATION ACCEPTANCE
```

---

## FINAL STATE

```text
CPL_EA_WHAT_FREEZE_AND_ADMISSION_v0
===================================

GOVERNANCE INPUT HEAD:
  3eb76f115a9052a2a2861a71180e56f25a571981

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

MIGRATION HEAD:
  026

FROZEN WHAT:
  docs/build/CPL_EA_WHAT_v0.1.md

FROZEN WHAT COMMIT:
  e7d51842043408cccd97bf3811de73c756784849

WHAT RE-CHALLENGE:
  ACCEPTED

WHAT FREEZE:
  GRANTED

BUILD UNIT ADMISSION:
  GRANTED

CANONICAL BUILD UNIT:
  B6_EXECUTION_ARTIFACT_GOVERNANCE

BUILD UNIT STATUS:
  ADMITTED

REQUIREMENTS CONSTRUCTION:
  AUTHORIZED

REQUIREMENTS STATUS:
  NOT YET CONSTRUCTED

EXECUTION MANDATE:
  NOT AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED

SOFTWARE BASELINE:
  UNCHANGED

POST-EA COMMON BLOCKER:
  NONE

CPL_MINIMUM_FOR_VIR_PGDR_REACHED:
  YES_AFTER_THIS_UNIT

NEXT GOVERNANCE ACTION:
  B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0
```

## STOP

**STOP.** No Requirement Matrix created in this artifact, no requirements challenged, no Execution Mandate, no candidate branch, no schema modification, no migration, no code modification, no VIR/PGDR modification. B6 is not declared complete. CPL is not declared permanently complete.

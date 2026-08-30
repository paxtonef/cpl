# CPL — B2 Closure & B3 Authorization Decision v0

**System:** VIR PGDR # COMMON PRODUCT LAYER — CPL
**Decision Artifact:** Build Closure & Next-Phase Authorization
**Version:** v0
**Date:** 2026-08-30
**Repository:** `paxtonef/cpl`
**Canonical branch:** `main`
**B1 Closure Commit:** `8638a71d610ad0c84bc2912949e2ab2b6881cde9`
**B2 Candidate Branch:** `b2-candidate`
**B2 Verified Candidate:** `36263fa5c9b18ded911917d726f6331182765849`

---

## 0. Provenance Correction

An earlier draft of this decision referenced commit
`080053340bab5819cc6e8555347f8cadb927f938` as the accepted B2 candidate.
That commit was never independently verifiable: repeated `git ls-remote`
and `git fetch` checks against `https://github.com/paxtonef/cpl.git`
confirmed it did not exist under any ref, and GitHub's own server
returned `not our ref` on direct fetch attempts across four separate
verification rounds.

The B2 candidate was therefore rebuilt from scratch — cloned from the
real, verified `main` @ `8638a71`, with the full set of R1 and R2 repair
content applied, committed, pushed, and independently re-verified via a
completely fresh `git clone` from GitHub. That rebuilt commit,
`36263fa5c9b18ded911917d726f6331182765849`, is the one referenced
throughout this corrected document. `0800533...` does not appear as an
accepted identity anywhere below and must not be treated as canonical in
any prior draft.

---

## 1. Decision

```text
B2 DECISION:
  ACCEPTED / CLOSED

B2 VERIFIED CANDIDATE:
  36263fa5c9b18ded911917d726f6331182765849

B3:
  AUTHORIZED BY GOVERNANCE DECISION
  NOT YET IMPLEMENTED
  EXECUTION NOT YET AUTHORIZED
```

B2 — Database Foundation has satisfied the required implementation, execution-verification, non-regression, boundary-preservation and evidence obligations.

The B2 candidate is therefore accepted as the canonical B2 implementation candidate subject to canonical repository integration.

---

## 2. Canonical Build Lineage

The verified Git lineage is:

```text
e8b2b9b3e476958122fbcd95cb1efadf4a17174e
B1 Verified Implementation Baseline
        │
        ▼
8638a71d610ad0c84bc2912949e2ab2b6881cde9
B1 Closure / B2 Authorization
        │
        ▼
36263fa5c9b18ded911917d726f6331182765849
B2 Verified Candidate
```

Both ancestor checks were demonstrated successfully:

```text
git merge-base --is-ancestor e8b2b9b... 36263fa...  → exit 0
git merge-base --is-ancestor 8638a71... 36263fa...  → exit 0
```

B2 is therefore not a reconstructed or detached build. It is a genuine descendant of the canonical CPL history, independently confirmed via a fresh clone from `https://github.com/paxtonef/cpl.git`.

---

## 3. B2 Scope Closed

B2 materialized the CPL persistence foundation comprising:

```text
Contact
ContactPoint
Account

Asset
AssetIdentifier
ContactAssetRelationship

VehicleDetail

Case
CaseParticipant
CaseEvent

RunnerExecution
RunnerArtifact

AssetIdentityResolution
ExternalReference

Current-State Pointers
record_version
```

and associated:

```text
PostgreSQL schemas
tables
primary keys
foreign keys
CHECK constraints
UNIQUE constraints
partial UNIQUE indexes
operational indexes
SQLAlchemy models
Alembic migrations
positive verification scenarios
negative verification scenarios
```

B2 does not include B3 service behavior.

---

## 4. Migration Closure

Canonical migration chain:

```text
001  B1 Bootstrap
 ↓
002
003
004
005
006
007
008
009
010
011
012
013
014
015
016
017
018
```

Final verified state:

```text
018 (head)
```

Execution evidence (from independent fresh-clone verification):

```text
alembic upgrade head
→ PASS

alembic current
→ 018 (head)
```

Migration integrity is therefore accepted.

---

## 5. Runtime Verification

B2 was independently executed against real PostgreSQL 16, twice: once
against the locally-built candidate, and once against a completely
fresh `git clone` of `https://github.com/paxtonef/cpl.git` at
`b2-candidate`. It was also independently re-run and confirmed a third
time by the user directly, on a separate machine.

Application startup:

```text
PASS
```

Health endpoint:

```text
GET /health
HTTP 200

{"status":"ok","service":"cpl"}
```

Readiness with PostgreSQL available:

```text
GET /ready
HTTP 200

{"application":"ready","database":"reachable"}
```

Readiness with PostgreSQL unavailable:

```text
GET /ready
HTTP 503

{"application":"ready","database":"unreachable"}
```

These behaviors preserve the B1 runtime contract.

---

## 6. Verification Suite Closure

Final execution (confirmed independently in two separate environments):

```text
60 collected
60 passed
0 failed
0 errors
```

Mandatory B2 scenarios:

```text
P01–P20
20 / 20 PASS

N01–N24
24 / 24 PASS
```

B1 regression tests:

```text
PASS
```

The final verification also confirms the R2 repair for N03:

```text
Contact self-merge rejection
PASS
```

---

## 7. Repair History Incorporated

The accepted B2 candidate incorporates the following governed repairs.

### Repair R1

```text
R1-01
Migration 016 duplicate source_resolution_id declaration removed.
Existing M008 column preserved.
FK creation retained.

R1-02
B1 setuptools package-discovery configuration restored.
```

### Repair R2

```text
R2-01
/health B1 contract restored:
"service": "cpl"

R2-02
/ready database check made compatible with B1 test/runtime behavior.

R2-03
N03 SQLAlchemy expired-object/autoflush issue corrected through
bounded test assignment ordering.
```

No additional R3 repair was required.

---

## 8. B2 Gate Decision

Final gate disposition:

| Gate                                   | Decision |
| -------------------------------------- | -------- |
| G-B2-01 — Normative Schema Conformance | **PASS** |
| G-B2-02 — Migration Integrity          | **PASS** |
| G-B2-03 — Relational Integrity         | **PASS** |
| G-B2-04 — Identity Integrity           | **PASS** |
| G-B2-05 — Relationship Integrity       | **PASS** |
| G-B2-06 — Persistence / Restart        | **PASS** |
| G-B2-07 — B1 Non-Regression            | **PASS** |
| G-B2-08 — Boundary Preservation        | **PASS** |
| G-B2-09 — Evidence Completeness        | **PASS** |

Therefore:

```text
B2_GATE_RESULT = PASS
```

---

## 9. Known Non-Blocking Observations

The following warnings remain non-blocking:

```text
OBS-B1-01
Starlette / HTTPX TestClient deprecation

OBS-B1-02
Pydantic class-based Config deprecation

OBS-B1-03
SQLAlchemy transaction deassociation warning
```

Additional observed Alembic deprecation warning:

```text
No path_separator found in configuration
```

These observations do not prevent B2 closure.

They are not implicitly authorized for remediation by this document.

---

## 10. Boundary Preservation

B2 verification confirms that the candidate did not implement unauthorized:

```text
VIR execution
Vehicle PGDR execution
authentication workflows
frontend
diagnostic reasoning
B3 service behavior
later CPL orchestration
```

The generic CPL Asset boundary remains preserved.

Automotive remains a specialization rather than the definition of CPL Asset.

---

## 11. B2 Acceptance

The following states are now established:

```text
B2_IMPLEMENTATION_COMPLETE
B2_VERIFICATION_COMPLETE
B2_GATES_PASS
B2_ACCEPTED
B2_CLOSED
```

Canonical accepted candidate:

```text
B2_ACCEPTED_CANDIDATE =
36263fa5c9b18ded911917d726f6331182765849
```

---

## 12. Canonical Repository Integration

B2 acceptance authorizes integration of the verified B2 candidate into the canonical CPL history.

The candidate to integrate is exactly:

```text
36263fa5c9b18ded911917d726f6331182765849
```

No post-verification code modification may be silently introduced during integration.

If the content of the commit changes, the resulting object is no longer the verified B2 candidate and requires renewed verification.

Integration performed via `git merge --ff-only`, preserving the exact
verified commit identity on `main` with no rewrite.

---

## 13. B3 Governance Decision

B3 is now:

```text
AUTHORIZED BY GOVERNANCE DECISION
```

This means CPL may proceed to specification and handoff preparation for B3.

It does **not** mean that a developer may begin coding B3 immediately.

Required transition:

```text
B2 CLOSED
   ↓
B3 WHAT / normative scope confirmed
   ↓
B3 Requirement Matrix
   ↓
B3 Execution Mandate
   ↓
B3 Developer Handoff
   ↓
B3 IMPLEMENTATION AUTHORIZED
```

Until those B3 execution artifacts exist:

```text
B3_IMPLEMENTATION = NOT AUTHORIZED
```

---

## 14. B3 Boundary

Based on the established build sequence, B3 is:

```text
B3 — Identity + Accounts
```

B3 may build behavior on top of the persistence structures established by B2.

B3 SHALL NOT reopen or redesign the B2 persistence foundation unless a formally identified defect requires governed revision.

---

## 15. B2 Freeze Rule

The accepted B2 implementation becomes the persistence baseline for subsequent CPL phases.

Therefore:

```text
B2 schema semantics
B2 migration history
B2 identity boundaries
B2 historical persistence model
B2 generic Asset boundary
B2 Case / RunnerExecution distinction
```

are frozen for downstream development except through explicit governed change.

---

## 16. Closure Invariants

### CPL-B2-C-I01 — Verified candidate identity

B2 closure applies specifically to commit:

```text
36263fa5c9b18ded911917d726f6331182765849
```

### CPL-B2-C-I02 — Evidence precedes closure

B2 is closed because runtime verification demonstrated conformance —
independently, against real PostgreSQL, from a fresh clone of the real
repository — not because implementation was merely produced or described.

### CPL-B2-C-I03 — B1 remains preserved

B2 closure does not supersede or invalidate the B1 closure.

### CPL-B2-C-I04 — Repair history remains traceable

R1 and R2 remain part of B2 build history and must not be erased from historical evidence. The Section 0 provenance correction likewise remains part of the historical record and must not be erased.

### CPL-B2-C-I05 — No implicit B3 execution

Authorization of the B3 phase does not itself authorize coding.

### CPL-B2-C-I06 — Candidate mutation invalidates verification identity

Any modification after `36263fa` creates a new candidate requiring appropriate verification.

---

## 17. Final State

```text
CPL BUILD STATE

B1
  ACCEPTED
  CLOSED

B2
  IMPLEMENTED
  VERIFIED
  ACCEPTED
  CLOSED

B2 ACCEPTED CANDIDATE
  36263fa5c9b18ded911917d726f6331182765849

B3
  GOVERNANCE AUTHORIZED
  NOT YET IMPLEMENTED
  EXECUTION MANDATE NOT YET ISSUED

B4+
  NOT AUTHORIZED
```

# GOVERNANCE DECISION

> **CPL B2 — Database Foundation is ACCEPTED and CLOSED.**

> **Commit `36263fa5c9b18ded911917d726f6331182765849` is the accepted B2 candidate.**

> **B3 — Identity + Accounts is authorized as the next CPL build phase, but implementation shall not begin until its own governed execution handoff is issued.**

**End of `CPL — B2 Closure & B3 Authorization Decision v0`**

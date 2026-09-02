# CPL — B3 Closure & B4 Authorization Decision v0

**System:** VIR PGDR # COMMON PRODUCT LAYER — CPL
**Decision Artifact:** Build Closure & Next-Phase Authorization
**Version:** v0
**Date:** 2026-09-02
**Repository:** `paxtonef/cpl`
**Canonical branch:** `main`
**B2 Closure Commit:** `4b83425828a2e8fd08bec568fc8937a830396ec4`
**B3 Candidate Branch:** `b3-candidate`
**B3 Verified Candidate:** `f03179066d55c01a8248f18b578fa6795fb81347`

---

## 0. Provenance

Unlike B2, B3's candidate identity was never in doubt at any point —
`f031790` was independently verified via fresh clone, fresh empty
database, and full-chain migration testing (`CPL_B3_FINAL_DEVOPS_EXECUTION_EVIDENCE_REPORT.md`)
before this closure document was drafted. There is no provenance
correction required here, unlike the B2 closure record.

---

## 1. Decision

```text
B3 DECISION:
  ACCEPTED / CLOSED

B3 VERIFIED CANDIDATE:
  f03179066d55c01a8248f18b578fa6795fb81347

B4:
  AUTHORIZED BY GOVERNANCE DECISION
  NOT YET IMPLEMENTED
  EXECUTION NOT YET AUTHORIZED
```

B3 — Identity + Accounts has satisfied the required WHAT freeze,
Requirement Matrix freeze, Execution Mandate, implementation,
independent DevOps verification, and evidence obligations.

The B3 candidate is therefore accepted as the canonical B3
implementation and integrated into canonical `main` via fast-forward
merge, preserving the exact verified commit identity.

---

## 2. Canonical Build Lineage

```text
e8b2b9b   B1 implementation
8638a71   B1 closure / B2 authorization
36263fa   B2 implementation
4b83425   B2 closure / B3 authorization
1b98d65…c764073   B3 WHAT + Requirement Matrix governance chain
74d0426   B3 Requirement Matrix frozen
7f43cf7   B3 Execution Mandate issued (Build Boundary crossed)
f031790   B3 verified implementation candidate
        │
        ▼
main @ f031790 (post fast-forward merge)
```

Ancestry independently confirmed:

```text
git merge-base --is-ancestor 7f43cf7 f031790   → exit 0
```

---

## 3. B3 Scope Closed

B3 materialized the CPL identity service layer comprising the 14
frozen primitives:

```text
get_contact, resolve_contact, create_contact
add_contact_point, verify_contact_point,
invalidate_contact_point, set_primary_contact_point
attach_account, resolve_authenticated_contact,
disable_account, revoke_account
detect_duplicate_contact, propose_merge, merge_contacts
```

and associated forward-only persistence:

```text
migrations 019-021
identity_operations (durable provenance)
merge_proposals (durable PROPOSE_MERGE artifact)
contact_point_verifications (Verification Assertion log)
contact_creation_requests (creation idempotency ledger)
```

B3 does not include authentication implementation, authorization
platform implementation, Asset identity resolution, Case lifecycle,
or Runner execution.

---

## 4. Execution Evidence

```text
Migration chain 001 → 021: verified from a genuinely empty database
alembic current: 021 (head)

pytest: 106 passed / 0 failed / 0 errors / 0 skipped
  B1 regression:     16/16
  B2 regression:     44/44
  B3 positive:       22/22
  B3 negative:       16/16
  B3 transaction:     3/3
  B3 traceability:    3/3
  B3 concurrency:     2/2

/health, /ready: unchanged from B1/B2 baseline
```

---

## 5. B3 Gate Result

| Gate | Result |
|---|---|
| G-B3-01 Baseline verification | PASS |
| G-B3-02 Branch discipline | PASS |
| G-B3-03 Migration preservation (001-018) | PASS |
| G-B3-04 Forward migration integrity | PASS |
| G-B3-05 Fourteen primitives, no 15th | PASS |
| G-B3-06 No generic CRUD escape hatch | PASS |
| G-B3-07 One canonical resolution semantics | PASS |
| G-B3-08 Account authority ladder | PASS |
| G-B3-09 Merge directionality / self-merge rejection | PASS |
| G-B3-10 Merge source preservation | PASS |
| G-B3-11 Related-object reconciliation matrix | PASS |
| G-B3-12 Merge idempotency | PASS |
| G-B3-13 Durable provenance | PASS |
| G-B3-14 No authentication implementation | PASS |
| G-B3-15 B1/B2 non-regression | PASS |
| G-B3-16 Requirement evidence completeness | **PARTIAL (disclosed, independently confirmed accurate)** |

```text
B3_GATE_RESULT = 15 PASS / 1 PARTIAL (disclosed)
```

---

## 6. Known Non-Blocking Observations

Carried forward from B1/B2:

```text
OBS-B1-01   Starlette / HTTPX TestClient deprecation
OBS-B1-02   Pydantic class-based Config deprecation
OBS-B1-03   SQLAlchemy transaction deassociation warning
```

New for B3:

```text
OBS-B3-01
invalidate_contact_point (REQ-B3-020) has no dedicated test.
Enforced in code; not yet exercised by a named test scenario.

OBS-B3-02
Per-authority-class denial is directly tested for CREATE_CONTACT
and AUTHORIZE_MERGE/EXECUTE_MERGE only, not all 11 authority
classes individually. The underlying mechanism (AuthorityContext.require())
is uniform across all 14 primitives.

OBS-B3-03
No HTTP/API transport layer was built for B3. The frozen WHAT
explicitly leaves transport open; this is scope, not a defect.

OBS-B3-04
Concurrency test coverage (2 of 4 suggested families: C-B3-02,
C-B3-04) is representative, not exhaustive.
```

These observations do not block B3 closure. They are not implicitly
authorized for remediation by this document.

---

## 7. Boundary Preservation

Independently confirmed absent from the B3 candidate:

```text
authentication implementation (password/OAuth/JWT/session)
authorization platform implementation
VIR execution
Vehicle PGDR execution
frontend
Asset identity resolution
Case lifecycle implementation
B4 or later phase work
```

---

## 8. B3 Acceptance

```text
B3_IMPLEMENTATION_COMPLETE
B3_VERIFICATION_COMPLETE
B3_GATES_PASS (15/16 full, 1/16 disclosed partial)
B3_ACCEPTED
B3_CLOSED
```

Canonical accepted candidate:

```text
B3_ACCEPTED_CANDIDATE =
f03179066d55c01a8248f18b578fa6795fb81347
```

---

## 9. Canonical Repository Integration

Integration performed via `git merge --ff-only`, preserving the
exact verified commit identity on `main` with no rewrite:

```text
git checkout main
git merge --ff-only b3-candidate
```

The candidate to integrate is exactly `f031790`. No post-verification
code modification may be silently introduced during integration. If
the content changes, the resulting object is no longer the verified
B3 candidate and requires renewed verification.

---

## 10. B4 Governance Decision

```text
B4:
  AUTHORIZED BY GOVERNANCE DECISION
```

This authorizes CPL to proceed to specification and handoff
preparation for B4. It does not itself authorize a developer to
begin coding B4.

Required transition, mirroring the discipline established for B3:

```text
B3 CLOSED
   ↓
B4 WHAT / normative scope confirmed
   ↓
B4 Requirement Matrix
   ↓
B4 Execution Mandate
   ↓
B4 Developer Handoff
   ↓
B4 IMPLEMENTATION AUTHORIZED
```

Until those B4 execution artifacts exist:

```text
B4_IMPLEMENTATION = NOT AUTHORIZED
```

---

## 11. B3 Freeze Rule

The accepted B3 implementation becomes the identity-service baseline
for subsequent CPL phases:

```text
14 primitive operations
resolution semantics (F-B3-05)
authority ladder (ASSESS -> PROPOSE -> AUTHORIZE -> EXECUTE)
related-object reconciliation matrix (RM-O01)
Verification Assertion minimum contract
durable provenance obligation
```

are frozen for downstream development except through explicit
governed change.

---

## 12. Closure Invariants

### CPL-B3-C-I01 — Verified candidate identity
B3 closure applies specifically to commit `f031790`.

### CPL-B3-C-I02 — Evidence precedes closure
B3 is closed because independent, adversarial-posture DevOps
verification (fresh clone, fresh empty database, full migration
chain, 106/106 tests) demonstrated conformance — not because
implementation was merely produced or self-reported.

### CPL-B3-C-I03 — B1/B2 remain preserved
B3 closure does not supersede or invalidate the B1 or B2 closures.

### CPL-B3-C-I04 — Disclosed gaps remain part of the record
OBS-B3-01 through OBS-B3-04 remain part of B3's historical evidence
and must not be silently erased in future documentation.

### CPL-B3-C-I05 — No implicit B4 execution
Authorization of the B4 phase does not itself authorize coding.

### CPL-B3-C-I06 — Candidate mutation invalidates verification identity
Any modification after `f031790` creates a new candidate requiring
appropriate re-verification.

---

## 13. Final State

```text
CPL BUILD STATE

B1   ACCEPTED / CLOSED
B2   ACCEPTED / CLOSED
B3   ACCEPTED / CLOSED

B3 ACCEPTED CANDIDATE
  f03179066d55c01a8248f18b578fa6795fb81347

B4
  GOVERNANCE AUTHORIZED
  NOT YET IMPLEMENTED
  EXECUTION MANDATE NOT YET ISSUED

B5+
  NOT AUTHORIZED
```

## Closure Record Commit

```text
B3_CLOSURE_RECORD_COMMIT = <filled in after this file is committed>
```

# GOVERNANCE DECISION

> **CPL B3 — Identity + Accounts is ACCEPTED and CLOSED.**

> **Commit `f03179066d55c01a8248f18b578fa6795fb81347` is the accepted B3 candidate, merged into `main` via fast-forward.**

> **B4 is authorized as the next CPL build phase, but implementation shall not begin until its own governed execution handoff is issued.**

**End of `CPL — B3 Closure & B4 Authorization Decision v0`**

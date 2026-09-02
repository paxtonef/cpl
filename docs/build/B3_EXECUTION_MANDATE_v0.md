# CPL — B3 Execution Mandate v0

**System:** Common Product Layer — CPL
**Build Phase:** B3 — Identity + Accounts
**Artifact:** Execution Mandate
**Version:** v0
**Canonical baseline:** `main @ 74d042637595a4d5cd357304327d1212365153d0`

**Frozen upstream authority:**

* `B3_IDENTITY_OBJECT_AUTHORITY_MAP_v0.md`
* `B3_IDENTITY_RESOLUTION_STATE_DECISION_MODEL_v0.md`
* `B3_SERVICE_BOUNDARY_AND_OPERATION_CONTRACT_v0.1.md`
* `B3_WHAT_CONSOLIDATION_AND_FREEZE_v0.md`
* `B3_WHAT_FREEZE_CHALLENGE_v0.md` — FREEZE_ACCEPTED, 24/24 PASS
* `B3_REQUIREMENT_MATRIX_v0.md` + `v0.1`
* `B3_REQUIREMENT_CHALLENGE_v0.md` — REPAIR_REQUIRED (bounded)
* `B3_REQUIREMENT_MATRIX_RE_CHALLENGE_v0.1.md` — PASS, 6/6, Requirement Matrix FROZEN

---

## 1. Purpose

This is the single artifact that crosses the Build Boundary.

Before this document:

```text
WHAT definition
requirement transformation
challenge
repair
re-challenge
```

were all legitimate governance activity.

None of them authorized a single line of application code, a migration, or a test.

This document, once materialized, does exactly one thing:

> **It authorizes a developer to begin B3 implementation, strictly bounded to what is frozen above, and to nothing else.**

It does not re-derive the WHAT. It does not re-litigate the Requirement Matrix. It packages the frozen state into an actionable, self-contained instruction.

---

# 2. What is authorized

```text
B3 IMPLEMENTATION
  AUTHORIZED

Scope:
  the 14 frozen primitive operations
  the 125 frozen requirements (REQ-B3-001 → REQ-B3-125)
  the frozen related-object reconciliation matrix
  the frozen Verification Assertion minimum contract
  the frozen durable provenance obligation
  the frozen same-logical-creation idempotency rule
```

Nothing else is authorized by this document.

---

# 3. What is explicitly NOT authorized

```text
B3 WHAT modification
Requirement Matrix modification
new primitive operations
B2 schema modification (unless a requirement demonstrably
   requires a narrowly-scoped, separately justified migration)
B1 runtime contract modification
authentication implementation
authorization/RBAC platform implementation
frontend
Asset identity resolution
Case lifecycle implementation
Runner execution (VIR, PGDR)
merge into main without passing DevOps verification
B4 or later phase work
```

Any implementation activity touching the above requires a separate, explicit governance decision — not an inference from this mandate.

---

# 4. Canonical starting point

Implementation MUST begin from a clean checkout of:

```text
main @ 74d042637595a4d5cd357304327d1212365153d0
```

This is the same commit already independently verified (via GitHub-exported zip, cross-checked against prior `git ls-remote`/`git clone` verification) to contain:

```text
B1 implementation      (e8b2b9b lineage)
B1 closure              (8638a71)
B2 implementation       (36263fa) — 60/60 tests passing
B2 closure               (4b83425)
B3 WHAT artifacts        (1b98d65 → c79be82)
B3 WHAT freeze            (f1a340c, 6002ec8)
B3 Requirement Matrix     (1eebe57 → 74d0426)
```

No implementation work may branch from an earlier or divergent commit.

---

# 5. Required branch discipline

Implementation MUST occur on a dedicated branch, not directly on `main`:

```text
b3-candidate
```

following the same pattern already established and verified for B2 (`b2-candidate` → independently DevOps-verified → merged via fast-forward into `main`).

`main` MUST NOT be modified directly during B3 implementation.

---

# 6. Developer instruction — primitive implementation order

The 14 primitives SHOULD be implemented in an order that respects their dependency structure, not alphabetically or by convenience:

```text
Phase 1 — Foundation reads
  01 get_contact
  02 resolve_contact

Phase 2 — Contact creation
  03 create_contact

Phase 3 — ContactPoint lifecycle
  04 add_contact_point
  05 verify_contact_point
  06 invalidate_contact_point
  07 set_primary_contact_point

Phase 4 — Account binding
  08 attach_account
  09 resolve_authenticated_contact
  10 disable_account
  11 revoke_account

Phase 5 — Reconciliation (highest risk, implement last)
  12 detect_duplicate_contact
  13 propose_merge
  14 merge_contacts
```

Phase 5 MUST NOT begin until Phases 1–4 are individually passing their assigned requirements.

---

# 7. Developer instruction — requirement traceability

Every unit of implementation work (a function, an endpoint, a service method — whatever the developer's chosen architecture calls it) MUST be traceable to one or more `REQ-B3-*` identifiers.

Commit messages, PR descriptions, or code comments SHOULD reference the relevant `REQ-B3-*` IDs being satisfied. This is not bureaucratic overhead — it is what allows DevOps to verify against the Requirement Matrix rather than against the developer's own description of what they built, which is exactly the failure mode this entire B2 verification saga existed to prevent.

---

# 8. Developer discretion — explicitly confirmed

Per `B3_REQUIREMENT_MATRIX_RE_CHALLENGE_v0.1.md` §7 and `B3_WHAT_FREEZE_CHALLENGE_v0.md` §24, the developer retains full discretion over:

```text
API transport (REST/RPC/internal)
endpoint paths and naming
Python class/module architecture
repository pattern
locking mechanism
transaction isolation level
idempotency storage mechanism
provenance storage schema
serialization format
logging/observability implementation
deployment mechanics
```

The developer MUST NOT re-derive or second-guess:

```text
what identity means
whether resolution mutates
whether duplicate detection authorizes merge
whether a disabled Account resolves current identity
whether Contact merge preserves the source
which relationship families preserve vs. reassociate on merge
what a Verification Assertion must minimally contain
whether provenance must survive process restart
whether similarity alone justifies treating two creation
   requests as the same request
```

These are frozen. If the developer believes one of them is wrong, the correct action is a **WHAT Change Request** or **Requirement Change Request**, not silent reinterpretation during implementation.

---

# 9. Test authorship requirement

The developer MUST produce a test suite covering, at minimum:

```text
P-B3-01 → P-B3-26   (positive scenarios, per Requirement Matrix v0.1 §8)
N-B3-01 → N-B3-35   (negative scenarios, per Requirement Matrix v0.1 §8)
C-B3-01 → C-B3-04   (concurrency scenarios)
T-B3-01 → T-B3-05   (transaction scenarios)
TR-B3-01 → TR-B3-08 (traceability scenarios)
```

against real PostgreSQL — not mocked persistence — consistent with the verification discipline already established and repeatedly enforced during B2's multi-round DevOps verification.

All existing B1 and B2 tests (60/60 as of `36263fa`) MUST continue to pass. This is REQ-B3-087 and REQ-B3-088, not optional.

---

# 10. DevOps verification requirement — non-negotiable

Per the established and repeatedly-validated pattern from B2:

```text
DevOps does NOT trust developer self-certified PASS claims as evidence.
```

Before any B3 candidate can be considered for acceptance, DevOps MUST independently:

1. Verify the candidate commit genuinely exists on the real repository (`git ls-remote` / fresh `git clone` — not a pasted description, not a checksum manifest, not a reconstruction from chat text).
2. Verify package installation succeeds from a clean environment.
3. Run `alembic upgrade head` against real PostgreSQL and confirm the resulting schema.
4. Run the full test suite (B1 + B2 + B3) against real PostgreSQL and report exact pass/fail counts.
5. Spot-check that primitive behavior matches its `REQ-B3-*` obligations, not merely that a test with a matching name exists and passes.
6. Confirm B1/B2 non-regression explicitly (not by assumption).
7. Confirm boundary preservation — no VIR/PGDR/auth/frontend/Asset/Case scope introduced.
8. Produce a written DevOps Execution Evidence Report with an explicit verdict: `B3_ACCEPTANCE_RECOMMENDED` or `B3_NOT_ACCEPTED`.

This mandate explicitly anticipates that a first candidate MAY fail this verification, exactly as B2's did across multiple rounds (a genuine migration defect and a genuine `/health`/`/ready` regression were both caught this way, not by self-report). That is the system working correctly, not a failure of process.

---

# 11. Merge conditions

`b3-candidate` may be merged into `main` only when:

```text
DevOps verdict = B3_ACCEPTANCE_RECOMMENDED
      AND
merge is performed via git merge --ff-only
      (preserving the exact verified commit identity,
      no rebase, no squash, no rewrite)
      AND
a B3 Closure & B4 Authorization document is subsequently
      materialized into docs/build/, following the same
      pattern established for B1 → B2 closure
```

Acceptance recommendation alone does not constitute closure — the same distinction already established and honored throughout B1 and B2 governance (`B2_ACCEPTANCE_RECOMMENDED ≠ B2_CLOSED`).

---

# 12. What this mandate does not decide

This mandate does not decide:

```text
which programming patterns to use
how many files to create
what the internal module structure looks like
whether to use synchronous or asynchronous database access
which testing framework beyond "must exercise real PostgreSQL"
```

These are legitimate engineering decisions explicitly left open by the frozen WHAT and frozen Requirement Matrix, and this mandate does not narrow them further.

---

# 13. Governance status upon materialization

```text
B3 WHAT
  FROZEN

B3 Requirement Matrix
  FROZEN

B3 Execution Mandate
  ISSUED

B3 Implementation
  AUTHORIZED
  (bounded strictly to Sections 2–9 above)

B3 DevOps Verification
  REQUIRED BEFORE ANY ACCEPTANCE

B3 Closure
  NOT YET GRANTED

B4
  NOT AUTHORIZED
```

---

# 14. Authorized transition

```text
B3 Execution Mandate v0
        │
        │  MATERIALIZED
        ▼
════════════════════════════
      BUILD BOUNDARY
════════════════════════════
        │
        ▼
  b3-candidate branch
        │
        ▼
  Developer implementation
  (Sections 6–9 above)
        │
        ▼
  Independent DevOps Verification
  (Section 10 above)
        │
   ┌────┴────┐
   │         │
 REJECT   ACCEPT
   │         │
repair    merge --ff-only
   │         │
   └──┐      ▼
      │  B3 Closure & B4 Authorization
      │      │
      └──────┘
```

## END — CPL B3 Execution Mandate v0

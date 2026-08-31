# CPL — B3 Requirement Matrix Re-Challenge v0.1

**System:** Common Product Layer — CPL
**Phase:** B3 — Identity + Accounts
**Artifact challenged:** `B3_REQUIREMENT_MATRIX_v0.1.md`
**Canonical baseline:** `c7640736249a9c9a8e3277990e898f27f00eff33`
**Challenge scope:** BOUNDED — RC-01 through RC-06 only
**Full WHAT re-analysis:** NOT REPEATED

---

## 1. Challenge scope discipline

Per the governing sequence established in `B3_REQUIREMENT_MATRIX_v0.1.md` §16, this Re-Challenge does not repeat the full B3 WHAT analysis already closed by `B3_WHAT_FREEZE_CHALLENGE_v0.md` (24/24 PASS) nor the full requirement-structure analysis already closed by `B3_REQUIREMENT_CHALLENGE_v0.md` (22/22 PASS).

It answers exactly six questions.

---

# 2. RC-01 — Were all four authorized repairs incorporated?

Checked against `B3_REQUIREMENT_CHALLENGE_v0.md` §26 repair scope:

```text
RM-O01  Related-object reconciliation
RM-O02  Verification Assertion Minimum Contract
RM-O03  Durable Provenance Minimum Obligation
RM-O04  Same Logical Contact Creation
```

Found in `v0.1`:

```text
RM-O01 → REQ-B3-101 through REQ-B3-115 (§3), plus §7 matrix
RM-O02 → REQ-B3-116 through REQ-B3-120 (§4)
RM-O03 → REQ-B3-121 through REQ-B3-123 (§5)
RM-O04 → REQ-B3-124 through REQ-B3-125 (§6)
```

Each closure section explicitly states the applicable relationship family or contract element and ends with an explicit `CLOSED` marker matching the Challenge's own closure language.

**VERDICT: PASS**

---

# 3. RC-02 — Did the repair remain within its authorization boundary?

The Challenge explicitly withheld authorization for:

```text
Python implementation
FastAPI endpoints
new migrations
schema changes
service classes
repositories
locking strategy
API design
RBAC implementation
verification provider
merge engine
B3 tests
```

Inspection of `v0.1` §12 ("HOW-leakage check") confirms the repair explicitly disclaims:

```text
FastAPI route structure
Python class architecture
repository pattern
SQL locking mechanism
transaction isolation level
queue technology
API transport
serialization format
audit-table schema
event-store technology
RBAC platform
authentication provider
verification provider
LLM provider
```

No requirement in REQ-B3-101→125 selects a concrete technology, framework, or storage mechanism. Each closure states an observable obligation (e.g., "MUST make recoverable," "MUST NOT manufacture," "MUST default to") rather than a mechanism.

**VERDICT: PASS**

---

# 4. RC-03 — Were REQ-B3-001 → 100 preserved?

`v0.1` §2 ("Normative continuity") explicitly states that all 100 original requirements "remain normative and retain their identifiers and meanings," and that v0.1 "does not renumber them."

Cross-referencing §8 ("Updated verification obligations") and §11 ("Non-regression declaration"), the new material is additive only — new positive scenarios (P-B3-19→26), new negative scenarios (N-B3-27→35), one new transaction scenario (T-B3-05), and three new traceability scenarios (TR-B3-06→08), none of which contradict or replace the original 18/26/4/4/5 families from `v0`.

No requirement text from `REQ-B3-001` through `REQ-B3-100` was found reproduced with altered wording inside `v0.1` — the original document remains the authoritative source for those IDs, and `v0.1` only extends.

**VERDICT: PASS**

---

# 5. RC-04 — Do REQ-B3-101 → 125 accurately encode the Challenge closures?

Spot-checking the highest-risk closure (merge-related reconciliation, RM-O01) against the Challenge's own per-family determinations:

| Family | Challenge default (§5-9 of Challenge) | v0.1 requirement default |
|---|---|---|
| Accounts | REASSOCIATE | REQ-B3-101: REASSOCIATE |
| ContactPoints | REASSOCIATE (conditional) | REQ-B3-105: REASSOCIATE where admissible |
| ContactAssetRelationships | PRESERVE | REQ-B3-110: PRESERVE |
| CaseParticipants | PRESERVE | REQ-B3-112: PRESERVE |
| ExternalReferences | PRESERVE | REQ-B3-114: PRESERVE |

All five match exactly, including the asymmetry between Accounts/ContactPoints (REASSOCIATE-default) and the other three (PRESERVE-default) — this asymmetry was the single most important determination in the Challenge and it transferred correctly rather than being flattened into one uniform rule.

The RM-O04 closure (REQ-B3-124/125) correctly preserves the Challenge's narrow scope: it defines creation-idempotency identity without smuggling in a general fuzzy-matching identity system, matching Challenge §17-20 precisely.

**VERDICT: PASS**

---

# 6. RC-05 — Did the repair introduce contradiction, HOW capture, or new semantic ambiguity?

### Contradiction check

No requirement in `v0.1` conflicts with a frozen WHAT invariant (`B3-X-I01` through `B3-X-I08`, `B3-SB-I01` through `B3-SB-I16`). In particular:

- REQ-B3-106 (verification preservation during reassociation) correctly reinforces rather than weakens F-B3-04 (verification mechanism remains external).
- REQ-B3-104 (Account REJECT_CONFLICT blocks merge) correctly reinforces F-B3-09 (reconciliation conflicts may block merge) rather than introducing a new override path.

### HOW capture check

Already addressed under RC-02. No new finding.

### New ambiguity check

One point requires explicit note rather than blocking: REQ-B3-109 introduces a "DEFER boundary" for ContactPoints using the qualitative test "does not make the surviving current identity misleading." This is intentionally qualitative — the Challenge itself (§6, ContactPoints closure) used equivalent qualitative language ("only where current identity correctness is not compromised"). This is consistent handoff to the Requirement Matrix's own §3 principle (current correctness + historical truth), not a new ambiguity introduced by the repair. It remains appropriately a downstream test-design question, not a WHAT or Requirement-level gap.

**VERDICT: PASS** (with the above noted, non-blocking)

---

# 7. RC-06 — Can the repaired matrix now be frozen without requiring developers to invent product semantics?

Applying the same developer-decision-leakage test used in `B3_WHAT_FREEZE_CHALLENGE_v0.md` §24:

A developer implementing B3 from `v0` + `v0.1` combined must still decide:

```text
locking mechanism
transaction isolation level
API transport
serialization format
storage schema for provenance
verification provider integration
```

A developer must **not** need to decide, and — per this review — is no longer required to decide:

```text
which relationship families preserve vs. reassociate history
      → closed by §7 matrix

what a Verification Assertion must minimally contain
      → closed by REQ-B3-116

whether provenance must survive process restart
      → closed by REQ-B3-121

whether name/email similarity alone justifies treating
two creation requests as the same request
      → closed by REQ-B3-125
```

These were exactly the four gaps identified as blocking in the original Requirement Challenge. All four are now closed at the semantic level.

**VERDICT: PASS**

---

# 8. Re-Challenge Scoreboard

| Check | Result |
|---|---|
| RC-01 — Repairs incorporated | PASS |
| RC-02 — Repair authorization boundary respected | PASS |
| RC-03 — REQ-B3-001→100 preserved | PASS |
| RC-04 — Closures accurately encoded | PASS |
| RC-05 — No contradiction/HOW capture/new ambiguity | PASS |
| RC-06 — Developer semantic discretion eliminated | PASS |

**6 / 6 PASS**

---

# 9. Findings

```text
BLOCKING FINDINGS        = 0
MAJOR FINDINGS           = 0
REPAIR REQUIRED          = NO
```

One non-blocking observation carried forward (not a finding requiring repair):

**RC-OBS-01**
REQ-B3-109's DEFER boundary for ContactPoints uses qualitative
language consistent with the Requirement Matrix's own governing
principle (§3.1). This is appropriately left for downstream
test-design elaboration, not a gap requiring further Requirement
Matrix repair.

---

# 10. Final Re-Challenge Verdict

```text
CPL B3 REQUIREMENT MATRIX RE-CHALLENGE v0.1

RC-01  Repairs incorporated              PASS
RC-02  Authorization boundary respected  PASS
RC-03  Original requirements preserved   PASS
RC-04  Closures accurately encoded       PASS
RC-05  No contradiction / HOW capture    PASS
RC-06  Developer discretion eliminated   PASS

Blocking findings
    NONE

Further Requirement Matrix repair required
    NO

B3 REQUIREMENT MATRIX
    FROZEN

B3 Execution Mandate
    NOT YET ISSUED

B3 Implementation
    NOT AUTHORIZED
```

**RE-CHALLENGE: PASS**

---

# 11. Frozen Requirement Matrix boundary

Effective upon governance recording of this Re-Challenge, the following become frozen alongside the already-frozen B3 WHAT:

```text
REQ-B3-001 → REQ-B3-125 (125 normative requirements)

14 / 14 primitive coverage
20 / 20 RMO family coverage
0 unresolved requirement-resolution items

related-object reconciliation matrix (§7 of v0.1)
Verification Assertion minimum contract
durable provenance minimum obligation
same-logical-creation idempotency rule

RM-I01 → RM-I12 (all Requirement Matrix invariants)
```

Any future contradiction with this frozen requirement set must be classified as a **Requirement Change Request**, following the same change-control discipline established for the WHAT layer — not silently absorbed into implementation, test repair, or DevOps correction.

---

# 12. Authorized transition

```text
B3 Requirement Matrix v0.1
             │
             │  RE-CHALLENGE PASS
             ▼
╔═══════════════════════════╗
║  REQUIREMENT MATRIX FROZEN ║
╚═══════════════════════════╝
             │
             ▼
     B3 EXECUTION MANDATE
     (not yet issued)
             │
════════════════════════════
       BUILD BOUNDARY
════════════════════════════
             │
             ▼
      B3 IMPLEMENTATION
      (not authorized)
```

The next legitimate governance artifact is the **B3 Execution Mandate** — the document that, once issued, will authorize a developer to begin implementation against this frozen requirement set. It has not yet been produced.

**End of `CPL — B3 Requirement Matrix Re-Challenge v0.1`**

# CPL — B4 Requirement Matrix Re-Challenge v0.1

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Requirement Matrix Re-Challenge
**Version:** v0.1
**Status:** RE-CHALLENGE COMPLETED — REQUIREMENTS ACCEPTED
**Canonical baseline:** `main @ ae913f9`
**Challenged artifact:** `B4_REQUIREMENT_MATRIX_v0.1.md`
**Requirement range:** `REQ-B4-001 → REQ-B4-260`
**Frozen source:** `B4 WHAT = FROZEN`
**Implementation authorization:** NONE

---

## 1. Purpose

This re-challenge verifies that the four repairs authorized by `B4_REQUIREMENT_CHALLENGE_v0.md` have closed the identified gaps without:

```text
reopening B4 WHAT
altering REQ-B4-001 → REQ-B4-240
introducing forbidden HOW
creating new authority
weakening historical preservation
or producing new material requirement gaps
```

The four repairs under review are:

```text
RM-B4-01  Decision/effect consistency
RM-B4-02  Dependency-disposition closure
RM-B4-03  Canonical-transition idempotency
RM-B4-04  Historical/current navigation distinction
```

Acceptance requires all repairs to survive targeted challenge and the complete matrix to be sufficiently determinate for an Execution Mandate.

---

# 2. Re-Challenge baseline

Canonical chain:

```text
B4 WHAT
  ↓
Global Freeze Re-Challenge
  ↓
FREEZE_ACCEPTED
  ↓
B4 Requirement Matrix v0
  REQ-B4-001 → 240
  ↓
Requirement Challenge
  ↓
REPAIR_REQUIRED
  RM-B4-01 → RM-B4-04
  ↓
B4 Requirement Matrix v0.1
  REQ-B4-001 → 260
  ↓
THIS RE-CHALLENGE
```

No implementation evidence is being evaluated here.

This is a requirement-governance gate.

---

# 3. RC-B4-RM-01 — Can canonical decision and effect diverge?

## Attack

Assume an implementation performs an Asset merge:

```text
CanonicalAssetIdentityDecision persisted
        ↓
Asset canonical mutation fails
```

Could the matrix permit the decision to remain represented as successfully committed?

No.

`REQ-B4-242` explicitly prohibits this.

Reverse the failure:

```text
Asset canonical mutation succeeds
        ↓
CanonicalAssetIdentityDecision persistence fails
```

`REQ-B4-241` prohibits the mutation from becoming observably committed without durable consistency with its governing decision.

`REQ-B4-245` closes the partial-failure case generally.

The same protection exists for Relationship transitions through `REQ-B4-243 → 245`.

### Result

```text
RC-B4-RM-01 = PASS
RM-B4-01 = CLOSED
```

---

# 4. Does RM-B4-01 accidentally prescribe transactions?

No.

The requirements establish:

```text
observable committed consistency
```

but do not require:

```text
SQL transaction
distributed transaction
event sourcing
unit of work
saga
two-phase commit
specific locking mechanism
```

HOW remains open.

### Result

```text
HOW LEAKAGE = NO
```

---

# 5. RC-B4-RM-02 — Can merge execute with unresolved material dependencies?

## Attack

Assume:

```text
Asset A
Asset B

SAME_PHYSICAL_ASSET established

Identifiers disposition:
  known

Relationships disposition:
  known

ExternalReferences disposition:
  unknown

Cases disposition:
  unknown
```

Could CPL merge A/B because physical identity has already been established?

No.

`REQ-B4-246` requires explicit governed disposition for every materially relevant dependency family.

`REQ-B4-247` requires:

```text
missing safe disposition
        ↓
HOLD or REJECT
```

`REQ-B4-248` prohibits implicit default disposition.

Therefore:

```text
positive physical identity
≠
automatic canonical merge authorization
```

### Result

```text
RC-B4-RM-02 = PASS
RM-B4-02 = CLOSED
```

---

# 6. Dependency completeness attack

Could an implementation satisfy the requirement by examining only dependency families it already knows how to handle?

No.

The governing criterion is not:

```text
implemented dependency families
```

but:

```text
every dependency family materially capable
of affecting canonical safety
```

This prevents implementation capability from silently defining governance scope.

### Result

```text
PASS
```

---

# 7. Unknown dependency behavior

Suppose a new CPL dependency family appears later.

If it can materially affect canonical safety but has no defined disposition:

```text
UNKNOWN MATERIAL DEPENDENCY
        ↓
NO SAFE DISPOSITION
        ↓
HOLD / REJECT
```

The system therefore fails closed.

This is compatible with future CPL evolution without requiring B4 to enumerate all future dependency types.

### Result

```text
PASS
```

---

# 8. RC-B4-RM-03 — Can replay duplicate canonical transitions?

## Attack 1 — Asset merge

```text
Request K:
MERGE A + B

network response lost

client retries Request K
```

`REQ-B4-250` prohibits a second independent canonical merge transition.

PASS.

## Attack 2 — Asset correction

Same governed correction request is replayed.

`REQ-B4-251` prohibits a second independent correction transition.

PASS.

## Attack 3 — Relationship mutation

Replay of the same governed:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

request cannot create a second independent canonical relationship transition under `REQ-B4-252`.

PASS.

### Result

```text
RC-B4-RM-03 = PASS
RM-B4-03 = CLOSED
```

---

# 9. Payload-collision attack

Consider:

```text
K1 → MERGE A/B
K2 → MERGE A/B
```

with identical payloads but distinct governed operation identities.

Could the system automatically treat K2 as replay merely because the payload matches?

No.

`REQ-B4-254` explicitly prohibits payload similarity alone from establishing canonical-transition idempotency identity.

This prevents accidental suppression of legitimate separate operations.

### Result

```text
PASS
```

---

# 10. Replay identity preservation

Could replay generate a new decision object while claiming semantic idempotency?

Not as an independent canonical transition.

`REQ-B4-253` requires preservation of:

```text
original committed canonical decision identity
```

or semantically equivalent governed transition identity.

The implementation mechanism remains open.

### Result

```text
PASS
```

---

# 11. RC-B4-RM-04 — Can current navigation erase historical attribution?

## Attack

Initial state:

```text
Relationship R

Contact B
   │
   └── R ──→ Asset Y
```

Later canonical evolution:

```text
Contact B → Contact A
Asset Y   → Asset X
```

Suppose current queries expose only:

```text
Contact A ↔ Asset X
```

and no supported inspection can reconstruct:

```text
Contact B ↔ Asset Y
```

Would this satisfy v0.1?

No.

`REQ-B4-255 → 258` explicitly require the distinction and historical reconstructability.

### Result

```text
RC-B4-RM-04 = PASS
```

---

# 12. ExternalReference attack

Historical state:

```text
ExternalReference ER
external system target → Asset B
```

Later:

```text
Asset B → Asset A
```

Current navigation may resolve to Asset A.

But `REQ-B4-259` requires historical inspection to remain capable of showing that the external system originally referenced Asset B.

Therefore:

```text
historical external binding
≠
current CPL navigation
```

### Result

```text
RM-B4-04 = CLOSED
```

---

# 13. Historical preservation does not freeze navigation

Reverse attack:

Could the new requirements accidentally force every normal current query to return historical identities?

No.

`REQ-B4-257` explicitly permits current canonical relationship queries to resolve canonical successors without rewriting historical endpoints.

Therefore both semantics coexist:

```text
CURRENT NAVIGATION
        ↓
current canonical identity

HISTORICAL INSPECTION
        ↓
historical identity
```

### Result

```text
PASS
```

---

# 14. RC-B4-RM-05 — Did repairs introduce forbidden HOW?

Review of `REQ-B4-241 → 260` finds no requirement for:

```text
table structure
column structure
ORM representation
API endpoint
SQL locking
transaction isolation level
event bus
event sourcing
CQRS
bitemporal schema
cache architecture
specific idempotency-key format
specific dependency registry implementation
```

The additions constrain observable system behavior.

### Result

```text
RC-B4-RM-05 = PASS
```

---

# 15. RC-B4-RM-06 — Do repairs conflict with frozen WHAT?

Test each repair.

### RM-B4-01

Strengthens the already-frozen relationship between canonical decisions and canonical effects.

```text
CONFLICT = NO
```

### RM-B4-02

Operationalizes frozen dependency-disposition semantics.

```text
CONFLICT = NO
```

### RM-B4-03

Extends already-required governed idempotency to canonical mutation replay.

```text
CONFLICT = NO
```

### RM-B4-04

Makes the already-frozen distinction between historical attribution and current canonical navigation acceptance-testable.

```text
CONFLICT = NO
```

### Result

```text
RC-B4-RM-06 = PASS
WHAT_CONFLICT = NO
```

---

# 16. Did the repair create a new authority?

No.

Nothing in `REQ-B4-241 → 260` grants authority to:

```text
VIR
domain resolver
administrator
human operator
identifier
similarity mechanism
relationship evidence source
implementation subsystem
```

that did not already exist in frozen WHAT.

The core boundary remains:

```text
DOMAIN
  determines domain truth where authorized

CPL
  governs canonical CPL identity/state
```

### Result

```text
PASS
```

---

# 17. Did the repair weaken Asset merge admission?

No.

The opposite occurs.

The complete gate is now more explicit:

```text
positive identity determination
        ↓
merge admission
        ↓
survivor determinacy
        ↓
dependency-disposition closure
        ↓
canonical decision
        ↓
consistent canonical effect
```

Any missing mandatory condition prevents successful canonical merge.

### Result

```text
PASS
```

---

# 18. Did the repair create auto-merge through identifier equality?

No.

Nothing modifies the frozen rule:

```text
same VIN
same registration
same serial number
same external identifier
same similarity result
        ≠
merge authority
```

Identifier equality remains evidence/input to governed resolution, not canonical merge authority.

### Result

```text
PASS
```

---

# 19. Did the repair weaken ambiguity handling?

No.

The frozen rule remains:

```text
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
FAILED
        ↓
NO CANONICAL MERGE
```

The new dependency-disposition requirements add another legitimate reason to withhold merge even after positive identity resolution.

### Result

```text
PASS
```

---

# 20. Correction-after-merge attack

Consider:

```text
A + B merged
        ↓
A selected survivor
        ↓
later evidence establishes:
A and B were different physical Assets
```

The repaired requirements do not trap the system in the incorrect merge.

Frozen correction semantics remain normative.

Correction can restore independent canonical identities while preserving:

```text
original merge decision
later correction decision
historical relationships
historical references
decision provenance
```

The added decision/effect consistency applies equally to correction.

### Result

```text
PASS
```

---

# 21. Double-evolution attack

Consider both sides changing:

```text
Contact B → Contact A

Asset Y → Asset X

Relationship R historically:
B ↔ Y
```

The repaired matrix supports:

```text
historical:
B ↔ Y

current canonical navigation:
A ↔ X
```

without changing Relationship R's historical identity.

This preserves B3 Contact semantics and B4 Asset semantics simultaneously.

### Result

```text
PASS
```

---

# 22. Valid-time / decision-time non-regression

None of the repairs collapse:

```text
VALID TIME
```

into:

```text
CPL DECISION TIME
```

A later decision may still establish or correct validity beginning earlier.

The repaired decision/effect consistency requirement concerns canonical commitment, not temporal meaning.

### Result

```text
PASS
```

---

# 23. Technical failure/non-resolution non-regression

RM-B4-01 does not convert technical failure into a governed semantic outcome.

Therefore:

```text
technical failure
≠
AMBIGUOUS
≠
UNRESOLVED
≠
CONTRADICTORY
```

Likewise, `HOLD` remains a governed admission state rather than a substitute for infrastructure failure.

### Result

```text
PASS
```

---

# 24. REQ-B4-001 → 240 preservation

The v0.1 artifact explicitly preserves the original requirement IDs and semantics.

No renumbering is authorized.

No requirement in `241 → 260` requires removal or weakening of an earlier requirement.

Logical compatibility check:

```text
REQ-B4-001 → 240
        +
REQ-B4-241 → 260
        ↓
NO MATERIAL CONTRADICTION FOUND
```

### Result

```text
NON-REGRESSION = PASS
```

---

# 25. Requirement numbering integrity

Effective range:

```text
REQ-B4-001
...
REQ-B4-240
REQ-B4-241
...
REQ-B4-260
```

No overlapping ID.

No reused ID.

No gap created by repair.

### Result

```text
PASS
```

---

# 26. RC-B4-RM-07 — Are all 260 requirements acceptance-testable?

The relevant B4 families can now be translated into acceptance evidence covering:

```text
Asset creation and identity

AssetIdentifier behavior

domain identity resolution

canonical Asset decisions

merge admission

survivor selection

dependency disposition

merge/correction

ExternalReference

DomainProjection

ContactAssetRelationship

canonical relationship decisions

valid time / decision time

idempotency

cardinality/conflict

history/provenance

authority boundaries

B3 compatibility

B1/B2/B3 non-regression

partial-failure consistency

historical/current navigation
```

No material normative question must now be invented by implementation merely to determine expected behavior.

### Result

```text
RC-B4-RM-07 = PASS
```

---

# 27. Testability does not mean tests are already defined

This distinction remains important.

The Requirement Matrix defines:

```text
WHAT MUST HOLD
```

It does not yet define the complete:

```text
test implementation
fixture structure
database setup
test naming
test framework organization
```

Those belong downstream.

Therefore acceptance-testability does not improperly cross the HOW boundary.

### Result

```text
PASS
```

---

# 28. RC-B4-RM-08 — Can an Execution Mandate now be written without inventing normative semantics?

Yes.

An Execution Mandate can now bind implementation to:

```text
Frozen B4 WHAT
        +
Frozen B4 Requirement Matrix
        +
canonical repository baseline
        +
existing B1/B2/B3 invariants
        +
verification obligations
```

without deciding new questions such as:

```text
Who determines physical Asset identity?

Who owns canonical merge authority?

What happens under ambiguity?

How is the survivor selected?

What happens to historical references?

What constitutes relationship identity?

How do valid time and decision time differ?

What happens on canonical replay?

What happens on partial canonical failure?

Can unresolved material dependencies be ignored?
```

Those questions are already normatively determined.

### Result

```text
RC-B4-RM-08 = PASS
```

---

# 29. Execution Mandate readiness boundary

Passing this re-challenge does **not** itself authorize implementation.

It authorizes production of the next governance artifact:

```text
B4_EXECUTION_MANDATE_v0.md
```

That mandate must establish at minimum:

```text
canonical build baseline

authorized implementation scope

frozen WHAT reference

frozen Requirement Matrix reference

branch policy

migration boundary

non-regression boundary

required test/evidence classes

candidate completion conditions

prohibited deviations

verification handoff
```

Only materialization of that mandate crosses the B4 build boundary.

---

# 30. New-gap challenge

Final question:

> After repairs RM-B4-01 → RM-B4-04, is there another material requirement gap whose resolution would require normative invention during implementation?

No such material gap is identified.

Some implementation choices remain intentionally unresolved, including:

```text
storage decomposition
service decomposition
transaction mechanism
locking strategy
API shape
internal class structure
query implementation
indexing
specific migration count
```

These are HOW choices, not missing WHAT.

### Result

```text
NEW MATERIAL REQUIREMENT GAP = NONE IDENTIFIED
```

---

# 31. Repair closure table

| Repair   | Subject                          | Result     |
| -------- | -------------------------------- | ---------- |
| RM-B4-01 | Decision/effect consistency      | **CLOSED** |
| RM-B4-02 | Dependency-disposition closure   | **CLOSED** |
| RM-B4-03 | Canonical-transition idempotency | **CLOSED** |
| RM-B4-04 | Historical/current navigation    | **CLOSED** |

```text
4 / 4 CLOSED
```

---

# 32. Targeted Re-Challenge scoreboard

```text
RC-B4-RM-01
Canonical decision/effect consistency
  PASS

RC-B4-RM-02
Dependency-disposition closure
  PASS

RC-B4-RM-03
Canonical-transition idempotency
  PASS

RC-B4-RM-04
Historical/current distinction
  PASS

RC-B4-RM-05
No forbidden HOW
  PASS

RC-B4-RM-06
Frozen WHAT compatibility
  PASS

RC-B4-RM-07
260-requirement acceptance-testability
  PASS

RC-B4-RM-08
Execution Mandate readiness
  PASS
```

### Score

```text
8 / 8 PASS
```

---

# 33. Global non-regression scoreboard

```text
Frozen B4 WHAT preserved:
  PASS

Asset Authority submodel preserved:
  PASS

Relationship submodel preserved:
  PASS

Asset merge authority preserved:
  PASS

Domain/CPL boundary preserved:
  PASS

Survivor determinacy preserved:
  PASS

Historical preservation preserved:
  PASS

Valid-time / decision-time distinction preserved:
  PASS

B3 Contact semantics preserved:
  PASS

B1/B2/B3 non-regression requirements preserved:
  PASS

REQ-B4-001 → 240 preserved:
  PASS

REQ-B4-241 → 260 compatible:
  PASS
```

---

# 34. Requirement freeze decision

The original challenge returned:

```text
REPAIR_REQUIRED
```

The authorized repairs have now all survived re-challenge.

No WHAT conflict exists.

No additional material requirement gap has been identified.

No prohibited HOW has been frozen.

Therefore:

```text
REQUIREMENTS_ACCEPTED
```

and:

```text
B4 REQUIREMENT MATRIX
  = FROZEN
```

---

# 35. Canonical requirement set

The frozen B4 implementation requirement set is:

```text
REQ-B4-001 → REQ-B4-260
```

with normative source:

```text
B4_REQUIREMENT_MATRIX_v0.md
        +
B4_REQUIREMENT_MATRIX_v0.1.md
```

where v0.1 preserves `001 → 240` and adds `241 → 260`.

No implementation system is authorized to silently:

```text
remove
renumber
weaken
reinterpret
or bypass
```

those requirements.

---

# 36. Change-control boundary

After this freeze, a newly discovered issue must be classified.

```text
implementation defect
        ↓
repair implementation

requirement interpretation question
        ↓
resolve against frozen WHAT + requirements

genuine requirement defect
        ↓
formal requirement change control

WHAT defect
        ↓
reopen WHAT explicitly
```

Implementation MUST NOT silently repair a requirement or WHAT defect by choosing new semantics in code.

---

# 37. Execution boundary

The governance transition is now:

```text
Frozen WHAT
      +
Frozen Requirements
      ↓
Execution Mandate
      ↓
Canonical Build Baseline
      ↓
Candidate Branch
      ↓
Implementation
      ↓
Tests + Evidence
      ↓
Candidate SHA
      ↓
Independent Verification
      ↓
Acceptance / Repair
```

This is the same governed production boundary established during B3.

---

# 38. Re-Challenge verdict

```text
CPL_B4_REQUIREMENT_MATRIX_RE_CHALLENGE_v0.1

Baseline:
  main @ ae913f9

Requirements challenged:
  REQ-B4-001 → REQ-B4-260

Authorized repairs:
  RM-B4-01 → RM-B4-04

Repairs closed:
  4 / 4

Targeted challenges:
  8 / 8 PASS

Frozen WHAT conflict:
  NO

Forbidden HOW introduced:
  NO

Existing requirements regressed:
  NO

New material requirement gap:
  NONE IDENTIFIED

Requirement acceptance:
  PASS

FINAL RESULT:
  REQUIREMENTS_ACCEPTED
```

---

# 39. Governance status after acceptance

```text
B4 Asset Authority
  = STABILIZED

B4 Relationship submodel
  = STABILIZED

B4 WHAT
  = FROZEN

B4 Requirement Matrix
  = FROZEN
  = REQ-B4-001 → REQ-B4-260

B4 Execution Mandate
  = AUTHORIZED FOR PRODUCTION
  = NOT YET ISSUED

B4 Implementation
  = NOT AUTHORIZED

B4 Acceptance
  = NOT GRANTED

B4 Closure
  = NOT GRANTED

B5
  = NOT AUTHORIZED
```

---

# 40. Next authorized artifact

The next artifact is exactly:

```text
B4_EXECUTION_MANDATE_v0.md
```

It must be produced against the canonical repository state **after this Re-Challenge has itself been materialized**.

Therefore we should **not produce the Execution Mandate yet**.

First:

```text
B4_REQUIREMENT_MATRIX_RE_CHALLENGE_v0.1.md
        ↓
materialize on main
        ↓
record resulting canonical SHA
        ↓
B4_EXECUTION_MANDATE_v0.md
```

That resulting SHA becomes the B4 implementation baseline.

---

# 41. Final declaration

```text
CPL B4 REQUIREMENT MATRIX RE-CHALLENGE v0.1
============================================

B4 WHAT:
  FROZEN

Requirement Matrix:
  REQ-B4-001 → REQ-B4-260

RM-B4-01:
  CLOSED

RM-B4-02:
  CLOSED

RM-B4-03:
  CLOSED

RM-B4-04:
  CLOSED

Targeted Re-Challenge:
  8 / 8 PASS

Non-regression:
  PASS

WHAT_CONFLICT:
  NO

HOW LEAKAGE:
  NO

NEW MATERIAL GAP:
  NONE IDENTIFIED

FINAL:
  REQUIREMENTS_ACCEPTED

B4 REQUIREMENT MATRIX:
  FROZEN

NEXT AUTHORIZED:
  B4_EXECUTION_MANDATE_v0.md

IMPLEMENTATION:
  NOT YET AUTHORIZED
```

**END — CPL B4 Requirement Matrix Re-Challenge v0.1**

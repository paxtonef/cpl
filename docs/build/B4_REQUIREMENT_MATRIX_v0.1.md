# CPL — B4 Requirement Matrix v0.1

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Requirement Matrix
**Version:** v0.1
**Status:** REPAIRED — PROPOSED FOR REQUIREMENT RE-CHALLENGE
**Canonical production baseline:** `main @ 66d7726`
**Frozen WHAT baseline:** `B4 WHAT = FROZEN`
**Repair authority:** `B4_REQUIREMENT_CHALLENGE_v0.md`
**Implementation authorization:** NONE

---

## 1. Purpose

`B4_REQUIREMENT_MATRIX_v0.1` repairs the challenged B4 Requirement Matrix v0 without reopening the frozen B4 WHAT.

The Requirement Challenge established:

```text
Initial matrix:
  REQ-B4-001 → REQ-B4-240

Challenge:
  CORE REQUIREMENT MODEL = PASS
  TRACEABILITY = PASS
  WHAT CONFORMANCE = PASS
  WHAT_CONFLICT = NO

Overall:
  REPAIR_REQUIRED
```

Four bounded repairs were authorized:

```text
RM-B4-01
  Canonical decision / canonical effect consistency

RM-B4-02
  Dependency-disposition closure

RM-B4-03
  Canonical-transition idempotency

RM-B4-04
  Historical/current navigation distinction
```

This version incorporates those four repairs.

---

# 2. Versioning rule

The existing requirement range:

```text
REQ-B4-001 → REQ-B4-240
```

is preserved **without renumbering or semantic modification**.

v0.1 adds:

```text
REQ-B4-241 → REQ-B4-260
```

Therefore the effective B4 Requirement Matrix is:

```text
REQ-B4-001 → REQ-B4-260
```

**260 requirements total.**

---

# 3. Normative preservation of v0 requirements

All requirements contained in:

```text
B4_REQUIREMENT_MATRIX_v0.md
```

from:

```text
REQ-B4-001
```

through:

```text
REQ-B4-240
```

remain normative in v0.1 exactly as challenged.

No existing requirement is:

```text
renumbered
deleted
weakened
reinterpreted
silently repaired
```

The additions below supplement the existing matrix.

---

# 4. RM-B4-01 — Canonical decision / effect consistency

## Problem closed

The v0 matrix required durable canonical decisions and durable canonical state, but did not explicitly prohibit partial canonical transitions such as:

```text
Decision persisted
Canonical mutation failed
```

or:

```text
Canonical mutation committed
Decision persistence failed
```

The frozen WHAT requires canonical decision and canonical effect to constitute one governed transition.

---

## REQ-B4-241

A canonical Asset identity mutation MUST NOT become observably committed unless its governing `CanonicalAssetIdentityDecision` and resulting canonical effect are durably consistent.

## REQ-B4-242

A `CanonicalAssetIdentityDecision` MUST NOT be represented as successfully committed when the canonical Asset mutation governed by that decision failed to become canonical.

## REQ-B4-243

A canonical relationship mutation MUST NOT become observably committed unless its governing `CanonicalRelationshipDecision` and resulting canonical relationship effect are durably consistent.

## REQ-B4-244

A `CanonicalRelationshipDecision` MUST NOT be represented as successfully committed when the canonical relationship mutation governed by that decision failed to become canonical.

## REQ-B4-245

Failure during a governed canonical transition MUST leave the system in a state in which no partial canonical transition is exposed as successfully committed.

---

# 5. RM-B4-01 semantic invariant

The effective requirement is:

```text
CANONICAL DECISION
        +
CANONICAL EFFECT
        ↓
ONE GOVERNED COMMITTED TRANSITION
```

or:

```text
NO SUCCESSFULLY COMMITTED TRANSITION
```

This requirement is about externally observable consistency.

It does **not** prescribe:

```text
specific SQL transaction mechanism
specific locking implementation
event sourcing
two-phase commit
specific persistence technology
```

---

# 6. RM-B4-02 — Dependency-disposition closure

## Problem closed

v0 required dependency disposition to be evaluated before Asset merge, but did not state a sufficiently explicit execution closure condition.

This could have allowed:

```text
some material dependencies unresolved
        ↓
merge executes anyway
```

The repaired matrix prohibits this.

---

## REQ-B4-246

Before canonical Asset merge execution, every dependency family materially capable of affecting canonical safety MUST have an explicit governed disposition.

## REQ-B4-247

If any material dependency family lacks a safe governed disposition, canonical Asset merge MUST remain `HOLD` or MUST be rejected.

## REQ-B4-248

Canonical Asset merge execution MUST NOT silently apply an implicit default disposition to an unresolved material dependency family.

## REQ-B4-249

Where dependency disposition affects the canonical outcome of an Asset merge, the implementation MUST preserve evidence sufficient to identify the governed disposition applied to each material dependency family.

---

# 7. Material dependency families

At minimum the previously frozen B4 semantics require consideration of applicable families such as:

```text
AssetIdentifier

AssetIdentityResolution

CanonicalAssetIdentityDecision

ContactAssetRelationship

Case

ExternalReference

DomainProjection

other canonical/historical references
```

This does not mean every merge must mutate every family.

It means each materially relevant family must have a known governed treatment before execution.

---

# 8. Dependency-disposition closure rule

The execution gate becomes:

```text
SAME_PHYSICAL_ASSET
        ↓
CPL merge admission
        ↓
material dependency analysis
        ↓
all material dispositions governed?
       / \
     NO   YES
     ↓     ↓
   HOLD   merge may proceed
   or
 REJECT
```

Asset physical identity may remain positively resolved while canonical merge remains on `HOLD`.

---

# 9. RM-B4-03 — Canonical-transition idempotency

## Problem closed

v0 specified idempotency for Asset creation and relationship establishment, but did not make replay semantics explicit for all canonical mutations.

A retry must not generate a second independent canonical history event merely because execution was repeated.

---

## REQ-B4-250

Replaying the same governed Asset merge request within its applicable idempotency scope MUST NOT create a second independent canonical Asset merge transition.

## REQ-B4-251

Replaying the same governed Asset correction request within its applicable idempotency scope MUST NOT create a second independent canonical Asset correction transition.

## REQ-B4-252

Replaying the same governed relationship canonical mutation request within its applicable idempotency scope MUST NOT create a second independent canonical relationship transition.

## REQ-B4-253

For replay-equivalent canonical mutation requests, idempotent execution MUST preserve the original committed canonical decision identity or semantically equivalent governed transition identity.

## REQ-B4-254

Similarity of canonical mutation payload alone MUST NOT establish canonical-transition idempotency identity.

---

# 10. Covered canonical relationship mutations

`REQ-B4-252` includes at least the semantic mutation families:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

where replay semantics apply.

The requirement does not imply that those four operations share one physical implementation.

---

# 11. Idempotency identity rule

B4 distinguishes:

```text
same governed operation identity
        ↓
REPLAY
```

from:

```text
same payload
        ↓
POSSIBLY DISTINCT OPERATION
```

For example:

```text
MERGE A/B request K
MERGE A/B request K
```

must be replay-safe.

But:

```text
request K1: MERGE A/B
request K2: MERGE A/B
```

cannot automatically be assumed to represent the same governed operation merely from payload similarity.

---

# 12. RM-B4-04 — Historical/current navigation distinction

## Problem closed

The frozen WHAT distinguishes:

```text
historical attribution
≠
current canonical navigation
```

The v0 matrix required historical preservation, but did not make sufficiently explicit that both views must be observably/verifiably distinguishable.

A system that preserved historical identifiers internally but exposed only rewritten current identity everywhere would not conform.

---

## REQ-B4-255

Where an Asset canonical successor differs from a historical Asset target, the system MUST preserve a verifiable distinction between historical attribution and current canonical navigation.

## REQ-B4-256

Where a Contact canonical successor differs from a historical `ContactAssetRelationship` Contact endpoint, the system MUST preserve a verifiable distinction between historical attribution and current canonical navigation.

## REQ-B4-257

Current canonical relationship queries MAY resolve current Contact and Asset canonical successors without rewriting the historical Contact and Asset endpoints of the relationship.

## REQ-B4-258

Historical relationship inspection MUST be capable of exposing the Contact and Asset identities originally associated with the `ContactAssetRelationship`.

## REQ-B4-259

Historical `ExternalReference` inspection MUST be capable of exposing the CPL target originally referenced by the external system even where current navigation resolves through another canonical Asset.

## REQ-B4-260

B4 acceptance evidence MUST demonstrate at least one case in which historical attribution and current canonical navigation differ and both are correctly reconstructable.

---

# 13. Historical/current example

Suppose:

```text
Historical state:

Contact B
    │
    └── Relationship R ──→ Asset Y
```

Later:

```text
Contact B → Contact A
Asset Y   → Asset X
```

The system may expose current navigation:

```text
Contact A ↔ Asset X
```

while historical inspection must still reconstruct:

```text
Relationship R originally:
Contact B ↔ Asset Y
```

v0.1 now makes both properties acceptance-testable.

---

# 14. ExternalReference example

Suppose external system `E` historically contains:

```text
external_ref = V-123
CPL target = Asset B
```

and later:

```text
Asset B → Asset A
```

Current canonical navigation may resolve:

```text
V-123 → canonical Asset A
```

but historical inspection must still show:

```text
external system E originally referenced Asset B
```

unless the external system itself independently changed its binding.

---

# 15. Repair traceability

```text
RM-B4-01
  → REQ-B4-241 → REQ-B4-245

RM-B4-02
  → REQ-B4-246 → REQ-B4-249

RM-B4-03
  → REQ-B4-250 → REQ-B4-254

RM-B4-04
  → REQ-B4-255 → REQ-B4-260
```

All four authorized repair families are represented.

---

# 16. Repair completeness

```text
RM-B4-01
  INCORPORATED

RM-B4-02
  INCORPORATED

RM-B4-03
  INCORPORATED

RM-B4-04
  INCORPORATED
```

**4 / 4 incorporated.**

---

# 17. Requirement count

```text
Previous:
  REQ-B4-001 → REQ-B4-240
  = 240

Added:
  REQ-B4-241 → REQ-B4-260
  = 20

Total:
  REQ-B4-001 → REQ-B4-260
  = 260
```

---

# 18. Frozen WHAT conformance

The repairs do not change:

```text
Asset ontology

AssetIdentifier semantics

AssetIdentityResolution authority

CanonicalAssetIdentityDecision semantics

merge authority

merge survivor precedence

canonical correction

ContactAssetRelationship identity

CanonicalRelationshipDecision semantics

VALID TIME / DECISION TIME

domain/CPL boundary

historical preservation

authorization boundary
```

Therefore:

```text
WHAT_CONFLICT = NO
```

---

# 19. No HOW capture

The added requirements do not require any particular:

```text
transaction library
database table
database constraint
API
ORM
event architecture
locking primitive
idempotency-key representation
temporal storage implementation
```

They define observable invariants.

Implementation remains free to choose HOW subject to conformance.

---

# 20. Canonical transition acceptance model

The repaired matrix now supports the complete pattern:

```text
INPUT / REQUEST
      ↓
AUTHORITY / ADMISSION
      ↓
CANONICAL DECISION
      ↓
CANONICAL EFFECT
      ↓
DURABLE CONSISTENT COMMIT
      ↓
CURRENT NAVIGATION
      +
HISTORICAL RECONSTRUCTABILITY
```

with replay protection and failure consistency.

---

# 21. Asset transition requirements after repair

For Asset canonical transitions, the matrix now jointly requires:

```text
positive admissible physical identity basis

CPL canonical admission

governed survivor determination

material dependency closure

CanonicalAssetIdentityDecision

decision/effect consistency

canonical-transition idempotency

historical continuity

current canonical navigation
```

No one of these substitutes for the others.

---

# 22. Relationship transition requirements after repair

For relationship transitions, the matrix now jointly requires:

```text
governed relationship identity

admissible evidence/authority

CanonicalRelationshipDecision

ESTABLISH / END / CORRECT / SUPERSEDE semantics

valid-time / decision-time distinction

decision/effect consistency

canonical-transition idempotency

endpoint historical preservation

current canonical navigation
```

---

# 23. Failure model after repair

A canonical transition may fail technically.

If so:

```text
partial canonical success
```

must not be exposed.

Likewise:

```text
HOLD
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
```

remain governed semantic outcomes rather than technical exceptions.

Thus:

```text
governed non-resolution
≠
technical execution failure
≠
partial committed canonical transition
```

---

# 24. Requirement verification additions

The existing verification requirements `REQ-B4-210 → REQ-B4-240` remain normative.

v0.1 additionally requires acceptance evidence capable of exercising `REQ-B4-241 → 260`.

The re-challenge must confirm that these requirements are sufficiently testable without inventing implementation.

---

# 25. Required re-challenge targets

The authorized Requirement Matrix Re-Challenge must test at least:

```text
RC-B4-RM-01
Can canonical state and canonical decision diverge
after partial failure?

RC-B4-RM-02
Can merge execute while a material dependency family
remains without governed disposition?

RC-B4-RM-03
Can replay create duplicate canonical transitions?

RC-B4-RM-04
Can historical attribution disappear behind
current canonical navigation?

RC-B4-RM-05
Do REQ-B4-241 → 260 impose forbidden HOW?

RC-B4-RM-06
Do REQ-B4-241 → 260 conflict with frozen B4 WHAT?

RC-B4-RM-07
Are REQ-B4-001 → 260 collectively acceptance-testable?

RC-B4-RM-08
Can an Execution Mandate now be written without
inventing additional normative semantics?
```

---

# 26. Requirement Re-Challenge acceptance condition

The matrix may freeze only if:

```text
RM-B4-01 → RM-B4-04
  all verified

REQ-B4-241 → REQ-B4-260
  individually compatible with frozen WHAT

REQ-B4-001 → REQ-B4-240
  no regression

WHAT_CONFLICT
  NO

additional material requirement gap
  NONE
```

---

# 27. Requirement Matrix status

```text
B4 Requirement Matrix v0
  MATERIALIZED
  CHALLENGED
  REPAIR_REQUIRED

B4 Requirement Challenge v0
  MATERIALIZED
  RM-B4-01 → RM-B4-04 authorized

B4 Requirement Matrix v0.1
  PRODUCED
  260 requirements effective
  4/4 repairs incorporated
  PROPOSED FOR REQUIREMENT RE-CHALLENGE
```

---

# 28. Governance status

```text
B4 WHAT
  = FROZEN

B4 Requirement Matrix v0.1
  = REPAIRED
  = NOT YET FROZEN

B4 Requirement Matrix Re-Challenge
  = NEXT GOVERNANCE STEP

B4 Execution Mandate
  = NOT AUTHORIZED

B4 Implementation
  = NOT AUTHORIZED
```

---

# 29. Next artifact

The next artifact is:

```text
B4_REQUIREMENT_MATRIX_RE_CHALLENGE_v0.1.md
```

If it concludes:

```text
REQUIREMENTS_ACCEPTED
```

then:

```text
B4 Requirement Matrix
  = FROZEN

B4 Execution Mandate
  = AUTHORIZED FOR PRODUCTION
```

Implementation will still **not** begin until that Execution Mandate is itself produced and canonically materialized.

---

# 30. Final declaration

```text
CPL B4 REQUIREMENT MATRIX v0.1
==============================

Frozen B4 WHAT:
  INTACT

Previous requirements:
  REQ-B4-001 → REQ-B4-240
  PRESERVED UNCHANGED

New requirements:
  REQ-B4-241 → REQ-B4-260

Total:
  260

RM-B4-01:
  INCORPORATED

RM-B4-02:
  INCORPORATED

RM-B4-03:
  INCORPORATED

RM-B4-04:
  INCORPORATED

Authorized repairs:
  4 / 4 incorporated

WHAT_CONFLICT:
  NO

STATUS:
  REPAIRED
  PROPOSED FOR REQUIREMENT RE-CHALLENGE

READY FOR:
  B4_REQUIREMENT_MATRIX_RE_CHALLENGE_v0.1

NOT READY FOR:
  EXECUTION MANDATE
  IMPLEMENTATION
```

**END — CPL B4 Requirement Matrix v0.1**

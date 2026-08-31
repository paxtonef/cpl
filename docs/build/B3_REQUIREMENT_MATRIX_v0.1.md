# CPL — B3 Requirement Matrix v0.1

**System:** Common Product Layer — CPL
**Phase:** B3 — Identity + Accounts
**Artifact:** Requirement Matrix
**Version:** v0.1
**Status:** REPAIRED — PROPOSED FOR RE-CHALLENGE
**Canonical repair baseline:** `75bf524a68309d707219738f1fecedc9eb9aef80`

**Supersedes for prospective B3 governance:** `B3_REQUIREMENT_MATRIX_v0.md`
**Preserves:** `REQ-B3-001 → REQ-B3-100`
**Authorized repair source:** `B3_REQUIREMENT_CHALLENGE_v0.md`

---

## 1. Repair authority

The B3 Requirement Challenge established:

```text
B3_REQUIREMENT_MATRIX_v0
  CHALLENGED
  REPAIR_REQUIRED

Repair authority:
  BOUNDED TO RM-O01 → RM-O04

WHAT reopening:
  NO

Primitive modification:
  NO

Implementation authorization:
  NO
```

This v0.1 incorporates those four closures without modifying the frozen B3 WHAT.

---

# 2. Normative continuity

All requirements:

```text
REQ-B3-001 → REQ-B3-100
```

from `B3_REQUIREMENT_MATRIX_v0.md` remain normative and retain their identifiers and meanings.

v0.1 does not renumber them.

The following requirements are added:

```text
REQ-B3-101 → REQ-B3-125
```

Their sole purpose is to materialize the four closures authorized by the Requirement Challenge.

---

# 3. RM-O01 — Related-Object Reconciliation

## 3.1 Governing principle

A Contact merge means:

```text
SOURCE Contact
  remains historically interpretable

TARGET Contact
  becomes surviving current Contact identity
```

It does **not** mean:

```text
SOURCE never existed
```

Related-object reconciliation MUST therefore preserve:

```text
CURRENT SEMANTIC CORRECTNESS
+
HISTORICAL TRUTH
```

The only authorized reconciliation classifications remain:

```text
PRESERVE
REASSOCIATE
REJECT_CONFLICT
DEFER
```

---

## 3.2 Accounts

### REQ-B3-101 — Account merge default

Accounts belonging to a merged source Contact MUST, by default, be reconciled toward the surviving Contact using:

```text
REASSOCIATE
```

where reassociation is admissible and does not violate Account identity invariants.

**Trace:** RMO-13 / REQ-B3-057
**Verification:** STATE / POSITIVE

---

### REQ-B3-102 — Account history preservation

Account reassociation during Contact merge MUST preserve sufficient historical provenance to establish the Account's prior association with the source Contact.

Reassociation MUST NOT rewrite history as though the Account had always belonged to the target Contact.

**Verification:** TRACEABILITY / STATE

---

### REQ-B3-103 — Equivalent Account binding

Where the target already possesses an equivalent admissible Account binding, reconciliation MUST NOT create a duplicate current binding.

The resulting semantics MUST be equivalent to:

```text
PRESERVE historical evidence
+
NO_CHANGE for current binding
```

**Verification:** IDEMPOTENCY / STATE

---

### REQ-B3-104 — Incompatible Account binding

Where reassociation would violate provider identity uniqueness or create an incompatible current Account binding, reconciliation MUST classify the condition as:

```text
REJECT_CONFLICT
```

and the Contact merge MUST NOT complete while that mandatory identity conflict remains unresolved.

**Verification:** NEGATIVE / TRANSACTION

---

## 3.3 ContactPoints

### REQ-B3-105 — ContactPoint merge default

A source ContactPoint SHOULD be reconciled toward the surviving Contact using:

```text
REASSOCIATE
```

where the resulting current ContactPoint state remains admissible.

**Verification:** STATE

---

### REQ-B3-106 — ContactPoint verification preservation

Reassociation MUST NOT constitute a new verification event.

Existing verification state MAY remain semantically valid only where its provenance and applicable verification semantics remain valid after reassociation.

B3 MUST NOT manufacture a fresh verification assertion as part of merge.

**Verification:** STATE / TRACEABILITY / NEGATIVE

---

### REQ-B3-107 — Equivalent ContactPoint reconciliation

Where the target already contains an equivalent current ContactPoint, B3 MUST NOT blindly create another equivalent active ContactPoint.

Historical evidence of the source relationship MUST remain recoverable.

**Verification:** STATE / IDEMPOTENCY

---

### REQ-B3-108 — Primary ContactPoint conflict

Reconciliation MUST NOT leave multiple primary ContactPoints in violation of existing B2 uniqueness semantics.

Primary status MUST NOT simply be copied from source to target where that would create a conflict.

**Verification:** NEGATIVE / STATE

---

### REQ-B3-109 — ContactPoint DEFER boundary

`DEFER` MAY be used for a ContactPoint reconciliation only where deferral does not make the surviving current identity misleading or violate a mandatory current identity invariant.

Otherwise the condition MUST resolve or become:

```text
REJECT_CONFLICT
```

before merge completion.

**Verification:** NEGATIVE / STATE

---

## 3.4 ContactAssetRelationships

### REQ-B3-110 — ContactAssetRelationship default

Historical `ContactAssetRelationships` attached to a source Contact MUST default to:

```text
PRESERVE
```

Contact merge MUST NOT rewrite the historical relationship to imply that the target Contact was necessarily the original relationship bearer.

**Verification:** STATE / TRACEABILITY

---

### REQ-B3-111 — Current Asset relationship semantics

Where current operational semantics require a relationship with the surviving Contact, B3 MAY establish or reassociate current semantics only where doing so is admissible under existing CPL relationship invariants.

Such current semantics MUST NOT destroy the historical source relationship.

**Verification:** STATE

---

## 3.5 CaseParticipants

### REQ-B3-112 — CaseParticipant default

Historical `CaseParticipant` records involving the source Contact MUST default to:

```text
PRESERVE
```

because participation is a historical fact.

**Verification:** STATE / TRACEABILITY

---

### REQ-B3-113 — Current Case resolution

Where an active Case requires the surviving current identity, the system MAY resolve the historical source Contact through the merge relationship to the surviving target Contact.

This MUST NOT require rewriting the historical CaseParticipant record as though the target had originally participated.

**Verification:** STATE

---

## 3.6 ExternalReferences

### REQ-B3-114 — ExternalReference default

`ExternalReferences` associated with the source Contact MUST default to:

```text
PRESERVE
```

**Verification:** STATE / TRACEABILITY

---

### REQ-B3-115 — ExternalReference reassociation authority

An ExternalReference MUST NOT be reassociated solely because its Contact was merged.

`REASSOCIATE` requires independently admissible authority/evidence for that external-reference relationship.

Absent such authority:

```text
PRESERVE
DEFER
or
REJECT_CONFLICT
```

MUST be used as appropriate.

**Verification:** NEGATIVE / STATE

---

## 3.7 RM-O01 closure

```text
Accounts
  DEFAULT = REASSOCIATE

ContactPoints
  DEFAULT = REASSOCIATE where admissible

ContactAssetRelationships
  DEFAULT = PRESERVE

CaseParticipants
  DEFAULT = PRESERVE

ExternalReferences
  DEFAULT = PRESERVE
```

`RM-O01 = CLOSED`

---

# 4. RM-O02 — Verification Assertion Minimum Contract

## 4.1 Boundary

B3 consumes the result of an external verification event.

B3 does NOT become the verification mechanism.

The Verification Assertion therefore represents:

```text
external verification
        ↓
governed assertion
        ↓
B3 admissibility decision
        ↓
ContactPoint state transition
```

---

### REQ-B3-116 — Minimum Verification Assertion semantics

An admissible Verification Assertion MUST make recoverable at least:

```text
assertion identity
target ContactPoint identity
verification class
issuer/source
verification result
verification time
authority/admissibility context
replay/idempotency identity
```

The Requirement Matrix does not prescribe a serialization format.

**Trace:** RMO-05 / REQ-B3-023 → 027
**Verification:** INSPECTION / NEGATIVE

---

### REQ-B3-117 — Conditional assertion information

Where applicable to the verification class, the assertion MUST also make available the semantics of:

```text
expiry
external reference
evidence reference
```

where those properties are material to admissibility.

**Verification:** POSITIVE / NEGATIVE

---

### REQ-B3-118 — Assertion rejection conditions

B3 MUST reject a Verification Assertion where a material admissibility condition includes:

```text
target mismatch
unsupported verification class
negative verification result
expired assertion where expiry applies
unauthorized issuer/context
invalid replay semantics
missing mandatory provenance
```

**Verification:** NEGATIVE

---

### REQ-B3-119 — Verification secret boundary

The Verification Assertion contract MUST NOT require B3 to persist or operate:

```text
password
OTP secret
OAuth credential
authentication token secret
raw authentication secret
```

solely to establish ContactPoint verification.

**Verification:** INSPECTION / BOUNDARY

---

### REQ-B3-120 — Assertion is evidence, not caller declaration

A caller's unsupported declaration that a ContactPoint is verified MUST NOT satisfy the Verification Assertion contract.

**Verification:** NEGATIVE

---

## 4.2 RM-O02 closure

```text
RM-O02 = CLOSED
```

No provider implementation, OTP mechanism, OAuth mechanism or transport has been selected.

---

# 5. RM-O03 — Durable Provenance Minimum Obligation

## 5.1 Governing distinction

B3 distinguishes:

```text
DURABLE GOVERNANCE PROVENANCE
≠
TRANSIENT EXECUTION OBSERVABILITY
```

Material identity decisions must remain explainable after process restart.

---

### REQ-B3-121 — Durable identity-operation provenance

For each material identity-changing B3 operation, B3 MUST durably preserve enough provenance to reconstruct:

```text
WHAT happened
TO WHAT
WHY
UNDER WHOSE AUTHORITY
USING WHAT MATERIAL EVIDENCE
WHEN
WITH WHAT RESULT
```

At minimum, durable provenance MUST make recoverable:

```text
operation identity
operation type
affected object identities
actor/requester identity or reference
authority context or reference
material evidence/assertion references
decision/result
timestamp
```

**Trace:** RMO-17 / REQ-B3-076 → 079
**Verification:** TRACEABILITY / RESTART

---

### REQ-B3-122 — Merge provenance minimum

A completed or rejected material merge decision MUST additionally make recoverable:

```text
source_contact_id
target_contact_id
merge proposal reference
merge authorization reference/context
material reconciliation result
final merge decision/result
```

**Verification:** TRACEABILITY

---

### REQ-B3-123 — ContactPoint verification provenance minimum

An accepted ContactPoint verification transition MUST make durably recoverable at least:

```text
contact_point_id
verification assertion reference
accepted verification class
verification time
result
```

together with the general authority/provenance information required by `REQ-B3-121`.

**Verification:** TRACEABILITY / RESTART

---

## 5.2 Non-required provenance material

The durable-provenance obligation does not, by itself, require persistence of:

```text
debug traces
stack traces
temporary calculations
raw provider payloads
LLM reasoning
internal agent chatter
secrets
```

unless independently required elsewhere.

Nor does it prescribe:

```text
audit table
event store
JSONB
relational schema
external provenance service
```

The requirement concerns **durable recoverability**, not storage architecture.

```text
RM-O03 = CLOSED
```

---

# 6. RM-O04 — Same Logical Contact Creation

## 6.1 Scope

This closure does NOT define universal human identity equivalence.

It defines only when two Contact-creation attempts count as the same logical creation for B3 idempotency and concurrency.

---

### REQ-B3-124 — Same logical creation identity

Two Contact-creation requests MUST be treated as the same logical creation for idempotency purposes where they carry the same governed creation/request identity within the same applicable authority and idempotency scope.

Examples of admissible governing identity include the semantic equivalent of:

```text
idempotency key
request identity
upstream operation identity
```

The specific mechanism is not prescribed.

**Trace:** RMO-15 / RMO-16 / REQ-B3-067 / REQ-B3-072
**Verification:** IDEMPOTENCY / CONCURRENCY

---

### REQ-B3-125 — Similarity is not creation identity

B3 MUST NOT classify two Contact-creation requests as the same logical creation solely because they share or resemble:

```text
name
email string
phone string
address
date of birth
similarity score
fuzzy-match score
ML output
LLM judgement
```

Such evidence MAY contribute to identity resolution, duplicate assessment or conflict detection under their applicable semantics.

It MUST NOT independently define Contact-creation idempotency.

Where independently governed identity evidence creates an identity conflict, B3 MUST use the applicable resolution/conflict semantics rather than silently create incompatible canonical Contacts.

**Verification:** NEGATIVE / CONCURRENCY

---

## 6.2 RM-O04 closure

```text
same governed creation identity
+ same applicable scope
        ↓
SAME LOGICAL CREATION
```

while:

```text
similar person data
        ↓
NOT SUFFICIENT
```

`RM-O04 = CLOSED`

---

# 7. Repaired related-object classification matrix

| Relationship family       | Default                        | Authorized conditional outcomes                                      |
| ------------------------- | ------------------------------- | -----------------------------------------------------------------------|
| Accounts                  | `REASSOCIATE`                  | `PRESERVE` history / `REJECT_CONFLICT`                               |
| ContactPoints             | `REASSOCIATE` where admissible | `PRESERVE` history / `REJECT_CONFLICT` / bounded `DEFER`             |
| ContactAssetRelationships | `PRESERVE`                     | current `REASSOCIATE` / `REJECT_CONFLICT` / `DEFER`                  |
| CaseParticipants          | `PRESERVE`                     | current resolution / `REJECT_CONFLICT` / `DEFER`                     |
| ExternalReferences        | `PRESERVE`                     | independently authorized `REASSOCIATE` / `REJECT_CONFLICT` / `DEFER` |

This matrix is normative for B3.

---

# 8. Updated verification obligations

The existing verification families remain applicable.

The repair adds explicit coverage requirements.

## Additional positive scenarios

```text
P-B3-19
Account successfully reconciled to surviving Contact

P-B3-20
ContactPoint successfully reconciled without manufacturing verification

P-B3-21
historical ContactAssetRelationship preserved across merge

P-B3-22
historical CaseParticipant preserved across merge

P-B3-23
ExternalReference historical association preserved

P-B3-24
valid Verification Assertion accepted

P-B3-25
durable provenance recoverable after process restart

P-B3-26
same governed Contact creation request replayed idempotently
```

---

## Additional negative scenarios

```text
N-B3-27
incompatible Account reconciliation blocks merge

N-B3-28
ContactPoint primary conflict not silently propagated

N-B3-29
unsafe ContactPoint DEFER does not permit misleading merge

N-B3-30
ExternalReference not silently rebound by Contact merge

N-B3-31
Verification Assertion target mismatch rejected

N-B3-32
expired Verification Assertion rejected where expiry applies

N-B3-33
unauthorized Verification Assertion rejected

N-B3-34
unsupported caller declaration cannot verify ContactPoint

N-B3-35
similar Contact data alone does not collapse two creation requests into one idempotency identity
```

---

## Additional transaction scenario

```text
T-B3-05
mandatory related-object reconciliation conflict
leaves Contact merge uncommitted
```

---

## Additional traceability scenarios

```text
TR-B3-06
Account merge reconciliation provenance recoverable

TR-B3-07
ContactPoint historical association recoverable after reassociation

TR-B3-08
merge authorization and reconciliation evidence recoverable after restart
```

---

# 9. Updated requirement coverage

```text
Existing requirements preserved:
  REQ-B3-001 → REQ-B3-100

New bounded-repair requirements:
  REQ-B3-101 → REQ-B3-125

Total requirements:
  125

Frozen primitives:
  14 / 14

RMO families:
  20 / 20

Previously open requirement-resolution items:
  4

Remaining open requirement-resolution items:
  0
```

---

# 10. Repair traceability

| Challenge closure                      | Materialized requirements |
| --------------------------------------- | -------------------------- |
| RM-O01 Related-object reconciliation   | REQ-B3-101 → 115          |
| RM-O02 Verification Assertion contract | REQ-B3-116 → 120          |
| RM-O03 Durable provenance              | REQ-B3-121 → 123          |
| RM-O04 Same logical Contact creation   | REQ-B3-124 → 125          |

Every addition is therefore traceable directly to the bounded repair authority established by `B3_REQUIREMENT_CHALLENGE_v0.md`.

---

# 11. Non-regression declaration

The repair does not authorize or introduce changes to:

```text
14 frozen B3 primitives
Contact object ontology
ContactPoint object ontology
Account object ontology
resolution-state ontology
authority ladder
merge directionality
historical source preservation
B1 runtime contract
B2 persistence foundation
B3 service boundary
```

No previously accepted requirement is intentionally weakened.

---

# 12. HOW-leakage check

v0.1 does not prescribe:

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

Those remain downstream implementation choices constrained by the requirements.

---

# 13. Developer discretion boundary

After v0.1, an implementation team MAY determine HOW to satisfy requirements.

It MUST NOT determine:

```text
which relationships preserve history
which relationships default to reassociation
whether verification requires evidence
whether provenance must survive restart
whether fuzzy similarity defines creation idempotency
whether merge conflicts may be silently ignored
```

Those are now governed requirements.

---

# 14. Requirement Matrix invariants after repair

All original RM invariants remain.

Additionally:

### RM-I09 — Reconciliation determinacy

Implementation MUST NOT invent default merge reconciliation semantics for the five governed relationship families.

### RM-I10 — Verification evidence boundary

ContactPoint verification MUST remain evidence-based without importing the external verification mechanism into CPL.

### RM-I11 — Durable decision explainability

Material identity mutation MUST remain explainable after restart.

### RM-I12 — Idempotency is not identity matching

Contact-creation idempotency MUST NOT become an implicit fuzzy identity-resolution mechanism.

---

# 15. Re-Challenge admission criteria

`B3_REQUIREMENT_MATRIX_v0.1.md` is admissible to Re-Challenge only if the canonical artifact demonstrates:

```text
REQ-B3-001 → 100 preserved
REQ-B3-101 → 125 added

RM-O01 CLOSED
RM-O02 CLOSED
RM-O03 CLOSED
RM-O04 CLOSED

no new primitive
no WHAT reopening
no authority collapse
no B1/B2 weakening
no implementation authorization
```

---

# 16. Re-Challenge scope

The next Re-Challenge SHOULD NOT repeat the entire B3 WHAT analysis.

It should test six questions:

```text
RC-01
Were all four authorized repairs incorporated?

RC-02
Did the repair remain within its authorization boundary?

RC-03
Were REQ-B3-001 → 100 preserved?

RC-04
Do REQ-B3-101 → 125 accurately encode the Challenge closures?

RC-05
Did the repair introduce contradiction, HOW capture,
or new semantic ambiguity?

RC-06
Can the repaired matrix now be frozen without requiring
developers to invent product semantics?
```

---

# 17. Current governance status

```text
B3 WHAT
  FROZEN

B3 Requirement Matrix v0
  CHALLENGED
  REPAIR_REQUIRED
  HISTORICAL ARTIFACT — PRESERVE

B3 Requirement Challenge v0
  MATERIALIZED
  REPAIR AUTHORITY ESTABLISHED

B3 Requirement Matrix v0.1
  REPAIRED
  RM-O01 CLOSED
  RM-O02 CLOSED
  RM-O03 CLOSED
  RM-O04 CLOSED
  PROPOSED FOR RE-CHALLENGE
  NOT YET FROZEN

B3 Requirement Re-Challenge
  REQUIRED

B3 Requirement Freeze
  NOT YET AUTHORIZED

B3 Execution Mandate
  NOT ISSUED

B3 Implementation
  NOT AUTHORIZED
```

---

# 18. Final declaration

The bounded repair is complete at the document level.

The Requirement Matrix now contains:

```text
125 normative requirements
14 / 14 primitive coverage
20 / 20 RMO coverage
0 unresolved requirement-resolution items
```

The transition now authorized is:

```text
B3_REQUIREMENT_MATRIX_v0.1
             ↓
       RE-CHALLENGE
             ↓
       ┌─────┴─────┐
       │           │
     FAIL         PASS
       │           │
 bounded repair    ↓
             REQUIREMENT FREEZE
                    ↓
             EXECUTION MANDATE
════════════════════════════════════
              BUILD BOUNDARY
════════════════════════════════════
                    ↓
             B3 IMPLEMENTATION
```

**END — CPL B3 Requirement Matrix v0.1**

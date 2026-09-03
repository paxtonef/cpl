# CPL — B4 Relationship Object & Authority Model v0.1

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Relationship Object & Authority Model
**Version:** v0.1
**Status:** REPAIRED — PROPOSED FOR TARGETED RE-CHALLENGE
**Repair source:** `B4_RELATIONSHIP_TARGETED_CHALLENGE_v0.md`
**Canonical baseline:** `main @ 870ef62`
**Implementation authorization:** NONE

---

## 1. Purpose of v0.1

This version repairs the B4 Relationship Object & Authority Model following the targeted challenge. It incorporates exactly the authorized repairs:

```text
R-B4-R01  Durable CanonicalRelationshipDecision
R-B4-R02  Valid-time / decision-time distinction
R-B4-R03  Stable logical relationship identity
R-B4-R04  Governed idempotency identity
R-B4-R05  Relationship evidence/conflict authority policy
R-B4-R06  Generic endpoint merge/correction behavior
R-B4-R07  Type/domain-governed cardinality and compatibility
R-B4-R08  END / CORRECT / SUPERSEDE semantic separation
```

No Asset Authority principle is reopened. No B4 implementation is authorized.

---

## 2. Core relationship ontology

B4 recognizes:

```text
Contact
Asset
ContactAssetRelationship
CanonicalRelationshipDecision
Relationship Evidence
Relationship Type Semantics
Relationship Authority Context
```

The following distinctions are normative:

```text
ContactAssetRelationship
    ≠ Contact identity

ContactAssetRelationship
    ≠ Asset identity

ContactAssetRelationship
    ≠ Authorization

ContactAssetRelationship
    ≠ CanonicalRelationshipDecision

Relationship Evidence
    ≠ CanonicalRelationshipDecision
```

---

## 3. ContactAssetRelationship as a persistent governed object

A `ContactAssetRelationship` is a persistent CPL object representing a governed relationship assertion between a Contact and an Asset. Its logical identity is independent of the current canonical representation of either endpoint. Therefore:

```text
Contact B → canonical Contact A
```

does not imply:

```text
relationship identity changed
```

Likewise:

```text
Asset Y → canonical Asset X
```

does not imply:

```text
relationship identity changed
```

---

## 4. Stable logical relationship identity

B4 adopts:

> A ContactAssetRelationship has governed persistent identity independent of current endpoint canonical identities, current status, and later correction.

Thus:

```text
current canonical Contact
+
current canonical Asset
+
relationship type
```

is NOT sufficient to define logical relationship identity. A relationship must possess its own durable identity or semantic equivalent.

---

## 5. Endpoint evolution invariant

Canonical evolution of either endpoint affects current navigation and interpretation. It does not rewrite relationship identity. Example:

```text
historical:
Relationship R
Contact B ↔ Asset Y

later:
Contact B → A
Asset Y → X

current navigation:
A ↔ X

historical relationship:
still B ↔ Y
```

Both views remain valid.

---

## 6. Relationship evidence

Relationship Evidence supports claims about a relationship. Possible evidence classes may include:

```text
registry information
contract
authenticated declaration
domain system evidence
operator evidence
external system evidence
historical CPL evidence
```

Evidence does not automatically become canonical relationship state.

---

## 7. Evidence ≠ authority

The fundamental rule is:

> Relationship evidence does not itself grant canonical relationship authority.

Thus:

```text
authenticated Contact claims OWNER
```

may be evidence. It is not universally sufficient to establish OWNER. Likewise:

```text
external system says DRIVER
```

may be evidence without being sufficient authority.

---

## 8. Relationship semantic authority

The semantics of a relationship type may be owned by:

```text
generic CPL
```

or:

```text
applicable domain authority
```

depending on the relationship type. Generic CPL must not silently appropriate domain truth.

---

## 9. Relationship type architecture

B4 adopts a governed relationship-type envelope. Conceptually:

```text
relationship semantic identifier
+
semantic authority / namespace context
+
applicable domain/context
```

The WHAT does not prescribe a specific serialization such as:

```text
automotive:DRIVER
property:TENANT
```

but requires equivalent semantic ownership.

---

## 10. Generic vocabulary boundary

B4 does not require a large universal closed relationship enum. A minimal generic core MAY exist. Domain-specific relationships remain extensible through governed semantic ownership. Therefore:

```text
DRIVER
```

need not become a universal CPL relationship. Likewise:

```text
TENANT
OPERATOR
```

may remain domain-specific.

---

## 11. Arbitrary free-text prohibition

The absence of a giant closed enum does not mean arbitrary relationship strings become canonical. A relationship type must be governed and semantically identifiable. Therefore:

```text
free text label
```

alone is insufficient as canonical relationship semantics.

---

## 12. Relationship admission

Canonical relationship establishment conceptually follows:

```text
Relationship Claim
      ↓
Evidence
      ↓
Applicable authority context
      ↓
Relationship admission
      ↓
CanonicalRelationshipDecision
      ↓
Canonical relationship interpretation
```

The physical implementation may compress these stages. Their semantic distinction must survive.

---

## 13. CanonicalRelationshipDecision

The targeted challenge confirmed that B4 requires:

```text
CanonicalRelationshipDecision
```

or a semantically equivalent first-class governed representation. It represents the CPL decision that changes canonical relationship interpretation.

---

## 14. Why decision is distinct from relationship state

A relationship object can express:

```text
what relationship is currently represented
```

but cannot by itself robustly express:

```text
why it was established
why it ended
why it was corrected
what authority supported the change
what prior decision was superseded
when CPL made the decision
```

Therefore:

```text
ContactAssetRelationship
    ≠
CanonicalRelationshipDecision
```

---

## 15. Decision durability

Every material canonical relationship mutation MUST have durable governed decision provenance. The decision must support:

```text
reference
traceability
evidence linkage
authority attribution
decision time
valid-time effect
supersession
audit
```

A transient log or runtime flag is insufficient.

---

## 16. Minimum decision semantics

A `CanonicalRelationshipDecision` must make recoverable at least:

```text
decision identity
decision type
relationship identity
Contact identity
Asset identity
relationship semantic type
supporting evidence
authority/admission context
valid-time effect
decision time
decision result
superseded decision where applicable
provenance
```

This is semantic, not a prescribed schema.

---

## 17. Decision classes

At minimum B4 distinguishes:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

These are semantic decision classes. They are not necessarily persisted as one flat enum.

---

## 18. END

END means:

> The relationship was considered valid and later ceased to be effective.

Thus:

```text
valid until T
```

is historical truth. Ending does not imply earlier invalidity.

---

## 19. CORRECT

CORRECT means:

> The prior canonical interpretation was inaccurate, incomplete, or retrospectively changed on the basis of later authoritative information.

Therefore:

```text
CORRECT
≠ END
```

A correction may change the interpreted valid-time history.

---

## 20. SUPERSEDE

SUPERSEDE means that one canonical decision replaces the current effect of a prior canonical decision without erasing the prior decision. Thus:

```text
D1
 ↓
D2 supersedes D1 current effect
```

while D1 remains historically reconstructable.

---

## 21. Decision supersession invariant

Relationship correction or supersession MUST change current canonical interpretation without erasing prior canonical decision history. This mirrors stabilized Asset identity decision semantics.

---

## 22. Valid time

B4 recognizes:

```text
VALID TIME
```

as the period during which the relationship is considered true or effective in the represented world. Example:

```text
OWNER valid from January to June
```

---

## 23. Decision time

B4 separately recognizes:

```text
DECISION TIME
```

as when CPL established, modified, corrected, or superseded its canonical interpretation. Example:

```text
relationship valid from January
but CPL established that fact in March
```

---

## 24. Valid-time / decision-time invariant

Relationship effective history and CPL decision history are distinct semantic dimensions where retroactive establishment or correction is possible. The system must preserve both sufficiently for reconstruction.

---

## 25. No mandatory bitemporal architecture

The previous distinction does NOT itself require:

```text
bitemporal SQL
system-versioned tables
specific temporal database
```

Those are HOW choices. The WHAT requires semantic reconstructability.

---

## 26. Retroactive establishment

CPL may learn today that a relationship became valid earlier. Conceptually:

```text
Decision time = T3
Valid from = T1
```

This is legitimate. CPL must not falsely represent the relationship as having only begun at T3.

---

## 27. Retroactive correction

CPL may later learn that a previously recorded valid period was wrong. Example:

```text
previous interpretation:
valid from T1

later authoritative interpretation:
valid from T2
```

The valid-time interpretation may change. Decision history must preserve that CPL previously held the earlier interpretation.

---

## 28. Relationship status is not one flat dimension

The challenge established that a simplistic:

```text
ACTIVE / INACTIVE
```

model is semantically insufficient. At minimum B4 must distinguish:

```text
currently effective
historically ended
disputed / unresolved
prior interpretation corrected or superseded
```

These may be represented through a combination of relationship state, decisions, and temporal semantics.

---

## 29. Relationship conflict

Conflict is semantic. Multiple records do not automatically imply contradiction. Example:

```text
Alice OWNER Asset A
Bob OWNER Asset A
```

may represent valid co-ownership. By contrast:

```text
Alice SOLE_OWNER Asset A
Bob SOLE_OWNER Asset A
same valid period
```

may be contradictory if domain semantics define sole ownership as exclusive.

---

## 30. Compatibility authority

Relationship compatibility and cardinality are governed by applicable relationship semantics and domain policy. Generic CPL MUST NOT infer incompatibility merely from record multiplicity.

---

## 31. Cardinality

No universal generic rule such as:

```text
one OWNER per Asset
one MANAGER per Asset
```

is frozen. Applicable semantics may permit:

```text
one
many
bounded many
exclusive one
coexisting many
```

depending on type and domain.

---

## 32. Type-governed cardinality invariant

Relationship cardinality and compatibility are governed by relationship-type/domain semantics, not by generic CPL assumptions. CPL may enforce applicable governed constraints. It does not invent them.

---

## 33. Evidence conflict

Relationship evidence may disagree. Example:

```text
E1 → Alice OWNER
E2 → Bob SOLE_OWNER
```

Generic CPL cannot resolve this merely through confidence or chronology. The applicable authority policy governs admissibility and precedence.

---

## 34. Forbidden evidence precedence

Relationship evidence precedence MUST NOT arise implicitly from:

```text
latest evidence wins
highest confidence wins
first inserted wins
last inserted wins
implementation preference
administrator preference
```

unless applicable policy explicitly grants such properties authoritative significance.

---

## 35. Unresolved relationship truth

Where conflicting evidence cannot be governedly resolved, valid outcomes include:

```text
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
HOLD
```

or semantically equivalent states. B4 must not force unsupported canonical mutation.

---

## 36. Relationship establishment idempotency

Repeated execution of the same governed relationship establishment operation must not create duplicate logical relationship state. Idempotency is based on:

```text
same governed establishment/request identity
+
same applicable execution scope
```

not merely similarity of content.

---

## 37. Content similarity is insufficient

The following does NOT by itself prove the same establishment operation:

```text
same Contact
same Asset
same relationship type
```

because the records may represent:

```text
different effective periods
new relationship after earlier end
distinct authoritative assertions
correction
separate legal events
```

---

## 38. Relationship idempotency invariant

Relationship establishment idempotency is defined by governed operation identity, not by endpoint/type similarity. Similarity may support duplicate assessment. It does not define request identity.

---

## 39. Asset merge interaction

When Asset B becomes canonically represented by Asset A:

```text
B → A
```

the default generic relationship behavior is:

```text
PRESERVE relationship identity
PRESERVE original Asset endpoint
ALLOW current navigation via canonical Asset A
DO NOT semantically reassign relationship merely because B merged
```

---

## 40. Asset correction interaction

If B later becomes independently canonical again following Asset correction, relationship history requires no artificial reconstruction. The original Asset endpoint was preserved. Current navigation changes according to the corrected Asset canonical topology.

---

## 41. Contact merge interaction

Likewise, when:

```text
Contact B → Contact A
```

the generic relationship behavior is:

```text
PRESERVE relationship identity
PRESERVE original Contact endpoint
ALLOW current navigation via canonical Contact A
DO NOT semantically rewrite relationship
```

---

## 42. Contact correction interaction

If a Contact merge is later corrected, current relationship navigation can follow the corrected Contact topology while preserving original relationship attribution. The relationship object itself is not recreated merely because endpoint representation changes.

---

## 43. Double endpoint evolution

Example:

```text
historical R:
Contact B ↔ Asset Y

later:
B → A
Y → X
```

Current view may expose:

```text
A ↔ X
```

while historical relationship identity remains:

```text
B ↔ Y
```

This remains valid even if one or both endpoint canonical decisions are later corrected.

---

## 44. Endpoint evolution invariant

Canonical endpoint evolution affects current relationship navigation and interpretation; it does not, by itself, mutate the historical ContactAssetRelationship. Any true semantic relationship change requires independent relationship governance.

---

## 45. Asset merge does not settle relationship truth

The fact that:

```text
Asset A = Asset B physically
```

does not establish:

```text
relationship(A) = relationship(B)
```

or settle conflicts between relationship assertions attached to A and B. Relationship truth retains its own authority model.

---

## 46. Contact merge does not settle relationship truth

Likewise, merging two Contact identities does not automatically determine whether their historical relationships are:

```text
equivalent
duplicative
conflicting
coexisting
superseding
```

Those are relationship semantics.

---

## 47. Relationship historical endpoint preservation

B4 MUST preserve sufficient provenance to reconstruct the endpoint identities under which a relationship was originally established. Thus:

```text
original Contact endpoint
original Asset endpoint
```

remain historically meaningful despite canonical evolution.

---

## 48. Current navigation vs historical attribution

The generic model distinguishes:

```text
CURRENT CANONICAL NAVIGATION
```

from:

```text
HISTORICAL ENDPOINT ATTRIBUTION
```

Neither substitutes for the other.

---

## 49. Relationship identity survives endpoint correction

A correction of Contact or Asset canonical topology does not create a new logical relationship merely because its current resolved endpoint changes. Stable relationship identity remains continuous.

---

## 50. Relationship mutation after endpoint evolution

If domain semantics genuinely require changing relationship truth after an endpoint merge/correction, that change must be expressed by an independent governed:

```text
CanonicalRelationshipDecision
```

It must not be hidden inside endpoint canonicalization.

---

## 51. Relationship type namespace

Each relationship type must have an identifiable semantic authority context. Conceptually:

```text
type identifier
+
authority namespace/context
```

This prevents semantic collisions between domains.

---

## 52. Domain relationship type

A domain-specific type such as:

```text
DRIVER
```

may be recognized inside the generic CPL relationship envelope while its semantics remain owned by the automotive domain. Generic CPL stores/governs continuity. The automotive domain owns what DRIVER means and which evidence establishes it.

---

## 53. Generic type

A generic CPL relationship type may exist only where its semantics are sufficiently cross-domain and governed centrally. B4 v0.1 does not yet require a mandatory generic type list.

---

## 54. Relationship vocabulary residual

The remaining vocabulary question is now narrow:

> Does B4 need a tiny mandatory generic relationship core, or can all relationship semantics be governed through extensible typed namespaces?

This is non-blocking for the repaired authority model and should be settled during B4 WHAT consolidation.

---

## 55. Ownership caution

Even if OWNER becomes a generic semantic identifier:

```text
OWNER
```

must not imply generic CPL authority to adjudicate legal ownership. Domain authority still determines admissibility and truth.

---

## 56. Relationship does not imply authorization

A relationship may be an authorization input. It does not itself decide authorization. Thus:

```text
Alice OWNER Asset A
```

does not automatically produce:

```text
Alice may perform action X
```

without an authorization policy.

---

## 57. Authorization invariant

ContactAssetRelationship may contribute evidence to authorization systems but MUST NOT become the generic authorization decision engine.

---

## 58. Contact identity does not imply relationship truth

B3 identity resolution establishes who the Contact is. It does not establish their relationship to an Asset. Therefore:

```text
authenticated Contact
+
resolved Asset
```

does NOT imply:

```text
valid ContactAssetRelationship
```

---

## 59. Relationship state does not imply identity truth

Conversely, a recorded relationship must not redefine Contact or Asset identity. Thus:

```text
relationship says Contact B ↔ Asset Y
```

does not prevent canonical Contact or Asset correction. Relationship history follows governed endpoint continuity.

---

## 60. Decision/evidence continuity

A later correction must preserve the evidence and decision chain explaining earlier canonical relationship interpretation. Conceptually:

```text
Evidence E1
 ↓
Decision D1
 ↓
canonical relationship interpretation
 ↓
Evidence E2
 ↓
Decision D2
type = CORRECT
 ↓
D2 supersedes D1 current effect
 ↓
corrected interpretation
```

---

## 61. No historical erasure

Correction MUST NOT transform history into:

```text
D1 never existed
```

or:

```text
E1 was never received
```

The earlier evidence may now be considered wrong or insufficient. Its historical existence remains relevant.

---

## 62. Current truth and decision history

B4 supports simultaneously:

```text
CURRENT TRUTH:
relationship is not considered valid for T1
```

and:

```text
GOVERNANCE HISTORY:
CPL previously considered the relationship valid for T1
based on E1 and D1
```

This is intentional.

---

## 63. Relationship decision supersession

Canonical relationship decision history must remain reconstructable through supersession or semantically equivalent governance continuity. The WHAT does not prescribe a linked-list implementation.

---

## 64. No silent relationship mutation

Any material canonical relationship change must be attributable to a governed canonical relationship decision. Prohibited:

```text
silent status update
silent endpoint reassignment
silent effective-date rewrite
silent relationship deletion
silent correction
```

when these materially change canonical interpretation without decision provenance.

---

## 65. Physical deletion prohibition for historical relationship state

A relationship that has ended or been corrected should not ordinarily be physically erased merely to express its non-current status. Historical provenance must remain reconstructable. Retention policy may exist separately.

---

## 66. Relationship query semantics

B4 should support conceptual queries such as:

```text
current Assets related to Contact C
current Contacts related to Asset A
historical relationships for Contact C
historical relationships for Asset A
relationship history for relationship R
```

without requiring historical data rewriting.

---

## 67. Query result canonicalization

A current query MAY resolve endpoints to their current canonical representatives. A historical query must be capable of exposing historical endpoint attribution. Query mode/contract belongs downstream. The semantic distinction is required.

---

## 68. Relationship conflict during Asset merge

Where relationship conflict prevents safe interpretation after a proposed Asset merge, the Asset merge may remain:

```text
HOLD
```

without altering the domain determination that the Assets represent the same physical object. This preserves authority separation.

---

## 69. Relationship conflict during Contact merge

Likewise, Contact canonical merge does not authorize arbitrary relationship collapse. Any necessary relationship reconciliation must respect relationship semantics.

---

## 70. Domain policy input

A domain policy may define:

```text
allowed relationship types
evidence classes
authority classes
cardinality
compatibility
conflict rules
valid-time rules
adjudication precedence
```

Generic CPL consumes and enforces those semantics within its envelope.

---

## 71. No domain policy invention

Generic CPL MUST NOT create domain-specific relationship truth merely because no policy is available. Where policy is required but absent, a governed non-resolution outcome is preferable.

---

## 72. Confidence rule

Confidence may describe evidence quality. Confidence does not equal authority. Therefore:

```text
confidence = 0.99
```

does not independently establish relationship state.

---

## 73. ML/LLM boundary

ML/LLM systems may contribute:

```text
evidence extraction
classification
candidate type identification
conflict detection
recommendation
```

They do not independently acquire canonical relationship decision authority.

---

## 74. Relationship establishment composition

A relationship establishment operation MUST NOT silently create missing Contact or Asset identities unless a separately governed composition explicitly authorizes such behavior. Thus:

```text
relationship establishment
≠ Contact creation
≠ Asset creation
```

---

## 75. Non-success semantics

Relationship admission may correctly result in:

```text
NOT_FOUND
INVALID
UNAUTHORIZED
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
HOLD
ALREADY_EXISTS
```

or equivalent semantics. These are not interchangeable with technical execution failure.

---

## 76. Technical failure separation

A database exception or execution failure must not be represented as:

```text
CONTRADICTORY
UNRESOLVED
HOLD
```

unless that domain state genuinely exists. Execution state and relationship state remain distinct.

---

## 77. R-B4-R01 incorporation

```text
Durable CanonicalRelationshipDecision

INCORPORATED
```

---

## 78. R-B4-R02 incorporation

```text
Valid-time / decision-time distinction

INCORPORATED
```

---

## 79. R-B4-R03 incorporation

```text
Stable logical relationship identity
independent of current canonical endpoints

INCORPORATED
```

---

## 80. R-B4-R04 incorporation

```text
Governed establishment/request identity
for idempotency

INCORPORATED
```

---

## 81. R-B4-R05 incorporation

```text
Relationship evidence/conflict precedence
governed through applicable authority policy

INCORPORATED
```

---

## 82. R-B4-R06 incorporation

```text
Endpoint merge/correction:
historical preservation
+
current canonical navigation
+
no implicit relationship mutation

INCORPORATED
```

---

## 83. R-B4-R07 incorporation

```text
Cardinality and compatibility
type/domain governed

INCORPORATED
```

---

## 84. R-B4-R08 incorporation

```text
END
≠ CORRECT
≠ SUPERSEDE

INCORPORATED
```

---

## 85. New invariant B4-RI18 — Stable relationship identity

A ContactAssetRelationship has persistent governed identity independent of current Contact and Asset canonical representations.

---

## 86. B4-RI19 — Relationship decision durability

Material canonical relationship mutation requires durable governed CanonicalRelationshipDecision provenance.

---

## 87. B4-RI20 — Decision supersession

Relationship correction or supersession changes current canonical effect without erasing prior canonical decisions.

---

## 88. B4-RI21 — Valid-time / decision-time distinction

Relationship effective history and CPL decision history remain semantically distinguishable where retroactive establishment or correction applies.

---

## 89. B4-RI22 — Endpoint evolution preservation

Contact or Asset canonical evolution does not itself rewrite relationship identity, semantics, or historical attribution.

---

## 90. B4-RI23 — Relationship idempotency identity

Relationship establishment replay is governed by operation identity, not endpoint/type similarity.

---

## 91. B4-RI24 — Conflict policy authority

Relationship conflict and evidence precedence derive from applicable semantic/domain authority policy, not generic implementation heuristics.

---

## 92. B4-RI25 — Type-governed cardinality

Cardinality, coexistence and incompatibility are governed by relationship-type/domain semantics.

---

## 93. B4-RI26 — Lifecycle distinction

END, CORRECT, and SUPERSEDE are distinct semantic relationship changes.

---

## 94. B4-RI27 — Canonical relationship decision requirement

Every material change in canonical relationship interpretation must be attributable to a durable governed decision.

---

## 95. B4-RI28 — Historical endpoint continuity

Original Contact and Asset relationship endpoints remain reconstructable despite later canonical endpoint evolution.

---

## 96. B4-RI29 — Relationship/authorization separation

Relationship truth may be an authorization input but is not itself the authorization decision.

---

## 97. B4-RI30 — Domain semantic ownership

Generic CPL governs relationship continuity and canonical representation without automatically acquiring domain authority over the semantics of domain-specific relationship types.

---

## 98. Open questions after repair

The challenge has substantially reduced the relationship open set. Remaining:

```text
O-B4-R01
Does CPL require a mandatory minimal generic type core?
    → NARROWED / NON-BLOCKING

O-B4-R05
Exact implementation-facing status representation
    → PARTIALLY RESOLVED semantically

Potential consolidation item:
How relationship decisions and Asset identity decisions
interact transactionally during complex reconciliation.
```

These do not invalidate the repaired authority model.

---

## 99. Resolved questions

```text
O-B4-R02
Type namespace / domain extension
    → RESOLVED AT WHAT LEVEL

O-B4-R03
CanonicalRelationshipDecision
    → REQUIRED

O-B4-R04
Logical relationship identity
    → RESOLVED

O-B4-R06
Cardinality / conflict authority
    → RESOLVED AT WHAT LEVEL

O-B4-R07
Valid time / decision time
    → RESOLVED

O-B4-R08
Asset endpoint merge/correction behavior
    → RESOLVED AT GENERIC WHAT LEVEL

O-B4-R09
Contact endpoint merge/correction behavior
    → RESOLVED AT GENERIC WHAT LEVEL

O-B4-R10
Relationship idempotency
    → RESOLVED
```

---

## 100. Cross-model alignment

The stabilized Asset and repaired Relationship submodels now form:

```text
ASSET IDENTITY

Evidence
 ↓
AssetIdentityResolution
 ↓
CanonicalAssetIdentityDecision
 ↓
Canonical Asset Interpretation
```

and:

```text
RELATIONSHIP

Evidence / authority
 ↓
Relationship Admission
 ↓
CanonicalRelationshipDecision
 ↓
Canonical Relationship Interpretation
```

They share governance structure while preserving distinct authorities.

---

## 101. No forced implementation symmetry

The conceptual symmetry does not mean both domains must have identical:

```text
tables
classes
APIs
state machines
services
```

Those remain HOW decisions.

---

## 102. Current B4 ontology candidate

B4 now contains at least:

```text
Asset
AssetIdentifier
AssetIdentityResolution
CanonicalAssetIdentityDecision
Domain Projection
ExternalReference
ContactAssetRelationship
CanonicalRelationshipDecision
```

These are distinct governed semantics.

---

## 103. Re-challenge scope

The repaired model should now be tested narrowly against:

```text
RC-B4-R01
Can endpoint canonical changes rewrite relationship identity?

RC-B4-R02
Can END and CORRECT still collapse?

RC-B4-R03
Can retroactive correction erase decision history?

RC-B4-R04
Can content similarity define relationship identity/idempotency?

RC-B4-R05
Can evidence conflict be resolved through generic heuristics?

RC-B4-R06
Can global cardinality rules leak into CPL?

RC-B4-R07
Can relationship canonical state change without durable decision?

RC-B4-R08
Can Contact/Asset merge mutate relationship semantics implicitly?

RC-B4-R09
Can domain relationship semantics leak into generic CPL authority?

RC-B4-R10
Can relationship truth become authorization automatically?

RC-B4-R11
Can valid-time correction destroy decision-time history?

RC-B4-R12
Can simultaneous valid same-type relationships be incorrectly deduplicated?
```

---

## 104. Re-challenge acceptance condition

The Relationship submodel becomes stabilized only if the repaired model shows that:

```text
stable relationship identity survives
decision history survives
valid time and decision time survive
endpoint evolution does not rewrite relationship truth
domain semantic authority remains bounded
idempotency does not become duplicate inference
cardinality remains policy-governed
authorization remains external
```

---

## 105. Governance status

```text
B4 Asset Authority submodel
  STABILIZED

B4 Relationship Object & Authority Model v0
  MATERIALIZED
  CHALLENGED
  REPAIR_REQUIRED

B4 Relationship Targeted Challenge v0
  COMPLETED
  REPAIR_REQUIRED

B4 Relationship Object & Authority Model v0.1
  REPAIRED
  R-B4-R01 → R-B4-R08 INCORPORATED
  PROPOSED FOR TARGETED RE-CHALLENGE

B4 Relationship submodel
  NOT YET STABILIZED

B4 WHAT
  NOT FROZEN

B4 Requirement Matrix
  NOT AUTHORIZED

B4 Execution Mandate
  NOT AUTHORIZED

B4 Implementation
  NOT AUTHORIZED
```

---

## 106. Final declaration

```text
B4_RELATIONSHIP_OBJECT_AND_AUTHORITY_MODEL_v0.1

REPAIR STATUS:
  8 / 8 INCORPORATED

NEW REQUIRED SEMANTIC OBJECT:
  CanonicalRelationshipDecision

RELATIONSHIP IDENTITY:
  STABLE GOVERNED OBJECT

TEMPORAL MODEL:
  VALID TIME ≠ DECISION TIME

ENDPOINT EVOLUTION:
  CURRENT NAVIGATION CHANGE
  ≠ HISTORICAL RELATIONSHIP REWRITE

IDEMPOTENCY:
  GOVERNED REQUEST IDENTITY

CARDINALITY:
  TYPE / DOMAIN GOVERNED

EVIDENCE CONFLICT:
  AUTHORITY-POLICY GOVERNED

AUTHORIZATION:
  OUTSIDE RELATIONSHIP DECISION

READY FOR:
  B4_RELATIONSHIP_TARGETED_RE_CHALLENGE_v0.1

NOT READY FOR:
  B4 WHAT FREEZE
  REQUIREMENT MATRIX
  EXECUTION MANDATE
  IMPLEMENTATION
```

**END — B4 Relationship Object & Authority Model v0.1**

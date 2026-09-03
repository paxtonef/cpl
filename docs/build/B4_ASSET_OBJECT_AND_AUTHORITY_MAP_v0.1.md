# CPL — B4 Asset Object & Authority Map v0.1

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Asset Object & Authority Map
**Version:** v0.1
**Status:** REPAIRED — PROPOSED FOR TARGETED RE-CHALLENGE
**Repair source:** `B4_ASSET_AUTHORITY_TARGETED_CHALLENGE_v0`
**Implementation authorization:** NONE

---

## 1. Purpose of v0.1

v0.1 repairs the B4 Asset authority model following the targeted challenge. It incorporates exactly the authorized repair boundary:

```text
R-B4-01  Durable CanonicalAssetIdentityDecision
R-B4-02  Canonical correction through supersession
R-B4-03  Dependency non-convergence
R-B4-04  Historical target preservation
R-B4-05  Explicit resolver precedence governance
```

It does **not** attempt to complete the entire B4 WHAT. In particular:

```text
O-B4-03 ContactAssetRelationship vocabulary
```

remains open. No implementation structure is authorized by this artifact.

---

## 2. Fundamental Asset ontology

CPL distinguishes:

```text
PHYSICAL OBJECT
      │
      ▼
    Asset
      │
      ├── AssetIdentifier
      ├── AssetIdentityResolution
      ├── CanonicalAssetIdentityDecision
      ├── ContactAssetRelationship
      ├── Case
      ├── Domain Projection
      └── ExternalReference
```

These objects must not be collapsed. In particular:

```text
Asset
    ≠ Physical Object

AssetIdentifier
    ≠ Asset

AssetIdentityResolution
    ≠ Asset

AssetIdentityResolution
    ≠ CanonicalAssetIdentityDecision

CanonicalAssetIdentityDecision
    ≠ Asset
```

---

## 3. Asset

An `Asset` is the CPL persistent identity through which the product represents and maintains continuity around a physical object. It is not itself the physical object. Therefore:

```text
physical object
      ↓ represented through
Asset
```

not:

```text
physical object = database row
```

This distinction permits CPL to represent uncertainty, duplicate candidate identities, reconciliation, merge and later correction without pretending that database identity and physical reality are identical.

---

## 4. Asset identity

`asset_id` is CPL canonical record identity. It is not a domain identifier. Therefore:

```text
asset_id ≠ VIN
asset_id ≠ registration
asset_id ≠ serial number
asset_id ≠ manufacturer identifier
asset_id ≠ external system identifier
```

No external identifier becomes canonical CPL identity merely because it is strong, unique within a source, or normally reliable.

---

## 5. AssetIdentifier

`AssetIdentifier` records an identifier associated with an Asset. Its existence means:

> CPL has a governed record that this identifier has been associated with this Asset.

It does not necessarily mean:

> This identifier conclusively establishes physical identity.

Therefore:

```text
identifier assertion
      ≠
physical identity determination
```

---

## 6. Identifier authority

Identifier validity may be domain-specific. CPL may:

```text
store identifier
preserve provenance
preserve source
preserve temporal information
preserve verification state
expose identifier state
```

CPL MUST NOT invent domain validity where the applicable domain authority owns that determination. For automotive identity, that boundary remains with VIR where already established.

---

## 7. Identifier match invariant

The following must never be equivalent:

```text
same identifier
      =
same physical Asset
```

The permitted chain is:

```text
identifier match
      ↓
identity evidence / hypothesis
      ↓
authorized identity resolution
      ↓
governed determination
```

Only after that may canonical reconciliation be considered.

---

## 8. AssetIdentityResolution

`AssetIdentityResolution` represents a governed determination concerning physical identity. Conceptually it answers:

> What has the authorized identity-resolution process determined about the relationship between these Asset representations and physical reality?

Possible semantic outcomes include:

```text
SAME_PHYSICAL_ASSET
NOT_SAME_PHYSICAL_ASSET
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
FAILED
```

The exact persistence representation remains a HOW decision unless separately frozen.

---

## 9. Identity determination authority

Physical identity is determined by the authorized identity resolver for the applicable domain. For automotive:

```text
VIR
 ↓
AssetIdentityResolution
```

VIR may determine:

```text
Asset A and Asset B represent
the same physical vehicle
```

or that they do not, or that the matter cannot currently be resolved. VIR does not thereby obtain CPL canonical mutation authority.

---

## 10. Authority separation

The central B4 authority invariant is:

> DOMAIN DETERMINES PHYSICAL IDENTITY; CPL GOVERNS CANONICAL IDENTITY.

Formally:

```text
DOMAIN
"What physical object is this?"
          │
          ▼
Identity Determination
          │
──────────┼────────── authority boundary
          │
          ▼
CPL
"How is that physical object represented
canonically in the product?"
```

Neither side substitutes itself for the other.

---

## 11. Resolver prohibition

An authorized domain resolver MUST NOT directly perform canonical CPL merge. Thus a resolver output must not semantically collapse:

```text
identity determination
+
canonical mutation
```

into one action. For example:

```text
INVALID RESOLVER SEMANTICS

MERGE ASSET B INTO ASSET A
```

The resolver should instead establish the relevant physical identity conclusion. Canonical action remains downstream.

---

## 12. Canonical merge authority

Only CPL canonical Asset identity authority may execute a canonical Asset merge. This authority is constrained. It does not mean:

```text
CPL may merge whenever it wishes
```

It means:

```text
admissible physical identity determination
            +
CPL merge-admission conditions
            ↓
possible canonical merge
```

---

## 13. Merge admission

A positive physical identity determination is necessary but not necessarily sufficient for canonical merge. Therefore:

```text
SAME_PHYSICAL_ASSET
        ↓
CPL Merge Admission
        ├── ADMIT
        └── HOLD / REFUSE
```

A merge may be held where structural reconciliation is not safely determined. This prevents:

```text
domain truth
    ↓
automatic database topology mutation
```

---

## 14. Negative merge rule

The following MUST NOT independently cause canonical merge:

```text
identifier equality
similarity
probabilistic similarity
record resemblance
execution order
administrative convenience
unresolved hypothesis
```

Nor may these resolution states cause merge:

```text
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
FAILED
```

The default under unresolved identity is separation.

---

## 15. Human/admin boundary

Human intervention may contribute:

```text
evidence
review
authorized adjudication
exception analysis
```

where policy permits. Human intervention does not constitute an unrestricted bypass around canonical merge admission. Therefore:

```text
admin click
   ≠
automatic authority to merge
```

---

## 16. CanonicalAssetIdentityDecision — new required semantic object

The targeted challenge established that physical identity resolution alone cannot represent CPL canonical history. B4 therefore recognizes:

```text
CanonicalAssetIdentityDecision
```

as a distinct semantic object. It represents a governed CPL decision affecting the current canonical representation of Asset identity.

---

## 17. Resolution ≠ Decision

This distinction is normative:

```text
AssetIdentityResolution
        ≠
CanonicalAssetIdentityDecision
```

The first answers:

> What has been determined about physical identity?

The second answers:

> What canonical representation has CPL authorized on the basis of admissible determinations and CPL governance?

Example:

```text
Resolution R1:
A = B physically

        ↓

CPL Decision D1:
HOLD
```

is valid. Therefore:

```text
SAME_PHYSICAL_ASSET
    ≠ necessarily
MERGE
```

---

## 18. Canonical decision durability

Every canonical Asset identity mutation produced by merge or correction MUST have durable governed decision provenance. A canonical decision must be sufficiently first-class to permit:

```text
reference
traceability
audit
authority attribution
supporting-resolution linkage
temporal reconstruction
supersession
```

A transient runtime choice or unstructured application log is insufficient.

---

## 19. Minimum semantic content of canonical identity decision

The WHAT requires sufficient information to establish:

```text
decision identity
decision type
affected Asset identities
resulting canonical representation
supporting identity determination
decision authority
decision time
decision status
provenance
supersession relationship where applicable
```

This is a semantic requirement. It does NOT prescribe:

```text
SQL table
ORM model
event-store record
API representation
specific field names
specific schema topology
```

---

## 20. Merge decision

A canonical merge decision establishes a current canonical representation such as:

```text
Asset A = surviving canonical Asset
Asset B = merged historical Asset
```

It MUST NOT mean:

```text
Asset B never existed
```

and MUST NOT require:

```text
DELETE Asset B
```

---

## 21. Historical merge invariant

Asset merge changes the current canonical representation of a physical object; it does not rewrite the historical fact that multiple Asset identities previously existed. Therefore the losing Asset remains historically addressable and traceable.

---

## 22. Merge provenance

A canonical merge must preserve the chain:

```text
Evidence
   ↓
AssetIdentityResolution
   ↓
CanonicalAssetIdentityDecision
   ↓
Canonical representation
```

The product must be capable of explaining why the current representation exists.

---

## 23. Erroneous merge

B4 explicitly recognizes that a previously admissible determination may later be superseded by better authoritative evidence. Example:

```text
T1:
A and B separate

T2:
Resolution R1
A = B

T3:
Decision M1
MERGE B → A

T4:
new evidence

T5:
Resolution R2
A ≠ B
```

CPL MUST be able to represent the corrected current canonical truth without falsifying T1–T3.

---

## 24. Canonical correction

The semantic operation for correcting an erroneous prior canonical identity decision is:

```text
CANONICAL IDENTITY CORRECTION
```

not historical erasure. A correction changes the current effect of the prior decision. It does not cause the prior decision to become nonexistent.

---

## 25. Correction by supersession

Canonical identity history follows:

```text
append / supersede
```

not:

```text
rewrite / erase
```

Therefore:

```text
Resolution R1
     ↓
Merge Decision M1
     ↓
current A ← B
     ↓
Resolution R2
     ↓
Correction Decision C1
supersedes current effect of M1
     ↓
current A and B distinct
```

while M1 remains historically true as a decision that occurred.

---

## 26. Canonical correction invariant

Canonical correction changes the current effect of a prior canonical identity decision; it MUST NOT erase, retroactively mutate into non-existence, or falsify that prior decision or the evidence that supported it at the time.

---

## 27. Correction requirements

Where correction requires restoration of separate canonical identities, CPL MUST preserve at least:

```text
original Assets
original merge decision
original supporting resolution
later authoritative resolution
correction decision
decision supersession chain
affected historical provenance
```

The precise transaction algorithm remains HOW.

---

## 28. Asset merge ≠ dependency merge

The targeted challenge established:

> Canonical Asset identity convergence MUST NOT automatically cause semantic convergence of dependent records.

Therefore:

```text
Asset A = Asset B physically
```

does NOT establish:

```text
relationships(A) = relationships(B)
cases(A) = cases(B)
projections(A) = projections(B)
external references(A) = external references(B)
```

---

## 29. Dependency families

At minimum, the rule applies to:

```text
AssetIdentifiers
ContactAssetRelationships
Cases
Domain Projections
ExternalReferences
AssetIdentityResolutions
historical references
```

Other dependent families inherit the same principle unless explicitly governed otherwise.

---

## 30. Dependency disposition

Canonical Asset reconciliation requires governed treatment of affected dependencies. Conceptual disposition classes may include:

```text
PRESERVE_AS_HISTORICAL
REASSOCIATE
SUPERSEDE
RECONCILE
HOLD
REJECT_CONFLICT
```

These describe the semantic space. They do not establish that every dependency family supports every disposition.

---

## 31. Per-family authority

Dependency treatment is governed by the semantics and authority of the dependency family. Asset identity authority MUST NOT silently acquire authority over unrelated dependent truth. Therefore:

```text
Asset merge
    ≠
authority to adjudicate every attached object
```

---

## 32. Historical target preservation

Where a dependent record historically referenced Asset B, later canonical reconciliation MUST NOT falsely assert that it originally referenced Asset A. B4 therefore distinguishes:

```text
ORIGINAL HISTORICAL TARGET
             ≠
CURRENT CANONICAL TARGET
```

where the distinction is semantically relevant.

---

## 33. Historical reconstructability

CPL MUST preserve sufficient provenance to reconstruct the Asset identity under which a dependent record was originally created, asserted, observed or referenced. This applies even when current navigation resolves through another canonical Asset.

---

## 34. Current navigation

Historical preservation does not prohibit convenient current navigation. For example:

```text
historical:
Case C → Asset B

canonical identity:
B → A

current lookup:
A exposes C
```

may be valid. But the system must not transform the historical claim into:

```text
Case C originally referenced A
```

if it did not.

---

## 35. ContactAssetRelationship independence

Asset identity reconciliation does not adjudicate relationship truth. Example:

```text
Asset A
OWNER = Alice

Asset B
OWNER = Bob
```

followed by:

```text
A = B physically
```

does NOT establish:

```text
Alice + Bob are simultaneous owners
```

nor:

```text
Bob supersedes Alice
```

nor any other relationship conclusion without the applicable relationship semantics and evidence.

---

## 36. Relationship authority invariant

Asset identity reconciliation MUST NOT itself determine the truth, chronology, validity or supersession of ContactAssetRelationships. This is separate from the still-open question of the complete B4 relationship vocabulary.

---

## 37. Case preservation

Cases attached historically to separate Asset identities remain historically meaningful. Canonical reconciliation may permit unified current discovery. It MUST NOT rewrite the historical identity context under which a Case existed.

---

## 38. Domain projection preservation

Domain projections may contain domain-derived state whose authority does not belong to generic CPL Asset identity governance. Therefore Asset merge does not automatically merge or select between competing domain projections. Applicable domain semantics must govern their treatment.

---

## 39. ExternalReference preservation

An ExternalReference records a relationship between an external system's identity and CPL representation. If:

```text
External system X
    historically referenced Asset B
```

a later merge B → A does not mean:

```text
External system X
    historically referenced Asset A
```

Canonical navigation and historical assertion remain distinct.

---

## 40. Resolver conflict

Multiple identity determinations may conflict. Example:

```text
R1 → SAME_PHYSICAL_ASSET
R2 → NOT_SAME_PHYSICAL_ASSET
```

CPL MUST NOT invent resolution by applying arbitrary generic heuristics.

---

## 41. Forbidden implicit resolver precedence

Resolver precedence MUST NOT arise implicitly from:

```text
latest result wins
first result wins
highest numeric confidence wins
execution order
database insertion order
implementation preference
```

unless an applicable domain authority policy explicitly gives one of those properties authoritative meaning.

---

## 42. Resolver precedence authority

Resolver precedence derives from:

```text
explicit applicable domain authority policy
```

or:

```text
authorized domain adjudication
```

where such mechanisms exist. Thus CPL may consume governed precedence. It does not invent domain truth precedence.

---

## 43. Contradiction state

Absent applicable governed precedence or adjudication:

```text
conflicting admissible determinations
        ↓
CONTRADICTORY
        ↓
NO MERGE
```

The contradiction remains explicit. CPL does not force closure.

---

## 44. Governed contradiction resolution

Where authorized policy legitimately resolves the conflict:

```text
R1
   \
    → contradiction
   /
R2
      ↓
applicable authority policy
      ↓
governed adjudication
      ↓
resolved identity determination
```

the resulting identity state may again become admissible for canonical consideration. The existence of conflict and its resolution remain traceable.

---

## 45. VIR boundary remains unchanged

For automotive:

> VIR owns automotive identity resolution

continues to hold. v0.1 does not grant VIR:

```text
canonical merge authority
canonical correction authority
generic CPL relationship authority
CPL database topology authority
```

VIR supplies domain-authoritative identity determination according to its governed scope.

---

## 46. CPL boundary remains unchanged

CPL owns:

```text
canonical Asset representation
merge admission
canonical merge decision
canonical correction decision
canonical decision history
product continuity
```

CPL does not thereby own:

```text
automotive physical identity truth
domain projection truth
ownership truth
external system truth
```

unless independently authorized.

---

## 47. Authority matrix

| Concern | Authority |
|---|---|
| CPL `asset_id` | CPL |
| Physical Asset identity | Authorized domain resolver |
| Automotive physical identity | VIR |
| Identifier storage/provenance | CPL |
| Domain validity of identifier | Applicable domain authority |
| Canonical merge admission | CPL |
| Canonical merge execution | CPL |
| Canonical merge decision | CPL |
| Canonical correction decision | CPL |
| Resolver precedence | Applicable domain authority policy/adjudication |
| Relationship truth | Applicable relationship/domain authority |
| Case historical attribution | CPL preservation; case semantics remain with applicable authority |
| Domain projection truth | Domain authority |
| External-reference historical assertion | Preserved as source/provenance fact |

---

## 48. Merge admission model v0.1

The repaired conceptual model is:

```text
Evidence / Identifier Signals
            ↓
Authorized Domain Resolution
            ↓
AssetIdentityResolution
            ↓
Identity-state admissibility
            ↓
Resolver-conflict governance if required
            ↓
CPL structural admission
            ↓
Dependency disposition sufficiency
            ↓
CanonicalAssetIdentityDecision
            ↓
Canonical representation
```

This is a semantic sequence, not a required runtime architecture.

---

## 49. Merge HOLD

A valid positive physical identity determination may produce:

```text
HOLD
```

rather than merge where, for example:

```text
dependency conflict unresolved
canonical survivor unresolved
required provenance insufficient
applicable governance incomplete
```

Thus:

```text
physical truth established
```

and:

```text
canonical restructuring safe
```

remain separate questions.

---

## 50. Correction admission

Similarly, evidence that an old merge is wrong does not authorize uncontrolled mutation. Conceptually:

```text
new authoritative resolution
            ↓
correction required?
            ↓
affected canonical decision identified
            ↓
dependency impact established
            ↓
CPL correction admission
            ↓
CanonicalAssetIdentityDecision
type = CORRECTION
            ↓
superseded canonical effect
```

---

## 51. Correction is not destructive rollback

The following semantic interpretation is forbidden:

```text
CORRECTION
    =
restore database as if merge never happened
```

because the merge did happen in product history. The system instead changes what is canonical now.

---

## 52. Current truth and historical truth

B4 therefore explicitly supports two non-conflicting statements:

```text
HISTORICAL TRUTH:
At T2 CPL treated B as canonically merged into A.

CURRENT TRUTH:
At T5 CPL treats A and B as distinct Assets.
```

Both can be true. This is essential to governed product continuity.

---

## 53. Decision supersession chain

Canonical decision history must be reconstructable as a chain or equivalent governed structure:

```text
D1
 ↓
D2 supersedes D1
 ↓
D3 supersedes D2
```

where applicable. The WHAT does not require a linked-list implementation. It requires semantic reconstructability.

---

## 54. No silent canonical mutation

Any canonical Asset identity mutation MUST be attributable to a governed canonical identity decision. Therefore prohibited:

```text
silent FK rewrites
silent survivor changes
silent unmerge
silent canonical pointer replacement
```

if they alter canonical Asset identity without durable decision provenance.

---

## 55. Merge survivor

Where a merge is admitted, CPL must establish which Asset becomes the current canonical representation. The survivor selection must be governed and traceable. It MUST NOT be inferred merely from:

```text
lower UUID
earlier row
latest row
lexicographic ordering
implementation convenience
```

unless future B4 rules explicitly authorize such a criterion. The complete survivor-selection policy is not invented in v0.1.

---

## 56. Physical deletion prohibition

Canonical Asset merge MUST NOT physically delete the losing Asset merely because it no longer represents the current canonical identity. Historical identity is part of product provenance.

---

## 57. Identifier preservation during merge

Identifiers historically associated with the losing Asset must remain historically reconstructable. Whether an identifier becomes navigable through the surviving canonical Asset is a separate current-state concern. Therefore:

```text
historical identifier attribution
    ≠ necessarily
current canonical identifier presentation
```

---

## 58. Identity resolution preservation

Previous resolutions must remain traceable even when later resolutions supersede their conclusions. A later authoritative resolution does not mean the previous resolution never existed. This parallels canonical decision history.

---

## 59. Evidence preservation

Evidence supporting an earlier identity determination must not be destroyed merely because the conclusion is later superseded. Otherwise the system cannot explain why an earlier canonical decision was reasonable or admissible at its time.

---

## 60. Provenance chain invariant

Where available, CPL must be capable of reconstructing:

```text
Evidence
  ↓
Resolution
  ↓
Canonical Decision
  ↓
Canonical Effect
  ↓
Later Evidence
  ↓
Later Resolution
  ↓
Correction Decision
  ↓
Corrected Canonical Effect
```

This is a core B4 governance property.

---

## 61. O-B4-01 disposition

```text
O-B4-01
Canonical correction mechanics

STATUS:
RESOLVED AT WHAT LEVEL
```

Resolution:

```text
canonical correction
    =
new governed canonical identity decision
that supersedes the current effect
of a prior canonical identity decision
without erasing history
```

Transactional implementation remains downstream.

---

## 62. O-B4-02 disposition

```text
O-B4-02
Dependency treatment during merge

STATUS:
PARTIALLY RESOLVED
```

Resolved:

```text
identity convergence
    ≠ dependency convergence

historical target must remain reconstructable

dependency disposition must be governed
```

Still requiring later B4 consolidation:

```text
exact disposition semantics by dependency family
```

No implementation may invent them silently.

---

## 63. O-B4-03 disposition

```text
O-B4-03
ContactAssetRelationship vocabulary

STATUS:
OPEN
```

v0.1 intentionally does not manufacture a complete vocabulary. The question must be resolved separately before B4 WHAT freeze if the vocabulary lies within B4 frozen scope.

---

## 64. O-B4-04 disposition

```text
O-B4-04
Resolver precedence

STATUS:
RESOLVED
```

Resolution:

```text
explicit applicable domain authority policy
or authorized adjudication
```

Absent such authority:

```text
CONTRADICTORY → NO MERGE
```

---

## 65. O-B4-05 disposition

```text
O-B4-05
Durable Merge Proposal / Decision representation

STATUS:
RESOLVED
```

B4 requires a durable:

```text
CanonicalAssetIdentityDecision
```

or semantically equivalent first-class governed representation. A specific database representation remains HOW.

---

## 66. Invariant registry — retained

The v0 authority invariants remain applicable except where made more precise by v0.1. Core retained invariants include:

```text
Asset identity ≠ external identifier
identifier match ≠ automatic identity
domain resolver determines physical identity
CPL owns canonical Asset representation
domain resolver MUST NOT directly merge CPL Assets
ambiguity MUST NOT cause merge
contradiction MUST NOT cause merge absent governed resolution
merged Asset MUST NOT be physically deleted
human/admin action MUST NOT bypass governed merge admission
```

---

## 67. New invariant B4-AI13 — Decision durability

Every canonical Asset identity mutation MUST possess durable governed decision provenance.

---

## 68. New invariant B4-AI14 — Decision supersession

Canonical correction MUST supersede the current effect of a prior canonical identity decision rather than erase or falsify that decision.

---

## 69. New invariant B4-AI15 — Dependency non-convergence

Canonical Asset identity convergence MUST NOT automatically cause semantic convergence, reassignment or adjudication of dependent records.

---

## 70. New invariant B4-AI16 — Historical target preservation

CPL MUST preserve sufficient provenance to reconstruct the Asset identity originally referenced by historical dependent records where canonical reconciliation changes current navigation.

---

## 71. New invariant B4-AI17 — Resolver precedence governance

Resolver precedence MUST arise only from explicit applicable domain authority policy or authorized adjudication and MUST NOT be inferred from generic implementation characteristics.

---

## 72. New invariant B4-AI18 — Relationship adjudication independence

Asset identity reconciliation MUST NOT itself adjudicate ContactAssetRelationship truth, chronology, validity or supersession.

---

## 73. New invariant B4-AI19 — Resolution/decision separation

AssetIdentityResolution and CanonicalAssetIdentityDecision are distinct governed concepts and MUST NOT be collapsed into one authority-bearing operation.

---

## 74. New invariant B4-AI20 — No silent canonical mutation

Any change to current canonical Asset identity representation MUST be attributable to a durable governed canonical identity decision.

---

## 75. New invariant B4-AI21 — Evidence continuity

Supersession of an identity determination or canonical identity decision MUST NOT erase the evidence and provenance that explain the earlier governed state.

---

## 76. New invariant B4-AI22 — Current/history distinction

Current canonical representation and historical Asset attribution are distinct dimensions and MUST remain jointly reconstructable.

---

## 77. Failure semantics

Where identity or canonical reconciliation cannot safely proceed, the system must prefer explicit non-resolution over invented certainty. Therefore valid outcomes include:

```text
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
HOLD
REJECTED
```

as applicable. Failure to reach merge is not itself a system failure. It may be the correct governed outcome.

---

## 78. Anti-inference rules

Developers and downstream build systems MUST NOT infer from v0.1:

```text
a required table name
a required endpoint
a required ORM model
a required message broker
a required event-sourcing architecture
a required workflow engine
a required API topology
a required correction algorithm
a universal relationship vocabulary
a universal resolver ranking
```

Those decisions require downstream authorization.

---

## 79. Explicitly prohibited implementation shortcuts

Regardless of eventual implementation, B4 semantics prohibit any behavior equivalent to:

```text
same VIN → merge
highest confidence → merge
latest resolver → merge
admin says merge → bypass governance
merge → delete losing Asset
merge → rewrite all historical dependencies
merge → silently combine relationship truth
correction → erase old merge
correction → destroy prior evidence
domain resolver → directly mutate canonical CPL identity
```

---

## 80. Authority boundary after repair

The repaired authority topology is:

```text
                DOMAIN

Evidence
   ↓
Authorized Identity Resolver
   ↓
AssetIdentityResolution
   │
   │ physical identity conclusion
   ▼
══════════ AUTHORITY BOUNDARY ══════════
   │
   ▼
                 CPL

Identity-state admissibility
   ↓
Resolver-conflict governance
   ↓
Canonical structural admission
   ↓
Dependency disposition sufficiency
   ↓
CanonicalAssetIdentityDecision
   ↓
Current canonical Asset representation
```

---

## 81. Correction topology after repair

```text
DOMAIN

Later Evidence
    ↓
Authorized Identity Resolver
    ↓
Later AssetIdentityResolution
    │
════╪════════ AUTHORITY BOUNDARY ═══════
    │
    ▼
CPL

Existing CanonicalAssetIdentityDecision
    ↓
Correction Admission
    ↓
New CanonicalAssetIdentityDecision
type = CORRECTION
    ↓
supersedes prior current effect
    ↓
Corrected canonical representation
```

---

## 82. What v0.1 has resolved

v0.1 now establishes:

```text
WHO determines physical Asset identity
WHO owns canonical merge
WHO owns canonical correction
WHY resolution and canonical decision differ
HOW canonical history must conceptually survive correction
WHY dependencies cannot be blindly converged
WHY historical target attribution must survive
WHO may establish resolver precedence
WHY identifier equality cannot cause merge
```

---

## 83. What v0.1 deliberately does not resolve

Still outside this repaired artifact:

```text
complete ContactAssetRelationship vocabulary
complete dependency-family disposition matrix
precise canonical survivor-selection rules
database schema for CanonicalAssetIdentityDecision
API contracts
transaction strategy
locking strategy
concurrency implementation
event publication mechanics
migration design
test implementation
```

These must not be silently inferred.

---

## 84. Re-challenge admission conditions

v0.1 is ready for targeted re-challenge specifically against:

```text
RC-B4-01
Can a cloned identifier still cause accidental merge?

RC-B4-02
Can mutable identifiers accidentally create canonical identity?

RC-B4-03
Can contradictory resolvers be silently ranked?

RC-B4-04
Can SAME_PHYSICAL_ASSET force unsafe dependency convergence?

RC-B4-05
Can an erroneous historical merge be corrected without erasing history?

RC-B4-06
Can dependencies lose original Asset attribution?

RC-B4-07
Can a domain resolver acquire canonical mutation authority indirectly?

RC-B4-08
Can an administrator bypass canonical admission?

RC-B4-09
Can canonical identity change without durable decision provenance?

RC-B4-10
Can correction destroy the evidence supporting the earlier state?
```

---

## 85. Acceptance criterion for re-challenge

For the authority repair to pass:

```text
RC-B4-01 → RC-B4-10
```

must demonstrate that no unresolved semantic path permits violation of the repaired invariants.

A re-challenge PASS does not freeze all B4 WHAT. It freezes only the repaired Asset authority model sufficiently to allow B4 WHAT work to continue.

---

## 86. Governance status

```text
B4 Asset Object & Authority Map v0:
    MATERIALIZED
    CHALLENGED
    REPAIR_REQUIRED

B4 Asset Object & Authority Map v0.1:
    PRODUCED
    PROPOSED FOR TARGETED RE-CHALLENGE

R-B4-01:
    INCORPORATED

R-B4-02:
    INCORPORATED

R-B4-03:
    INCORPORATED

R-B4-04:
    INCORPORATED

R-B4-05:
    INCORPORATED

O-B4-01:
    RESOLVED AT WHAT LEVEL

O-B4-02:
    PARTIALLY RESOLVED

O-B4-03:
    OPEN

O-B4-04:
    RESOLVED

O-B4-05:
    RESOLVED

B4 WHAT:
    NOT FROZEN

B4 Requirement Matrix:
    NOT AUTHORIZED

B4 Execution Mandate:
    NOT AUTHORIZED

B4 Implementation:
    NOT AUTHORIZED
```

---

## 87. Final status

```text
B4_ASSET_OBJECT_AND_AUTHORITY_MAP_v0.1

STATUS:
    REPAIRED

TARGETED CHALLENGE REPAIRS:
    5 / 5 INCORPORATED

CORE AUTHORITY PRINCIPLE:
    DOMAIN DETERMINES PHYSICAL IDENTITY;
    CPL GOVERNS CANONICAL IDENTITY.

NEW GOVERNED OBJECT:
    CanonicalAssetIdentityDecision

CANONICAL CORRECTION:
    SUPERSESSION, NOT HISTORICAL ERASURE

DEPENDENCY CONVERGENCE:
    NOT IMPLIED BY ASSET IDENTITY CONVERGENCE

HISTORICAL ATTRIBUTION:
    MUST REMAIN RECONSTRUCTABLE

RESOLVER PRECEDENCE:
    DOMAIN-GOVERNED, NEVER IMPLICIT

READY FOR:
    B4 ASSET AUTHORITY TARGETED RE-CHALLENGE v0.1

NOT READY FOR:
    B4 WHAT FREEZE
    REQUIREMENT MATRIX
    EXECUTION MANDATE
    IMPLEMENTATION
```

**END — B4 Asset Object & Authority Map v0.1**

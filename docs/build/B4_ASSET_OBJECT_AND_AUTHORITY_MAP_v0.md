# CPL — B4 Asset Object & Authority Map v0

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Asset Object & Authority Map
**Version:** v0
**Status:** PROPOSED FOR CHALLENGE
**Canonical baseline:** `main @ cad880c`
**Upstream artifact:** `B4_ASSETS_AND_RELATIONSHIPS_WHAT_DEFINITION_v0.md`
**Implementation authorization:** NONE

---

## 1. Purpose

This artifact defines the objects, semantic authorities and authority boundaries governing B4 Asset identity and Contact–Asset relationships.

It resolves the principal open question left by the B4 WHAT Definition v0:

```text
Asset Merge Authority
```

without turning domain-specific identity resolvers into owners of CPL canonical identity.

The governing separation is:

```text
REAL-WORLD OBJECT
       │
       ▼
DOMAIN IDENTITY DETERMINATION
       │
       ▼
ASSET IDENTITY RESOLUTION
       │
       ▼
CPL CANONICAL ADMISSION
       │
       ▼
CPL CANONICAL EXECUTION
       │
       ▼
CANONICAL ASSET REPRESENTATION
```

These stages MUST NOT be collapsed merely because one software component could technically perform several of them.

---

## 2. Fundamental authority invariant

B4 adopts:

> DOMAIN DETERMINES PHYSICAL IDENTITY; CPL GOVERNS CANONICAL IDENTITY.

Consequently:

```text
Domain Resolver
    ≠ CPL Asset authority

Physical identity determination
    ≠ canonical merge decision

Canonical merge admission
    ≠ merge execution

Identifier match
    ≠ physical identity determination
```

---

## 3. Object map

The principal B4 objects are:

```text
Asset
│
├── AssetIdentifier
│
├── AssetIdentityResolution
│
├── Domain Projection
│      └── VehicleDetail [existing example]
│
├── ExternalReference
│
└── ContactAssetRelationship
       │
       ├── Contact
       ├── relationship semantics
       ├── temporal state
       └── authority / provenance
```

Supporting conceptual objects include:

```text
Asset Evidence
Identity Determination
Merge Admission
Canonical Merge Decision
Canonical Correction Decision
Relationship Evidence
```

Not every conceptual object necessarily requires a dedicated persistence table or public API. That is a downstream HOW decision unless later requirements state otherwise.

---

## 4. Asset

### Nature

`Asset` is the canonical CPL representation of a persistent object.

```text
real-world object
      ↓
CPL Asset
      ↓
asset_id
```

### Authority

CPL owns:

```text
canonical Asset identity
canonical Asset lifecycle
canonical Asset relationships
canonical representation continuity
```

CPL does NOT thereby acquire authority to determine every domain-specific fact about the physical object.

### Invariant

```text
Asset identity
≠ AssetIdentifier
≠ Domain Projection
≠ ExternalReference
≠ ContactAssetRelationship
```

---

## 5. AssetIdentifier

### Nature

An `AssetIdentifier` is identity-bearing evidence associated with an Asset. Examples may include:

```text
VIN
registration
serial number
registry identifier
manufacturer identifier
domain identifier
```

### Authority

An identifier MAY:

```text
support lookup
support resolution
support conflict detection
support identity evidence
```

An identifier MUST NOT independently:

```text
create canonical Asset identity
merge Assets
override a domain identity determination
```

### Invariant

> Identifier equality is evidence of possible identity, not authority to establish identity.

---

## 6. Mutable identifier invariant

External identifiers may change while the represented physical object remains the same. Therefore:

```text
identifier changed
    ≠
Asset changed
```

and:

```text
new identifier
    ≠
new Asset
```

unless governed identity resolution establishes otherwise. This is particularly important for mutable registration identifiers.

---

## 7. ExternalReference

`ExternalReference` represents the representation or reference of a CPL object in another context or system. The distinction is:

```text
AssetIdentifier
    → contributes to identifying the physical Asset

ExternalReference
    → identifies a representation/reference elsewhere
```

Example:

```text
VIN
    = AssetIdentifier

external CRM vehicle-record ID
    = ExternalReference
```

An ExternalReference MUST NOT automatically acquire Asset identity authority.

---

## 8. Domain Projection

A Domain Projection specializes an Asset without replacing its canonical identity. Current example:

```text
Asset
  │
  └── VehicleDetail
```

The authority relation is:

```text
Asset
    owns canonical identity

Domain Projection
    owns/supports domain-specific representation
```

Therefore:

```text
VehicleDetail
≠ canonical vehicle identity
```

A projection may change without requiring creation of a new Asset.

---

## 9. Asset Evidence

Asset Evidence is information capable of contributing to a determination concerning the identity of a physical object. It may originate from:

```text
identifier
registry
domain resolver
external system
human evidence
historical CPL state
domain observation
other admissible source
```

Evidence itself is not necessarily authoritative. Therefore:

```text
EVIDENCE
    ≠
DETERMINATION
```

---

## 10. Identity Determination Authority

The authority to establish whether two Asset records represent the same physical object belongs to the authorized identity resolver for the relevant domain. Conceptually:

```text
Asset evidence
      ↓
Authorized Domain Resolver
      ↓
Identity Determination
```

Possible determination classes include:

```text
SAME_PHYSICAL_ASSET
NOT_SAME_PHYSICAL_ASSET
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
FAILED
```

Exact downstream representation may differ, provided these semantic distinctions remain preserved.

---

## 11. Automotive authority

For the automotive domain:

```text
Automotive Identity Determination Authority
=
VIR
```

VIR may establish, subject to its own governed resolution semantics:

```text
Asset A and Asset B represent
the same physical vehicle
```

VIR MUST NOT thereby:

```text
merge Asset A into Asset B
delete an Asset
rewrite CPL relationships
rewrite CPL cases
change canonical CPL topology
```

VIR determines automotive physical identity. CPL governs canonical representation.

---

## 12. AssetIdentityResolution

`AssetIdentityResolution` is the CPL object through which a governed identity conclusion concerning an Asset becomes persistently interpretable. Conceptually it records or represents:

```text
subject evidence
resolution target(s)
determination
authority/source
confidence where applicable
provenance
time
status
supersession/history
```

The precise storage representation remains downstream. The semantic requirement is that the conclusion remain reconstructable and historically interpretable.

---

## 13. Current versus historical resolution

B4 distinguishes:

```text
CURRENT RESOLUTION
        ≠
HISTORICAL RESOLUTION
```

A later resolution may supersede an earlier resolution. It MUST NOT make the earlier resolution appear never to have existed. Therefore:

```text
R1 → superseded by R2
```

means:

```text
R1 remains historical
R2 becomes current
```

not:

```text
R1 deleted
```

---

## 14. Resolution authority does not imply mutation authority

An authorized resolver may produce:

```text
SAME_PHYSICAL_ASSET
```

but MUST NOT directly produce the canonical command:

```text
MERGE B INTO A
```

The correct chain is:

```text
Domain Identity Determination
          ↓
AssetIdentityResolution
          ↓
CPL Merge Admission
```

This boundary prevents domain systems from acquiring implicit authority over CPL canonical structure.

---

## 15. Canonical Merge Admission Authority

A positive physical identity determination is necessary but not sufficient for canonical merge. CPL owns the Merge Admission Authority. Its question is:

> Given an admissible identity determination, may these canonical Asset representations safely and lawfully be reconciled under CPL invariants?

Thus:

```text
SAME_PHYSICAL_ASSET
        ↓
identity prerequisite satisfied
        ↓
CPL MERGE ADMISSION
       / \
    ADMIT  DO NOT ADMIT
```

---

## 16. Why admission is separate from determination

Two Assets may genuinely represent the same physical object while their CPL state still requires reconciliation. For example:

```text
Asset A
 ├── identifiers
 ├── relationships
 └── cases

Asset B
 ├── other identifiers
 ├── conflicting relationship state
 └── other historical references
```

The domain resolver may correctly determine:

```text
A = B physically
```

without possessing the authority or knowledge necessary to decide how CPL canonical state must be reconciled. Therefore:

> Physical identity truth does not itself define canonical restructuring semantics.

---

## 17. Merge admission outcomes

The conceptual admission outcomes are:

```text
ADMITTED
HELD
REJECTED
```

Their purpose is to distinguish:

```text
identity established + structurally admissible
identity established + reconciliation unresolved
identity insufficient / prohibited
```

Exact naming may be refined before freeze.

---

## 18. Strong no-merge rule

B4 adopts:

> No positive admissible identity determination, no canonical merge.

Therefore:

```text
AMBIGUOUS      → NO MERGE
CONTRADICTORY  → NO MERGE
UNRESOLVED     → NO MERGE
FAILED         → NO MERGE
```

Likewise:

```text
identifier equality alone
similarity alone
human suspicion alone
ML similarity alone
LLM judgement alone
```

MUST NOT cause canonical merge.

---

## 19. Canonical Merge Execution Authority

Once merge admission is granted, CPL owns execution of the canonical merge. Therefore:

```text
Identity Determination Authority
    = authorized domain resolver

Merge Admission Authority
    = CPL

Merge Execution Authority
    = CPL Asset identity capability
```

Admission and execution belong within CPL but remain distinct authorities.

---

## 20. Survivor semantics

A canonical merge has directional semantics. Conceptually:

```text
Asset A = surviving canonical Asset
Asset B = merged historical Asset
```

The merge MUST NOT mean:

```text
DELETE Asset B
```

nor:

```text
Asset B never existed
```

---

## 21. Historical preservation invariant

B4 adopts:

> Asset merge changes the current canonical representation of a physical object; it does not rewrite the historical fact that multiple CPL Asset identities previously existed.

Consequently, the losing Asset identity MUST remain historically interpretable. Its historical existence cannot be erased merely because current canonical representation has changed.

---

## 22. Historical dependency preservation

Canonical merge must account for historical dependencies associated with both Assets, including where applicable:

```text
identifiers
identity resolutions
ContactAssetRelationships
domain projections
ExternalReferences
Cases
Runner-produced references
historical pointers
other canonical references
```

This does NOT mean every reference must necessarily be reassigned. The later B4 requirements must define:

```text
PRESERVE
REASSOCIATE
SUPERSEDE
REJECT_CONFLICT
DEFER
```

semantics where relevant. The Authority Map establishes only that they MUST NOT be silently destroyed.

---

## 23. Human and administrative intervention

Human intervention may provide:

```text
evidence
review
confirmation
adjudication
exception handling
```

where authorized by policy. But:

```text
admin clicks merge
        ↓
unconditional merge
```

is NOT an acceptable authority model. Human intervention remains subject to governed identity determination and merge admission.

---

## 24. Human adjudication boundary

A policy MAY designate a qualified human authority as an admissible identity adjudicator for a particular domain or exception class. If so, that human acts within:

```text
Identity Determination Authority
```

not outside the authority model. The human still does not automatically acquire:

```text
Canonical Merge Execution Authority
```

---

## 25. Conflicting resolver evidence

B4 must support the possibility that admissible evidence or authorized resolvers disagree. Example:

```text
Resolver/Evidence R1:
A = B

Resolver/Evidence R2:
A ≠ B
```

CPL MUST NOT resolve a domain controversy merely because it needs a single database answer. Unless an applicable authority policy resolves the conflict:

```text
CONTRADICTORY
    ↓
NO MERGE
```

---

## 26. Resolver hierarchy

B4 does NOT establish a universal hierarchy among every future domain resolver. Resolver precedence is domain/policy-specific. Therefore:

```text
resolver disagreement
```

cannot be resolved by an arbitrary implementation ordering such as:

```text
latest wins
first wins
highest numeric confidence wins
```

unless explicitly authorized.

---

## 27. Cloned identifier case

Consider:

```text
Vehicle A → VIN X
Vehicle B → VIN X
```

The same VIN does not prove:

```text
Vehicle A = Vehicle B
```

Possible causes include:

```text
data error
cloning
fraud
transcription
source corruption
domain-specific anomaly
```

Therefore:

```text
same strong identifier
        ↓
identity hypothesis
        ↓
authorized domain resolution
```

not automatic merge.

---

## 28. Mutable registration case

Consider:

```text
T1:
Vehicle A → registration X

T2:
same Vehicle A → registration Y
```

B4 MUST permit:

```text
same Asset
+
identifier lifecycle change
```

without requiring a new Asset merely because a mutable identifier changed. This demonstrates again:

```text
Asset identity
≠ identifier identity
```

---

## 29. Structural conflict after positive determination

Consider:

```text
Domain Resolver:
A = B physically
```

but CPL finds incompatible canonical state. The result MUST NOT be:

```text
domain says same
→ force merge
```

Instead:

```text
SAME_PHYSICAL_ASSET
        ↓
CPL Merge Admission
        ↓
structural conflict
        ↓
HELD / REJECTED
```

The physical identity determination remains valid unless separately superseded. The canonical merge may nevertheless remain inadmissible.

---

## 30. Erroneous historical merge

The most difficult lifecycle case is:

```text
T1
Resolver determines A = B

T2
CPL admits merge

T3
B merged into A

T4
new authoritative evidence establishes
A ≠ B
```

B4 MUST NOT pretend that the T3 merge never happened. Nor may the system remain permanently trapped in an incorrect canonical representation merely because merge was previously accepted.

---

## 31. Canonical correction principle

B4 therefore adopts:

> A canonical Asset merge is a governed canonical decision based on the admissible identity state at a given time; it is not an irreversible metaphysical truth.

A later authoritative resolution may invalidate the basis for the current canonical representation. This requires a governed correction mechanism.

---

## 32. Correction is not historical erasure

The conceptual lifecycle is:

```text
Resolution R1
A = B
   ↓
Merge Decision M1
B → A
   ↓
later evidence
   ↓
Resolution R2
A ≠ B
   ↓
Canonical Correction C1
```

The historical record must remain:

```text
R1 existed
M1 occurred
R2 superseded the identity conclusion
C1 corrected current canonical representation
```

It MUST NOT become:

```text
M1 never happened
```

---

## 33. Canonical correction authority

The same fundamental authority separation applies to correction:

```text
Domain Authority
    determines that previous physical identity
    conclusion is no longer valid

CPL
    determines and executes the corresponding
    canonical representation correction
```

A domain resolver MUST NOT directly rewrite historical CPL merge state.

---

## 34. Correction semantics status

The authority allocation for correction is established. However, the exact semantics of canonical correction remain subject to targeted challenge. In particular, B4 must determine whether correction means:

```text
reactivate historical Asset identity
create a new current canonical Asset representation
supersede canonical merge linkage
restore/reconcile selected relationships
some governed composition of these
```

Therefore:

```text
Asset Merge Authority Allocation
    = RESOLVED

Asset Merge Correction Semantics
    = CHALLENGE REQUIRED
```

---

## 35. ContactAssetRelationship

ContactAssetRelationship represents a governed relation between:

```text
Contact
   ↕
Asset
```

It does NOT define either object's canonical identity. Therefore:

```text
ContactAssetRelationship
    ≠ Contact identity
    ≠ Asset identity
```

---

## 36. Relationship semantic authority

A relationship assertion must establish at least conceptually:

```text
Contact
Asset
relationship type
effective state/time
authority
provenance
```

A mere foreign-key association is insufficient to express the governed meaning of the relationship.

---

## 37. Relationship types

B4 recognizes that different relationship semantics may coexist, for example:

```text
OWNER
USER
DRIVER
LESSEE
MANAGER
RESPONSIBLE_PARTY
```

The exact canonical vocabulary MUST be reconciled with the existing B2 model before freeze. No new relationship vocabulary is frozen by this Authority Map alone.

---

## 38. Relationship temporality

Relationships may be:

```text
current
historical
ended
superseded
```

depending on the canonical B2 model and later B4 requirements. Ending a relationship MUST NOT imply deletion of its historical existence. Thus:

```text
relationship ended
    ≠
relationship never existed
```

---

## 39. Relationship evidence

Relationship Evidence supports a claim such as:

```text
Contact C has relationship R with Asset A
```

Possible evidence may include:

```text
registry evidence
contract evidence
authenticated declaration
domain evidence
operator evidence
external system evidence
previous CPL state
```

Evidence does not automatically establish authority.

---

## 40. Relationship authority

B4 distinguishes:

```text
Relationship Evidence
        ≠
Relationship Authority
```

An admissible policy determines whether evidence is sufficient to establish, modify or end a relationship. CPL governs the canonical relationship representation once authority requirements are satisfied.

---

## 41. Asset creation authority

B4 distinguishes:

```text
NOT_FOUND
    ≠
CREATE
```

Asset creation requires independent admission. Conceptually:

```text
identity resolution
      ↓
NOT_FOUND
      ↓
creation admission
      ↓
CREATE ASSET
```

Creation authority belongs to CPL under applicable policy. A domain resolver may establish that no existing Asset has been resolved. It does not automatically acquire authority to create canonical CPL objects.

---

## 42. Asset creation idempotency

Asset creation must not produce uncontrolled duplicates from repeated execution of the same governed creation request. However:

```text
similar Asset evidence
```

must not automatically be treated as:

```text
same creation request
```

The exact idempotency semantics belong to the later Requirement Matrix.

---

## 43. Authority matrix

| Object / Decision | Primary authority | Explicit non-authority |
|---|---|---|
| Canonical Asset identity | CPL | Identifier / domain projection |
| Domain physical identity | Authorized domain resolver | CPL generic workflow |
| Automotive physical identity | VIR | Generic CPL inference |
| AssetIdentifier semantics | CPL + applicable domain rules | Raw identifier value alone |
| AssetIdentityResolution | Governed resolution authority | Similarity alone |
| Current canonical representation | CPL | Domain resolver |
| Merge admission | CPL | Domain resolver |
| Merge execution | CPL | VIR / identifier / admin bypass |
| Canonical correction | CPL | Domain resolver direct mutation |
| Domain Projection | Applicable domain capability | Projection as canonical identity |
| ContactAssetRelationship | CPL under relationship authority policy | FK existence alone |
| Relationship evidence | Evidence source | Evidence alone as universal authority |
| ExternalReference | CPL reference semantics | External system as canonical CPL authority |
| Asset creation | CPL under creation policy | NOT_FOUND alone |

---

## 44. Authority transition map

The complete B4 identity transition becomes:

```text
OBSERVATION / EVIDENCE
          │
          ▼
DOMAIN IDENTITY DETERMINATION
          │
          ▼
ASSET IDENTITY RESOLUTION
          │
          ├── NOT_SAME
          │       ↓
          │    KEEP SEPARATE
          │
          ├── AMBIGUOUS
          │       ↓
          │    KEEP SEPARATE
          │
          ├── CONTRADICTORY
          │       ↓
          │    KEEP SEPARATE
          │
          └── SAME
                  ↓
          CPL MERGE ADMISSION
              /       \
          REJECT/HOLD  ADMIT
             │           │
             │           ▼
             │      CPL MERGE EXECUTION
             │           │
             │           ▼
             └────► CANONICAL STATE
                         │
                         ▼
                 HISTORICAL EVIDENCE
                         │
                  later contradiction?
                         │
                         ▼
                NEW DOMAIN RESOLUTION
                         │
                         ▼
                 CPL CORRECTION
```

---

## 45. B4 authority invariants

**B4-AI01 — Domain/CPL separation**
Domain authority determines physical identity; CPL governs canonical identity.

**B4-AI02 — Evidence/non-authority separation**
Evidence alone does not automatically confer decision authority.

**B4-AI03 — Identifier non-sovereignty**
No AssetIdentifier independently possesses merge authority.

**B4-AI04 — Resolver mutation prohibition**
A domain resolver MUST NOT directly mutate canonical CPL Asset topology.

**B4-AI05 — Admission/execution separation**
Positive identity determination does not automatically execute merge.

**B4-AI06 — Ambiguity preservation**
Unresolved identity keeps canonical Assets separate.

**B4-AI07 — Historical preservation**
Canonical merge does not erase historical Asset identity.

**B4-AI08 — Correctability**
A canonical merge may be superseded/corrected if later authoritative identity evidence invalidates its basis.

**B4-AI09 — Correction history**
Canonical correction does not erase the historical merge decision.

**B4-AI10 — Relationship non-identity**
ContactAssetRelationship does not determine canonical Asset identity.

**B4-AI11 — Projection non-identity**
Domain Projection does not replace Asset identity.

**B4-AI12 — Creation separation**
NOT_FOUND does not itself authorize Asset creation.

---

## 46. Explicit prohibitions

B4 MUST NOT permit:

```text
same VIN → automatic merge
same registration → automatic merge
same serial number → automatic merge
similar records → automatic merge
LLM judgement → automatic merge
admin click → unconditional merge
VIR → direct CPL Asset merge
positive resolution → forced merge despite CPL conflict
merge → physical deletion of losing Asset
correction → deletion of historical merge evidence
relationship → implicit proof of Asset identity
domain projection → second canonical Asset identity
```

---

## 47. Resolved questions

This Authority Map resolves:

```text
Who determines physical Asset identity?
    → authorized domain resolver

Who determines automotive physical identity?
    → VIR

Who owns canonical Asset identity?
    → CPL

Who admits canonical Asset merge?
    → CPL

Who executes canonical Asset merge?
    → CPL

Can identifiers merge Assets?
    → NO

Can VIR directly merge CPL Assets?
    → NO

Can ambiguity cause merge?
    → NO

Can admin authority bypass merge admission?
    → NO

Must merged Asset history survive?
    → YES

Can a wrong historical merge be corrected?
    → YES, through governed canonical correction

Who owns that correction?
    → CPL, following admissible domain identity determination.
```

---

## 48. Questions intentionally not yet frozen

The following remain open for challenge/refinement:

```text
O-B4-01
Exact canonical correction mechanics after erroneous merge.

O-B4-02
Exact reconciliation treatment of identifiers,
relationships, cases, projections and references during merge.

O-B4-03
Exact canonical ContactAssetRelationship type vocabulary
against existing B2 implementation.

O-B4-04
Exact resolver precedence policy where multiple authorized
domain identity authorities exist.

O-B4-05
Whether canonical merge requires an explicit persisted
Merge Proposal / Merge Decision object or whether equivalent
durable provenance is sufficient.
```

These questions MUST NOT be delegated silently to implementation.

---

## 49. Targeted challenge set

Before B4 WHAT freeze, the Authority Map MUST survive at least:

```text
TC-B4-01
Same VIN attached to two physically distinct vehicles.

TC-B4-02
Same vehicle changes registration identifier.

TC-B4-03
Two authorized evidence paths produce contradictory
physical identity conclusions.

TC-B4-04
Domain resolver establishes SAME_PHYSICAL_ASSET,
but CPL dependencies make immediate merge unsafe.

TC-B4-05
A previously accepted merge is later proven incorrect.

TC-B4-06
Both Assets possess historically meaningful relationships,
cases and references before merge.
```

---

## 50. Authority resolution status

```text
ASSET MERGE AUTHORITY

Identity Determination Authority:
  RESOLVED

Automotive Identity Authority:
  RESOLVED

Canonical Merge Admission Authority:
  RESOLVED

Canonical Merge Execution Authority:
  RESOLVED

Identifier Authority:
  RESOLVED

Human/Admin Boundary:
  RESOLVED

Ambiguity Rule:
  RESOLVED

Historical Preservation:
  RESOLVED

Canonical Correction Authority:
  RESOLVED

Canonical Correction Mechanics:
  OPEN — TARGETED CHALLENGE REQUIRED
```

---

## 51. Governance status

```text
B4 WHAT Definition v0:
  MATERIALIZED

B4 Asset Object & Authority Map v0:
  PRODUCED
  PROPOSED FOR TARGETED CHALLENGE

B4 Asset Merge Authority Allocation:
  RESOLVED

B4 Asset Merge Lifecycle:
  PARTIALLY RESOLVED

B4 WHAT:
  NOT FROZEN

B4 Requirements:
  NOT AUTHORIZED

B4 Execution Mandate:
  NOT AUTHORIZED

B4 Implementation:
  NOT AUTHORIZED
```

---

## 52. Next governance operation

The next step should not yet be the global B4 Freeze Challenge.

We first need a bounded challenge of this authority model:

```text
B4_ASSET_AUTHORITY_TARGETED_CHALLENGE_v0
```

against `TC-B4-01 → TC-B4-06`.

Its purpose is specifically to determine whether:

```text
O-B4-01 → O-B4-05
```

can be closed without reopening the fundamental B4 definition.

Only after that should we consolidate the complete B4 WHAT and perform its global Freeze Challenge.

**END — CPL B4 Asset Object & Authority Map v0**

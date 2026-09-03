# CPL — B4 WHAT Consolidation v0

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** WHAT Consolidation
**Version:** v0
**Status:** PROPOSED FOR CONSOLIDATION CHALLENGE
**Canonical baseline:** `main @ aa3c453`
**Implementation authorization:** NONE

---

## 1. Purpose

This artifact consolidates the complete B4 WHAT from the now-stabilized submodels:

```text
B4_ASSETS_AND_RELATIONSHIPS_WHAT_DEFINITION_v0

B4_ASSET_OBJECT_AND_AUTHORITY_MAP_v0.1
B4_ASSET_AUTHORITY_TARGETED_RE_CHALLENGE_v0.1

B4_RELATIONSHIP_OBJECT_AND_AUTHORITY_MODEL_v0.1
B4_RELATIONSHIP_TARGETED_RE_CHALLENGE_v0.1
```

The purpose is no longer to discover the fundamental Asset or Relationship authority model. Those submodels are stabilized. The purpose is to produce one coherent B4 WHAT and close the remaining consolidation issues:

```text
C-B4-01  Asset survivor selection
C-B4-02  Dependency disposition
C-B4-03  Relationship type envelope
C-B4-04  AssetIdentifier lifecycle
C-B4-05  ExternalReference lifecycle
C-B4-06  Domain Projection lifecycle
C-B4-07  Final B4 operation surface
C-B4-08  Outcome / failure vocabulary
```

---

## 2. B4 mission

B4 establishes the governed CPL capability for:

```text
canonical Asset continuity
physical Asset identity resolution
Asset identifier lifecycle
canonical Asset identity decisions
Contact–Asset relationship continuity
canonical relationship decisions
domain projection binding
external reference continuity
historical/current interpretation
canonical merge and correction
```

B4 does not implement domain systems such as VIR or PGDR. It governs how their outputs may contribute to or consume CPL Asset continuity.

---

## 3. Fundamental B4 ontology

The consolidated B4 object set is:

```text
Asset
AssetIdentifier
AssetIdentityResolution
CanonicalAssetIdentityDecision
DomainProjection
ExternalReference
ContactAssetRelationship
CanonicalRelationshipDecision
```

with upstream:

```text
Contact
```

from B3. These must remain distinct concepts.

---

## 4. Physical reality versus CPL representation

B4 preserves:

```text
PHYSICAL OBJECT
      ≠
CPL Asset
```

An Asset is the persistent CPL representation through which the product maintains continuity around a physical object. This distinction makes possible:

```text
uncertainty
duplicate candidate representations
resolution
merge
correction
historical continuity
```

without equating database identity with physical reality.

---

## 5. Asset canonical identity

CPL canonical Asset identity is represented by:

```text
asset_id
```

It is not replaced by:

```text
VIN
registration
serial number
manufacturer ID
external system ID
domain projection
relationship
```

Thus:

```text
AssetIdentifier
≠ Asset
```

remains a core invariant.

---

## 6. Physical identity authority

Physical identity belongs to the authorized resolver for the relevant domain. For automotive:

```text
VIR
```

owns automotive physical identity resolution. CPL does not infer automotive physical identity merely from generic data similarity.

---

## 7. Asset resolution

The conceptual chain remains:

```text
Asset evidence
      ↓
Authorized Domain Resolver
      ↓
AssetIdentityResolution
```

with semantic outcomes including:

```text
SAME_PHYSICAL_ASSET
NOT_SAME_PHYSICAL_ASSET
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
FAILED
```

Technical failure remains distinct from identity state.

---

## 8. Canonical Asset authority

A positive physical identity determination does not itself mutate canonical CPL representation. The complete chain is:

```text
AssetIdentityResolution
        ↓
CPL canonical admission
        ↓
CanonicalAssetIdentityDecision
        ↓
current canonical Asset representation
```

Thus:

```text
AssetIdentityResolution
≠ CanonicalAssetIdentityDecision
```

---

## 9. CanonicalAssetIdentityDecision

This is a required B4 semantic object. It represents CPL's governed decision affecting canonical Asset representation. At minimum it must support semantic distinction between:

```text
MERGE
CORRECTION
```

and preserve:

```text
decision identity
affected Assets
supporting resolution
authority
time
provenance
result
supersession
```

No implementation representation is prescribed here.

---

## 10. Asset merge

Canonical Asset merge means:

```text
Asset A = surviving current canonical Asset
Asset B = merged historical Asset
```

It does not mean:

```text
DELETE Asset B
```

nor:

```text
Asset B never existed
```

Historical Asset identity remains reconstructable.

---

## 11. Canonical Asset correction

A merge later shown to be wrong is corrected through:

```text
new authoritative resolution
        ↓
new CanonicalAssetIdentityDecision
        ↓
CORRECTION
        ↓
supersession of prior current canonical effect
```

not historical erasure. Therefore:

```text
current truth
≠
history rewritten
```

---

## 12. C-B4-01 — Asset survivor selection

The remaining question is:

> When merge is admitted, how is the surviving canonical Asset selected?

B4 must not leave this to arbitrary implementation rules. Forbidden implicit criteria include:

```text
lowest UUID
earliest row
latest row
alphabetical order
developer preference
database order
```

---

## 13. Survivor-selection principle

The survivor must be selected by a governed CPL canonical continuity rule. The general rule should be:

> Select the Asset that maximizes preservation of existing canonical continuity and minimizes unnecessary canonical rewriting, subject to identity, authority, provenance and structural integrity constraints.

This means survivor selection should consider semantically relevant factors such as:

```text
existing canonical role
historical continuity
established external references
current canonical references
accepted domain projections
existing cases / operational continuity
identity-resolution history
```

but not reduce them to an arbitrary numeric score unless separately governed.

---

## 14. Existing canonical continuity preference

Where one Asset is already the established current canonical representation and the other is a later duplicate representation, the existing canonical Asset SHOULD normally survive unless a material governance reason requires otherwise. Thus:

```text
established canonical Asset
+
later duplicate Asset
    ↓
prefer established canonical continuity
```

This is a default, not an absolute law.

---

## 15. Survivor override

A different survivor may be required where the existing canonical Asset is itself structurally or semantically unsuitable. Any override must be explicit and traceable through the `CanonicalAssetIdentityDecision`.

### C-B4-01 status

```text
RESOLVED AT WHAT LEVEL
```

Implementation still chooses how to evaluate the governed rule.

---

## 16. Dependency non-convergence

The stabilized Asset model already established:

```text
Asset identity convergence
≠ dependency semantic convergence
```

Therefore Asset merge cannot blindly rewrite:

```text
AssetIdentifiers
ContactAssetRelationships
Cases
Domain Projections
ExternalReferences
AssetIdentityResolutions
```

---

## 17. C-B4-02 — Dependency disposition

The consolidated WHAT now defines generic disposition classes:

```text
PRESERVE
REASSOCIATE_CURRENT
SUPERSEDE
RECONCILE
HOLD
REJECT_CONFLICT
```

These are semantic dispositions, not necessarily database operations.

---

## 18. AssetIdentifier disposition

Default:

```text
PRESERVE historical attribution
+
make identifier discoverable through current canonical Asset
where semantically admissible
```

An identifier MUST NOT be silently reinterpreted as though it had always belonged to the surviving Asset. Where identifier conflict exists:

```text
RECONCILE
HOLD
or
REJECT_CONFLICT
```

may apply.

---

## 19. AssetIdentityResolution disposition

Historical resolutions remain attached to their historical context. They may inform the current canonical Asset through resolution/decision chains. They MUST NOT be rewritten to claim that an earlier resolution targeted a different Asset identity.

Default:

```text
PRESERVE
```

---

## 20. CanonicalAssetIdentityDecision disposition

All prior decisions are immutable as historical governance facts. New decisions may:

```text
SUPERSEDE
```

their current effect. They are never reassigned or deleted merely because canonical topology changes.

---

## 21. ContactAssetRelationship disposition

Default:

```text
PRESERVE relationship identity
PRESERVE original Asset endpoint
ALLOW current navigation through surviving Asset
```

Asset merge itself does not alter relationship truth. If relationship semantics must change, a separate `CanonicalRelationshipDecision` is required.

---

## 22. Case disposition

Cases remain historically associated with the Asset identity under which they were created. Current lookup MAY expose them through the current canonical Asset.

Default:

```text
PRESERVE historical attribution
+
current canonical navigation
```

---

## 23. Domain Projection disposition

Domain projections preserve their historical Asset attribution. Where multiple projections now relate to the same physical object, applicable domain semantics determine whether they:

```text
coexist
reconcile
supersede
conflict
```

Generic CPL must not adjudicate domain projection truth.

Default:

```text
PRESERVE + DOMAIN_RECONCILIATION_IF_REQUIRED
```

---

## 24. ExternalReference disposition

Historical external references remain tied to the Asset representation originally referenced by the external system. Current navigation may resolve through the surviving Asset.

Generic default:

```text
PRESERVE historical reference
+
canonical navigation
```

Direct reassignment requires separate authority.

---

## 25. Dependency blocking rule

A positive `SAME_PHYSICAL_ASSET` determination does not force merge where mandatory dependency dispositions remain unsafe or unresolved. Therefore:

```text
SAME_PHYSICAL_ASSET
      ↓
dependency reconciliation
      ↓
safe?
  YES → merge may proceed
  NO  → HOLD / REJECT
```

### C-B4-02 status

```text
RESOLVED
```

at the generic WHAT level.

---

## 26. ContactAssetRelationship ontology

A `ContactAssetRelationship` is a first-class governed object with stable identity. Its logical identity is independent of:

```text
current canonical Contact
current canonical Asset
current status
current relationship interpretation
```

---

## 27. CanonicalRelationshipDecision

B4 requires a distinct:

```text
CanonicalRelationshipDecision
```

for material relationship changes. Semantic decision types include:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

Each decision must preserve evidence, authority, time, effect and supersession provenance.

---

## 28. Relationship valid time and decision time

B4 preserves:

```text
VALID TIME
≠
DECISION TIME
```

A relationship may become known later than it became valid. A later decision may retroactively correct interpreted valid time without erasing prior decision history.

---

## 29. C-B4-03 — Relationship type envelope

B4 adopts a governed extensible relationship type envelope rather than a large fixed cross-domain enum. A canonical relationship type requires:

```text
semantic identifier
semantic authority / namespace
applicable domain/context
```

---

## 30. Mandatory generic core

The challenge did not establish a need for a mandatory generic type vocabulary. Therefore B4 freezes no required generic relationship type names at WHAT level. Even apparently generic terms such as:

```text
OWNER
USER
MANAGER
```

may exist where governed, but they are not mandatory universal CPL semantics. This avoids pretending CPL owns universal legal/social ontology.

### C-B4-03 status

```text
RESOLVED
```

The envelope is generic; relationship type semantics may be domain-owned.

---

## 31. Relationship cardinality

Cardinality, coexistence and incompatibility are governed by relationship-type/domain semantics. Generic CPL does not assume:

```text
one OWNER
one USER
one MANAGER
```

or any other universal cardinality.

---

## 32. Relationship endpoint evolution

When a Contact or Asset canonical identity changes:

```text
historical endpoint
    remains historical

current navigation
    follows canonical successor
```

Relationship semantics are not implicitly rewritten.

---

## 33. Relationship idempotency

Repeated execution of the same governed establishment request must not create duplicate logical relationship state. Idempotency is based on:

```text
governed request / operation identity
+
applicable scope
```

not endpoint/type similarity.

---

## 34. AssetIdentifier purpose

AssetIdentifier records an identifier associated with an Asset and preserves its lifecycle. Identifiers may be:

```text
added
verified
disputed
invalidated
superseded
historical
```

depending on applicable semantics. They are not canonical Asset identity.

---

## 35. C-B4-04 — AssetIdentifier lifecycle

The B4 generic lifecycle is:

```text
OBSERVED / SUBMITTED
      ↓
ADMITTED
      ↓
CURRENT / APPLICABLE
      ↓
may become
SUPERSEDED
INVALIDATED
DISPUTED
HISTORICAL
```

The exact state representation remains downstream.

---

## 36. Identifier validity is contextual

An identifier may be valid for:

```text
a jurisdiction
a time period
a source
a domain
```

and no longer valid later. Thus:

```text
identifier invalidated
≠ Asset invalidated
```

---

## 37. Identifier replacement

Replacing a mutable identifier must preserve historical attribution. Example:

```text
registration X
    ↓ replaced
registration Y
```

must not erase X's historical association.

---

## 38. Identifier conflict

Conflicting identifiers must not automatically cause:

```text
merge
new Asset
identifier deletion
```

They become evidence for governed resolution.

### C-B4-04 status

```text
RESOLVED AT WHAT LEVEL
```

---

## 39. ExternalReference purpose

ExternalReference identifies a representation of a CPL object in another system/context. It is distinct from AssetIdentifier. The core distinction remains:

```text
AssetIdentifier
  contributes to identifying the physical object

ExternalReference
  points to external representation/context
```

---

## 40. C-B4-05 — ExternalReference lifecycle

External references may be:

```text
created
current
superseded
invalidated
historical
```

where applicable. They must preserve:

```text
external system/context
external identity/reference
historical CPL target
provenance
```

---

## 41. ExternalReference authority

An external system may be authoritative about its own reference. It is not automatically authoritative about CPL canonical Asset identity. Thus:

```text
external reference exists
≠ physical identity determination
≠ canonical merge authority
```

---

## 42. ExternalReference after Asset merge

If external system E historically referenced Asset B and B later merges to A:

```text
historical reference → B
current canonical navigation → A
```

unless the external system itself independently rebinds its reference.

### C-B4-05 status

```text
RESOLVED
```

---

## 43. Domain Projection purpose

A Domain Projection describes domain-specific properties of an Asset. Example:

```text
Asset
  ↓
VehicleDetail
```

The projection does not own canonical Asset identity.

---

## 44. C-B4-06 — Domain Projection lifecycle

Generic lifecycle semantics include:

```text
ATTACHED
CURRENT
UPDATED
SUPERSEDED
HISTORICAL
DISPUTED / CONFLICTING where applicable
```

The exact representation remains domain-specific.

---

## 45. Projection authority

Domain projection truth belongs to the applicable domain authority. CPL governs:

```text
attachment to Asset
continuity
history
canonical navigation
```

without inventing the underlying domain facts.

---

## 46. Projection conflict

If two projections conflict after Asset reconciliation:

```text
generic CPL
    MUST NOT arbitrarily choose one
```

The applicable domain authority must resolve the conflict. Asset merge may remain HOLD where unresolved projection conflict makes canonical execution unsafe.

### C-B4-06 status

```text
RESOLVED
```

---

## 47. B4 canonical authority layers

The consolidated authority architecture is:

```text
DOMAIN / EVIDENCE AUTHORITY
       │
       ▼
determination
       │
══════════════════════
       │
       ▼
CPL ADMISSION AUTHORITY
       │
       ▼
CANONICAL DECISION
       │
       ▼
CURRENT CANONICAL INTERPRETATION
       │
       ▼
HISTORICAL CONTINUITY
```

This applies with domain-specific differences to Asset identity and relationships.

---

## 48. B4 Asset flow

```text
Evidence
   ↓
AssetIdentityResolution
   ↓
CPL admission
   ↓
CanonicalAssetIdentityDecision
   ↓
current canonical Asset state
```

---

## 49. B4 Relationship flow

```text
Relationship evidence
   ↓
authority/admission
   ↓
CanonicalRelationshipDecision
   ↓
current canonical relationship interpretation
```

No separate persisted `RelationshipDetermination` object is required by WHAT.

---

## 50. C-B4-07 — Final B4 operation surface

The consolidated B4 operation surface should be semantic rather than transport-specific.

### Asset retrieval / resolution

```text
get_asset
resolve_asset
```

### Asset creation

```text
create_asset
```

### Identifier lifecycle

```text
add_asset_identifier
update/invalidate_asset_identifier
get_asset_identifiers
```

### Asset canonical identity

```text
assess_asset_identity
admit_asset_merge
execute_asset_merge
correct_asset_identity
```

---

## 51. Relationship operations

```text
get_contact_asset_relationship
list_contact_asset_relationships

establish_contact_asset_relationship
end_contact_asset_relationship
correct_contact_asset_relationship
```

Current canonical relationship queries should support conceptual navigation:

```text
Contact → Assets
Asset → Contacts
```

---

## 52. Domain projection operations

```text
attach_domain_projection
get_domain_projection
update/supersede_domain_projection
```

Actual domain logic remains outside generic B4.

---

## 53. External reference operations

```text
add_external_reference
get_external_references
invalidate/supersede_external_reference
```

---

## 54. Operation surface caution

These are semantic operation families, not required HTTP endpoints or method names. The Requirement Matrix may later refine exact contracts. No transport is frozen.

### C-B4-07 status

```text
RESOLVED AT WHAT LEVEL
```

---

## 55. Separation of resolve / create

B4 preserves:

```text
NOT_FOUND
≠ CREATE
```

Asset resolution failure to find an existing Asset does not itself create one. Creation requires separate admission.

---

## 56. Separation of determination / merge

Likewise:

```text
SAME_PHYSICAL_ASSET
≠ MERGE
```

Merge requires CPL canonical admission.

---

## 57. Separation of relationship evidence / establishment

Likewise:

```text
relationship evidence
≠ canonical relationship
```

Relationship establishment requires governed admission and a canonical decision.

---

## 58. C-B4-08 — Outcome vocabulary

B4 requires semantic consistency across its operation families. We should distinguish four classes.

### A. Successful determinations

```text
MATCHED / SAME_PHYSICAL_ASSET
NOT_FOUND
NOT_SAME_PHYSICAL_ASSET
```

as applicable.

### B. Governed non-resolution

```text
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
HOLD
```

### C. Governed rejection

```text
INVALID
UNAUTHORIZED
REJECTED
CONFLICTING
```

as applicable.

### D. Technical failure

```text
FAILED
```

or equivalent technical execution failure.

---

## 59. Technical failure invariant

Technical failure MUST NOT be represented as a legitimate domain/identity state. Thus:

```text
database timeout
≠ UNRESOLVED

network exception
≠ AMBIGUOUS

internal error
≠ NOT_FOUND
```

---

## 60. HOLD semantics

HOLD means:

> A determination or claim may be partially admissible, but canonical mutation cannot safely proceed yet.

For example:

```text
SAME_PHYSICAL_ASSET
+
dependency conflict
→ HOLD merge
```

HOLD is not technical failure.

---

## 61. CONFLICT semantics

CONTRADICTORY refers to incompatible evidence/determinations whose authority has not yet been governedly resolved. REJECT_CONFLICT / CONFLICTING may describe a canonical admission failure due to structural incompatibility. These distinctions should remain testable.

### C-B4-08 status

```text
RESOLVED AT SEMANTIC LEVEL
```

Exact naming may be normalized in the Requirement Matrix without changing semantics.

---

## 62. B4 history model

B4 consistently distinguishes:

```text
current canonical representation
```

from:

```text
historical representation
```

and:

```text
world-valid time
```

from:

```text
CPL decision time
```

where applicable.

---

## 63. Historical continuity invariant

Canonical correction must not erase:

```text
earlier Asset identity
earlier relationship identity
earlier resolution
earlier canonical decision
earlier evidence
earlier external reference
historical endpoint attribution
```

unless separate retention policy lawfully governs data removal.

---

## 64. No historical rewriting

B4 prohibits semantic shortcuts equivalent to:

```text
merge → rewrite history

correction → pretend prior state never existed

endpoint merge → rewrite relationship endpoint

identifier replacement → delete prior identifier history
```

---

## 65. Relationship generic type decision

The consolidated B4 WHAT does not require a frozen list of generic relationship types. Instead it freezes the envelope:

```text
governed semantic type
+
authority namespace/context
+
domain semantics where applicable
```

This resolves the remaining non-blocking vocabulary question.

---

## 66. Status representation decision

B4 freezes semantic distinctions, not a single status enum. Relationship implementation must be capable of representing:

```text
current effectiveness
end
dispute/unresolved state
correction/supersession
```

and Asset/identifier/projection structures must similarly preserve necessary current/history semantics.

---

## 67. Cross-B3 compatibility

B4 must preserve B3 Contact canonical evolution semantics. Contact merge/correction must not require B4 to rewrite historical relationship identity. Thus:

```text
B3 canonical Contact continuity
+
B4 canonical Asset continuity
+
B4 Relationship continuity
```

must compose without historical falsification.

---

## 68. Cross-domain compatibility

B4 must support future domains without rebuilding canonical Asset identity. Examples may include:

```text
vehicle
property
machine
battery
solar installation
drone
industrial equipment
```

Domain-specific semantics enter through governed identity resolvers, projections and relationship types.

---

## 69. VIR boundary

VIR:

```text
determines automotive physical identity
```

It may provide evidence/resolution to B4. It MUST NOT directly:

```text
merge canonical Assets
correct canonical Asset topology
adjudicate generic ContactAssetRelationships
```

---

## 70. PGDR boundary

PGDR consumes a stable Asset/vehicle representation and may produce diagnostic/health state. PGDR does not become canonical Asset identity authority. B4 does not implement PGDR diagnostics.

---

## 71. Generic CPL boundary

B4 owns:

```text
Asset continuity
canonical Asset identity representation
canonical identity decisions
identifier continuity
ExternalReference continuity
domain projection binding continuity
ContactAssetRelationship continuity
canonical relationship decisions
current/history navigation
```

It does not own all domain truth.

---

## 72. B4 consolidated invariants — Asset

```text
B4-CI01 Asset ≠ physical object
B4-CI02 Asset ≠ AssetIdentifier
B4-CI03 Identifier match ≠ identity determination
B4-CI04 Domain determines physical identity
B4-CI05 CPL governs canonical identity
B4-CI06 Resolution ≠ canonical decision
B4-CI07 Positive identity determination ≠ mandatory merge
B4-CI08 Merge preserves historical Asset identity
B4-CI09 Correction supersedes, not erases
B4-CI10 Dependency convergence is not implied by identity convergence
```

---

## 73. B4 consolidated invariants — Relationships

```text
B4-CI11 Relationship ≠ endpoint identity
B4-CI12 Relationship ≠ authorization
B4-CI13 Evidence ≠ relationship authority
B4-CI14 Relationship has stable identity
B4-CI15 Material relationship mutation requires canonical decision
B4-CI16 Valid time ≠ decision time
B4-CI17 END ≠ CORRECT ≠ SUPERSEDE
B4-CI18 Endpoint canonical evolution ≠ relationship rewrite
B4-CI19 Cardinality is type/domain governed
B4-CI20 Relationship idempotency uses governed operation identity
```

---

## 74. B4 consolidated invariants — History

```text
B4-CI21 Current canonical state ≠ historical attribution
B4-CI22 Canonical correction preserves prior decisions
B4-CI23 Historical evidence remains explainable after supersession
B4-CI24 External references preserve historical target
B4-CI25 Domain projections do not become parallel canonical identity
```

---

## 75. B4 consolidated invariants — Authority

```text
B4-CI26 Resolver authority ≠ canonical mutation authority
B4-CI27 Admin privilege ≠ domain truth authority
B4-CI28 Confidence ≠ authority
B4-CI29 Generic CPL does not invent domain resolver precedence
B4-CI30 Generic CPL does not invent relationship semantics
```

---

## 76. B4 IN scope

```text
canonical Asset representation
Asset creation admission
Asset physical-identity resolution consumption
AssetIdentifier lifecycle
Asset canonical merge/correction
CanonicalAssetIdentityDecision
ExternalReference continuity
Domain Projection attachment/continuity
ContactAssetRelationship lifecycle
CanonicalRelationshipDecision
relationship valid-time/decision-time semantics
current/historical navigation
dependency disposition during canonical identity changes
```

---

## 77. B4 OUT scope

```text
VIR implementation
PGDR diagnostics
domain-specific diagnostic reasoning
authorization engine
authentication provider
frontend
billing
generic CRM
Contact–Contact social graph
Asset–Asset network topology
domain workflow engines
```

---

## 78. B4 final semantic object set candidate

The consolidated WHAT recognizes the following required governed semantic objects:

```text
Asset
AssetIdentifier
AssetIdentityResolution
CanonicalAssetIdentityDecision
ExternalReference
DomainProjection
ContactAssetRelationship
CanonicalRelationshipDecision
```

No additional first-class semantic object is currently required for B4 freeze.

---

## 79. B4 final authority chain

```text
WORLD / EXTERNAL SOURCES
        ↓
Evidence
        ↓
Domain Determination
        ↓
────────────────────────────
        ↓
CPL Admission
        ↓
Canonical Decision
        ↓
Current Canonical Interpretation
        ↓
Historical Continuity
```

This is the central transversal architecture of B4.

---

## 80. Consolidation issue closure scoreboard

```text
C-B4-01 Asset survivor selection
  RESOLVED

C-B4-02 Dependency disposition
  RESOLVED

C-B4-03 Relationship type envelope
  RESOLVED

C-B4-04 AssetIdentifier lifecycle
  RESOLVED

C-B4-05 ExternalReference lifecycle
  RESOLVED

C-B4-06 Domain Projection lifecycle
  RESOLVED

C-B4-07 Final operation surface
  RESOLVED AT WHAT LEVEL

C-B4-08 Outcome/failure vocabulary
  RESOLVED AT SEMANTIC LEVEL
```

**8 / 8 closed for consolidation.**

---

## 81. Remaining ambiguity policy

Any remaining choice that concerns:

```text
table structure
API path
class layout
transaction isolation
locking
serialization
event architecture
ORM
migration shape
```

belongs downstream.

Any remaining choice that changes:

```text
object meaning
authority
canonical decision semantics
historical preservation
merge/correction meaning
relationship truth
```

would require WHAT governance and may not be delegated to implementation.

---

## 82. Freeze-readiness test

B4 is now sufficiently consolidated to ask:

> Can a Requirement Matrix be produced without requiring developers to invent unresolved B4 product semantics?

Preliminary answer:

```text
YES — subject to global Freeze Challenge
```

That challenge must still attempt to falsify the consolidated model.

---

## 83. Global Freeze Challenge targets

The next challenge should test at least:

```text
FC-B4-01  Asset duplicate with cloned identifier
FC-B4-02  Mutable identifier without Asset discontinuity
FC-B4-03  Resolver contradiction
FC-B4-04  Asset merge with dependency conflict
FC-B4-05  Wrong merge later corrected
FC-B4-06  Survivor-selection continuity conflict
FC-B4-07  Historical ExternalReference after merge
FC-B4-08  Conflicting Domain Projections
FC-B4-09  Relationship co-ownership
FC-B4-10  Relationship contradiction
FC-B4-11  Retroactive relationship correction
FC-B4-12  Double endpoint canonical evolution
FC-B4-13  Idempotent relationship establishment
FC-B4-14  Technical failure vs governed non-resolution
FC-B4-15  Domain authority attempts canonical mutation
FC-B4-16  Authorization attempts to collapse into relationship
FC-B4-17  Historical evidence survives correction
FC-B4-18  B3 Contact continuity remains compatible
```

---

## 84. Challenge outcome contract

Allowed global challenge outcomes:

```text
FREEZE_ACCEPTED
REPAIR_REQUIRED
WHAT_REOPEN_REQUIRED
```

`FREEZE_ACCEPTED` means B4 WHAT may become frozen. `REPAIR_REQUIRED` means bounded consolidation repair. `WHAT_REOPEN_REQUIRED` means a fundamental submodel failed.

---

## 85. Governance status

```text
B4 Asset Authority submodel
  STABILIZED

B4 Relationship submodel
  STABILIZED

B4 WHAT Consolidation v0
  PRODUCED
  PROPOSED FOR CONSOLIDATION / FREEZE CHALLENGE

B4 WHAT
  NOT YET FROZEN

B4 Requirement Matrix
  NOT YET AUTHORIZED

B4 Execution Mandate
  NOT AUTHORIZED

B4 Implementation
  NOT AUTHORIZED
```

---

## 86. Canonical next sequence

```text
main @ aa3c453
      ↓
B4_WHAT_CONSOLIDATION_v0
      ↓
materialization
      ↓
B4 WHAT GLOBAL FREEZE CHALLENGE
      ↓
   ┌──┴─────────────┐
   │                │
REPAIR_REQUIRED   FREEZE_ACCEPTED
   │                │
repair              ↓
re-challenge    B4 WHAT FROZEN
                    ↓
            B4 REQUIREMENT MATRIX
```

---

## 87. Final declaration

```text
CPL B4 WHAT CONSOLIDATION v0
=============================

Asset Authority:
  STABILIZED

Relationship Authority:
  STABILIZED

Consolidation issues:
  8 / 8 CLOSED

Required semantic objects:
  8

Canonical decision layers:
  Asset identity decision
  Relationship decision

History model:
  CURRENT ≠ HISTORICAL
  VALID TIME ≠ DECISION TIME where applicable

Authority:
  DOMAIN DETERMINES DOMAIN TRUTH
  CPL GOVERNS CANONICAL REPRESENTATION

B4 WHAT:
  CONSOLIDATED
  NOT YET FROZEN

READY FOR:
  GLOBAL B4 WHAT FREEZE CHALLENGE

NOT READY FOR:
  REQUIREMENT MATRIX
  EXECUTION MANDATE
  IMPLEMENTATION
```

**END — B4 WHAT Consolidation v0**

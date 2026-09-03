# CPL — B4 Relationship Object & Authority Model v0

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Relationship Object & Authority Model
**Version:** v0
**Status:** PROPOSED FOR CHALLENGE
**Canonical baseline:** `main @ e2e0e39`
**Upstream authority:** B4 Asset Authority submodel STABILIZED
**Implementation authorization:** NONE

---

## 1. Purpose

This artifact defines the semantic nature, lifecycle, authority and historical behavior of `ContactAssetRelationship` within B4.

It addresses the principal relationship-side questions left open after stabilization of the Asset Authority submodel:

```text
What does a Contact–Asset relationship assert?
Who may establish it?
What is evidence versus authority?
Can multiple relationships coexist?
How does time affect relationship truth?
How are conflicts represented?
How are relationships ended or superseded?
What survives Asset merge/correction?
Which relationship semantics belong to generic CPL,
and which must remain domain-specific?
```

This artifact does not define implementation structures. It does not authorize B4 coding.

---

## 2. Fundamental relationship invariant

B4 establishes:

> A ContactAssetRelationship is a governed assertion about the relationship between a Contact and an Asset during an applicable temporal and semantic context.

Therefore:

```text
ContactAssetRelationship
    ≠ Contact identity

ContactAssetRelationship
    ≠ Asset identity

ContactAssetRelationship
    ≠ physical ownership automatically

ContactAssetRelationship
    ≠ authorization automatically
```

The relationship is a distinct governed object.

---

## 3. Core relationship structure

Conceptually:

```text
Contact
   │
   │
   ▼
ContactAssetRelationship
   │
   ├── Asset
   ├── relationship type
   ├── effective period / temporal state
   ├── status
   ├── evidence
   ├── authority
   ├── provenance
   └── historical continuity
```

A relationship therefore has semantics independent of either endpoint.

---

## 4. Why the relationship must be first-class

A raw association:

```text
contact_id + asset_id
```

cannot express enough meaning. The same Contact and Asset may have multiple distinct relationships:

```text
owner
driver
user
manager
lessee
responsible party
```

and those relationships may exist at different times. Therefore:

```text
relationship identity
    ≠ endpoint pair alone
```

---

## 5. Relationship assertion

A relationship assertion expresses a claim of the form:

> Contact C has relationship R to Asset A during temporal context T under evidence E and authority P

This is fundamentally different from:

```text
Contact C exists
Asset A exists
```

The existence of both objects does not imply a relationship.

---

## 6. Relationship truth

B4 does not treat a relationship row merely as an arbitrary user-entered label. A current canonical relationship must represent a relationship state that CPL is authorized to recognize. Therefore:

```text
relationship evidence
        ↓
relationship determination / admission
        ↓
canonical relationship state
```

The exact implementation need not reproduce those stages as separate services, but the semantic distinction must survive.

---

## 7. Evidence ≠ authority

The core rule is:

> Evidence that a relationship exists does not itself establish authority to make that relationship canonical.

Possible evidence includes:

```text
registry information
contract
invoice
insurance information
authenticated declaration
domain-system evidence
operator observation
historical CPL record
external-system record
```

But:

```text
evidence
≠ canonical relationship authority
```

---

## 8. Relationship authority

CPL owns canonical representation of the Contact–Asset relationship once applicable authority requirements are satisfied. However, CPL does not necessarily own the underlying domain truth. Example:

```text
ownership of vehicle
```

may depend on applicable domain evidence or authority. Thus:

```text
DOMAIN / SOURCE
determines or supports relationship truth

        ↓

CPL
governs canonical representation
```

This parallels, but is not identical to, the Asset identity authority boundary.

---

## 9. Relationship authority classes

B4 should distinguish at least:

```text
RELATIONSHIP_EVIDENCE_AUTHORITY
RELATIONSHIP_ADMISSION_AUTHORITY
RELATIONSHIP_MUTATION_AUTHORITY
RELATIONSHIP_TERMINATION_AUTHORITY
RELATIONSHIP_CORRECTION_AUTHORITY
```

These may later map to fewer implementation roles, but their semantic distinctions should remain explicit.

---

## 10. Relationship evidence authority

A source may be authorized to provide evidence without having authority to directly create canonical relationship state. For example:

```text
VIR identifies a vehicle
```

does not mean VIR automatically possesses authority to assert:

```text
Contact X OWNS Asset Y
```

Likewise:

```text
authenticated Contact declaration
```

may be evidence but not sufficient authority for every relationship type.

---

## 11. Relationship admission authority

CPL must decide whether the submitted evidence and authority context are sufficient to establish a canonical relationship. Conceptually:

```text
Relationship Claim
      ↓
Evidence
      ↓
Authority Context
      ↓
CPL Admission
      ↓
ADMIT / HOLD / REJECT
```

The exact state labels may be refined later.

---

## 12. No relationship-by-convenience

The following is prohibited semantically:

```text
Contact uses Asset
therefore Contact = OWNER
```

or:

```text
Contact registered Asset
therefore Contact = OWNER
```

or:

```text
Contact opened a Case
therefore Contact = OWNER
```

or:

```text
Contact is authenticated
therefore claimed relationship is true
```

These are different facts.

---

## 13. Relationship vocabulary problem

The existing B4 documents left:

```text
O-B4-03 ContactAssetRelationship vocabulary
```

open. This artifact must address it carefully. A generic CPL relationship vocabulary should contain only semantics that are sufficiently cross-domain to belong to the shared product layer. It should not absorb every future domain-specific role.

---

## 14. Candidate generic relationship classes

A reasonable generic candidate vocabulary is:

```text
OWNER
USER
CUSTODIAN
MANAGER
BENEFICIARY
RESPONSIBLE_PARTY
```

But B4 should not yet assume all of these are equally valid for every Asset domain. For example:

```text
DRIVER
```

is strongly automotive-specific.

```text
TENANT
```

may be property-specific. Therefore B4 needs a distinction between:

```text
GENERIC RELATIONSHIP SEMANTICS
```

and:

```text
DOMAIN-SPECIFIC RELATIONSHIP SEMANTICS
```

---

## 15. Generic vs domain-specific vocabulary

B4 adopts:

> CPL may define a generic relationship envelope without requiring one universal closed relationship vocabulary for all Asset domains.

Thus conceptually:

```text
relationship_type
    ↓
generic CPL type
or
domain-governed subtype/type
```

subject to policy. This avoids turning CPL into a universal ontology of every possible real-world relationship.

---

## 16. Relationship type namespace

The semantic model should support the idea that a relationship type has an authority context or namespace. Conceptually:

```text
generic:OWNER
automotive:DRIVER
property:TENANT
industrial:OPERATOR
```

This is not a required string format. The important point is that:

```text
relationship label
```

must not become globally authoritative merely because two domains use the same word.

---

## 17. OWNER

OWNER is especially dangerous because it appears generic but may have domain-specific legal meaning. Therefore B4 should treat OWNER as:

```text
canonical relationship semantic
```

only where evidence and authority sufficient for the relevant domain establish it. The existence of a generic OWNER type must not imply CPL can independently adjudicate legal title.

---

## 18. USER

USER means that the Contact is recognized as using the Asset under an applicable relationship context. It does not imply:

```text
ownership
custody
authority to dispose
legal responsibility
```

unless separate semantics establish those facts.

---

## 19. CUSTODIAN

CUSTODIAN indicates custody/control of the Asset without necessarily implying ownership. This may be useful cross-domain, but its exact admissibility remains policy-governed.

---

## 20. RESPONSIBLE_PARTY

RESPONSIBLE_PARTY should be treated cautiously. It may mean:

```text
operational responsibility
administrative responsibility
service responsibility
```

depending on context. Therefore a generic label alone may be insufficient unless the relationship includes appropriate semantic context. This suggests that some relationship types may require additional domain qualification.

---

## 21. Coexistence

Multiple relationships may coexist for the same Contact/Asset pair. Example:

```text
Alice OWNER Asset A
Alice USER Asset A
```

Likewise multiple Contacts may simultaneously hold different relationships to the same Asset:

```text
Alice OWNER
Bob USER
Carla MANAGER
```

Therefore:

```text
one Asset
≠ one Contact relationship
```

and:

```text
one Contact–Asset pair
≠ one relationship total
```

---

## 22. Same-type coexistence

The difficult question is whether multiple simultaneous relationships of the same type may exist. Example:

```text
Alice OWNER Asset A
Bob OWNER Asset A
```

This might be valid under co-ownership. Therefore B4 MUST NOT impose a universal invariant:

```text
one current OWNER per Asset
```

unless the applicable domain semantics require it. This is a critical correction to any overly simplistic uniqueness model.

---

## 23. B2 uniqueness constraints

If B2 already contains uniqueness constraints for ContactAssetRelationship, B4 must interpret them precisely rather than generalize beyond them. Therefore before B4 freeze:

```text
existing B2 constraints
```

must be reconciled with:

```text
relationship type
status
effective period
domain semantics
```

A database uniqueness constraint cannot silently define relationship ontology.

---

## 24. Temporal semantics

A relationship is generally time-bounded. Conceptually:

```text
effective_from
effective_to
```

or semantically equivalent state must allow:

```text
CURRENT
HISTORICAL
FUTURE?
ENDED
```

where applicable. The exact fields depend on B2 and later requirements.

---

## 25. Time is part of relationship truth

The statement:

```text
Alice owns Asset A
```

may be true at T1 and false at T2. Therefore the canonical relationship assertion is incomplete without temporal context where the relationship can change. Thus:

```text
relationship truth
=
Contact + Asset + type + applicable time/context
```

not merely:

```text
Contact + Asset + type
```

---

## 26. Ending relationship

Ending a relationship MUST NOT mean deleting its historical record. Conceptually:

```text
CURRENT
   ↓
ENDED
```

or:

```text
effective_to = T
```

rather than physical erasure. Historical relationship truth remains reconstructable.

---

## 27. Supersession

Some relationship changes may be better represented through supersession than simple termination. Example:

```text
R1:
Alice MANAGER Asset A

R2:
Bob MANAGER Asset A
```

Depending on domain semantics, R2 may:

```text
coexist
supersede
replace
```

R1. B4 must not assume replacement merely because the type is the same.

---

## 28. Contradictory relationship claims

Example:

```text
Claim 1:
Alice OWNER Asset A

Claim 2:
Bob OWNER Asset A
```

These are not necessarily contradictory. They could represent co-ownership. By contrast:

```text
Claim 1:
Alice sole legal owner

Claim 2:
Bob sole legal owner
```

may be contradictory. This exposes a key rule:

> Contradiction is semantic, not merely structural.

The relationship type and domain context determine incompatibility.

---

## 29. Relationship conflict

B4 should therefore represent relationship conflict only where applicable semantics establish incompatibility. Conceptually:

```text
compatible
coexisting
ambiguous
contradictory
unresolved
```

may be required states at the determination level. A generic CPL rule must not infer contradiction solely from multiple records.

---

## 30. Relationship determination

There is likely a semantic object or state analogous to:

```text
RelationshipDetermination
```

but this does not necessarily require a new persisted entity. Its purpose would be to distinguish:

```text
evidence
    ↓
determination
    ↓
canonical relationship mutation
```

However, unlike Asset physical identity, many relationship cases may be directly governed by authoritative source evidence. We should not invent an unnecessarily heavy resolver abstraction unless challenge proves it necessary.

---

## 31. Canonical relationship mutation

Every material relationship mutation should be attributable to a governed decision. At minimum:

```text
CREATE / ESTABLISH
END
CORRECT
SUPERSEDE
```

must be distinguishable semantically. A direct database update that loses why the relationship changed is insufficient for governed history.

---

## 32. Durable relationship provenance

Material relationship changes must preserve enough provenance to reconstruct:

```text
what relationship was asserted
between which Contact and Asset
what type
what evidence supported it
who/what asserted or adjudicated it
under what authority
when it became effective
what canonical change occurred
```

Exact persistence representation remains downstream.

---

## 33. Relationship correction

A historical relationship assertion may later be found wrong. Example:

```text
T1:
Alice OWNER Asset A

T2:
new authoritative evidence:
Alice was never owner
```

The system needs to distinguish:

```text
relationship ended at T2
```

from:

```text
earlier relationship assertion was erroneous
```

These are semantically different.

---

## 34. End ≠ correction

This is a critical invariant:

```text
END
    ≠
CORRECT
```

Ending says:

> relationship was valid and ceased.

Correction says:

> prior canonical relationship state was inaccurate or insufficiently justified.

Historical provenance should preserve both the earlier canonical state and the later correction.

---

## 35. Relationship correction by supersession

Like Asset canonical identity correction, relationship correction should preserve governance history. Conceptually:

```text
Relationship Decision D1
   ↓
canonical relationship R1
   ↓
new evidence
   ↓
Correction Decision D2
   ↓
D2 supersedes current effect of D1
```

without pretending D1 never existed as a product decision.

---

## 36. Asset merge interaction

The stabilized Asset Authority submodel established:

```text
Asset identity convergence
    ≠
relationship semantic convergence
```

This model adopts that rule directly. When:

```text
Asset B → Asset A canonically
```

relationships historically attached to B must not automatically be:

```text
rewritten
merged
ended
superseded
```

without relationship-specific semantics.

---

## 37. Historical Asset target

A relationship originally established against Asset B must preserve that historical target. Current navigation may resolve:

```text
B → A
```

but the relationship history must remain capable of stating:

```text
this relationship was originally asserted against B
```

---

## 38. Relationship current navigation after Asset merge

Current operations may need to answer:

> Which Contacts are currently related to canonical Asset A?

This may include relationships historically established against merged Asset B. That is a current-view/navigation problem. It must not destroy historical relationship attribution.

---

## 39. Relationship conflict during Asset merge

Asset merge admission may need to HOLD if relationship state cannot safely be interpreted. Example:

```text
Asset A:
current domain-authoritative sole-owner claim = Alice

Asset B:
current domain-authoritative sole-owner claim = Bob
```

and domain semantics establish those claims as incompatible. Then:

```text
Asset physical identity = SAME
```

may still coexist with:

```text
canonical Asset merge = HOLD
```

until relationship conflict is governed. This preserves the Asset Authority model.

---

## 40. Asset correction interaction

If Asset B was merged into A and later canonical correction restores B as independent: relationships historically attached to B should not require historical reconstruction from nothing. Because original target attribution was preserved, current relationship state can be re-evaluated under the corrected Asset topology. This validates the historical-target invariant.

---

## 41. Contact merge interaction

B3 allows Contact merge while preserving historical Contact identity. Therefore B4 relationship semantics must support both endpoints being governed identities subject to canonical evolution:

```text
Contact B → Contact A
Asset Y → Asset X
```

A relationship may therefore historically reference both:

```text
historical Contact identity
historical Asset identity
```

while current navigation resolves through their canonical successors.

---

## 42. Double canonical evolution

Example:

```text
Relationship R:
Contact B → Asset Y

later:
Contact B merged → Contact A
Asset Y merged → Asset X
```

Current navigation might expose:

```text
Contact A ↔ Asset X
```

but provenance must preserve:

```text
R was originally established:
Contact B ↔ Asset Y
```

This is a strong cross-B3/B4 invariant.

---

## 43. Relationship does not follow arbitrary canonical rewriting

The relationship itself must not be silently rewritten merely because either endpoint has a canonical successor. Instead, current resolution/navigation should be capable of resolving canonical endpoints while history remains intact. This mirrors the broader product-continuity model.

---

## 44. Relationship canonicality

A useful distinction emerges:

```text
RELATIONSHIP HISTORICAL RECORD
```

versus:

```text
CURRENT CANONICAL INTERPRETATION
```

The first records what relationship CPL recognized at a time. The second answers what relationship is currently considered effective given:

```text
relationship state
Contact canonical state
Asset canonical state
applicable authority/policy
```

These must not be collapsed.

---

## 45. Relationship authority and Contact authority

B4 must not infer relationship authority from B3 identity authority. An authenticated/resolved Contact may be correctly identified while making a false relationship claim. Therefore:

```text
Contact identity established
    ≠
relationship claim established
```

This is fundamental.

---

## 46. Self-asserted relationships

Some relationship types may permit self-assertion. Example candidate:

```text
USER
```

might under some policy permit:

```text
Contact declares use
```

Other types such as legal ownership may require stronger authority. Therefore B4 should not adopt either universal rule:

```text
self-assertion always sufficient
```

or:

```text
self-assertion never sufficient
```

Admissibility is relationship-type/domain-specific.

---

## 47. External authoritative relationships

Some domains may possess a strongly authoritative source. For example:

```text
registry
contractual authority
fleet-management authority
```

A domain adapter may classify such evidence appropriately. CPL may consume the determination without becoming the source of domain truth.

---

## 48. Relationship admission policy

The generic relationship model therefore needs a policy concept:

```text
relationship type
+
domain/context
+
evidence class
+
authority context
    ↓
admission semantics
```

The exact policy engine is HOW. The WHAT requires the decision not to be arbitrary.

---

## 49. Relationship status

B4 should support semantic distinction among at least:

```text
CURRENT
ENDED
DISPUTED?
CORRECTED?
```

but we should be cautious not to invent states unnecessarily before checking B2 and challenge results. At minimum the model requires the distinction:

```text
currently effective
historically effective
historically asserted but later corrected
```

Exact status vocabulary remains candidate-level.

---

## 50. Disputed relationship

A relationship may become disputed without being conclusively invalidated. Example:

```text
existing OWNER relationship
new contradictory evidence
insufficient authority to determine replacement truth
```

The correct system response may be:

```text
DISPUTED / UNRESOLVED
```

rather than immediate termination or correction. This prevents forced certainty.

---

## 51. Current relationship under dispute

Whether a disputed relationship remains operationally effective is policy-dependent. B4 should not globally decide:

```text
disputed = inactive
```

or:

```text
disputed = active
```

for every domain. This belongs to relationship policy. The dispute itself must remain visible.

---

## 52. Relationship evidence continuity

As with Asset identity:

> A later relationship correction or supersession MUST NOT erase the evidence that explains why an earlier canonical relationship state existed.

This preserves decision quality and auditability.

---

## 53. Relationship decision

The challenge should test whether B4 requires a first-class:

```text
CanonicalRelationshipDecision
```

analogous to:

```text
CanonicalAssetIdentityDecision
```

Potential semantic roles:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

At this stage, this is marked as a candidate structural object rather than frozen immediately.

---

## 54. Why a CanonicalRelationshipDecision may be necessary

Without one, the system may know:

```text
relationship row changed
```

but not reliably:

```text
why
under which evidence
under which authority
whether it was termination or correction
what previous decision it superseded
```

That repeats the exact weakness discovered in Asset canonical merge. Therefore the upcoming challenge must attempt to eliminate the need for this concept. If it cannot, it should become a required semantic object.

---

## 55. Relationship operation families — candidate

Potential future primitive families include:

```text
get relationships
establish relationship
end relationship
correct relationship
resolve current relationships
```

Potential domain-specific operations may exist elsewhere. These are not frozen primitive operations. They are merely semantic families for WHAT analysis.

---

## 56. Relationship query direction

The system must support both conceptual directions:

```text
Contact → Assets
```

and:

```text
Asset → Contacts
```

without implying that these are separate relationship truths. They are views over the same governed relationship state.

---

## 57. Relationship uniqueness

No universal uniqueness rule should be frozen at the generic level beyond B2 invariants already accepted. Uniqueness may depend on:

```text
relationship type
domain
effective period
status
Asset class
Contact class
```

Therefore B4 must resist turning implementation constraints into ontology.

---

## 58. Relationship cardinality

Likewise cardinality may vary:

```text
one-to-one
one-to-many
many-to-one
many-to-many
```

depending on relationship semantics. The generic ContactAssetRelationship must therefore not assume a universal cardinality beyond endpoint existence.

---

## 59. Relationship provenance and source

At minimum, a canonical relationship must be explainable through:

```text
source
evidence
authority
time
relationship semantics
canonical decision
```

where applicable. This does not mean raw external payloads must always be retained. It means the canonical state must remain governably explainable.

---

## 60. Relationship confidence

A confidence value may be useful for certain evidence or determinations. But:

```text
confidence
    ≠ authority
```

and:

```text
confidence = 1.0
    ≠ relationship automatically canonical
```

unless explicit policy grants that evidence class decisive authority.

---

## 61. LLM/ML boundary

ML or LLM systems may:

```text
extract relationship evidence
classify candidate relationship type
identify conflicts
suggest resolution
```

They MUST NOT independently acquire canonical relationship authority merely because their confidence is high. This parallels Asset identity rules.

---

## 62. Domain adapter boundary

A domain adapter may define:

```text
allowed domain relationship types
evidence semantics
authority policy
conflict rules
temporal rules
```

within the generic CPL envelope. It must not redefine canonical Contact or Asset identity.

---

## 63. Generic CPL responsibility

Generic CPL should own:

```text
relationship object continuity
endpoint integrity
temporal/historical continuity
canonical relationship state
relationship-decision provenance
current vs historical interpretation
generic governance envelope
```

while domain packs may own domain truth semantics.

---

## 64. Domain responsibility

Domain systems may own:

```text
what DRIVER means in automotive
what TENANT means in property
what OPERATOR means in industrial context
which evidence proves those relationships
what conflicts are impossible
what authority hierarchy applies
```

CPL consumes those semantics through governed boundaries.

---

## 65. Relationship anti-collapse invariant

B4 must prevent collapse of:

```text
Contact identity
Asset identity
Relationship truth
Authorization
```

These are four different dimensions. Example:

```text
Alice is the authenticated Contact
Asset X is the resolved vehicle
Alice is OWNER of X
Alice may modify X
```

are four separate claims. None should be inferred automatically from the others.

---

## 66. Authorization boundary

A ContactAssetRelationship may contribute to authorization elsewhere. For example:

```text
OWNER
```

may later be relevant to access policy. But B4 MUST NOT turn the relationship itself into the authorization engine. Thus:

```text
relationship
    may be authorization input

relationship
    ≠ authorization decision
```

---

## 67. Relationship historical truth

The system must be capable of representing:

```text
At T1, CPL canonically recognized relationship R.
At T2, R ended.
At T3, new evidence showed R had actually been incorrect.
```

This may require distinguishing:

```text
historically canonical state
```

from:

```text
retrospective corrected interpretation
```

without erasing either. This is another reason challenge must examine canonical relationship decision history.

---

## 68. Retroactive correction

Some evidence may establish that a relationship was invalid from an earlier date. Example:

```text
relationship recorded as OWNER from T1
new authoritative evidence says ownership actually ended at T0
```

The system may need to correct effective history while preserving governance history. Thus:

```text
relationship effective history
    ≠
decision/audit history
```

This distinction is structurally important.

---

## 69. Two temporal dimensions

The previous case reveals potentially two temporal dimensions:

```text
VALID TIME
When the relationship is considered true in the world

TRANSACTION / DECISION TIME
When CPL learned/decided/recorded it
```

B4 should not yet require a full bitemporal database architecture. But it should recognize the semantic distinction where corrections are possible.

---

## 70. Bitemporal semantic invariant candidate

> A later correction MAY change CPL's current interpretation of when a relationship was valid without erasing when CPL originally recorded or decided the earlier state.

This is a semantic requirement, not yet a storage prescription.

---

## 71. Relationship merge is not a primitive assumption

Two relationship records may later be discovered to represent the same relationship history. B4 should not automatically introduce:

```text
merge_relationships
```

as a primitive. Deduplication may be handled through correction/supersession depending on the model. This needs challenge if it becomes relevant.

---

## 72. Relationship identity

An unresolved question remains:

> What makes two ContactAssetRelationship records represent the same logical relationship?

Possible dimensions:

```text
Contact identity
Asset identity
relationship type
domain
effective interval
source
authority
```

The answer matters for idempotency and correction. This must be closed before Requirement Matrix.

---

## 73. Asset/Contact canonical changes and relationship identity

If a Contact or Asset is canonically merged, the relationship's logical identity should not automatically change merely because an endpoint's current canonical representative changed. This supports historical continuity. Therefore endpoint canonicalization and relationship identity are distinct.

---

## 74. Candidate relationship logical identity

A candidate conceptual identity is:

```text
historical Contact identity
+
historical Asset identity
+
relationship semantic type/context
+
governed establishment identity
```

rather than merely:

```text
current canonical Contact
+
current canonical Asset
```

This remains subject to challenge.

---

## 75. Idempotency

Repeated execution of the same governed relationship-establishment request must not unintentionally create duplicate canonical relationship state. But similar endpoint/type data alone may not be sufficient to identify the same logical request. This mirrors B3 Contact creation idempotency.

---

## 76. Relationship creation ≠ Asset creation

If a Contact claims a relationship to an unknown Asset:

```text
relationship establishment
```

must not silently create an Asset unless a separately governed composition authorizes it. Likewise an unknown Contact must not be silently created by relationship establishment. This preserves boundary separation.

---

## 77. Relationship admission failure

Valid non-success outcomes may include conceptually:

```text
NOT_FOUND
INVALID
UNAUTHORIZED
AMBIGUOUS
CONFLICTING
UNRESOLVED
HELD
ALREADY_EXISTS
```

depending on later service semantics. These must not all become generic technical failure.

---

## 78. Relationship state failure ≠ execution failure

A disputed or unresolved relationship claim is a domain/governance state. A database failure is an execution failure. The distinction must survive.

---

## 79. Relationship object candidate invariants

**B4-RI01 — Relationship is first-class**
A ContactAssetRelationship is more than an endpoint pair.

**B4-RI02 — Evidence ≠ authority**
Relationship evidence does not automatically authorize canonical state.

**B4-RI03 — Identity ≠ relationship**
Contact or Asset identity does not imply their relationship.

**B4-RI04 — Relationship ≠ authorization**
Relationship state may inform authorization but is not itself the authorization engine.

**B4-RI05 — Historical continuity**
Ending/correcting relationship state does not erase governance history.

**B4-RI06 — Temporal truth**
Relationship truth may vary over time.

**B4-RI07 — Same-type multiplicity is domain-governed**
Generic CPL does not universally prohibit simultaneous same-type relationships.

**B4-RI08 — Asset merge does not adjudicate relationships**
Asset identity reconciliation does not determine relationship truth.

**B4-RI09 — Contact merge does not erase relationship history**
Current canonical navigation and historical endpoints remain distinguishable.

**B4-RI10 — Endpoint evolution ≠ relationship rewrite**
Canonical endpoint changes do not silently rewrite relationship history.

**B4-RI11 — Domain vocabulary boundary**
Generic CPL does not need to own a closed vocabulary for all domain relationships.

**B4-RI12 — Confidence ≠ authority**
Relationship confidence alone cannot establish canonical relationship state.

---

## 80. Candidate new invariants

**B4-RI13 — End/correction distinction**
Ending a valid relationship and correcting an erroneous relationship are different semantic events.

**B4-RI14 — Relationship decision traceability**
Material canonical relationship changes must be traceable to evidence, authority and decision context.

**B4-RI15 — Valid-time/decision-time distinction**
Where retroactive correction occurs, relationship effective time and CPL decision time must remain conceptually distinguishable.

**B4-RI16 — Current/history coexistence**
Current canonical relationship interpretation must coexist with reconstructable historical canonical states.

**B4-RI17 — No implicit endpoint creation**
Relationship establishment cannot silently create Contact or Asset identity.

---

## 81. Open questions registry

The relationship model intentionally leaves several questions open.

```text
O-B4-R01
Exact generic ContactAssetRelationship vocabulary.

O-B4-R02
Exact relationship type namespace/domain-extension mechanism.

O-B4-R03
Whether CanonicalRelationshipDecision is a required
first-class governed semantic object.

O-B4-R04
Exact logical identity of a ContactAssetRelationship.

O-B4-R05
Exact status/state vocabulary.

O-B4-R06
Per-type cardinality and conflict rules.

O-B4-R07
Precise handling of valid time versus decision time.

O-B4-R08
Relationship dispositions during Asset merge/correction.

O-B4-R09
Relationship dispositions during Contact merge/correction.

O-B4-R10
Relationship idempotency semantics.
```

None of these may be delegated silently to implementation.

---

## 82. What is already sufficiently resolved

Despite the open questions, the following relationship principles are now strong candidates:

```text
Relationship is a governed first-class semantic object.
Relationship evidence ≠ relationship authority.
Relationship ≠ endpoint identity.
Relationship ≠ authorization.
Relationships are temporally meaningful.
Ending ≠ correction.
Historical state must survive.
Asset merge does not settle relationship truth.
Contact merge does not settle relationship truth.
Current canonical navigation ≠ historical attribution.
Generic CPL should support domain-specific relationship semantics
without becoming the owner of every domain vocabulary.
```

---

## 83. Challenge targets

The next challenge must attack the model with cases such as:

```text
TC-B4-R01
Two simultaneous owners are valid.

TC-B4-R02
Two simultaneous sole owners are contradictory.

TC-B4-R03
Contact self-asserts ownership without authoritative evidence.

TC-B4-R04
Relationship was valid, then ended.

TC-B4-R05
Relationship was recorded, later proven never valid.

TC-B4-R06
Relationship correction is retroactive.

TC-B4-R07
Asset endpoint is merged, then corrected.

TC-B4-R08
Contact endpoint is merged.

TC-B4-R09
Both Contact and Asset endpoints are merged.

TC-B4-R10
Domain-specific DRIVER relationship enters generic CPL.

TC-B4-R11
Same relationship-establishment request is replayed.

TC-B4-R12
Two records appear duplicate but have different effective periods.

TC-B4-R13
Relationship evidence sources disagree.

TC-B4-R14
Relationship contributes to authorization but does not decide it.

TC-B4-R15
Historical relationship must remain discoverable after endpoint evolution.
```

---

## 84. Challenge objective

The challenge must determine especially whether the model needs:

```text
CanonicalRelationshipDecision
```

as a distinct semantic object. The burden of proof should be:

> Can we preserve correction, supersession, authority, provenance, valid-time/decision-time distinction without such a governed decision concept?

If not, the object should become part of the B4 WHAT.

---

## 85. Relationship vocabulary challenge objective

The challenge should also determine whether B4 needs:

```text
a small frozen generic core vocabulary
+
domain extension
```

or whether:

```text
fully domain-governed typed relationships
inside a generic CPL envelope
```

is the cleaner model. We should not freeze a vocabulary merely because example labels are convenient.

---

## 86. B4 relationship boundary

B4 relationship semantics include:

```text
Contact–Asset relationship representation
relationship authority/evidence
relationship lifecycle
temporal interpretation
history
correction
canonical navigation
interaction with Contact/Asset canonical identity evolution
```

They exclude:

```text
general social graph
Contact–Contact relationships
Asset–Asset topology
authorization engine
domain-specific business workflows
billing
diagnostics
VIR execution
PGDR execution
```

---

## 87. Relationship model definition candidate

> B4 Contact–Asset Relationship capability represents governed, temporally meaningful assertions between canonical Contact and Asset identities, preserving evidence, authority, historical attribution and correction semantics while allowing current canonical navigation to follow evolving Contact and Asset identity without rewriting the history under which the relationship was originally established.

---

## 88. Governance status

```text
B4 WHAT Definition v0
    MATERIALIZED

B4 Asset Authority submodel
    STABILIZED

B4 Relationship Object & Authority Model v0
    PRODUCED
    PROPOSED FOR TARGETED CHALLENGE

B4 Relationship submodel
    NOT STABILIZED

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

## 89. Next operation

The next governance artifact should be:

```text
B4_RELATIONSHIP_TARGETED_CHALLENGE_v0.md
```

against `TC-B4-R01 → TC-B4-R15`. Its primary closure targets are:

```text
O-B4-R01 → O-B4-R10
```

with special emphasis on:

```text
CanonicalRelationshipDecision
logical relationship identity
generic vs domain vocabulary
valid-time vs decision-time
endpoint merge/correction behavior
```

Only after this relationship submodel is stabilized should we combine:

```text
Asset Authority
+
Relationship Authority
+
Asset resolution
+
identifier lifecycle
+
domain projection
+
dependency semantics
```

into the B4 WHAT Consolidation.

**END — B4 Relationship Object & Authority Model v0**

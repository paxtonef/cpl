# CPL — B4 Relationship Targeted Challenge v0

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Relationship Targeted Challenge
**Version:** v0
**Status:** CHALLENGE COMPLETED — REPAIR REQUIRED
**Canonical baseline:** `main @ 3af71bb`
**Primary challenged artifact:** `B4_RELATIONSHIP_OBJECT_AND_AUTHORITY_MODEL_v0.md`
**Implementation authorization:** NONE

---

## 1. Challenge purpose

This challenge attempts to falsify the B4 relationship model before it is incorporated into the consolidated B4 WHAT. The challenge attacks the fifteen scenarios defined by the Relationship Object & Authority Model:

```text
TC-B4-R01  Two simultaneous owners are valid
TC-B4-R02  Two simultaneous sole owners are contradictory
TC-B4-R03  Self-asserted ownership without sufficient authority
TC-B4-R04  Valid relationship later ends
TC-B4-R05  Recorded relationship later proven never valid
TC-B4-R06  Retroactive correction
TC-B4-R07  Asset endpoint merge then correction
TC-B4-R08  Contact endpoint merge
TC-B4-R09  Both endpoints merge
TC-B4-R10  Domain-specific DRIVER inside generic CPL
TC-B4-R11  Replay of same establishment request
TC-B4-R12  Apparent duplicates with different effective periods
TC-B4-R13  Conflicting relationship evidence
TC-B4-R14  Relationship used by authorization
TC-B4-R15  Historical relationship discovery after endpoint evolution
```

It must also attempt to close:

```text
O-B4-R01 → O-B4-R10
```

without allowing implementation to invent product semantics.

---

## 2. Challenge standard

For each target, the result may be:

```text
PASS
PASS_WITH_REFINEMENT
FAIL
```

A `PASS_WITH_REFINEMENT` means the core model survives but a WHAT-level rule is missing. If missing rules materially affect implementation semantics, the overall result must be:

```text
REPAIR_REQUIRED
```

even if the architecture itself survives.

---

## 3. Core model under attack

The challenged model asserts:

```text
Relationship Evidence
        ↓
Authority / Admissibility
        ↓
Canonical Relationship State
        ↓
Historical Continuity
        ↓
Current Interpretation
```

while preserving:

```text
Contact identity
≠ Asset identity
≠ Relationship truth
≠ Authorization
```

This separation is the principal model to test.

---

## 4. TC-B4-R01 — Two simultaneous owners

### Scenario

```text
Alice OWNER Asset A
Bob   OWNER Asset A
```

Could both be valid? Yes. Co-ownership is possible. Therefore a generic CPL invariant such as:

```text
one current OWNER per Asset
```

would be ontologically wrong. The challenged model correctly states that same-type multiplicity is domain-governed.

### Result

```text
TC-B4-R01 = PASS
```

### Confirmed invariant

```text
same relationship type
+
same Asset
+
same period
≠ automatically conflict
```

---

## 5. TC-B4-R02 — Two sole owners

### Scenario

```text
Alice SOLE_OWNER Asset A
Bob   SOLE_OWNER Asset A
same effective period
```

Assume the applicable domain semantics define these assertions as mutually exclusive. The system must then represent a contradiction. The existing model says contradiction is semantic rather than structural. That is correct.

But this exposes a requirement: CPL must be able to consume relationship-type/domain rules that determine compatibility or incompatibility. Without such semantics, the generic layer cannot decide whether two records conflict.

### Result

```text
TC-B4-R02 = PASS_WITH_REFINEMENT
```

Required refinement:

> relationship compatibility must be governed by applicable relationship semantics/policy, not inferred from record count.

---

## 6. TC-B4-R03 — Self-asserted ownership

### Scenario

An authenticated Contact states:

> I own Asset A.

Could CPL establish OWNER merely because the Contact is authenticated? No. The model already establishes:

```text
Contact identity established
≠
relationship claim established
```

and:

```text
self-assertion
may be evidence
≠ universally sufficient authority
```

For a USER relationship, self-assertion might be admissible under policy. For legal ownership, stronger evidence may be required.

### Result

```text
TC-B4-R03 = PASS
```

No universal self-assertion policy should be added.

---

## 7. TC-B4-R04 — Relationship valid, then ended

### Scenario

```text
T1:
Alice OWNER Asset A

T2:
Alice ceases to be owner
```

This is a genuine lifecycle transition:

```text
valid relationship
    ↓
ENDED
```

The historical state must remain true for T1. The challenged model explicitly distinguishes termination from deletion.

### Result

```text
TC-B4-R04 = PASS
```

---

## 8. TC-B4-R05 — Relationship later proven never valid

### Scenario

```text
T1:
CPL records Alice OWNER Asset A

T2:
authoritative evidence establishes
Alice was never owner
```

This is not:

```text
END at T2
```

because that would falsely imply ownership was valid until T2. The model correctly distinguishes:

```text
END
≠
CORRECT
```

But the challenge exposes a stronger issue. To preserve governance history, CPL must distinguish:

```text
historically canonical relationship decision
```

from:

```text
current retrospective interpretation of relationship validity
```

A relationship row alone is unlikely to capture this robustly.

### Result

```text
TC-B4-R05 = PASS_WITH_REFINEMENT
```

This is the first strong indication that `CanonicalRelationshipDecision` is necessary.

---

## 9. TC-B4-R06 — Retroactive correction

### Scenario

Relationship recorded:

```text
valid_from = T1
```

Later authoritative evidence establishes:

```text
actual validity ended at T0
```

or:

```text
relationship never became valid
```

The system must be able to correct the valid-time interpretation while preserving the fact that CPL only learned this later. Therefore two temporal dimensions are genuinely required semantically:

```text
VALID TIME
when the relationship is considered true in the world

DECISION / RECORD TIME
when CPL accepted or changed that interpretation
```

A single timestamp dimension cannot preserve both truths cleanly. This does not require a bitemporal database architecture. But the semantic distinction is now necessary.

### Result

```text
TC-B4-R06 = PASS_WITH_REPAIR
```

Required repair:

> Relationship effective history and CPL decision history must remain independently reconstructable.

---

## 10. Important structural discovery — CanonicalRelationshipDecision

The previous two scenarios show that relationship state alone cannot cleanly represent:

```text
why CPL established a relationship
why CPL ended it
why CPL later corrected it
what prior state was superseded
what authority supported the change
when CPL made the decision
```

Therefore the challenge cannot eliminate the candidate concept:

```text
CanonicalRelationshipDecision
```

Instead, it confirms its necessity.

---

## 11. CanonicalRelationshipDecision semantics

The semantic object represents a governed CPL decision affecting canonical relationship interpretation. Possible decision classes include at least:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

The precise implementation representation remains HOW. The object must be sufficiently first-class for:

```text
traceability
authority attribution
evidence linkage
decision time
affected relationship
supersession
audit
```

Therefore:

```text
Relationship evidence
≠
CanonicalRelationshipDecision
```

and:

```text
Relationship record/state
≠
CanonicalRelationshipDecision
```

---

## 12. O-B4-R03 — CanonicalRelationshipDecision

The challenge resolves this open question.

```text
O-B4-R03 = RESOLVED
```

B4 requires a durable governed `CanonicalRelationshipDecision` or semantic equivalent. It does not require a particular:

```text
SQL table
ORM class
event stream
API resource
```

---

## 13. TC-B4-R07 — Asset endpoint merge then correction

### Scenario

Historical relationship:

```text
R:
Contact C ↔ Asset B
```

Then:

```text
Asset B → Asset A
```

Later Asset correction restores B as independent. If the relationship was rewritten to A at merge time, correction becomes difficult or historically false. The stabilized Asset Authority model already requires preservation of original Asset target. The relationship model correctly inherits this rule. Thus:

```text
historical relationship endpoint = B
current canonical navigation may resolve = A
```

and after correction:

```text
current endpoint may again resolve = B
```

without fabricating history.

### Result

```text
TC-B4-R07 = PASS
```

---

## 14. TC-B4-R08 — Contact endpoint merge

### Scenario

Historical relationship:

```text
Contact B ↔ Asset X
```

Then B3 canonical Contact merge:

```text
Contact B → Contact A
```

Could B4 rewrite the historical relationship to Contact A? No. The relationship must preserve historical Contact attribution while allowing current navigation through A. The model already states this.

### Result

```text
TC-B4-R08 = PASS
```

---

## 15. TC-B4-R09 — Both endpoints merge

### Scenario

```text
R historically:
Contact B ↔ Asset Y

Later:
Contact B → Contact A
Asset Y   → Asset X
```

Current view:

```text
Contact A ↔ Asset X
```

Historical truth:

```text
R was established Contact B ↔ Asset Y
```

Both statements must coexist. The model supports precisely this distinction.

### Result

```text
TC-B4-R09 = PASS
```

---

## 16. Cross-endpoint correction attack

Now suppose:

```text
Contact B merge later corrected
Asset Y merge remains valid
```

The relationship must permit current interpretation:

```text
Contact B ↔ Asset X
```

while retaining original:

```text
Contact B ↔ Asset Y
```

This confirms a key principle:

> Relationship identity cannot be defined solely by the current canonical identities of its endpoints.

### Result

```text
TC-B4-R09A = PASS
```

---

## 17. O-B4-R04 — Logical relationship identity

The challenge can now close this more precisely.

> Two relationship records represent the same logical governed relationship only if they share a governed establishment identity or equivalent durable relationship identity.

They must not be considered identical solely because current canonical endpoints and relationship type happen to match. Therefore:

```text
current Contact
+
current Asset
+
relationship type
```

is insufficient as logical identity. A relationship needs its own durable identity.

### Resolution

```text
O-B4-R04 = RESOLVED
```

A `ContactAssetRelationship` must possess governed continuity independent of current canonical endpoint representation.

---

## 18. Relationship identity invariant

Add:

> Canonical endpoint evolution MUST NOT change the logical identity of an already-established ContactAssetRelationship.

This is essential for merges and corrections on either endpoint.

---

## 19. TC-B4-R10 — Automotive DRIVER in generic CPL

### Scenario

Automotive domain needs:

```text
DRIVER
```

Should generic CPL freeze DRIVER as a universal relationship type? No. The model correctly distinguishes:

```text
generic relationship envelope
+
domain-governed semantics
```

DRIVER belongs naturally to automotive semantics. Likewise:

```text
TENANT
```

may belong to property. This argues against a large universal generic enum.

### Result

```text
TC-B4-R10 = PASS
```

---

## 20. Generic vocabulary attack

Could CPL avoid generic vocabulary entirely and simply accept arbitrary strings? That would also be weak. The shared layer still needs semantic distinctions sufficient to govern:

```text
relationship identity
relationship lifecycle
authority
temporal behavior
history
domain ownership of type semantics
```

The right model is therefore not:

```text
one closed universal vocabulary
```

nor:

```text
uncontrolled free text
```

but:

```text
governed typed relationship namespace/envelope
```

with types owned either generically or by domain authority.

---

## 21. O-B4-R01 / R02 — Vocabulary and namespace

The challenge closes the architecture but not a large fixed vocabulary.

```text
O-B4-R01
Exact generic relationship vocabulary
```

Resolution:

> Generic CPL SHOULD NOT freeze an extensive cross-domain relationship vocabulary in B4. A minimal generic core MAY exist, but domain relationship semantics must remain extensible.

```text
O-B4-R02
namespace/domain-extension mechanism
```

Resolution:

> Every relationship type must have an identifiable semantic authority/namespace or equivalent ownership context.

Thus B4 requires conceptually:

```text
relationship semantic identifier
+
authority/namespace context
```

without prescribing a string format.

### Status

```text
O-B4-R01 = PARTIALLY RESOLVED
O-B4-R02 = RESOLVED AT WHAT LEVEL
```

The exact tiny generic core, if any, can be decided during consolidation.

---

## 22. TC-B4-R11 — Replay same establishment request

### Scenario

A governed establishment operation is repeated due to retry:

```text
request K:
Alice USER Asset A

request K repeated
```

The system must not create duplicate logical relationship state. Therefore idempotency must be tied to governed operation identity. However:

```text
same Contact
same Asset
same type
```

does not necessarily prove the same request. It could represent:

```text
two periods
two distinct authoritative assertions
correction
new establishment after prior end
```

### Result

```text
TC-B4-R11 = PASS_WITH_REFINEMENT
```

Required rule:

> same governed relationship-establishment operation identity within the same applicable scope → same logical establishment execution.

---

## 23. TC-B4-R12 — Similar records, different periods

### Scenario

```text
R1:
Alice USER Asset A
2025-01 → 2025-06

R2:
Alice USER Asset A
2026-01 →
```

They have the same endpoints and type. They are not necessarily duplicates. Therefore relationship logical identity must not be inferred merely from:

```text
Contact + Asset + type
```

The temporal/establishment context matters.

### Result

```text
TC-B4-R12 = PASS
```

This reinforces `O-B4-R04` closure.

---

## 24. O-B4-R10 — Idempotency semantics

The challenge can close this.

```text
O-B4-R10 = RESOLVED
```

Relationship establishment idempotency is based on:

```text
same governed establishment/request identity
+
same applicable execution scope
```

not on similarity of relationship content alone. Similarity may support duplicate assessment but not silently define request identity.

---

## 25. TC-B4-R13 — Evidence disagreement

### Scenario

```text
Evidence E1:
Alice OWNER Asset A

Evidence E2:
Bob SOLE_OWNER Asset A
```

What should generic CPL do? It cannot infer the truth without applicable relationship semantics and authority rules. Therefore it must support:

```text
CONTRADICTORY
AMBIGUOUS
UNRESOLVED
```

or equivalent governed non-resolution. It must not resolve using:

```text
latest evidence
highest confidence
administrator preference
```

unless applicable policy gives such characteristics authority. This mirrors Asset identity resolver precedence.

### Result

```text
TC-B4-R13 = PASS_WITH_REFINEMENT
```

Required invariant:

> Relationship evidence precedence and adjudication must arise from applicable relationship/domain authority policy, not generic CPL heuristics.

---

## 26. Relationship conflict governance

The challenge therefore establishes:

```text
Relationship Evidence
      ↓
Applicable Authority Policy
      ↓
Determination
      ↓
CanonicalRelationshipDecision
```

Where evidence conflict remains unresolved:

```text
CONTRADICTORY / UNRESOLVED
       ↓
NO unsupported canonical mutation
```

---

## 27. TC-B4-R14 — Relationship contributes to authorization

### Scenario

Another system asks:

> Is Alice allowed to modify Asset A?

and sees:

```text
Alice OWNER Asset A
```

Could B4 itself answer YES? No. B4 states only the canonical relationship. An authorization system may consume the relationship as an input. Other policy factors may apply. Therefore:

```text
relationship truth
≠ authorization decision
```

### Result

```text
TC-B4-R14 = PASS
```

---

## 28. Authorization leakage attack

Could an implementation expose:

```text
relationship.can_modify = true
```

as part of B4? Only if that field expresses domain relationship semantics already governed elsewhere. If it is actually a policy decision granting permissions, it belongs outside generic B4 relationship authority. The WHAT boundary survives.

---

## 29. TC-B4-R15 — Historical discoverability

### Scenario

Historical relationship:

```text
Contact B ↔ Asset Y
```

Both endpoints later merge. Can a historical query still determine the original relationship? The model explicitly requires this. Current navigation may return canonical successors. Historical query/provenance must still reconstruct:

```text
B ↔ Y
```

### Result

```text
TC-B4-R15 = PASS
```

---

## 30. Historical discoverability after correction

Suppose both endpoint merges are later partially corrected. The original relationship remains the same historical governed object. Only current interpretation/navigation changes. This confirms again that relationship identity must be independent from endpoint current canonical identity.

### Result

```text
TC-B4-R15A = PASS
```

---

## 31. Valid-time / decision-time challenge

Now attack the temporal model directly. Suppose CPL records on 1 June:

```text
relationship valid from 1 January
```

This means:

```text
valid time = 1 January
decision time = 1 June
```

Later on 1 August CPL learns the relationship actually began 1 March. The corrected valid-time statement changes. The historical fact that CPL previously believed 1 January must remain reconstructable. Therefore a single generic:

```text
created_at
updated_at
```

semantic cannot carry all required meaning.

### Result

```text
TEMPORAL MODEL = REQUIRES EXPLICIT REPAIR
```

---

## 32. O-B4-R07 — Valid time / decision time

Resolved at WHAT level:

```text
O-B4-R07 = RESOLVED
```

B4 must distinguish semantically:

```text
RELATIONSHIP VALID TIME
```

from:

```text
CPL DECISION TIME
```

where retroactive establishment/correction is supported. This does not prescribe bitemporal database architecture. It requires reconstructability of both dimensions.

---

## 33. Relationship status challenge

Could a simple status enum:

```text
ACTIVE
INACTIVE
```

represent:

```text
currently valid
ended valid relationship
relationship later corrected as never valid
disputed relationship
```

No. The dimensions are partially orthogonal. For example:

```text
historically recorded
currently not effective
retrospectively corrected
```

cannot be expressed cleanly by a single binary lifecycle. Therefore B4 should not freeze a simplistic status model.

---

## 34. O-B4-R05 — Status vocabulary

The challenge does not justify one universal flat enum. Instead it establishes minimum semantic distinctions:

```text
CURRENTLY EFFECTIVE

ENDED
  previously considered valid and later ceased

DISPUTED / UNRESOLVED
  current relationship truth is not settled

CORRECTED / SUPERSEDED INTERPRETATION
  prior canonical interpretation has been replaced
```

Implementation may represent these dimensions through state, decisions and temporal information.

### Status

```text
O-B4-R05 = PARTIALLY RESOLVED
```

The semantic distinctions are fixed; representation remains downstream.

---

## 35. Cardinality challenge

Can generic CPL determine:

```text
one OWNER
many OWNERS
one MANAGER
many MANAGERS
```

for every Asset type? No. Such constraints are relationship-type/domain-specific. The generic model must support policy-defined:

```text
cardinality
coexistence
compatibility
conflict
```

without inventing universal rules.

---

## 36. O-B4-R06 — Cardinality and conflict rules

Resolved structurally:

```text
O-B4-R06 = RESOLVED AT WHAT LEVEL
```

Generic CPL owns enforcement of applicable governed relationship constraints. The applicable relationship/domain semantic authority defines those constraints. No generic universal cardinality is established.

---

## 37. Asset merge disposition challenge

Suppose relationship R historically targets Asset B, then B merges into A. What disposition occurs? The generic answer should not be:

```text
REASSOCIATE R to A
```

because that destroys original attribution. Nor necessarily:

```text
do nothing
```

because current discovery must work. The correct relationship-level rule is:

```text
PRESERVE historical relationship identity/target
+
resolve current canonical endpoint separately
```

unless a relationship-specific canonical decision independently changes relationship semantics.

### Result

This substantially closes the generic relationship disposition under Asset merge.

---

## 38. O-B4-R08 — Asset merge/correction disposition

```text
O-B4-R08 = RESOLVED AT GENERIC WHAT LEVEL
```

Default generic behavior:

```text
PRESERVE relationship object
PRESERVE original Asset target
ALLOW current navigation via Asset canonical successor
DO NOT semantically reassign relationship merely due to Asset merge
```

If domain semantics require an actual relationship mutation, it must occur through a separate governed relationship decision. On Asset correction, current endpoint resolution changes accordingly without rewriting the historical relationship.

---

## 39. Contact merge disposition challenge

The same reasoning applies to Contact endpoint evolution. Therefore default:

```text
PRESERVE relationship object
PRESERVE original Contact target
ALLOW current navigation via Contact canonical successor
```

A Contact merge itself must not mutate relationship semantics.

---

## 40. O-B4-R09 — Contact merge/correction disposition

```text
O-B4-R09 = RESOLVED AT GENERIC WHAT LEVEL
```

The relationship follows current canonical endpoint navigation without being historically rewritten. Any semantic relationship change requires its own governed relationship decision.

---

## 41. Combined endpoint merge rule

This gives a powerful generic invariant:

> Canonical endpoint evolution affects current relationship interpretation/navigation; it does not, by itself, mutate the historical ContactAssetRelationship.

This applies symmetrically to Contact and Asset evolution.

---

## 42. CanonicalRelationshipDecision confirmed

Across:

```text
establishment
ending
retroactive correction
dispute resolution
supersession
relationship-specific mutation after endpoint changes
```

the challenge cannot preserve required governance history without a distinct decision concept. Therefore:

```text
CanonicalRelationshipDecision
= REQUIRED SEMANTIC OBJECT
```

This is the principal structural finding of the challenge.

---

## 43. Decision types

At minimum, the semantic decision space must support:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

Potential:

```text
HOLD
REJECT
```

may be outcomes of admission rather than canonical mutation decisions. The exact state machine remains for consolidation.

---

## 44. Relationship decision minimum semantics

A durable relationship decision must make recoverable at least:

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
result
superseded decision where applicable
provenance
```

This is semantic, not a schema mandate.

---

## 45. Relationship establishment identity

A new canonical relationship must itself have stable identity. Endpoint canonical changes must not change this identity. Thus relationship identity is conceptually anchored by:

```text
relationship_id
```

or semantically equivalent stable CPL identity. The database already has a relationship object in B2; B4 should preserve its continuity rather than derive relationship identity dynamically from current endpoints.

---

## 46. No duplicate derivation from endpoints

Therefore prohibited:

```text
same current Contact
+
same current Asset
+
same type
=
same logical relationship
```

This may be evidence of duplication, but is not authoritative identity.

---

## 47. Logical relationship identity result

The challenge establishes:

> A ContactAssetRelationship is a persistent governed CPL object whose logical identity survives changes in endpoint canonical representation, relationship status, and canonical interpretation.

That is stronger and cleaner than a compound-key ontology.

---

## 48. Vocabulary architecture result

The challenge favors:

```text
GENERIC CPL RELATIONSHIP ENVELOPE
        +
GOVERNED RELATIONSHIP TYPE IDENTIFIER
        +
TYPE AUTHORITY / NAMESPACE
        +
DOMAIN-SPECIFIC SEMANTICS
```

rather than a giant closed enum. A minimal generic core may still be useful, but it is not necessary to stabilize the relationship ontology.

---

## 49. O-B4-R01 residual

The only remaining vocabulary question is therefore:

> Does B4 need any mandatory generic types at all, or only a governed extensible type system?

This can be settled during B4 WHAT consolidation without blocking the Relationship authority model.

```text
O-B4-R01 = NARROWED / NON-BLOCKING
```

---

## 50. Conflict authority result

Relationship conflict semantics are governed by:

```text
relationship semantic type
domain/context
valid time
evidence
authority policy
cardinality/compatibility rules
```

Generic CPL preserves and enforces the governed result but does not invent underlying domain truth.

---

## 51. Relationship determination layer

The challenge shows that we do need the semantic distinction:

```text
Relationship Evidence
      ↓
Relationship Determination / Admission
      ↓
CanonicalRelationshipDecision
      ↓
Canonical Relationship Interpretation
```

But a dedicated persisted `RelationshipDetermination` object is not yet proven necessary. Evidence + authority/admission + decision may be sufficient. Therefore we should not invent another first-class object unless later consolidation requires it.

---

## 52. No over-ontologization

This is important. B4 already requires:

```text
ContactAssetRelationship
CanonicalRelationshipDecision
```

It does not yet require:

```text
RelationshipEvidence table
RelationshipDetermination table
RelationshipConflict table
RelationshipHistory table
```

as independent objects. Their semantics may be represented through existing structures and provenance. The WHAT should freeze semantics, not multiply tables.

---

## 53. Reconciliation with Asset Authority submodel

The two B4 submodels now align:

```text
ASSET SIDE

Evidence
 ↓
AssetIdentityResolution
 ↓
CanonicalAssetIdentityDecision
 ↓
Canonical Asset interpretation
```

and:

```text
RELATIONSHIP SIDE

Evidence / authority
 ↓
Relationship admission
 ↓
CanonicalRelationshipDecision
 ↓
Canonical relationship interpretation
```

But they retain different domain authorities. This symmetry is useful without implying identical implementation.

---

## 54. Cross-B3 symmetry

Likewise B3 already established:

```text
identity evidence
≠ resolution
≠ canonical mutation
```

B4 relationship governance now follows the same deeper pattern:

```text
evidence
≠ determination/admission
≠ canonical decision
```

This suggests a transversal CPL governance pattern rather than ad hoc tables.

---

## 55. Challenge findings

The targeted challenge produces these required repairs:

```text
R-B4-R01
Require durable CanonicalRelationshipDecision.

R-B4-R02
Recognize valid-time and decision-time as distinct semantics.

R-B4-R03
Define ContactAssetRelationship as having stable logical identity
independent of current canonical endpoint identities.

R-B4-R04
Define relationship idempotency from governed establishment/request
identity, not endpoint/type similarity.

R-B4-R05
Govern relationship evidence precedence/conflict through applicable
relationship/domain authority policy.

R-B4-R06
Define generic endpoint merge behavior as historical preservation
plus current canonical navigation, not semantic reassignment.

R-B4-R07
Define relationship cardinality/compatibility as type/domain-governed,
not globally inferred.

R-B4-R08
Preserve END versus CORRECT versus SUPERSEDE distinction.
```

---

## 56. Open-question disposition

After challenge:

```text
O-B4-R01
Exact generic vocabulary
    → NARROWED / NON-BLOCKING

O-B4-R02
Type namespace/domain extension
    → RESOLVED AT WHAT LEVEL

O-B4-R03
CanonicalRelationshipDecision
    → RESOLVED / REQUIRED

O-B4-R04
Logical relationship identity
    → RESOLVED

O-B4-R05
Status/state vocabulary
    → PARTIALLY RESOLVED

O-B4-R06
Cardinality/conflict
    → RESOLVED AT WHAT LEVEL

O-B4-R07
Valid time vs decision time
    → RESOLVED

O-B4-R08
Asset merge/correction disposition
    → RESOLVED AT GENERIC WHAT LEVEL

O-B4-R09
Contact merge/correction disposition
    → RESOLVED AT GENERIC WHAT LEVEL

O-B4-R10
Idempotency
    → RESOLVED
```

No open item requires reopening the stabilized Asset Authority model.

---

## 57. New relationship invariants

**B4-RI18 — Stable relationship identity**
A ContactAssetRelationship has governed persistent identity independent of current endpoint canonical representations.

**B4-RI19 — Canonical relationship decision durability**
Material canonical relationship changes require durable governed decision provenance.

**B4-RI20 — Decision supersession**
Relationship correction/supersession does not erase prior canonical decisions.

**B4-RI21 — Valid-time / decision-time separation**
Relationship truth time and CPL decision time are semantically distinct where retroactive correction applies.

**B4-RI22 — Endpoint evolution preservation**
Contact or Asset canonical evolution does not itself rewrite relationship semantics or historical attribution.

**B4-RI23 — Relationship idempotency identity**
Logical request replay is determined by governed operation identity, not endpoint/type similarity.

**B4-RI24 — Conflict policy authority**
Relationship conflict/precedence derives from applicable semantic authority policy, not generic implementation heuristics.

**B4-RI25 — Type-governed cardinality**
Same-type multiplicity and incompatibility are governed by relationship semantics/domain policy.

**B4-RI26 — End/correction/supersession separation**
END, CORRECT, and SUPERSEDE are distinct semantic changes.

---

## 58. TC results

| Challenge | Result |
|---|---|
| R01 simultaneous owners | PASS |
| R02 simultaneous sole owners | PASS_WITH_REFINEMENT |
| R03 self-asserted ownership | PASS |
| R04 valid then ended | PASS |
| R05 later proven never valid | PASS_WITH_REFINEMENT |
| R06 retroactive correction | PASS_WITH_REPAIR |
| R07 Asset endpoint merge/correction | PASS |
| R08 Contact endpoint merge | PASS |
| R09 both endpoints merge | PASS |
| R10 domain DRIVER | PASS |
| R11 establishment replay | PASS_WITH_REFINEMENT |
| R12 same relationship/different periods | PASS |
| R13 contradictory evidence | PASS_WITH_REFINEMENT |
| R14 authorization use | PASS |
| R15 historical discoverability | PASS |

The fundamental model survives all attacks.

---

## 59. Overall verdict

The v0 Relationship Object & Authority Model is not rejected. Its fundamental architecture is valid. But the challenge discovered eight normative repairs that must be incorporated before the relationship submodel can be stabilized. Therefore:

```text
B4_RELATIONSHIP_TARGETED_CHALLENGE_v0

CORE MODEL:
  PASS

OVERALL VERDICT:
  REPAIR_REQUIRED

WHAT REOPENING:
  NO

ASSET AUTHORITY REOPENING:
  NO

IMPLEMENTATION:
  NOT AUTHORIZED
```

---

## 60. Authorized repair boundary

The next repair is limited to:

```text
R-B4-R01 → R-B4-R08
```

It must not expand B4 into:

```text
authorization engine
social graph
Contact–Contact relationship system
Asset–Asset topology
domain-specific workflow system
```

---

## 61. Next artifact

Produce:

```text
B4_RELATIONSHIP_OBJECT_AND_AUTHORITY_MODEL_v0.1.md
```

It must incorporate the eight repairs while preserving v0 historically. Then perform:

```text
B4_RELATIONSHIP_TARGETED_RE_CHALLENGE_v0.1
```

The re-challenge should be considerably narrower.

---

## 62. Re-challenge targets

At minimum:

```text
RC-B4-R01
Can endpoint canonical changes still rewrite relationship identity?

RC-B4-R02
Can a correction be confused with an ordinary relationship end?

RC-B4-R03
Can retroactive correction destroy decision history?

RC-B4-R04
Can relationship duplication be inferred from current endpoints/type?

RC-B4-R05
Can conflicting evidence be resolved through implementation heuristics?

RC-B4-R06
Can cardinality be accidentally globalized?

RC-B4-R07
Can relationship changes occur without CanonicalRelationshipDecision?

RC-B4-R08
Can Asset/Contact merge silently mutate relationship semantics?

RC-B4-R09
Can domain relationship type semantics leak into generic CPL authority?

RC-B4-R10
Can a relationship itself become an authorization decision?
```

---

## 63. Governance status

```text
B4 Asset Authority submodel
  STABILIZED

B4 Relationship Object & Authority Model v0
  MATERIALIZED
  CHALLENGED
  REPAIR_REQUIRED

B4 Relationship Targeted Challenge v0
  COMPLETED

B4 Relationship Object & Authority Model v0.1
  AUTHORIZED FOR PRODUCTION

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

## 64. Final result

```text
B4 RELATIONSHIP TARGETED CHALLENGE v0
=====================================

15 PRIMARY CHALLENGE CASES

CORE ARCHITECTURE:
  SURVIVES

NEW REQUIRED SEMANTIC OBJECT:
  CanonicalRelationshipDecision

MAJOR TEMPORAL DISCOVERY:
  VALID TIME ≠ CPL DECISION TIME

RELATIONSHIP IDENTITY:
  STABLE INDEPENDENT OBJECT

ENDPOINT MERGE:
  NAVIGATION CHANGE ≠ RELATIONSHIP REWRITE

IDEMPOTENCY:
  GOVERNED REQUEST IDENTITY

CARDINALITY:
  TYPE / DOMAIN GOVERNED

EVIDENCE CONFLICT:
  AUTHORITY-POLICY GOVERNED

OVERALL:
  REPAIR_REQUIRED

NEXT:
  B4_RELATIONSHIP_OBJECT_AND_AUTHORITY_MODEL_v0.1
```

**END — B4 Relationship Targeted Challenge v0**

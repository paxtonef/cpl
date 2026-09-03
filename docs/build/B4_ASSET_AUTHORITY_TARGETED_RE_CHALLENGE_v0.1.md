# CPL — B4 Asset Authority Targeted Re-Challenge v0.1

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Asset Authority Targeted Re-Challenge
**Version:** v0.1
**Status:** RE-CHALLENGE COMPLETED — PASS
**Challenged artifact:** `B4_ASSET_OBJECT_AND_AUTHORITY_MAP_v0.1.md`
**Repair source:** `B4_ASSET_AUTHORITY_TARGETED_CHALLENGE_v0.md`
**Canonical materialization baseline:** `main @ 9b0c7ed01f7fdf03afd4e1818c79a833abd0adc2`
**Implementation authorization:** NONE

---

## 1. Purpose

This re-challenge determines whether the five repairs authorized by the B4 Asset Authority Targeted Challenge actually close the weaknesses identified in v0 without introducing new authority leakage or historical inconsistency.

The repaired model must survive:

```text
RC-B4-01  cloned identifier
RC-B4-02  mutable identifier
RC-B4-03  contradictory resolvers
RC-B4-04  physical identity convergence + dependency conflict
RC-B4-05  erroneous historical merge
RC-B4-06  historical dependencies
RC-B4-07  indirect domain-resolver canonical mutation
RC-B4-08  administrative bypass
RC-B4-09  canonical mutation without durable decision
RC-B4-10  correction destroying earlier evidence
```

A PASS stabilizes the Asset Authority submodel only. It does not freeze the complete B4 WHAT.

---

## 2. Repair set under verification

The challenged v0.1 incorporates:

```text
R-B4-01
Durable CanonicalAssetIdentityDecision

R-B4-02
Canonical correction through supersession

R-B4-03
Dependency non-convergence

R-B4-04
Historical target preservation

R-B4-05
Explicit resolver precedence governance
```

The re-challenge must verify these as interacting rules, not independently.

---

## 3. Authority architecture under re-challenge

```text
DOMAIN

Evidence
   ↓
Authorized Identity Resolver
   ↓
AssetIdentityResolution
   │
════════ AUTHORITY BOUNDARY ════════
   │
   ▼
CPL

Identity admissibility
   ↓
Conflict governance
   ↓
Structural admission
   ↓
Dependency disposition sufficiency
   ↓
CanonicalAssetIdentityDecision
   ↓
Current Canonical Representation
```

Fundamental invariant:

> DOMAIN DETERMINES PHYSICAL IDENTITY; CPL GOVERNS CANONICAL IDENTITY.

---

## 4. RC-B4-01 — Cloned identifier

### Attack

Two genuinely different vehicles possess the same apparent VIN:

```text
Asset A → VIN X
Asset B → VIN X

but:

A ≠ B physically
```

Can identifier equality reach canonical merge without domain resolution?

### v0.1 path

```text
VIN equality
    ↓
identity evidence / hypothesis
    ↓
authorized identity resolution required
```

The following path is prohibited:

```text
VIN equality → canonical merge
```

Even a strong identifier has no merge authority.

### Result

```text
RC-B4-01 = PASS
```

No bypass exists in the WHAT.

---

## 5. RC-B4-02 — Mutable identifier

### Attack

One physical vehicle changes registration:

```text
T1 → registration X
T2 → registration Y
```

Can CPL interpret the new identifier as a new physical Asset automatically? No. v0.1 preserves:

```text
Asset identity
    ≠
identifier lifecycle
```

Neither adding nor replacing an identifier establishes physical-object discontinuity.

### Result

```text
RC-B4-02 = PASS
```

---

## 6. RC-B4-03 — Contradictory resolvers

### Attack

```text
R1 → SAME_PHYSICAL_ASSET
R2 → NOT_SAME_PHYSICAL_ASSET
```

Can an implementation silently choose R1 because it:

```text
ran later
has confidence .98
was inserted last
came from a preferred code path
```

No. v0.1 explicitly prohibits implicit precedence based on:

```text
recency
execution order
confidence
database order
implementation preference
```

unless an applicable authority policy gives such a property authoritative meaning. Absent governed precedence:

```text
CONTRADICTORY
      ↓
NO MERGE
```

### Result

```text
RC-B4-03 = PASS
```

`R-B4-05` closes the original weakness.

---

## 7. Resolver precedence does not leak into CPL authority

A second attack is necessary. Suppose CPL stores domain precedence metadata. Could CPL then be considered the authority deciding which resolver is correct? No.

The model distinguishes:

```text
CPL stores/applies authority policy
```

from:

```text
CPL authors domain authority policy
```

The former is permissible. The latter is not implied. Therefore application of a domain-governed rule does not transfer domain epistemic authority to CPL.

### Result

```text
RC-B4-03A = PASS
```

---

## 8. RC-B4-04 — Identity convergence with dependency conflict

### Attack

Authorized resolution establishes:

```text
A = B physically
```

while:

```text
A → OWNER Alice
B → OWNER Bob
```

Can CPL infer relationship convergence merely because Asset identity converged? No.

v0.1 explicitly establishes:

```text
Asset identity convergence
        ≠
dependency semantic convergence
```

and separately:

```text
Asset identity reconciliation
        ≠
ContactAssetRelationship adjudication
```

A positive physical identity resolution therefore does not settle ownership truth.

---

## 9. Structural admission attack

Could CPL nevertheless merge A/B while leaving unresolved dependencies in an unsafe state?

v0.1 introduces:

```text
SAME_PHYSICAL_ASSET
        ↓
CPL structural admission
        ↓
dependency disposition sufficiency
        ↓
MERGE or HOLD
```

Therefore a positive domain determination does not force structural execution. The correct governed result may be:

```text
physical identity = resolved
canonical merge = HOLD
```

### Result

```text
RC-B4-04 = PASS
```

`R-B4-03` successfully separates identity convergence from dependency convergence.

---

## 10. RC-B4-05 — Erroneous historical merge

### Attack

```text
R1:
A = B

M1:
MERGE B → A

later:

R2:
A ≠ B
```

Can the model restore correct current representation without pretending M1 never happened?

v0.1 provides:

```text
R1
 ↓
M1
 ↓
canonical A ← B
 ↓
R2
 ↓
C1
type = CORRECTION
supersedes current effect of M1
 ↓
canonical A / B distinct
```

M1 remains historical. R1 remains historical. The current canonical effect changes.

### Result

```text
RC-B4-05 = PASS
```

This is the principal validation of `R-B4-01` + `R-B4-02`.

---

## 11. Correction-loop attack

Now attack the correction itself. Suppose:

```text
M1 → merge
C1 → correct merge
M2 → later evidence again establishes sameness
```

Does supersession permit repeated canonical evolution without destroying prior history? Yes, conceptually:

```text
M1
 ↓
C1 supersedes M1 current effect
 ↓
M2 supersedes C1 current effect
```

provided each mutation is separately governed and evidence-backed. Therefore the model is not limited to a single merge/unmerge cycle. It supports canonical history.

### Result

```text
RC-B4-05A = PASS
```

---

## 12. Critical semantic confirmation

The re-challenge confirms that the new object is necessary:

```text
CanonicalAssetIdentityDecision
```

because neither:

```text
Asset
```

nor:

```text
AssetIdentityResolution
```

can independently represent:

```text
what CPL decided
when
why
under what authority
what current canonical effect resulted
what later superseded that effect
```

Therefore:

```text
AssetIdentityResolution
        ≠
CanonicalAssetIdentityDecision
```

survives re-challenge.

---

## 13. RC-B4-06 — Historical dependencies

### Attack

Before merge:

```text
Case C → Asset B
ExternalReference E → Asset B
Relationship R → Asset B
```

After:

```text
B → A canonically
```

Could implementation rewrite the historical records so that they appear always to have referenced A? No.

v0.1 requires:

```text
ORIGINAL HISTORICAL TARGET
        ≠
CURRENT CANONICAL TARGET
```

where semantically relevant. And requires reconstructability of the original Asset attribution.

### Result

```text
RC-B4-06 = PASS
```

`R-B4-04` closes the historical-rewrite vulnerability.

---

## 14. Navigation attack

Could historical preservation prevent useful current navigation? No.

The model permits:

```text
historical:
Case C → B

canonical:
B → A

current navigation:
A exposes Case C
```

while prohibiting the false assertion:

```text
Case C originally referenced A
```

Current navigation and historical provenance coexist.

### Result

```text
RC-B4-06A = PASS
```

---

## 15. RC-B4-07 — Indirect resolver canonical mutation

This attack tests the authority boundary itself. Suppose VIR returns:

```text
SAME_PHYSICAL_ASSET
```

and CPL automatically executes merge with no independently represented canonical decision. Functionally, VIR would then control canonical topology even if the code technically lived inside CPL. That would violate the authority model.

v0.1 blocks this through:

```text
Resolution
   ↓
CPL admission
   ↓
CanonicalAssetIdentityDecision
   ↓
canonical mutation
```

The decision layer cannot be omitted semantically.

### Result

```text
RC-B4-07 = PASS
```

---

## 16. Stronger RC-B4-07 attack — deterministic admission

Suppose every SAME_PHYSICAL_ASSET determination always results in merge. Would the presence of a CanonicalAssetIdentityDecision object alone preserve the authority boundary? No.

A decorative decision record generated after an automatic domain-triggered merge would not constitute real CPL governance. v0.1 already prevents this because:

```text
positive identity determination
    = necessary
    ≠ sufficient
```

and structural admission may produce HOLD. Therefore canonical decision must represent an actual governed CPL admission, not merely audit logging of a resolver command.

### Result

```text
RC-B4-07A = PASS
```

This is an important confirmation.

---

## 17. RC-B4-08 — Administrative bypass

### Attack

An administrator knows that A/B are duplicates and directly triggers:

```text
merge(A,B)
```

without domain identity determination. Could administrative privilege constitute canonical authority? No.

v0.1 explicitly establishes:

```text
human/admin intervention
    MAY contribute evidence/adjudication where authorized
```

but

```text
admin action
    MUST NOT bypass merge admission
```

Therefore operational privilege is not epistemic authority.

### Result

```text
RC-B4-08 = PASS
```

---

## 18. Authorized human adjudication

What if domain policy explicitly makes a qualified human reviewer an authorized adjudicator? That is different. The human conclusion then enters as:

```text
authorized domain adjudication
```

not:

```text
administrative bypass
```

It still passes through CPL canonical admission. Thus the model distinguishes:

```text
human authority under policy
```

from:

```text
human technical privilege
```

### Result

```text
RC-B4-08A = PASS
```

---

## 19. RC-B4-09 — Silent canonical mutation

### Attack

A developer implements merge by changing pointers/FKs but creates no durable canonical decision. Could the resulting database nevertheless be considered compliant because the final state is correct? No.

v0.1 contains:

> Any change to current canonical Asset identity representation MUST be attributable to a durable governed canonical identity decision.

Thus:

```text
correct final topology
+
no canonical decision provenance
=
NON-CONFORMING
```

### Result

```text
RC-B4-09 = PASS
```

---

## 20. Decision-record attack

Could an unstructured log line satisfy this requirement? For example:

```text
INFO merged B into A
```

No. The required decision must be sufficiently first-class to support:

```text
reference
traceability
authority
supporting-resolution linkage
time
status
supersession
audit
```

A log message cannot reliably carry the required canonical semantics.

### Result

```text
RC-B4-09A = PASS
```

---

## 21. Implementation-neutrality attack

Conversely, does requiring a durable canonical decision accidentally prescribe a SQL table? No.

v0.1 explicitly distinguishes semantic object from physical implementation. A conforming implementation might theoretically use:

```text
relational record
event representation
other durable governed representation
```

provided all frozen semantics are satisfied. Therefore WHAT remains implementation-neutral.

### Result

```text
RC-B4-09B = PASS
```

---

## 22. RC-B4-10 — Correction destroys earlier evidence

### Attack

After discovering an erroneous merge, implementation:

```text
restores A/B
deletes R1
deletes M1
retains only R2/C1
```

The current state becomes correct. Is this compliant? No.

v0.1 explicitly requires evidence continuity and historical decision preservation. The valid chain remains:

```text
Evidence E1
 ↓
Resolution R1
 ↓
Decision M1
 ↓
former canonical effect
 ↓
Evidence E2
 ↓
Resolution R2
 ↓
Correction C1
 ↓
current canonical effect
```

### Result

```text
RC-B4-10 = PASS
```

---

## 23. Evidence-correction attack

Suppose earlier evidence was objectively wrong. Should it still be preserved? Yes, as historical evidence received/used — not as currently valid truth. This distinction is essential:

```text
historically existed evidence
    ≠
currently accepted conclusion
```

Deleting bad evidence would make the governance history less intelligible, not more correct.

### Result

```text
RC-B4-10A = PASS
```

---

## 24. Cross-test — cloned VIN followed by erroneous merge

Combine RC-B4-01 and RC-B4-05:

```text
same VIN
 ↓
resolver mistakenly says SAME
 ↓
CPL admits merge
 ↓
later forensic resolver says NOT_SAME
```

Can the model recover? Yes. The first resolver conclusion and CPL decision remain historical. The later authorized resolution supports a correction decision. Separate canonical identity can be restored without falsifying the previous state.

### Result

```text
RC-B4-X01 = PASS
```

---

## 25. Cross-test — resolver conflict during correction

Suppose after M1:

```text
R2 → NOT_SAME
R3 → SAME
```

with no governed precedence. Can correction occur? No. The identity state is contradictory. Therefore:

```text
CONTRADICTORY
    ↓
NO automatic correction
```

The current state may itself be suspect, but CPL must not invent the replacement truth. Explicit unresolvedness is permitted.

### Result

```text
RC-B4-X02 = PASS
```

---

## 26. Important consequence

The previous result means:

```text
NO MERGE
```

and:

```text
NO CORRECTION
```

can both be correct governed outcomes under insufficient authority. Governance is not equivalent to forcing resolution. This is consistent with the broader CPL doctrine.

---

## 27. Cross-test — merge with unresolved ownership

Suppose:

```text
physical identity:
A = B
```

but ownership records conflict. Does this necessarily prevent Asset merge forever? Not necessarily.

The model says dependency disposition must be sufficiently governed for safe execution. Depending on later relationship semantics, the result could be:

```text
PRESERVE_AS_HISTORICAL
RECONCILE
HOLD
```

etc. But Asset identity authority itself cannot decide ownership.

### Result

```text
RC-B4-X03 = PASS
```

No authority leakage detected.

---

## 28. Cross-test — domain resolver attempts survivor selection

Suppose VIR says:

```text
A and B are same vehicle.
Keep A.
```

Can "Keep A" bind CPL? Not merely by virtue of VIR's physical identity authority. Survivor selection concerns CPL canonical representation. Unless an explicit future contract grants domain input a role in survivor selection, CPL retains that authority.

### Result

```text
RC-B4-X04 = PASS
```

---

## 29. Remaining weakness: survivor-selection policy

The re-challenge confirms the authority owner but not the complete rule:

```text
WHO chooses survivor?
    CPL

BY WHAT COMPLETE POLICY?
    not yet frozen
```

This does not invalidate the Asset Authority submodel. It identifies work for later B4 consolidation. It MUST NOT be invented by implementation.

---

## 30. Remaining weakness: dependency-family disposition

Likewise:

```text
identity convergence ≠ dependency convergence
```

is frozen enough at the authority level. But exact treatment for every family remains incomplete. Therefore `O-B4-02` remains:

```text
PARTIALLY RESOLVED
```

and cannot yet disappear from B4's open-question registry.

---

## 31. Remaining weakness: ContactAssetRelationship vocabulary

Nothing in the re-challenge establishes a complete vocabulary. Therefore:

```text
O-B4-03 = OPEN
```

This is intentionally preserved. A PASS here must not be misread as permission to silently invent:

```text
OWNER
DRIVER
LESSEE
USER
MANAGER
...
```

as the complete canonical vocabulary.

---

## 32. Re-challenge results

| Test | Result |
|---|---|
| RC-B4-01 | PASS |
| RC-B4-02 | PASS |
| RC-B4-03 | PASS |
| RC-B4-03A | PASS |
| RC-B4-04 | PASS |
| RC-B4-05 | PASS |
| RC-B4-05A | PASS |
| RC-B4-06 | PASS |
| RC-B4-06A | PASS |
| RC-B4-07 | PASS |
| RC-B4-07A | PASS |
| RC-B4-08 | PASS |
| RC-B4-08A | PASS |
| RC-B4-09 | PASS |
| RC-B4-09A | PASS |
| RC-B4-09B | PASS |
| RC-B4-10 | PASS |
| RC-B4-10A | PASS |
| RC-B4-X01 | PASS |
| RC-B4-X02 | PASS |
| RC-B4-X03 | PASS |
| RC-B4-X04 | PASS |

**22 / 22 PASS**

---

## 33. Repair verification

```text
R-B4-01
Durable CanonicalAssetIdentityDecision
    → VERIFIED

R-B4-02
Correction through supersession
    → VERIFIED

R-B4-03
Dependency non-convergence
    → VERIFIED

R-B4-04
Historical target preservation
    → VERIFIED

R-B4-05
Explicit resolver precedence governance
    → VERIFIED
```

**5 / 5 repairs survive re-challenge.**

---

## 34. Authority leakage verification

No tested path permits:

```text
identifier → canonical authority
resolver → direct canonical mutation
administrator → governance bypass
CPL → domain identity invention
Asset merge → relationship adjudication
canonical merge → historical erasure
canonical correction → evidence destruction
```

Result:

```text
AUTHORITY LEAKAGE:
NONE FOUND IN REPAIRED MODEL
```

---

## 35. Ontological verification

The re-challenge confirms the necessity and separation of:

```text
Asset
AssetIdentifier
AssetIdentityResolution
CanonicalAssetIdentityDecision
ContactAssetRelationship
```

Particularly:

```text
PHYSICAL REALITY
      ↓
RESOLUTION
      ↓
CANONICAL DECISION
      ↓
PRODUCT REPRESENTATION
```

These are different ontological layers. Collapsing any adjacent pair would reintroduce one of the challenged failures.

---

## 36. Asset Authority submodel decision

The repaired submodel may now be considered:

```text
STABILIZED
```

for continuation of B4 WHAT work. This means its authority allocation and core invariants should no longer be casually reopened downstream. It does not mean:

```text
B4 WHAT = FROZEN
```

---

## 37. Stabilized authority invariants

The following survive targeted challenge and re-challenge:

```text
B4-AI13 Decision durability
B4-AI14 Decision supersession
B4-AI15 Dependency non-convergence
B4-AI16 Historical target preservation
B4-AI17 Resolver precedence governance
B4-AI18 Relationship adjudication independence
B4-AI19 Resolution/decision separation
B4-AI20 No silent canonical mutation
B4-AI21 Evidence continuity
B4-AI22 Current/history distinction
```

Together with the retained v0 authority invariants, these form the stabilized Asset Authority invariant set.

---

## 38. Open questions after PASS

The re-challenge does not manufacture closure where none exists. Remaining:

```text
O-B4-02
Exact dependency-family disposition semantics
    → PARTIALLY RESOLVED

O-B4-03
ContactAssetRelationship vocabulary
    → OPEN

Canonical survivor-selection policy
    → REQUIRES B4 CONTINUATION
```

These are now the important unresolved B4 matters around the Asset/Relationship model.

---

## 39. No Requirement Matrix yet

The Asset Authority submodel passing does not establish complete B4 requirements. The following remain premature:

```text
B4_REQUIREMENT_MATRIX
B4_EXECUTION_MANDATE
B4 implementation
```

because B4 WHAT itself remains incomplete.

---

## 40. No code authorization

This PASS MUST NOT be interpreted as authorization to implement:

```text
CanonicalAssetIdentityDecision
merge service
correction service
resolver-precedence engine
dependency-reconciliation engine
```

The semantic objects are now stabilized, but implementation remains downstream of the complete B4 WHAT freeze and requirement process.

---

## 41. Re-challenge verdict

```text
B4_ASSET_AUTHORITY_TARGETED_RE_CHALLENGE_v0.1

RESULT:
    PASS

TESTS:
    22 / 22 PASS

REPAIRS:
    5 / 5 VERIFIED

CORE AUTHORITY MODEL:
    STABILIZED

ASSET MERGE AUTHORITY:
    STABILIZED

CANONICAL CORRECTION SEMANTICS:
    STABILIZED

RESOLUTION / DECISION SEPARATION:
    STABILIZED

HISTORICAL PRESERVATION:
    STABILIZED

RESOLVER PRECEDENCE AUTHORITY:
    STABILIZED

AUTHORITY LEAKAGE:
    NONE FOUND
```

---

## 42. Governance state

```text
B4 WHAT Definition v0
    MATERIALIZED

B4 Asset Object & Authority Map v0
    MATERIALIZED
    CHALLENGED
    REPAIR_REQUIRED

B4 Asset Authority Targeted Challenge v0
    COMPLETED
    REPAIR_REQUIRED

B4 Asset Object & Authority Map v0.1
    PRODUCED
    REPAIRED
    TARGETED RE-CHALLENGE PASSED

B4 Asset Authority Targeted Re-Challenge v0.1
    COMPLETED
    PASS

B4 Asset Authority submodel
    STABILIZED

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

## 43. Next B4 work

We should not immediately perform a global B4 freeze challenge. The targeted work has done its job: Asset authority is no longer the blocking uncertainty. The remaining WHAT work now shifts to the relationship side and the remaining dependency semantics.

The next logical artifact is therefore:

```text
B4_RELATIONSHIP_OBJECT_AND_AUTHORITY_MODEL_v0
```

Its job should be narrower than the Asset Authority work:

```text
ContactAssetRelationship
        ↓
What does a relationship assert?

Who may assert it?

Who may determine its validity?

Can multiple relationships coexist?

How does time affect it?

How are contradiction and supersession represented?

What survives Asset merge/correction?

Which relationship concepts belong to generic CPL
versus domain packs?
```

Only after that should we consolidate Asset + Relationship semantics into the complete B4 WHAT.

**END — B4 Asset Authority Targeted Re-Challenge v0.1**

# CPL — B4 Requirement Challenge v0

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Requirement Challenge
**Version:** v0
**Status:** CHALLENGE COMPLETED — REPAIR REQUIRED
**Canonical baseline:** `main @ bfb3d16`
**Primary challenged artifact:** `B4_REQUIREMENT_MATRIX_v0.md`
**Frozen source:** `B4 WHAT = FROZEN`
**Implementation authorization:** NONE

---

## 1. Challenge purpose

This challenge tests whether `REQ-B4-001 → REQ-B4-240` faithfully and completely translate the frozen B4 WHAT into testable requirements without:

```text
inventing HOW
omitting frozen semantics
weakening authority boundaries
introducing contradictions
creating false implementation freedom
or reopening WHAT implicitly
```

Allowed outcomes:

```text
REQUIREMENTS_ACCEPTED
REPAIR_REQUIRED
WHAT_CONFLICT
```

---

# 2. Challenge standard

A requirement matrix is acceptable only if:

```text
1. every normative requirement is traceable to frozen WHAT;

2. every frozen WHAT obligation that matters to implementation
   appears in at least one atomic requirement;

3. requirements are testable enough to drive acceptance;

4. implementation freedom remains only where WHAT intentionally
   leaves HOW open;

5. no requirement silently alters the frozen ontology or authority model.
```

---

# 3. RC-B4-REQ-01 — Traceability of all 240 requirements

A family-by-family review finds that the matrix tracks the frozen B4 object set and authority boundaries correctly.

Coverage exists for:

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

and for:

```text
merge
correction
survivor selection
dependency disposition
valid time / decision time
endpoint evolution
idempotency
conflict/cardinality
history/provenance
domain/CPL authority
B3 compatibility
non-regression
verification
```

### Result

```text
RC-B4-REQ-01 = PASS
```

---

# 4. RC-B4-REQ-02 — Did the matrix invent HOW?

Most requirements remain implementation-neutral.

Examples of correctly preserved WHAT-level freedom:

```text
"or semantically equivalent"
"must preserve"
"must support"
"must remain distinguishable"
```

No requirement mandates:

```text
specific SQL table
specific endpoint path
specific ORM class
event sourcing
message broker
bitemporal database
specific transaction engine
```

### Result

```text
RC-B4-REQ-02 = PASS
```

---

# 5. RC-B4-REQ-03 — Missing frozen semantics

The matrix is broad, but three frozen semantics are not yet translated sharply enough for implementation acceptance.

They concern:

```text
A. canonical mutation atomicity / decision-effect consistency

B. dependency disposition completeness before merge execution

C. canonical navigation versus historical attribution behavior
   at query/consumption boundaries
```

These omissions do not reopen WHAT.

They require bounded requirement repair.

### Result

```text
RC-B4-REQ-03 = FAIL — REPAIR REQUIRED
```

---

# 6. Missing requirement A — decision and canonical effect consistency

Frozen B4 semantics require:

```text
CanonicalAssetIdentityDecision
    ↓
canonical effect
```

and:

```text
CanonicalRelationshipDecision
    ↓
canonical effect
```

The matrix requires durable decisions, but does not explicitly require that a canonical state mutation and its authoritative decision remain **consistently committed as one governed effect**.

Without this, an implementation could produce:

```text
decision persisted
canonical state mutation failed
```

or:

```text
canonical state changed
decision persistence failed
```

and still arguably satisfy several existing requirements individually.

That would violate the frozen governance model.

---

# 7. Required repair RM-B4-01 — Canonical decision/effect consistency

Add a requirement family establishing:

> A canonical Asset or Relationship mutation MUST NOT become observably committed unless its governing canonical decision and resulting canonical effect are durably consistent.

This does not prescribe a transaction implementation.

It prescribes an acceptance property.

Conceptually:

```text
decision + canonical effect
    = one governed committed transition
```

or neither becomes canonical.

### Classification

```text
REQUIREMENT GAP
not WHAT conflict
```

---

# 8. RC-B4-REQ-04 — Survivor requirements

`REQ-B4-070 → 077` correctly encode the frozen precedence:

```text
existing governing survivor
    ↓
established canonical Asset
    ↓
governed override only
    ↓
HOLD if unresolved
```

Implementation convenience and domain resolver authority are explicitly excluded.

### Result

```text
RC-B4-REQ-04 = PASS
```

---

# 9. RC-B4-REQ-05 — Domain/CPL identity authority

`REQ-B4-182 → 192` accurately preserve the frozen boundary:

```text
CPL may request
CPL may consume
CPL may persist
CPL may assess admissibility

but

CPL does not become domain identity authority
```

The earlier ambiguous `assess_asset_identity` formulation has not leaked into the requirement matrix.

### Result

```text
RC-B4-REQ-05 = PASS
```

---

# 10. RC-B4-REQ-06 — Merge/correction completeness

The matrix covers:

```text
positive resolution prerequisite
separate admission
HOLD
ambiguity/contradiction prohibition
domain resolver prohibition
historical survivor preservation
correction by supersession
restoration of independent canonical Assets
```

This is strong.

However, correction also interacts with dependency disposition and historical navigation. Those are covered in other families.

No missing merge ontology is detected.

### Result

```text
RC-B4-REQ-06 = PASS
```

---

# 11. RC-B4-REQ-07 — Dependency disposition testability

`REQ-B4-078 → 086` define disposition categories and prohibit silent historical rewriting.

But one material issue remains.

The matrix says merge admission must evaluate dependency disposition “sufficiently,” yet does not define a closure condition for execution.

A developer could interpret this as:

```text
some dependencies unresolved
but merge still executed
because core dependencies were checked
```

That is too loose.

---

# 12. Required repair RM-B4-02 — Dependency disposition closure

Add:

> Before canonical Asset merge execution, every dependency family that can materially affect canonical safety MUST have an explicit governed disposition, or the merge MUST remain HOLD / be rejected.

This preserves the generic disposition model without requiring every dependency family to be implemented identically.

Conceptually:

```text
all material dependencies
    ↓
disposition known?
   YES → merge may proceed
   NO  → HOLD / REJECT
```

### Result

```text
RC-B4-REQ-07 = PASS WITH REQUIRED REPAIR
```

---

# 13. RC-B4-REQ-08 — ExternalReference and DomainProjection

Requirements adequately preserve:

```text
historical target
current canonical navigation
external-system rebinding distinction
domain authority over projection truth
generic CPL non-adjudication
```

No major omission is found.

### Result

```text
RC-B4-REQ-08 = PASS
```

---

# 14. RC-B4-REQ-09 — Relationship identity independence

`REQ-B4-104 → 110` clearly establish:

```text
stable relationship identity
independent of current Contact
independent of current Asset
independent of endpoint canonical evolution
```

This is implementation-testable.

### Result

```text
RC-B4-REQ-09 = PASS
```

---

# 15. RC-B4-REQ-10 — CanonicalRelationshipDecision completeness

`REQ-B4-120 → 132` provide strong coverage:

```text
decision identity
relationship identity
type/context
evidence
authority
decision time
valid-time effect
supersession
ESTABLISH / END / CORRECT / SUPERSEDE
```

No semantic gap except the decision/effect consistency already identified in RM-B4-01.

### Result

```text
RC-B4-REQ-10 = PASS WITH CROSS-REPAIR RM-B4-01
```

---

# 16. RC-B4-REQ-11 — Valid-time / decision-time verification

The matrix correctly requires semantic distinction without prescribing bitemporal storage.

`REQ-B4-133 → 141` allow tests such as:

```text
decision made at T3
validity beginning T1

later correction at T5
validity revised to T2

D1 still reconstructable
D2 becomes current interpretation
```

This is sufficient.

### Result

```text
RC-B4-REQ-11 = PASS
```

---

# 17. RC-B4-REQ-12 — Idempotency specification

Relationship idempotency is correctly tied to governed operation identity.

Asset creation is also tied to governed request identity.

However, there is an asymmetry.

The matrix does not explicitly require idempotency behavior for **canonical decisions** themselves.

A replay of the same merge/correction decision request could potentially produce duplicate decision records or duplicate transitions.

This is not necessarily a WHAT defect, but it is a requirement-level gap.

---

# 18. Required repair RM-B4-03 — Canonical mutation idempotency

Add:

> Replaying the same governed canonical mutation request within its idempotency scope MUST NOT create a second independent canonical transition.

Apply to at least:

```text
Asset merge
Asset correction
Relationship establish
Relationship end
Relationship correction
Relationship supersession
```

The exact idempotency-key representation remains HOW.

### Result

```text
RC-B4-REQ-12 = PASS WITH REQUIRED REPAIR
```

---

# 19. RC-B4-REQ-13 — Cardinality and conflict

The matrix correctly avoids freezing universal rules and requires:

```text
type/domain governed cardinality
type/domain governed compatibility
explicit contradiction where rules establish conflict
no generic confidence/recency heuristic
```

This preserves authority correctly.

### Result

```text
RC-B4-REQ-13 = PASS
```

---

# 20. RC-B4-REQ-14 — Technical failure versus governed non-resolution

The separation is explicit and testable.

Examples prohibited by requirements:

```text
DB timeout → UNRESOLVED
resolver crash → AMBIGUOUS
network failure → NOT_FOUND
```

A legitimate AMBIGUOUS result remains distinct from a failed resolver execution.

### Result

```text
RC-B4-REQ-14 = PASS
```

---

# 21. RC-B4-REQ-15 — Provenance/history acceptance testability

The provenance family is broadly correct.

But there is one under-specification: requirements demand historical reconstructability while not clearly requiring that **current canonical navigation and historical target queries expose different semantics when appropriate**.

Without this, implementation could preserve internal provenance yet expose only rewritten/current endpoints everywhere.

That would satisfy storage-level preservation but violate product semantics.

---

# 22. Required repair RM-B4-04 — Historical/current query distinction

Add:

> Where current canonical navigation differs from historical attribution, the system MUST expose or make verifiable both interpretations according to the applicable operation/query context.

At minimum, acceptance evidence must be able to show:

```text
historical target = B
current canonical target = A
```

for merged Assets/Contacts without rewriting the historical fact.

This applies to:

```text
ContactAssetRelationship
ExternalReference
Cases where B4 navigation applies
historical Asset references
```

### Result

```text
RC-B4-REQ-15 = PASS WITH REQUIRED REPAIR
```

---

# 23. RC-B4-REQ-16 — B3 compatibility

`REQ-B4-193 → 199` properly cover:

```text
Contact merge
Contact correction
historical endpoint preservation
current canonical Contact navigation
double Contact/Asset evolution
```

No B3 WHAT conflict is found.

### Result

```text
RC-B4-REQ-16 = PASS
```

---

# 24. RC-B4-REQ-17 — B1/B2/B3 non-regression

The matrix explicitly requires preservation of:

```text
B1
B2
B3
/health
/ready
PostgreSQL persistence
transaction/session semantics
migrations 001–021
existing tests
```

This is strong.

One caution: “existing tests MUST NOT be weakened” is necessary but not sufficient; behavior itself must remain conformant even if tests are incomplete.

That is already implicit in REQ-B4-200 → 202.

### Result

```text
RC-B4-REQ-17 = PASS
```

---

# 25. RC-B4-REQ-18 — Can implementation acceptance be determined?

Not yet fully.

Most B4 behavior is testable, but the four gaps identified above would leave acceptance ambiguity around:

```text
decision/effect consistency
dependency-disposition closure
canonical-transition replay
historical/current navigation distinction
```

Therefore the matrix is close but not yet freeze-ready.

### Result

```text
RC-B4-REQ-18 = FAIL — BOUNDED REPAIR REQUIRED
```

---

# 26. Additional challenge — Requirement atomicity

Most requirements are atomic.

A few combine multiple obligations but remain acceptably testable.

No need to renumber or split the existing 240 requirements merely for stylistic purity.

The repair should preserve:

```text
REQ-B4-001 → REQ-B4-240
```

and add new requirements starting at:

```text
REQ-B4-241
```

This preserves traceability.

---

# 27. Additional challenge — Requirement conflicts

No direct contradiction is found between:

```text
historical preservation
current navigation
correction
idempotency
authority boundaries
```

The four repairs can be added without altering existing requirements.

### Result

```text
INTERNAL REQUIREMENT CONSISTENCY = PASS
```

---

# 28. Additional challenge — HOW leakage through “real PostgreSQL”

`REQ-B4-240` requires full acceptance against real PostgreSQL.

This is not improper HOW leakage because PostgreSQL is already an accepted CPL substrate from earlier phases and B4 must preserve it.

### Result

```text
PASS
```

---

# 29. Additional challenge — Migration numbering

`REQ-B4-208` says B4 schema evolution must be forward-only after migration `021`.

This is appropriate given canonical B3 baseline.

It does not prescribe how many B4 migrations must exist.

### Result

```text
PASS
```

---

# 30. Additional challenge — Relationship decision types

The four decision types:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

are frozen semantics, not an implementation enum mandate.

The matrix preserves this correctly.

### Result

```text
PASS
```

---

# 31. Additional challenge — Asset decision types

The matrix requires merge and correction semantics but does not force an enum such as:

```text
MERGE
CORRECTION
```

into one storage structure.

This correctly preserves implementation freedom.

### Result

```text
PASS
```

---

# 32. Repair RM-B4-01 — Decision/effect consistency

Add:

### REQ-B4-241

A canonical Asset identity mutation MUST NOT become observably committed unless its governing CanonicalAssetIdentityDecision and resulting canonical effect are durably consistent.

### REQ-B4-242

A CanonicalAssetIdentityDecision MUST NOT be accepted as successfully committed if the canonical Asset mutation it governs failed to become canonical.

### REQ-B4-243

A canonical relationship mutation MUST NOT become observably committed unless its governing CanonicalRelationshipDecision and resulting canonical effect are durably consistent.

### REQ-B4-244

A CanonicalRelationshipDecision MUST NOT be accepted as successfully committed if the canonical relationship mutation it governs failed to become canonical.

### REQ-B4-245

Failure during a governed canonical transition MUST leave the system in a state where no partial canonical transition is exposed as successfully committed.

---

# 33. Repair RM-B4-02 — Dependency disposition closure

Add:

### REQ-B4-246

Before canonical Asset merge execution, every dependency family materially capable of affecting canonical safety MUST have an explicit governed disposition.

### REQ-B4-247

If any material dependency family lacks a safe governed disposition, Asset merge MUST remain HOLD or be rejected.

### REQ-B4-248

Merge execution MUST NOT silently apply an implicit default disposition to an unresolved material dependency family.

### REQ-B4-249

The implementation MUST preserve evidence identifying the disposition applied to each material dependency family involved in a canonical merge where such disposition affects canonical outcome.

---

# 34. Repair RM-B4-03 — Canonical transition idempotency

Add:

### REQ-B4-250

Replaying the same governed Asset merge request within its idempotency scope MUST NOT create a second independent canonical merge transition.

### REQ-B4-251

Replaying the same governed Asset correction request within its idempotency scope MUST NOT create a second independent canonical correction transition.

### REQ-B4-252

Replaying the same governed relationship canonical mutation request within its idempotency scope MUST NOT create a second independent canonical relationship transition.

### REQ-B4-253

Canonical mutation idempotency MUST preserve the original committed canonical decision identity or semantically equivalent transition identity for replay-equivalent requests.

### REQ-B4-254

Similarity of mutation payload alone MUST NOT establish canonical-transition idempotency identity.

---

# 35. Repair RM-B4-04 — Historical/current navigation

Add:

### REQ-B4-255

Where an Asset canonical successor differs from an historical Asset target, the system MUST preserve a verifiable distinction between historical attribution and current canonical navigation.

### REQ-B4-256

Where a Contact canonical successor differs from an historical relationship Contact endpoint, the system MUST preserve a verifiable distinction between historical attribution and current canonical navigation.

### REQ-B4-257

Current canonical relationship queries MAY resolve current Contact and Asset successors without rewriting historical relationship endpoints.

### REQ-B4-258

Historical relationship inspection MUST be capable of exposing the Contact and Asset identities originally associated with the relationship.

### REQ-B4-259

Historical ExternalReference inspection MUST be capable of exposing the CPL target originally referenced by the external system even where current navigation resolves through another canonical Asset.

### REQ-B4-260

Acceptance evidence MUST demonstrate at least one case in which historical attribution and current canonical navigation differ and are both correctly reconstructable.

---

# 36. Requirement count after authorized repair

The repaired matrix will contain:

```text
REQ-B4-001 → REQ-B4-260
```

**260 requirements.**

Existing requirement IDs MUST remain unchanged.

No renumbering of `001 → 240` is authorized.

---

# 37. WHAT conflict check

Do any of RM-B4-01 → RM-B4-04 change frozen B4 WHAT?

No.

They operationalize already-frozen semantics:

```text
canonical decision durability
dependency disposition
idempotent governed transitions
historical/current distinction
```

Therefore:

```text
WHAT_CONFLICT = NO
```

---

# 38. Challenge scoreboard

```text
RC-B4-REQ-01   PASS
RC-B4-REQ-02   PASS
RC-B4-REQ-03   FAIL — bounded repair
RC-B4-REQ-04   PASS
RC-B4-REQ-05   PASS
RC-B4-REQ-06   PASS
RC-B4-REQ-07   PASS WITH REPAIR
RC-B4-REQ-08   PASS
RC-B4-REQ-09   PASS
RC-B4-REQ-10   PASS WITH CROSS-REPAIR
RC-B4-REQ-11   PASS
RC-B4-REQ-12   PASS WITH REPAIR
RC-B4-REQ-13   PASS
RC-B4-REQ-14   PASS
RC-B4-REQ-15   PASS WITH REPAIR
RC-B4-REQ-16   PASS
RC-B4-REQ-17   PASS
RC-B4-REQ-18   FAIL — bounded repair
```

---

# 39. Challenge verdict

The matrix is **not rejected**.

Its architecture and traceability are sound.

The frozen WHAT remains intact.

But four requirement-level gaps prevent acceptance.

```text
B4_REQUIREMENT_CHALLENGE_v0

CORE REQUIREMENT MODEL:
  PASS

TRACEABILITY:
  PASS

WHAT CONFORMANCE:
  PASS

WHAT_CONFLICT:
  NO

OVERALL:
  REPAIR_REQUIRED
```

---

# 40. Authorized repair boundary

Only the following repairs are authorized:

```text
RM-B4-01
Decision/effect consistency

RM-B4-02
Dependency-disposition closure

RM-B4-03
Canonical-transition idempotency

RM-B4-04
Historical/current navigation distinction
```

Add:

```text
REQ-B4-241 → REQ-B4-260
```

Do not alter the meaning or numbering of:

```text
REQ-B4-001 → REQ-B4-240
```

except if the re-challenge finds a direct contradiction.

---

# 41. Next artifact

The next artifact is:

```text
B4_REQUIREMENT_MATRIX_v0.1.md
```

with:

```text
260 requirements
RM-B4-01 → RM-B4-04 incorporated
```

Then:

```text
B4_REQUIREMENT_MATRIX_RE_CHALLENGE_v0.1.md
```

must verify the repairs and non-regression.

---

# 42. Re-challenge targets

At minimum:

```text
RC-B4-RM-01
Can canonical state and canonical decision diverge on partial failure?

RC-B4-RM-02
Can merge execute with an unresolved material dependency family?

RC-B4-RM-03
Can replay create duplicate canonical transitions?

RC-B4-RM-04
Can historical attribution be lost behind current canonical navigation?

RC-B4-RM-05
Did new requirements introduce HOW constraints?

RC-B4-RM-06
Did new requirements conflict with frozen WHAT?

RC-B4-RM-07
Are all 260 requirements now acceptance-testable?

RC-B4-RM-08
Can an Execution Mandate be written without inventing normative semantics?
```

---

# 43. Governance status

```text
B4 WHAT
  = FROZEN

B4 Requirement Matrix v0
  = PRODUCED
  = CHALLENGED
  = REPAIR_REQUIRED

B4 Requirement Matrix v0.1
  = AUTHORIZED FOR PRODUCTION

B4 Requirement Matrix
  = NOT YET FROZEN

B4 Execution Mandate
  = NOT AUTHORIZED

B4 Implementation
  = NOT AUTHORIZED
```

---

# 44. Final result

```text
CPL B4 REQUIREMENT CHALLENGE v0
===============================

Frozen WHAT:
  INTACT

Initial requirements:
  240

Requirement architecture:
  PASS

Traceability:
  PASS

WHAT conflict:
  NONE

Bounded defects:
  4

Authorized repairs:
  RM-B4-01 → RM-B4-04

Additional requirements:
  REQ-B4-241 → REQ-B4-260

Repaired total:
  260

RESULT:
  REPAIR_REQUIRED

NEXT:
  B4_REQUIREMENT_MATRIX_v0.1
```

**END — CPL B4 Requirement Challenge v0**

# CPL — B3 Requirement Challenge v0

**System:** Common Product Layer — CPL
**Phase:** B3 — Identity + Accounts
**Artifact challenged:** `B3_REQUIREMENT_MATRIX_v0.md`
**Canonical commit:** `1eebe57`
**Upstream authority:** B3 WHAT frozen at `6002ec8`
**Challenge status:** GOVERNANCE REVIEW
**Implementation authorization:** NONE

---

## 1. Challenge objective

The challenge asks one question:

> Is the Requirement Matrix sufficiently complete, determinate, testable and bounded that an Execution Mandate can later authorize implementation without requiring developers to invent B3 semantics?

This is not another WHAT challenge.

The following remain frozen:

```text
14 primitives
20 RMO obligation families
identity object boundaries
authority model
resolution semantics
merge semantics
service boundary
B1/B2 preservation obligations
```

The challenge may therefore:

```text
CLARIFY
CLOSE
STRENGTHEN
MAKE TESTABLE
REMOVE AMBIGUITY
```

but MUST NOT:

```text
ADD PRODUCT SCOPE
ADD PRIMITIVES
CHANGE OBJECT AUTHORITY
CHANGE MERGE PHILOSOPHY
MOVE AUTHORITY BETWEEN SYSTEMS
SELECT IMPLEMENTATION TECHNOLOGY
```

---

# 2. Challenge result — executive finding

The matrix is structurally strong but cannot yet be frozen.

The principal reason is exactly what the matrix itself identified: `RM-O01 → RM-O04` still leave decisions that would otherwise fall to implementation.

Challenge result:

```text
100 requirements reviewed structurally

WHAT contradiction:
  NONE FOUND

Primitive expansion:
  NONE FOUND

Material HOW leakage:
  NONE REQUIRING WHAT REOPENING

Unverifiable requirement:
  REPAIRABLE

Unresolved semantic obligations:
  4

RESULT:
  REPAIR_REQUIRED
```

This is a bounded repair.

No B3 WHAT reopening is required.

---

# 3. RM-O01 — Related-object reconciliation

## Challenge question

When:

```text
Contact A
   ↓ merge
Contact B
```

what happens to relationships currently attached to A?

The matrix currently permits:

```text
PRESERVE
REASSOCIATE
REJECT_CONFLICT
DEFER
```

but does not close the classification per relationship family.

That is insufficient for implementation.

A developer must not decide this.

---

# 4. RM-O01 closure principle

The critical distinction is:

> Does the relationship describe identity, historical fact, participation, or an external reference?

Merge does not mean:

```text
A never existed
```

It means:

```text
A remains historically interpretable
```

but

```text
B becomes the surviving current Contact identity
```

Therefore reconciliation must preserve both:

```text
CURRENT SEMANTIC USABILITY
+
HISTORICAL TRUTH
```

This yields different treatment by relationship family.

---

# 5. Accounts

An Account represents an external authentication/provider identity bound to a Contact.

After:

```text
A → B
```

an Account formerly belonging to A cannot continue to identify A as the current authenticated Contact.

Therefore the default classification is:

```text
Accounts
    ↓
REASSOCIATE
```

but only if reassociation preserves provider-binding uniqueness.

If B already owns an incompatible Account with the same:

```text
provider
+
provider_subject
```

the operation cannot blindly reassociate.

Therefore:

```text
NO CONFLICT
    → REASSOCIATE

EQUIVALENT EXISTING BINDING
    → PRESERVE / NO_CHANGE semantics

INCOMPATIBLE BINDING
    → REJECT_CONFLICT
```

The original association must remain historically recoverable.

## Closure

```text
Accounts:

PRIMARY:
  REASSOCIATE

CONDITIONAL:
  PRESERVE historical provenance
  REJECT_CONFLICT on incompatible binding

DEFER:
  forbidden when Account reconciliation
  is necessary for current identity correctness
```

**RM-O01/Accounts = CLOSED**

---

# 6. ContactPoints

ContactPoints are more delicate because two Contacts may contain:

```text
same email
same phone
different email
different phone
different verification states
different primary states
```

Blind reassociation could violate uniqueness or falsely transfer authority.

Default:

```text
ContactPoints
    ↓
REASSOCIATE
```

subject to preservation of:

```text
verification state
historical provenance
validity state
```

However, primary status requires recomputation under existing uniqueness constraints.

Therefore:

```text
compatible point
    → REASSOCIATE

equivalent existing point
    → PRESERVE historical evidence
      + avoid duplicate current relationship

primary conflict
    → do NOT blindly preserve both primary states

incompatible identity conflict
    → REJECT_CONFLICT

non-authoritative unresolved reconciliation
    → DEFER may be permitted
```

Crucially:

> Reassociation does not constitute new verification.

## Closure

```text
ContactPoints:

PRIMARY:
  REASSOCIATE

CONDITIONAL:
  PRESERVE history
  REJECT_CONFLICT where identity safety requires
  DEFER only where current identity correctness
  is not compromised
```

**RM-O01/ContactPoints = CLOSED**

---

# 7. ContactAssetRelationships

This relationship describes a historical/domain relationship between a Contact and an Asset.

Merge must not rewrite history to pretend B was always the original participant.

Therefore automatic reassignment is inappropriate as the universal rule.

Default:

```text
PRESERVE
```

The historical relationship remains attached to its historical Contact A.

Where downstream semantics require a current surviving Contact relationship, a separate current association MAY be created/reassociated according to existing CPL constraints.

Therefore:

```text
historical relationship
    → PRESERVE

current relationship needed
    → REASSOCIATE or establish equivalent
       only where admissible

duplicate/conflicting active relationship
    → REJECT_CONFLICT

non-critical unresolved relationship
    → DEFER
```

## Closure

```text
ContactAssetRelationships:

PRIMARY:
  PRESERVE

CONDITIONAL:
  REASSOCIATE current semantics where required
  REJECT_CONFLICT
  DEFER where safe
```

**RM-O01/ContactAssetRelationships = CLOSED**

---

# 8. CaseParticipants

Case participation is a historical fact:

```text
Contact A participated in Case X
```

A later identity merge must not falsify that history.

Therefore:

```text
CaseParticipants
    ↓
PRESERVE
```

The surviving Contact may be resolved through the merge chain for current operations, but the historical participant record should remain interpretable.

Where an active Case requires current participant resolution:

```text
current operational projection
    → may resolve/reassociate to B
```

without rewriting historical participation.

## Closure

```text
CaseParticipants:

PRIMARY:
  PRESERVE

CURRENT OPERATIONAL RESOLUTION:
  may resolve through surviving Contact

REJECT_CONFLICT:
  where an active-case invariant would be violated

DEFER:
  permitted for non-critical reconciliation
```

**RM-O01/CaseParticipants = CLOSED**

---

# 9. ExternalReferences

ExternalReference is evidence of an external association/reference.

Its provenance matters.

Changing:

```text
external reference → A
```

into:

```text
external reference → B
```

without retaining the original association could destroy evidence.

Therefore:

```text
ExternalReferences
    ↓
PRESERVE
```

Current resolution may follow:

```text
ExternalReference
      ↓
historical Contact A
      ↓ merged_into
current Contact B
```

Where an external system explicitly supports rebinding, that is a separate governed operation and must not be silently inferred from Contact merge.

## Closure

```text
ExternalReferences:

PRIMARY:
  PRESERVE

REASSOCIATE:
  only with independently admissible authority/evidence

REJECT_CONFLICT:
  where external identity contradicts reassociation

DEFER:
  permitted
```

**RM-O01/ExternalReferences = CLOSED**

---

# 10. RM-O01 final matrix

| Relationship | Default | Conditional |
|---|---|---|
| Accounts | REASSOCIATE | PRESERVE history / REJECT_CONFLICT |
| ContactPoints | REASSOCIATE | PRESERVE history / REJECT_CONFLICT / limited DEFER |
| ContactAssetRelationships | PRESERVE | REASSOCIATE current semantics / REJECT_CONFLICT / DEFER |
| CaseParticipants | PRESERVE | current resolution / REJECT_CONFLICT / DEFER |
| ExternalReferences | PRESERVE | authorized REASSOCIATE / REJECT_CONFLICT / DEFER |

This is sufficiently determinate to prevent developer invention while leaving implementation mechanism open.

**RM-O01 = CLOSED**

---

# 11. RM-O02 — Verification Assertion Minimum Contract

The current matrix correctly says that B3 does not perform OTP/OAuth/etc.

But `verify_contact_point` cannot consume an undefined blob called "verification assertion."

We need the semantic minimum.

An admissible Verification Assertion MUST provide sufficient information to establish:

```text
ASSERTION IDENTITY
TARGET
METHOD/CLASS
ISSUER/SOURCE
RESULT
TIME
AUTHORITY/ADMISSIBILITY
REPLAY IDENTITY
```

This does not require a particular JSON structure or provider.

---

# 12. Minimum assertion semantics

The assertion must make recoverable at least:

```text
assertion_id
contact_point_id
verification_class
issuer/source
verification_result
verified_at
authority/admissibility context
replay/idempotency identity
```

Where applicable:

```text
expires_at
external_reference
evidence_reference
```

The assertion MUST NOT require B3 to store:

```text
OTP secret
password
OAuth credential
raw authentication secret
```

---

# 13. Assertion acceptance rules

B3 MUST reject an assertion when:

```text
target mismatch
unsupported verification class
negative result
expired assertion where expiry applies
unauthorized issuer/context
invalid replay semantics
missing mandatory provenance
```

B3 MUST NOT reinterpret:

> "caller says verified"

as verification evidence.

The assertion describes the result of an external verification event, not the external mechanism itself.

Therefore:

**RM-O02 = CLOSED**

---

# 14. RM-O03 — Provenance Minimum Persistence Obligation

The matrix currently says provenance must be "recoverable."

That is insufficient because a developer could satisfy it with transient logs.

Material identity decisions must survive process restart.

The challenge therefore distinguishes:

```text
DURABLE PROVENANCE
vs
EXECUTION OBSERVABILITY
```

---

# 15. Durable provenance

For every identity-changing B3 operation, B3 MUST durably preserve enough information to reconstruct:

```text
WHAT happened
TO WHAT
WHY
UNDER WHOSE AUTHORITY
USING WHAT MATERIAL EVIDENCE
WHEN
WITH WHAT RESULT
```

At minimum:

```text
operation identity
operation type
affected object IDs
actor/requester identity or actor reference
authority context/reference
material evidence/assertion references
decision/result
timestamp
```

For merge:

```text
source_contact_id
target_contact_id
proposal/authorization reference
reconciliation result
```

For ContactPoint verification:

```text
contact_point_id
verification assertion reference
accepted verification class
verification time
```

---

# 16. What need not be durably persisted

The requirement does not mandate persistence of:

```text
debug traces
stack traces
temporary calculations
raw provider payloads
LLM reasoning
internal execution chatter
secrets
```

unless independently required by another system/policy.

Nor does the Requirement Matrix choose:

```text
table
event store
audit table
JSONB
external provenance service
```

That belongs downstream.

The obligation is:

> Durably recoverable semantics, not a prescribed storage implementation.

Therefore:

**RM-O03 = CLOSED**

---

# 17. RM-O04 — Same Logical Contact Creation

This is the most subtle closure after merge.

We must avoid defining general human identity equivalence here.

Otherwise B3 would accidentally become a universal identity matching system.

The question is narrower:

> When are two creation requests considered the same logical creation for idempotency/concurrency purposes?

They are the same logical creation when they carry the same governed creation identity, not merely similar personal information.

---

# 18. Creation identity rule

The strongest admissible signal is an explicit:

```text
idempotency key
/
request identity
/
upstream operation identity
```

within the same applicable authority/scope.

Therefore:

```text
same creation operation identity
+ same authority/scope
→ same logical creation
```

B3 MUST NOT infer same logical creation merely because two requests contain:

```text
same name
similar name
same address
same date of birth
LLM similarity
fuzzy-match score
```

Those may contribute to identity resolution or duplicate assessment, but they do not independently define creation idempotency.

---

# 19. Strong external identity collision

A second case exists.

If two concurrent requests contain the same admissible externally unique identity already governed by B3, such as an identity binding whose uniqueness is independently established, the system must not knowingly create incompatible canonical results merely because idempotency keys differ.

This is not:

```text
same logical request
```

It is:

```text
identity conflict protection
```

and should therefore resolve through conflict/resolution semantics rather than silently creating duplicates.

---

# 20. RM-O04 closure

```text
SAME LOGICAL CREATION:

same governed creation/request identity
within same applicable scope
```

NOT sufficient by itself:

```text
same name
same email string
same phone string
same address
similarity score
LLM judgement
```

Independent identity conflicts remain governed by resolution/conflict rules.

Therefore:

**RM-O04 = CLOSED**

---

# 21. Challenge of the 100 requirements

With the four open items closed, the matrix can now be challenged globally.

**C01 — Primitive completeness**
14 / 14 covered
PASS

**C02 — RMO completeness**
20 / 20 covered
PASS

**C03 — Frozen WHAT consistency**

No requirement requires modification of frozen B3 WHAT.

PASS

**C04 — Hidden primitive detection**

No requirement creates an additional public semantic primitive.

PASS

**C05 — Authority preservation**

The distinction:

```text
ASSESS_DUPLICATE
PROPOSE_MERGE
AUTHORIZE_MERGE
EXECUTE_MERGE
```

remains intact.

PASS

**C06 — Resolution semantics**

The distinction between:

```text
MATCHED
NOT_FOUND
AMBIGUOUS
CONFLICTING
UNRESOLVED
PROVISIONAL
technical failure
```

remains intact.

PASS

**C07 — Merge semantics**

Directionality, historical preservation, authorization and reconciliation are now sufficiently constrained.

PASS

**C08 — Verification boundary**

External verification mechanism remains outside B3 while assertion consumption is sufficiently defined.

PASS

**C09 — Authentication boundary**

No authentication provider implementation enters B3.

PASS

**C10 — Authorization boundary**

B3 consumes authority semantics without becoming the authorization platform.

PASS

**C11 — Historical integrity**

Merge, Account lifecycle and ContactPoint lifecycle preserve historical interpretability.

PASS

**C12 — Idempotency**

The principal ambiguous creation case is now closed.

PASS

**C13 — Concurrency**

Requirements specify invariant outcomes without imposing locking architecture.

PASS

**C14 — Transactionality**

Atomicity obligations are observable and testable.

PASS

**C15 — Provenance**

Durability obligation is now explicit without choosing persistence architecture.

PASS

**C16 — Related-object reconciliation**

All five relationship families now possess default semantics and constrained exceptions.

PASS

**C17 — B2 non-regression**

Requirements explicitly preserve B2 persistence and acceptance behavior.

PASS

**C18 — B1 non-regression**

`/health` and `/ready` remain protected.

PASS

**C19 — HOW leakage**

No material requirement forces framework, DB technique, API transport, locking strategy or provenance storage implementation.

PASS

**C20 — Developer semantic discretion**

No material product-semantic decision identified by this challenge remains delegated to the developer.

PASS

---

# 22. Testability challenge

The 100 requirements are not all necessarily one-test-per-requirement.

That would be a mistake.

The correct relation is:

```text
Requirement
     ↓
one or more verification obligations

Verification scenario
     ↓
may satisfy several requirements
```

The existing verification families provide a credible downstream basis:

```text
Positive       18
Negative       26
Concurrency     4
Transaction     4
Traceability    5
```

plus B1/B2 regression.

Therefore:

**TESTABILITY = PASS**

---

# 23. DevOps determinability challenge

Question:

> Could an independent verifier eventually determine acceptance without relying on developer self-certification?

After the repairs above: yes.

Evidence can be mechanically or evidentially assessed for:

```text
repository lineage
candidate delta
installation
schema/migrations
positive behavior
negative behavior
transaction behavior
concurrency invariants
provenance durability
boundary preservation
B1/B2 non-regression
```

Therefore:

**DEVOPS_DETERMINABILITY = PASS**

---

# 24. Requirement Challenge scoreboard

```text
CH-01 Primitive coverage                 PASS
CH-02 RMO coverage                       PASS
CH-03 WHAT consistency                   PASS
CH-04 No hidden primitive                PASS
CH-05 Authority model                    PASS
CH-06 Resolution semantics               PASS
CH-07 Merge semantics                    PASS
CH-08 Verification boundary              PASS
CH-09 Authentication boundary            PASS
CH-10 Authorization boundary             PASS
CH-11 Historical integrity               PASS
CH-12 Idempotency                        PASS
CH-13 Concurrency                        PASS
CH-14 Transactionality                   PASS
CH-15 Provenance                         PASS
CH-16 Related-object reconciliation      PASS
CH-17 B2 non-regression                  PASS
CH-18 B1 non-regression                  PASS
CH-19 HOW leakage                        PASS
CH-20 Developer semantic discretion      PASS
CH-21 Testability                        PASS
CH-22 DevOps determinability             PASS

TOTAL:
22 / 22 PASS
```

But there is an important governance distinction.

The challenge itself has established the repairs necessary to close `RM-O01 → RM-O04`.

Those repairs are not yet present in `B3_REQUIREMENT_MATRIX_v0.md`.

Therefore we must not declare the existing v0 frozen.

---

# 25. Challenge verdict

```text
B3_REQUIREMENT_MATRIX_v0

CHALLENGE:
  22 / 22 PASS
  conditional upon incorporation
  of RM-O01 → RM-O04 closures

EXISTING v0:
  NOT ACCEPTED AS-IS

VERDICT:
  REPAIR_REQUIRED

REPAIR SCOPE:
  BOUNDED

WHAT REOPENING:
  NO

NEW PRIMITIVE:
  NO

ARCHITECTURAL DECISION:
  NO
```

---

# 26. Authorized repair

Produce:

```text
B3_REQUIREMENT_MATRIX_v0.1.md
```

The repair MUST incorporate the four closures from this challenge:

```text
RM-O01
  exact related-object reconciliation semantics

RM-O02
  Verification Assertion Minimum Contract

RM-O03
  Durable Provenance Minimum Obligation

RM-O04
  Same Logical Contact Creation rule
```

The four items should cease to appear as open issues.

The repaired matrix should retain the existing `REQ-B3-001 → REQ-B3-100` identities wherever possible.

If additional normative requirements are required to encode the closures explicitly, they should continue from:

```text
REQ-B3-101
```

rather than renumbering the existing requirements.

This preserves traceability.

---

# 27. What is NOT authorized

The Requirement Challenge does not authorize:

```text
Python implementation
FastAPI endpoints
new migrations
schema changes
service classes
repositories
locking strategy
API design
RBAC implementation
verification provider
merge engine
B3 tests
```

Those remain downstream of Requirement Freeze and Execution Mandate.

---

# 28. Governance state after challenge

```text
B3 WHAT
  FROZEN

B3 Requirement Matrix v0
  CHALLENGED
  REPAIR_REQUIRED

Repair authority
  GRANTED
  LIMITED TO RM-O01 → RM-O04 CLOSURE

B3 Requirement Matrix v0.1
  AUTHORIZED FOR PRODUCTION

Requirement Re-Challenge
  REQUIRED

Requirement Freeze
  NOT YET AUTHORIZED

Execution Mandate
  NOT ISSUED

B3 Implementation
  NOT AUTHORIZED
```

---

# 29. Canonical next sequence

```text
main @ 1eebe57
      │
      ▼
B3_REQUIREMENT_CHALLENGE_v0
      │
      │ REPAIR_REQUIRED
      ▼
B3_REQUIREMENT_MATRIX_v0.1
      │
      ▼
RE-CHALLENGE
      │
      ├── FAIL → bounded repair
      │
      └── PASS
            ↓
B3 REQUIREMENT MATRIX FREEZE
            ↓
B3 EXECUTION MANDATE
════════════════════════════════
         BUILD BOUNDARY
════════════════════════════════
            ↓
B3 IMPLEMENTATION
```

## Final result

REPAIR_REQUIRED, mais c'est un résultat très propre : le challenge n'a découvert aucune faiblesse nécessitant de rouvrir le WHAT. Il a transformé les quatre zones encore ouvertes en décisions normatives explicites.

**End of `CPL — B3 Requirement Challenge v0`**

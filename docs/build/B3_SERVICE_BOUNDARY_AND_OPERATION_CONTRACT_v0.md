# CPL — B3 Service Boundary & Operation Contract v0

**System:** Common Product Layer — CPL
**Build Phase:** B3 — Identity + Accounts
**Artifact:** Service Boundary & Operation Contract
**Version:** v0
**Canonical predecessors:**

* `B3_IDENTITY_OBJECT_AUTHORITY_MAP_v0.md`
* `B3_IDENTITY_RESOLUTION_STATE_DECISION_MODEL_v0.md`

**Canonical repository baseline:** `main @ e35d4d9`

---

## 1. Purpose

This artifact defines the **externally consumable functional boundary of CPL B3**.

The preceding artifacts established:

```text
Identity Object & Authority Map
→ what identity objects mean
→ where authority resides

Identity Resolution State & Decision Model
→ what CPL may conclude
→ which identity transitions may follow
```

This artifact establishes:

> **What may a caller ask B3 to do, what must it provide, what may B3 return, and under which authority and invariants may state change occur?**

It defines semantic operation contracts.

It does **not** prescribe REST endpoints, Python classes, framework architecture, transport protocol or UI.

---

# 2. B3 Service Boundary

B3 exposes governed identity operations over the persistence foundation established by B2.

Conceptually:

```text
                 CALLER
                    │
                    ▼
        ┌───────────────────────┐
        │    B3 SERVICE         │
        │       BOUNDARY        │
        ├───────────────────────┤
        │ Contact Resolution    │
        │ Contact Lifecycle     │
        │ ContactPoint          │
        │ Account Binding       │
        │ Reconciliation        │
        └───────────┬───────────┘
                    │
                    ▼
             B2 Persistence
```

Callers SHALL NOT need direct knowledge of the persistence mechanics in order to perform governed B3 operations.

---

# 3. B3 Operation Families

B3 operations are divided into five families:

```text
B3-O1  Contact Resolution
B3-O2  Contact Lifecycle
B3-O3  ContactPoint Lifecycle
B3-O4  Account Binding
B3-O5  Identity Reconciliation
```

This classification is semantic, not necessarily an implementation module structure.

---

# 4. Common Request Envelope

Every identity operation that can materially affect identity state SHOULD conceptually receive:

```text
OperationRequest
├── operation
├── caller_context
├── authority_context
├── request_id / idempotency context
├── evidence
├── target identifiers
├── applicable policy context
└── provenance
```

Not every field must become an API parameter.

The contract requires that B3 possess sufficient context to determine whether the requested operation is admissible.

---

# 5. Common Response Envelope

B3 operations SHOULD conceptually return:

```text
OperationResult
├── outcome
├── affected / resolved object
├── resolution_state where applicable
├── decision
├── mutation_performed
├── evidence/provenance reference
├── conflict / ambiguity information
└── failure or rejection reason
```

The caller must be able to distinguish:

```text
successful resolution
successful mutation
legitimate non-resolution
governance rejection
invalid request
execution failure
```

These outcomes SHALL NOT be collapsed into one generic failure state.

---

# 6. Operation Outcome Classes

Canonical semantic outcome classes:

```text
SUCCESS
NO_MATCH
AMBIGUOUS
CONFLICTING
UNRESOLVED
REJECTED
INVALID
NOT_FOUND
ALREADY_EXISTS
NO_CHANGE
EXECUTION_FAILURE
```

The downstream implementation may represent these using typed results, exceptions, status codes or other mechanisms.

Their semantic distinctions must survive.

---

# 7. B3-O1 — Contact Resolution

## 7.1 `find_contact`

### Purpose

Retrieve an existing Contact from a sufficiently authoritative CPL identifier.

### Typical input

```text
contact_id
```

### Possible outcomes

```text
SUCCESS → Contact
NOT_FOUND
INVALID
EXECUTION_FAILURE
```

### Invariant

`find_contact` performs retrieval.

It SHALL NOT:

```text
create Contact
merge Contact
attach Account
attach ContactPoint
modify identity state
```

---

# 8. `resolve_contact`

### Purpose

Resolve observed identity evidence against existing CPL Contacts.

### Input

Conceptually:

```text
ResolveContactRequest
├── evidence[]
├── caller_context
├── authority_context
└── policy_context
```

### Output

```text
MATCHED
NOT_FOUND
AMBIGUOUS
CONFLICTING
UNRESOLVED
```

plus relevant candidate/evidence information.

### Mutation rule

Default:

```text
resolve_contact
→ READ / ASSESS
→ NO IDENTITY MUTATION
```

Resolution and mutation remain separate.

### Prohibition

`resolve_contact` SHALL NOT silently convert `MATCHED` into an account/contact-point attachment.

---

# 9. `find_or_create_contact`

This operation may exist for caller convenience, but it is **not** primitive identity semantics.

Conceptually it composes:

```text
resolve_contact
      ↓
resolution decision
      ↓
authorized create_contact
```

### Required behavior

```text
MATCHED
→ return existing Contact

NOT_FOUND
+ creation authorized
→ create Contact

NOT_FOUND
+ creation not authorized
→ return NOT_FOUND / REJECTED

AMBIGUOUS
→ NO CREATE

CONFLICTING
→ NO CREATE

UNRESOLVED
→ NO CREATE by default
```

### Critical invariant

```text
find_or_create
≠
database lookup + unconditional INSERT
```

---

# 10. B3-O2 — Contact Lifecycle

## 10.1 `create_contact`

### Purpose

Create a persistent CPL Contact under authorized conditions.

### Required semantic input

```text
contact_type
creation evidence/context
caller authority
provenance
```

Additional attributes may be accepted where defined by B2.

### Preconditions

At minimum:

```text
caller has Contact creation authority
contact_type valid
required creation context present
no known blocking identity conflict
```

### Output

```text
CreatedContact
```

or:

```text
REJECTED
INVALID
CONFLICTING
ALREADY_EXISTS where determinable
EXECUTION_FAILURE
```

### Prohibition

Creation SHALL NOT implicitly establish:

```text
verified email
verified phone
authenticated Account
asset ownership
case participation
```

unless separate authorized operations establish those facts.

---

# 11. Provisional Contact Creation

B3 SHALL support the semantic possibility of provisional creation.

Conceptually:

```text
create_contact(
    identity_status = PROVISIONAL
)
```

The exact persistence representation is downstream.

The important invariant is:

> CPL may preserve an operational identity without falsely asserting that identity resolution is complete.

Promotion from provisional to established identity requires a governed transition.

---

# 12. `get_contact`

Where distinction from `find_contact` is useful:

```text
find_contact
→ resolution/search semantics

get_contact
→ retrieval by canonical Contact identity
```

The implementation may ultimately expose only one operation if semantics remain unambiguous.

This is therefore **OPTIONAL at the service-name level**, not a mandatory separate implementation.

---

# 13. B3-O3 — ContactPoint Lifecycle

## 13.1 `add_contact_point`

### Purpose

Associate a communication/identity evidence point with a Contact.

### Input

Conceptually:

```text
contact_id
contact_point_type
value
provenance
caller authority
```

### Preconditions

```text
Contact exists
Contact permits modification
ContactPoint type valid
caller authorized
applicable uniqueness constraints satisfied
```

### Output

```text
ContactPoint
```

initially in an appropriate verification state.

### Critical invariant

Adding a ContactPoint does not itself prove that the Contact controls it.

---

# 14. `verify_contact_point`

### Purpose

Record that a ContactPoint has satisfied an accepted verification mechanism.

### Input

```text
contact_point_id
verification evidence
verification mechanism/context
authority
```

### Preconditions

```text
ContactPoint exists
verification evidence admissible
verification transition allowed
```

### Result

Conceptually:

```text
UNVERIFIED / PENDING
        ↓
     VERIFIED
```

### Prohibition

The operation SHALL NOT manufacture verification merely because a caller declares the value correct.

Verification requires admissible verification evidence.

---

# 15. `invalidate_contact_point`

### Purpose

Indicate that a previously usable ContactPoint should no longer be treated as current/valid evidence.

Possible causes:

```text
revocation
failed re-verification
known reassignment
administrative invalidation
provider evidence
```

Historical existence SHALL remain preserved.

---

# 16. `set_primary_contact_point`

### Purpose

Select the preferred active ContactPoint of a given type where B2 permits one primary active point.

### Preconditions

```text
ContactPoint belongs to Contact
ContactPoint active
applicable verification requirement satisfied
caller authorized
```

### Invariant

Primary means:

```text
preferred current point
```

not:

```text
identity authority
```

---

# 17. B3-O4 — Account Binding

## 17.1 `attach_account`

### Purpose

Bind an external authentication/provider identity to a CPL Contact.

Conceptually:

```text
Provider Identity
      ↓
   Account
      ↓
   Contact
```

### Required input

```text
contact_id
provider
provider_subject / external provider identity
authority context
provenance
```

### Preconditions

```text
Contact exists
provider identity structurally valid
binding not prohibited by existing Account state
caller authorized
no conflicting existing binding
```

### Outcomes

```text
SUCCESS
ALREADY_EXISTS
CONFLICTING
REJECTED
INVALID
EXECUTION_FAILURE
```

### Critical invariant

An external provider identity SHALL NOT be bound to a different Contact merely because a new request asks for it.

Existing contradictory bindings produce conflict.

---

# 18. `resolve_authenticated_contact`

### Purpose

Resolve an already authenticated external identity into CPL identity.

Input:

```text
provider
provider_subject
authenticated identity evidence
caller context
```

Conceptual behavior:

```text
provider identity
      ↓
existing Account?
  ┌───────┴────────┐
 YES               NO
  │                 │
  ▼                 ▼
Contact       identity resolution
```

### Existing valid Account

If an admissible active Account binding exists:

```text
→ MATCHED Contact
```

subject to Contact/Account state validation.

### No Account

B3 may:

```text
resolve using additional evidence
return NOT_FOUND
return AMBIGUOUS
return CONFLICTING
return UNRESOLVED
```

It SHALL NOT automatically create and bind a Contact unless the calling operation explicitly possesses that authority and policy permits it.

---

# 19. `disable_account`

### Purpose

Make an Account unavailable for active use without destroying historical binding.

Conceptual transition:

```text
ACTIVE
  ↓
DISABLED
```

The precise B2 state vocabulary remains authoritative.

### Historical rule

Disabling an Account SHALL NOT erase:

```text
provider identity
historical Contact association
creation provenance
prior activity evidence
```

---

# 20. `revoke_account`

### Purpose

Represent a stronger termination of the Account's authority/validity.

Conceptually:

```text
ACTIVE / DISABLED
        ↓
     REVOKED
```

Revocation SHALL NOT normally be represented by physical deletion.

---

# 21. Account Rebinding

B3 SHALL NOT provide an unrestricted operation equivalent to:

```text
account.contact_id = another_contact
```

Changing the Contact behind an existing provider identity is an **identity reconciliation event**, not ordinary Account editing.

It belongs behind B3-O5 authority.

---

# 22. B3-O5 — Identity Reconciliation

## 22.1 `detect_duplicate_contact`

### Purpose

Assess whether multiple CPL Contacts may represent the same real-world actor.

### Result

```text
NO_DUPLICATE_INDICATION
POSSIBLE_DUPLICATE
STRONG_DUPLICATE_CANDIDATE
UNRESOLVED
```

These names are semantic, not necessarily final enum values.

### Mutation

None.

---

# 23. `propose_merge`

### Purpose

Create a governed merge proposal from identity reconciliation evidence.

Input conceptually includes:

```text
source_contact_id
target_contact_id
evidence
reason
proposer authority
provenance
```

Output:

```text
MergeCandidate
```

### Mutation rule

The Contacts SHALL NOT yet be merged.

---

# 24. `merge_contacts`

### Purpose

Execute an authorized identity merge.

This is the highest-risk B3 mutation.

### Preconditions

At minimum:

```text
source exists
target exists
source != target
source eligible for merge
target eligible to survive
merge evidence exists
merge decision authorized
no prohibited structural conflict
```

### Result

Conceptually:

```text
source.status = MERGED
source.merged_into_id = target.id
```

plus all required historical/reconciliation handling.

### Mandatory invariant

The source Contact remains historically addressable/interpretable.

---

# 25. Merge Direction

Merge is directional:

```text
SOURCE
  ↓
TARGET
```

Therefore:

```text
merge(A, B)
≠
merge(B, A)
```

The target is the surviving canonical Contact.

The choice of target requires explicit decision semantics.

---

# 26. Merge and Related Objects

A merge must define behavior for objects related to the source Contact, including at least:

```text
Accounts
ContactPoints
ContactAssetRelationships
CaseParticipants
ExternalReferences
```

However, B3 SHALL NOT blindly rewrite every historical foreign key from source to target.

For each relationship family the downstream Requirement Matrix must determine whether it is:

```text
retained historically
transferred
superseded
duplicated only by explicit rule
left pointing to historical source
```

This is a critical requirement for B3 implementation design.

---

# 27. Merge Idempotency

Replaying an already completed merge:

```text
A → B
```

must not create additional mutation or corruption.

The operation should produce a semantic equivalent of:

```text
NO_CHANGE / ALREADY_MERGED
```

when appropriate.

---

# 28. Forbidden Generic CRUD Boundary

B3 SHALL NOT expose identity semantics as unrestricted generic CRUD such as:

```text
update_contact(any_fields)
update_account(any_fields)
update_contact_point(any_fields)
delete_contact()
delete_account()
delete_contact_point()
```

because these operations erase the distinction between:

```text
business transition
identity decision
administrative mutation
historical preservation
```

B3 exposes **meaningful operations**, not arbitrary persistence mutation.

---

# 29. Physical Delete Rule

B3 SHOULD treat physical deletion of identity-bearing objects as outside ordinary service behavior.

Default:

```text
Contact → status transition
Account → disable/revoke
ContactPoint → invalidate/revoke
Merge → historical supersession
```

not:

```text
DELETE FROM ...
```

Any future hard-deletion capability requires separate policy, particularly for regulatory/data-retention purposes.

---

# 30. Authority Classes

The exact authorization system is outside B3, but B3 contracts require semantic authority distinctions.

At minimum:

```text
READ_IDENTITY
RESOLVE_IDENTITY
CREATE_CONTACT
MANAGE_CONTACT_POINT
VERIFY_CONTACT_POINT
ATTACH_ACCOUNT
MANAGE_ACCOUNT
PROPOSE_MERGE
AUTHORIZE_MERGE
EXECUTE_MERGE
```

A single caller may hold several authorities.

B3 SHALL NOT assume all callers possess all authorities.

---

# 31. Authority vs Authentication

B3 receives authority context.

It does not implement the system that authenticates or authorizes the caller.

Therefore:

```text
Auth system
    ↓
authenticated/authorized caller context
    ↓
B3
    ↓
enforces operation preconditions
```

B3 may reject a request because required authority is absent.

It does not issue login credentials.

---

# 32. Idempotency Boundary

Operations with material mutation SHOULD support governed replay protection.

Priority operations:

```text
create_contact
add_contact_point
verify_contact_point
attach_account
disable_account
revoke_account
merge_contacts
```

Idempotency SHALL mean:

> repeated execution of the same authorized logical operation does not create unintended additional identity state.

---

# 33. Transaction Boundary

A material identity operation SHALL either:

```text
complete its required state transition
```

or:

```text
leave no misleading partial identity transition
```

Particularly:

```text
attach_account
verify_contact_point
merge_contacts
```

must have explicit transactional integrity.

---

# 34. Concurrency Boundary

B3 must assume concurrent attempts may occur.

Examples:

```text
two callers create same provider Account

two callers select primary email

two resolution processes create Contact simultaneously

two merge decisions target same source
```

Database constraints from B2 remain part of the defense, but B3 operation semantics must correctly interpret resulting conflicts.

---

# 35. Constraint Failure Is Not Generic Error

If B2 rejects a mutation because an identity invariant is violated, B3 SHOULD translate that into the relevant semantic outcome.

Example:

```text
duplicate provider identity constraint
        ↓
CONFLICTING / ALREADY_EXISTS
```

rather than exposing only:

```text
database integrity error
```

The persistence layer protects the invariant.

The B3 boundary explains its meaning.

---

# 36. Provenance Requirement

Material B3 mutations must carry enough provenance to answer:

```text
who/what requested the operation?
what evidence supported it?
under what authority?
when?
what was changed?
```

The precise persistence mechanism is not fixed here.

---

# 37. Read Operations vs Decision Operations vs Mutation Operations

B3 SHALL preserve three semantic categories:

### Read

```text
find_contact
get_contact
```

### Decision / Resolution

```text
resolve_contact
resolve_authenticated_contact
detect_duplicate_contact
propose_merge
```

### Mutation

```text
create_contact
add_contact_point
verify_contact_point
invalidate_contact_point
set_primary_contact_point
attach_account
disable_account
revoke_account
merge_contacts
```

A decision operation SHALL NOT silently become a mutation operation.

---

# 38. Operation Composition

Higher-level convenience operations may compose primitives.

Example:

```text
register_authenticated_actor
```

could eventually compose:

```text
resolve_authenticated_contact
        ↓
if NOT_FOUND
        ↓
create_contact
        ↓
attach_account
```

But the composition must preserve every individual authority and decision boundary.

Convenience SHALL NOT bypass governance.

---

# 39. External Consumer Independence

Consumers such as:

```text
VIR
PGDR
future frontend
future authentication adapter
community systems
other runners
```

must consume B3 through its semantic boundary rather than redefining identity independently.

A downstream system SHALL NOT create its own competing meaning of CPL Contact identity.

---

# 40. B3 Does Not Own Asset Identity

B3 resolves **actors**.

It does not resolve:

```text
vehicle identity
machine identity
property identity
generic Asset identity
```

Those belong to the Asset side of CPL and later phases.

Therefore:

```text
Contact Resolution
≠
Asset Identity Resolution
```

even though the patterns may later share generic infrastructure.

---

# 41. B3 Does Not Own Case Identity

Likewise:

```text
Contact
≠
Case
```

B3 may eventually be called while establishing a Case participant, but Case creation and Case lifecycle remain outside B3.

---

# 42. Minimum B3 v1 Operations

For B3 v1, the minimum candidate operation set is:

```text
CONTACT

find_contact
resolve_contact
create_contact
find_or_create_contact

CONTACT POINT

add_contact_point
verify_contact_point
invalidate_contact_point
set_primary_contact_point

ACCOUNT

attach_account
resolve_authenticated_contact
disable_account
revoke_account

RECONCILIATION

detect_duplicate_contact
propose_merge
merge_contacts
```

Total:

```text
15 semantic operations
```

This is a candidate freeze set for the Requirement Matrix.

---

# 43. Operations Deferred from B3 v1

Unless later requirements prove them necessary, defer:

```text
bulk identity import
bulk merge
automatic probabilistic merge
cross-tenant identity federation
biometric identity
government identity verification
provider-specific OAuth implementation
password credentials
session management
RBAC
identity graph ML
LLM-authorized identity decisions
hard deletion
```

---

# 44. Core Service Invariants

### B3-SB-I01 — Semantic operations

B3 exposes governed identity operations, not unrestricted CRUD.

### B3-SB-I02 — Read does not mutate

Retrieval operations cannot silently alter identity state.

### B3-SB-I03 — Resolution does not implicitly mutate

A resolution conclusion and a state transition are separate.

### B3-SB-I04 — Authority accompanies mutation

Every material identity mutation requires applicable authority.

### B3-SB-I05 — Provider identity remains external

Account binding does not transfer CPL identity authority to an external provider.

### B3-SB-I06 — ContactPoint is evidence/channel

ContactPoint mutation does not redefine Contact identity.

### B3-SB-I07 — Merge is exceptional

Merge requires reconciliation evidence and separate authority.

### B3-SB-I08 — Merge preserves history

The source Contact is superseded, not erased.

### B3-SB-I09 — Constraints remain meaningful

Persistence constraint failures are translated into identity-domain outcomes where possible.

### B3-SB-I10 — Mutation is transactionally coherent

B3 does not expose misleading partial identity transitions.

### B3-SB-I11 — Replay does not multiply identity

Material operations require appropriate idempotency semantics.

### B3-SB-I12 — B3 resolves actors only

Asset and Case identity remain outside the B3 boundary.

---

# 45. Operation Contract Summary

| Operation                       | Reads | Decides |       Mutates |  Elevated authority |
| ------------------------------- | ----: | ------: | ------------: | ------------------: |
| `find_contact`                  |   Yes |      No |            No |                  No |
| `resolve_contact`               |   Yes |     Yes |            No |          Resolution |
| `create_contact`                |   Yes |     Yes |           Yes |            Creation |
| `find_or_create_contact`        |   Yes |     Yes |   Conditional |            Creation |
| `add_contact_point`             |   Yes |      No |           Yes |        ContactPoint |
| `verify_contact_point`          |   Yes |     Yes |           Yes |        Verification |
| `invalidate_contact_point`      |   Yes |     Yes |           Yes |        ContactPoint |
| `set_primary_contact_point`     |   Yes |     Yes |           Yes |        ContactPoint |
| `attach_account`                |   Yes |     Yes |           Yes |             Account |
| `resolve_authenticated_contact` |   Yes |     Yes | No by default |          Resolution |
| `disable_account`               |   Yes |     Yes |           Yes |             Account |
| `revoke_account`                |   Yes |     Yes |           Yes |             Account |
| `detect_duplicate_contact`      |   Yes |     Yes |            No |      Reconciliation |
| `propose_merge`                 |   Yes |     Yes | proposal only |      Merge proposal |
| `merge_contacts`                |   Yes |     Yes |           Yes | **Merge execution** |

---

# 46. B3 Boundary Freeze Candidate

Subject to challenge before the Requirement Matrix:

```text
B3 OWNS

Actor identity resolution
Contact controlled creation
ContactPoint lifecycle
ContactPoint verification semantics
External Account binding
Authenticated identity → Contact resolution
Account disable/revoke
Duplicate Contact detection
Merge proposal
Governed Contact merge
Identity-operation provenance semantics
Identity-operation idempotency semantics
Identity-operation conflict semantics
```

B3 DOES NOT OWN:

```text
Authentication mechanisms
Authorization system
OAuth implementation
Passwords
Sessions
JWT
RBAC
Frontend
Asset identity
Asset relationships
Case lifecycle
Runner execution
VIR
PGDR
CRM
Hard-delete policy
```

---

# 47. Completion Criterion

B3 is not complete merely because the underlying B2 tables can be manipulated.

B3 is complete when an authorized consumer can request an identity operation and CPL can:

```text
understand the request
      ↓
determine applicable identity state
      ↓
apply authority and policy
      ↓
make an explicit decision
      ↓
perform or refuse the mutation
      ↓
preserve history
      ↓
return a semantically meaningful result
```

without requiring the consumer to manipulate identity persistence directly.

---

# 48. Relationship to B3 Requirement Matrix

We now have three layers:

```text
B3 Identity Object & Authority Map
              │
              │ WHAT EXISTS?
              ▼
B3 Identity Resolution State & Decision Model
              │
              │ WHAT MAY BE CONCLUDED?
              ▼
B3 Service Boundary & Operation Contract
              │
              │ WHAT MAY BE REQUESTED?
              ▼
        B3 REQUIREMENT MATRIX
```

The Requirement Matrix can now transform these semantic obligations into individually testable requirements.

---

# 49. Status

```text
B3_IDENTITY_OBJECT_AUTHORITY_MAP
  RECORDED

B3_IDENTITY_RESOLUTION_STATE_DECISION_MODEL
  RECORDED

B3_SERVICE_BOUNDARY_AND_OPERATION_CONTRACT
  PROPOSED v0

B3_REQUIREMENT_MATRIX
  NOT YET PRODUCED

B3_EXECUTION_MANDATE
  NOT ISSUED

B3_IMPLEMENTATION
  NOT AUTHORIZED
```

**End of `CPL — B3 Service Boundary & Operation Contract v0`**

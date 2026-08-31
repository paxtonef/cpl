# CPL — B3 Service Boundary & Operation Contract v0.1

**System:** Common Product Layer — CPL
**Build Phase:** B3 — Identity + Accounts
**Artifact:** Service Boundary & Operation Contract
**Version:** v0.1 — Cross-Artifact Repair
**Status:** PROPOSED FOR RE-CHALLENGE
**Canonical baseline:** `main @ cb5a05d`

**Canonical predecessors:**

* `B3_IDENTITY_OBJECT_AUTHORITY_MAP_v0.md`
* `B3_IDENTITY_RESOLUTION_STATE_DECISION_MODEL_v0.md`
* `B3_SERVICE_BOUNDARY_AND_OPERATION_CONTRACT_v0.md`

---

## 1. Purpose

This version consolidates the B3 Service Boundary following the cross-artifact challenge of the three B3 WHAT artifacts.

It is a bounded repair of v0.

It does not:

```text
authorize implementation;
introduce transport/API architecture;
modify the B2 persistence foundation;
expand B3 into authentication or authorization;
expand B3 into Asset or Case identity;
authorize B3 execution.
```

The repair is limited to the ten cross-artifact decisions:

```text
F-B3-01 → F-B3-10
```

---

## 2. Governing Semantic Chain

B3 SHALL preserve the following separation:

```text
Evidence
   ↓
Resolution
   ↓
Decision
   ↓
Authority
   ↓
Mutation
   ↓
Historical State
```

No service convenience operation may collapse these layers in a way that removes a governed decision boundary.

---

## 3. B3 Service Boundary

B3 exposes governed operations concerning actor identity.

```text
                 CALLER
                    │
                    ▼
        ┌───────────────────────┐
        │      B3 SERVICE       │
        │        BOUNDARY       │
        ├───────────────────────┤
        │ Contact               │
        │ Contact Resolution    │
        │ ContactPoint          │
        │ Account Binding       │
        │ Reconciliation        │
        └───────────┬───────────┘
                    │
                    ▼
             B2 Persistence
```

Consumers SHALL NOT be required to manipulate B2 persistence directly to perform governed B3 identity operations.

---

## 4. Explicit Boundary

B3 owns:

```text
actor identity resolution
controlled Contact creation
ContactPoint lifecycle
ContactPoint verification-state recording
external Account binding
authenticated identity → Contact resolution
Account disable/revoke
duplicate Contact assessment
merge proposal
governed Contact merge
identity-operation provenance
identity-operation conflict semantics
identity-operation idempotency semantics
```

B3 does not own:

```text
authentication mechanisms
passwords
OAuth protocol execution
OTP delivery
email verification transport
SMS verification transport
sessions
JWT
RBAC
authorization-system administration
frontend
Asset identity
Case lifecycle
Runner execution
VIR
PGDR
hard-delete policy
```

---

## 5. F-B3-01 — PROVISIONAL Semantics

PROVISIONAL SHALL NOT become a new persistent `Contact.status` in B3 v1.

The B2 Contact lifecycle remains authoritative.

Therefore:

```text
Contact.status
≠
ResolutionState
```

A Contact may exist as:

```text
Contact.status = ACTIVE
```

while the current identity conclusion concerning that Contact remains:

```text
ResolutionState = PROVISIONAL
```

PROVISIONAL describes the epistemic/governed quality of the identity resolution or association.

It does not define a new Contact lifecycle state.

**Invariant B3-SB-I13**

> Resolution uncertainty SHALL NOT be encoded by inventing an unauthorized Contact lifecycle state.

---

## 6. F-B3-02 — Canonical Contact Retrieval

B3 v1 SHALL use:

```text
get_contact(contact_id)
```

as the canonical direct retrieval operation.

`find_contact` is removed from the primitive B3 v1 operation set.

This establishes an explicit distinction:

```text
get_contact
→ retrieval by canonical CPL Contact identity

resolve_contact
→ identity resolution from evidence
```

No operation named `find_contact` is required by the B3 v1 contract.

---

## 7. `get_contact`

### Purpose

Retrieve a Contact by canonical CPL Contact identifier.

### Input

```text
contact_id
caller_context where required
```

### Outcomes

```text
SUCCESS
NOT_FOUND
INVALID
EXECUTION_FAILURE
```

### Mutation

None.

### Prohibition

`get_contact` SHALL NOT:

```text
create Contact
modify Contact
attach Account
attach ContactPoint
perform identity reconciliation
change resolution state
```

---

## 8. `resolve_contact`

### Purpose

Evaluate identity evidence against CPL Contacts using the canonical B3 identity-resolution semantics.

Conceptual request:

```text
ResolveContactRequest
├── evidence[]
├── caller_context
├── authority_context
└── policy_context
```

Possible semantic results include:

```text
MATCHED
NOT_FOUND
AMBIGUOUS
CONFLICTING
UNRESOLVED
PROVISIONAL
```

where applicable under the Resolution State & Decision Model.

### Mutation rule

```text
resolve_contact
→ READ
→ ASSESS
→ DECIDE RESOLUTION
→ NO IDENTITY MUTATION
```

**Invariant B3-SB-I14**

> Resolution does not imply mutation.

---

## 9. F-B3-03 — `find_or_create_contact`

`find_or_create_contact` is not a B3 v1 primitive.

It is classified as:

```text
COMPOSED_OPERATION
OPTIONAL
```

Its semantic composition is:

```text
resolve_contact
       ↓
explicit resolution result
       ↓
creation admissibility decision
       ↓
create_contact
```

It SHALL NOT bypass either primitive contract.

In particular:

```text
MATCHED
→ return existing Contact

NOT_FOUND
+ creation authorized
→ create_contact may execute

AMBIGUOUS
→ NO CREATE

CONFLICTING
→ NO CREATE

UNRESOLVED
→ NO CREATE by default
```

A future orchestrator may expose this convenience operation, but its existence is not required for B3 v1 completion.

---

## 10. `create_contact`

### Purpose

Create a persistent CPL Contact when creation is authorized and identity conditions permit it.

Required semantic inputs include:

```text
contact_type
creation context/evidence
caller authority
provenance
```

### Preconditions

At minimum:

```text
valid contact_type
creation authority present
required creation context present
no known blocking identity conflict
```

### Outcomes

```text
SUCCESS
REJECTED
INVALID
CONFLICTING
ALREADY_EXISTS
EXECUTION_FAILURE
```

### Prohibition

Creation SHALL NOT implicitly establish:

```text
verified email
verified telephone
authenticated Account
Asset ownership
Case participation
completed identity resolution
```

---

## 11. ContactPoint Operations

B3 v1 primitive ContactPoint operations are:

```text
add_contact_point
verify_contact_point
invalidate_contact_point
set_primary_contact_point
```

A ContactPoint remains:

> identity evidence and/or communication channel

It is not itself the authoritative definition of the Contact.

---

## 12. `add_contact_point`

### Preconditions

```text
Contact exists
Contact permits modification
ContactPoint type valid
caller authorized
applicable uniqueness constraints satisfied
```

Adding the point SHALL NOT imply verification.

Conceptually:

```text
add_contact_point
        ↓
ContactPoint exists
        ↓
verification not automatically established
```

---

## 13. F-B3-04 — Verification Boundary

B3 does not perform external verification mechanisms.

B3 SHALL NOT own:

```text
send email
send SMS
generate OTP
validate OAuth challenge
perform biometric check
contact government identity provider
```

Instead:

```text
External / trusted verification mechanism
                 ↓
       Verification Assertion
                 ↓
                B3
                 ↓
      verification-state transition
```

`verify_contact_point` means:

> accept an admissible verification assertion and record the corresponding governed ContactPoint transition.

It does not mean:

> independently perform the external verification procedure.

---

## 14. Verification Assertion

The exact implementation representation remains downstream, but B3 must conceptually possess sufficient information to establish:

```text
what ContactPoint was verified?
what mechanism produced the assertion?
what evidence/result was produced?
who/what had authority to assert it?
when did verification occur?
is the assertion admissible under policy?
```

A caller's unsupported declaration:

> "this email is verified"

is insufficient by itself.

---

## 15. `verify_contact_point`

### Input

Conceptually:

```text
contact_point_id
verification_assertion
authority_context
provenance
```

### Preconditions

```text
ContactPoint exists
assertion admissible
assertion applies to that ContactPoint
transition permitted
authority sufficient
```

### Result

The ContactPoint enters the appropriate verified state.

### Failure

Invalid, unsupported or inadmissible assertions SHALL NOT create verified state.

---

## 16. `invalidate_contact_point`

This operation records that a ContactPoint must no longer be treated as current valid evidence/channel.

Possible causes include:

```text
revocation
known reassignment
failed re-verification
administrative invalidation
trusted provider evidence
```

Historical existence SHALL remain preserved.

---

## 17. `set_primary_contact_point`

Primary means:

> preferred current ContactPoint of applicable type

It does not mean:

> identity authority

The operation requires:

```text
point belongs to Contact
point active
required verification state satisfied
uniqueness invariant preserved
authority present
```

---

## 18. Account Operations

B3 v1 Account operations are:

```text
attach_account
resolve_authenticated_contact
disable_account
revoke_account
```

Account represents an external provider identity binding to CPL identity.

It does not transfer ultimate identity authority to that provider.

---

## 19. `attach_account`

Conceptually:

```text
External Provider Identity
          ↓
       Account
          ↓
       Contact
```

Required inputs:

```text
contact_id
provider
provider_subject
authority_context
provenance
```

Preconditions:

```text
Contact exists
provider identity structurally valid
binding permitted
caller authorized
no conflicting binding
```

Existing contradictory binding SHALL produce conflict rather than silent reassignment.

---

## 20. F-B3-05 — One Resolution Semantics

`resolve_authenticated_contact` SHALL NOT implement an independent identity-resolution model.

It is a specialized entry into the same semantic resolution system used by:

```text
resolve_contact
```

Therefore:

```text
ONE RESOLUTION SEMANTICS
        +
MULTIPLE EVIDENCE TYPES
```

An authenticated provider identity is an evidence type, not a separate identity ontology.

Conceptually:

```text
AuthenticatedProviderIdentityEvidence
               ↓
      canonical resolution model
               ↓
        resolution result
```

---

## 21. `resolve_authenticated_contact`

Input:

```text
provider
provider_subject
authenticated identity evidence
caller_context
```

If an admissible active Account binding exists:

```text
provider identity
      ↓
active Account
      ↓
Contact
      ↓
MATCHED
```

subject to Contact state and applicable policy.

If no authoritative active Account binding exists, the operation may return:

```text
NOT_FOUND
AMBIGUOUS
CONFLICTING
UNRESOLVED
PROVISIONAL
```

or use additional admissible evidence through the canonical resolution model.

It SHALL NOT automatically create a Contact or Account unless a separately governed composition explicitly authorizes those mutations.

---

## 22. F-B3-06 — Account State and Resolution Authority

Account existence alone does not establish current resolution authority.

For B3 v1:

```text
ACTIVE
→ may provide current authenticated-resolution authority

PENDING
→ contextual evidence only

DISABLED
→ historical binding; no current authenticated-resolution authority

REVOKED
→ historical evidence only; no current authenticated-resolution authority
```

Thus:

```text
historical binding
≠
current authority
```

**Invariant B3-SB-I15**

> Disabled or revoked Account bindings SHALL NOT silently resolve current authenticated identity.

---

## 23. `disable_account`

Conceptual transition:

```text
ACTIVE
  ↓
DISABLED
```

Disabling removes current active-use authority while preserving historical identity evidence.

It SHALL NOT erase:

```text
provider identity
historical Contact association
creation provenance
historical activity
```

---

## 24. `revoke_account`

Conceptual transition:

```text
ACTIVE / DISABLED
        ↓
     REVOKED
```

Revocation is stronger than ordinary disabling.

Historical binding remains preserved unless a separate future retention/deletion authority dictates otherwise.

---

## 25. Account Rebinding

B3 SHALL NOT expose unrestricted rebinding equivalent to:

```text
account.contact_id = another_contact
```

A contradictory Account-to-Contact relationship is an identity reconciliation matter.

It SHALL NOT be treated as ordinary editing.

---

## 26. Identity Reconciliation Operations

B3 v1 reconciliation primitives are:

```text
detect_duplicate_contact
propose_merge
merge_contacts
```

These represent three different levels of authority:

```text
ASSESS
  ↓
PROPOSE
  ↓
EXECUTE
```

They SHALL remain distinguishable.

---

## 27. F-B3-10 — Duplicate Detection Has No Merge Authority

`detect_duplicate_contact` produces:

```text
DuplicateAssessment
```

Possible semantic assessment outcomes may include:

```text
NO_DUPLICATE_INDICATION
POSSIBLE_DUPLICATE
STRONG_DUPLICATE_CANDIDATE
UNRESOLVED
```

No score, similarity measure, model output or confidence value can itself authorize merge.

Therefore:

```text
DuplicateAssessment
≠
MergeDecision
```

and:

```text
confidence = 1.0
```

still does not imply:

```text
AUTHORIZE_MERGE
```

---

## 28. `propose_merge`

Purpose:

> transform admissible reconciliation evidence into an explicit merge proposal.

Conceptual input:

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

The creation of a MergeCandidate SHALL NOT mutate either Contact into merged state.

---

## 29. `merge_contacts`

`merge_contacts` is the highest-authority B3 v1 mutation.

It executes an already admissible and authorized reconciliation decision.

Required conditions include:

```text
source exists
target exists
source != target
source eligible
target eligible
merge evidence exists
merge authority exists
related-object invariants can be preserved
no unresolved blocking structural conflict
```

Conceptually:

```text
SOURCE
   ↓
MERGED INTO
   ↓
TARGET
```

Merge is directional:

```text
merge(A, B)
≠
merge(B, A)
```

---

## 30. F-B3-07 — Source Preservation

Merge SHALL preserve the source Contact.

Conceptually:

```text
source.status = MERGED
source.merged_into_id = target.id
```

The source SHALL remain historically interpretable.

Merge SHALL NOT normally mean:

```text
DELETE source
```

**Invariant B3-SB-I16**

> Identity reconciliation supersedes historical identity representation; it does not erase it.

---

## 31. F-B3-08 — No Blind Foreign-Key Rewrite

B3 SHALL NOT define merge as:

```text
for every FK referencing SOURCE:
    replace SOURCE with TARGET
```

Historical references may themselves constitute evidence.

Therefore related objects require relationship-family-specific semantics.

At minimum the merge process must consider:

```text
Accounts
ContactPoints
ContactAssetRelationships
CaseParticipants
ExternalReferences
```

---

## 32. Historical vs Active Relationships

B3 SHALL distinguish between:

```text
historical relationship
```

and:

```text
current identity-bearing relationship
```

Historical references MAY remain attached to the source Contact where necessary to preserve provenance.

Current identity-bearing relationships MAY require governed reassociation.

These two cases SHALL NOT be treated identically.

---

## 33. F-B3-09 — Account Conflicts During Merge

An Account associated with SOURCE SHALL NOT be blindly transferred to TARGET.

Conceptually:

```text
SOURCE Account
      ↓
TARGET compatibility assessment
```

If reassociation would violate an identity invariant:

```text
→ CONFLICTING
→ merge blocked
```

If reassociation is admissible:

```text
→ governed reassociation may occur
```

The Requirement Matrix must specify the exact admissibility conditions.

---

## 34. ContactPoint Conflicts During Merge

The same preservation-first rule applies.

B3 SHALL NOT:

```text
blindly copy all ContactPoints
blindly delete source ContactPoints
blindly make them primary on TARGET
```

Potential conflicts include:

```text
duplicate primary point
different verification states
contradictory active values
historically reassigned point
```

If safe reconciliation cannot be established:

```text
merge_contacts
→ CONFLICTING / REJECTED
```

---

## 35. F-B3-07/08/09 — Merge Preservation Rule

The consolidated B3 v1 rule is:

> If B3 cannot reconcile identity-bearing relationships while preserving history and all applicable invariants, the merge SHALL NOT execute.

Therefore:

```text
uncertain reconciliation
        ↓
do not partially merge
        ↓
return governed non-success outcome
```

---

## 36. Merge Transaction Boundary

Merge must be transactionally coherent.

The system SHALL NOT expose a state such as:

```text
source marked MERGED
but required Account reconciliation failed
```

or:

```text
some identity relationships transferred
while merge itself failed
```

Required transition:

```text
all required merge mutations succeed
```

or:

```text
no misleading partial merge state survives
```

---

## 37. Merge Idempotency

Replay of an already completed logical merge:

```text
A → B
```

SHALL NOT multiply mutation.

Appropriate result:

```text
NO_CHANGE
```

or:

```text
ALREADY_MERGED
```

where semantically appropriate.

---

## 38. Generic CRUD Remains Forbidden

B3 SHALL NOT expose unrestricted primitives such as:

```text
update_contact(any_fields)
update_contact_point(any_fields)
update_account(any_fields)

delete_contact()
delete_contact_point()
delete_account()
```

because these collapse semantic transitions into persistence mutation.

B3 exposes governed operations.

B2 provides persistence.

These responsibilities SHALL remain distinct.

---

## 39. Authority Classes

The B3 contract requires at least the following semantic authorities:

```text
READ_IDENTITY
RESOLVE_IDENTITY
CREATE_CONTACT

MANAGE_CONTACT_POINT
VERIFY_CONTACT_POINT

ATTACH_ACCOUNT
MANAGE_ACCOUNT

ASSESS_DUPLICATE
PROPOSE_MERGE
AUTHORIZE_MERGE
EXECUTE_MERGE
```

The external authorization system may represent them differently.

The semantic distinctions must survive.

---

## 40. Authentication vs Authority

B3 does not authenticate callers.

Conceptually:

```text
Authentication / Authorization System
                ↓
       caller authority context
                ↓
               B3
                ↓
      operation admissibility
```

B3 consumes authority context and enforces its own operation preconditions.

It does not issue credentials.

---

## 41. Common Operation Outcomes

B3 SHALL preserve semantic distinctions between:

```text
SUCCESS
MATCHED
NO_MATCH / NOT_FOUND
AMBIGUOUS
CONFLICTING
UNRESOLVED
PROVISIONAL
REJECTED
INVALID
ALREADY_EXISTS
ALREADY_MERGED
NO_CHANGE
EXECUTION_FAILURE
```

The implementation representation is downstream.

These states SHALL NOT all collapse into generic execution failure.

---

## 42. Idempotency

Material B3 operations must define appropriate replay semantics.

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

Repeated execution of the same logical authorized request SHALL NOT unintentionally multiply identity state.

---

## 43. Concurrency

B3 SHALL assume concurrent operations.

Examples:

```text
two Contact creation attempts from equivalent evidence

two Account binding attempts for same provider identity

two primary ContactPoint selections

two merge attempts involving same source Contact
```

B2 constraints remain a defense mechanism.

B3 must interpret constraint conflicts as identity-domain outcomes where possible.

---

## 44. Provenance

Material B3 decisions and mutations must preserve sufficient provenance to establish:

```text
what operation was requested?
who/what requested it?
what evidence supported it?
under what authority?
what decision was reached?
what mutation occurred?
when?
```

The exact storage implementation remains downstream.

---

## 45. Read / Decision / Mutation Separation

### Retrieval

```text
get_contact
```

### Resolution / Assessment

```text
resolve_contact
resolve_authenticated_contact
detect_duplicate_contact
```

### Proposal

```text
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

No lower-authority category may silently execute a higher-authority category.

---

## 46. B3 v1 Primitive Operation Freeze Candidate

The repaired candidate primitive set contains 14 operations:

```text
CONTACT
01 get_contact
02 resolve_contact
03 create_contact

CONTACT POINT
04 add_contact_point
05 verify_contact_point
06 invalidate_contact_point
07 set_primary_contact_point

ACCOUNT
08 attach_account
09 resolve_authenticated_contact
10 disable_account
11 revoke_account

RECONCILIATION
12 detect_duplicate_contact
13 propose_merge
14 merge_contacts
```

`find_or_create_contact` is excluded from this primitive count.

It remains an optional governed composition.

---

## 47. Cross-Artifact Repair Decisions

The v0 → v0.1 delta incorporates exactly these decisions:

```text
F-B3-01
PROVISIONAL is a resolution/association state,
not a Contact persistent status.

F-B3-02
get_contact is canonical retrieval.
find_contact is removed as a separate primitive.

F-B3-03
find_or_create_contact is a composition,
not a core primitive.

F-B3-04
B3 records admissible verification assertions;
it does not perform external verification mechanisms.

F-B3-05
resolve_authenticated_contact uses the same
resolution semantics as resolve_contact.

F-B3-06
Only ACTIVE Account bindings may provide
current authenticated-resolution authority.

F-B3-07
Contact merge preserves the source Contact
and historical interpretability.

F-B3-08
Merge does not blindly rewrite related FKs.

F-B3-09
Account / ContactPoint reconciliation conflicts
may block merge.

F-B3-10
Duplicate detection produces assessment evidence,
never merge authority.
```

---

## 48. Consolidated Cross-Artifact Invariants

**B3-X-I01 — One resolution semantics**
All resolution entry points operate under the same governed identity-resolution model.

**B3-X-I02 — No hidden creation shortcut**
Convenience composition cannot bypass resolution and creation authority.

**B3-X-I03 — Verification mechanism remains external**
B3 records admissible verification outcomes; it does not own verification transport.

**B3-X-I04 — Historical binding is not active authority**
Disabled/revoked Accounts cannot silently resolve current authenticated identity.

**B3-X-I05 — Merge is preservation-first**
Unsafe reconciliation blocks merge.

**B3-X-I06 — Duplicate assessment has no execution authority**
Detection, similarity or confidence cannot authorize merge.

**B3-X-I07 — Decision and mutation remain distinguishable**
An identity conclusion does not automatically cause persistence mutation.

**B3-X-I08 — Persistence does not define semantics**
The existence of a technically possible B2 database update does not make that update an authorized B3 operation.

---

## 49. Deferred Capabilities

B3 v1 continues to defer:

```text
bulk identity import
bulk merge
automatic probabilistic merge
automatic ML/LLM-authorized merge
cross-tenant identity federation
biometric identity
government identity verification
OAuth protocol implementation
password credentials
session management
JWT
RBAC
identity graph ML
hard deletion
Asset identity resolution
Case lifecycle
```

No repair decision expands this scope.

---

## 50. Completion Criterion

B3 is complete when an authorized consumer can:

```text
present an identity operation
          ↓
B3 understands its semantic class
          ↓
evaluates identity evidence/state
          ↓
applies authority and admissibility
          ↓
returns explicit decision
          ↓
performs or refuses mutation
          ↓
preserves history and provenance
          ↓
returns meaningful outcome
```

without requiring the consumer to perform arbitrary identity-table mutation.

---

## 51. Relationship to Requirement Matrix

After successful re-challenge:

```text
Identity Object & Authority Map
            ↓
Identity Resolution State & Decision Model
            ↓
Service Boundary & Operation Contract v0.1
            ↓
      WHAT CONSOLIDATION
            ↓
      Requirement Matrix
            ↓
      Execution Mandate
            ↓
════════ BUILD BOUNDARY ════════
            ↓
      B3 Implementation
```

The Requirement Matrix will convert the frozen semantic obligations into individually identifiable, testable requirements.

---

## 52. Status

```text
B3_IDENTITY_OBJECT_AUTHORITY_MAP_v0
  RECORDED

B3_IDENTITY_RESOLUTION_STATE_DECISION_MODEL_v0
  RECORDED

B3_SERVICE_BOUNDARY_AND_OPERATION_CONTRACT_v0
  RECORDED / CHALLENGED

B3_SERVICE_BOUNDARY_AND_OPERATION_CONTRACT_v0.1
  PROPOSED / AWAITING RE-CHALLENGE

B3_WHAT
  NOT YET FROZEN

B3_REQUIREMENT_MATRIX
  NOT YET AUTHORIZED FOR PRODUCTION

B3_EXECUTION_MANDATE
  NOT ISSUED

B3_IMPLEMENTATION
  NOT AUTHORIZED
```

**End of `CPL — B3 Service Boundary & Operation Contract v0.1`**

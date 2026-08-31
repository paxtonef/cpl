# CPL — B3 Requirement Matrix v0

**System:** Common Product Layer — CPL
**Build Phase:** B3 — Identity + Accounts
**Artifact:** Requirement Matrix
**Version:** v0
**Status:** PROPOSED FOR REQUIREMENT CHALLENGE
**Canonical repository:** `paxtonef/cpl`
**Canonical WHAT Freeze:** `6002ec802e3cd912e233043ab83445872f5dc67f`

**Authoritative upstream artifacts:**

* `B3_IDENTITY_OBJECT_AUTHORITY_MAP_v0.md`
* `B3_IDENTITY_RESOLUTION_STATE_DECISION_MODEL_v0.md`
* `B3_SERVICE_BOUNDARY_AND_OPERATION_CONTRACT_v0.1.md`
* `B3_WHAT_CONSOLIDATION_AND_FREEZE_v0.md`
* `B3_WHAT_FREEZE_CHALLENGE_v0.md`

**Governance state:**

```text
B3 WHAT
  FROZEN

B3 Requirement Matrix
  AUTHORIZED FOR PRODUCTION
  THIS DOCUMENT = v0 CANDIDATE

B3 Execution Mandate
  NOT ISSUED

B3 Implementation
  NOT AUTHORIZED
```

---

## 1. Purpose

This matrix transforms the frozen B3 WHAT into individually identifiable, normative and verifiable requirements.

It does not reopen the B3 WHAT.

It does not prescribe implementation architecture unless a particular implementation property is necessary to satisfy a frozen semantic obligation.

The transformation chain is:

```text
FROZEN B3 WHAT
      ↓
20 RMO obligation families
      ↓
individual normative requirements
      ↓
verification obligations
      ↓
Requirement Challenge
      ↓
Execution Mandate
```

---

# 2. Requirement status vocabulary

Each requirement in this matrix has one of the following normative strengths:

```text
MUST
  mandatory for B3 acceptance

MUST NOT
  prohibited behavior

SHOULD
  expected unless explicit justified deviation is accepted

MAY
  permitted but not required
```

For B3 v1 acceptance, requirements marked `MUST` or `MUST NOT` constitute the normative acceptance surface.

---

# 3. Traceability model

Every requirement carries:

```text
REQ-ID
RMO family
Primitive(s)
Normative requirement
Verification type
Acceptance evidence
```

Verification types:

```text
POSITIVE
NEGATIVE
STATE
CONCURRENCY
TRANSACTION
NON_REGRESSION
INSPECTION
TRACEABILITY
```

---

# 4. Frozen primitive boundary

This Requirement Matrix SHALL operate only on the frozen 14 primitive operations:

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

No requirement in this matrix authorizes addition or deletion of a primitive.

---

# 5. RMO-01 — Object Retrieval

### REQ-B3-001 — Canonical Contact retrieval

`get_contact` MUST retrieve a Contact by canonical `contact_id`.

**Verification:** POSITIVE

Expected:

```text
existing contact_id
→ SUCCESS + Contact
```

---

### REQ-B3-002 — Missing Contact

`get_contact` MUST distinguish an unknown `contact_id` from execution failure.

Expected:

```text
unknown contact_id
→ NOT_FOUND
```

not:

```text
generic database failure
```

**Verification:** NEGATIVE

---

### REQ-B3-003 — Retrieval immutability

`get_contact` MUST NOT mutate Contact identity state or related identity-bearing objects.

**Verification:** STATE

---

# 6. RMO-02 — Resolution Semantics

### REQ-B3-004 — Resolution without mutation

`resolve_contact` MUST evaluate identity evidence without automatically creating or mutating Contact, ContactPoint or Account state.

**Verification:** STATE

---

### REQ-B3-005 — Matched resolution

Where admissible evidence resolves uniquely to one existing Contact, B3 MUST be capable of returning:

```text
MATCHED
```

with the resolved Contact.

**Verification:** POSITIVE

---

### REQ-B3-006 — No-match resolution

Where no admissible existing Contact matches the evidence, B3 MUST be capable of returning:

```text
NOT_FOUND
```

without automatically creating a Contact.

**Verification:** NEGATIVE / STATE

---

### REQ-B3-007 — Ambiguous resolution

Where more than one Contact remains plausibly admissible and no rule establishes a unique result, B3 MUST return:

```text
AMBIGUOUS
```

B3 MUST NOT arbitrarily select one candidate.

**Verification:** NEGATIVE

---

### REQ-B3-008 — Conflicting evidence

Where admissible evidence actively supports incompatible Contact resolutions, B3 MUST return:

```text
CONFLICTING
```

or equivalent frozen semantic outcome.

B3 MUST NOT overwrite one evidence source merely to force a match.

**Verification:** NEGATIVE

---

### REQ-B3-009 — Unresolved resolution

Where B3 lacks sufficient grounds for MATCHED, NOT_FOUND, AMBIGUOUS or CONFLICTING under applicable policy, it MUST be capable of returning:

```text
UNRESOLVED
```

**Verification:** NEGATIVE

---

### REQ-B3-010 — Provisional semantics

Where a provisional identity association is permitted, B3 MUST represent `PROVISIONAL` as resolution/association semantics and MUST NOT introduce `PROVISIONAL` as a new Contact lifecycle status.

**Verification:** INSPECTION + STATE

---

### REQ-B3-011 — Technical failure separation

Execution failure MUST NOT be represented as:

```text
NOT_FOUND
AMBIGUOUS
CONFLICTING
UNRESOLVED
PROVISIONAL
```

**Verification:** NEGATIVE

---

# 7. RMO-03 — Contact Creation

### REQ-B3-012 — Explicit creation authority

`create_contact` MUST require applicable Contact creation authority.

**Verification:** NEGATIVE

---

### REQ-B3-013 — Valid Contact type

`create_contact` MUST reject an unsupported `contact_type`.

**Verification:** NEGATIVE

---

### REQ-B3-014 — Creation does not imply verification

Successful Contact creation MUST NOT implicitly establish:

```text
verified ContactPoint
active Account
Asset ownership
Case participation
completed identity resolution
```

**Verification:** STATE

---

### REQ-B3-015 — Conflict blocks creation

Where creation evidence exposes a known blocking identity conflict, Contact creation MUST NOT silently create another canonical Contact.

**Verification:** NEGATIVE

---

### REQ-B3-016 — No hidden find-or-create primitive

No B3 primitive may implement unconditional:

```text
lookup
→ if absent INSERT
```

as a substitute for the frozen resolution → decision → creation sequence.

**Verification:** INSPECTION + NEGATIVE

---

# 8. RMO-04 — ContactPoint Lifecycle

### REQ-B3-017 — ContactPoint attachment

`add_contact_point` MUST attach a valid ContactPoint only to an existing admissible Contact.

**Verification:** POSITIVE / NEGATIVE

---

### REQ-B3-018 — No implicit verification

A newly attached ContactPoint MUST NOT become VERIFIED solely because it was added.

**Verification:** STATE

---

### REQ-B3-019 — ContactPoint ownership

B3 MUST reject ContactPoint operations where the ContactPoint does not belong to the claimed Contact context when such ownership is required.

**Verification:** NEGATIVE

---

### REQ-B3-020 — ContactPoint invalidation preserves history

`invalidate_contact_point` MUST make the point unavailable as current valid evidence/channel without erasing its historical existence.

**Verification:** STATE

---

### REQ-B3-021 — Primary ContactPoint constraint

`set_primary_contact_point` MUST preserve the B2 uniqueness semantics governing active primary ContactPoints of the applicable type.

**Verification:** POSITIVE / NEGATIVE

---

### REQ-B3-022 — Primary does not imply identity authority

Selection as primary MUST NOT grant the ContactPoint additional identity authority beyond the frozen ContactPoint semantics.

**Verification:** STATE / INSPECTION

---

# 9. RMO-05 — Verification Assertion Admissibility

### REQ-B3-023 — External verification boundary

B3 MUST NOT implement the external verification transport/mechanism as part of `verify_contact_point`.

**Verification:** INSPECTION / BOUNDARY

---

### REQ-B3-024 — Verification assertion required

`verify_contact_point` MUST require an admissible verification assertion or equivalent governed evidence.

A caller declaration alone MUST NOT be sufficient.

**Verification:** NEGATIVE

---

### REQ-B3-025 — Verification target binding

A verification assertion MUST apply to the ContactPoint being transitioned.

An assertion for ContactPoint A MUST NOT verify ContactPoint B.

**Verification:** NEGATIVE

---

### REQ-B3-026 — Verification authority

The assertion and/or caller context MUST satisfy the applicable verification authority conditions.

**Verification:** NEGATIVE

---

### REQ-B3-027 — Replay safety

Replay of the same logical accepted verification event MUST NOT multiply identity state or create inconsistent verification history.

**Verification:** IDEMPOTENCY

---

# 10. RMO-06 — Account Binding

### REQ-B3-028 — Account attachment

`attach_account` MUST bind a structurally valid external provider identity to an existing Contact when applicable authority and admissibility conditions are met.

**Verification:** POSITIVE

---

### REQ-B3-029 — Unique provider identity

B3 MUST preserve the B2 uniqueness invariant for:

```text
provider + provider_subject
```

**Verification:** NEGATIVE

---

### REQ-B3-030 — Contradictory binding

Where an external provider identity is already bound incompatibly to another Contact, `attach_account` MUST NOT silently rebind it.

Expected semantic outcome:

```text
CONFLICTING
```

or equivalent.

**Verification:** NEGATIVE

---

### REQ-B3-031 — Account attachment authority

Account binding MUST require applicable Account attachment authority.

**Verification:** NEGATIVE

---

### REQ-B3-032 — No provider identity supremacy

Successful Account attachment MUST NOT redefine the Contact's canonical CPL identity as being owned by the external provider.

**Verification:** INSPECTION

---

# 11. RMO-07 — Account-State Authority

### REQ-B3-033 — Active Account resolution

An admissible `ACTIVE` Account MAY provide current authenticated-resolution authority.

**Verification:** POSITIVE

---

### REQ-B3-034 — Pending Account limitation

A `PENDING` Account MUST NOT by itself provide final current authenticated-resolution authority.

**Verification:** NEGATIVE

---

### REQ-B3-035 — Disabled Account limitation

A `DISABLED` Account MUST NOT resolve current authenticated identity as an active binding.

Its historical relationship MUST remain recoverable.

**Verification:** NEGATIVE + STATE

---

### REQ-B3-036 — Revoked Account limitation

A `REVOKED` Account MUST NOT provide current authenticated-resolution authority.

Its historical existence MUST remain recoverable.

**Verification:** NEGATIVE + STATE

---

### REQ-B3-037 — Disable Account lifecycle

`disable_account` MUST transition an admissible Account into the B2 `DISABLED` state without deleting the Account.

**Verification:** STATE

---

### REQ-B3-038 — Revoke Account lifecycle

`revoke_account` MUST transition an admissible Account into the B2 `REVOKED` state without ordinary physical deletion.

**Verification:** STATE

---

# 12. RMO-08 — Duplicate Assessment

### REQ-B3-039 — Duplicate assessment read-only identity semantics

`detect_duplicate_contact` MUST NOT merge, delete, rebind or otherwise mutate Contact identity state.

**Verification:** STATE

---

### REQ-B3-040 — Duplicate assessment output

The operation MUST be capable of distinguishing at least the semantic equivalents of:

```text
NO_DUPLICATE_INDICATION
POSSIBLE_DUPLICATE
STRONG_DUPLICATE_CANDIDATE
UNRESOLVED
```

**Verification:** POSITIVE

---

### REQ-B3-041 — Confidence has no merge authority

No similarity score, confidence score, ML output or LLM output may independently authorize Contact merge.

**Verification:** NEGATIVE / INSPECTION

---

# 13. RMO-09 — Merge Proposal

### REQ-B3-042 — Proposal separation

`propose_merge` MUST produce a merge proposal/candidate without itself changing either Contact into `MERGED`.

**Verification:** STATE

---

### REQ-B3-043 — Proposal provenance

A merge proposal MUST preserve sufficient evidence to identify:

```text
source Contact
target Contact
basis/evidence
reason
proposer/requester
time
```

**Verification:** TRACEABILITY

---

### REQ-B3-044 — Proposal directionality

A merge proposal MUST distinguish source from target.

```text
proposal(A → B)
≠
proposal(B → A)
```

**Verification:** POSITIVE

---

# 14. RMO-10 — Merge Authorization

### REQ-B3-045 — Separate merge authority

`merge_contacts` MUST require applicable merge execution authority and an admissible prior merge authorization context.

Duplicate assessment alone MUST NOT satisfy this requirement.

**Verification:** NEGATIVE

---

### REQ-B3-046 — Authorization target consistency

Merge authorization for:

```text
A → B
```

MUST NOT authorize:

```text
B → A
```

or another source/target pair.

**Verification:** NEGATIVE

---

# 15. RMO-11 — Merge Execution

### REQ-B3-047 — Self-merge rejection

`merge_contacts` MUST reject:

```text
source_contact_id == target_contact_id
```

**Verification:** NEGATIVE

---

### REQ-B3-048 — Source preservation

Successful merge MUST preserve the source Contact as an interpretable historical Contact.

**Verification:** STATE

---

### REQ-B3-049 — Source merged state

Successful merge MUST establish the semantic equivalent of:

```text
SOURCE.status = MERGED
SOURCE.merged_into_id = TARGET.id
```

using the accepted B2 persistence semantics.

**Verification:** STATE

---

### REQ-B3-050 — Target survives

The target Contact MUST remain the surviving current Contact identity.

**Verification:** STATE

---

### REQ-B3-051 — Merge directionality

The system MUST preserve semantic distinction between:

```text
merge(A,B)
merge(B,A)
```

**Verification:** NEGATIVE / STATE

---

### REQ-B3-052 — Already merged replay

Replaying an already completed logical merge MUST NOT multiply mutation.

The result SHOULD be semantically equivalent to:

```text
ALREADY_MERGED
```

or:

```text
NO_CHANGE
```

**Verification:** IDEMPOTENCY

---

# 16. RMO-12 — Historical Preservation

### REQ-B3-053 — Contact historical existence

Merge MUST NOT physically erase the source Contact as ordinary behavior.

**Verification:** STATE

---

### REQ-B3-054 — Account history

Account disable, revoke or reconciliation MUST preserve sufficient historical Account binding information.

**Verification:** TRACEABILITY

---

### REQ-B3-055 — ContactPoint history

ContactPoint invalidation or reconciliation MUST preserve sufficient historical evidence of the former association/state.

**Verification:** TRACEABILITY

---

### REQ-B3-056 — Current vs historical distinction

B3 MUST permit downstream verification to distinguish current identity-bearing relationships from historical relationships.

**Verification:** STATE / TRACEABILITY

---

# 17. RMO-13 — Related-Object Reconciliation

The Freeze Challenge authorized four classifications only:

```text
PRESERVE
REASSOCIATE
REJECT_CONFLICT
DEFER
```

Each relevant relationship family MUST be explicitly classified.

## REQ-B3-057 — Accounts during merge

Accounts associated with the source Contact MUST be reconciled under one or more authorized classifications:

```text
PRESERVE
REASSOCIATE
REJECT_CONFLICT
DEFER
```

Blind reassignment is forbidden.

**Verification:** POSITIVE / NEGATIVE / STATE

---

### REQ-B3-058 — ContactPoints during merge

ContactPoints associated with the source MUST be reconciled under the same authorized semantic space.

B3 MUST NOT blindly:

```text
copy all
delete all
make all primary
```

**Verification:** NEGATIVE / STATE

---

### REQ-B3-059 — ContactAssetRelationships

B3 merge behavior for `ContactAssetRelationships` MUST be explicitly classified as one or more of:

```text
PRESERVE
REASSOCIATE
REJECT_CONFLICT
DEFER
```

and MUST NOT be left to developer improvisation.

**Verification:** INSPECTION + STATE

---

### REQ-B3-060 — CaseParticipants

B3 merge behavior for `CaseParticipants` MUST be explicitly classified within the same four-state semantic space.

**Verification:** INSPECTION + STATE

---

### REQ-B3-061 — ExternalReferences

B3 merge behavior for `ExternalReferences` MUST be explicitly classified within the frozen semantic space.

**Verification:** INSPECTION + STATE

---

### REQ-B3-062 — Unsafe reconciliation blocks merge

If required related-object reconciliation cannot be completed without violating an identity or historical invariant, `merge_contacts` MUST NOT succeed.

**Verification:** NEGATIVE

---

# 18. RMO-14 — Transaction Integrity

### REQ-B3-063 — Atomic Account binding

An Account attachment operation MUST NOT leave a misleading partial binding if the complete operation fails.

**Verification:** TRANSACTION

---

### REQ-B3-064 — Atomic verification transition

A ContactPoint verification operation MUST NOT leave an authoritative verified state if required verification persistence fails.

**Verification:** TRANSACTION

---

### REQ-B3-065 — Atomic merge

A failed merge MUST NOT leave a state where:

```text
source = MERGED
```

while required identity reconciliation has failed.

**Verification:** TRANSACTION

---

### REQ-B3-066 — Merge rollback

Where any mandatory merge mutation fails, all identity-state mutations belonging to that logical merge MUST be rolled back or otherwise leave an equivalent non-misleading state.

**Verification:** TRANSACTION

---

# 19. RMO-15 — Idempotency

### REQ-B3-067 — Contact creation replay

Replay of the same logical authorized Contact creation request MUST NOT unintentionally produce multiple Contacts.

**Verification:** IDEMPOTENCY

---

### REQ-B3-068 — ContactPoint attachment replay

Replay of the same logical ContactPoint attachment MUST NOT unintentionally multiply equivalent active ContactPoints.

**Verification:** IDEMPOTENCY

---

### REQ-B3-069 — Account binding replay

Replay of the same logical Account attachment MUST NOT create multiple equivalent provider bindings.

**Verification:** IDEMPOTENCY

---

### REQ-B3-070 — Account lifecycle replay

Repeated disable/revoke requests MUST produce stable semantics and MUST NOT corrupt Account history.

**Verification:** IDEMPOTENCY

---

### REQ-B3-071 — Merge replay

Repeated execution of the same completed authorized merge MUST remain semantically stable.

**Verification:** IDEMPOTENCY

---

# 20. RMO-16 — Concurrency

### REQ-B3-072 — Concurrent equivalent Contact creation

Concurrent attempts representing the same logical authorized creation MUST NOT result in uncontrolled duplicate identity creation where B3 possesses sufficient information to identify the equivalence.

**Verification:** CONCURRENCY

---

### REQ-B3-073 — Concurrent provider binding

Concurrent attempts to bind one provider identity incompatibly to multiple Contacts MUST NOT result in two simultaneously valid active bindings.

**Verification:** CONCURRENCY

---

### REQ-B3-074 — Concurrent primary ContactPoint

Concurrent primary-selection operations MUST NOT leave a state violating the applicable B2 primary ContactPoint uniqueness invariant.

**Verification:** CONCURRENCY

---

### REQ-B3-075 — Concurrent merge

Concurrent merge operations involving the same source Contact MUST NOT create mutually incompatible surviving identity states.

**Verification:** CONCURRENCY

---

# 21. RMO-17 — Provenance

### REQ-B3-076 — Material-operation provenance

For each material B3 decision/mutation, sufficient provenance MUST be recoverable to identify:

```text
operation
requester / actor
evidence
authority context
decision
mutation
time
```

**Verification:** TRACEABILITY

---

### REQ-B3-077 — Merge provenance

Merge provenance MUST additionally preserve:

```text
source
target
reason
supporting reconciliation evidence
authorization context
```

**Verification:** TRACEABILITY

---

### REQ-B3-078 — Verification provenance

Verification state transition provenance MUST identify the verification assertion/mechanism context sufficient to explain why the transition was accepted.

**Verification:** TRACEABILITY

---

### REQ-B3-079 — No provenance invention

Where mandatory provenance is unavailable, B3 MUST NOT fabricate or infer provenance merely to complete an operation record.

**Verification:** NEGATIVE

---

# 22. RMO-18 — Boundary Preservation

### REQ-B3-080 — No authentication implementation

B3 MUST NOT implement:

```text
password handling
OAuth execution
OTP delivery
session issuance
JWT issuance
```

**Verification:** INSPECTION

---

### REQ-B3-081 — No authorization platform

B3 MAY consume authority context but MUST NOT become the general RBAC/authorization administration system.

**Verification:** INSPECTION

---

### REQ-B3-082 — No Asset identity resolution

B3 MUST NOT implement generic Asset or automotive identity resolution.

**Verification:** INSPECTION

---

### REQ-B3-083 — No Case lifecycle

B3 MUST NOT implement Case creation/lifecycle behavior beyond what is strictly necessary to preserve existing relationship semantics during identity reconciliation.

**Verification:** INSPECTION

---

### REQ-B3-084 — No Runner execution

B3 MUST NOT implement VIR, PGDR or other Runner execution.

**Verification:** INSPECTION

---

### REQ-B3-085 — No generic CRUD escape hatch

B3 MUST NOT expose unrestricted generic identity mutation capable of bypassing the frozen semantic operations.

**Verification:** INSPECTION / NEGATIVE

---

# 23. RMO-19 — B2 Non-Regression

### REQ-B3-086 — B2 migration continuity

B3 MUST preserve the accepted B2 migration foundation unless an explicit governed B2 change is separately authorized.

**Verification:** NON_REGRESSION

---

### REQ-B3-087 — Existing B2 tests

All B2 acceptance tests MUST remain passing after B3 implementation unless an explicitly authorized upstream change revises them.

**Verification:** NON_REGRESSION

---

### REQ-B3-088 — B1 runtime contract

The preserved B1 runtime behavior for:

```text
/health
/ready
```

MUST remain non-regressed by B3.

**Verification:** NON_REGRESSION

---

### REQ-B3-089 — Existing persistence integrity

B3 MUST NOT weaken accepted B2:

```text
PK
FK
CHECK
UNIQUE
partial unique
historical state
```

semantics merely to simplify service implementation.

**Verification:** INSPECTION + NON_REGRESSION

---

# 24. RMO-20 — Semantic Failure Outcomes

### REQ-B3-090 — Domain rejection vs execution failure

B3 MUST distinguish a governed domain rejection from a technical execution failure.

**Verification:** NEGATIVE

---

### REQ-B3-091 — Conflict vs invalid input

`CONFLICTING` MUST remain semantically distinguishable from `INVALID`.

**Verification:** NEGATIVE

---

### REQ-B3-092 — Ambiguous vs unresolved

`AMBIGUOUS` MUST remain distinguishable from `UNRESOLVED`.

**Verification:** NEGATIVE

---

### REQ-B3-093 — Already exists

Where an operation is blocked because an equivalent object/binding already exists, B3 SHOULD expose an `ALREADY_EXISTS` or equivalent semantic outcome rather than a generic failure where technically possible.

**Verification:** POSITIVE / NEGATIVE

---

### REQ-B3-094 — No-change semantics

A replay or request that requires no new mutation SHOULD return a semantic equivalent of:

```text
NO_CHANGE
```

or another explicit idempotent outcome rather than falsely reporting a fresh mutation.

**Verification:** IDEMPOTENCY

---

# 25. Cross-cutting authority requirements

### REQ-B3-095 — Retrieval authority

Where policy requires it, Contact retrieval MUST respect `READ_IDENTITY` authority.

---

### REQ-B3-096 — Resolution authority

Identity-resolution operations MUST respect `RESOLVE_IDENTITY` authority.

---

### REQ-B3-097 — Contact creation authority

Contact creation MUST respect `CREATE_CONTACT`.

---

### REQ-B3-098 — ContactPoint management authority

ContactPoint lifecycle operations MUST respect applicable:

```text
MANAGE_CONTACT_POINT
VERIFY_CONTACT_POINT
```

authority.

---

### REQ-B3-099 — Account authority

Account operations MUST distinguish:

```text
ATTACH_ACCOUNT
MANAGE_ACCOUNT
```

where applicable.

---

### REQ-B3-100 — Reconciliation authority ladder

The implementation MUST preserve distinct authority semantics for:

```text
ASSESS_DUPLICATE
PROPOSE_MERGE
AUTHORIZE_MERGE
EXECUTE_MERGE
```

No lower authority MUST silently satisfy a higher authority requirement.

---

# 26. Primitive-specific minimum requirement mapping

| Primitive                       | Minimum requirements        |
| ------------------------------- | --------------------------- |
| `get_contact`                   | 001–003, 095                |
| `resolve_contact`               | 004–011, 096                |
| `create_contact`                | 012–016, 067, 072, 097      |
| `add_contact_point`             | 017–018, 068, 098           |
| `verify_contact_point`          | 023–027, 064, 078, 098      |
| `invalidate_contact_point`      | 020, 055, 098               |
| `set_primary_contact_point`     | 021–022, 074, 098           |
| `attach_account`                | 028–032, 063, 069, 073, 099 |
| `resolve_authenticated_contact` | 033–036, 004–011, 096       |
| `disable_account`               | 035, 037, 054, 070, 099     |
| `revoke_account`                | 036, 038, 054, 070, 099     |
| `detect_duplicate_contact`      | 039–041, 100                |
| `propose_merge`                 | 042–044, 043, 077, 100      |
| `merge_contacts`                | 045–066, 071, 075, 077, 100 |

---

# 27. Positive Verification Families

The B3 implementation must ultimately demonstrate positive scenarios covering at least:

```text
P-B3-01  retrieve existing Contact
P-B3-02  resolve uniquely matched Contact
P-B3-03  create authorized Contact
P-B3-04  attach ContactPoint
P-B3-05  accept valid verification assertion
P-B3-06  set valid primary ContactPoint
P-B3-07  attach external Account
P-B3-08  resolve via ACTIVE Account
P-B3-09  disable Account
P-B3-10  revoke Account
P-B3-11  detect plausible duplicate
P-B3-12  create directional merge proposal
P-B3-13  execute authorized merge
P-B3-14  preserve merged source
P-B3-15  preserve historical Account/ContactPoint context
P-B3-16  replay Account binding safely
P-B3-17  replay merge safely
P-B3-18  recover material provenance
```

This list is a **minimum verification family**, not yet a final test-plan numbering freeze.

---

# 28. Negative Verification Families

The B3 implementation must ultimately demonstrate rejection/non-mutation scenarios covering at least:

```text
N-B3-01  unknown Contact retrieval
N-B3-02  ambiguous resolution not guessed
N-B3-03  conflicting resolution not overwritten
N-B3-04  unresolved does not mutate
N-B3-05  execution failure not represented as epistemic outcome
N-B3-06  unauthorized Contact creation
N-B3-07  conflicting creation
N-B3-08  ContactPoint added without implicit verification
N-B3-09  invalid verification assertion
N-B3-10  verification assertion for wrong ContactPoint
N-B3-11  duplicate provider identity binding conflict
N-B3-12  PENDING Account not authoritative
N-B3-13  DISABLED Account not authoritative
N-B3-14  REVOKED Account not authoritative
N-B3-15  duplicate assessment cannot merge
N-B3-16  merge proposal cannot merge
N-B3-17  merge without authorization
N-B3-18  self merge
N-B3-19  wrong-direction merge authorization
N-B3-20  Account reconciliation conflict blocks merge
N-B3-21  ContactPoint reconciliation conflict blocks merge
N-B3-22  failed merge leaves no partial merge
N-B3-23  generic CRUD bypass absent
N-B3-24  authentication implementation absent
N-B3-25  Asset identity implementation absent
N-B3-26  Runner implementation absent
```

Again, these are requirement-derived verification families, not yet the final executable test specification.

---

# 29. Concurrency Verification Families

At minimum:

```text
C-B3-01 concurrent equivalent Contact creation
C-B3-02 concurrent incompatible provider binding
C-B3-03 concurrent primary ContactPoint selection
C-B3-04 concurrent merge on same source Contact
```

Required outcome:

> frozen B3 invariants survive concurrency.

The Requirement Matrix does not prescribe the mechanism.

---

# 30. Transaction Verification Families

At minimum:

```text
T-B3-01 Account binding failure leaves no false binding
T-B3-02 ContactPoint verification failure leaves no false VERIFIED state
T-B3-03 merge reconciliation failure rolls back identity-state mutation
T-B3-04 merge failure after intermediate operation leaves no misleading partial state
```

---

# 31. Traceability Verification Families

At minimum:

```text
TR-B3-01 Contact creation provenance recoverable
TR-B3-02 ContactPoint verification provenance recoverable
TR-B3-03 Account attachment provenance recoverable
TR-B3-04 merge proposal provenance recoverable
TR-B3-05 merge execution provenance recoverable
```

---

# 32. B3 acceptance evidence classes

For B3 to be accepted eventually, evidence must include at least:

```text
repository identity
candidate commit identity
canonical ancestry
B3 delta inspection

installation evidence
migration evidence if migrations exist
schema compatibility evidence

positive scenario evidence
negative scenario evidence
concurrency evidence
transaction evidence
provenance evidence

B1/B2 non-regression evidence
boundary-preservation evidence
gate-by-gate result
```

---

# 33. Requirement Matrix invariants

### RM-I01 — Frozen WHAT precedence

No requirement may contradict the frozen B3 WHAT.

### RM-I02 — No hidden new primitive

Requirements cannot create a 15th primitive.

### RM-I03 — No HOW capture

A requirement SHOULD specify observable obligation rather than implementation mechanism.

### RM-I04 — Testability

Every `MUST`/`MUST NOT` requirement must have a credible verification route.

### RM-I05 — Traceability

Every B3 acceptance scenario must trace back to one or more `REQ-B3-*`.

### RM-I06 — B2 preservation

Requirement refinement cannot silently weaken B2 invariants.

### RM-I07 — Failure semantics preserved

Domain states cannot collapse into generic execution errors.

### RM-I08 — Authority preserved

Requirement elaboration cannot reduce or collapse the frozen authority ladder.

---

# 34. Open requirement-resolution items

The matrix has transformed most frozen semantics into requirements, but four areas still require **requirement-level closure**, not WHAT reopening.

### RM-O01 — Related-object classification

For merge, the exact required classification must be finalized for:

```text
Accounts
ContactPoints
ContactAssetRelationships
CaseParticipants
ExternalReferences
```

using only:

```text
PRESERVE
REASSOCIATE
REJECT_CONFLICT
DEFER
```

---

### RM-O02 — Verification Assertion Minimum Contract

The matrix must eventually define the minimum admissible information required for a verification assertion without choosing a provider implementation.

---

### RM-O03 — Provenance Minimum Persistence Obligation

The matrix must determine what must be durably recoverable versus merely observable during execution.

It must not prescribe the storage technology unnecessarily.

---

### RM-O04 — Contact creation equivalence for idempotency/concurrency

The matrix must define the minimum semantic conditions under which two Contact-creation requests count as the "same logical creation" for requirements 067 and 072.

This may be narrower than general identity equivalence.

---

# 35. Requirement Matrix Challenge questions

Before v0 can be accepted, challenge at least:

1. Does every frozen primitive have sufficient requirements?
2. Does every frozen invariant map to at least one requirement?
3. Does every `MUST`/`MUST NOT` have a credible verification route?
4. Have any HOW decisions leaked into requirements?
5. Does any requirement reopen the WHAT?
6. Are merge-related requirements sufficiently determinate?
7. Are related-object classifications closed enough for implementation?
8. Are authority requirements testable without implementing RBAC inside B3?
9. Is verification assertion admissibility sufficiently specified?
10. Are idempotency semantics testable?
11. Are concurrency obligations testable?
12. Is provenance sufficiently testable?
13. Does the matrix preserve all B1/B2 non-regression obligations?
14. Can an implementation team act without inventing product semantics?
15. Can DevOps independently determine PASS/FAIL from the resulting build?

---

# 36. Current Requirement Matrix status

```text
REQ-B3 requirements defined:
  100

Frozen primitive operations covered:
  14 / 14

RMO families covered:
  20 / 20

Positive verification families:
  18

Negative verification families:
  26

Concurrency verification families:
  4

Transaction verification families:
  4

Traceability verification families:
  5

Requirement-level open items:
  4

WHAT reopening required:
  NO

Requirement Challenge required:
  YES
```

---

# 37. Governance status

```text
B3 WHAT
  FROZEN

B3 Requirement Matrix v0
  PRODUCED
  NOT YET ACCEPTED
  REQUIREMENT CHALLENGE REQUIRED

B3 Execution Mandate
  NOT AUTHORIZED FOR ISSUANCE YET

B3 implementation
  NOT AUTHORIZED
```

---

# 38. Final declaration

This matrix creates the first testable transformation of the frozen B3 WHAT.

It does **not** authorize implementation.

The next allowed transition is:

```text
B3 REQUIREMENT MATRIX v0
          ↓
REQUIREMENT CHALLENGE
          ↓
     ┌────┴────┐
     │         │
 REPAIR     ACCEPT
     │         │
     └────┐    │
          ▼    ▼
       RM v0.x
          ↓
REQUIREMENT MATRIX FROZEN
          ↓
B3 EXECUTION MANDATE
════════════════════════════
       BUILD BOUNDARY
════════════════════════════
          ↓
B3 IMPLEMENTATION
```

## END — CPL B3 Requirement Matrix v0

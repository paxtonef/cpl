# CPL — Next Build Unit WHAT v0

## 0. Purpose

This artifact determines the semantic identity and boundary of the next CPL Build Unit following:

```text
B4 CLOSED
    ↓
CPL Build Structuring v0
    ↓
CPL Build Structure Challenge v0
    ↓
NEXT_UNIT_IDENTIFIED
```

The Build Structure Challenge identified an ungoverned B2-era operational schema:

```text
Case
CaseParticipant
RunnerExecution
RunnerArtifact
CaseEvent
```

The purpose of this WHAT is to determine whether these objects form one Build Unit or multiple ordered Build Units, and to define the first admissible unit.

This artifact defines WHAT only.

It does not define requirements.

It does not authorize implementation.

---

# 1. Canonical baselines

Software baseline inherited from B4:

```text
1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628
```

B4 closure governance:

```text
313b5a6023090a17e0ae824204c2de28d8305dd6
```

Build Structuring / Challenge governance HEAD:

```text
6d19f8e1d0e7deb902dade80dd8d4b07e99bbcd7
```

---

# 2. Existing operational schema

The following objects already exist materially:

```text
Case
CaseParticipant
RunnerExecution
RunnerArtifact
CaseEvent
```

They were introduced as schema before B3/B4 governance work.

They are not new candidate tables.

The next Build Unit must govern existing structures rather than duplicate them.

---

# 3. Fundamental semantic split

The five objects do not belong to one undifferentiated concept.

They separate into two semantic families.

## 3.1 Case family

```text
Case
CaseParticipant
CaseEvent
```

This family represents a governed operational context.

A Case provides a durable frame within which:

* a problem,
* request,
* investigation,
* service interaction,
* diagnostic process,
* repair process,
* claim,
* or other bounded operational matter

may be represented.

A Case is not itself an execution.

A Case may exist before any RunnerExecution.

A Case may exist without any RunnerExecution.

A Case may contain zero, one, or multiple executions.

---

## 3.2 Execution family

```text
RunnerExecution
RunnerArtifact
```

This family represents governed execution activity performed within an operational context.

A RunnerExecution represents that a runner or governed execution system was invoked.

A RunnerArtifact represents a persisted output produced by or associated with that execution.

An execution is therefore subordinate to a Case context.

---

# 4. OSQ-01 — One Build Unit or two?

Resolution:

```text
TWO BUILD UNITS
```

The current five-object candidate must be split into:

```text
BU-1
Case Governance
    Case
    CaseParticipant
    CaseEvent

BU-2
Execution Governance
    RunnerExecution
    RunnerArtifact
```

Reason:

```text
Case can exist without RunnerExecution.

RunnerExecution is contextualized by Case.

Therefore:

Case Governance
    is structurally prior to
Execution Governance.
```

The split also prevents the next Build Unit from becoming an excessively broad "operational everything" layer.

---

# 5. Next Build Unit identity

The next admissible Build Unit is:

```text
CASE GOVERNANCE
```

Provisional identifier:

```text
CPL Case Governance
```

Only after freeze may it receive the next B-number.

---

# 6. Core object — Case

A `Case` is:

> A stable CPL operational context representing a bounded matter within which governed participation, assertions/events and later executions may occur.

A Case is not:

```text
world event
workflow engine
runner execution
domain truth
state machine
business process engine
generic project
generic ticket
```

---

# 7. Case identity

A Case possesses a stable CPL identity.

```text
Case identity
    ≠
domain matter
    ≠
external case identifier
    ≠
RunnerExecution
    ≠
CaseEvent
```

A Case remains identifiable across:

```text
status change
participant change
event accumulation
execution creation
correction
closure
historical reconstruction
```

---

# 8. Case and the world

A Case does not assert that a real-world event occurred.

It represents that CPL has opened or maintains an operational context concerning some matter.

Therefore:

```text
WORLD MATTER
    ≠
DOMAIN ASSERTION
    ≠
CPL CASE
```

Example:

```text
WORLD
vehicle may have a mechanical problem

DOMAIN
PGDR or technician reports a diagnosis

CPL
Case records the governed operational context
within which that diagnosis is handled
```

A Case never becomes proof that the underlying world condition exists.

---

# 9. Case scope

A Case may concern:

```text
Contact
Asset
both
```

The exact allowed anchoring must preserve existing B2 schema unless a later governed repair is required.

A Case may represent operational contexts such as:

```text
diagnostic case
repair case
claim case
service request
investigation
resolution process
```

The CPL does not own the domain semantics of those case types.

---

# 10. Case type

`case_type` is classification, not ontology.

It must not cause CPL to become a universal domain model.

Therefore:

```text
case_type
    identifies operational category

case_type
    does NOT make CPL authoritative
    over domain truth
```

The mechanism by which case types are admitted or validated belongs to requirements/HOW, not this WHAT.

---

# 11. Case lifecycle

Case lifecycle is CPL-governed operational state.

It is distinct from domain state.

Examples conceptually include:

```text
OPEN
ACTIVE
CLOSED
CANCELLED
```

but this WHAT does not freeze a specific enum unless inherited directly from the existing schema.

Invariant:

```text
CASE STATUS
    ≠
DOMAIN OBJECT STATUS
```

Closing a diagnostic Case does not mean:

```text
vehicle repaired
vehicle safe
vehicle operable
diagnosis true
```

It means only that the CPL operational context reached its governed terminal state.

---

# 12. Participation

`CaseParticipant` represents participation in a Case.

It is not a durable structural relationship.

Therefore:

```text
CaseParticipant
    ≠
ContactAssetRelationship
```

Examples:

```text
REQUESTER
TECHNICIAN
ADVISOR
CLAIMANT
REVIEWER
```

These are case-scoped capacities.

---

# 13. Participation boundary

A participant role does not itself imply authority.

```text
ROLE
    ≠
AUTHORITY
    ≠
PERMISSION
    ≠
IDENTITY
```

A Contact may participate in a Case without possessing authority to make every Case decision.

Case participation therefore records:

```text
who participates
and in what case-scoped capacity
```

not:

```text
what they are universally authorized to do
```

---

# 14. Participation temporal semantics

Case participation is temporally bounded by the Case.

Conceptually:

```text
joined_at
left_at
```

represent participation in the operational context.

They do not constitute a general valid-time claim about the external world.

Therefore:

```text
Case participation time
    ≠
B4 relationship valid time
```

---

# 15. CaseEvent

A `CaseEvent` is an append-oriented representation that something was reported, recorded or produced within the Case context.

It is not automatically a world event.

Core invariant:

```text
WORLD EVENT
    ≠
DOMAIN ASSERTION
    ≠
CASE EVENT
```

This distinction must become explicit and frozen.

---

# 16. Meaning of CaseEvent

A CaseEvent answers:

> What was recorded as occurring within the governed Case history?

It does not necessarily answer:

> What objectively occurred in the physical world?

Examples:

```text
DIAGNOSIS_REPORTED
DOCUMENT_RECEIVED
PARTICIPANT_ADDED
REPAIR_REPORTED_COMPLETE
CASE_REVIEW_REQUESTED
```

The exact event vocabulary remains outside this WHAT unless required by inherited schema constraints.

---

# 17. Event time

CaseEvent may possess something equivalent to:

```text
occurred_at
recorded_at / created_at
```

These concepts must not be silently conflated.

Conceptually:

```text
reported occurrence time
    ≠
CPL recording time
```

If only one currently exists in the B2 schema, requirements must determine whether the distinction requires extension.

The WHAT only establishes the semantic distinction.

---

# 18. Actor

Current B2 schema includes:

```text
actor_type
actor_reference_id
```

The Case Governance Build Unit does not introduce a generalized Actor object.

Instead:

```text
Actor reference
    identifies who/what is recorded as acting

AuthorityContext
    determines whether the action is authorized
```

These remain distinct.

---

# 19. OSQ-03 — actor_type

The existing closed actor categories must not automatically become permanent CPL ontology merely because they were introduced in B2.

Resolution:

```text
B2 SCHEMA CONSTRAINT
    ≠
FROZEN SEMANTIC INVARIANT
```

Therefore the next requirements process must evaluate the existing categories:

```text
CONTACT
SYSTEM
RUNNER
ADMIN
EXTERNAL_PARTY
```

against the Case Governance WHAT.

They may be retained if sufficient.

They may be repaired if insufficient.

But no generalized Actor hierarchy is authorized.

---

# 20. CaseEvent and execution

A CaseEvent may refer to a RunnerExecution.

However:

```text
CaseEvent
    can exist without RunnerExecution
```

Examples:

```text
human note recorded
external document received
participant added
case opened
case closed
```

Therefore CaseEvent belongs to Case Governance, not Execution Governance.

---

# 21. RunnerExecution exclusion

`RunnerExecution` is explicitly outside this Build Unit.

It belongs to the subsequent candidate Build Unit:

```text
Execution Governance
```

Case Governance may define the semantic boundary where future executions attach.

It must not govern RunnerExecution itself.

---

# 22. RunnerArtifact exclusion

`RunnerArtifact` is also excluded.

It belongs with RunnerExecution because its identity and lifecycle are execution-dependent.

Thus:

```text
RunnerExecution
      ↓
RunnerArtifact
```

remain together for the subsequent Build Unit.

---

# 23. OSQ-02 — parent_execution_id

Because `RunnerExecution` is not part of the current Build Unit, `parent_execution_id` is not resolved here.

It is transferred to the subsequent Execution Governance WHAT.

Provisional questions remain:

```text
retry lineage?
execution replacement?
execution derivation?
supersession?
re-execution chain?
```

No semantic interpretation is frozen by Case Governance.

---

# 24. Authority

Case operations must be governed.

At WHAT level, the system must distinguish:

```text
participant
actor
authority
canonical decision
```

A user being a CaseParticipant must never automatically authorize Case mutation.

Authority remains governed separately.

---

# 25. Canonical Case decisions

B3/B4 established a recurring governance pattern:

```text
request / assertion
      ↓
authority evaluation
      ↓
canonical decision
      ↓
effect
```

Case Governance must preserve that pattern where canonical Case mutation requires governance.

However, this WHAT does not yet specify the exact number or schema of decision objects.

It establishes only the invariant:

> Material Case lifecycle changes must not bypass CPL governance.

---

# 26. Decision vs event

A particularly important distinction:

```text
CaseEvent
    ≠
Canonical Case Decision
```

A CaseEvent records history.

A canonical decision authorizes or determines a CPL state transition.

An event must never acquire decision authority merely because it was recorded.

---

# 27. Event vs command

Similarly:

```text
request
    ≠
decision
    ≠
event
```

Example:

```text
request to close case
        ↓
canonical decision
        ↓
case becomes closed
        ↓
CASE_CLOSED event recorded
```

These must remain semantically distinguishable even if implementation later combines some storage paths.

---

# 28. Correction

Case history must be correctable without silent destruction.

The general B3/B4 principle carries forward:

```text
correction
    ≠
history deletion
```

A later governed correction must preserve enough provenance to reconstruct what was previously represented.

---

# 29. Supersession

Where a Case-level assertion or canonical decision becomes invalid or corrected:

```text
old representation
    → superseded

new representation
    → current
```

Historical trace must remain reconstructable.

This does not mean every CaseEvent requires supersession semantics.

The exact event correction model belongs to requirements.

---

# 30. Current vs historical navigation

Case Governance must support both:

```text
current operational view

and

historical reconstruction
```

These are distinct queries.

Examples:

```text
Who currently participates?
What was participation at time T?

What is current Case status?
What status history led here?
```

---

# 31. Idempotency

Material Case transitions must be idempotent under governed replay.

The WHAT establishes:

```text
same authorized operation replay
    must not silently create duplicate canonical transition
```

Payload similarity alone does not necessarily establish operation identity.

Detailed idempotency keys belong to requirements/HOW.

---

# 32. Domain boundary

Case Governance must not absorb domain logic.

Forbidden examples:

```text
CPL decides diagnosis validity
CPL determines vehicle operability
CPL determines whether repair succeeded
CPL determines insurance liability
```

Those remain domain determinations.

CPL governs their operational representation.

---

# 33. Anti-workflow boundary

Case Governance is not authorization for a generic workflow engine.

A Case may accumulate:

```text
participants
events
status changes
future executions
```

but CPL does not automatically define:

```text
arbitrary workflow DSL
BPMN engine
generic task scheduler
universal process automation
```

---

# 34. Anti-event-sourcing boundary

CaseEvent does not turn CPL into a universal event-sourcing architecture.

CaseEvent is a governed Case-history primitive.

It must not become:

```text
all system state = event replay
```

unless a future separate decision explicitly authorizes that architecture.

---

# 35. Object graph after this Build Unit

Conceptually:

```text
Contact
   │
   ├───────────────┐
   │               │
   ▼               ▼
CaseParticipant   Case
                    │
                    ├── CaseEvent
                    │
                    └── future RunnerExecution
                              │
                              └── RunnerArtifact

Asset
  │
  └───────────────► Case
```

Exact FK topology remains inherited from materialized schema and subject to requirements validation.

---

# 36. Dependency structure

The resulting build dependency becomes:

```text
B3 Identity
      │
      ▼
B4 Asset + Relationship
      │
      ▼
Case Governance
      │
      ▼
Execution Governance
      │
      ▼
VIR / PGDR / other domain integrations
```

This is the key structural result.

---

# 37. Next-next Build Unit

The subsequent candidate is provisionally:

```text
Execution Governance
```

covering:

```text
RunnerExecution
RunnerArtifact
```

It is NOT authorized for implementation.

Its WHAT is NOT yet authorized until Case Governance reaches the appropriate gate.

---

# 38. Explicit inclusions

The current Build Unit includes semantically:

```text
Case
CaseParticipant
CaseEvent

Case identity
Case lifecycle
Case authority boundaries
Case-scoped participation
Case history
Case event semantics
world/assertion/representation separation
correction principles
historical/current navigation
idempotent Case transitions
```

---

# 39. Explicit exclusions

The current Build Unit excludes:

```text
RunnerExecution governance
RunnerArtifact governance
VIR logic
PGDR logic
generic Occurrence table
generic Evidence primitive
generic Actor/Role model
Organization
Membership
generic State engine
generic workflow engine
generic event-sourcing platform
billing
frontend
authorization platform
```

---

# 40. Frozen candidate invariants

Candidate invariants for challenge:

```text
CG-CI01
A Case is a CPL operational context, not a world event.

CG-CI02
WORLD MATTER ≠ DOMAIN ASSERTION ≠ CPL CASE.

CG-CI03
Case identity is stable and distinct from domain identity.

CG-CI04
CaseParticipant ≠ ContactAssetRelationship.

CG-CI05
Role ≠ Authority ≠ Permission ≠ Identity.

CG-CI06
Participation is Case-scoped.

CG-CI07
CaseEvent ≠ world event.

CG-CI08
WORLD EVENT ≠ DOMAIN ASSERTION ≠ CASE EVENT.

CG-CI09
CaseEvent ≠ canonical Case decision.

CG-CI10
Request ≠ decision ≠ event.

CG-CI11
Case status ≠ domain object status.

CG-CI12
Case Governance must preserve current and historical views.

CG-CI13
Material Case transitions require governed authority.

CG-CI14
Governed replay must not create duplicate canonical transition.

CG-CI15
Correction must preserve reconstructable history.

CG-CI16
Case may exist without RunnerExecution.

CG-CI17
RunnerExecution is subordinate to Case context.

CG-CI18
RunnerExecution and RunnerArtifact belong to a later Build Unit.

CG-CI19
CPL must not acquire domain-truth authority through Case records.

CG-CI20
Case Governance must not become a generic workflow or event-sourcing engine.
```

---

# 41. Resolution of Build Structuring questions

```text
OSQ-01
One unit or two?

RESOLVED:
TWO.

1. Case Governance
2. Execution Governance


OSQ-02
Meaning of parent_execution_id?

DEFERRED:
belongs to Execution Governance WHAT.


OSQ-03
actor_type frozen or revisitable?

RESOLVED:
existing B2 schema is inherited implementation,
not automatically frozen ontology.

Its adequacy must be challenged during Case Governance requirements.
No generic Actor model is authorized.
```

---

# 42. Build Unit determination

```text
NEXT BUILD UNIT:

CPL CASE GOVERNANCE
```

Status:

```text
WHAT_DEFINED_v0
```

Not yet:

```text
WHAT_FROZEN
```

---

# 43. Next governance action

The next action is:

```text
CASE GOVERNANCE WHAT CHALLENGE v0
```

The challenge must attempt to falsify at least:

```text
1. the split Case Governance / Execution Governance
2. Case as operational context rather than generic workflow
3. CaseParticipant ≠ durable relationship
4. CaseEvent ≠ world event
5. CaseEvent ≠ decision
6. Case status ≠ domain state
7. whether existing B2 schema can satisfy these semantics
8. whether any hidden dependency requires RunnerExecution in the same unit
```

---

# 44. Final status

```text
BUILD STRUCTURE
  RESOLVED

NEXT BUILD UNIT
  CPL CASE GOVERNANCE

WHAT v0
  DEFINED

WHAT CHALLENGE
  REQUIRED

WHAT FREEZE
  NOT YET AUTHORIZED

REQUIREMENTS
  NOT AUTHORIZED

IMPLEMENTATION
  NOT AUTHORIZED

EXECUTION GOVERNANCE
  IDENTIFIED AS SUBSEQUENT CANDIDATE
  NOT YET AUTHORIZED
```

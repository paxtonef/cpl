# CPL — B3 Identity Resolution State & Decision Model v0

**System:** Common Product Layer — CPL
**Build Phase:** B3 — Identity + Accounts
**Artifact:** Identity Resolution State & Decision Model
**Version:** v0
**Canonical predecessor:** `B3_IDENTITY_OBJECT_AUTHORITY_MAP_v0.md`
**Canonical repository baseline:** `main` @ `1b98d65`

---

## 1. Purpose

This artifact defines the governed states, decisions and transitions by which CPL determines whether observed identity evidence can be associated with a persistent Contact.

It governs the transformation:

```text
Observed Identity Evidence
          ↓
Identity Resolution
          ↓
Resolution State
          ↓
Permitted Decision
          ↓
Controlled State Transition
```

It does not define authentication mechanisms, UI flows, provider-specific OAuth behavior, or implementation architecture.

Its purpose is to ensure that B3 never silently converts evidence into identity.

---

## 2. Fundamental distinction

CPL SHALL distinguish:

```text
OBSERVATION
    ≠
EVIDENCE
    ≠
RESOLUTION
    ≠
DECISION
    ≠
IDENTITY MUTATION
```

An email address, telephone number, external provider identifier or declared name may constitute evidence.

Evidence may support a resolution.

A resolution may support a decision.

Only an authorized decision may mutate CPL identity state.

Therefore:

```text
Evidence
   ↓
does not itself mutate
   ↓
Contact
```

---

## 3. Resolution object

Every governed resolution SHALL conceptually contain:

```text
Resolution
├── resolution_id
├── observed_evidence
├── candidate_contacts
├── evidence_assessment
├── resolution_state
├── decision
├── decision_authority
├── confidence / certainty representation
├── conflicts
├── provenance
├── created_at
└── resulting_action
```

This does not require B3 to create a new database table.

The structure defines the semantic object that the B3 service must reason over and expose through its contracts.

---

## 4. Canonical Resolution States

B3 SHALL distinguish at least the following states.

### 4.1 MATCHED

Meaning:

> Available evidence is sufficient under applicable policy to resolve the observation to one existing CPL Contact.

```text
Evidence
   ↓
exactly one admissible Contact
   ↓
MATCHED
```

MATCHED does not mean metaphysical certainty that two real-world persons are identical.

It means CPL possesses sufficient governed grounds to perform the association.

Possible consequences:

```text
return Contact
attach Account
attach ContactPoint
record additional evidence
```

subject to operation-specific authority.

### 4.2 NOT_FOUND

Meaning:

> No existing Contact satisfies the applicable resolution criteria.

It means:

> No admissible existing match found

not:

> This actor has never existed in CPL.

The distinction matters because evidence may be incomplete.

NOT_FOUND MAY permit Contact creation when the caller possesses creation authority.

It SHALL NOT automatically cause creation.

### 4.3 AMBIGUOUS

Meaning:

> More than one existing Contact remains a plausible admissible resolution.

Example:

```text
Evidence
   ↓
Contact A plausible
Contact B plausible
   ↓
AMBIGUOUS
```

Required behavior:

```text
DO NOT arbitrarily select one
DO NOT create another Contact merely to escape ambiguity
DO NOT merge candidates automatically
```

Possible actions:

```text
request additional evidence
return candidate set
escalate
defer resolution
```

### 4.4 CONFLICTING

Meaning:

> Available evidence supports mutually incompatible identity conclusions.

Example:

```text
provider account → Contact A
verified phone → Contact B
policy says both evidence sources are authoritative
```

This is not merely ambiguity.

In ambiguity: evidence is insufficient to choose.

In conflict: evidence actively points in incompatible directions.

A conflict SHALL block automatic identity mutation unless an explicit policy defines a safe resolution.

### 4.5 PROVISIONAL

Meaning:

> CPL has established a temporary resolution or Contact association that is permitted operationally but is not yet sufficiently established to be treated as fully resolved.

Typical case:

```text
new authenticated actor
+
no existing Contact
+
creation permitted
+
evidence insufficient for stronger identity conclusion
```

The system may therefore establish:

```text
PROVISIONAL Contact association
```

without pretending:

```text
identity conclusively resolved
```

A provisional state must be capable of later:

```text
confirmation
reconciliation
supersession
merge
rejection
```

### 4.6 UNRESOLVED

Meaning:

> CPL cannot currently reach an admissible resolution.

Unlike AMBIGUOUS or CONFLICTING, this state does not necessarily identify a specific reason beyond insufficient resolvability.

Examples:

```text
insufficient evidence
unsupported evidence type
resolution dependency unavailable
policy does not permit conclusion
```

It is the safe fallback state.

---

## 5. Why ERROR is not a Resolution State

The following must remain separate:

```text
UNRESOLVED
≠
ERROR
```

UNRESOLVED is a legitimate epistemic outcome.

ERROR means the resolution operation could not execute correctly.

For example:

```text
no sufficient evidence
→ UNRESOLVED

database unavailable
→ execution failure

invalid request
→ request rejection
```

Technical failure must never masquerade as an identity conclusion.

---

## 6. Resolution State Model

Canonical model:

```text
                       ┌───────────────┐
                       │   EVIDENCE    │
                       └───────┬───────┘
                               │
                               ▼
                       ┌───────────────┐
                       │  RESOLUTION   │
                       └───────┬───────┘
                               │
       ┌───────────┬───────────┼───────────┬────────────┐
       ▼           ▼           ▼           ▼            ▼
    MATCHED    NOT_FOUND   AMBIGUOUS   CONFLICTING   UNRESOLVED
       │           │
       │           └──────────────┐
       │                          ▼
       │                    PROVISIONAL
       │
       ▼
AUTHORIZED ACTION
```

This diagram represents possible outcomes, not mandatory temporal transitions between every state.

---

## 7. Decision Model

A resolution state and a decision are different objects.

For example:

```text
Resolution State = MATCHED
```

does not itself mean:

```text
attach_account = authorized
```

The decision layer must evaluate:

```text
Resolution State
+
Requested Operation
+
Caller Authority
+
Applicable Policy
+
Current Contact State
+
Evidence Provenance
+
Conflict State
```

and produce a decision.

---

## 8. Canonical Decisions

B3 SHALL support a decision vocabulary at least equivalent to:

```text
RETURN_MATCH
CREATE_CONTACT
CREATE_PROVISIONAL_CONTACT
ATTACH_ACCOUNT
ATTACH_CONTACT_POINT
VERIFY_CONTACT_POINT
REJECT_ASSOCIATION
REQUEST_ADDITIONAL_EVIDENCE
DEFER
ESCALATE
PROPOSE_MERGE
AUTHORIZE_MERGE
REJECT_MERGE
```

These are semantic decisions.

The later service contract may group or expose them differently.

---

## 9. State → Permitted Decision Matrix

| Resolution state | Automatic return | Contact creation | Account attachment | Merge |
|---|---|---|---|---|
| MATCHED | potentially | NO | potentially | NO |
| NOT_FOUND | NO | potentially | only following authorized creation/resolution | NO |
| AMBIGUOUS | NO | NO | NO | proposal only |
| CONFLICTING | NO | NO | NO | proposal/escalation only |
| PROVISIONAL | qualified | already provisional | policy-controlled | NO automatic merge |
| UNRESOLVED | NO | policy-dependent but normally NO | NO | NO |

"Potentially" means subject to authority and policy.

It does not mean automatic authorization.

---

## 10. Contact Creation Decision

Creation requires more than:

```text
NOT_FOUND
```

The actual condition is:

```text
NOT_FOUND
+
sufficient creation evidence
+
caller authorized to create
+
creation policy satisfied
+
no blocking conflict
=
CREATE_CONTACT permitted
```

Otherwise:

```text
NOT_FOUND
→ no mutation
```

This prevents `find_or_create_contact` from becoming an uncontrolled identity factory.

---

## 11. Authenticated Identity Resolution

Authentication provides evidence that:

> a provider has authenticated an identity according to that provider's mechanism.

It does not prove:

> which CPL Contact the identity belongs to.

Therefore:

```text
Authenticated Provider Identity
             ↓
          Account?
        /          \
      YES           NO
       ↓             ↓
Known Contact     Resolution
                     ↓
              MATCHED / NOT_FOUND /
              AMBIGUOUS / CONFLICTING /
              UNRESOLVED
```

An existing valid Account binding can provide strong CPL resolution evidence because CPL previously established that relation.

But the provider itself does not become CPL identity authority.

---

## 12. ContactPoint Resolution

A ContactPoint may participate in resolution only according to its state.

Conceptually:

```text
UNVERIFIED email
    ↓
weak / contextual evidence

VERIFIED email
    ↓
stronger evidence

REVOKED email
    ↓
historical evidence
    ≠ current identity authority
```

Verification strengthens an evidence claim.

It does not transform the ContactPoint into the Contact's identity.

---

## 13. Evidence Combination

B3 SHALL NOT assume:

```text
one evidence item
=
one identity decision
```

Resolution may combine evidence.

Conceptually:

```text
E1 + E2 + E3
      ↓
Evidence Assessment
      ↓
Resolution
```

Evidence may be:

```text
supporting
contradictory
redundant
stale
revoked
unverified
verified
provider-derived
CPL-derived
declared
historical
```

The Requirement Matrix must later determine which combinations B3 v1 actually implements.

---

## 14. Confidence

A numeric confidence score SHALL NOT independently authorize identity mutation.

Therefore:

```text
confidence = 0.99
```

does not mean:

```text
merge authorized
```

Confidence is evidence about resolution quality.

Authority is a governance property.

They must remain separate.

---

## 15. Ambiguity Rule

Canonical invariant:

> When CPL has multiple plausible Contacts and no authorized rule establishes a unique resolution, the correct result is AMBIGUOUS, not "best guess."

Therefore B3 SHALL NOT silently select:

```text
first result
highest database rank
most recently used Contact
lexicographically first Contact
highest probabilistic score alone
```

unless a future explicit policy authorizes a deterministic resolution rule and defines its evidentiary meaning.

---

## 16. Conflict Rule

Canonical invariant:

> Contradictory authoritative evidence must remain visible as conflict until a governed decision resolves it.

The implementation SHALL NOT eliminate conflict merely by overwriting one source with another.

---

## 17. Merge Candidate

Resolution may discover:

```text
Contact A
and
Contact B
likely represent the same actor
```

The resolution result is:

```text
PROPOSE_MERGE
```

not:

```text
MERGE
```

The distinction is mandatory.

---

## 18. Merge Authority

Merge requires a separate authority decision.

Conceptually:

```text
Duplicate Evidence
       ↓
Merge Candidate
       ↓
Evidence Review
       ↓
Merge Decision
     /       \
AUTHORIZE    REJECT
    ↓
Merge Transition
```

The merge operation must preserve the historical existence of the source Contact.

---

## 19. Merge State Transition

Authorized merge:

```text
SOURCE Contact
ACTIVE
   ↓
MERGED
   ↓
merged_into_id = TARGET
```

Target Contact remains the surviving identity.

The source SHALL NOT simply disappear.

Historical relationships must remain interpretable.

---

## 20. Merge Prohibitions

B3 SHALL NOT automatically merge Contacts solely because they share:

```text
name
email
telephone number
postal address
provider
organization
asset
IP address
device
```

Any of these may contribute evidence.

None independently establishes universal identity equivalence.

---

## 21. Idempotency

Identity mutation operations must be designed so that replay does not accidentally create duplicate identity state.

At minimum, B3 must later define idempotency semantics for:

```text
create_contact
attach_account
attach_contact_point
verify_contact_point
merge_contacts
```

Example:

```text
same provider + same provider_subject
```

must not create multiple active Accounts representing the same provider identity where B2 constraints already prohibit it.

---

## 22. Historical preservation

Identity resolution is temporally sensitive.

Something may be true at T1 and no longer true at T2.

Therefore B3 must preserve distinctions such as:

```text
currently verified
historically verified

currently active
historically active

currently associated
historically associated

current Contact
merged historical Contact
```

B3 SHALL NOT rewrite history merely to make the current state simpler.

---

## 23. Decision Provenance

A material identity decision must be explainable through at least:

```text
what was observed
what evidence was considered
which Contact candidates existed
what state was concluded
what decision was made
under which policy/authority
when it occurred
```

The implementation mechanism remains for later specification.

The semantic obligation belongs to B3 WHAT.

---

## 24. Caller Authority

Different callers may have different rights.

Conceptually:

```text
Caller A
→ may resolve Contact
→ may not create Contact

Caller B
→ may create provisional Contact
→ may not merge

Caller C
→ may authorize merge
```

Therefore service operations must not infer authority merely from possession of valid input.

---

## 25. Failure-safe principle

When B3 cannot establish that a mutation is authorized:

```text
NO MUTATION
```

is the default.

This applies particularly to:

```text
AMBIGUOUS
CONFLICTING
UNRESOLVED
insufficient authority
insufficient evidence
unsupported transition
```

---

## 26. Resolution determinism

Given:

```text
same persisted state
same evidence
same policy version
same authority context
```

B3 SHOULD produce the same resolution decision.

If external/non-deterministic reasoning is later introduced, its contribution must not silently become authoritative.

---

## 27. LLM Independence

B3 identity authority SHALL NOT depend on a particular LLM.

An LLM may later assist with:

```text
candidate discovery
normalization
similarity analysis
conflict explanation
merge proposal
```

but:

```text
LLM output
≠ identity authority
```

A weaker, local or future model must be replaceable without changing CPL's identity semantics.

---

## 28. Core invariants

**B3-IR-I01 — Evidence is not identity**
No individual observation automatically defines a Contact.

**B3-IR-I02 — Resolution precedes mutation**
Identity mutation requires an explicit resolution/decision path.

**B3-IR-I03 — Ambiguity remains ambiguity**
B3 does not hide unresolved multiplicity through arbitrary selection.

**B3-IR-I04 — Conflict remains visible**
Contradictory evidence is preserved until governed resolution.

**B3-IR-I05 — Authentication is evidence**
Authentication providers do not own CPL identity.

**B3-IR-I06 — Creation requires authority**
NOT_FOUND does not automatically create a Contact.

**B3-IR-I07 — Merge requires separate authority**
Duplicate detection and identity merge are distinct operations.

**B3-IR-I08 — Historical identity survives**
Merge, revocation and reassociation do not erase relevant historical state.

**B3-IR-I09 — Confidence is not authority**
Probabilistic confidence cannot independently authorize mutation.

**B3-IR-I10 — Safe non-decision**
When no authorized conclusion exists, CPL may return no identity decision.

**B3-IR-I11 — Execution failure is not epistemic uncertainty**
Technical errors must not be represented as NOT_FOUND, AMBIGUOUS, or UNRESOLVED.

**B3-IR-I12 — Model independence**
Identity semantics remain independent of the execution model used to assist resolution.

---

## 29. B3 v1 minimum resolution capability

B3 v1 should be considered functionally complete only if it can distinguish at minimum:

```text
Known actor
Unknown actor
Ambiguous actor
Conflicting evidence
Provisional identity
Unresolved identity
```

and can prevent unauthorized transitions between those situations.

---

## 30. What this artifact does NOT authorize

This document does not authorize implementation.

It does not freeze:

```text
API routes
Python class names
database additions
service architecture
confidence algorithms
provider integrations
UI
authentication implementation
```

Those remain downstream decisions.

---

## 31. Relationship to the next artifact

We now have:

```text
B3 Identity Object & Authority Map
          ↓
defines WHAT EXISTS
and WHO HAS AUTHORITY

B3 Identity Resolution State & Decision Model
          ↓
defines WHAT CAN BE CONCLUDED
and WHICH TRANSITIONS MAY FOLLOW
```

**End of `CPL — B3 Identity Resolution State & Decision Model v0`**

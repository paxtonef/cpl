# CPL — B4 Execution Mandate v0

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Execution Mandate
**Version:** v0
**Status:** ISSUED — BUILD BOUNDARY CROSSED
**Canonical baseline:** `main @ 2ec1e60`
**Frozen WHAT:** B4 WHAT = FROZEN
**Frozen Requirements:** `REQ-B4-001 → REQ-B4-260` = FROZEN
**Authorized implementation branch:** `b4-candidate`
**Implementation authorization:** YES — within this mandate only

---

## 1. Mandate purpose

This mandate authorizes implementation of B4 against the frozen B4 WHAT and frozen B4 Requirement Matrix.

The mandate does **not** reopen product semantics.

The implementation team MUST build the B4 candidate such that:

```text
Frozen WHAT
    +
Frozen Requirements
    +
Canonical baseline
    ↓
Governed B4 Build Execution
    ↓
Candidate implementation
    ↓
Tests + evidence
    ↓
Candidate SHA
    ↓
Independent verification
```

---

## 2. Canonical baseline

The mandatory build baseline is:

```text
Repository:
  paxtonef/cpl

Branch:
  main

Canonical SHA:
  2ec1e60
```

Development MUST start from this exact canonical repository state or an exact clone/export of it.

No uncertain sandbox baseline is permitted.

No overlay onto an unrelated repository state is permitted.

---

## 3. Baseline verification

Before implementation begins, the build system MUST verify:

```text
repository identity
branch identity
baseline SHA
working-tree cleanliness
origin synchronization
required governance artifacts
```

At minimum:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git rev-parse HEAD
git status
```

Expected:

```text
HEAD = 2ec1e60...
working tree = CLEAN
```

If the baseline differs unexpectedly:

```text
STOP
```

The build system MUST NOT silently adapt.

---

## 4. Authorized candidate branch

The authorized implementation branch is:

```text
b4-candidate
```

It MUST be created from:

```text
main @ 2ec1e60
```

The build system MUST preserve evidence of:

```text
candidate branch creation point
candidate baseline SHA
candidate final SHA
```

---

## 5. Frozen normative sources

Implementation authority derives from the following canonical chain.

### B4 WHAT

```text
B4_WHAT_GLOBAL_FREEZE_RE_CHALLENGE_v0.1.md
```

Result:

```text
FREEZE_ACCEPTED
```

### B4 Requirements

```text
B4_REQUIREMENT_MATRIX_v0.md
B4_REQUIREMENT_MATRIX_v0.1.md
B4_REQUIREMENT_MATRIX_RE_CHALLENGE_v0.1.md
```

Effective frozen requirement set:

```text
REQ-B4-001 → REQ-B4-260
```

Result:

```text
REQUIREMENTS_ACCEPTED
```

---

## 6. Normative precedence

If implementation interpretation conflicts with a frozen B4 requirement:

```text
frozen requirement governs
```

If a requirement appears to conflict with frozen WHAT:

```text
STOP
report WHAT/requirement conflict
```

Do not silently choose one interpretation.

If implementation convenience conflicts with frozen semantics:

```text
frozen semantics govern
```

---

## 7. Authorized implementation scope

B4 implementation may modify or add code necessary to implement:

```text
Asset continuity
AssetIdentifier lifecycle
AssetIdentityResolution persistence/consumption
CanonicalAssetIdentityDecision
Asset merge admission
Asset merge execution
Asset correction
survivor selection
dependency disposition
ExternalReference
DomainProjection
ContactAssetRelationship evolution
CanonicalRelationshipDecision
valid-time / decision-time semantics
endpoint canonical navigation
idempotency
conflict/cardinality governance
historical/current reconstruction
B4 outcome/failure semantics
```

Only work necessary to satisfy frozen B4 requirements is authorized.

---

## 8. Prohibited scope expansion

The implementation MUST NOT introduce or expand into:

```text
authorization engine
social graph
Contact–Contact relationships
Asset–Asset topology
VIR implementation
PGDR diagnostic logic
generic workflow engine
billing
frontend
CRM functionality
new domain ontology
new B5 functionality
```

unless directly required by an already-frozen B4 requirement.

---

## 9. Existing application baseline

Accepted B3 implementation remains canonical upstream behavior.

The build MUST preserve:

```text
B1 accepted behavior
B2 accepted behavior
B3 accepted behavior
```

No B4 implementation choice may regress accepted upstream behavior.

---

## 10. Database baseline

The accepted migration baseline is:

```text
021 (head)
```

B4 schema changes MUST be forward-only.

B4 MUST NOT rewrite or amend:

```text
001 → 021
```

Any B4 migration begins after `021`.

---

## 11. Migration authorization

B4 MAY add migrations required by the frozen requirements.

The number and decomposition of migrations are HOW decisions.

They MUST satisfy:

```text
forward-only evolution
clean upgrade from B3 accepted state
repeatable canonical installation
real PostgreSQL compatibility
```

---

## 12. Asset object requirements

Implementation MUST preserve Asset as a stable CPL identity distinct from:

```text
physical object
AssetIdentifier
ExternalReference
DomainProjection
```

No identifier may become canonical Asset identity merely through implementation convenience.

---

## 13. AssetIdentifier implementation boundary

Implementation MUST support the frozen lifecycle semantics:

```text
attach
current/applicable
supersede
invalidate
historical preservation
```

without requiring a specific status encoding.

Identifier equality MUST NOT auto-merge Assets.

---

## 14. AssetIdentityResolution boundary

Generic CPL MAY:

```text
request
consume
persist
retrieve
evaluate admissibility
```

for domain physical-identity resolutions.

Generic CPL MUST NOT become the producer of domain physical identity merely by implementing B4.

For automotive:

```text
VIR authority remains external to canonical CPL mutation
```

---

## 15. CanonicalAssetIdentityDecision

Implementation MUST provide durable governed representation for canonical Asset identity decisions.

A compliant representation MUST support at least:

```text
decision identity
affected Assets
supporting resolution
authority/provenance
decision time
canonical effect
supersession
```

Exact schema is not mandated.

---

## 16. Asset merge admission

Canonical merge execution MUST require:

```text
admissible positive physical identity determination
        +
CPL canonical admission
        +
survivor determinacy
        +
dependency-disposition closure
```

Only then may merge execute.

---

## 17. Mandatory no-merge states

The implementation MUST prevent merge under:

```text
AMBIGUOUS
CONTRADICTORY
UNRESOLVED
technical FAILED
unsafe dependency state
undetermined survivor
```

unless a previously unresolved governed condition has been legitimately resolved.

---

## 18. Survivor selection

Implementation MUST enforce the frozen precedence:

```text
1. existing governing canonical survivor
2. otherwise established canonical CPL Asset
3. override only through explicit governed rule
4. override provenance mandatory
5. domain resolver does not automatically select survivor
```

Implementation-order heuristics are prohibited.

---

## 19. Dependency disposition

Before canonical merge:

```text
every materially relevant dependency family
```

must have a governed disposition.

If not:

```text
HOLD or REJECT
```

The implementation MUST NOT use hidden generic reassignment as a fallback.

---

## 20. Canonical Asset correction

Implementation MUST support correction of an erroneous canonical Asset decision by supersession.

Correction MUST preserve:

```text
prior Asset identities
prior resolutions
prior canonical decisions
prior evidence
historical references
```

No destructive “pretend the merge never happened” rollback is permitted.

---

## 21. Canonical decision/effect consistency

For Asset canonical transitions:

```text
CanonicalAssetIdentityDecision
+
canonical Asset effect
```

must become observably committed consistently.

Partial successful canonical transition is prohibited.

---

## 22. Asset transition idempotency

Replay-equivalent:

```text
merge
correction
```

requests MUST NOT produce independent duplicate canonical transitions.

Idempotency identity MUST NOT be inferred solely from payload similarity.

---

## 23. ExternalReference

Implementation MUST distinguish:

```text
historical external target
```

from:

```text
current canonical navigation
```

after Asset merge/correction.

ExternalReference MUST NOT become Asset identity authority.

---

## 24. DomainProjection

Implementation MUST preserve:

```text
projection authority
projection history
Asset binding
```

while preventing DomainProjection from becoming canonical Asset identity.

Generic CPL MUST NOT adjudicate conflicting domain truth.

---

## 25. ContactAssetRelationship

Implementation MUST preserve ContactAssetRelationship as a stable governed object whose logical identity does not depend solely on current canonical endpoints.

The relationship must survive:

```text
Contact merge/correction
Asset merge/correction
```

without historical rewriting.

---

## 26. CanonicalRelationshipDecision

Material relationship changes MUST be governed through durable relationship decision semantics.

At minimum:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

must remain semantically distinguishable.

---

## 27. Relationship valid time / decision time

Implementation MUST preserve the frozen distinction:

```text
VALID TIME
≠
CPL DECISION TIME
```

No specific bitemporal architecture is mandated.

But acceptance evidence MUST demonstrate reconstruction of both where retroactive establishment/correction occurs.

---

## 28. Relationship authority

Implementation MUST preserve:

```text
evidence
≠ authority
```

and:

```text
Contact identity
≠ relationship truth
```

and:

```text
relationship truth
≠ authorization decision
```

---

## 29. Relationship type semantics

Implementation MUST support governed extensible relationship typing with identifiable semantic authority/context.

It MUST NOT require one universal closed cross-domain enum.

It MUST NOT accept uncontrolled arbitrary free-text as canonical semantics.

---

## 30. Cardinality and conflict

Generic CPL MUST apply applicable type/domain governance for:

```text
cardinality
compatibility
coexistence
conflict
```

No universal `one OWNER`, `one USER`, etc. rule may be invented.

---

## 31. Relationship transition idempotency

Replay-equivalent canonical relationship mutation requests MUST NOT produce independent duplicate transitions.

This applies to:

```text
ESTABLISH
END
CORRECT
SUPERSEDE
```

where applicable.

---

## 32. Relationship decision/effect consistency

Relationship canonical decision and resulting canonical relationship effect MUST become observably committed consistently.

No successful partial transition is permitted.

---

## 33. Historical/current navigation

Implementation MUST make both views verifiable where they differ:

```text
HISTORICAL ATTRIBUTION
CURRENT CANONICAL NAVIGATION
```

This applies at least to:

```text
ContactAssetRelationship
ExternalReference
Asset-dependent history
```

as governed by frozen requirements.

---

## 34. Outcome semantics

Implementation MUST preserve distinctions among:

```text
successful determination
governed non-resolution
governed rejection
technical failure
```

In particular:

```text
DB failure
≠ UNRESOLVED

network failure
≠ AMBIGUOUS

resolver crash
≠ NOT_FOUND
```

---

## 35. Required positive verification families

The candidate MUST include positive evidence for at least:

```text
Asset creation
identifier lifecycle
positive identity resolution consumption
canonical merge
governed survivor selection
Asset correction
ExternalReference preservation
DomainProjection behavior
relationship establishment
relationship END
relationship CORRECT
relationship SUPERSEDE
relationship current navigation
historical reconstruction
idempotent replay
```

---

## 36. Required negative verification families

The candidate MUST include negative evidence for at least:

```text
identifier equality does not auto-merge

AMBIGUOUS does not merge

CONTRADICTORY does not merge

UNRESOLVED does not merge

technical resolver failure does not merge

admin privilege does not bypass merge admission

domain resolver does not directly mutate canonical CPL identity

survivor cannot be selected by implementation convenience

merge cannot execute with unresolved material dependencies

relationship evidence does not bypass admission

relationship does not automatically grant authorization
```

---

## 37. Required correction verification

Candidate evidence MUST include at least one scenario where:

```text
Asset merge accepted
        ↓
later evidence contradicts merge
        ↓
canonical correction
        ↓
independent Assets restored
        ↓
prior decision/history preserved
```

---

## 38. Required temporal verification

Candidate evidence MUST include at least one scenario where:

```text
relationship valid at T1
decision recorded at T3
later correction at T5
valid-time interpretation changes
prior decision remains reconstructable
```

---

## 39. Required endpoint-evolution verification

Candidate evidence MUST include:

```text
historical Contact B ↔ Asset Y
```

followed by canonical endpoint evolution such that current navigation differs from historical attribution.

Both views MUST remain reconstructable.

---

## 40. Required dependency-disposition verification

Candidate evidence MUST demonstrate:

```text
positive physical identity
+
unresolved material dependency
→ HOLD / REJECT
```

and:

```text
all material dependencies safely dispositioned
→ merge may proceed
```

---

## 41. Required failure-consistency verification

Candidate tests MUST inject or simulate failure at a point capable of creating partial canonical transition and prove that the system does not expose:

```text
decision-only successful transition
```

or:

```text
canonical-effect-only successful transition
```

---

## 42. Real PostgreSQL requirement

B4 acceptance evidence MUST run against real PostgreSQL.

Mock-only database verification is insufficient for final acceptance.

---

## 43. Migration verification

Candidate verification MUST demonstrate:

```text
accepted B3 database state
        ↓
B4 migrations
        ↓
new B4 head
```

successfully.

No mutation of historical migrations `001–021` is permitted.

---

## 44. Full regression requirement

Candidate verification MUST execute:

```text
B1 regression
B2 regression
B3 regression
B4 tests
```

against the accepted environment.

Existing upstream tests MUST NOT be weakened to obtain PASS.

---

## 45. Health/readiness non-regression

Candidate MUST preserve:

```text
/health
/ready
```

including existing PostgreSQL readiness behavior.

---

## 46. Canonical build environment

The implementation system SHOULD use the repository's existing accepted environment unless a frozen requirement makes change necessary.

Any dependency addition or version change MUST be justified by B4 implementation need and reported in candidate evidence.

Unrelated dependency churn is prohibited.

---

## 47. Candidate completion condition

`b4-candidate` may be declared implementation-complete only when:

```text
all intended B4 code exists
all intended B4 migrations exist
all required B4 tests exist
full regression passes
real PostgreSQL verification passes
migration verification passes
working tree clean
candidate SHA recorded
```

---

## 48. Candidate SHA

The final candidate commit SHA MUST be immutable for independent verification.

The implementation system MUST report:

```text
B4_CANDIDATE_SHA=<actual SHA>
```

No verifier should be asked to verify “latest branch” without a pinned candidate SHA.

---

## 49. Candidate branch publication

The completed candidate MUST be made accessible to independent verification.

Preferred:

```text
push b4-candidate to github.com/paxtonef/cpl
```

If the coding environment cannot access GitHub, it MUST produce a valid transferable Git artifact such as:

```text
git bundle
```

from which the exact candidate branch/commit can be reconstructed.

---

## 50. Phantom-commit prohibition

A reported candidate SHA is not evidence that a candidate exists.

Candidate existence must be independently verifiable through:

```text
GitHub remote
or
valid Git bundle containing the commit
```

A SHA not materially retrievable is NOT an accepted candidate.

---

## 51. Candidate evidence package

The implementation handoff MUST report at minimum:

```text
repository
baseline SHA
branch
candidate SHA
files changed
migrations added
tests added
total tests executed
test result
PostgreSQL verification
migration head
working-tree state
known limitations
requirement coverage summary
```

---

## 52. Requirement traceability

The implementation MUST provide enough evidence to determine that:

```text
REQ-B4-001 → REQ-B4-260
```

have implementation and/or verification coverage as applicable.

This need not mean one test per requirement.

It means no requirement may silently disappear.

---

## 53. Deviations

If the implementation discovers that a frozen requirement cannot be implemented without changing normative meaning:

```text
STOP
```

Return a governance deviation.

Do not reinterpret the requirement in code.

---

## 54. Permitted implementation decisions

Developers retain authority over HOW decisions such as:

```text
module decomposition
class structure
function naming
schema decomposition
indexing
transaction mechanism
locking strategy
query strategy
test structure
internal abstraction
```

provided all frozen semantics and requirements remain satisfied.

---

## 55. Prohibited semantic invention

Developers MUST NOT invent:

```text
new merge authority
new survivor rule
new identifier authority
new resolver precedence
new relationship truth semantics
new authorization behavior
new history-rewrite policy
new canonical correction semantics
```

---

## 56. Independent verification

After candidate completion, verification MUST occur independently from the build claim.

The verifier must obtain the candidate from a retrievable source, preferably GitHub, and independently establish:

```text
candidate SHA
baseline ancestry
migration behavior
test results
PostgreSQL behavior
upstream non-regression
```

---

## 57. Verification is not implementation acceptance by assertion

The following is insufficient:

```text
developer says tests pass
```

The verifier must actually execute the required checks.

---

## 58. Verification outcome

Independent verification must return one of:

```text
ACCEPT_CANDIDATE

REPAIR_REQUIRED

VERIFICATION_BLOCKED
```

`ACCEPT_CANDIDATE` means the candidate satisfies the mandate based on evidence.

It does not itself close B4 until governance closure is materialized.

---

## 59. Repair loop

If verification returns:

```text
REPAIR_REQUIRED
```

repairs MUST remain bounded to verified defects.

The repaired candidate must receive a new candidate SHA.

The old failed candidate SHA remains historical evidence.

---

## 60. Integration rule

The candidate MUST NOT be merged into `main` merely because development reports completion.

Merge requires independent verification acceptance.

---

## 61. Main branch protection rule

Until acceptance:

```text
main
```

remains at the canonical governance baseline plus subsequent governance-only artifacts.

B4 implementation stays isolated on:

```text
b4-candidate
```

---

## 62. Post-verification merge

Only after independent candidate acceptance may governance authorize:

```text
b4-candidate
    ↓
main
```

The merge method should preserve verifiable candidate identity.

Fast-forward is preferred where ancestry permits it.

---

## 63. Closure condition

B4 may be declared closed only when:

```text
candidate accepted
candidate integrated into main
origin/main synchronized
full accepted evidence available
closure artifact materialized
```

---

## 64. B5 prohibition

No B5 implementation or WHAT work is authorized by this mandate.

B5 authorization requires explicit B4 closure governance.

---

## 65. Authorized Build Execution summary

```text
INPUT

Repository:
  paxtonef/cpl

Baseline:
  main @ 2ec1e60

Frozen WHAT:
  B4

Frozen Requirements:
  REQ-B4-001 → REQ-B4-260

        ↓

AUTHORIZED BUILD

Branch:
  b4-candidate

Scope:
  B4 only

        ↓

IMPLEMENTATION

code
migrations
tests
evidence

        ↓

CANDIDATE

pinned candidate SHA

        ↓

INDEPENDENT VERIFICATION

real PostgreSQL
migration verification
full regression
B4 verification

        ↓

ACCEPT / REPAIR
```

---

## 66. Build boundary

Upon canonical materialization of this Execution Mandate:

```text
B4 BUILD BOUNDARY = CROSSED
```

and:

```text
B4 implementation = AUTHORIZED
```

only within this mandate.

---

## 67. Governance status before materialization

```text
B4 WHAT
  = FROZEN

B4 Requirement Matrix
  = FROZEN

B4 Execution Mandate v0
  = PRODUCED
  = NOT YET CANONICALLY ISSUED

B4 Implementation
  = NOT YET AUTHORIZED
```

---

## 68. Governance status after materialization

After this exact artifact is committed to canonical `main`:

```text
B4 WHAT
  = FROZEN

B4 Requirement Matrix
  = FROZEN

B4 Execution Mandate
  = ISSUED

B4 Build Boundary
  = CROSSED

b4-candidate
  = AUTHORIZED

B4 Implementation
  = AUTHORIZED

B4 Acceptance
  = NOT GRANTED

B4 Closure
  = NOT GRANTED

B5
  = NOT AUTHORIZED
```

---

## 69. Dev handoff instruction

Once materialized, the developer/coding system receives:

```text
1. canonical repository:
   paxtonef/cpl

2. baseline:
   2ec1e60

3. this Execution Mandate

4. frozen B4 WHAT artifacts

5. frozen Requirement Matrix:
   REQ-B4-001 → 260

6. authorization:
   build b4-candidate only
```

It MUST NOT be told merely:

```text
implement B4
```

without the governed corpus.

---

## 70. Final mandate

```text
CPL B4 EXECUTION MANDATE v0
===========================

Canonical build baseline:
  main @ 2ec1e60

Frozen WHAT:
  YES

Frozen Requirements:
  REQ-B4-001 → REQ-B4-260

Authorized branch:
  b4-candidate

Migration baseline:
  021

Implementation scope:
  B4 ONLY

Real PostgreSQL verification:
  REQUIRED

Full B1/B2/B3 regression:
  REQUIRED

B4 verification:
  REQUIRED

Candidate SHA:
  REQUIRED

Independent verification:
  REQUIRED

Direct merge before verification:
  PROHIBITED

Semantic invention:
  PROHIBITED

B5:
  NOT AUTHORIZED

STATUS:
  READY FOR CANONICAL MATERIALIZATION
```

**END — CPL B4 Execution Mandate v0**

# CPL Build Structure Challenge v0

**Baseline inspected:** `1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628` (exact pinned software baseline, detached HEAD clone)
**Governance read through:** `313b5a6023090a17e0ae824204c2de28d8305dd6`
**Task type:** INVESTIGATION — no B5 implementation, migrations, code, or candidate branch created

---

## 1. Baseline inspected

```text
Repository:        paxtonef/cpl
Software baseline:  1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628
Migration head:      025
```

Inspection performed via `git checkout` of the exact SHA into a fresh clone, not a future or working branch.

---

## 2. Existing CPL primitives

| Primitive | Stable identity | Lifecycle | Authority boundary | Provenance | Valid time | Decision time | Current state | Historical reconstruction | Domain truth vs CPL representation |
|---|---|---|---|---|---|---|---|---|---|
| Contact | `contact_id` | ACTIVE/MERGED/... | AuthorityContext | — | — | — | via `merged_into_id` chain | yes | CPL canonical |
| Asset | `asset_id` | ACTIVE/MERGED/... | AuthorityContext | — | — | — | via `merged_into_id` chain | yes | CPL canonical |
| ContactAssetRelationship | `relationship_id`, independent of endpoints | ACTIVE/ENDED | AuthorityContext + evidence | `CanonicalRelationshipDecision.evidence` | `valid_from/valid_until` | `decided_at` | current row | via decision chain | CPL canonical (relationship *fact*, evidence domain-sourced) |
| AssetIdentifier | `asset_identifier_id` | OBSERVED/VERIFIED/SUPERSEDED/INVALIDATED/DISPUTED | — | `source` | — | — | non-superseded rows | yes | evidence only, never truth |
| ExternalReference | `external_reference_id` | CURRENT/SUPERSEDED/INVALIDATED | — | `reference_system` | — | — | current row | yes (historical target preserved) | external system's own record |
| DomainProjection | `projection_id` | ATTACHED/CURRENT/SUPERSEDED/HISTORICAL/DISPUTED | `domain_authority` field | `source_resolution_id` | — | — | current row(s) | yes | explicitly domain-owned |
| AssetIdentityResolution | `resolution_id` | terminal (RESOLVED/AMBIGUOUS/.../FAILED) | — | `resolver_type/version` | — | — | n/a (immutable record) | yes, via `supersedes_resolution_id` | domain-produced determination |
| CanonicalAssetIdentityDecision | `decision_id` | EXECUTED/HOLD/REJECTED | `authority_context` JSONB | `resolution_id` link | n/a | `decided_at` | n/a (immutable) | yes, via `supersedes_decision_id` | CPL canonical (governs, doesn't determine) |
| CanonicalRelationshipDecision | `decision_id` | EXECUTED/HOLD/REJECTED | `authority_context` JSONB | `evidence` JSONB | `valid_from/valid_until` | `decided_at` | n/a (immutable) | yes | CPL canonical |
| AuthorityContext | n/a (a checker, not a persisted object) | n/a | itself | n/a | n/a | n/a | n/a | n/a | pure authorization gate, reused unmodified since B3 |

This is a mature, internally consistent set. Every governed CPL object already follows the same skeleton: **stable identity → immutable decision/resolution record → supersession chain → current/historical navigation split**.

---

## 3. Existing occurrence-like structures

This is the central finding of this investigation.

Searching the actual codebase (not the abstract CPL vision) for event/occurrence/action-shaped structures surfaces **five tables that already exist, created in B2 (migrations `009`–`013`), and have never been touched by B3 or B4's governance work**:

```text
Case              (migration 009)
CaseParticipant   (migration 010)
RunnerExecution   (migration 011)
RunnerArtifact    (migration 012)
CaseEvent         (migration 013)
```

Inspection of each (`app/cpl/models/case*.py`, `runner_*.py`):

- **`RunnerExecution`** — `case_id`, `asset_id`, `runner_type`, `runner_version`, `execution_status` (`CREATED/QUEUED/RUNNING/COMPLETED/FAILED/BLOCKED/CANCELLED`), `parent_execution_id` (self-FK, for retries — exactly B4's supersession pattern one layer earlier), `initiated_by_contact_id`, `idempotency_key`. **This already is an "occurrence": a domain runner (VIR/PGDR) was invoked, in a context, with an outcome.**
- **`RunnerArtifact`** — `execution_id`, `artifact_type`, `payload` (JSONB), `content_hash`, `artifact_status` (`CREATED/VALIDATED/SUPERSEDED/REJECTED`), `supersedes_artifact_id` (self-FK). **This already is a persisted, versioned "evidence/result of an occurrence."**
- **`CaseEvent`** — `case_id`, `event_type`, `actor_type` (`CONTACT/SYSTEM/RUNNER/ADMIN/EXTERNAL_PARTY`), `actor_reference_id`, `execution_id`, `occurred_at`, `payload` (JSONB). **This already is a generic, append-only occurrence log with minimal actor typing.**
- **`CaseParticipant`** — `case_id`, `contact_id`, `participant_role` (free text, e.g. `REQUESTER`), `participant_status`. **This already is a role-based participation record, structurally distinct from `ContactAssetRelationship`.**
- **`Case`** — the grouping/context object tying the above together, with its own status lifecycle.

Separately, `app/cpl/identity/evidence.py` (B3) defines `Evidence`/`EmailEvidence`/`PhoneEvidence`/`ProviderAccountEvidence` — but these are **ephemeral Python dataclasses**, never persisted, consumed transiently as input to the resolution engine and then discarded once a resolution/decision is recorded. B3 already demonstrates a working precedent: *evidence does not need to be a canonical persisted CPL object to support governed resolution.*

**Critical qualifier:** none of `Case`/`RunnerExecution`/`RunnerArtifact`/`CaseEvent`/`CaseParticipant` has *any* governance layer. Confirmed by search: no service-layer code outside `app/cpl/models/` references them except one passing comment in `reconciliation.py`. No `AuthorityContext` gate, no idempotency enforcement in code (the `idempotency_key` column on `RunnerExecution` is unused), no canonical-decision object, no correction/supersession *service*, no current/historical navigation helper. Existing tests only perform bare ORM inserts to prove the B2 schema shape (`tests/integration/test_b2_positive.py`).

**This changes the shape of the investigation.** The proposed "Occurrence + Participation" primitive is not something CPL lacks a *schema* for — it is something CPL lacks *governance* for, on tables that have sat unbuilt-upon since B2.

---

## 4. Occurrence hypothesis challenge

Testing the ten mandated scenarios against the existing schema:

| Scenario | Maps onto existing structure without distortion? |
|---|---|
| Vehicle inspection | `RunnerExecution(runner_type=PGDR)` + `RunnerArtifact(artifact_type=INSPECTION_REPORT)` — yes |
| Diagnosis | `RunnerExecution` + `RunnerArtifact(artifact_type=DIAGNOSTIC_RESULT)` — yes |
| Repair | `Case(case_type=REPAIR)` + `CaseEvent(event_type=REPAIR_COMPLETED)` — yes, with `CaseParticipant(role=TECHNICIAN)` |
| Ownership transfer | Already fully covered by B4's `CanonicalRelationshipDecision` (END + ESTABLISH pair) — **does not need Occurrence at all** |
| Registration event | `CaseEvent` or `RunnerArtifact` depending on whether a runner produced it — yes |
| Insurance claim | `Case(case_type=CLAIM)` + `CaseParticipant` (claimant, adjuster) + `CaseEvent` sequence — yes |
| Maintenance | Same shape as repair — yes |
| Asset identity resolution | Already fully governed by B4 (`AssetIdentityResolution`) — **does not need Occurrence** |
| Asset merge | Already fully governed by B4 (`CanonicalAssetIdentityDecision`) — **does not need Occurrence** |
| Asset correction | Already fully governed by B4 — **does not need Occurrence** |

**Conclusion:** a *freshly invented* generic `Occurrence` primitive would be substantially redundant with `RunnerExecution` + `CaseEvent`, which already exist. The genuine gap is not ontological absence — it is **governance absence** on existing schema. Building a brand-new `Occurrence` table alongside an already-existing, structurally near-identical `RunnerExecution`/`CaseEvent` pair would itself violate the anti-overgeneralization gate (Phase 14): it would produce two competing "things that happen" primitives in the same system.

`Occurrence` as a *governance layer over the existing Case/RunnerExecution/RunnerArtifact/CaseEvent schema* survives the challenge. `Occurrence` as a *new schema object* does not — it is unnecessary.

---

## 5. Participation hypothesis challenge

- `Contact OWNS Asset` — durable, structural, correctly modeled by `ContactAssetRelationship` (as B4 built it).
- `Garage PERFORMS Repair` / `Vehicle SUBJECT_OF Repair` / `Alice REQUESTS Repair` — these are not durable structural facts about two canonical objects; they are roles held *within a bounded Case/RunnerExecution*, with a start/end tied to that Case's lifecycle, not an independent valid-time interval of their own.

`CaseParticipant` already exists and already encodes exactly this shape: `case_id` + `contact_id` + `participant_role` + `joined_at`/`left_at`. Attempting to force `Garage PERFORMS Repair` into `ContactAssetRelationship` would require either (a) inventing a `relationship_type` for every conceivable participation role, polluting the durable-relationship type space with transient case-scoped roles, or (b) generalizing `ContactAssetRelationship` into `GenericEverythingRelationship`, which §12 of the Build Structuring hypothesis (and B4's own scope boundary) explicitly prohibits.

**Explicit answers:**
- Is Participation a new primitive? **No** — it already exists as `CaseParticipant`, ungoverned.
- Is it merely a role on Occurrence? **Yes**, in the sense that it is scoped to `Case`/`RunnerExecution`, not independent.
- Is it a relationship subtype? **No** — confirmed structurally distinct (own table, own status lifecycle, no `relationship_type` overlap).
- Does it require Actor/Role first? **No** — `participant_role` is a plain text field, exactly mirroring how `AssetIdentifier.identifier_type` and `relationship_type` are handled elsewhere in CPL (governed extensible typing, no universal enum). See §7.
- Does it require different temporal boundaries than B4 relationships? **Yes** — `joined_at`/`left_at` are case-scoped, not independent valid-time claims about the world; this is a smaller, simpler temporal model than B4's relationship valid-time/decision-time split, and evidence suggests it does not need to be as elaborate.

---

## 6. HBS-Q01 — Evidence dependency

Two working precedents already coexist in the codebase:

**Model A (Occurrence first, Evidence as enrichment)** — already validated by B3's `evidence.py`: identity resolution consumes ephemeral `Evidence` objects and persists only the *outcome* (`AssetIdentityResolution`), never the evidence itself as a standalone canonical object.

**Model B (Evidence required first)** — already validated by `RunnerArtifact`: a `RunnerExecution` occurrence is not considered meaningful without at least one `RunnerArtifact` (the schema ties artifacts to `execution_id`, not the reverse), and the artifact itself is the versioned, supersedable evidentiary payload.

These are not actually in conflict — they answer different questions. B3 shows that *transient input* evidence need not be canonical. `RunnerArtifact` shows that *produced/output* evidence of an occurrence should be canonical, versioned, and supersedable — exactly like every other B3/B4 decision object.

**Conclusion:** a minimal canonical Occurrence (governed `RunnerExecution`) **can** exist without inventing a *new, generalized* Evidence primitive, because a schema-level artifact/evidence object (`RunnerArtifact`) already exists and already follows the established supersession pattern. **HBS-Q01 answer: NO new generalized Evidence primitive is required as a hard prerequisite.** Governing `RunnerArtifact` alongside `RunnerExecution` in the same increment is a soft dependency (they are naturally built together), not a blocking one.

---

## 7. HBS-Q02 — Actor/Role dependency

`CaseEvent.actor_type` is a closed enum (`CONTACT/SYSTEM/RUNNER/ADMIN/EXTERNAL_PARTY`) — a minimal, already-frozen-in-schema actor *category* distinction. `CaseParticipant.participant_role` is free text — exactly the same governed-extensible-typing pattern B4 already uses for `relationship_type` and `AssetIdentifier.identifier_type` (no universal closed enum, no arbitrary uncontrolled free text either — see B4's `REQ-B4-117/118` precedent).

Testing the six mandated actor scenarios against this existing shape:
- Person acting personally → `actor_type=CONTACT`, `actor_reference_id=contact_id`
- Person acting for organization → `actor_type=CONTACT` + `participant_role` describing the capacity (no Organization primitive needed yet, since none of B1–B4 requires one — see §10)
- Garage acting as repair provider → `actor_type=CONTACT` (or `EXTERNAL_PARTY` if unregistered) + `participant_role=REPAIR_PROVIDER`
- System acting as domain resolver → `actor_type=RUNNER`, tied to `execution_id`
- Administrator acting under CPL authority → `actor_type=ADMIN`
- Automated service recording an assertion → `actor_type=SYSTEM`

All six map cleanly onto the existing `actor_type` + `participant_role` + `AuthorityContext` combination, exactly as B4 combined `relationship_type` + `AuthorityContext` without a generalized Role model.

**Distinctions preserved (per mandate):**
- Identity = `Contact`/`Asset`/system identity (already governed)
- Role = `participant_role` / `actor_type` (schema-level, extensible, not identity)
- Authority = `AuthorityContext` (a distinct, orthogonal checker — a Contact can hold a role without holding the authority to act on it)
- Permission = not yet modeled anywhere in CPL (out of scope, unchanged)
- Relationship = `ContactAssetRelationship` (durable, cross-Case)
- Participation = `CaseParticipant` (Case-scoped, transient)

**Conclusion — HBS-Q02 answer:** Participation can be governed **without** first introducing a generalized Actor/Role model. The existing minimal `actor_type` enum + free-text `participant_role` pattern is sufficient, mirroring B4's own resolved position on relationship typing. A full Actor/Role primitive is a **soft/optional** future enrichment, not a hard prerequisite.

---

## 8. HBS-Q03 — World / Assertion / CPL Representation

Applying the three-layer test to each mandated scenario, using the actual schema fields available:

**Inspection**
- WORLD: the vehicle was physically inspected
- DOMAIN ASSERTION: PGDR (or a human inspector) asserts inspection findings
- CPL REPRESENTATION: `RunnerExecution` (that an inspection *was invoked/performed*) + `RunnerArtifact` (the asserted findings, as opaque domain payload)

**Diagnosis** — identical shape, `artifact_type=DIAGNOSTIC_RESULT`.

**Repair**
- WORLD: repair physically occurred
- DOMAIN: garage asserts repair occurred, with what was done
- CPL: `CaseEvent`/`RunnerArtifact` recording that assertion, `CaseParticipant(role=TECHNICIAN)` recording who

**Ownership transfer** — already resolved by B4: CPL represents the *canonical relationship decision* (`CanonicalRelationshipDecision` type `END`+`ESTABLISH`), never the world fact of a handshake or paperwork signing itself.

**Determination:** In every case, the existing schema (`RunnerExecution`/`RunnerArtifact`/`CaseEvent`) already represents **the domain assertion**, not the world event directly — the tables never claim "X happened," only "runner Y produced payload Z" or "actor A reported event type B at time T." This is structurally identical to B4's own resolved boundary: `AssetIdentityResolution` represents that VIR *determined* same-physical-asset, not that the vehicles *are* physically identical as an independent CPL truth-claim.

**This is the single most important finding of this investigation:** CPL's existing pattern already answers HBS-Q03 correctly by construction, and it did so *before* B4 — B2's schema design (unknowingly or not) already kept WORLD and CPL REPRESENTATION separate. The risk the hypothesis worried about — "Occurrence = thing that happened" making CPL authoritative over reality — is avoidable by simply **not deviating from the pattern already present**: any future WHAT must define `RunnerExecution`/`CaseEvent` explicitly as *governed records of domain assertions*, never as world-fact assertions themselves, exactly as B4-CI04/05 did for physical identity.

**Flag for future WHAT:** the current `RunnerExecution`/`CaseEvent` schema has no explicit invariant *stating* this boundary (unlike B4, which has it as a frozen, named principle). Any WHAT built on these tables must state it explicitly rather than relying on it being implicit in the column names.

---

## 9. State dependency analysis

- **Mileage, operability, registration status, repair status** — these are domain truth values. The existing `DomainProjection.payload` (JSONB, domain-owned) and `RunnerArtifact.payload` (JSONB, execution-scoped) are both already-governed containers capable of holding these without CPL needing to understand their internal shape.
- **CPL canonical state** that *does* need to exist: `execution_status` on `RunnerExecution`, `artifact_status` on `RunnerArtifact`, `case_status` on `Case` — all already present, all already following the B3/B4 status-lifecycle pattern (a closed, small, CPL-governed enum, distinct from domain-payload content).
- **Derived state** (e.g. "is this vehicle currently operable") is not represented anywhere and does not need to be — it can be computed by a domain consumer from the latest `RunnerArtifact`/`DomainProjection` payload without CPL owning a derivation engine.

**Conclusion:** no generic `State`/`StateTransition` primitive is required, **before or after** governing Occurrence. The B4 invariant (`DOMAIN DETERMINES DOMAIN TRUTH; CPL GOVERNS CANONICAL REPRESENTATION`) is sufficient, applied the same way it already was to `DomainProjection`. **`State` is REJECTED as a structural candidate at this time**, consistent with §5 of the Build Structuring hypothesis.

---

## 10. Organization / Account dependency analysis

- **Account** — already exists (`app/cpl/models/account.py`, migration `004`) and is **already governed**: referenced by `app/cpl/identity/accounts.py`, `resolution.py`, and `reconciliation.py` since B3. It is a 1:1 auth-provider link on `Contact` (`auth_provider` + `provider_subject_id`), not an organizational-membership concept. **Not a gap** — already built, already integrated, out of scope for this investigation.
- **Organization** — does not exist anywhere in the schema (no table, no model, no migration). No current primitive (`Case`, `RunnerExecution`, `ContactAssetRelationship`) has any foreign key or field suggesting it is blocked without one.
- **Membership** — does not exist; same conclusion.
- **User** — conflated historically with `Contact`+`Account` per the B1 handoff manifest's own product-identity boundary discussion; already resolved by B3, not a gap.
- **Role** — addressed in §7; exists at the minimal schema-attribute level already, not as a blocking prerequisite.

**Conclusion:** none of Organization/Membership/Account/User/Role is a structural prerequisite for the next Build Unit. Account is already built. The others are either already-adequate minimal attributes (Role) or genuinely absent but **not required by any current dependency** (Organization/Membership) — they are independent future Build Units or application/domain concerns, not CPL-primitive priorities now.

---

## 11. Remaining primitive candidates

Revised node set, based on evidence rather than the original hypothesis's assumed abstractions:

```text
Occurrence-Governance   (govern existing Case/RunnerExecution/RunnerArtifact/CaseEvent)
Participation-Governance (govern existing CaseParticipant)
Evidence                (NOT required as new primitive — RunnerArtifact suffices)
Actor/Role              (NOT required as new primitive — actor_type + participant_role suffice)
State                   (REJECTED — no primitive needed)
Organization/Account    (Account already built; Organization not currently required)
```

The candidate list collapses substantially once actual schema evidence is applied. What remains is narrower than the original hypothesis proposed.

---

## 12. Dependency graph

```text
B3 Identity ──┐
              ├──► B4 Asset/Relationship ──► Occurrence-Governance
              │         (Case, RunnerExecution, RunnerArtifact,
              │          CaseEvent, CaseParticipant already exist
              │          as B2 schema; this unit adds authority,
              │          idempotency, canonical decisions,
              │          correction/supersession, navigation —
              │          the same governance pattern as B3→B4)
              │
              └──► (no other primitive currently blocks Occurrence-Governance)

Evidence (RunnerArtifact)     — SOFT dependency of Occurrence-Governance (naturally co-built, not blocking)
Actor/Role (actor_type field) — SOFT dependency (already present at minimal fidelity)
State                          — NOT a dependency (rejected as unnecessary)
Organization                   — NOT a dependency (no current edge requires it)
```

**Edges:**
- `Occurrence-Governance requires B4 Asset/Relationship` — because `RunnerExecution.asset_id` and `Case.asset_id` are foreign keys into the B4-governed Asset table; a `RunnerExecution` must reference a canonically-governed Asset to be meaningful.
- `Occurrence-Governance requires B3 Identity` — because `Case.primary_contact_id`/`CaseParticipant.contact_id` reference canonically-governed Contacts.
- `Occurrence-Governance does NOT require a new Evidence primitive` — `RunnerArtifact` already exists at adequate fidelity (HARD: none; SOFT: co-build recommended).
- `Occurrence-Governance does NOT require a new Actor/Role primitive` — `actor_type`/`participant_role` already exist at adequate fidelity (HARD: none; SOFT: none currently identified).
- `State does NOT depend on or block Occurrence-Governance` — orthogonal, deferred indefinitely pending future evidence.
- `Organization does NOT depend on or block Occurrence-Governance` — no current edge.

---

## 13. Hard dependencies

```text
Occurrence-Governance → B3 Identity (Contact)
Occurrence-Governance → B4 Asset/Relationship (Asset)
```

No other hard dependency was found for the leading candidate.

---

## 14. Soft dependencies

```text
Occurrence-Governance ~ RunnerArtifact governance (natural co-build, not blocking — could ship in a later increment)
Occurrence-Governance ~ minimal actor_type validation (natural co-build, already schema-present)
```

---

## 15. Rejected structural candidates

```text
new "Occurrence" TABLE (as opposed to governing the existing RunnerExecution/CaseEvent) — REJECTED, redundant
new generalized "Evidence" primitive — REJECTED as a hard prerequisite, RunnerArtifact suffices
new generalized "Actor/Role" primitive — REJECTED as a hard prerequisite, existing attributes suffice
generic "State"/"StateTransition" engine — REJECTED, violates DOMAIN DETERMINES DOMAIN TRUTH
"GenericEverythingRelationship" — REJECTED, explicitly prohibited by B4 precedent
Organization/Membership ecosystem — REJECTED as a current prerequisite (no dependency edge found)
VIR / PGDR implementation — REJECTED, out of CPL-primitive scope entirely (domain logic)
```

---

## 16. Next Build Unit determination

```text
NEXT_UNIT_IDENTIFIED
```

**Unit:** Governance of the existing `Case` / `RunnerExecution` / `RunnerArtifact` / `CaseEvent` / `CaseParticipant` schema — applying the same governance pattern B3 applied to `Contact` and B4 applied to `Asset`/`ContactAssetRelationship`: authority boundaries, idempotency, canonical decision objects, correction/supersession, current/historical navigation.

**Why required now:** these five tables have existed since B2 (before B3 even began) with zero governance. They are the only remaining major schema surface in the entire repository with no B3/B4-equivalent governance layer. Every dependency they have (`Contact`, `Asset`) is already satisfied by frozen, closed B3/B4 work. No other investigated candidate (Evidence, Actor/Role, State, Organization) has evidence of being a genuine blocking prerequisite — each was either already adequately present or has no dependency edge pointing to it from the current frontier.

**What it depends on:** B3 Identity (`Contact`), B4 Asset/Relationship (`Asset`) — both closed and frozen.

**What depends on it:** any future domain-runner integration (VIR, PGDR) needs a governed `RunnerExecution`/`RunnerArtifact` to record its invocations and outputs; any future Evidence or Actor/Role enrichment would attach to this governed layer rather than to raw B2 schema.

**Why competing candidates cannot precede it:** Evidence and Actor/Role are not independent Build Units at all under current evidence — they are properties this same unit should decide how to represent (using what already exists), not separate prerequisite units. State and Organization have no dependency edge from the current frontier and are not required by anything currently blocked.

**What it explicitly excludes:** VIR/PGDR domain logic, a generic State engine, a generic Evidence object beyond `RunnerArtifact`, a generic Actor/Role object beyond `actor_type`/`participant_role`, Organization/Membership.

---

## 17. Explicit exclusions

```text
NOT VIR implementation
NOT PGDR implementation
NOT a new Occurrence table (govern the existing RunnerExecution/CaseEvent instead)
NOT a new generalized Evidence object
NOT a new generalized Actor/Role object
NOT a generic State/StateTransition engine
NOT Organization/Membership
NOT a universal authorization engine
NOT frontend, billing, or workflow-engine work
```

---

## 18. Open structural questions

```text
OSQ-01
Should Case/RunnerExecution/CaseEvent governance ship as one Build Unit,
or split into (a) RunnerExecution+RunnerArtifact and (b) Case+CaseParticipant+
CaseEvent as two smaller units? Both depend only on already-closed B3/B4 work,
so this is a sequencing choice, not a dependency question — deferred to WHAT.

OSQ-02
Does RunnerExecution's existing self-referential parent_execution_id
(for retries) need the same "survivor selection"-style precedence
rules B4 needed for Asset merge, or is a simpler linear retry chain
sufficient? Requires WHAT-level analysis, not resolvable by inspection alone.

OSQ-03
CaseEvent.actor_type is a closed enum baked into the B2 schema
(CONTACT/SYSTEM/RUNNER/ADMIN/EXTERNAL_PARTY). Should the next WHAT treat
this as frozen (inherited B2 constraint) or revisit it as part of
governance? This investigation deliberately did not decide this.
```

---

## 19. Governance conflicts discovered

**None.** No frozen B1–B4 WHAT or requirement is contradicted by the findings above. The recommendation to govern existing tables rather than invent new ones is a HOW/scope observation, not a semantic conflict with anything frozen.

One **observation, not a conflict**: the original Build Structuring hypothesis (document 16) proposed inventing `Occurrence` as a new primitive without having inspected whether one already existed in the materialized schema. This investigation's principal contribution is exactly that inspection — the hypothesis's underlying instinct (something occurrence-shaped is the next gap) is confirmed; its proposed implementation path (build it fresh) is not, given what already exists.

---

## 20. Final status

```text
CPL_BUILD_STRUCTURE_CHALLENGE_v0

Occurrence hypothesis:
  SURVIVES, IN REVISED FORM
  (govern existing Case/RunnerExecution/RunnerArtifact/CaseEvent,
   do not build a new table)

Participation hypothesis:
  SURVIVES, IN REVISED FORM
  (govern existing CaseParticipant, do not build a new table)

HBS-Q01 (Evidence dependency):
  RESOLVED — NOT a hard prerequisite; RunnerArtifact already suffices

HBS-Q02 (Actor/Role dependency):
  RESOLVED — NOT a hard prerequisite; existing actor_type/participant_role suffice

HBS-Q03 (World/Assertion/Representation boundary):
  RESOLVED — existing schema already keeps CPL representation distinct from
  world/domain assertion; future WHAT must state this explicitly as a
  named invariant, as B4 did

State:
  REJECTED as a structural candidate

Organization/Account:
  Account already governed (not a gap); Organization NOT currently required

FINAL STATUS:
  NEXT_UNIT_IDENTIFIED

Next unit:
  Governance of existing Case / RunnerExecution / RunnerArtifact /
  CaseEvent / CaseParticipant schema (B2-era, currently ungoverned)

Next action:
  A WHAT process for this unit may now begin, informed by this
  investigation — including OSQ-01..03 as open questions the WHAT
  must resolve, not this investigation.
```

**STOP.** No B5 WHAT, no requirements, no migrations, no production code, no candidate branch were created by this investigation.

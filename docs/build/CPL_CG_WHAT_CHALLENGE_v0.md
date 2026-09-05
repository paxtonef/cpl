# CPL_CG_WHAT_CHALLENGE_v0

**CG = Case Governance candidate. v0 = revision of this challenge.**
**Naming convention (per governance decision on this artifact): pre-admission artifacts use `CPL_CG_...`; only if this WHAT survives and is subsequently frozen does the unit become `B5` and later artifacts become `B5_CASE_GOVERNANCE_...`. This artifact stays `CPL_CG_...` regardless of verdict, since a repair verdict does not constitute admission.**

---

## 1. Baselines inspected

```text
Governance baseline (challenged artifact commit): d3e1a88
Software baseline (actual schema inspected):      1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628
```

Inspection performed via detached-HEAD checkout of the exact software SHA, cross-referenced against `docs/build/CPL_NEXT_BUILD_UNIT_WHAT_v0.md` at `d3e1a88`.

---

## 2. Candidate WHAT inspected

`CPL_NEXT_BUILD_UNIT_WHAT_v0.md` — proposes splitting the five-object B2-era operational schema into `Case Governance` (Case, CaseParticipant, CaseEvent) followed by `Execution Governance` (RunnerExecution, RunnerArtifact), with Case Governance as the next admissible Build Unit.

---

## 3. Case primitive challenge (CQ1, CQ2)

**CQ1 — genuinely common, or automotive residue?**

The `Case` table's own fields (`primary_contact_id`, `asset_id`, `domain`, `case_type`, `case_status`) contain no automotive-specific vocabulary — `case_status`'s CHECK constraint (`OPEN/IN_PROGRESS/WAITING_FOR_USER/WAITING_FOR_EXTERNAL_INFORMATION/RESOLVED/CLOSED/REOPENED/CANCELLED`) is domain-neutral and reads like a generic support/service-case lifecycle, not a vehicle-diagnostic one. `case_type` is unconstrained free text (confirmed: no CHECK constraint on this column). Tested against VIR/PGDR/repair/insurance-claim/consulting-service-request, the *concept* — a bounded matter, opened by/about a Contact, tracked to a governed terminal state, with participants and a history — transfers without distortion to all of them, and plausibly to non-automotive CPL consumers (a support case, a consulting engagement) as well.

**However:** `asset_id` is `NOT NULL`. A pure consulting engagement with no physical/canonical Asset involved (e.g., "Alice requests financial advice") **cannot** be represented by the current schema without inventing a placeholder Asset. This is a genuine constraint failure for full domain generality — see §14 (Asset anchoring).

**Verdict:** Case survives as a genuine CPL-common concept. The current schema's mandatory-Asset constraint is automotive/VIR-PGDR residue and is flagged as a required repair target (not a rejection of the concept itself).

**CQ2 — Case vs Matter/Engagement/Work Item.**

"Case" does carry legal/support-ticket connotations that could bias future requirement authors toward those specific domains. However, this challenge finds no evidence that the *semantics* defined in the candidate WHAT (§6–§11) actually require legal-case or ticket-specific behavior — the WHAT itself explicitly disclaims "legal case," "support ticket," etc. as unintended readings (§6 of the WHAT). Renaming the physical table is out of this challenge's authorized scope (no schema repair authorized). The distinction the WHAT should make explicit: **the canonical ontology name in future governance prose need not be identical to the physical `cases` table name.** This is a documentation gap, not a structural one.

**Finding:** flag as WHAT gap (§22), not blocking.

---

## 4. Case/Execution split challenge (CQ3, CQ4)

**CQ3 — does Case exist independently?**

Confirmed from schema: `Case` has no FK pointing *to* `RunnerExecution` as a requirement of Case's own creation — a `Case` row can be inserted with zero executions (verified: `RunnerExecution.case_id` is the only link, and it points the other direction). `RunnerExecution.case_id` is `NOT NULL` — **the schema does not merely permit but structurally requires every RunnerExecution to belong to exactly one Case.** There is no path for "Execution → optional Case" or "Execution → multiple Cases" in the current schema. This is stronger evidence for the ordering than the candidate WHAT itself claimed (the WHAT asserted it as a design principle; the schema already enforces it as a hard constraint).

**CQ4 — is this a semantic dependency, or just a database FK?**

This is correctly flagged by the challenge mandate as the major gate, and the candidate WHAT's own reasoning (§4 of the WHAT: "RunnerExecution references Case" → "Case Governance is structurally prior") **conflates schema dependency with build-order dependency without justifying the inference.** A FK constraint alone only proves you cannot physically insert a `RunnerExecution` row before its `Case` row exists — it says nothing about whether the *governance layer* (authority, canonical decisions, idempotency, correction) for Case must be *built and frozen* before Execution Governance's own governance layer can be built. In principle, Execution Governance could add authority/idempotency/decision objects on top of `RunnerExecution`/`RunnerArtifact` while `Case` remains raw, ungoverned B2 schema — the FK would still be satisfiable by inserting raw `Case` rows without any governance around them.

**So does a genuine (non-schema) dependency exist?** Yes — but for a different reason than the WHAT gave, and it comes from §5's finding below: `Case.current_execution_id` and `CaseEvent.execution_id`. **Case's own "current state" navigation already depends on Execution semantics being meaningful** (see §5). That is a real governance dependency, not a database artifact. The WHAT's stated justification is therefore **methodologically wrong even though its conclusion is directionally right** — this is exactly the kind of "reusable pattern treated as automatic ontology" the anti-copy gate (§27 of the mandate) exists to catch, applied here to a dependency-reasoning shortcut rather than a governance-pattern copy.

**Verdict on CQ4:** schema dependency ≠ semantic dependency, confirmed as distinct. A genuine (but narrower and differently-justified) governance dependency does exist — see §5.

---

## 5. Dependency-type analysis / Intermediate-state admissibility (CQ5, CQ21, CQ22, CQ23)

**This is the central finding of this challenge.**

`Case` carries `current_execution_id` (nullable FK into `runner_executions`), added in migration `016` — the *same migration, same pattern* as `Asset.current_identity_resolution_id`. This is not incidental: migration `016` establishes "current-state pointer" as a deliberate, uniform B2-wide architectural convention, later formalized by B3 (`Contact`) and B4 (`Asset`) governance. Its presence on `Case` means **Case's own concept of "current state" was designed from B2 onward to include "which execution currently governs this Case's operational status."**

Separately, `CaseEvent.execution_id` (nullable) allows any recorded Case event to be attributed to a specific execution.

**Testing CQ5's five sub-questions directly:**

- *Can governed Case reference ungoverned execution?* — Structurally yes (nullable FK, no constraint violated), but semantically this means a "governed" Case's own `current_execution_id` pointer would reference a row with no authority boundary, no idempotency, no canonical-decision trail, and no correction/supersession semantics. A Case Governance implementation that claims full current/historical navigation (CG-CI12) cannot honestly claim it while one of its own "current state" fields points into ungoverned territory.
- *Can CaseEvent reference ungoverned RunnerExecution?* — Same answer, same problem, for history reconstruction specifically.
- *Can authority decisions cross the boundary?* — Not under the current WHAT's design (Case Governance does not touch RunnerExecution at all), which is exactly why this is a problem: nothing *governs* what happens when `current_execution_id` needs to change.
- *Can historical reconstruction cross the boundary?* — Partially: the Case-side row (which execution was "current" at a point) is reconstructable from Case's own decision trail, but the *content* of that execution (was it corrected? superseded? retried?) is not reconstructable without Execution Governance existing.
- *Can Case lifecycle depend on execution outcome?* — The schema makes this structurally plausible (a Case's status could reasonably move to `RESOLVED` because its current execution completed), but the candidate WHAT explicitly refuses to specify this (§11/§25 of the WHAT correctly defer it) — leaving an open question about whether `case_status` transitions are *allowed* to be triggered by raw, ungoverned execution status changes during the intermediate period.

**CQ21 (Execution exclusion verdict):**

```text
EXECUTION_EXCLUSION_REQUIRES_REPAIR
```

Not `INVALID` — Case genuinely can be created, participated in, and have events recorded without any RunnerExecution ever existing, so full inclusion of RunnerExecution in this Build Unit is not required. But not `VALID` as currently written either — the WHAT must explicitly scope `current_execution_id` and `CaseEvent.execution_id` as **opaque, execution-governance-owned pointers that Case Governance persists but does not interpret, mutate the meaning of, or claim current/historical navigation authority over**, until Execution Governance exists. This must become an explicit invariant, not an implicit gap.

**CQ22 (Artifact exclusion verdict):**

```text
ARTIFACT_EXCLUSION_VALID
```

No field on `Case`, `CaseParticipant`, or `CaseEvent` references `RunnerArtifact` directly (`RunnerArtifact` only links to `RunnerExecution.execution_id`). Case-level history and participation are fully meaningful without any artifact object existing. Artifact exclusion survives cleanly — this is a materially different (and better-founded) situation than the execution-pointer coupling above.

**CQ23 (Intermediate-state admissibility):**

```text
INTERMEDIATE_STATE_ADMISSIBLE_WITH_BOUNDARY
```

The intermediate state (Case governed, Execution ungoverned) is admissible **only if** the repair in CQ21 is made explicit: Case Governance requirements must state that `current_execution_id`/`CaseEvent.execution_id` are carried but not semantically owned by this Build Unit, and that no Case Governance operation may be gated on, or claim to fully reconstruct, execution-side state. Without that explicit boundary statement, the intermediate state would silently expose a governance bypass (a "governed" Case whose current-state pointer is unenforceable).

---

## 6. CaseParticipant challenge (CQ6, CQ7)

**CQ6.** Testing each role:

| Role | Durable relationship? | Case participation? | Both? |
|---|---|---|---|
| owner | Yes — already `ContactAssetRelationship` (B4) | No | — |
| driver | Plausibly durable (`ContactAssetRelationship`) | Also plausibly case-scoped (e.g. "driver at time of incident") | **Both, non-duplicative** — see below |
| requester | No | Yes | — |
| technician | No (rarely durable) | Yes | — |
| advisor | No (rarely durable) | Yes | — |
| reviewer | No | Yes | — |
| claimant | Sometimes (`owner` may equal `claimant`) | Yes | Possible, non-duplicative |
| repair provider | Could be durable if a repeat garage relationship exists | Yes, at minimum | Possible |

The "both" cases (driver, claimant, repair provider) do **not** create duplication of authority or truth, because they answer different questions at different scopes: `ContactAssetRelationship` answers "is this durable and true across Cases," while `CaseParticipant` answers "who is involved in *this* bounded matter, in what capacity." A Contact can simultaneously be the durable `OWNER` (B4 relationship) and the case-scoped `CLAIMANT` (this Case) without contradiction — these are genuinely orthogonal facts, not two representations of the same fact.

**Verdict:** `CaseParticipant ≠ ContactAssetRelationship` **survives**. No evidence of forced duplication found.

**CQ7.** `participant_role` (free text) is best classified as **classification/capacity**, not authority claim or domain assertion — it records "in what capacity this Contact is recorded as involved," structurally identical to how B4 treats `relationship_type` (governed-extensible, no universal enum, no automatic authorization implication — CG-CI05 already states this correctly). CPL can govern participation without owning universal role semantics, exactly as it already governs relationship types without owning universal relationship semantics. This mirrors an already-validated B4 precedent and is **not** an anti-copy violation, because the *underlying justification* (extensible typing without CPL becoming domain-authoritative) applies independently to Case, not merely by analogy.

---

## 7. CaseEvent challenge (CQ8, CQ9, CQ10)

**CQ8.** Classifying the six example event types:

| Event | Classification |
|---|---|
| CASE_OPENED | CPL event (pure governance fact) |
| PARTICIPANT_ADDED | CPL event (pure governance fact) |
| DOCUMENT_RECEIVED | Technical/CPL event (receipt is a CPL-observable fact; document *content* is domain) |
| DIAGNOSIS_REPORTED | Domain assertion, CPL-recorded |
| REPAIR_REPORTED_COMPLETE | Domain assertion, CPL-recorded (explicitly *reported*, not *verified*) |
| CASE_CLOSED | Canonical-decision consequence (should follow from a decision, not be independently assertable) |

A single `CaseEvent` table **can** safely represent all these classes structurally (same columns suffice: `event_type`, `actor_type`, `payload`), but the WHAT must make the *classification itself* — not just the storage shape — an explicit part of governance, or future implementers will silently blur "CPL fact" and "domain assertion" inside undifferentiated `payload` JSONB. This is not a structural failure, but it is a real WHAT gap (§22).

**CQ9.** Testing the four-representation chain (request → decision → status change → event):

```text
request close
    ↓
decision close
    ↓
Case.status = CLOSED
    ↓
CASE_CLOSED event
```

All four are **not** independently necessary for every transition — for low-stakes transitions (e.g. `PARTICIPANT_ADDED`) a request/decision pair is unnecessary bureaucracy; the WHAT's own §26/§27 already anticipates this by not mandating decision-gating for every event. But for **status-bearing transitions** (open→closed, closed→reopened), collapsing decision and event risks exactly the B3/B4-identified failure mode: an event recorded without a corresponding governed decision could later be misread as having *authorized* the transition it merely describes. No semantic duplication or conflicting-history risk was found **provided** the WHAT keeps the discipline: decision authorizes, event narrates. This distinction **survives** but is fragile — it depends entirely on discipline not yet specified as a requirement (correctly deferred, per the WHAT's own scope).

**CQ10.** Testing the WORLD/DOMAIN ASSERTION/CASE EVENT boundary against five scenarios — all five (vehicle repaired, vehicle inspected, claim submitted, document received, user requested service) decompose cleanly using the existing `actor_type` + `payload` shape: CPL never needs to independently verify or assert the world-fact, it only needs to record who claimed it and what was recorded. No scenario was found where `CaseEvent` would be forced to become authoritative world truth **provided the WHAT's own invariant (CG-CI07/CG-CI08) is honored strictly** — the risk is entirely in future implementation discipline, not in the current schema or WHAT text. **Boundary survives.**

---

## 8. World/Assertion/Representation challenge (CQ10, continued)

See §7 above — folded together since CQ10 was addressed as a single analysis. No additional failure found beyond what is documented there.

---

## 9. Event/Decision challenge

See §7, CQ9. No additional finding beyond the fragility noted there (discipline-dependent, not structurally enforced — flagged as a requirement-stage concern, not a WHAT-stage defect).

---

## 10. Case lifecycle challenge (CQ11, CQ12, CQ13)

**CQ11.** The actual `case_status` CHECK constraint values (`OPEN/IN_PROGRESS/WAITING_FOR_USER/WAITING_FOR_EXTERNAL_INFORMATION/RESOLVED/CLOSED/REOPENED/CANCELLED`) contain **no domain-truth-laden values** — no `REPAIRED`, `SAFE`, `DIAGNOSED`, `ELIGIBLE`, `APPROVED` exist in the frozen B2 enum. This is a clean pass: **Case status ≠ domain state survives**, and moreover the existing schema already enforces this boundary by construction, not merely by WHAT-level aspiration.

**CQ12.** Classifying lifecycle transitions:

```text
create, activate  → likely require canonical governance (material creation/state entry)
suspend, close, cancel, reopen → likely require canonical governance (material terminal/near-terminal transitions)
correct → requires canonical governance by B3/B4 precedent
merge, supersede → UNRESOLVED — see CQ13
```

The WHAT is correct to avoid mechanically importing B4's full identity-resolution machinery (survivor precedence, dependency-disposition closure) — nothing in Case's structure suggests two Cases require *physical identity resolution* the way two Assets might. A lighter-weight decision pattern (request → authority check → decision → effect, without survivor/dependency-disposition machinery) is adequate evidence-wise. **Anti-copy finding:** the WHAT's §25 already shows awareness of this ("this WHAT does not yet specify... It establishes only the invariant") — a correct, restrained position, not a violation.

**CQ13.** Testing whether two independently created Cases could later be found to concern the same matter (e.g., two service requests about the same recurring vehicle issue): this is **plausible and not addressed anywhere in the candidate WHAT.** The WHAT states "may exist without RunnerExecution" and similar existence claims but never addresses Case-to-Case consolidation. This is a genuine, unflagged gap.

**Finding:** Case merge/consolidation is a **real WHAT gap**, correctly left undesigned per the mandate's instruction ("do not design the mechanism"), but it must be explicitly named as an open question in the WHAT rather than silently absent. Flagged in §22 below.

---

## 11. Case correction/history challenge (CQ14, CQ15)

**CQ14.** Distinguishing correction types:

```text
correct Case metadata (title, case_type)     → CPL-owned, low-stakes
correct participant record                    → CPL-owned (who/what capacity is a CPL fact)
correct CaseEvent                              → CPL-owned (the record of what was reported)
reverse an erroneous Case transition           → CPL-owned, B3/B4-pattern correction (supersession, not deletion)
correct a domain assertion (e.g. "diagnosis was wrong") → NOT CPL-owned; CPL may record that a *new* CaseEvent supersedes an old one's *reported content*, but CPL never adjudicates whether the diagnosis itself was medically/mechanically correct
```

This split is coherent and consistent with the B4 precedent (CPL corrects its own representations, never domain truth). No failure found.

**CQ15.** Testing historical reconstruction scenarios: participant joins/leaves (supported by `joined_at`/`left_at`, already in schema), status changes (requires a decision/event trail not yet present as schema — currently only `case_status`'s *current* value exists, with no history table), incorrect event corrected (no `supersedes_event_id`-style column currently exists on `CaseEvent`, unlike `RunnerArtifact.supersedes_artifact_id`), Case reopened (`REOPENED` status exists, but no explicit link back to what was reopened or why), domain assertion superseded (no schema support currently), execution later attached (`current_execution_id` already supports this, per §5).

**Finding:** the current B2 schema is **missing supersession/correction infrastructure** for `Case` and `CaseEvent` that `RunnerArtifact` already has (`supersedes_artifact_id`). This is expected — B2 predates any governance pattern — but it means Case Governance's requirements phase will need **new schema** (a decision object, at minimum), not merely new service-layer code over existing columns, unlike some of B4's lighter-weight additions. This is a legitimate scope observation, not a WHAT defect, since the WHAT correctly defers exact schema to requirements (§25, §29 of the WHAT).

---

## 12. Actor challenge (CQ16 / WHAT's OSQ-03)

Testing the seven scenarios against the existing five-value `actor_type` enum (`CONTACT/SYSTEM/RUNNER/ADMIN/EXTERNAL_PARTY`):

| Scenario | Fits existing enum? |
|---|---|
| organization | No clean fit — not a Contact, not obviously EXTERNAL_PARTY |
| external professional | Plausibly `EXTERNAL_PARTY`, acceptable stretch |
| government authority | Plausibly `EXTERNAL_PARTY`, acceptable stretch |
| another CPL service | Plausibly `SYSTEM`, acceptable |
| AI system | Ambiguous between `SYSTEM` and `RUNNER` — no clean fit |
| human acting for organization | Fits `CONTACT` for identity, but the "for organization" capacity has no representation anywhere (echoes §10 of the Build Structuring investigation: Organization does not exist) |
| anonymous/external source | Plausibly `EXTERNAL_PARTY`, acceptable |

**Verdict:** `actor_type` is **repairable, not sufficient as-is and not unnecessary**. Three of seven test scenarios (organization, AI system, human-acting-for-organization) do not map cleanly. This does **not** require a generalized Actor/Role ontology (no evidence any scenario needs *authority* or *role hierarchy* semantics beyond classification) — it requires the existing enum's value set to be revisited during requirements, consistent with the WHAT's own correct framing that "B2 schema constraint ≠ frozen semantic invariant" (§19 of the WHAT). This finding **confirms and sharpens** OSQ-03's resolution rather than overturning it.

---

## 13. Asset anchoring challenge (CQ17)

As established in §3 (CQ1) and confirmed structurally: `Case.asset_id` is `NOT NULL`. Testing "non-Asset Cases" (e.g., a pure Contact-only consulting engagement, a claim not tied to a specific vehicle) shows the schema **cannot currently represent them** without an artificial Asset row.

This directly matches the discrepancy the prior turn's materialization already flagged (§9 of the WHAT vs. actual schema). This challenge confirms it is real and material: **B4 Asset is currently a hard schema dependency for Case creation, not merely "an available anchor" as the WHAT's §9 implies by listing "Contact / Asset / both" as options.** Today there is no "Contact-only" option. This **may alter the Build Structure graph** in the sense that Case Governance's dependency on B4 is *stronger* than the WHAT states (mandatory, not optional), even though the WHAT's overall dependency ordering (`B4 → Case Governance`) is not wrong — it is simply not *softened* the way §9's phrasing suggests.

**This is a required repair**, not a rejection: the WHAT must either (a) state plainly that Case currently requires both Contact and Asset and treat "Asset-optional Case" as an explicit future schema-repair candidate, or (b) commit to that schema repair as in-scope for this Build Unit's requirements phase.

---

## 14. Domain-neutrality challenge (CQ18)

Searching for VIR/PGDR-specific coupling in the Case-family schema:

- `Case.asset_id NOT NULL` — **automotive residue** (already flagged, §13)
- `case_status` enum — clean, domain-neutral (§10)
- `case_type` — unconstrained free text, domain-neutral
- `CaseParticipant.participant_role` — unconstrained free text, domain-neutral
- `CaseEvent.actor_type` — domain-neutral categories, though incomplete (§12)
- `Case.domain` field (`Text, NOT NULL`) — this is itself a domain-tag field (values like `"AUTOMOTIVE"` seen in existing B2 tests), which is **appropriately generic infrastructure** (mirrors `Asset.asset_domain` from B4) rather than a coupling — it exists precisely to let non-automotive domains coexist, which is evidence *for* domain neutrality, not against it.

**Verdict:** one confirmed automotive coupling (`asset_id NOT NULL`), everything else domain-neutral or explicitly designed for multi-domain use. This is a **bounded, already-identified failure**, not a systemic one — it does not constitute "Case Governance is secretly automotive" in the broad sense, but it is a real, required repair.

---

## 15. Workflow/event-sourcing contamination challenge (CQ19, CQ20)

**CQ19.** Testing whether Case requires ordered steps, task dependencies, a transition graph, assigned work, deadlines, workflow conditions, or automation triggers: **none of these exist in the current schema**, and the candidate WHAT explicitly disclaims them (§33). No evidence found that Case Governance's minimal semantics (identity, status, participants, events) require workflow machinery to function. **Boundary holds.**

**CQ20.** Testing whether historical reconstruction requires replaying all `CaseEvent`s to derive current `Case` state: **no** — `Case.case_status` is itself the authoritative current-state column (not derived from event replay), and `CaseEvent` is explicitly a *log*, not the state-derivation mechanism, consistent with WHAT §34. Event-sourcing contamination is **not present** and the WHAT correctly names the boundary. No repair needed.

---

## 16. Execution exclusion verdict

See §5. Restated:

```text
EXECUTION_EXCLUSION_REQUIRES_REPAIR
```

## 17. Artifact exclusion verdict

See §5. Restated:

```text
ARTIFACT_EXCLUSION_VALID
```

---

## 18. Build Unit cohesion/minimality (CQ24, CQ25)

**CQ24.** `Case`, `CaseParticipant`, `CaseEvent` share: a common authority boundary (all governed by the same eventual Case-scoped `AuthorityContext` usage), a common lifecycle dependency (participants and events are meaningless without an existing Case), and a common verification boundary (any acceptance test for "Case Governance works" naturally exercises all three together). **Sufficient cohesion found** — no evidence supports further splitting these three.

**CQ25.** Testing removability: `CaseEvent` could theoretically be deferred (a Case with only status + participants would still be minimally meaningful), but the WHAT's own invariant CG-CI12 (current/historical navigation) and CG-CI15 (correction must preserve reconstructable history) both **require** some history mechanism — without `CaseEvent`, there is no way to reconstruct "what led to this Case's current state" at all, which would violate those already-adopted invariants. `CaseParticipant` is similarly not removable without breaking §12–14 of the WHAT (participation is explicitly part of the primitive's purpose). **No component of the three is removable without breaking already-stated invariants.** The Build Unit is not unnecessarily broad.

---

## 19. Anti-copy findings

```text
canonical decision pattern       → REQUIRED BY CASE SEMANTICS
  (material status transitions need governed authorization,
   independently justified in §10 above, not merely copied)

supersession pattern              → REQUIRED BY CASE SEMANTICS
  (CQ15 shows Case/CaseEvent currently LACK supersession
   infrastructure RunnerArtifact already has — this is a gap
   to fill, not a pattern copied without justification)

idempotency                       → REQUIRED BY CASE SEMANTICS
  (identical justification to B3/B4: governed replay of the
   same Case-mutation request must not silently duplicate)

current/historical navigation     → REQUIRED BY CASE SEMANTICS,
                                     BUT SCOPE MUST EXCLUDE
                                     current_execution_id (§5)

authority context                 → REQUIRED BY CASE SEMANTICS
  (reused AuthorityContext mechanism itself is appropriate reuse,
   not a semantic assumption — B3/B4 already established it as a
   generic, non-domain-specific checker)
```

**One confirmed anti-copy violation, already covered in §4:** the WHAT's *justification* for the Case→Execution build-order dependency incorrectly derived a governance conclusion from a schema-level FK observation, without independently justifying why the FK implies governance ordering. The conclusion happens to be correct for an unrelated reason (§5's `current_execution_id` coupling), but the stated reasoning in the WHAT itself must be repaired.

---

## 20. HANNIBAL boundary findings

Reviewing `CPL_BUILD_STRUCTURING_v0.md` and `CPL_BUILD_STRUCTURE_CHALLENGE_v0.md` for construction-dependency conclusions that silently became semantic definitions:

- The Build Structure Challenge's conclusion that `RunnerArtifact` "already is the evidence object" (HBS-Q01) is a **construction-dependency finding** (no new table needed) that does **not** overreach into defining what evidence *means* semantically for Case Governance — appropriately left to this WHAT and future requirements. No violation found.
- The Build Structure Challenge's HBS-Q03 conclusion (schema already keeps CPL representation distinct from world assertion) is descriptive of *existing* schema behavior, not a new semantic rule invented by HANNIBAL — it correctly recommended the *future WHAT* state this explicitly (which this WHAT's CG-CI02/CG-CI07/CG-CI08 do). No violation found.
- No instance was found of the Build Structuring or Build Structure Challenge documents prescribing Case *status values*, *event vocabulary*, or *participant roles* — those were correctly left to this WHAT and beyond. HANNIBAL boundary **holds** across both prior documents.

---

## 21. WHAT gaps

```text
GAP-01
Case-to-Case consolidation/merge is not addressed anywhere in the
candidate WHAT (CQ13). Must be named as an explicit open question,
not silently absent.

GAP-02
CaseEvent classification (CPL-fact vs domain-assertion vs
canonical-decision-consequence) is not made an explicit governance
concern (CQ8) — risk of undifferentiated payload blurring the
boundary the WHAT itself wants to preserve.

GAP-03
Case/CaseEvent currently lack any supersession/correction schema
(unlike RunnerArtifact) — CQ15. Requirements phase must add new
schema, not just service-layer code, unlike some lighter B4 work.

GAP-04
The naming distinction between physical table name ("cases") and
canonical ontology vocabulary (CQ2) is not addressed.
```

---

## 22. Required repairs

```text
REPAIR-01 (blocking)
Explicitly scope current_execution_id / CaseEvent.execution_id as
opaque, execution-governance-owned pointers NOT interpreted, gated
on, or claimed as fully-navigable by Case Governance, until
Execution Governance exists (resolves EXECUTION_EXCLUSION_REQUIRES_REPAIR).

REPAIR-02 (blocking)
Correct §4's dependency justification: replace the FK-implies-
build-order reasoning with the actual justification
(current_execution_id coupling, REPAIR-01).

REPAIR-03 (non-blocking but required before requirements)
Explicitly state that Case.asset_id is currently NOT NULL
(mandatory), correcting §9's "Contact / Asset / both" framing,
and explicitly decide whether Asset-optional Case is in-scope
schema repair for this Build Unit's requirements phase.

REPAIR-04 (non-blocking)
Add GAP-01 through GAP-04 as named open questions in the WHAT,
rather than leaving them implicitly absent.
```

---

## 23. Final verdict

```text
WHAT_REPAIR_REQUIRED
```

The core structural decision — Case Governance as an admissible, sufficiently cohesive Build Unit, ordered before Execution Governance — **survives this challenge**. No evidence was found requiring `BUILD_STRUCTURE_REOPEN_REQUIRED`: the split itself is not invalid, only under-specified at two points (the execution-pointer coupling and the Asset-anchoring overstatement), both of which are bounded repairs to the WHAT text, not reversals of the Build Structuring decision.

```text
CPL_CG_WHAT_CHALLENGE_v0
=========================

Case as CPL primitive:            SURVIVES (with asset-anchoring repair)
Case/Execution split:              SURVIVES (with dependency-justification repair)
Execution exclusion:                REQUIRES_REPAIR
Artifact exclusion:                 VALID
CaseParticipant boundary:          SURVIVES
CaseEvent ontology:                 SURVIVES (with classification-gap repair)
Event vs Decision:                  SURVIVES (discipline-dependent)
World/Assertion/Representation:    SURVIVES
Case status vs domain state:        SURVIVES CLEANLY
Actor/Role:                         REPAIRABLE, NOT SUFFICIENT AS-IS
Build Unit cohesion/minimality:    CONFIRMED
Anti-copy:                          ONE VIOLATION FOUND (dependency reasoning)
HANNIBAL boundary:                  HOLDS

BLOCKING REPAIRS:                   2 (REPAIR-01, REPAIR-02)
NON-BLOCKING REPAIRS:                2 (REPAIR-03, REPAIR-04)

FINAL VERDICT:                      WHAT_REPAIR_REQUIRED
```

---

## 24. Stop condition

**STOP.** No WHAT freeze, no requirements, no schema modification, no production code, no migrations, no B5 designation, no candidate branch, no Execution Governance work performed or authorized by this challenge.

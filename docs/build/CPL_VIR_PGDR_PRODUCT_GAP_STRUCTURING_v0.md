# CPL_VIR_PGDR_PRODUCT_GAP_STRUCTURING_v0

## INVESTIGATION BASELINES

```text
CPL SOFTWARE:
  2ac075daea7d162825ed73ded0c7548011242a8f

CPL GOVERNANCE:
  f1a7bae35b047db54027452c8c565d48695aaced

VIR:
  https://github.com/paxtonef/vehicle-identity-resolver
  Real git commit SHA (obtained after publication, superseding the
  earlier zip-export fingerprint used during the initial pass of this
  investigation):
  a342aba7cc2fc517621f4fc79c3191bdfdc9e10b

VIR BRANCH:
  main

VIR WORKTREE:
  CLEAN

PGDR:
  https://github.com/paxtonef/pgdr
  Real git commit SHA (obtained after publication, superseding the
  earlier zip-export fingerprint):
  0580b1a5ba5867a607a33197372fcaf4164f0fb6

PGDR BRANCH:
  main

PGDR WORKTREE:
  CLEAN
```

**Content identity confirmed:** both repositories were initially supplied as GitHub zip exports (no `.git` history, no real SHA obtainable). After the repositories were made public, both were re-cloned with full git history and directly diffed (`diff -rq`) against the originally-inspected zip contents. Result: **byte-identical** (the one reported difference, a stray `src/pgdr/__pycache__` directory, was a Python bytecode artifact created by this investigation's own test run against the extracted zip, not a real content difference). All findings and citations in this report were made against the exact content now identified by the two SHAs above; nothing needed re-investigation as a result of publication.

---

## 1. Executive verdict

```text
PRIMARY VERDICT:        PRODUCT_FRONTIER_IDENTIFIED
EG-01:                   CONFIRMED_WITH_REPAIR
CPL_MINIMUM_FOR_VIR_PGDR_REACHED:  CONDITIONAL
```

The short version: **VIR and PGDR are each independently mature, well-governed systems that do not yet talk to CPL or to each other in any live way.** VIR has a real database and HTTP API but its own, separate SQLite store — zero CPL awareness. PGDR has no persistence at all (`persistence.required: false`) and no HTTP API — it is a stateless CLI that accepts a bare `--vir-id` string typed by whoever invokes it, never calling VIR. The "VIR → PGDR handoff" that exists today is a *documented contract shape* (`DiagnosticIdentityContext`), not a working pipe — nothing currently moves data from one to the other automatically. `RunnerExecution`/`RunnerArtifact` remain exactly as under-governed as the prior Build Structuring pass found them (§7 of the investigation mandate), and they are the most direct, evidence-grounded candidate for the next common gap — but a repair to the earlier hypothesis is required (see §12): the schema-level fit is strong, but at least one genuine common capability (execution-result classification analogous to B5's `CaseEventType`) is not yet present and would need to be added, not merely governed as-is.

---

## 2. Canonical starting state

As pinned in the investigation baselines above. B1–B5 closed; B5's Closure Record (`f1a7bae`) is the current governance HEAD. Software baseline `2ac075d` independently re-verified in this pass: `git checkout 2ac075daea7d162825ed73ded0c7548011242a8f` against a fresh clone of `https://github.com/paxtonef/cpl.git` succeeded and `git rev-parse HEAD` returned the exact expected SHA.

---

## 3. Target product journey

Investigated against the mandate's proposed journey (§2 of the mandate). The journey as actually supportable by current evidence, annotated:

```text
USER
  ↓
ACCOUNT / CONTACT               — CPL: Contact (B3), governed
  ↓
REGISTERED VEHICLE              — CPL: Asset + ContactAssetRelationship (B4), governed
  ↓
VIR                              — external system, real HTTP API, real SQLite persistence,
                                    ZERO awareness of CPL Contact/Asset
  ↓
VEHICLE IDENTITY / INFORMATION  — VIR's VehicleIdentityResolution; not currently
                                    represented as any CPL object
  ↓
PGDR                             — external system, NO persistence, NO HTTP API,
                                    accepts VIR output only as a manually-supplied
                                    CLI string (--vir-id, --vir-status); never calls VIR
  ↓
DIAGNOSTIC CASE                  — PGDR's own in-memory DiagnosticCaseState.case_id
                                    (same name, unrelated substance to CPL's Case)
  ↓
EXECUTION                        — CPL: RunnerExecution schema exists (B2), ungoverned;
                                    no code anywhere creates a row here for VIR or PGDR
  ↓
RESULT / ARTIFACT                — CPL: RunnerArtifact schema exists (B2), ungoverned;
                                    PGDR's GaragePreparationReport/UserSummary exist only
                                    in-process, never written anywhere
  ↓
HISTORY / FOLLOW-UP              — CPL: CaseEvent (B5), governed, but nothing currently
                                    writes a CaseEvent from a VIR or PGDR execution
```

---

## 4. Existing CPL capability map

Confirmed present and governed at `2ac075d` (all verified by direct file inspection, not assumed from the frontier list in the mandate):

```text
app/cpl/identity/       Contact, ContactPoint, Account, resolution, reconciliation,
                          authority, evidence, provenance, verification
app/cpl/assets/          Asset, AssetIdentifier, AssetIdentityResolution,
                          CanonicalAssetIdentityDecision, merge, relationships,
                          ExternalReference, DomainProjection, authority
app/cpl/cases/           Case, CaseParticipant, CaseEvent — lifecycle, participants,
                          events, correction, authority, outcomes (B5)
```

Confirmed ABSENT (no service-layer code beyond bare SQLAlchemy models):

```text
app/cpl/models/runner_execution.py    — model only
app/cpl/models/runner_artifact.py     — model only
```

`grep -rln "RunnerExecution\|RunnerArtifact" app/ --include="*.py" | grep -v "/models/"` returns **zero results**. The only test references are B2's own bare-CRUD schema tests and one B5 boundary test (`test_b5_repair_verification.py`, confirming B5 does *not* interpret `execution_status` — it does not add governance).

Confirmed: **zero HTTP business-logic routes exist anywhere in CPL.** `app/api/__init__.py` is an empty package marker; `app/main.py` exposes only `/health` and `/ready`. This is consistent with the explicit, repeated B3/B4/B5 precedent (no frozen requirement has ever mandated a transport surface).

---

## 5. VIR capability/interface findings

**Interface:** Real FastAPI HTTP service (`src/vir/api/routes.py`) plus a CLI (`src/vir/cli/main.py`) plus a web router (`src/vir/web/routes.py`). Verified endpoints, cited directly from `routes.py`:

```text
POST /v1/vehicle-identities/resolve
POST /v1/vehicle-identities/{resolution_id}/clarifications
GET  /v1/vehicle-identities/{resolution_id}
GET  /health
GET  /v1/vehicle-identities/{resolution_id}/handoff/diagnostic
```

**DOCUMENTATION / IMPLEMENTATION DIVERGENCE (§0.2):** `EXECUTION_BASELINE.md` (an early-phase document) states the `handoff/diagnostic` and `{resolution_id}` GET endpoints "still return 501" and require "a persistent store (P-later: Persistence)." The actual current code (`src/vir/api/routes.py`, `src/vir/persistence.py`) shows these are fully implemented, backed by a real `SQLitePersistenceAdapter` (`src/vir/adapters/sqlite_persistence_adapter.py`). The documentation predates a later persistence phase; the implementation is ahead of the doc. Not treated as ambiguous — the executable code is authoritative per the investigation instruction, and is what this report relies on.

**Inputs required** (`VehicleIdentityRequest`, `src/vir/domain/models.py:188`): `request_id`, `locale`, `registration` (plate-based lookup), `vin`, `manual_identity`, `supporting_documents`, `consent`. **No Contact/owner/user field exists anywhere in this model** — confirmed by direct grep (`owner|contact|user_id|driver` returns zero hits in `src/vir/domain/models.py`'s request/resolution types). VIR resolves vehicle identity purely from vehicle-side identifiers; it has no concept of who is asking.

**Output:** `VehicleIdentityResolution`, classified by field:

```text
resolution_id            — VIR-local identifier (VIR's own SQLite PK, not a CPL identity)
resolution_status         — DOMAIN DETERMINATION (VIR's own resolution engine's verdict)
vehicle_identity          — DOMAIN DETERMINATION (manufacturer/model/engine/etc.)
confidence                — DOMAIN DETERMINATION (VIR's own scoring)
unresolved_fields,
contradictions             — DOMAIN DETERMINATION
```

None of this is currently written to CPL in any form. VIR persists exclusively to its own SQLite database (`src/vir/persistence.py`: "Today's implementation is SQLite... PostgreSQL is the likely target once the runner operates at scale" — a documented, not-yet-built future intent, not current behavior).

**`ResolutionStatus` enum** (`src/vir/domain/enums.py:4`): 8 values — `resolved, provisionally_resolved, ambiguous, insufficient_data, contradictory, unsupported_country, provider_unavailable, invalid_identifier`.

---

## 6. PGDR capability/interface findings

**Interface:** CLI only (`src/pgdr/cli.py`, Click-based). Confirmed directly from `runner_execution_contract.yaml`: `api.available: false`, `persistence.required: false`, `"DiagnosticSession exists only in process memory for the duration of a single CLI invocation; nothing is written to disk or a database."`

**Inputs required** (`cli.py` `run` command): `--vir-id` (bare string, `resolution_id: str` — no VIR call is ever made; confirmed by `grep -rln "requests\.|httpx\.|http://|https://|urllib" src/pgdr/` returning zero results), `--vir-status` (a manually-typed `Click.Choice` from PGDR's own 5-value `ResolutionStatus` enum, `src/pgdr/enums.py:5`), `--complaint`, plus vehicle-state/location/urgency/consent flags.

Explicit design principle found in code (`src/pgdr/models.py:34`): *"Input contract only — the PGDR never reconstructs VIR logic (PGDR-ID-001)."* This is a deliberate architectural boundary, not an oversight: PGDR expects to *receive* VIR's output, never to compute or fetch it.

**Concrete incompatibility, independently reproduced:** PGDR's `ResolutionStatus` (5 values) is a strict subset of VIR's `ResolutionStatus` (8 values). The three VIR-only values — `unsupported_country`, `invalid_identifier`, `provider_unavailable` — **cannot be passed to PGDR's CLI at all**; `Click.Choice` validation would reject them outright. Verified by direct enum-set comparison in this investigation, not inferred. If VIR ever resolves to one of these three statuses, there is currently no way to hand that off to PGDR as-is.

**Output:** `GaragePreparationReport` + `UserSummary` (`src/pgdr/models.py:228,253`), pure Pydantic objects, held in memory, printed as console text and optionally dumped as JSON to stdout (`session.result.model_dump_json()`). **Never written to any file or database.**

**Governance:** PGDR routes every diagnostic *claim* (not identity, not execution) through **GGM**, a separate, external, pinned package (`vendor/ggm-1.2.0-py3-none-any.whl`) — its own epistemic-status/authority-level/claim-family governance system, entirely independent of CPL. GGM governs statements like "compatible with symptom X," not vehicle or case identity. This is domain-specific diagnostic-epistemics governance, out of CPL's scope by construction — no evidence found that CPL should absorb or interface with GGM's internal model; the boundary is already clean (`src/pgdr/governance/port.py`: PGDR's own neutral DTOs "carry no GGM vocabulary").

**PGDR's own internal `case_id`** (`src/pgdr/domain/analytical_state.py:34`): `DiagnosticCaseState.case_id`, auto-generated as `CASE-{uuid4hex}`. Same name, entirely unrelated substance to CPL's `Case` — this is a naming collision to be aware of during any future integration design, not evidence that PGDR already has a CPL-compatible Case concept.

---

## 7. RunnerExecution findings

Schema (`app/cpl/models/runner_execution.py`, unchanged since B2, migration `011`):

```text
execution_id, case_id (FK -> cases, NOT NULL), asset_id (FK -> assets, NOT NULL),
runner_type, runner_version, execution_purpose (nullable),
execution_status (CREATED/QUEUED/RUNNING/COMPLETED/FAILED/BLOCKED/CANCELLED),
parent_execution_id (self-FK, nullable), initiated_by_contact_id (FK -> contacts, nullable),
idempotency_key (nullable, unused), started_at, completed_at, created_at
```

- **Consumers:** none. **Service/API support:** none. **Tests:** B2 bare-CRUD only, plus one B5 boundary-preservation test.
- **Lifecycle, authority, history, retry/replay, failure, correction semantics:** none implemented — the columns exist (`execution_status`, `parent_execution_id`) but nothing governs transitions between them, checks authority before writing, or records why a transition happened.
- **VIR compatibility:** `runner_type`/`runner_version` could hold `"VIR"`/VIR's package version; `case_id`/`asset_id` map cleanly onto CPL's own governed objects. No structural incompatibility found.
- **PGDR compatibility:** same — `runner_type = "PGDR"` fits; `initiated_by_contact_id` maps to the requesting Contact. No structural incompatibility found.

---

## 8. RunnerArtifact findings

Schema (`app/cpl/models/runner_artifact.py`, unchanged since B2, migration `012`):

```text
artifact_id, execution_id (FK -> runner_executions, NOT NULL),
artifact_type, schema_name, schema_version, artifact_status
  (CREATED/VALIDATED/SUPERSEDED/REJECTED), payload (JSONB, NOT NULL),
hash_algorithm/content_hash (paired, nullable), supersedes_artifact_id (self-FK), created_at
```

**Notable structural alignment (evidence, not coincidence):** `RunnerArtifact.schema_name`/`schema_version` already exist. Both VIR and PGDR independently maintain their own "Runner Execution Contract" documents with a `schema_version` field (`RUNNER_EXECUTION_CONTRACT.md` in VIR; `runner_execution_contract.yaml` with `schema_version: 1` in PGDR). This is a real convergence of intent across three independently-developed systems — worth naming explicitly as evidence for any future WHAT, not merely asserted.

- **Consumers/service/API/tests:** none, same as `RunnerExecution`.
- **Can `RunnerArtifact` hold VIR/PGDR output without becoming domain authority?** Yes, structurally — `payload` is opaque JSONB; `schema_name`/`schema_version` let a consumer interpret it correctly without CPL parsing domain content. `ARTIFACT CONTAINS DOMAIN RESULT ≠ CPL DETERMINES DOMAIN TRUTH` holds by construction here, exactly as it already does for B4's `DomainProjection`.
- **Gap found:** unlike B5's `CaseEventType` registry (definition-time semantic classification, REQ-B5-115), there is no equivalent classification for `RunnerArtifact.artifact_type` — nothing distinguishes "this artifact is a domain determination" from "this artifact is a technical execution log" at the `artifact_type` level. This is the concrete gap referenced in the Executive Verdict's "repair" qualifier on EG-01.

---

## 9. VIR→PGDR handoff analysis

```text
VIR
 ↓
WHAT OUTPUT?          VehicleIdentityResolution (VIR-internal, SQLite-persisted)
 ↓
WHAT REPRESENTATION?  DiagnosticIdentityContext (src/vir/domain/models.py:255) —
                       a purpose-built, already-existing handoff DTO:
                       resolution_id, identity_status, vehicle (dict), diagnostic_constraints (dict)
 ↓
WHAT VALIDATION?       NONE currently enforced end-to-end — the DTO exists and is
                       served over HTTP (GET .../handoff/diagnostic), but nothing
                       calls that endpoint and feeds the result into PGDR
                       automatically. PGDR's CLI takes hand-typed strings instead.
 ↓
WHAT IDENTITY LINK?    NONE — VIR's resolution_id and PGDR's --vir-id are matched
                       only by convention (a human copies the string), not by any
                       shared identity system. Neither references a CPL Asset.
 ↓
PGDR
```

`DOMAIN DETERMINES DOMAIN TRUTH; CPL GOVERNS COMMON CANONICAL REPRESENTATION` is currently **not tested by this handoff at all**, because CPL is not part of the handoff path today. VIR determines vehicle identity; PGDR consumes a manually-relayed summary of it; nothing canonical governs the link between them.

---

## 10. End-to-end journey coverage matrix

| Step | Status | Evidence |
|---|---|---|
| 1. User exists/registers | IMPLEMENTED + GOVERNED | CPL `Contact` (B3) |
| 2. Contact identity resolved | IMPLEMENTED + GOVERNED | CPL `identity/resolution.py`, `reconciliation.py` |
| 3. Vehicle registered | IMPLEMENTED + GOVERNED | CPL `Asset` (B4) |
| 4. Asset created/resolved | IMPLEMENTED + GOVERNED | CPL `assets/creation.py`, `resolution.py` |
| 5. Contact↔Asset relationship | IMPLEMENTED + GOVERNED | CPL `ContactAssetRelationship` (B4) |
| 6. Case created | IMPLEMENTED + GOVERNED | CPL `cases/lifecycle.py` (B5) |
| 7. VIR requested | IMPLEMENTED (VIR-side only) | `POST /v1/vehicle-identities/resolve` — real, but has no CPL-side caller |
| 8. VIR execution represented (as CPL RunnerExecution) | MISSING | zero code creates a `RunnerExecution` row anywhere |
| 9. VIR result persisted/referenced (as CPL RunnerArtifact) | MISSING | zero code creates a `RunnerArtifact` row; VIR persists only to its own SQLite |
| 10. PGDR requested | IMPLEMENTED (PGDR-side only) | `pgdr run` CLI — real, but has no automatic caller and no automatic VIR-fed input |
| 11. PGDR execution represented (as CPL RunnerExecution) | MISSING | same as step 8 |
| 12. PGDR result persisted/referenced (as CPL RunnerArtifact) | MISSING | PGDR output exists only in-process; nothing writes it anywhere |
| 13. Result exposed to product | MISSING | no CPL/product API surface exists to serve any of this to a frontend |
| 14. Historical case/result reconstructable | PARTIALLY IMPLEMENTED | `CaseEvent` (B5) could record this, but nothing currently writes a `CaseEvent` from a VIR/PGDR execution |

Steps 1–6: solid, governed CPL substrate. Steps 7 and 10: real, working systems that simply aren't wired to anything. Steps 8, 9, 11, 12, 13: genuinely missing — not under-governed, **absent**. Step 14: the mechanism exists but is unused for this purpose.

---

## 11. Three-bucket gap map

### COMMON GAP — CPL

**GAP-C01**
- Description: Govern `RunnerExecution` (authority, idempotency, lifecycle transition discipline, correction/history) — the same governance pattern B3→Contact, B4→Asset, B5→Case each already applied to their respective B2-era substrate.
- Evidence: §7 above; zero service layer exists today.
- Required by journey step: 8, 11.
- Layer: CPL (Common Product Layer).
- Dependencies: B3 Identity (`initiated_by_contact_id`), B4 Asset (`asset_id`), B5 Case (`case_id`) — all closed, satisfied.
- Blocking: YES for steps 8/11; downstream steps 9/12/13/14 depend on it.
- Existing substrate: full B2 schema, unchanged.
- Recommended disposition: candidate for a governed Build Unit — but see GAP-C02 first.

**GAP-C02**
- Description: `RunnerArtifact.artifact_type` currently has no definition-time semantic-classification mechanism analogous to B5's `CaseEventType` (REQ-B5-115). Without it, a future consumer cannot determine whether an artifact is a domain determination, a technical log, or something else, without inspecting arbitrary payload content — repeating exactly the ambiguity B5 closed for `CaseEvent`.
- Evidence: §8 above; direct comparison against `case_event_type.py`.
- Required by journey step: 9, 12.
- Layer: CPL.
- Dependencies: GAP-C01 (natural co-build, same as B5's `RunnerExecution`↔`RunnerArtifact` cohesion question).
- Blocking: NON-BLOCKING in isolation, but leaving it unaddressed while governing `RunnerExecution`/`RunnerArtifact` would reproduce a defect this project has already learned to avoid.
- Existing substrate: `schema_name`/`schema_version` columns already present (§8) — a lighter fix than B5's, since the pattern (a small registry table) is already proven.
- Recommended disposition: fold into the same Build Unit as GAP-C01, or address explicitly as an in-scope requirement of it.

**No other CPL gap was found to be blocking.** Contact, Asset, Case, and their relationships are sufficient for steps 1–6. Nothing in VIR's or PGDR's actual input/output contracts requires a generalized Actor, Role, Evidence, State, Organization, or event-sourcing primitive — every candidate concept from §5 of the mandate was checked against VIR's and PGDR's real data models and found unnecessary (VIR has no Contact-adjacent concept at all; PGDR's "case" and "governance" are self-contained and domain-specific).

### DOMAIN / INTEGRATION GAP — VIR/PGDR

**GAP-D01**
- Description: No code exists anywhere that calls VIR's HTTP API from CPL or from a caller acting on CPL's behalf, and no code exists that calls PGDR (which has no API to call — it's CLI-only). The "VIR → PGDR" pipeline is entirely human-mediated today (copy a `resolution_id`, retype a `--vir-status`).
- Evidence: §5, §6, §9.
- Required by journey step: 7, 10.
- Layer: VIR/PGDR domain integration.
- Blocking: YES for any automated journey.
- Recommended disposition: NOT a CPL concern — this is integration/orchestration code that calls VIR's existing API and PGDR's existing CLI, using whatever `RunnerExecution` governance CPL provides (if GAP-C01 is built) or, absent that, some other mechanism entirely outside CPL.

**GAP-D02**
- Description: `ResolutionStatus` vocabulary mismatch (VIR 8 values, PGDR 5 values) — confirmed exactly in §6.
- Evidence: direct enum-set comparison, reproduced in this investigation.
- Required by journey step: 7→10 handoff.
- Layer: VIR/PGDR domain integration (not CPL — this is a contract mismatch between two domain systems, not a CPL representation problem).
- Blocking: only for the 3 affected status values; the other 5 already interoperate.
- Recommended disposition: a PGDR-side or integration-layer decision (expand PGDR's accepted enum, or map the 3 extra VIR values to PGDR's nearest equivalent at the integration boundary) — out of CPL's scope entirely.

**GAP-D03**
- Description: PGDR gives no persistence at all; any product needs somewhere to keep the diagnostic session/result beyond a single CLI process. Whether that "somewhere" is CPL's `RunnerArtifact` or a PGDR-side addition is undecided by current evidence.
- Evidence: §6, `persistence.required: false`.
- Layer: ambiguous — genuinely could resolve into CPL (if `RunnerArtifact` governance is built and PGDR's caller writes into it) or into domain/integration layer (if PGDR itself grows a persistence adapter, as VIR did). Flagged as a **blocking question** (§16), not resolved here.

### PRODUCT GAP — SITE/API/UI

**GAP-P01**
- Description: No product/application HTTP API exists anywhere (CPL exposes only `/health`/`/ready`; VIR's API is VIR-specific and would need to be called by something; PGDR has no API at all).
- Required by journey step: 13, and implicitly all frontend-facing steps in §15 of the mandate.
- Layer: Product/API.
- Blocking: YES for any real user-facing product, but explicitly **not** a CPL gap — no frozen CPL requirement across B3/B4/B5 has ever mandated a transport surface, and nothing in this investigation found a concrete reason to change that now.
- Recommended disposition: product/application-layer work, consuming whatever CPL/VIR/PGDR governance exists underneath it.

**GAP-P02**
- Description: No frontend exists. Per §15 of the mandate, frontend absence alone must not cause CPL expansion — and it doesn't; nothing found in VIR or PGDR's actual contracts requires new CPL primitives merely to support a UI.
- Layer: Product/UI.
- Blocking: YES for end-user usability, NOT a CPL gap.

---

## 12. Execution Governance hypothesis verdict

```text
EG-01: CONFIRMED_WITH_REPAIR
```

`RunnerExecution` + `RunnerArtifact` do form the next minimal common gap standing between CPL as built and an automatable VIR/PGDR journey (GAP-C01) — this much is directly confirmed by the coverage matrix (§10): every missing step downstream of the existing, governed Contact/Asset/Case substrate routes through exactly these two ungoverned objects.

The repair: the hypothesis as previously stated (`CPL_BUILD_STRUCTURING_v0.md`) did not anticipate GAP-C02 (artifact semantic classification) as part of the same gap — this investigation found it by direct structural comparison against B5's already-solved `CaseEventType` problem, not by assumption. A WHAT built on the unrepaired hypothesis would likely reproduce the exact class-collapse risk B5's `GAP-02` was built to close.

---

## 13. Split/cohesion verdict

Testing the three alternatives from §18 of the mandate:

**A. `Execution Governance { RunnerExecution, RunnerArtifact }` as one unit** — supported by the same semantic/build-dependency reasoning B5 already established for its own two-table predecessor (Case+CaseParticipant+CaseEvent cohesion, §18 of `CPL_CG_WHAT_CHALLENGE_v0.md`): `RunnerArtifact.execution_id` is `NOT NULL`, meaning an artifact cannot exist without its execution, and no evidence was found of a scenario where governing one without the other produces a coherent intermediate state (unlike B5's Case/Execution split, where Case genuinely could exist without any execution — here, an ungoverned `RunnerArtifact` with a governed `RunnerExecution`, or vice versa, would leave exactly the kind of governance-boundary gap B5's own Requirement Challenge (RM-B5-01 through 09) was built to catch).

**B. `Execution Governance → Artifact Governance` as two units** — tested and rejected: unlike Case→Execution (where `Case` demonstrably exists independently in the actual product journey — steps 1–6 above prove it), no step in the actual VIR/PGDR journey exercises a `RunnerExecution` without an eventual `RunnerArtifact` (every execution either produces a result or fails; both are equally within scope of "what happened during this execution," not two separable concerns).

**C. Another decomposition** — none found in the actual repository evidence; VIR and PGDR each produce exactly one execution-plus-result shape, not a more granular structure that would suggest a different split.

**Verdict: one Build Unit — `RunnerExecution` + `RunnerArtifact` together — is the correct cohesion**, distinct from B5's split decision, and justified by the same dependency-type discipline (schema dependency ≠ semantic dependency, applied here to find they *do* coincide, not that they don't).

---

## 14. Minimum CPL stopping point

```text
CPL_MINIMUM_FOR_VIR_PGDR_REACHED = CONDITIONAL
```

**Condition:** IF GAP-C01 (with GAP-C02 folded in) is built as one governed Build Unit, THEN CPL can stop and product/domain construction (GAP-D01–D03, GAP-P01–P02) can proceed without requiring further CPL primitives — no other capability investigated in this pass was found to block the minimum journey.

**IF NOT built:** the additional blocking common capability is exactly GAP-C01/C02 as scoped above — nothing broader. No other CPL gap was found to be blocking (§11 — the negative findings for Actor/Role/Evidence/State/Organization are as load-bearing as the positive findings for `RunnerExecution`/`RunnerArtifact`).

---

## 15. Product construction dependency graph

Derived from repository evidence, not assumed from the mandate's suggested shape:

```text
B1-B5 (CLOSED, 2ac075d)
        │
        ▼
Execution/Artifact Governance  (GAP-C01 + GAP-C02, one Build Unit — NOT YET ADMITTED)
        │
        ├──────────────────────┬────────────────────────┐
        ▼                      ▼                         ▼
VIR integration           PGDR integration          (both may proceed
(call existing             (call existing             in parallel once
VIR HTTP API,               PGDR CLI, feed             the governed
write governed              its output into a          RunnerExecution/
RunnerExecution/             governed RunnerArtifact)   Artifact objects
RunnerArtifact)                                          exist)
        │                      │
        └──────────┬───────────┘
                    ▼
        VIR→PGDR handoff resolution
        (GAP-D02: status-vocabulary mapping;
         GAP-D03: where PGDR's result persists)
                    │
                    ▼
        Application/API layer (GAP-P01)
                    │
                    ▼
        Frontend (GAP-P02)
                    │
                    ▼
        Operational VIR/PGDR Product
```

Note: unlike the mandate's suggested linear shape, VIR integration and PGDR integration are **not** strictly sequential on each other — both depend on the same governed Execution/Artifact layer, but neither depends on the other's integration code being built first. Only the *handoff* between them (GAP-D02/D03) has a real ordering constraint, and it sits after both, not between them.

---

## 16. Blocking questions

```text
BQ-01
Where should PGDR's result ultimately live — as a CPL RunnerArtifact
(requiring PGDR's caller to write there) or as a PGDR-side persistence
addition (mirroring what VIR already built for itself)? This
investigation found evidence for both being structurally possible and
did not find evidence forcing one answer. Recommend this be resolved
explicitly in the next WHAT, not assumed.

BQ-02
Should the CPL-governed RunnerExecution eventually replace VIR's own
SQLite-persisted resolution_id as the canonical identity of a VIR
execution, or coexist alongside it indefinitely (VIR keeps its own
store; CPL separately records that an execution happened)? Evidence
found: VIR's own documentation anticipates a future PostgreSQL adapter
but has not built one — this is VIR's own roadmap item, not something
this investigation can resolve on VIR's behalf.

BQ-03
GAP-D02's status-vocabulary mismatch: does its resolution belong to
VIR (narrow its output), PGDR (widen its input), or a translation
layer between them? Not resolvable from repository evidence alone —
requires a product/domain decision outside CPL's authority.
```

---

## 17. Recommended next governance action

```text
Define a pre-admission WHAT for the demonstrated Common Gap:
Execution/Artifact Governance (RunnerExecution + RunnerArtifact,
including artifact semantic classification per GAP-C02), following
the same Build Structuring Challenge -> WHAT -> WHAT Challenge cycle
already used for Case Governance.
```

This is a recommendation only; it is not executed by this investigation.

---

## FINAL SUMMARY

```text
CPL_VIR_PGDR_PRODUCT_GAP_STRUCTURING_v0
=======================================

CANONICAL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

GOVERNANCE HEAD:
  f1a7bae35b047db54027452c8c565d48695aaced

B5:
  CLOSED

TARGET:
  OPERATIONAL VIR/PGDR PRODUCT

COMMON CPL GAPS:
  GAP-C01 (Execution/Artifact Governance), GAP-C02 (artifact semantic
  classification) — one Build Unit

VIR/PGDR INTEGRATION GAPS:
  GAP-D01 (no automated caller of either system), GAP-D02 (status
  vocabulary mismatch), GAP-D03 (undecided persistence location)

PRODUCT/API/UI GAPS:
  GAP-P01 (no application API), GAP-P02 (no frontend) — neither is a
  CPL gap

EG-01:
  CONFIRMED_WITH_REPAIR

NEXT COMMON BUILD UNIT:
  Execution/Artifact Governance (candidate name only)
  NOT ADMITTED

CPL_MINIMUM_FOR_VIR_PGDR_REACHED:
  CONDITIONAL (on building the above)

PRIMARY VERDICT:
  PRODUCT_FRONTIER_IDENTIFIED

NEXT GOVERNANCE ACTION:
  Define pre-admission WHAT for Execution/Artifact Governance

IMPLEMENTATION:
  NOT AUTHORIZED
```

**STOP.** No production code, migrations, schema modification, route implementation, frontend implementation, VIR modification, PGDR modification, requirements generation, Execution Mandate, candidate branch, or Build Unit admission was performed by this investigation.

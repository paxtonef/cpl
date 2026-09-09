# CPL_VIR_PGDR_PRODUCT_INTEGRATION_REALITY_CHECK_v0

## 1. Executive verdict

```text
FINAL VERDICT: PRODUCT_FRONTIER_READY
```

All three repositories were cloned and inspected directly — no design-from-assumption anywhere below. The
central finding: **VIR and PGDR were already built expecting each other.** VIR's `DiagnosticIdentityContext`
handoff endpoint and PGDR's `VehicleIdentityContext` input model share almost every field directly, and
PGDR's own code cites "PGDR-ID-001" in a docstring explaining it never reconstructs VIR logic — this
integration was anticipated on the domain side before this investigation ever started. On the CPL side,
`AssetIdentityResolution` (an `execution_id` FK to `runner_executions`, a `canonical_identity_payload` JSONB,
a `confidence` numeric field) and `VehicleDetail` (a `source_resolution_id` FK) look purpose-built for
exactly this handoff too, though nothing currently wires them to VIR.

**Zero evidenced COMMON_GAP.** Every transition in the product path is either directly usable today or
needs adapter/orchestration code — never a new CPL primitive. `CPL_REOPEN_REQUIRED = NO`.
`B7_REQUIRED = NOT_DEMONSTRATED`.

The real, load-bearing architectural fact this investigation surfaces: **CPL, VIR, and PGDR share no
runtime, no datastore, and no API today.** CPL is a Postgres-backed internal Python service layer with no
external API (`/health` and `/ready` only). VIR is a FastAPI HTTP service with its own SQLite store. PGDR is
a CLI plus a programmatically-callable class with **zero persistence** — its own contract document says so
explicitly. Nothing in any of the three connects to anything else. The Product Integration Build Plan (§28)
is a plan to build the layer that doesn't exist yet, not to repair anything broken.

---

## 2. Repository identities and observed SHAs

```text
CPL
  remote:            https://github.com/paxtonef/cpl
  branch:            main
  observed HEAD:     1836a2c6bf54bd9fa83f88a94077dec5b0fd1abd
  working tree:       clean (fresh clone)
  canonical build baseline (from B6 Closure Record): 6181dabb9239e281974c368ad8f5df80350cabf1

VIR (vehicle-identity-resolver)
  remote:            https://github.com/paxtonef/vehicle-identity-resolver
  branch:            main
  observed HEAD:     a342aba7cc2fc517621f4fc79c3191bdfdc9e10b
  working tree:       clean (fresh clone)
  canonical certified baseline: NOT INDEPENDENTLY ESTABLISHED — this investigation treats the observed HEAD
                                  as the inspection target; no prior CPL governance artifact certifies a
                                  different VIR SHA as canonical.

PGDR
  remote:            https://github.com/paxtonef/pgdr
  branch:            main
  observed HEAD:     0580b1a5ba5867a607a33197372fcaf4164f0fb6
  working tree:       clean (fresh clone)
  canonical certified baseline: NOT INDEPENDENTLY ESTABLISHED — same treatment as VIR.
```

`OBSERVED HEAD ≠ HISTORICALLY CERTIFIED CANONICAL BASELINE`, preserved: VIR and PGDR have no CPL-style
governance chain certifying a specific SHA as canonical, so this investigation names the observed HEAD
explicitly rather than inventing a certified one.

---

## 3. Evidence methodology

Every material claim below cites an exact file path, symbol, or test. Confidence markers used throughout:
`CONFIRMED` (read directly from source or a passing test), `PARTIAL` (exists but incomplete for the product
need), `ABSENT` (searched for, not found), `UNDERDETERMINED` (evidence insufficient to classify). No
repository was modified; two disposable in-memory Python scripts were run against locally-installed
dependencies purely to cross-check enum values already visible in source — not against any repository's own
runtime.

---

## 4. CPL usable capability inventory

| Capability | Model | Service | Persistence | App operation | HTTP route | Tested | Real PG tested | Product-consumable |
|---|---|---|---|---|---|---|---|---|
| Contact | `app/cpl/models/contact.py` | `app/cpl/identity/contacts.py` (`create_contact`, `get_contact`, `resolve_contact`) | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED (B3 suite) | CONFIRMED | Python-import only |
| Asset | `app/cpl/models/asset.py` | `app/cpl/assets/creation.py` (`create_asset`), `merge.py`, `identifiers.py` | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED (B4 suite) | CONFIRMED | Python-import only |
| ContactAssetRelationship | model present | `app/cpl/assets/relationships.py` (`establish_relationship`, `end_relationship`) | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED | CONFIRMED | Python-import only |
| Case | `app/cpl/models/case.py` | `app/cpl/cases/lifecycle.py` (`create_case`, `transition_case_status`) | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED (B5 suite) | CONFIRMED | Python-import only |
| CaseParticipant | model present | `app/cpl/cases/` | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED | CONFIRMED | Python-import only |
| CaseEvent | model present | `app/cpl/cases/events.py` (per B5) | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED | CONFIRMED | Python-import only |
| RunnerExecution | `app/cpl/models/runner_execution.py` | `app/cpl/runners/execution.py` (`admit_execution`, `transition_status`, `persist_runner_report`, `retry_execution`) | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED (227/227, B6) | CONFIRMED | Python-import only |
| RunnerArtifact | `app/cpl/models/runner_artifact.py` | `app/cpl/runners/artifacts.py` (`register_artifact`, `supersede_artifact`) | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED (B6) | CONFIRMED | Python-import only |
| AssetIdentityResolution (VIR-relevant) | `app/cpl/models/asset_identity_resolution.py` | `app/cpl/assets/resolution.py` (`request_asset_identity_resolution`, `record_asset_identity_resolution`) | CONFIRMED | CONFIRMED | ABSENT | CONFIRMED | CONFIRMED | Python-import only |
| VehicleDetail (automotive) | `app/automotive/models/vehicle_detail.py` | ABSENT — no dedicated write function found | CONFIRMED (model only) | ABSENT | ABSENT | UNDERDETERMINED | UNDERDETERMINED | Model exists, no write path yet |

**Not confusing database capability with product-consumable capability (§7 discipline):** every row above is
`CONFIRMED` at the database/service layer and `Python-import only` at the product-consumable layer — nothing
is reachable except by code running inside the same Python environment, importing CPL as a package.

---

## 5. CPL product-surface gap

```text
git diff (grep) app/main.py: exactly two routes — GET /health, GET /ready
app/api/__init__.py: "API layer placeholder — B1 boundary only. Future phases will expose CPL service
                        contracts through this layer." (verbatim, unchanged since B1)
```

`CAPABILITY EXISTS IN CPL ≠ PRODUCT CAN CURRENTLY CALL IT` is not a slogan here — it is the literal, confirmed
state of the repository. This is classified `PRODUCT_GAP` per §7's own instruction: CPL's capabilities are
genuinely reusable common primitives (proven by 6 closed Build Units and 227/227 tests); what's missing is
exposure, not capability. No evidence anywhere suggests this exposure gap is itself a *common* capability
CPL lacks — it's a product-integration decision about how the orchestration layer talks to CPL (in-process
import vs. a future HTTP layer), addressed in §21/§28.

---

## 6. VIR entry-point analysis

```text
Runtime:      FastAPI + Uvicorn, Python >=3.12 (pyproject.toml)
Entry point:  uvicorn vir.api.routes:app  (src/vir/api/routes.py)
CLI:          `vir resolve --manufacturer <name> --model <name> --year <year>` (console_scripts entry point)
```

Routes (`src/vir/api/routes.py`, read directly):

```text
POST /v1/vehicle-identities/resolve                              → VehicleIdentityResolution   CONFIRMED
POST /v1/vehicle-identities/{resolution_id}/clarifications           → VehicleIdentityResolution   CONFIRMED
GET  /v1/vehicle-identities/{resolution_id}                             → VehicleIdentityResolution   CONFIRMED
GET  /v1/vehicle-identities/{resolution_id}/handoff/diagnostic             → DiagnosticIdentityContext   CONFIRMED
GET  /health                                                                   → {"status":"ok"}             CONFIRMED
```

Input contract (`VehicleIdentityRequest`, `src/vir/domain/models.py`): `request_id`, `locale`, `registration
{registration_number, country_code}`, `vin`, `manual_identity {...}`, `supporting_documents`, `consent
{external_lookup_allowed}`. All fields are user/product-originated — none require VIR-internal state to
construct.

**Note on staleness:** `RUNNER_EXECUTION_CONTRACT.md` (root-level doc) claims `persistent_store: NONE` and
that the handoff endpoint returns 501. This is **stale** — the actual current code (`src/vir/persistence.py`,
`src/vir/adapters/sqlite_persistence_adapter.py`, and `routes.py`'s use of `STORE`) shows a working SQLite-
backed store and a working handoff endpoint. Documentation was not trusted over source, per this
investigation's own evidence standard.

---

## 7. VIR output contract

`VehicleIdentityResolution` (`src/vir/domain/models.py`): `request_id`, `resolution_id`, `created_at`,
`resolution_status` (enum, 8 values — see §13), `confidence {score, level}`, `vehicle_identity`
(`CanonicalVehicleIdentity | None` — manufacturer/model/production/body/fuel/engine/transmission/
identifiers), `alternative_candidates`, `unresolved_fields`, `contradictions` (list of `Contradiction`
objects), `clarification_questions`, `field_evidence`, `source_summary`, `limitations`.

Structured, serializable (Pydantic `BaseModel`), persisted (SQLite via `STORE`), **not currently represented
as a CPL artifact anywhere** — no code in CPL, VIR, or PGDR converts this into a `RunnerArtifact`. This is
the first concrete `PI` candidate.

---

## 8. VIR → CPL mapping

| RunnerExecution field | Source | Classification |
|---|---|---|
| `case_id` | Product/orchestrator context (which Case this VIR call belongs to) | DEFAULT JUSTIFIED — orchestrator responsibility, not VIR's |
| `asset_id` | Product/orchestrator context (the Asset being identified) | DEFAULT JUSTIFIED |
| `runner_type` | Literal `"VIR"` | DIRECT MATCH (constant) |
| `runner_version` | VIR has no exposed version field on the resolution itself; `app.version` on the FastAPI app is `"0.1.0"` | TRANSFORM (orchestrator reads from a config/health value, not per-resolution) |
| `execution_purpose` | Orchestrator-assigned (e.g. `"vehicle_identity_resolution"`) | DEFAULT JUSTIFIED |
| `idempotency_key` | VIR's own `request_id` | DIRECT MATCH |
| `execution_status` | Derived from `resolution_status` (VIR call is synchronous; maps to `COMPLETED` on any HTTP 200 response, `FAILED` on VIR-side technical error) | TRANSFORM |

No `MISSING` field. Every RunnerExecution field is either a direct match or resolvable by the orchestrator
context — `EXISTS_NEEDS_ADAPTER`, not `COMMON_GAP`.

For `RunnerArtifact`: `payload` = `VehicleIdentityResolution.model_dump()` (direct, JSONB-compatible);
`artifact_type` = `"vir_resolution"`; `schema_name`/`schema_version` = a new registered definition (REQ-B6-089
mechanism, already built and tested in B6); `semantic_function` = `DOMAIN_DETERMINATION_CARRIER`;
`lifecycle_role` = `FINAL` (or `INTERMEDIATE` for a pre-clarification resolution — the orchestrator's
decision, both values already supported); `presentation_role` = product decision, `INTERNAL` by default.
CPL is **not** asked to determine VIR truth anywhere in this mapping — the artifact carries VIR's own
conclusion opaquely, per B6's own frozen discipline.

---

## 9. Asset/VIR identity connection

```text
app/cpl/models/asset_identity_resolution.py:
  resolution_status  CHECK IN ('RESOLVED','PARTIALLY_RESOLVED','AMBIGUOUS','CONTRADICTORY','UNRESOLVED','FAILED')
  confidence         NUMERIC(5,4)
  execution_id        FK -> runner_executions.execution_id
  canonical_identity_payload  JSONB NOT NULL
  provenance_payload  JSONB
  supersedes_resolution_id  self-FK

app/automotive/models/vehicle_detail.py:
  source_resolution_id  FK -> cpl.asset_identity_resolutions.resolution_id
```

This model pair is **already shaped for exactly this connection** — `execution_id` links a resolution to the
`RunnerExecution` that produced it; `canonical_identity_payload` is a natural target for VIR's
`CanonicalVehicleIdentity`; `VehicleDetail.source_resolution_id` closes the loop back to the resolution.
`app/cpl/assets/resolution.py::request_asset_identity_resolution`/`record_asset_identity_resolution` are the
existing write functions. **No write path exists yet for `VehicleDetail` itself** (no `create_vehicle_detail`-
style function found) — a small, non-semantic gap (`PRODUCT_GAP`, trivial adapter code, not a new CPL
primitive).

`resolution_status` vocabulary mismatch (TRANSFORM required, not a gap): VIR's 8-value enum vs. CPL's 6-value
enum — see §13 for the exact table.

```text
COMMON_GAP test: does existing CPL semantics genuinely fail to represent this relationship? NO — the model
pair was evidently designed for it. Classification: EXISTS_NEEDS_ADAPTER.
```

---

## 10. PGDR entry-point analysis

```text
Runtime:      Python, Click CLI (src/pgdr/cli.py) — a single-invocation CLI, not a long-running service.
CLI entry:    python3 run_pgdr.py run --vir-id ... --complaint ...   (or `pgdr run` if installed)
API:          ABSENT — docs/runner_execution_contract.md states explicitly: "interfaces.api.available: false"
Persistence:  ABSENT — same document: "No LLM, database, persistence layer, ... none of these exist in the
                codebase, and this phase doesn't add them."
```

**Load-bearing finding:** `pgdr.session_controller.SessionController` (`src/pgdr/session_controller.py`) has
zero interactive/TTY code (`grep` confirms no `input()`/`rich.prompt` calls in that file — those live only in
`cli.py`). Its public surface:

```text
SessionController.start(request: PreGarageDiagnosticRequest) -> DiagnosticSession       CONFIRMED, line 138
SessionController.submit_answer(session, answer: Answer) -> DiagnosticSession              CONFIRMED, line 189
SessionController.get_current_state(session) -> dict                                          CONFIRMED, line 275
```

This is a genuine, already-existing programmatic API — PGDR does not need an HTTP layer to be invoked by an
orchestrator; it needs to be `pip install`-ed (or path-imported, as `run_pgdr.py` does) and driven directly.
The CLI's interactivity is a thin UI wrapper around this class, not intrinsic to PGDR's core.

---

## 11. PGDR input contract

`PreGarageDiagnosticRequest` (`src/pgdr/models.py`): `request_id`, `locale`, `vehicle_identity_context`
(`VehicleIdentityContext`), `initial_complaint` (`InitialComplaint`), `user_context` (`UserContext`),
`evidence` (`list[Evidence]`), `consent` (`Consent`).

Source-of-origin for each top-level field:

| Field | Must originate from |
|---|---|
| `vehicle_identity_context` | VIR (explicitly — `pgdr/domain/identity.py`'s docstring: "the VIR input contract") |
| `initial_complaint` | User, via product/frontend |
| `user_context` | User/product context (driving status, technical level) |
| `evidence` | User/product (media, prior observations) — optional |
| `consent` | User, via product/frontend |

**VIR output is not sufficient alone** — confirmed directly, not assumed: `initial_complaint`, `user_context`,
and `consent` have no VIR analogue whatsoever and must come from the product layer. This is exactly the kind
of claim §14 requires be proven, not assumed, and it is proven here by reading the model definition.

`VehicleIdentityContext` itself (`src/pgdr/models.py`, confirmed):

```python
class VehicleIdentityContext(BaseModel):
    """Input contract only — the PGDR never reconstructs VIR logic (PGDR-ID-001)."""
    resolution_id: str
    resolution_status: ResolutionStatus
    confidence: Optional[ConfidenceScore] = None
    vehicle_identity: Optional[dict[str, Any]] = None
    unresolved_fields: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
```

---

## 12. PGDR output contract

`DiagnosticSession` (`src/pgdr/models.py`, line 316) carries `state: SessionState`, transition log, and
eventually a `garage_preparation_report: Optional[GaragePreparationReport]` (line 306, on the containing
result model). State machine (`src/pgdr/session_controller.py`, transitions read directly): `RECEIVED →
IDENTITY_RESOLUTION → COMPLAINT_ANALYSIS → IMMEDIATE_SAFETY_TRIAGE → (ESCALATED | SYMPTOM_COLLECTION) →
EVIDENCE_COLLECTION → CONTRADICTION_CHECK → REASONING → REPORT_GENERATION → COMPLETED`.

Findings/report: `GaragePreparationReport` — a garage-facing diagnostic output, governed through
`pgdr/governance/reporting.py::govern_and_build_result` before appearing in any final report (GGM
governance layer, confirmed present in `vendor/ggm-1.2.0-py3-none-any.whl`). Failure modes: `ESCALATED`
(safety-triggered terminal state, distinct from normal completion) is the one PGDR-specific terminal state
worth naming explicitly for CPL mapping purposes (§16).

Serialization: Pydantic `BaseModel`, directly JSONB-compatible. Persistence: **none** — PGDR produces this
in-memory only; if the orchestrator doesn't capture it, it's gone. **This is exactly the gap CPL's
`RunnerArtifact` exists to fill** — not a new CPL capability, but CPL's existing, closed B6 capability doing
precisely the job it was built for.

Direct-to-`RunnerArtifact`: yes, structurally — same reasoning as §8's `RunnerArtifact` mapping, with
`semantic_function = DOMAIN_DETERMINATION_CARRIER`, `artifact_type = "pgdr_garage_preparation_report"`.

---

## 13. PGDR → CPL mapping

`SessionState` → `execution_status` (`_TRANSITIONS` table already exists in `app/cpl/runners/execution.py`,
confirmed unchanged since B6 closure):

| PGDR `SessionState` | B6 `execution_status` | Classification |
|---|---|---|
| `RECEIVED` | `CREATED` | DIRECT MATCH |
| `IDENTITY_RESOLUTION` … `REASONING` (in progress) | `RUNNING` | TRANSFORM (collapse PGDR's internal phase granularity — domain detail, not CPL's concern) |
| Any phase awaiting `submit_answer()` | `BLOCKED` | DIRECT MATCH — B6's own `REQ-B6-012` defines BLOCKED as exactly this: materialized, cannot proceed pending a governed precondition. Already tested (`test_p21_blocked_transition_and_recovery`). |
| `COMPLETED` | `COMPLETED` | DIRECT MATCH |
| `ESCALATED` | `COMPLETED` | TRANSFORM — per B6's own frozen discipline (`REQ-B6-007`), execution completion is a representation fact, never a domain-truth claim; the escalation itself is domain content carried in the artifact payload/classification, not a new execution_status value. |

No `MISSING`. No new CPL execution-status value is required — B6's frozen 7-value vocabulary, closed months
before this investigation and unaware of PGDR's specific state names, already covers every case.

`RunnerArtifact` mapping: as §12. Both are `EXISTS_NEEDS_ADAPTER`, confirmed by direct reasoning against
already-tested CPL code, not assumption.

---

## 14. VIR → PGDR handoff

```text
VIR OUTPUT (DiagnosticIdentityContext)          PGDR INPUT (VehicleIdentityContext)
  resolution_id: str                        →     resolution_id: str                      DIRECT
  identity_status: ResolutionStatus         →     resolution_status: ResolutionStatus         TRANSFORMABLE (§below)
  vehicle: dict[str, Any]                   →     vehicle_identity: Optional[dict[str, Any]]     DIRECT
  diagnostic_constraints: dict[str, Any]    →     (no direct target — see note)                     MISSING* (see below)
  (n/a — VIR resolution's own field)        →     confidence: Optional[ConfidenceScore]                DERIVABLE — from resolution.confidence.score, available at the VehicleIdentityResolution level even though DiagnosticIdentityContext doesn't carry it directly; DiagnosticIdentityContext.diagnostic_constraints.confidence_score duplicates it
  (n/a)                                     →     unresolved_fields: list[str]                            AVAILABLE ELSEWHERE — on VehicleIdentityResolution directly, and echoed into diagnostic_constraints.unresolved_fields
  (n/a)                                     →     contradictions: list[str]                                   TRANSFORMABLE — VIR's Contradiction objects need flattening (e.g. to field_path strings)
```

`*MISSING` is qualified, not a gap: `diagnostic_constraints` (engine-code-known, factory-configuration-known,
confidence, unresolved fields, contradiction flag) has no single PGDR field target — it doesn't need one.
PGDR's `VehicleIdentityContext` is deliberately thin (per its own docstring, "the PGDR never reconstructs VIR
logic"); the richer `diagnostic_constraints` payload is exactly the kind of thing that stays in the CPL
`RunnerArtifact` (§8) as full provenance, while only the minimum PGDR actually asks for crosses the handoff.
This is a design confirmation, not a defect.

**Handoff mechanism (§18's own question, answered directly):** not `RunnerArtifact → RunnerArtifact`
coupling (correctly excluded already — B6's own frozen `REQ-B6-051` prohibits this). The evidenced mechanism
is: orchestrator reads VIR's `DiagnosticIdentityContext` (or the richer `VehicleIdentityResolution`) →
constructs a fresh PGDR `VehicleIdentityContext` via a pure mapping function → this is a **domain adapter /
product-integration service** function, exactly the category §18 anticipates as the answer, confirmed by
evidence rather than assumed.

---

## 15. Handoff provenance

Testing the required distinctions against B6's actual, closed, tested vocabulary:

```text
VIR execution PRODUCED artifact        → RunnerArtifact.execution_id            EXISTS_AND_USABLE
PGDR execution USED artifact/input     → no dedicated CPL field for this today  EXISTS_NEEDS_ADAPTER
PGDR artifact PRODUCED BY PGDR exec.   → RunnerArtifact.execution_id (PGDR's own execution)  EXISTS_AND_USABLE
Derived/reference relation (if needed) → RM-B6-03 (ExternalReference reuse) still DEFERRED, per B6 Closure
```

"PGDR execution USED artifact/input" is the one genuinely open item: CPL's B6 has `PRODUCED BY`
(`execution_id`) and `SUPERSEDES` (`supersedes_artifact_id`) as its two implemented relation types
(confirmed, `app/cpl/runners/artifacts.py`); `USED AS INPUT` was named in the frozen B6 WHAT/Requirements as
a *distinction to preserve*, not as a relation CPL was required to implement a dedicated column for — and it
wasn't. This is `EXISTS_NEEDS_ADAPTER`: representable today via the `RunnerGovernanceDecision.prior_value`/
`new_value` JSONB (already present, B6-built) recording which VIR artifact_id informed a given PGDR
execution's admission, without a new CPL schema element. **Tested against the anti-generalization bar (§25):
existing JSONB decision-record fields can carry this reference today — no new CPL column is required, so
this is not a `COMMON_GAP`.**

---

## 16. Case/execution composition

`Case.current_execution_id` (B5, confirmed unchanged) and `CaseEvent` already exist and are exactly the
opaque-reference mechanism this journey needs. Test result: **one `Case` can govern both executions** — CPL
never required them to be the same runner type, and B5's own frozen semantics (`Case ≠ RunnerExecution`,
confirmed still holding post-B6) treat `current_execution_id` as an opaque pointer regardless of which runner
produced it. `CaseParticipant` is usable if the product needs to represent, e.g., a garage participant later —
not required for the minimum path. No `CaseEvent` schema change needed; `append_case_event`-style functions
already exist per B5. **Case does not become a workflow engine** — it doesn't need to; the actual
orchestration state lives in the orchestrator's own code (§28's PI units), Case only records what happened.

---

## 17. Product API reality

```text
CPL:   /health, /ready only.                                                          ABSENT (product routes)
VIR:   /v1/vehicle-identities/{resolve, clarifications, get, handoff/diagnostic}, /health.   EXISTS_AND_USABLE (VIR-scoped only)
PGDR:  none.                                                                              ABSENT
```

No repository today exposes a unified journey. VIR's own API is real and usable for VIR's own scope, but
nothing composes it with CPL or PGDR. This entire row is `PRODUCT_GAP` — a new orchestration/API layer, not
a defect in any existing repository.

---

## 18. Frontend reality

```text
Searched: no frontend code, framework, or UI found in cpl, vir, or pgdr repositories.
FRONTEND: ABSENT
```

No evidence of an existing frontend anywhere. This investigation does not design one (per its own scope
limits) — it records the gap as `PRODUCT_GAP`, to be structured, not built, later.

---

## 19. End-to-end reality table

| Transition | Classification |
|---|---|
| USER → CONTACT | EXISTS_NEEDS_ADAPTER (CPL primitive exists, Python-import only) |
| CONTACT → ASSET | EXISTS_NEEDS_ADAPTER (CPL primitive exists, Python-import only) |
| ASSET → VIR | PRODUCT_GAP (orchestrator must call VIR's HTTP API; no existing wiring) |
| VIR → RUNNEREXECUTION | EXISTS_NEEDS_ADAPTER (§8) |
| VIR → RUNNERARTIFACT | EXISTS_NEEDS_ADAPTER (§8) |
| VIR RESULT → ASSET IDENTITY | EXISTS_NEEDS_ADAPTER (§9 — models purpose-built, no write path for VehicleDetail yet) |
| VIR ARTIFACT → PGDR INPUT | EXISTS_NEEDS_ADAPTER (§14 — near-direct field match) |
| PGDR → RUNNEREXECUTION | EXISTS_NEEDS_ADAPTER (§13) |
| PGDR → RUNNERARTIFACT | EXISTS_NEEDS_ADAPTER (§12/13) |
| CASE → EXECUTIONS | EXISTS_AND_USABLE (§16) |
| RESULT → PRODUCT API | PRODUCT_GAP (§17) |
| PRODUCT API → FRONTEND | PRODUCT_GAP (§18) |

**Zero `COMMON_GAP`. Zero `DOMAIN_GAP`. Zero `BLOCKED`.**

---

## 20. Gap register

```text
G-01  VIR->CPL mapping code absent           PRODUCT_GAP   → PI-01
G-02  VehicleDetail write path absent           PRODUCT_GAP   → PI-01
G-03  resolution_status vocabulary transform       PRODUCT_GAP   → PI-01 (table in §9/§13)
G-04  VIR->PGDR field mapper absent                   PRODUCT_GAP   → PI-02
G-05  PGDR session <-> CPL execution wrapper absent      PRODUCT_GAP   → PI-03
G-06  "USED AS INPUT" relation has no dedicated column      EXISTS_NEEDS_ADAPTER (JSONB decision record suffices) → PI-03
G-07  Case orchestration entry point absent                    PRODUCT_GAP   → PI-04 (fills CPL's own automotive/orchestration/__init__.py placeholder)
G-08  Product API absent                                          PRODUCT_GAP   → PI-05
G-09  Frontend absent                                                PRODUCT_GAP   → PI-06 (structuring only, not built here)
```

No `COMMON_GAP` line exists in this register — none was found.

---

## 21. COMMON_GAP analysis

None found. Every candidate examined (execution-status vocabulary for PGDR's states, an artifact relation
type for "used as input", CPL's lack of an HTTP API) resolved to `EXISTS_AND_USABLE` or `EXISTS_NEEDS_ADAPTER`
under the anti-generalization test (§25): for each, a strong evidence-based answer exists for *why* it's not
a CPL gap — either the primitive already exists and is tested (execution-status, decision-record JSONB), or
the missing piece is a Python-level import/exposure choice with no bearing on CPL's own governed semantics
(the HTTP-API question). `CPL_REOPEN_REQUIRED = NO` follows directly.

---

## 22. DOMAIN_GAP analysis

None found requiring CPL or orchestrator attention. VIR's providers are all in-memory stubs (confirmed,
`RUNNER_EXECUTION_CONTRACT.md` §Provider Requirements — "none_are_network_backed: true") — this is a real
limitation for a production deployment, but it is entirely VIR's own domain scope to resolve (real provider
adapters), not something this product-integration investigation is authorized or positioned to solve. Noted,
not solved, per this investigation's own scope.

---

## 23. PRODUCT_GAP analysis

Nine items in the gap register (§20), all `PRODUCT_GAP` or reducible to trivial adapter code. All are
addressed by PI-01 through PI-06 (§28). None require touching CPL, VIR, or PGDR's own repositories — every PI
unit lives in a new orchestration layer that *consumes* all three as dependencies (VIR over HTTP; CPL and
PGDR as installed Python packages, since both already have real, tested, non-interactive programmatic
entry points).

---

## 24. Minimum operational product path

```text
1. Contact/Asset/Case exist in CPL (create_contact, create_asset, create_case — all closed, tested)
2. Orchestrator calls VIR: POST /v1/vehicle-identities/resolve
3. Orchestrator writes the VIR call into CPL: admit_execution + register_artifact + record_asset_identity_resolution
4. Orchestrator maps VIR's handoff context into PGDR's VehicleIdentityContext
5. Orchestrator drives PGDR: SessionController.start() -> [submit_answer() loop] -> COMPLETED
6. Orchestrator writes the PGDR run into CPL: admit_execution + transition_status(BLOCKED/RUNNING as needed) +
   persist_runner_report(COMPLETED) + register_artifact(GaragePreparationReport)
7. Result retrievable from CPL by execution_id / case_id
```

No step above requires code changes inside `cpl`, `vehicle-identity-resolver`, or `pgdr`. Every step is new
orchestration code calling existing, already-tested entry points.

---

## 25. PI build-unit candidates

See §28 (Product Integration Build Plan) — the candidates are specified there directly, per this
investigation's own stop condition (§32 of the instruction): one document, no second study.

---

## 26. CPL reopening decision

```text
CPL_REOPEN_REQUIRED = NO
```

No evidenced `COMMON_GAP` exists (§21).

---

## 27. B7 candidacy decision

```text
B7_REQUIRED = NOT_DEMONSTRATED
```

`B7_CANDIDACY_DEMONSTRATED` requires an evidenced `COMMON_GAP`; none exists. This matches exactly the
epistemic boundary the B6 Closure Record already set: *"no additional common CPL blocker is currently
identified... [not] a guarantee about what a real integration pass will find."* This investigation is that
real integration pass, for the currently-scoped product journey, and it found none.

---

## 28. Product Integration Build Plan

All PI units live in a **new repository** (name not fixed by this investigation — e.g. `cpl-product-
integration`), which depends on `cpl` and `pgdr` as installed Python packages and calls `vir` over HTTP. No
existing repository is modified.

```text
PI-01 — VIR Integration (client + CPL registration)
Repository:   NEW (product-integration)
Purpose:      Call VIR's real HTTP API and represent the call as governed CPL state.
Reuses:       VIR: POST /v1/vehicle-identities/resolve, POST .../clarifications,
              GET .../handoff/diagnostic (all confirmed working, §6).
              CPL: app.cpl.assets.creation.create_asset,
              app.cpl.assets.resolution.{request_asset_identity_resolution,record_asset_identity_resolution},
              app.cpl.runners.execution.{admit_execution,persist_runner_report},
              app.cpl.runners.artifacts.register_artifact.
Build:        (a) async HTTP client wrapping VIR's 4 endpoints; (b) resolution_status transform table
              (VIR's 8 values -> CPL AssetIdentityResolution's 6, §9); (c) a small VehicleDetail write
              function (none exists today, G-02); (d) RunnerArtifact schema registration for "vir_resolution"
              (uses B6's existing REQ-B6-089 registry mechanism).
Input:        VehicleIdentityRequest fields (from product/frontend, once it exists) or a direct call for
              this PI unit's own testing.
Output:       CPL rows: RunnerExecution, RunnerArtifact, AssetIdentityResolution, VehicleDetail — all linked.
Depends on:   none (VIR is already runnable; CPL is already closed).
Tests:        real Postgres integration test, VIR run in-process (its own TestClient) or as a live process.
Done when:    a captured VIR resolution deterministically produces the full linked CPL row set, verified
              against real Postgres.

PI-02 — VIR -> PGDR Handoff Mapper
Repository:   NEW (product-integration)
Purpose:      Pure function: VIR's DiagnosticIdentityContext -> PGDR's VehicleIdentityContext.
Reuses:       VIR's DiagnosticIdentityContext (read), PGDR's VehicleIdentityContext (construct) — both
              already-defined Pydantic models, no changes to either repo.
Build:        Field mapping per §14's table; contradiction-object flattening; a resolution_status pass-through
              validated against PGDR's own 5-value enum (a strict subset of VIR's 8 — the 3 VIR-only values
              represent "VIR couldn't attempt resolution," which this mapper explicitly refuses to forward,
              raising instead of guessing).
Input:        A VIR DiagnosticIdentityContext (or VehicleIdentityResolution for the richer confidence path).
Output:       A valid PGDR VehicleIdentityContext.
Depends on:   PI-01 (needs VIR's real response shape) — can be built in parallel once PI-01's contract is
              known; does not depend on PI-01's code.
Tests:        pure unit tests, no I/O — exhaustive over VIR's 8 status values including the 3 refused ones.
Done when:    every real VIR DiagnosticIdentityContext this investigation observed maps to a
              Pydantic-valid PGDR VehicleIdentityContext, or is explicitly and correctly refused.

PI-03 — PGDR Session Adapter (CPL-governed)
Repository:   NEW (product-integration)
Purpose:      Drive PGDR's SessionController programmatically; represent the multi-turn session as a governed
              CPL RunnerExecution; persist the final GaragePreparationReport (PGDR itself persists nothing).
Reuses:       PGDR: pgdr.session_controller.SessionController.{start,submit_answer,get_current_state}
              (all confirmed non-interactive, §10).
              CPL: app.cpl.runners.execution.{admit_execution,transition_status,persist_runner_report},
              app.cpl.runners.artifacts.register_artifact.
Build:        SessionState -> execution_status mapping (§13's table, including ESCALATED -> COMPLETED);
              a loop that calls submit_answer() while PGDR needs more input, transitioning CPL's execution
              through BLOCKED/RUNNING as appropriate; RunnerArtifact schema registration for
              "pgdr_garage_preparation_report"; a JSONB decision-record note capturing which VIR artifact_id
              informed this PGDR execution (§15, closes G-06 without new CPL schema).
Input:        A PGDR VehicleIdentityContext (from PI-02) plus user-originated InitialComplaint/UserContext/
              Consent (§11 — not from VIR).
Output:       CPL rows: RunnerExecution (VIR's sibling under the same Case), RunnerArtifact
              (GaragePreparationReport).
Depends on:   PI-02 (needs the mapped input shape).
Tests:        real Postgres + a real, fully scripted (non-interactive) PGDR session run end-to-end, including
              at least one BLOCKED/submit_answer cycle and one ESCALATED-path run.
Done when:    a full PGDR diagnostic session, driven programmatically, produces exactly one terminal
              RunnerExecution and one associated GaragePreparationReport RunnerArtifact in real Postgres.

PI-04 — Case Orchestration Service
Repository:   NEW (product-integration)
Purpose:      The actual product entry point — sequence VIR then PGDR under one governed Case. This is the
              literal implementation of app/automotive/orchestration/__init__.py's own existing placeholder
              (register_vehicle_for_contact, resolve_vehicle_identity, start_vehicle_diagnostic,
              continue_vehicle_diagnostic) — CPL's own prior planning already named this shape.
Reuses:       CPL: app.cpl.identity.contacts.{get_contact,create_contact}, app.cpl.assets.creation.create_asset,
              app.cpl.cases.lifecycle.{create_case,transition_case_status}.
              This PI unit: PI-01, PI-02, PI-03 in full.
Build:        The four orchestration functions named above; Case.current_execution_id sequencing across the
              VIR-then-PGDR pair.
Input:        User registration + vehicle identifier(s) + complaint text + consent.
Output:       One Case governing two linked RunnerExecutions and their artifacts, retrievable end to end.
Depends on:   PI-01, PI-03.
Tests:        full real-Postgres end-to-end integration test, Contact through final report.
Done when:    one function call produces the complete governed journey in real Postgres.

PI-05 — Product API
Repository:   NEW (product-integration), FastAPI app
Purpose:      HTTP-expose PI-04. Account/contact, vehicle registration, case creation, VIR invocation
              (including clarification submission), PGDR invocation (including answer submission), execution
              status polling, artifact/result retrieval, history.
Reuses:       PI-04 entirely.
Build:        FastAPI routes + request/response schemas wrapping PI-04's functions.
Depends on:   PI-04.
Tests:        httpx-based API integration tests, real Postgres.
Done when:    the entire journey is drivable via HTTP alone.

PI-06 — Frontend Journey (structuring only)
Repository:   NEW (frontend, TBD framework — UNDETERMINED, no existing evidence to build from)
Purpose:      Thin UI over PI-05: registration form -> VIR result/clarification screen -> PGDR
              complaint/question screens -> result/history screen.
Reuses:       PI-05's API entirely.
Build:        Not specified here — structuring only, per this investigation's own scope limit (§18, §37 of
              the instruction: do not design frontend during Reality Check).
Depends on:   PI-05.
Tests:        not specified at this stage.
Done when:    a real user completes the full journey through a browser.
```

---

## 29. Dependency DAG

```text
PI-01
  ├──> PI-02 ──> PI-03 ──┐
  └───────────────────────┼──> PI-04 ──> PI-05 ──> PI-06
```

Derived from repository evidence: PI-02 and PI-03 both require PI-01's confirmed VIR response shape before
their own contracts can be finalized, but PI-01's CPL-registration half (writing VIR's result into CPL) has
no dependency on PI-02/PI-03 and can proceed once VIR's shape is known. PI-04 requires both the VIR-side
(PI-01) and PGDR-side (PI-03, which itself needs PI-02) chains complete.

---

## 30. Parallelization

```text
Wave 1: PI-01                                    SEQUENTIAL (foundational — nothing else can start meaningfully
                                                   without VIR's confirmed response shape)
Wave 2: PI-02                                    PARALLEL with continuing PI-01 CPL-write work once VIR's
                                                   shape is confirmed
Wave 3: PI-03                                    BLOCKED_BY PI-02
Wave 4: PI-04                                    BLOCKED_BY PI-01, PI-03
Wave 5: PI-05                                    BLOCKED_BY PI-04
Wave 6: PI-06                                    BLOCKED_BY PI-05 (structuring only in this phase)
```

Two independent AI-coder tracks are safe from Wave 2 onward: one on PI-02→PI-03 (the PGDR-facing chain), one
finishing PI-01's CPL-write half in parallel, converging at PI-04.

---

## Stop-condition verification

```text
PRODUCT_PATH:        DETERMINED
GAPS:                CLASSIFIED
COMMON_BLOCKERS:     KNOWN (zero)
BUILD_UNITS:         IDENTIFIED (6: PI-01..PI-06)
DEPENDENCIES:        IDENTIFIED
BUILD_ORDER:         DETERMINED
```

Investigation is complete per its own stop condition. No further architectural exploration follows.

---

## CPL / VIR / PGDR PRODUCT INTEGRATION REALITY CHECK

```text
CPL OBSERVED:
  1836a2c6bf54bd9fa83f88a94077dec5b0fd1abd

VIR OBSERVED:
  a342aba7cc2fc517621f4fc79c3191bdfdc9e10b

PGDR OBSERVED:
  0580b1a5ba5867a607a33197372fcaf4164f0fb6

TARGET:
  FIRST OPERATIONAL VIR/PGDR PRODUCT

PRODUCT PATH:
  DETERMINED

CPL CAPABILITIES:
  Rich, tested, closed (B1-B6) internal Python service layer; zero product-facing API beyond /health,/ready

VIR ENTRY POINT:
  POST /v1/vehicle-identities/resolve (FastAPI, SQLite-backed, real handoff endpoint already built for PGDR)

PGDR ENTRY POINT:
  pgdr.session_controller.SessionController (programmatic, non-interactive, zero persistence)

VIR → CPL:
  EXISTS_NEEDS_ADAPTER

VIR → PGDR:
  EXISTS_NEEDS_ADAPTER (near-direct field match — both sides were evidently built expecting each other)

PGDR → CPL:
  EXISTS_NEEDS_ADAPTER

CASE COMPOSITION:
  EXISTS_AND_USABLE

PRODUCT API:
  ABSENT

FRONTEND:
  ABSENT

COMMON GAPS:
  0

DOMAIN GAPS:
  0

PRODUCT GAPS:
  9 (G-01..G-09)

BLOCKERS:
  0

CPL_REOPEN_REQUIRED:
  NO

B7_REQUIRED:
  NOT_DEMONSTRATED

PI BUILD UNITS:
  6 (PI-01..PI-06)

BUILD WAVES:
  6

MINIMUM PRODUCT BUILD PLAN:
  READY

FINAL VERDICT:
  PRODUCT_FRONTIER_READY

NEXT ACTION:
  execute Product Integration Build Plan
```

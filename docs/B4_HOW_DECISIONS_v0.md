# B4 Candidate — HOW Decisions (Documented, Not Governance Deviations)

Two implementation-architecture questions were resolved during the B4
candidate build. Both were checked against the frozen B4 WHAT and
frozen Requirement Matrix before being decided; neither introduces new
normative semantics, so neither is a `GOVERNANCE_DEVIATION`.

## 1. VehicleDetail vs. generic DomainProjection

**Question:** Should the existing (B2-accepted) `automotive.vehicle_details`
table be wired into the new generic `cpl.domain_projections` lifecycle
table, or kept decoupled?

**Frozen corpus check:**
- `B4_WHAT_CONSOLIDATION_v0.1.md` §43 gives `Asset -> VehicleDetail` only
  as an *illustrative example* of what a Domain Projection conceptually is.
- §44 (`C-B4-06`) states explicitly: **"The exact representation remains
  domain-specific."** — the WHAT deliberately declines to mandate a
  specific storage representation.
- `REQ-B4-096` through `REQ-B4-103` (Requirement Matrix) require that
  *the system* support projection distinctness, provenance, history-
  preserving update/supersession, and non-arbitrated conflict — none of
  them name `VehicleDetail` or require any particular table to be the
  vehicle for those properties.
- `B4_EXECUTION_MANDATE_v0.md` §8/§9 lists "VIR implementation" as
  prohibited scope expansion and requires B1/B2/B3 accepted behavior to
  be preserved unmodified.

**Decision (HOW, not WHAT):** `cpl.domain_projections` is the generic
CPL governance layer that satisfies `REQ-B4-096..103`. `VehicleDetail`
remains exactly as B2 left it — a single-row-per-Asset automotive
payload table, untouched by this candidate. No frozen requirement forces
these two to be wired together, and doing so would mean either (a)
retrofitting `VehicleDetail` with lifecycle/history columns — a B2
schema change with no B4 requirement demanding it and every reason
(Mandate §46, "unrelated dependency churn is prohibited") not to do it
casually — or (b) having generic CPL write automotive-specific payload
shape into `domain_projections.payload`, which would mean generic B4
code encoding VIR-specific knowledge, contradicting the domain/CPL
boundary (`B4-CI32`). Leaving them decoupled satisfies the frozen
requirements with the least invented architecture.

## 2. B4-specific HTTP routes

**Question:** Does B4 need new HTTP/REST routes exposing its
functionality?

**Frozen corpus check:**
- No requirement in `REQ-B4-001` → `REQ-B4-260` mentions HTTP, an
  endpoint path, a verb, or a route.
- `B4_WHAT_CONSOLIDATION_v0.1.md` §54 ("Operation surface caution")
  states operation families "are semantic operation families, not
  required HTTP endpoints or method names."
- Requirement Matrix §29 explicitly lists "API path" among items that
  "belong downstream" (HOW, not WHAT).
- **Direct project precedent:** B3, which implemented 14 governed
  identity primitives under an equally strict Execution Mandate, added
  **zero** HTTP routes — `app/api/__init__.py` remains "a placeholder"
  and all B3 functionality is exposed only as Python service functions
  under `app.cpl.identity.*`. Only `/health` and `/ready` (from B1)
  exist as routes anywhere in the accepted codebase.

**Decision (HOW, not WHAT):** No B4 HTTP routes were added, for
consistency with the established B3 pattern and because no frozen
requirement mandates a transport surface. All B4 functionality is
exposed as service functions under `app.cpl.assets.*`, mirroring
`app.cpl.identity.*` exactly.

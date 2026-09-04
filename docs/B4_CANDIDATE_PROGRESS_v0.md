# B4 Candidate — Progress Report (WIP Checkpoint)

**Status: IN PROGRESS — NOT COMPLETE. This is a WIP checkpoint commit, not a final candidate.**

Per `B4_EXECUTION_MANDATE_v0.md` Sec. 50 (Phantom-commit prohibition) and
Sec. 57 (verification is not acceptance by assertion), this report makes
no claim of `CANDIDATE_COMPLETE`. Everything below is either (a) verified
by actually running it against real PostgreSQL in this session, or (b)
explicitly marked as not yet done.

- Repository: `paxtonef/cpl`
- Mandated code baseline: `2ec1e60d24487e74efb4c8a64885652215939631` (verified ancestor, `b4-candidate` created exactly there)
- Migration head at this checkpoint: `024`
- Full regression at this checkpoint: **134 / 134 passing** (106 B1–B3 baseline + 28 new B4) against real PostgreSQL 16
- `/health`, `/ready`: both verified passing on this schema
- Migration upgrade **and** downgrade round-trip verified for 022→024

## Implemented and test-verified this checkpoint

| Area | REQ range | Status |
|---|---|---|
| Migrations 022–024 | — | clean up/downgrade round-trip verified |
| Asset merge admission/execution | REQ-B4-047–060 | implemented, tested (positive + negative) |
| Survivor selection (governed precedence) | REQ-B4-070–077 | implemented, tested incl. override-without-reason → HOLD |
| Dependency-disposition closure | REQ-B4-078–086, 246–249 | implemented, tested (missing family → HOLD, REJECT_CONFLICT → CONFLICTING) |
| Asset correction (supersession) | REQ-B4-061–069 | implemented, tested — original MERGE decision preserved untouched |
| Canonical decision/effect consistency | REQ-B4-241–245 | implemented; **verified under actual injected failure** (SAVEPOINT-based test forcing `IntegrityError` mid-transaction — no partial state visible after rollback) |
| Asset merge/correction idempotency | REQ-B4-250, 251, 253, 254 | implemented, tested (replay returns original decision) |
| AssetIdentityResolution outcome separation | REQ-B4-025–036, 162–171 | implemented, tested — AMBIGUOUS/CONTRADICTORY/UNRESOLVED/FAILED all distinct, technical FAILED never reinterpreted as a domain outcome |
| ContactAssetRelationship: ESTABLISH/END/CORRECT/SUPERSEDE | REQ-B4-104–132 | implemented, tested |
| Relationship valid-time/decision-time distinction | REQ-B4-133–141 | implemented, tested (CORRECT supersedes prior decision's current effect, history preserved) |
| Relationship idempotency | REQ-B4-150–154 | implemented (same idempotency-key mechanism as Asset side) |
| Relationship cardinality/conflict (policy-driven) | REQ-B4-155–161 | implemented, tested — no universal cardinality invented; SOLE policy example tested |
| Historical vs. current navigation | REQ-B4-255–260 | implemented, tested for both ContactAssetRelationship and ExternalReference after Asset merge |
| ExternalReference lifecycle | REQ-B4-087–095 | implemented, tested (supersede preserves historical row, invalidate) |
| DomainProjection lifecycle (generic) | REQ-B4-096–103 | implemented, tested — conflicting CURRENT projections reported as `DOMAIN_RECONCILIATION_REQUIRED`, never arbitrated by CPL |
| Authority denial | REQ-B4-056 | tested — weak authority context raises `AuthorityDeniedError` before any mutation |
| Non-regression B1/B2/B3 | REQ-B4-200–209 | 106/106 original tests still pass unmodified; migrations 001–021 untouched |

## NOT done yet — explicitly deferred, not silently dropped

- **AssetIdentifier lifecycle service layer** (REQ-B4-015–024): the B2 schema/model exists; no B4-specific supersede/invalidate service functions written yet (mirrors what was done for ExternalReference).
- **Asset creation admission service** (REQ-B4-009–014) as a distinct governed function — Assets are currently created directly via the ORM in tests; no `create_asset` admission wrapper with idempotency exists yet.
- **AssetIdentityResolution request/consume service functions** (REQ-B4-182–192, the `request_asset_identity_resolution` / `record_asset_identity_resolution` / `evaluate_asset_resolution_admissibility` operation family from the frozen WHAT's FR-B4-02 repair) — resolutions are currently inserted directly in tests; the governed request/consume wrapper functions described in the WHAT are not yet implemented.
- **Full requirement-by-requirement traceability matrix** for all 260 requirements (REQ-B4-210) — this report groups by family; it is not a line-by-line REQ-B4-001→260 mapping.
- **B4-specific FastAPI routes** — all B4 functionality so far is at the service layer only; no HTTP surface has been added.
- Automotive-specific `VehicleDetail` integration with the new generic `DomainProjection` governance table — they currently coexist unconnected; wiring VIR's existing vehicle_details rows into `domain_projections` (or deciding they remain deliberately separate) is an open decision, not yet made.

## Known limitations

- `assess_relationship_compatibility`'s cardinality policy is evaluated at call time only — there is no enforcement hook wired into `establish_relationship` itself yet (a caller must invoke the check separately before establishing).
- Test coverage for relationship-side negative cases (evidence-without-authority, relationship-does-not-grant-authorization) is not yet written, though the positive/idempotent/supersede paths are.

## Governance deviations

NONE. No frozen WHAT or requirement semantics were reinterpreted; all implementation choices made (survivor "established" = earlier `created_at`, dependency families list, SOLE-cardinality policy shape) are HOW decisions within the frozen WHAT's explicitly-left-open bounds.

## This is not yet a candidate for independent verification

This checkpoint is committed to `b4-candidate` for durability and visibility, not as a submission for DevOps verification under Mandate Sec. 56–58. No `B4_CANDIDATE_SHA` is being declared as final. Further implementation work is needed before that gate.

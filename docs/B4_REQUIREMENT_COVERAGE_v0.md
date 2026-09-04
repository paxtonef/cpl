# B4 Candidate — Requirement Coverage Evidence (REQ-B4-001 → REQ-B4-260)

Generated against candidate commit built on `b4-candidate` (checkpoint `8abca66` + continuation).

Evidence classes, per Mandate Sec. 52/23 ("no requirement may silently
disappear"; "a one-test-per-requirement structure is NOT required"):

- **DIRECT** — the requirement ID is explicitly cited in a docstring/comment
  next to the implementing code and/or an asserting test.
- **STRUCTURAL** — satisfied by schema/architecture design that makes
  violation impossible without a separate code change (e.g. Asset.asset_id
  being the sole PK, independent of AssetIdentifier rows).
- **REGRESSION-SUITE** — evidenced by the full B1/B2/B3/B4 suite passing
  unmodified (specifically the non-regression and full-suite-execution
  families, F23/F24, which are properties *of the test run itself*, not
  of any single function).


---

## F01 Asset identity/continuity  (`REQ-B4-001` – `REQ-B4-008`, 8 requirements)

**Evidence class:** STRUCTURAL

**Evidence:** Asset.asset_id is the sole PK; AssetIdentifier is a separate FK-linked table (app/cpl/models/asset.py, asset_identifier.py). Multiple unresolved candidate Assets coexisting: tests/test_b4_negative.py test_n01-n04 (two Assets, AMBIGUOUS/CONTRADICTORY/UNRESOLVED/FAILED all block convergence).

## F02 Asset creation  (`REQ-B4-009` – `REQ-B4-014`, 6 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/creation.py; tests/test_b4_second_pass.py::TestAssetCreationAdmission (4 tests).

## F03 AssetIdentifier lifecycle  (`REQ-B4-015` – `REQ-B4-024`, 10 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/identifiers.py; tests/test_b4_second_pass.py::TestAssetIdentifierLifecycle (5 tests).

## F04 AssetIdentityResolution  (`REQ-B4-025` – `REQ-B4-036`, 12 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/resolution.py; tests/test_b4_second_pass.py::TestAssetIdentityResolutionOperationFamily; tests/test_b4_negative.py (AMBIGUOUS/CONTRADICTORY/UNRESOLVED/FAILED distinction).

## F05 CanonicalAssetIdentityDecision  (`REQ-B4-037` – `REQ-B4-046`, 10 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/models/canonical_asset_identity_decision.py + app/cpl/assets/merge.py::_record_decision; tests/test_b4_positive.py test_p03/p05.

## F06 Asset merge admission/execution  (`REQ-B4-047` – `REQ-B4-060`, 14 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/merge.py::admit_and_execute_asset_merge; tests/test_b4_positive.py, test_b4_negative.py (11 tests combined).

## F07 Asset correction  (`REQ-B4-061` – `REQ-B4-069`, 9 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/merge.py::correct_asset_identity; tests/test_b4_positive.py test_p05.

## F08 Survivor selection  (`REQ-B4-070` – `REQ-B4-077`, 8 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/merge.py::_select_survivor; tests/test_b4_positive.py test_p02/p06, test_b4_negative.py test_n08.

## F09 Dependency disposition  (`REQ-B4-078` – `REQ-B4-086`, 9 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/merge.py (MATERIAL_DEPENDENCY_FAMILIES, ALLOWED_DISPOSITIONS); tests/test_b4_negative.py test_n06/n07.

## F10 ExternalReference  (`REQ-B4-087` – `REQ-B4-095`, 9 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/external_references.py, navigation.py; tests/test_b4_positive.py test_p10, test_b4_additional.py::TestB4ExternalReference.

## F11 DomainProjection  (`REQ-B4-096` – `REQ-B4-103`, 8 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/projections.py; tests/test_b4_additional.py::TestB4DomainProjection.

## F12 Relationship identity  (`REQ-B4-104` – `REQ-B4-110`, 7 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/models/contact_asset_relationship.py (pre-existing B2 schema, logical relationship_id independent of endpoints) + app/cpl/assets/navigation.py; tests/test_b4_positive.py test_p09/p11.

## F13 Relationship authority  (`REQ-B4-111` – `REQ-B4-119`, 9 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/relationships.py::establish_relationship; tests/test_b4_positive.py test_p07, test_b4_additional.py negative cases.

## F14 CanonicalRelationshipDecision  (`REQ-B4-120` – `REQ-B4-132`, 13 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/models/canonical_relationship_decision.py + app/cpl/assets/relationships.py (ESTABLISH/END/CORRECT/SUPERSEDE); tests/test_b4_positive.py test_p08, test_b4_additional.py::TestB4RelationshipSupersedeAndCardinality.

## F15 Relationship time/lifecycle  (`REQ-B4-133` – `REQ-B4-141`, 9 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/relationships.py::correct_relationship_valid_time (valid_from/valid_until vs decided_at); tests/test_b4_positive.py test_p08.

## F16 Endpoint evolution  (`REQ-B4-142` – `REQ-B4-149`, 8 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/navigation.py; tests/test_b4_positive.py test_p09/p11 (Asset-side and simultaneous Contact+Asset evolution).

## F17 Relationship idempotency  (`REQ-B4-150` – `REQ-B4-154`, 5 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/relationships.py (RelationshipMutationRequest idempotency ledger, same pattern as Asset side); architecture shared with REQ-B4-250-254 (directly tested there).

## F18 Cardinality/conflict  (`REQ-B4-155` – `REQ-B4-161`, 7 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/relationships.py::assess_relationship_compatibility, integrated into establish_relationship; tests/test_b4_additional.py + test_b4_second_pass.py::TestIntegratedCardinality.

## F19 Outcomes/failures  (`REQ-B4-162` – `REQ-B4-171`, 10 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/outcomes.py (B4Outcome, TechnicalFailureError); tests/test_b4_negative.py test_n01-n04 (AMBIGUOUS/CONTRADICTORY/UNRESOLVED/FAILED all distinct outcomes).

## F20 Provenance/history  (`REQ-B4-172` – `REQ-B4-181`, 10 requirements)

**Evidence class:** STRUCTURAL

**Evidence:** CanonicalAssetIdentityDecision.supersedes_decision_id / CanonicalRelationshipDecision.supersedes_decision_id chains preserve prior rows (never UPDATE-in-place, never DELETE) — exercised by test_p05 (Asset correction preserves original MERGE decision + resolution), test_p08 (relationship CORRECT chains to prior END decision), TestAssetIdentifierLifecycle::test_supersede_preserves_history, TestB4ExternalReference::test_supersede_preserves_historical_row, TestB4DomainProjection::test_attach_and_supersede_preserves_history.

## F21 Domain/CPL boundaries  (`REQ-B4-182` – `REQ-B4-192`, 11 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/resolution.py (request/record/evaluate_admissibility never determines identity itself); tests/test_b4_second_pass.py::TestAssetIdentityResolutionOperationFamily, TestRelationshipNegativeCoverage::test_domain_resolver_cannot_directly_mutate_canonical_topology.

## F22 B3 compatibility  (`REQ-B4-193` – `REQ-B4-199`, 7 requirements)

**Evidence class:** STRUCTURAL

**Evidence:** app/cpl/assets/navigation.py::current_contact_id mirrors Contact.merged_into_id (B3's own mechanism) without touching contacts table; directly exercised by test_p11 (simultaneous Contact+Asset evolution) and test_p09.

## F23 Non-regression  (`REQ-B4-200` – `REQ-B4-209`, 10 requirements)

**Evidence class:** REGRESSION-SUITE

**Evidence:** All 106 original B1/B2/B3 tests pass byte-for-byte unmodified in the full suite run (152/152 total); migrations 001-021 are untouched on disk (only 022-025 added); B4 schema changes are exclusively additive (new tables + nullable new columns + widened CHECK constraints, no destructive ALTER).

## F24 Verification/evidence  (`REQ-B4-210` – `REQ-B4-240`, 31 requirements)

**Evidence class:** REGRESSION-SUITE + DIRECT

**Evidence:** Existence of required test categories: positive (test_b4_positive.py, 11), negative (test_b4_negative.py, 10), idempotency (test_p04, test_create_asset_idempotent_replay), correction (test_p05), survivor precedence+override (test_p02/p06/n08), dependency-disposition (test_n06/n07), ExternalReference historical target (test_p10), conflicting DomainProjection (TestB4DomainProjection), relationship co-existence/conflict (TestIntegratedCardinality), END vs CORRECT (test_p08), valid/decision-time reconstruction (test_p08), idempotent replay (test_p04 + relationship equivalents), endpoint evolution incl. simultaneous (test_p09/p11), clean install (fresh-DB migration verified this session), migration from B3 head 021 (verified this session), full regression against real PostgreSQL (152/152, this session).

## RM-B4-01 Decision/effect consistency  (`REQ-B4-241` – `REQ-B4-245`, 5 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/merge.py (single-transaction decision+effect flush); tests/test_b4_additional.py::TestB4FailureConsistency — actual injected IntegrityError via SAVEPOINT, proving no partial transition survives rollback.

## RM-B4-02 Dependency-disposition closure  (`REQ-B4-246` – `REQ-B4-249`, 4 requirements)

**Evidence class:** DIRECT (246/247) + STRUCTURAL (248/249)

**Evidence:** tests/test_b4_negative.py test_n06/n07 directly test 246/247. REQ-B4-248 (no implicit default) is structural: the code has no default-disposition branch at all — missing/invalid dispositions always produce HOLD, never a silent default. REQ-B4-249 (evidence of disposition) is structural: dependency_disposition dict is stored verbatim in CanonicalAssetIdentityDecision.dependency_disposition (JSONB column).

## RM-B4-03 Transition idempotency  (`REQ-B4-250` – `REQ-B4-254`, 5 requirements)

**Evidence class:** DIRECT (250-253) + STRUCTURAL (254)

**Evidence:** test_p04 (merge replay). REQ-B4-254 (payload similarity alone insufficient) is structural: the idempotency lookup key is exclusively the caller-supplied idempotency_key string (AssetMergeRequest PK) — there is no code path that derives a match from asset_a_id/asset_b_id/resolution_id equality; directly analogous test exists on the Asset-creation side (test_distinct_keys_same_payload_create_distinct_assets).

## RM-B4-04 Historical/current navigation  (`REQ-B4-255` – `REQ-B4-260`, 6 requirements)

**Evidence class:** DIRECT

**Evidence:** app/cpl/assets/navigation.py; tests/test_b4_positive.py test_p09/p10/p11 (ContactAssetRelationship, ExternalReference, and simultaneous dual-endpoint cases).


---

## Summary

```text
Total requirements:        260 (REQ-B4-001 -> REQ-B4-260)
Requirements unaccounted:  0
DIRECT evidence:           ~21 of 28 family blocks (majority of requirements)
STRUCTURAL evidence:       F01, F20, F22 (basic invariants, supersession-chain
                            history, B3-compat — all satisfied by architecture,
                            not absence of testing)
REGRESSION-SUITE evidence: F23, F24 (non-regression + verification-category
                            existence — these are properties of the whole
                            suite run, not any single function)

Full suite at this checkpoint: 152 / 152 passing (106 B1-B3 baseline + 46 new B4)
```

"""Asset canonical merge admission/execution, survivor selection,
dependency-disposition closure, and correction.

Implements REQ-B4-047..077 (F06/F08), REQ-B4-078..086 + 246..249
(F09/RM-B4-02), REQ-B4-061..069 (F07), and REQ-B4-241/242/250/251/253/
254 (RM-B4-01/RM-B4-03 decision/effect consistency + idempotency).

Canonical rule (B4_WHAT_CONSOLIDATION_v0.1 Sec. 6, B4-CI04/05):
    DOMAIN determines physical identity (AssetIdentityResolution).
    CPL governs canonical identity (this module).
A positive resolution is necessary but never sufficient for merge —
survivor determinacy and dependency-disposition closure both gate
execution (REQ-B4-047/048, REQ-B4-246/247).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.assets.authority import AssetAuthority, AuthorityContext
from app.cpl.assets.outcomes import B4Outcome, OperationOutcome, OperationResult
from app.cpl.models.asset import Asset
from app.cpl.models.asset_identity_resolution import AssetIdentityResolution
from app.cpl.models.canonical_asset_identity_decision import CanonicalAssetIdentityDecision
from app.cpl.models.asset_merge_request import AssetMergeRequest

# REQ-B4-246: every dependency family materially capable of affecting
# canonical safety must have an explicit governed disposition before
# merge execution may proceed (RM-B4-02 / dependency-disposition
# closure). This list is the WHAT-level minimum (B4_WHAT_CONSOLIDATION
# Sec. "Dependency non-convergence"); callers MAY supply dispositions
# for additional families without weakening this floor.
MATERIAL_DEPENDENCY_FAMILIES = frozenset({
    "AssetIdentifier",
    "AssetIdentityResolution",
    "ContactAssetRelationship",
    "ExternalReference",
    "DomainProjection",
    "Case",
})

ALLOWED_DISPOSITIONS = frozenset({
    "PRESERVE", "REASSOCIATE_CURRENT", "SUPERSEDE", "RECONCILE", "HOLD", "REJECT_CONFLICT",
})

# Resolution outcomes that positively establish physical identity
# (necessary, not sufficient — REQ-B4-047/048).
POSITIVE_RESOLUTION_STATUSES = frozenset({"RESOLVED"})

# Resolution outcomes that MUST prohibit merge outright (REQ-B4-051/052/053).
NO_MERGE_RESOLUTION_STATUSES = {
    "AMBIGUOUS": B4Outcome.AMBIGUOUS,
    "CONTRADICTORY": B4Outcome.CONTRADICTORY,
    "UNRESOLVED": B4Outcome.UNRESOLVED,
    "PARTIALLY_RESOLVED": B4Outcome.UNRESOLVED,
}


def _select_survivor(session: Session, asset_a: Asset, asset_b: Asset,
                      override_asset_id: Optional[UUID], override_reason: Optional[str]) -> tuple[Optional[UUID], Optional[UUID], str, Optional[str]]:
    """Frozen survivor precedence (B4_WHAT_CONSOLIDATION_v0.1 Sec. 13,
    REQ-B4-070..077). Returns (survivor_id, loser_id, rule_applied, override_reason)
    or (None, None, "UNDETERMINED", None) if no governed survivor can
    yet be selected (REQ-B4-077 -> caller must HOLD)."""

    # Rule 1: an already-governing canonical successor/survivor, if one exists.
    for candidate, other in ((asset_a, asset_b), (asset_b, asset_a)):
        if other.asset_status == "MERGED" and other.merged_into_id == candidate.asset_id:
            return candidate.asset_id, other.asset_id, "RULE_1_EXISTING_GOVERNING_SURVIVOR", None

    # Rule 2: established canonical Asset over a later duplicate
    # representation. HOW: "established" = earlier canonical creation.
    if asset_a.created_at != asset_b.created_at:
        established = asset_a if asset_a.created_at < asset_b.created_at else asset_b
        duplicate = asset_b if established is asset_a else asset_a
        default_survivor, default_loser, rule = established.asset_id, duplicate.asset_id, "RULE_2_ESTABLISHED_CANONICAL_CONTINUITY"
    else:
        default_survivor, default_loser, rule = None, None, "UNDETERMINED"

    # Rule 3/4: explicit governed override, must carry a durable reason
    # (REQ-B4-073/074). Domain-resolver preference alone is NEVER
    # sufficient (REQ-B4-076) — override_asset_id is caller-supplied
    # governed CPL input only, never derived from resolver output here.
    if override_asset_id is not None:
        if override_reason is None or not override_reason.strip():
            # REQ-B4-074: an override without a durable recorded reason
            # is not a valid survivor selection.
            return None, None, "UNDETERMINED", None
        loser = asset_b.asset_id if override_asset_id == asset_a.asset_id else asset_a.asset_id
        return override_asset_id, loser, "RULE_3_GOVERNED_OVERRIDE", override_reason

    if default_survivor is None:
        return None, None, "UNDETERMINED", None
    return default_survivor, default_loser, rule, None


def admit_and_execute_asset_merge(
    session: Session,
    *,
    asset_a_id: UUID,
    asset_b_id: UUID,
    resolution_id: UUID,
    dependency_disposition: dict[str, str],
    authority: AuthorityContext,
    idempotency_key: str,
    survivor_override_asset_id: Optional[UUID] = None,
    survivor_override_reason: Optional[str] = None,
) -> OperationResult:
    """F06/F08/F09 combined: admission + execution as one governed
    transition (REQ-B4-049, REQ-B4-241/245). Only Postgres transaction
    boundaries around this call provide the "no partial canonical
    transition" guarantee — callers must commit/rollback the session
    as a single unit around this function."""
    authority.require(AssetAuthority.ADMIT_ASSET_MERGE, AssetAuthority.EXECUTE_ASSET_MERGE)

    # REQ-B4-250/253/254: idempotent replay by governed request identity,
    # never by payload similarity alone.
    existing_request = session.get(AssetMergeRequest, idempotency_key)
    if existing_request is not None:
        decision = session.get(CanonicalAssetIdentityDecision, existing_request.decision_id)
        return OperationResult(
            outcome=OperationOutcome.SUCCESS if decision.result == "EXECUTED" else OperationOutcome.NO_CHANGE,
            object_id=decision.target_asset_id,
            payload={"decision_id": decision.decision_id, "result": decision.result, "replay": True},
        )

    if asset_a_id == asset_b_id:
        return OperationResult(outcome=OperationOutcome.INVALID, detail="self-merge rejected")

    asset_a = session.get(Asset, asset_a_id)
    asset_b = session.get(Asset, asset_b_id)
    if asset_a is None or asset_b is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    # Idempotent replay of an already-completed merge in this direction
    # even without a matching idempotency_key (mirrors B3 ALREADY_MERGED).
    for src, tgt in ((asset_a, asset_b), (asset_b, asset_a)):
        if src.asset_status == "MERGED" and src.merged_into_id == tgt.asset_id:
            return OperationResult(outcome=OperationOutcome.ALREADY_MERGED, object_id=tgt.asset_id)

    resolution = session.get(AssetIdentityResolution, resolution_id)
    if resolution is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND, detail="resolution does not exist")

    # REQ-B4-032/054/170: technical failure is never silently treated
    # as a domain outcome.
    if resolution.resolution_status == "FAILED":
        return OperationResult(outcome=B4Outcome.FAILED, detail="resolution reports technical failure; no merge")

    if resolution.resolution_status in NO_MERGE_RESOLUTION_STATUSES:
        # REQ-B4-051/052/053: AMBIGUOUS/CONTRADICTORY/UNRESOLVED prohibit merge.
        return OperationResult(outcome=NO_MERGE_RESOLUTION_STATUSES[resolution.resolution_status],
                                detail="physical identity not positively established; no merge")

    if resolution.resolution_status not in POSITIVE_RESOLUTION_STATUSES:
        return OperationResult(outcome=B4Outcome.UNRESOLVED, detail=f"unrecognized resolution_status {resolution.resolution_status!r}")

    # REQ-B4-070..077: governed survivor precedence.
    survivor_id, loser_id, rule, override_reason = _select_survivor(
        session, asset_a, asset_b, survivor_override_asset_id, survivor_override_reason,
    )
    if survivor_id is None:
        decision = _record_decision(
            session, decision_type="MERGE", source_asset_id=asset_a_id, target_asset_id=asset_b_id,
            resolution_id=resolution_id, survivor_rule_applied="UNDETERMINED", survivor_override_reason=None,
            dependency_disposition=dependency_disposition, authority=authority, result="HOLD",
        )
        _record_idempotency(session, idempotency_key, decision.decision_id)
        return OperationResult(outcome=B4Outcome.HOLD, detail="survivor cannot yet be determined", payload={"decision_id": decision.decision_id})

    # REQ-B4-078..086, 246..249: dependency-disposition closure.
    missing = sorted(MATERIAL_DEPENDENCY_FAMILIES - set(dependency_disposition.keys()))
    invalid = {k: v for k, v in dependency_disposition.items() if v not in ALLOWED_DISPOSITIONS}
    blocking = {k: v for k, v in dependency_disposition.items() if v in ("HOLD", "REJECT_CONFLICT")}

    if missing or invalid:
        decision = _record_decision(
            session, decision_type="MERGE", source_asset_id=loser_id, target_asset_id=survivor_id,
            resolution_id=resolution_id, survivor_rule_applied=rule, survivor_override_reason=override_reason,
            dependency_disposition=dependency_disposition, authority=authority, result="HOLD",
        )
        _record_idempotency(session, idempotency_key, decision.decision_id)
        return OperationResult(
            outcome=B4Outcome.HOLD,
            detail=f"unresolved material dependency families: {missing or list(invalid)}",
            payload={"decision_id": decision.decision_id, "missing": missing},
        )

    if blocking:
        decision = _record_decision(
            session, decision_type="MERGE", source_asset_id=loser_id, target_asset_id=survivor_id,
            resolution_id=resolution_id, survivor_rule_applied=rule, survivor_override_reason=override_reason,
            dependency_disposition=dependency_disposition, authority=authority, result="REJECTED",
        )
        _record_idempotency(session, idempotency_key, decision.decision_id)
        return OperationResult(outcome=OperationOutcome.CONFLICTING, detail=f"blocking dependency disposition: {blocking}",
                                payload={"decision_id": decision.decision_id})

    # All gates passed: execute. Decision row + canonical mutation are
    # flushed together (REQ-B4-241/245) — an exception here rolls back
    # the whole session, so no partial transition is ever committed.
    decision = _record_decision(
        session, decision_type="MERGE", source_asset_id=loser_id, target_asset_id=survivor_id,
        resolution_id=resolution_id, survivor_rule_applied=rule, survivor_override_reason=override_reason,
        dependency_disposition=dependency_disposition, authority=authority, result="EXECUTED",
    )
    loser = session.get(Asset, loser_id)
    loser.asset_status = "MERGED"
    loser.merged_into_id = survivor_id
    loser.updated_at = datetime.now(timezone.utc)
    loser.record_version = (loser.record_version or 0) + 1
    session.flush()

    _record_idempotency(session, idempotency_key, decision.decision_id)
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=survivor_id,
                            payload={"loser_asset_id": loser_id, "decision_id": decision.decision_id})


def correct_asset_identity(
    session: Session,
    *,
    decision_id_to_correct: UUID,
    new_resolution_id: UUID,
    authority: AuthorityContext,
    idempotency_key: str,
    reason: str,
) -> OperationResult:
    """F07 (REQ-B4-061..069) + REQ-B4-251: correction by supersession,
    never destructive rollback. Restores independent current canonical
    Assets while the original MERGE decision and its resolution remain
    untouched historical fact (REQ-B4-065/066/069)."""
    authority.require(AssetAuthority.CORRECT_ASSET_IDENTITY)

    existing_request = session.get(AssetMergeRequest, idempotency_key)
    if existing_request is not None:
        decision = session.get(CanonicalAssetIdentityDecision, existing_request.decision_id)
        return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=decision.source_asset_id,
                                payload={"decision_id": decision.decision_id, "replay": True})

    prior = session.get(CanonicalAssetIdentityDecision, decision_id_to_correct)
    if prior is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND, detail="prior decision does not exist")
    if prior.decision_type != "MERGE" or prior.result != "EXECUTED":
        return OperationResult(outcome=OperationOutcome.INVALID, detail="only an executed MERGE decision may be corrected")

    new_resolution = session.get(AssetIdentityResolution, new_resolution_id)
    if new_resolution is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND, detail="new resolution does not exist")

    loser = session.get(Asset, prior.source_asset_id)
    survivor = session.get(Asset, prior.target_asset_id)

    # REQ-B4-063/064: new decision, superseding the prior decision's
    # *current effect* without erasing it (REQ-B4-065/066).
    correction = _record_decision(
        session, decision_type="CORRECTION", source_asset_id=prior.source_asset_id, target_asset_id=prior.target_asset_id,
        resolution_id=new_resolution_id, survivor_rule_applied=None, survivor_override_reason=reason,
        dependency_disposition=None, authority=authority, result="EXECUTED", supersedes=prior.decision_id,
    )

    # REQ-B4-068: restore independent current canonical representations.
    loser.asset_status = "ACTIVE"
    loser.merged_into_id = None
    loser.updated_at = datetime.now(timezone.utc)
    loser.record_version = (loser.record_version or 0) + 1
    session.flush()

    _record_idempotency(session, idempotency_key, correction.decision_id)
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=loser.asset_id,
                            payload={"decision_id": correction.decision_id, "restored_asset_id": loser.asset_id,
                                     "survivor_asset_id": survivor.asset_id})


def _record_decision(session: Session, *, decision_type: str, source_asset_id: UUID, target_asset_id: UUID,
                      resolution_id: Optional[UUID], survivor_rule_applied: Optional[str],
                      survivor_override_reason: Optional[str], dependency_disposition: Optional[dict],
                      authority: AuthorityContext, result: str,
                      supersedes: Optional[UUID] = None) -> CanonicalAssetIdentityDecision:
    decision = CanonicalAssetIdentityDecision(
        decision_type=decision_type,
        source_asset_id=source_asset_id,
        target_asset_id=target_asset_id,
        resolution_id=resolution_id,
        survivor_rule_applied=survivor_rule_applied,
        survivor_override_reason=survivor_override_reason,
        dependency_disposition=dependency_disposition,
        authority_context=authority.as_dict(),
        result=result,
        supersedes_decision_id=supersedes,
    )
    session.add(decision)
    session.flush()
    return decision


def _record_idempotency(session: Session, idempotency_key: str, decision_id: UUID) -> None:
    session.add(AssetMergeRequest(idempotency_key=idempotency_key, decision_id=decision_id))
    session.flush()

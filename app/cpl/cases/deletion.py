"""Governed deletion of an expired Case (REQ-B5-116, the narrow exception
to the history requirements listed in the B5 amendment).

`delete_expired_case` is the ONLY code path that physically deletes a Case.
It deletes the Case and the rows that exist only because of it, in one
transaction and in the order the RESTRICT foreign keys impose (none is
altered, no trigger exists or is disabled):

  runner_artifact_redactions   of the Case's artifacts (REQ-B6-091 traces)
  runner_governance_decisions  of the Case's executions or artifacts
  runner_artifacts             of the Case's executions (vir_resolution,
                               Premiers Constats, reports; every version)
  asset_identity_resolutions   recorded by the Case's executions
  runner_execution_corrections of the Case's executions
  case_events                  of the Case
  runner_executions            of the Case
  case_participants            of the Case
  case_mutation_requests       of the Case's canonical decisions
  canonical_case_decisions     of the Case
  cases                        the Case itself

What is never deleted: the Contact, its Account and credentials, the
vehicle (Asset, VehicleDetail, owner relationship, its identifiers and
creation request), another Case and anything recorded by it, manufacturer
knowledge, notices and catalogues. One pointer outside the Case is
cleared, not deleted: VehicleDetail.source_resolution_id when it names a
resolution of the Case (the vehicle's summary stays; its source is then
"no longer kept").

A Case is deleted only when its creation (cases.created_at, the starting
point ``creation_dossier``) is before the cutoff the caller computed from an
explicit retention period. A Case still within its period is not touched. A
Case that a row outside it still depends on (another Case's execution, event
or resolution, the vehicle's current identity, a projection or an identity
decision) is not touched either: the deletion is refused (CONFLICT) with
the kinds of dependency named, never their content.

Each deletion writes one CaseDeletion row: the Case's opaque identifier,
the operation, the reason, the period, the opaque operator reference and
row counts -- nothing of the Case's content, no contact, no vehicle, no
vehicle identifier. A Case already deleted is NO_CHANGE (idempotent). The
caller commits; a failure before the commit leaves the Case whole.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.automotive.models.vehicle_detail import VehicleDetail
from app.cpl.cases.authority import AuthorityContext, AuthorityDeniedError, CaseAuthority
from app.cpl.cases.outcomes import CaseOutcome, CaseResult
from app.cpl.models.asset import Asset
from app.cpl.models.asset_identity_resolution import AssetIdentityResolution
from app.cpl.models.canonical_asset_identity_decision import CanonicalAssetIdentityDecision
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.models.case import Case
from app.cpl.models.case_deletion import CaseDeletion
from app.cpl.models.case_event import CaseEvent
from app.cpl.models.case_mutation_request import CaseMutationRequest
from app.cpl.models.case_participant import CaseParticipant
from app.cpl.models.domain_projection import DomainProjection
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.runner_artifact_redaction import RunnerArtifactRedaction
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_execution_correction import RunnerExecutionCorrection
from app.cpl.models.runner_governance_decision import RunnerGovernanceDecision
from app.cpl.runners.redaction import valid_operator_reference

REASON = "RETENTION_POLICY"
ANCHOR = "creation_dossier"


@dataclass
class CaseFootprint:
    """The ids of every row that exists only because of the Case."""
    case_id: UUID
    executions: list[UUID] = field(default_factory=list)
    artifacts: list[UUID] = field(default_factory=list)
    decisions: list[UUID] = field(default_factory=list)
    redactions: list[UUID] = field(default_factory=list)
    resolutions: list[UUID] = field(default_factory=list)
    corrections: list[UUID] = field(default_factory=list)
    events: list[UUID] = field(default_factory=list)
    participants: list[UUID] = field(default_factory=list)
    case_decisions: list[UUID] = field(default_factory=list)
    mutation_requests: list[str] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        return {"cases": 1, "runner_executions": len(self.executions), "runner_artifacts": len(self.artifacts),
                "runner_governance_decisions": len(self.decisions),
                "runner_artifact_redactions": len(self.redactions),
                "asset_identity_resolutions": len(self.resolutions),
                "runner_execution_corrections": len(self.corrections), "case_events": len(self.events),
                "case_participants": len(self.participants), "canonical_case_decisions": len(self.case_decisions),
                "case_mutation_requests": len(self.mutation_requests)}


def _ids(query) -> list:
    return [row[0] for row in query]


def case_footprint(session: Session, case_id: UUID) -> CaseFootprint:
    fp = CaseFootprint(case_id=case_id)
    fp.executions = _ids(session.query(RunnerExecution.execution_id).filter(RunnerExecution.case_id == case_id))
    fp.artifacts = _ids(session.query(RunnerArtifact.artifact_id)
                        .filter(RunnerArtifact.execution_id.in_(fp.executions)))
    fp.decisions = _ids(session.query(RunnerGovernanceDecision.decision_id).filter(or_(
        RunnerGovernanceDecision.execution_id.in_(fp.executions),
        RunnerGovernanceDecision.artifact_id.in_(fp.artifacts))))
    fp.redactions = _ids(session.query(RunnerArtifactRedaction.artifact_id)
                         .filter(RunnerArtifactRedaction.artifact_id.in_(fp.artifacts)))
    fp.resolutions = _ids(session.query(AssetIdentityResolution.resolution_id)
                          .filter(AssetIdentityResolution.execution_id.in_(fp.executions)))
    fp.corrections = _ids(session.query(RunnerExecutionCorrection.correction_id)
                          .filter(RunnerExecutionCorrection.execution_id.in_(fp.executions)))
    fp.events = _ids(session.query(CaseEvent.event_id).filter(CaseEvent.case_id == case_id))
    fp.participants = _ids(session.query(CaseParticipant.case_participant_id).filter(CaseParticipant.case_id == case_id))
    fp.case_decisions = _ids(session.query(CanonicalCaseDecision.decision_id)
                             .filter(CanonicalCaseDecision.case_id == case_id))
    fp.mutation_requests = _ids(session.query(CaseMutationRequest.idempotency_key)
                                .filter(CaseMutationRequest.decision_id.in_(fp.case_decisions)))
    return fp


def outside_dependencies(session: Session, fp: CaseFootprint) -> list[str]:
    """Kinds of rows outside the Case that still point into it (names only).
    Any of them means the Case cannot be deleted without changing data that
    is not its own."""
    found = []

    def check(kind: str, query) -> None:
        if query.first() is not None:
            found.append(kind)

    check("execution of another case", session.query(RunnerExecution.execution_id).filter(
        RunnerExecution.parent_execution_id.in_(fp.executions), ~RunnerExecution.execution_id.in_(fp.executions)))
    check("artifact of another case", session.query(RunnerArtifact.artifact_id).filter(
        RunnerArtifact.supersedes_artifact_id.in_(fp.artifacts), ~RunnerArtifact.artifact_id.in_(fp.artifacts)))
    check("event of another case", session.query(CaseEvent.event_id).filter(
        CaseEvent.execution_id.in_(fp.executions), CaseEvent.case_id != fp.case_id))
    check("current execution of another case", session.query(Case.case_id).filter(
        Case.current_execution_id.in_(fp.executions), Case.case_id != fp.case_id))
    check("resolution of another case", session.query(AssetIdentityResolution.resolution_id).filter(
        AssetIdentityResolution.supersedes_resolution_id.in_(fp.resolutions),
        ~AssetIdentityResolution.resolution_id.in_(fp.resolutions)))
    check("current identity of the vehicle", session.query(Asset.asset_id).filter(
        Asset.current_identity_resolution_id.in_(fp.resolutions)))
    check("domain projection", session.query(DomainProjection.projection_id).filter(
        DomainProjection.source_resolution_id.in_(fp.resolutions)))
    check("asset identity decision", session.query(CanonicalAssetIdentityDecision.decision_id).filter(
        CanonicalAssetIdentityDecision.resolution_id.in_(fp.resolutions)))
    return found


def _delete(session: Session, column, ids: list) -> None:
    if ids:
        session.query(column.class_).filter(column.in_(ids)).delete(synchronize_session=False)


def delete_expired_case(session: Session, *, case_id: UUID, created_before: datetime, retention_days: int,
                        authority: AuthorityContext, operation_id: Optional[UUID] = None) -> CaseResult:
    try:
        authority.require(CaseAuthority.DELETE_EXPIRED_CASE)
    except AuthorityDeniedError:
        return CaseResult(outcome=CaseOutcome.AUTHORITY_REJECTION, detail="missing DELETE_EXPIRED_CASE authority")
    if not isinstance(retention_days, int) or isinstance(retention_days, bool) or retention_days < 1:
        return CaseResult(outcome=CaseOutcome.SEMANTIC_REJECTION, detail="an explicit retention period is required")
    if created_before.tzinfo is None:
        return CaseResult(outcome=CaseOutcome.SEMANTIC_REJECTION, detail="cutoff must carry a time zone")
    if not valid_operator_reference(authority.actor_reference):
        return CaseResult(outcome=CaseOutcome.SEMANTIC_REJECTION, detail="operator reference must be opaque")
    if session.get(CaseDeletion, case_id) is not None:
        return CaseResult(outcome=CaseOutcome.NO_CHANGE, object_id=case_id, detail="already deleted")
    case = session.get(Case, case_id, with_for_update=True)
    if case is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND, object_id=case_id)
    if case.created_at >= created_before:
        return CaseResult(outcome=CaseOutcome.SEMANTIC_REJECTION, object_id=case_id,
                          detail="case still within its retention period")
    fp = case_footprint(session, case_id)
    blockers = outside_dependencies(session, fp)
    if blockers:
        return CaseResult(outcome=CaseOutcome.CONFLICT, object_id=case_id,
                          detail="still referenced from outside the case: " + ", ".join(blockers))

    # Pointers to the Case's rows: its own current execution, and the
    # vehicle summary's source (cleared, the summary stays).
    case.current_execution_id = None
    if fp.resolutions:
        (session.query(VehicleDetail).filter(VehicleDetail.source_resolution_id.in_(fp.resolutions))
         .update({VehicleDetail.source_resolution_id: None}, synchronize_session=False))
    session.flush()

    _delete(session, RunnerArtifactRedaction.artifact_id, fp.redactions)
    _delete(session, RunnerGovernanceDecision.decision_id, fp.decisions)
    _delete(session, RunnerArtifact.artifact_id, fp.artifacts)
    _delete(session, AssetIdentityResolution.resolution_id, fp.resolutions)
    _delete(session, RunnerExecutionCorrection.correction_id, fp.corrections)
    _delete(session, CaseEvent.event_id, fp.events)
    _delete(session, RunnerExecution.execution_id, fp.executions)
    _delete(session, CaseParticipant.case_participant_id, fp.participants)
    _delete(session, CaseMutationRequest.idempotency_key, fp.mutation_requests)
    _delete(session, CanonicalCaseDecision.decision_id, fp.case_decisions)
    session.expunge(case)
    _delete(session, Case.case_id, [case_id])

    operation_id = operation_id or uuid4()
    counts = fp.counts()
    session.add(CaseDeletion(case_id=case_id, operation_id=operation_id, reason=REASON,
                             retention_days=retention_days, anchor=ANCHOR,
                             operator_reference=authority.actor_reference, deleted_counts=counts))
    session.flush()
    return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=case_id,
                      payload={"operation_id": str(operation_id), "counts": counts})


@dataclass
class CaseDeletionPlan:
    """What a deletion would do: case ids and row counts only."""
    due: list[UUID] = field(default_factory=list)
    blocked: dict[UUID, list[str]] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)


def plan_expired_cases(session: Session, *, created_before: datetime) -> CaseDeletionPlan:
    """Reads only. `due`: Cases created before the cutoff that can be
    deleted; `blocked`: those a row outside them still depends on."""
    plan = CaseDeletionPlan()
    for (case_id,) in (session.query(Case.case_id).filter(Case.created_at < created_before)
                       .order_by(Case.created_at, Case.case_id)):
        fp = case_footprint(session, case_id)
        blockers = outside_dependencies(session, fp)
        if blockers:
            plan.blocked[case_id] = blockers
            continue
        plan.due.append(case_id)
        for kind, n in fp.counts().items():
            plan.counts[kind] = plan.counts.get(kind, 0) + n
    return plan

"""Governed expurgation of vehicle identifiers from RunnerArtifacts
(REQ-B6-091, the narrow exception to REQ-B6-053..059).

Only artifacts registered as `vir_resolution` (artifact_type and
schema_name) are eligible, and only their vehicle identifiers -- the plate
and the VIN -- are removed. The locations follow VIR's
VehicleIdentityResolution schema, not the words in it:

  vehicle_identity.identifiers.{vin, registration_number}
  alternative_candidates[].identity.identifiers.*        (same keys)
  alternative_candidates[].field_evidence[]               (identifier paths)
  excluded_candidates[].candidate.identity.identifiers.*  (same keys)
  excluded_candidates[].candidate.field_evidence[]        (identifier paths)
  excluded_candidates[].field_provenance[].raw_value      (identifier paths)
  excluded_candidates[].{declared_value, candidate_value} (identifier path)
  field_evidence[]: resolved_value, sources[] and consulted_without_value[]
      reported_value / source_value                       (identifier paths)
  contradictions[].values[].value                         (identifier paths)
  clarification_questions[].choices[]                     (identifier target)
  provider_unconfirmed_fields[].raw_value of a provider field documented as
      carrying an identifier (RegCheck numSerieMoteur, « VIN number »)

Each value becomes null; every structure, field path, source, method,
reliability, contradiction and internal reference stays, and so does the
registration country (not an identifier of the vehicle). The same function
serves new writes (the product removes the identifiers before registering a
vir_resolution artifact) and the expurgation of artifacts registered before.

`redact_artifact_identifiers` is the ONLY code path that may change a
registered payload or set `redaction_status`. Per artifact, in one
transaction: a governed decision (ARTIFACT_REDACTION), the payload without
the identifiers, `content_hash` recomputed over the payload as persisted
(REQ-B6-054 keeps holding), `redaction_status = 'REDACTED'`, and a
RunnerArtifactRedaction row keeping the registration hash as a historical
trace. Every version linked by supersession is treated in the same
operation, so no older version keeps the values. No removed value and no
copy of the removed content is written anywhere.

`classify_integrity` tells apart an original that is intact, an artifact
expurgated by this operation, and any other alteration.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.runner_artifact_redaction import RunnerArtifactRedaction
from app.cpl.models.runner_governance_decision import RunnerGovernanceDecision
from app.cpl.runners.artifacts import IntegrityCheckOutcome, compute_content_hash, verify_content_integrity
from app.cpl.runners.authority import AuthorityContext, AuthorityDeniedError, RunnerAuthority
from app.cpl.runners.outcomes import RunnerOutcome, RunnerResult

ELIGIBLE_ARTIFACT_TYPE = "vir_resolution"
ELIGIBLE_SCHEMA_NAME = "vir_resolution"
OPERATION = "VEHICLE_IDENTIFIER_REDACTION"
REASONS = ("RETENTION_POLICY", "DATA_SUBJECT_REQUEST")
REDACTED = "REDACTED"
_HASH_ALGORITHM = "sha256"

IDENTIFIER_KEYS = ("vin", "registration_number")
IDENTIFIER_PATHS = tuple(f"identifiers.{k}" for k in IDENTIFIER_KEYS)
# Provider fields kept raw by VIR (provider_unconfirmed_fields) whose
# documentation says they carry a vehicle identifier.
IDENTIFYING_PROVIDER_FIELDS = frozenset({("provider-fr-regcheck", "numSerieMoteur")})

# An opaque operator reference: no address, no space, no personal name form.
_OPERATOR_REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{7,63}")


class IntegrityClass:
    ORIGINAL_INTACT = "ORIGINAL_INTACT"
    REDACTED_AUTHORIZED = "REDACTED_AUTHORIZED"
    UNAUTHORIZED_ALTERATION = "UNAUTHORIZED_ALTERATION"
    NO_HASH_RECORDED = "NO_HASH_RECORDED"


def _is_identifier_path(path) -> bool:
    return isinstance(path, str) and path in IDENTIFIER_PATHS


def _filled(value) -> bool:
    return value not in (None, "")


class _Scrubber:
    def __init__(self):
        self.removed: list[str] = []

    def null(self, holder: dict, key: str, where: str) -> None:
        if isinstance(holder, dict) and _filled(holder.get(key)):
            holder[key] = None
            self.removed.append(where)

    def identity(self, identity, where: str) -> None:
        if isinstance(identity, dict) and isinstance(identity.get("identifiers"), dict):
            for key in IDENTIFIER_KEYS:
                self.null(identity["identifiers"], key, f"{where}.identifiers.{key}")

    def source(self, source, where: str) -> None:
        for key in ("reported_value", "source_value"):
            self.null(source, key, f"{where}.{key}")

    def evidence_list(self, items, where: str) -> None:
        for i, fe in enumerate(items or []):
            if not (isinstance(fe, dict) and _is_identifier_path(fe.get("field_path"))):
                continue
            at = f"{where}[{i}]"
            self.null(fe, "resolved_value", f"{at}.resolved_value")
            for group in ("sources", "consulted_without_value"):
                for j, src in enumerate(fe.get(group) or []):
                    self.source(src, f"{at}.{group}[{j}]")


def redact_vehicle_identifiers(payload: Optional[dict]) -> tuple[dict, list[str]]:
    """The vir_resolution payload without the plate and the VIN, and the
    locations that held one (names with their position, never values)."""
    out = copy.deepcopy(payload or {})
    s = _Scrubber()
    s.identity(out.get("vehicle_identity"), "vehicle_identity")
    s.evidence_list(out.get("field_evidence"), "field_evidence")
    for i, c in enumerate(out.get("alternative_candidates") or []):
        if isinstance(c, dict):
            s.identity(c.get("identity"), f"alternative_candidates[{i}].identity")
            s.evidence_list(c.get("field_evidence"), f"alternative_candidates[{i}].field_evidence")
    for i, e in enumerate(out.get("excluded_candidates") or []):
        if not isinstance(e, dict):
            continue
        at = f"excluded_candidates[{i}]"
        cand = e.get("candidate")
        if isinstance(cand, dict):
            s.identity(cand.get("identity"), f"{at}.candidate.identity")
            s.evidence_list(cand.get("field_evidence"), f"{at}.candidate.field_evidence")
        for j, fp in enumerate(e.get("field_provenance") or []):
            if isinstance(fp, dict) and _is_identifier_path(fp.get("field_path")):
                s.null(fp, "raw_value", f"{at}.field_provenance[{j}].raw_value")
        if _is_identifier_path(e.get("field_path")):
            s.null(e, "declared_value", f"{at}.declared_value")
            s.null(e, "candidate_value", f"{at}.candidate_value")
    for i, c in enumerate(out.get("contradictions") or []):
        if isinstance(c, dict) and _is_identifier_path(c.get("field_path")):
            for j, v in enumerate(c.get("values") or []):
                s.null(v, "value", f"contradictions[{i}].values[{j}].value")
    for i, q in enumerate(out.get("clarification_questions") or []):
        if isinstance(q, dict) and _is_identifier_path(q.get("target_field")):
            for j, ch in enumerate(q.get("choices") or []):
                s.null(ch, "value", f"clarification_questions[{i}].choices[{j}].value")
                if isinstance(ch, dict) and _filled(ch.get("label")):
                    ch["label"] = ""
                    s.removed.append(f"clarification_questions[{i}].choices[{j}].label")
    for i, u in enumerate(out.get("provider_unconfirmed_fields") or []):
        if isinstance(u, dict) and (u.get("source_id"), u.get("provider_field")) in IDENTIFYING_PROVIDER_FIELDS:
            s.null(u, "raw_value", f"provider_unconfirmed_fields[{i}].raw_value")
    return out, s.removed


def holds_vehicle_identifier(payload: Optional[dict]) -> bool:
    return bool(redact_vehicle_identifiers(payload)[1])


def is_eligible(artifact: RunnerArtifact) -> bool:
    return artifact.artifact_type == ELIGIBLE_ARTIFACT_TYPE and artifact.schema_name == ELIGIBLE_SCHEMA_NAME


def valid_operator_reference(reference: Optional[str]) -> bool:
    return isinstance(reference, str) and _OPERATOR_REFERENCE.fullmatch(reference) is not None


def supersession_chain(session: Session, artifact: RunnerArtifact) -> list[RunnerArtifact]:
    """Every artifact linked to this one by supersession, in either direction,
    the artifact itself included, oldest first."""
    seen: dict[UUID, RunnerArtifact] = {artifact.artifact_id: artifact}
    todo = [artifact]
    while todo:
        current = todo.pop()
        linked = []
        if current.supersedes_artifact_id is not None:
            linked.append(session.get(RunnerArtifact, current.supersedes_artifact_id))
        linked += session.query(RunnerArtifact).filter(RunnerArtifact.supersedes_artifact_id == current.artifact_id).all()
        for other in linked:
            if other is not None and other.artifact_id not in seen:
                seen[other.artifact_id] = other
                todo.append(other)
    return sorted(seen.values(), key=lambda a: (a.created_at, str(a.artifact_id)))


def classify_integrity(session: Session, artifact: RunnerArtifact) -> str:
    record = session.get(RunnerArtifactRedaction, artifact.artifact_id)
    hashed = verify_content_integrity(artifact)
    if artifact.redaction_status is None and record is None:
        if hashed == IntegrityCheckOutcome.NO_HASH_RECORDED:
            return IntegrityClass.NO_HASH_RECORDED
        return IntegrityClass.ORIGINAL_INTACT if hashed == IntegrityCheckOutcome.MATCH else IntegrityClass.UNAUTHORIZED_ALTERATION
    if (artifact.redaction_status == REDACTED and record is not None and hashed == IntegrityCheckOutcome.MATCH
            and artifact.content_hash == record.redacted_content_hash and not holds_vehicle_identifier(artifact.payload)):
        return IntegrityClass.REDACTED_AUTHORIZED
    return IntegrityClass.UNAUTHORIZED_ALTERATION


def audit_integrity(session: Session) -> dict[str, list[UUID]]:
    out: dict[str, list[UUID]] = {k: [] for k in (IntegrityClass.ORIGINAL_INTACT, IntegrityClass.REDACTED_AUTHORIZED,
                                                   IntegrityClass.UNAUTHORIZED_ALTERATION, IntegrityClass.NO_HASH_RECORDED)}
    for artifact in session.query(RunnerArtifact).order_by(RunnerArtifact.created_at, RunnerArtifact.artifact_id):
        out[classify_integrity(session, artifact)].append(artifact.artifact_id)
    return out


def _refusal(session: Session, artifact: RunnerArtifact) -> Optional[str]:
    """Why this artifact cannot be expurgated as it stands, or None."""
    if artifact.redaction_status == REDACTED:
        if classify_integrity(session, artifact) != IntegrityClass.REDACTED_AUTHORIZED:
            return "already expurgated but its content no longer matches the expurgation record"
        return None
    if session.get(RunnerArtifactRedaction, artifact.artifact_id) is not None:
        return "an expurgation record exists for an artifact not marked expurgated"
    if verify_content_integrity(artifact) == IntegrityCheckOutcome.MISMATCH:
        return "content does not match its registration hash: an alteration is never laundered by an expurgation"
    return None


def _redact_one(session: Session, artifact: RunnerArtifact, *, operation_id: UUID, reason: str,
                authority: AuthorityContext) -> bool:
    if artifact.redaction_status == REDACTED:
        return False
    redacted, removed = redact_vehicle_identifiers(artifact.payload)
    if not removed:
        return False
    new_hash = compute_content_hash(redacted)
    decision = RunnerGovernanceDecision(
        decision_type="ARTIFACT_REDACTION", decision_mode="AUTHORITY_EVALUATION", artifact_id=artifact.artifact_id,
        authority_context=authority.as_dict(),
        prior_value={"redaction_status": None, "hash_algorithm": artifact.hash_algorithm,
                     "content_hash": artifact.content_hash},
        new_value={"redaction_status": REDACTED, "hash_algorithm": _HASH_ALGORITHM, "content_hash": new_hash,
                   "operation": OPERATION, "operation_id": str(operation_id), "reason": reason,
                   "redacted_locations": removed},
        result="EXECUTED",
    )
    session.add(decision)
    session.flush()
    session.add(RunnerArtifactRedaction(
        artifact_id=artifact.artifact_id, decision_id=decision.decision_id, operation_id=operation_id,
        operation=OPERATION, reason=reason, operator_reference=authority.actor_reference,
        original_hash_algorithm=artifact.hash_algorithm, original_content_hash=artifact.content_hash,
        hash_algorithm=_HASH_ALGORITHM, redacted_content_hash=new_hash, redacted_locations=removed,
    ))
    artifact.payload = redacted
    artifact.hash_algorithm = _HASH_ALGORITHM
    artifact.content_hash = new_hash
    artifact.redaction_status = REDACTED
    session.flush()
    return True


def redact_artifact_identifiers(session: Session, *, artifact_id: UUID, reason: str, authority: AuthorityContext,
                                operation_id: Optional[UUID] = None) -> RunnerResult:
    """Expurgates the artifact and every version linked to it by
    supersession, all or nothing: if one of them cannot be (an unauthorized
    alteration, an inconsistent record), none is touched. Idempotent: an
    artifact already expurgated or holding no identifier is left as it is."""
    try:
        authority.require(RunnerAuthority.REDACT_ARTIFACT)
    except AuthorityDeniedError:
        return RunnerResult(outcome=RunnerOutcome.AUTHORITY_REJECTION, detail="missing REDACT_ARTIFACT authority")
    if reason not in REASONS:
        return RunnerResult(outcome=RunnerOutcome.SEMANTIC_REJECTION, detail=f"reason must be one of {REASONS}")
    if not valid_operator_reference(authority.actor_reference):
        return RunnerResult(outcome=RunnerOutcome.SEMANTIC_REJECTION, detail="operator reference must be opaque")
    artifact = session.get(RunnerArtifact, artifact_id, with_for_update=True)
    if artifact is None:
        return RunnerResult(outcome=RunnerOutcome.NOT_FOUND)
    chain = supersession_chain(session, artifact)
    if not all(is_eligible(a) for a in chain):
        return RunnerResult(outcome=RunnerOutcome.SEMANTIC_REJECTION, object_id=artifact_id,
                            detail="only vir_resolution artifacts may be expurgated (REQ-B6-091)")
    for member in chain:
        why = _refusal(session, member)
        if why is not None:
            return RunnerResult(outcome=RunnerOutcome.CONFLICT, object_id=member.artifact_id, detail=why)
    operation_id = operation_id or uuid4()
    done = [a.artifact_id for a in chain
            if _redact_one(session, a, operation_id=operation_id, reason=reason, authority=authority)]
    return RunnerResult(outcome=RunnerOutcome.SUCCESS if done else RunnerOutcome.NO_CHANGE, object_id=artifact_id,
                        payload={"operation_id": str(operation_id), "redacted": [str(x) for x in done],
                                 "chain": [str(a.artifact_id) for a in chain]})


@dataclass
class RedactionPlan:
    """What an operation would do: artifact ids only, never content."""
    to_redact: list[UUID] = field(default_factory=list)
    refused: dict[UUID, str] = field(default_factory=dict)
    already_redacted: int = 0
    without_identifier: int = 0


def plan_redaction(session: Session, *, created_before: Optional[datetime] = None,
                   artifact_ids: Optional[Iterable[UUID]] = None) -> RedactionPlan:
    """The eligible artifacts still holding an identifier (each with its
    supersession chain), optionally limited to an explicit list or to those
    registered before a date the operator gives. No period is decided here."""
    query = session.query(RunnerArtifact).filter(RunnerArtifact.artifact_type == ELIGIBLE_ARTIFACT_TYPE,
                                                 RunnerArtifact.schema_name == ELIGIBLE_SCHEMA_NAME)
    if created_before is not None:
        query = query.filter(RunnerArtifact.created_at < created_before)
    if artifact_ids is not None:
        query = query.filter(RunnerArtifact.artifact_id.in_(list(artifact_ids)))
    plan = RedactionPlan()
    seen: set[UUID] = set()
    for artifact in query.order_by(RunnerArtifact.created_at, RunnerArtifact.artifact_id):
        for member in supersession_chain(session, artifact):
            if member.artifact_id in seen:
                continue
            seen.add(member.artifact_id)
            why = _refusal(session, member)
            if why is not None:
                plan.refused[member.artifact_id] = why
            elif member.redaction_status == REDACTED:
                plan.already_redacted += 1
            elif holds_vehicle_identifier(member.payload):
                plan.to_redact.append(member.artifact_id)
            else:
                plan.without_identifier += 1
    return plan

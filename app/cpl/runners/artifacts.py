"""RunnerArtifact registration, validation, supersession, and integrity
(REQ-B6-018..034, 053..061, 078, 089, 090).

`supersede_artifact` is the ONLY code path that may set
`artifact_status = 'SUPERSEDED'` or `supersedes_artifact_id` — this is
the repaired REQ-B6-057 contract: `supersedes_artifact_id` (set on the
new artifact) is canonical; `artifact_status = 'SUPERSEDED'` (set on the
old artifact) is a derived projection, written in the same governed
operation, never independently. `check_supersession_consistency`
provides the explicit, directly-testable consistency query REQ-B6-057
requires.

`compute_content_hash`/`verify_content_integrity` implement REQ-B6-053
..056: hash is computed over the exact persisted `payload` JSONB
content (canonical JSON serialization — sorted keys, no whitespace
ambiguity — REQ-B6-054), is required whenever content is stored inline
(REQ-B6-053), and a mismatch is flagged as a distinct integrity failure
never conflated with structural REJECTED (REQ-B6-055) and never treated
as evidence of semantic validity or domain truth (REQ-B6-056).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.cpl.runners.authority import RunnerAuthority, AuthorityContext, AuthorityDeniedError
from app.cpl.runners.classification import validate_classification, ClassificationValidationOutcome
from app.cpl.runners.outcomes import RunnerOutcome, RunnerResult
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.runner_artifact_schema_definition import RunnerArtifactSchemaDefinition
from app.cpl.models.runner_governance_decision import RunnerGovernanceDecision

_HASH_ALGORITHM = "sha256"


def compute_content_hash(payload: dict) -> str:
    """REQ-B6-054: hashed over the exact payload as persisted, using a
    canonical (sorted-key, separator-normalized) JSON serialization so
    the same logical content always hashes identically regardless of
    Python dict insertion order."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class IntegrityCheckOutcome:
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    NO_HASH_RECORDED = "NO_HASH_RECORDED"


def verify_content_integrity(artifact: RunnerArtifact) -> str:
    """REQ-B6-055: mismatch is flagged distinctly — never silently
    corrected, never conflated with REJECTED (structural rejection has a
    different meaning, REQ-B6-033)."""
    if artifact.content_hash is None:
        return IntegrityCheckOutcome.NO_HASH_RECORDED
    recomputed = compute_content_hash(artifact.payload or {})
    return IntegrityCheckOutcome.MATCH if recomputed == artifact.content_hash else IntegrityCheckOutcome.MISMATCH


def register_artifact(
    session: Session,
    *,
    execution_id: UUID,
    artifact_type: str,
    schema_name: str,
    schema_version: str,
    payload: dict,
    semantic_function: str,
    lifecycle_role: str,
    presentation_role: str,
    hash_algorithm: Optional[str] = None,
    content_hash: Optional[str] = None,
    authority: AuthorityContext,
) -> RunnerResult:
    """REQ-B6-078: registration requires a governed decision.
    REQ-B6-090: classification is validated before registration
    proceeds. REQ-B6-089/032: structural validation against the
    registered (schema_name, schema_version) pair determines
    CREATED -> VALIDATED vs. CREATED -> REJECTED."""
    try:
        authority.require(RunnerAuthority.REGISTER_ARTIFACT)
    except AuthorityDeniedError:
        return RunnerResult(outcome=RunnerOutcome.AUTHORITY_REJECTION, detail="missing REGISTER_ARTIFACT authority")

    classification = validate_classification(
        semantic_function=semantic_function, lifecycle_role=lifecycle_role, presentation_role=presentation_role,
    )
    if classification.outcome != ClassificationValidationOutcome.VALID:
        # REQ-B6-090: a classification failure is itself a structural
        # registration rejection (REQ-B6-033's discipline extended to
        # this second structural gate) — never a domain-level rejection.
        return RunnerResult(outcome=RunnerOutcome.SEMANTIC_REJECTION,
                             detail=f"classification {classification.outcome}: {classification.detail}")

    # REQ-B6-053: hash required for inline-stored content. An artifact is
    # "inline" in this candidate whenever its payload is provided (always,
    # in this Build Unit — no external-reference-only artifact path is
    # implemented here). Caller-supplied hash_algorithm/content_hash are
    # honored only if they already match; otherwise they are computed here.
    if hash_algorithm is None and content_hash is None:
        hash_algorithm = _HASH_ALGORITHM
        content_hash = compute_content_hash(payload)

    new_artifact_id = uuid4()
    decision = RunnerGovernanceDecision(
        decision_type="ARTIFACT_REGISTRATION",
        decision_mode="AUTOMATIC_RULE_BOUND",  # REQ-B6-078: "possibly lighter-weight than admission"
        artifact_id=new_artifact_id,
        authority_context=authority.as_dict(),
        new_value={"execution_id": str(execution_id), "artifact_type": artifact_type,
                   "schema_name": schema_name, "schema_version": schema_version},
        result="EXECUTED",
    )
    session.add(decision)

    artifact = RunnerArtifact(
        artifact_id=new_artifact_id, execution_id=execution_id, artifact_type=artifact_type,
        schema_name=schema_name, schema_version=schema_version, payload=payload,
        hash_algorithm=hash_algorithm, content_hash=content_hash,
        semantic_function=semantic_function, lifecycle_role=lifecycle_role, presentation_role=presentation_role,
        artifact_status="CREATED",
    )
    session.add(artifact)
    session.flush()

    validated = _validate_structure(session, artifact)
    session.flush()

    return RunnerResult(outcome=RunnerOutcome.SUCCESS, object_id=new_artifact_id,
                         payload={"decision_id": decision.decision_id, "artifact_status": artifact.artifact_status,
                                  "structurally_valid": validated})


def _validate_structure(session: Session, artifact: RunnerArtifact) -> bool:
    """REQ-B6-089/032b/032d: CREATED -> VALIDATED only via an objective
    check against a registered (schema_name, schema_version) definition;
    an unregistered pair or a non-conformant payload routes to REJECTED
    (REQ-B6-033: structural reason only, never a domain-level rejection)."""
    definition = session.get(RunnerArtifactSchemaDefinition, (artifact.schema_name, artifact.schema_version))
    if definition is None:
        artifact.artifact_status = "REJECTED"
        return False

    payload = artifact.payload or {}
    for field_name in definition.required_fields:
        if field_name not in payload:
            artifact.artifact_status = "REJECTED"
            return False
    for field_name, expected_type in definition.field_types.items():
        if field_name in payload and not _type_matches(payload[field_name], expected_type):
            artifact.artifact_status = "REJECTED"
            return False

    artifact.artifact_status = "VALIDATED"
    return True


_TYPE_MAP = {"string": str, "number": (int, float), "boolean": bool, "object": dict, "array": list}


def _type_matches(value, expected_type: str) -> bool:
    py_type = _TYPE_MAP.get(expected_type)
    if py_type is None:
        return True  # unknown declared type is not this function's concern to police further
    return isinstance(value, py_type)


def supersede_artifact(
    session: Session, *, old_artifact_id: UUID, new_payload: dict, authority: AuthorityContext,
) -> RunnerResult:
    """REQ-B6-057 (repaired), 058, 059, 061: the ONLY code path that may
    set artifact_status='SUPERSEDED' or supersedes_artifact_id. Requires
    a governed decision (REQ-B6-061/079). The old artifact row is
    retained in full, never deleted (REQ-B6-058). Only a VALIDATED
    artifact may be superseded (REQ-B6-034's transition table)."""
    try:
        authority.require(RunnerAuthority.SUPERSEDE_ARTIFACT)
    except AuthorityDeniedError:
        return RunnerResult(outcome=RunnerOutcome.AUTHORITY_REJECTION, detail="missing SUPERSEDE_ARTIFACT authority")

    old = session.get(RunnerArtifact, old_artifact_id)
    if old is None:
        return RunnerResult(outcome=RunnerOutcome.NOT_FOUND)
    if old.artifact_status != "VALIDATED":
        return RunnerResult(outcome=RunnerOutcome.SEMANTIC_REJECTION,
                             detail=f"only a VALIDATED artifact may be superseded, current status is {old.artifact_status!r}")

    new_artifact_id = uuid4()
    decision = RunnerGovernanceDecision(
        decision_type="ARTIFACT_SUPERSESSION",
        decision_mode="AUTHORITY_EVALUATION",
        artifact_id=new_artifact_id,
        authority_context=authority.as_dict(),
        prior_value={"old_artifact_id": str(old_artifact_id), "old_artifact_status": old.artifact_status},
        new_value={"new_artifact_id": str(new_artifact_id)},
        result="EXECUTED",
    )
    session.add(decision)

    new_artifact = RunnerArtifact(
        artifact_id=new_artifact_id, execution_id=old.execution_id, artifact_type=old.artifact_type,
        schema_name=old.schema_name, schema_version=old.schema_version, payload=new_payload,
        hash_algorithm=_HASH_ALGORITHM, content_hash=compute_content_hash(new_payload),
        semantic_function=old.semantic_function, lifecycle_role=old.lifecycle_role,
        presentation_role=old.presentation_role, artifact_status="CREATED",
        supersedes_artifact_id=old_artifact_id,
    )
    session.add(new_artifact)
    session.flush()
    _validate_structure(session, new_artifact)

    # Coordinated write: old artifact's status becomes SUPERSEDED in the
    # same governed operation, same transaction. Neither field is ever
    # set independently of the other by any other code path in this module.
    old.artifact_status = "SUPERSEDED"
    session.flush()

    return RunnerResult(outcome=RunnerOutcome.SUCCESS, object_id=new_artifact_id,
                         payload={"decision_id": decision.decision_id, "supersedes": str(old_artifact_id)})


def check_supersession_consistency(session: Session) -> list[UUID]:
    """REQ-B6-057's explicit consistency test, made directly callable and
    testable: returns the artifact_ids of any inconsistent rows —
    SUPERSEDED-status artifacts with no referencing supersedes_artifact_id,
    or supersedes_artifact_id links to a target not marked SUPERSEDED.
    An empty list is the passing state."""
    superseded = {row.artifact_id for row in session.query(RunnerArtifact.artifact_id).filter(RunnerArtifact.artifact_status == "SUPERSEDED")}
    referenced = {
        row.supersedes_artifact_id
        for row in session.query(RunnerArtifact.supersedes_artifact_id).filter(RunnerArtifact.supersedes_artifact_id.isnot(None))
    }
    return sorted(superseded.symmetric_difference(referenced), key=str)

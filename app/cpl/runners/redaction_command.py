"""Operator command for the governed expurgation of vehicle identifiers
(REQ-B6-091). Simulation by default: nothing is written without --executer.

    python -m app.cpl.runners.redaction_command --motif RETENTION_POLICY \\
        --operateur OPERATEUR-REF [--avant 2026-01-01T00:00:00+00:00] \\
        [--artefact UUID ...] [--executer]

Prints counts and artifact identifiers only, never a payload value. The
database is the one of DATABASE_URL; the command decides no period: --avant
is a date the operator gives, or every eligible artifact is considered.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID, uuid4

from app.cpl.identity.authority import AuthorityContext
from app.cpl.runners.authority import RunnerAuthority
from app.cpl.runners.outcomes import RunnerOutcome
from app.cpl.runners.redaction import (
    REASONS, plan_redaction, redact_artifact_identifiers, valid_operator_reference,
)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="redaction_command", description=__doc__.split("\n\n")[0])
    p.add_argument("--motif", required=True, choices=REASONS)
    p.add_argument("--operateur", required=True, help="référence opaque de l'opérateur (8 à 64 caractères)")
    p.add_argument("--avant", type=datetime.fromisoformat, default=None,
                   help="seulement les artefacts enregistrés avant cette date (avec fuseau)")
    p.add_argument("--artefact", type=UUID, action="append", default=None, help="limiter à cet artefact (répétable)")
    p.add_argument("--executer", action="store_true", help="appliquer ; sans cette option : simulation")
    return p


def run(argv: Optional[Sequence[str]] = None, session_factory=None, out=sys.stdout) -> int:
    args = _parser().parse_args(argv)
    if not valid_operator_reference(args.operateur):
        print("référence d'opérateur refusée : 8 à 64 caractères parmi lettres, chiffres, _ . : -", file=out)
        return 2
    if args.avant is not None and args.avant.tzinfo is None:
        print("--avant doit porter un fuseau horaire", file=out)
        return 2
    if session_factory is None:
        from app.db.engine import SessionLocal as session_factory
    authority = AuthorityContext(granted=frozenset({RunnerAuthority.REDACT_ARTIFACT}), actor_reference=args.operateur)
    mode = "exécution" if args.executer else "simulation (aucune écriture)"
    with session_factory() as session:
        plan = plan_redaction(session, created_before=args.avant, artifact_ids=args.artefact)
        print(f"mode : {mode}", file=out)
        print(f"artefacts vir_resolution à expurger : {len(plan.to_redact)}", file=out)
        print(f"déjà expurgés : {plan.already_redacted} ; sans plaque ni VIN : {plan.without_identifier}", file=out)
        print(f"refusés (intégrité) : {len(plan.refused)}", file=out)
        for artifact_id, why in plan.refused.items():
            print(f"  refusé {artifact_id} : {why}", file=out)
        if not args.executer:
            for artifact_id in plan.to_redact:
                print(f"  à expurger {artifact_id}", file=out)
            return 0                      # nothing was written: the plan only reads
        operation_id = uuid4()
        done, failed = 0, 0
        for artifact_id in plan.to_redact:
            result = redact_artifact_identifiers(session, artifact_id=artifact_id, reason=args.motif,
                                                 authority=authority, operation_id=operation_id)
            if result.outcome == RunnerOutcome.SUCCESS:
                session.commit()
                done += len(result.payload["redacted"])
            elif result.outcome == RunnerOutcome.NO_CHANGE:
                session.commit()
            else:
                session.rollback()
                failed += 1
                print(f"  non expurgé {artifact_id} : {result.outcome} {result.detail or ''}".rstrip(), file=out)
        print(f"opération {operation_id} : {done} artefact(s) expurgé(s), {failed} échec(s)", file=out)
        return 1 if failed or plan.refused else 0


if __name__ == "__main__":
    sys.exit(run())

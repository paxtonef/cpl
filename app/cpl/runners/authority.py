"""B6 Runner authority classes (REQ-B6-014, 022, 076..079).

Reuses the generic AuthorityContext checker from B3
(app.cpl.identity.authority), matching B5's own precedent — permitted
and recommended by the frozen requirements, not semantically mandated
(WHAT §22: "the Build Structure Challenge found VIR itself has no
Contact concept whatsoever ... no generalized Actor/Role concept is
introduced"). ADMIT_EXECUTION and TRANSITION_EXECUTION_STATUS are kept
distinct authority classes even though REQ-B6-015/077's repair makes
the latter automatic/rule-bound for runner-reported transitions — the
authority *class* still exists and is checked; what changed is that a
runner-reported report satisfies it automatically rather than via a
separate manual grant (see app.cpl.runners.execution.persist_runner_report)."""
from __future__ import annotations

from app.cpl.identity.authority import AuthorityContext, AuthorityDeniedError  # noqa: F401


class RunnerAuthority:
    READ_EXECUTION = "READ_EXECUTION"
    ADMIT_EXECUTION = "ADMIT_EXECUTION"
    TRANSITION_EXECUTION_STATUS = "TRANSITION_EXECUTION_STATUS"
    REGISTER_ARTIFACT = "REGISTER_ARTIFACT"
    SUPERSEDE_ARTIFACT = "SUPERSEDE_ARTIFACT"
    CORRECT_EXECUTION = "CORRECT_EXECUTION"

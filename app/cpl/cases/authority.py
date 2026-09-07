"""B5 Case authority classes (REQ-B5-051, REQ-B5-013).

Reuses the generic AuthorityContext checker from B3
(app.cpl.identity.authority) as a HOW choice — permitted and
recommended by the frozen requirements, not semantically mandated.
A different governed authority-checking mechanism could equally
satisfy REQ-B5-046..051.
"""
from __future__ import annotations

from app.cpl.identity.authority import AuthorityContext, AuthorityDeniedError  # noqa: F401


class CaseAuthority:
    READ_CASE = "READ_CASE"
    CREATE_CASE = "CREATE_CASE"
    TRANSITION_CASE_STATUS = "TRANSITION_CASE_STATUS"
    MANAGE_CASE_PARTICIPANT = "MANAGE_CASE_PARTICIPANT"
    RECORD_CASE_EVENT = "RECORD_CASE_EVENT"
    CORRECT_CASE = "CORRECT_CASE"

"""Lightweight authority-context representation.

B3 consumes authority context; it does not implement the general
authorization/RBAC platform (REQ-B3-081, B3-SB-I05). This module
defines the minimal semantic authority classes required by the
frozen Requirement Matrix (Section 20 / 39) and a simple checkable
context — callers wire this to whatever real authorization system
exists upstream.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class Authority:
    READ_IDENTITY = "READ_IDENTITY"
    RESOLVE_IDENTITY = "RESOLVE_IDENTITY"
    CREATE_CONTACT = "CREATE_CONTACT"
    MANAGE_CONTACT_POINT = "MANAGE_CONTACT_POINT"
    VERIFY_CONTACT_POINT = "VERIFY_CONTACT_POINT"
    ATTACH_ACCOUNT = "ATTACH_ACCOUNT"
    MANAGE_ACCOUNT = "MANAGE_ACCOUNT"
    ASSESS_DUPLICATE = "ASSESS_DUPLICATE"
    PROPOSE_MERGE = "PROPOSE_MERGE"
    AUTHORIZE_MERGE = "AUTHORIZE_MERGE"
    EXECUTE_MERGE = "EXECUTE_MERGE"


class AuthorityDeniedError(Exception):
    """Raised when a caller lacks required authority.

    This is a genuine precondition failure, distinct from a domain
    outcome — callers at the boundary layer are expected to catch
    this and translate it into their own REJECTED/403/etc.
    representation; the frozen WHAT does not choose that mapping.
    """


@dataclass(frozen=True)
class AuthorityContext:
    """Minimal authority context: a set of granted authority classes
    plus an opaque actor reference for provenance (REQ-B3-076)."""

    granted: frozenset[str] = field(default_factory=frozenset)
    actor_reference: str | None = None

    def require(self, *authorities: str) -> None:
        missing = [a for a in authorities if a not in self.granted]
        if missing:
            raise AuthorityDeniedError(f"missing required authority: {', '.join(missing)}")

    def as_dict(self) -> dict:
        return {"granted": sorted(self.granted), "actor_reference": self.actor_reference}

"""CPL B3 — Identity + Accounts service layer.

Implements the 14 frozen primitives authorized by
docs/build/B3_EXECUTION_MANDATE_v0.md against
docs/build/B3_REQUIREMENT_MATRIX_v0.1.md (REQ-B3-001 -> REQ-B3-125).

    CONTACT
        get_contact, resolve_contact, create_contact

    CONTACT POINT
        add_contact_point, verify_contact_point,
        invalidate_contact_point, set_primary_contact_point

    ACCOUNT
        attach_account, resolve_authenticated_contact,
        disable_account, revoke_account

    RECONCILIATION
        detect_duplicate_contact, propose_merge, merge_contacts

No 15th primitive. No generic CRUD. No authentication mechanism.
See each module's docstring for its REQ-B3-* traceability.
"""
from app.cpl.identity.authority import Authority, AuthorityContext, AuthorityDeniedError
from app.cpl.identity.evidence import EmailEvidence, Evidence, PhoneEvidence, ProviderAccountEvidence
from app.cpl.identity.outcomes import (
    IdentityOperationError,
    OperationOutcome,
    OperationResult,
    ResolutionResult,
    ResolutionState,
)
from app.cpl.identity.verification import AssertionRejected, VerificationAssertion

from app.cpl.identity.contacts import create_contact, get_contact, resolve_contact
from app.cpl.identity.contact_points import (
    add_contact_point,
    invalidate_contact_point,
    set_primary_contact_point,
    verify_contact_point,
)
from app.cpl.identity.accounts import (
    attach_account,
    disable_account,
    resolve_authenticated_contact,
    revoke_account,
)
from app.cpl.identity.reconciliation import detect_duplicate_contact, merge_contacts, propose_merge

__all__ = [
    "Authority", "AuthorityContext", "AuthorityDeniedError",
    "Evidence", "EmailEvidence", "PhoneEvidence", "ProviderAccountEvidence",
    "OperationOutcome", "OperationResult", "ResolutionState", "ResolutionResult", "IdentityOperationError",
    "VerificationAssertion", "AssertionRejected",
    "get_contact", "resolve_contact", "create_contact",
    "add_contact_point", "verify_contact_point", "invalidate_contact_point", "set_primary_contact_point",
    "attach_account", "resolve_authenticated_contact", "disable_account", "revoke_account",
    "detect_duplicate_contact", "propose_merge", "merge_contacts",
]

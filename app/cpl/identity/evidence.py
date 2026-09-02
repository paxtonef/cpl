"""Identity evidence types consumed by the canonical resolution engine.

One resolution semantics, multiple evidence types (F-B3-05,
REQ-B3-004..011). Authenticated provider identity is *an* evidence
type here, not a separate identity ontology.
"""
from __future__ import annotations

from dataclasses import dataclass


class Evidence:
    """Base marker for identity evidence."""


@dataclass(frozen=True)
class EmailEvidence(Evidence):
    value: str


@dataclass(frozen=True)
class PhoneEvidence(Evidence):
    value: str


@dataclass(frozen=True)
class ProviderAccountEvidence(Evidence):
    provider: str
    provider_subject: str

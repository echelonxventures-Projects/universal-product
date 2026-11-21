"""UCOS Ω∞ — Universal Meta-Kernel (PROGRAM-002, WAVE-2).

The Universal Meta-Kernel is the immutable engineering substrate upon which every
future capability, provider, project, civilization, organization, technology,
intelligence, domain, and execution model is constructed. It contains ONLY universal
meta-abstractions and NO concrete domain, provider, technology, or Earth assumptions.

Constitutional design (why this is the *smallest possible* kernel):

    * A single reflective root — :data:`~engine.kernel.meta.META_TYPE_ROOT` — closes the
      open world without any finite base enumeration. ``MetaType`` is itself a
      ``MetaObject`` classified by ``MetaType``; the type of types is registered, not
      hard-coded.
    * Every concept-category is a **registered** ``MetaType`` (DATA), never a member of a
      closed enum and never a code branch. A previously unknown civilization, language
      family, value-exchange system, taxation model, audit model, temporal model,
      governance model, scientific model, provider category, capability domain or
      execution model is admitted by *registration only* — the kernel is not redesigned
      (Engineering Rule 7).
    * Everything possesses identity (Rule 3), participates in governance (Rule 4) and
      supports unlimited extension (Rule 5). Providers implement; the kernel abstracts
      (Rule 6).

The kernel is technology/language/runtime/infrastructure/database/cloud/domain/
organization/industry/civilization/planet/time/calendar/currency/tax/audit/AI/provider/
future independent. It is stdlib-only and deterministic (no wall-clock, no RNG, no
network on any determined path).
"""

from __future__ import annotations

from engine.kernel.governance import (
    Constraint,
    Governance,
    GovernanceDecision,
    Policy,
)
from engine.kernel.identity import UniversalIdentity, canonical_json, content_digest, mint
from engine.kernel.kernel import MetaKernel
from engine.kernel.meta import META_TYPE_ROOT, MetaObject, MetaTypeRef
from engine.kernel.registry import AdmissionRecord, UniversalRegistry

__all__ = [
    "MetaKernel",
    "UniversalRegistry",
    "AdmissionRecord",
    "MetaObject",
    "MetaTypeRef",
    "META_TYPE_ROOT",
    "Governance",
    "Policy",
    "Constraint",
    "GovernanceDecision",
    "UniversalIdentity",
    "mint",
    "canonical_json",
    "content_digest",
]

__kernel_version__ = "1.0.0"

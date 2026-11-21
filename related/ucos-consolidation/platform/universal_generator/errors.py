"""UCOS-UNG-001 — Universal Ω Nucleus Generator error taxonomy.

The generator reuses the certified Foundation error discipline: every error is rooted in
:class:`~platform.foundation.errors.PlatformError`, carries a stable ``EC2-UNG-*`` code and
structured, non-secret context, and fails **closed**.

Failing closed matters more here than almost anywhere else. A generator that guesses produces
an artifact nobody declared, and a generated artifact carries the authority of the declaration
it came from — so a guess would launder itself into Repository Truth. Every absence below is
therefore a refusal: an unknown template, an unresolved destination token, a target naming a
template that is not registered.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class GeneratorError(PlatformError):
    """Base class for all Universal Ω Nucleus Generator (UNG-001) errors."""

    code = "EC2-UNG-000"


class GenerationTargetError(GeneratorError):
    """A declared generation target is malformed, incomplete, or names an unknown kind."""

    code = "EC2-UNG-TARGET-001"


class GenerationTemplateError(GeneratorError):
    """A template is not registered, is registered twice differently, or refused to render."""

    code = "EC2-UNG-TEMPLATE-001"


class GenerationDestinationError(GeneratorError):
    """A destination pattern carries a token the declaration cannot resolve (fail-closed)."""

    code = "EC2-UNG-DESTINATION-001"


class GenerationPlanError(GeneratorError):
    """A generation plan is empty, internally inconsistent, or collides on a destination."""

    code = "EC2-UNG-PLAN-001"


__all__ = [
    "GeneratorError",
    "GenerationTargetError",
    "GenerationTemplateError",
    "GenerationDestinationError",
    "GenerationPlanError",
]

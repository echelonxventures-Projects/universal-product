"""EPIC-RTE-002 — Execution Authorization (Runtime Execution Platform).

Realises **Execution Authorization**: the gate that decides whether a
:class:`~engine.runtime.composition.RuntimeComposition` may be executed by the
platform. Authorisation confers **engineering-execution authority only** and never
constitutional authority or finality (RUNTIME-013 ORL-22; IP-01 / DE-05 / C-05):
while the external gates (EC-1) remain open, an authorised execution asserts
nothing beyond provisional engineering execution.

The gate reuses the EC-1 provisional-state disclosure verbatim
(:func:`engine.runtime.disclosure.disclosure_present`, EPIC-005): a composition may
be authorised **only** if it carries a well-formed disclosure. The result is a
deterministic, recorded :class:`Authorization` — it grants no capability and runs
nothing (ORL-15).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.disclosure import disclosure_present
from engine.runtime.execution.errors import ExecutionAuthorizationError

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition

_logger = get_logger("runtime.execution.authorization")

#: The only authority an execution may ever hold while the gates are open.
EXECUTION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

#: The recorded authorization format.
AUTHORIZATION_FORMAT = "ucos-execution-authorization/1.0.0"


@dataclass(frozen=True, slots=True)
class Authorization:
    """A recorded, non-authoritative execution authorisation decision (ORL-22)."""

    authorization_id: str
    composition_id: str
    subject: str
    authority: str
    granted: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_format": AUTHORIZATION_FORMAT,
            "authorization_id": self.authorization_id,
            "composition_id": self.composition_id,
            "subject": self.subject,
            "authority": self.authority,
            "granted": self.granted,
        }


def authorize(composition: RuntimeComposition, *, subject: str = "engineering") -> Authorization:
    """Authorise ``composition`` for engineering execution (deterministic).

    Args:
        composition: the composition to authorise.
        subject: a non-secret identifier for the requesting engineering subject.

    Raises:
        ExecutionAuthorizationError: if the composition carries no well-formed EC-1
            provisional-state disclosure (execution may not proceed while the gates
            are open without acknowledging their provisionality).
    """
    with trace("runtime.execution.authorize", composition=composition.composition_id):
        if not disclosure_present(composition.disclosure):
            raise ExecutionAuthorizationError(
                "composition is missing the EC-1 provisional-state disclosure; "
                "execution is refused",
                composition_id=composition.composition_id,
            )
        authorization = Authorization(
            authorization_id=_authorization_id(composition.composition_id, subject),
            composition_id=composition.composition_id,
            subject=subject,
            authority=EXECUTION_AUTHORITY,
            granted=True,
        )
    _logger.info(
        "runtime.execution.authorized",
        authorization_id=authorization.authorization_id,
        composition_id=composition.composition_id,
        subject=subject,
    )
    return authorization


def require_authorization(authorization: Authorization) -> Authorization:
    """Return ``authorization`` if it grants engineering execution, else raise."""
    if not authorization.granted or authorization.authority != EXECUTION_AUTHORITY:
        raise ExecutionAuthorizationError(
            "execution authorization is not granted or asserts a foreign authority",
            authorization_id=authorization.authorization_id,
            authority=authorization.authority,
        )
    return authorization


def _authorization_id(composition_id: str, subject: str) -> str:
    payload = f"{composition_id}||subject={subject}||authority={EXECUTION_AUTHORITY}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"UCOS-EXEC-AUTH-{digest[:16]}"


__all__ = [
    "EXECUTION_AUTHORITY",
    "AUTHORIZATION_FORMAT",
    "Authorization",
    "authorize",
    "require_authorization",
]

"""TASK-000017 — Gap Report model (EPIC-003, IMP-007 §17).

When any pipeline stage fails, the compiler halts and produces a **Gap Report**:
a structured, auditable record of *what* failed, *where* in the pipeline, and the
non-secret context needed to diagnose it (ARCH-GOV-001 Law 003 — STOP → GAP REPORT
→ REQUEST AUTHORITY). Gap Reports are the compiler's failure currency; the
orchestrator (TASK-000028) attaches one to every halted build.

A Gap Report is derived deterministically from a :class:`CompilerError` and the
stage that raised it, so identical failures produce identical reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.compiler.errors import CompilerError


class Stage(str, Enum):
    """The deterministic pipeline stages (IMP-007 §3)."""

    PARSE = "parse"
    VALIDATE = "validate"
    RESOLVE = "resolve"
    COMPILE = "compile"
    OPTIMIZE = "optimize"
    PACKAGE = "package"
    SIGN = "sign"
    PUBLISH = "publish"


@dataclass(frozen=True, slots=True)
class GapReport:
    """An auditable record of a halted compilation (IMP-007 §17)."""

    stage: Stage
    code: str
    message: str
    blueprint_id: str | None = None
    context: dict[str, Any] | None = None

    @classmethod
    def from_error(
        cls,
        stage: Stage,
        error: CompilerError,
        *,
        blueprint_id: str | None = None,
    ) -> GapReport:
        """Build a Gap Report from the error that halted ``stage``."""
        return cls(
            stage=stage,
            code=error.code,
            message=error.message,
            blueprint_id=blueprint_id,
            context=dict(error.context) if error.context else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialisable, auditable representation of the report."""
        payload: dict[str, Any] = {
            "gap_report": True,
            "stage": self.stage.value,
            "code": self.code,
            "message": self.message,
        }
        if self.blueprint_id is not None:
            payload["blueprint_id"] = self.blueprint_id
        if self.context:
            payload["context"] = self.context
        return payload


__all__ = ["Stage", "GapReport"]

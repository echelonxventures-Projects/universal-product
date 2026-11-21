"""UKDA Part 06/14 — Agent & Developer Auto-Bootstrap (EPIC-UKDA).

A newly created AI agent or developer must require *zero* architectural
explanation: by consuming the canonical knowledge base alone they immediately know
the why, what, how, rules, standards, constraints, current architecture, previous
decisions, and future direction.

    * :class:`BootstrapDigest` — a deterministic, structured projection of the base
      into exactly the sections an agent/developer needs on first contact. It
      renders both a machine-consumable ``to_dict`` (for agent context loading) and
      a human-readable Markdown brief (for developers).

The digest is derived purely from ratified/active canonical knowledge, so it is
always current and never a separately maintained artifact.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind
from engine.knowledge.store import KnowledgeBase

#: The canonical section order every agent/developer receives (stable).
BOOTSTRAP_SECTIONS: tuple[str, ...] = (
    "constitution",
    "principles",
    "standards",
    "conventions",
    "rules",
    "constraints",
    "patterns",
    "anti_patterns",
    "decisions",
    "current_state",
)


@dataclass(frozen=True, slots=True)
class BootstrapDigest:
    """A deterministic onboarding digest for an agent or developer (Part 06/14)."""

    constitution: tuple[str, ...]
    principles: tuple[str, ...]
    standards: tuple[str, ...]
    conventions: tuple[str, ...]
    rules: tuple[str, ...]
    constraints: tuple[str, ...]
    patterns: tuple[str, ...]
    anti_patterns: tuple[str, ...]
    decisions: tuple[str, ...]
    current_state: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "constitution": list(self.constitution),
            "principles": list(self.principles),
            "standards": list(self.standards),
            "conventions": list(self.conventions),
            "rules": list(self.rules),
            "constraints": list(self.constraints),
            "patterns": list(self.patterns),
            "anti_patterns": list(self.anti_patterns),
            "decisions": list(self.decisions),
            "current_state": dict(self.current_state),
        }

    def to_markdown(self) -> str:
        lines = [
            "# UCOS Ω∞ — Repository Bootstrap Brief",
            "",
            "You are now oriented. Everything below is derived from the single "
            "canonical knowledge base. Treat ratified knowledge as binding.",
        ]
        sections = [
            ("Constitution", self.constitution),
            ("Principles", self.principles),
            ("Standards", self.standards),
            ("Conventions", self.conventions),
            ("Rules", self.rules),
            ("Constraints", self.constraints),
            ("Patterns", self.patterns),
            ("Anti-patterns", self.anti_patterns),
            ("Decisions", self.decisions),
        ]
        for title, items in sections:
            lines.append("")
            lines.append(f"## {title}")
            if items:
                lines.extend(f"- {item}" for item in items)
            else:
                lines.append("- _none_")
        lines.append("")
        lines.append("## Current canonical state")
        for key, value in sorted(self.current_state.items()):
            lines.append(f"- **{key}**: {value}")
        lines.append("")
        return "\n".join(lines) + "\n"


def _entries(base: KnowledgeBase, kind: KnowledgeKind) -> tuple[str, ...]:
    return tuple(f"{o.cko_id} — {o.title}: {o.statement}" for o in base.by_kind(kind))


def build_digest(base: KnowledgeBase) -> BootstrapDigest:
    """Project the canonical base into a deterministic bootstrap digest."""
    constitution = tuple(
        f"{o.cko_id} — {o.title}: {o.statement}"
        for o in base.by_authority(KnowledgeAuthority.CONSTITUTIONAL)
    )
    decisions = tuple(
        f"{d.decision_id} — {d.title}: {d.chosen_architecture}" for d in base.decisions()
    )
    current_state = {
        "total_objects": len(base.objects()),
        "total_decisions": len(base.decisions()),
        "active_objects": len(base.active_objects()),
        "constitutional_objects": len(base.by_authority(KnowledgeAuthority.CONSTITUTIONAL)),
    }
    return BootstrapDigest(
        constitution=constitution,
        principles=_entries(base, KnowledgeKind.PRINCIPLE),
        standards=_entries(base, KnowledgeKind.STANDARD),
        conventions=_entries(base, KnowledgeKind.CONVENTION),
        rules=_entries(base, KnowledgeKind.RULE),
        constraints=_entries(base, KnowledgeKind.CONSTRAINT),
        patterns=_entries(base, KnowledgeKind.PATTERN),
        anti_patterns=_entries(base, KnowledgeKind.ANTI_PATTERN),
        decisions=decisions,
        current_state=current_state,
    )


__all__ = ["BOOTSTRAP_SECTIONS", "BootstrapDigest", "build_digest"]

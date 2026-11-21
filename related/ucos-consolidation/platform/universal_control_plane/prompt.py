"""UCOS-CTRL-000001 — Universal Prompt Engine.

Renders deterministic, context-rich prompts for execution agents.
Every prompt is content-addressed: the same item + agent + universe + context
always produces the same prompt text and the same prompt_id.

Templates are registered data, not hard-coded strings. The engine ships
with a default template; projects register specialised ones.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import PromptRenderError
from platform.universal_control_plane.ontology import AgentRecord, BacklogItem, Prompt
from typing import Any

_DEFAULT_TEMPLATE_ID = "ctrl.prompt.default"

_DEFAULT_TEMPLATE = """\
# UCOS Control Plane — Agent Execution Prompt

## Universe
{universe_id}

## Assigned Work Item
ID:          {item_id}
Title:       {title}
Priority:    {priority}
Description: {description}
Milestone:   {milestone_id}
Objective:   {objective_id}

## Agent
ID:   {agent_id}
Name: {agent_name}
Kind: {agent_kind}

## Success Criteria
{success_criteria}

## Context
{context}

## Instructions
Execute the assigned work item to the standard defined by the success criteria.
Record evidence, emit a determination, and register all produced artifacts.
"""


def _context_digest(context: dict[str, Any]) -> str:
    blob = json.dumps(context, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _prompt_id(item_id: str, agent_id: str, universe_id: str, ctx_digest: str) -> str:
    payload = {"item": item_id, "agent": agent_id, "universe": universe_id, "ctx": ctx_digest}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "PRM-" + hashlib.sha256(blob.encode()).hexdigest()[:12]


@dataclass
class PromptEngine:
    """Renders and stores agent prompts. Templates are registered data."""

    _templates: dict[str, str] = field(default_factory=dict)
    _prompts: dict[str, Prompt] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._templates[_DEFAULT_TEMPLATE_ID] = _DEFAULT_TEMPLATE

    def register_template(self, template_id: str, template: str) -> None:
        if not template_id.strip():
            raise PromptRenderError("template_id must be non-empty")
        if not template.strip():
            raise PromptRenderError("template body must be non-empty")
        self._templates[template_id] = template

    def render(
        self,
        item: BacklogItem,
        agent: AgentRecord,
        *,
        universe_id: str,
        success_criteria: str = "",
        context: dict[str, Any] | None = None,
        template_id: str = _DEFAULT_TEMPLATE_ID,
        tick: int = 0,
    ) -> Prompt:
        """Render a prompt for *item* + *agent* and cache it by content-addressed ID."""
        if template_id not in self._templates:
            raise PromptRenderError(f"template not registered: {template_id!r}")
        ctx = context or {}
        ctx_digest = _context_digest(ctx)
        pid = _prompt_id(item.item_id, agent.agent_id, universe_id, ctx_digest)

        if pid in self._prompts:
            return self._prompts[pid]

        ctx_text = "\n".join(f"  {k}: {v}" for k, v in sorted(ctx.items())) if ctx else "(none)"
        try:
            text = self._templates[template_id].format(
                universe_id=universe_id,
                item_id=item.item_id,
                title=item.title,
                priority=item.priority,
                description=item.description or "(none)",
                milestone_id=item.milestone_id or "(none)",
                objective_id=item.objective_id or "(none)",
                agent_id=agent.agent_id,
                agent_name=agent.name,
                agent_kind=agent.kind,
                success_criteria=success_criteria or "(none)",
                context=ctx_text,
            )
        except KeyError as exc:
            raise PromptRenderError(
                f"template {template_id!r} references unknown field {exc}"
            ) from exc

        prompt = Prompt(
            prompt_id=pid,
            item_id=item.item_id,
            agent_id=agent.agent_id,
            universe_id=universe_id,
            text=text,
            context_digest=ctx_digest,
            template_id=template_id,
            tick=tick,
        )
        self._prompts[pid] = prompt
        return prompt

    def get(self, prompt_id: str) -> Prompt | None:
        return self._prompts.get(prompt_id)

    def for_item(self, item_id: str) -> list[Prompt]:
        return [p for p in self._prompts.values() if p.item_id == item_id]

    def count(self) -> int:
        return len(self._prompts)

    def template_ids(self) -> list[str]:
        return sorted(self._templates)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "PromptEngine",
            "templates": self.template_ids(),
            "prompts_rendered": self.count(),
            "prompts": [p.to_dict() for p in self._prompts.values()],
        }

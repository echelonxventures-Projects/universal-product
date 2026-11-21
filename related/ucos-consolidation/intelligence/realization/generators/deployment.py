"""URI-000001 — the Deployment Generator.

Realizes *how a realized universe reaches production*. The stage sequence is not invented
here: it is the gate ladder of UCIC-001 (the frozen Universal Capability Implementation
Contract), which URI-000001 is itself governed by. Each stage is bound to:

* the concrete artifacts it deploys (read from what the upstream generators produced);
* the fail-closed condition that must hold to advance;
* the rollback action if it does not.

Rollback is total and non-destructive by construction: every deployed artifact is
regenerable from canonical knowledge, so the rollback action is *regenerate at the prior
knowledge seal*, never "restore from a snapshot of unknown provenance".

Two projections: a deployment descriptor and a CI pipeline. The YAML is emitted by a
small deterministic writer rather than a third-party serializer, keeping the subsystem
standard-library only (UCKO-PRIN-0003 / TP-04).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from intelligence.realization.contracts import (
    FAMILY_ORDER,
    ArtifactFamily,
    GeneratedArtifact,
    MediaKind,
)
from intelligence.realization.generators.base import GenerationContext, Generator

DEPLOYMENT_DOCUMENT_FORMAT = "ucos-uri-deployment/1.0.0"

#: The gate ladder, quoted from UCIC-001 Output 3 (FROZEN v1.0). Not invented here.
UCIC_GATES: tuple[tuple[str, str], ...] = (
    ("READY_TO_IMPLEMENT", "on frontier, dependencies satisfied, authorized, SoD ok"),
    ("IMPLEMENTED", "additive-only change on declared surfaces, one capability"),
    ("VALIDATED", "static + dynamic + tests + coverage + evidence"),
    ("CERTIFIED", "certification gates pass, certifier != executor"),
    ("READY_TO_COMMIT", "intelligence + twin + registry updated, commit hygiene"),
    ("READY_FOR_PRODUCTION", "deployment + operations + production gates satisfied"),
)

_GATE_SOURCE = "00-MASTER/UCIC-001-UNIVERSAL-CAPABILITY-IMPLEMENTATION-CONTRACT.md"


def _yaml_scalar(value: Any) -> str:
    """Render a scalar deterministically, quoting only when necessary."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    needs_quote = (
        not text
        or text[0] in "-?:,[]{}#&*!|>'\"%@` "
        or text[-1] == " "
        or ": " in text
        or text.lower() in {"true", "false", "null", "yes", "no", "on", "off"}
    )
    if needs_quote:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def _yaml_lines(value: Any, indent: int = 0) -> list[str]:
    """Emit deterministic YAML for nested mappings/sequences/scalars."""
    pad = "  " * indent
    if isinstance(value, Mapping):
        lines: list[str] = []
        for key in value:
            item = value[key]
            if isinstance(item, Mapping | list | tuple) and item:
                lines.append(f"{pad}{key}:")
                lines.extend(_yaml_lines(item, indent + 1))
            elif isinstance(item, Mapping):
                lines.append(f"{pad}{key}: {{}}")
            elif isinstance(item, list | tuple):
                lines.append(f"{pad}{key}: []")
            else:
                lines.append(f"{pad}{key}: {_yaml_scalar(item)}")
        return lines
    if isinstance(value, list | tuple):
        lines = []
        for item in value:
            if isinstance(item, Mapping):
                nested = _yaml_lines(item, indent + 1)
                first = nested[0].lstrip() if nested else "{}"
                lines.append(f"{pad}- {first}")
                lines.extend(nested[1:])
            else:
                lines.append(f"{pad}- {_yaml_scalar(item)}")
        return lines
    return [f"{pad}{_yaml_scalar(value)}"]


class DeploymentGenerator(Generator):
    """Derives the deployment descriptor and CI pipeline for one realization target."""

    family = ArtifactFamily.DEPLOYMENT
    name = "uri.deployment"
    version = "1.0.0"

    def generate(self, context: GenerationContext) -> tuple[GeneratedArtifact, ...]:
        slug = context.target.path_slug
        descriptor = self._descriptor(context)
        return (
            self.json_artifact(
                context,
                relative_path=f"deployment/{slug}-deployment.json",
                payload=descriptor,
            ),
            self.text_artifact(
                context,
                relative_path=f"deployment/{slug}-pipeline.yml",
                media=MediaKind.YAML,
                lines=self._pipeline(context, descriptor),
            ),
        )

    # -- derivation -----------------------------------------------------------

    def _deployables(self, context: GenerationContext) -> list[dict[str, Any]]:
        """Everything the upstream families produced for this target, in family order."""
        deployables = []
        for family in FAMILY_ORDER:
            for path in context.upstream_paths(family):
                deployables.append({"family": family.value, "path": path})
        return deployables

    def _stages(
        self, context: GenerationContext, deployables: Sequence[Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        runtime_descriptor = context.upstream_artifact(ArtifactFamily.RUNTIME, "-runtime.json")
        runtime_module = context.upstream_artifact(ArtifactFamily.RUNTIME, "_runtime.py")
        stages: list[dict[str, Any]] = []
        for index, (gate, condition) in enumerate(UCIC_GATES, start=1):
            stages.append(
                {
                    "order": index,
                    "gate": gate,
                    "advance_condition": condition,
                    "fail_closed": True,
                    "action": self._action(gate, runtime_descriptor, runtime_module),
                    "rollback": {
                        "strategy": "regenerate-at-prior-knowledge-seal",
                        "destructive": False,
                        "detail": (
                            "Every deployed artifact is regenerable from canonical "
                            "knowledge; rolling back re-runs realization at the previous "
                            "knowledge seal. No snapshot of unknown provenance is used."
                        ),
                    },
                }
            )
        stages[-1]["artifacts"] = [dict(entry) for entry in deployables]
        return stages

    @staticmethod
    def _action(
        gate: str, runtime_descriptor: str | None, runtime_module: str | None
    ) -> dict[str, Any]:
        actions: dict[str, dict[str, Any]] = {
            "READY_TO_IMPLEMENT": {
                "operation": "verify-authority",
                "detail": "confirm the governing determination authorizes this realization",
            },
            "IMPLEMENTED": {
                "operation": "materialize-artifacts",
                "detail": "write generated artifacts to the declared additive surface only",
            },
            "VALIDATED": {
                "operation": "run-generated-tests",
                "detail": "execute the generated test artifacts and the mechanical checks",
            },
            "CERTIFIED": {
                "operation": "seal-evidence",
                "detail": "emit the consolidated evidence bundle and the governance decision",
            },
            "READY_TO_COMMIT": {
                "operation": "verify-idempotence",
                "detail": "re-run realization and assert byte-identical output",
            },
            "READY_FOR_PRODUCTION": {
                "operation": "boot-runtime",
                "detail": "boot the generated runtime and require a ready health report",
                "runtime_descriptor": runtime_descriptor,
                "runtime_entrypoint": (f"{runtime_module}:boot" if runtime_module else None),
            },
        }
        return actions[gate]

    def _descriptor(self, context: GenerationContext) -> dict[str, Any]:
        target = context.target
        deployables = self._deployables(context)
        stages = self._stages(context, deployables)
        payload = context.envelope(
            artifact_id=f"UCOS-URI-DEPLOY-{target.path_slug.upper()}",
            title=f"{target.universe} — Realized Deployment Plan",
            document_format=DEPLOYMENT_DOCUMENT_FORMAT,
        )
        payload.update(
            {
                "universe": target.universe,
                "target_id": target.target_id,
                "target_seal": target.seal,
                "gate_ladder_source": _GATE_SOURCE,
                "gate_ladder": [
                    {"gate": gate, "condition": condition} for gate, condition in UCIC_GATES
                ],
                "stages": stages,
                "stage_count": len(stages),
                "deployables": deployables,
                "deployable_count": len(deployables),
                "rollback": {
                    "strategy": "regenerate-at-prior-knowledge-seal",
                    "reversible": True,
                    "destructive": False,
                    "prerequisite": "the prior knowledge seal is recorded in evidence",
                },
                "environments": [
                    {
                        "name": "local",
                        "artifact_root": "realization/",
                        "gate_floor": "IMPLEMENTED",
                    },
                    {
                        "name": "ci",
                        "artifact_root": "realization/",
                        "gate_floor": "READY_TO_COMMIT",
                    },
                    {
                        "name": "production",
                        "artifact_root": "realization/",
                        "gate_floor": "READY_FOR_PRODUCTION",
                    },
                ],
                "expected_knowledge_seal": context.intake.knowledge_seal,
                "source_ckos": list(target.cko_ids),
            }
        )
        return payload

    # -- pipeline -------------------------------------------------------------

    def _pipeline(self, context: GenerationContext, descriptor: Mapping[str, Any]) -> list[str]:
        target = context.target
        lines = self.provenance_comment(context, "#")
        pipeline: dict[str, Any] = {
            "name": f"URI realization — {target.universe}",
            "on": {"workflow_dispatch": {}, "push": {"paths": ["knowledge/**"]}},
            "concurrency": {
                "group": f"uri-realization-{target.path_slug}",
                "cancel-in-progress": False,
            },
            "env": {
                "UCOS_EXPECTED_KNOWLEDGE_SEAL": context.intake.knowledge_seal,
                "UCOS_TARGET_ID": target.target_id,
            },
            "jobs": {
                "realize": {
                    "runs-on": "ubuntu-latest",
                    "steps": self._pipeline_steps(descriptor),
                }
            },
        }
        lines.append("")
        lines.extend(_yaml_lines(pipeline))
        lines.append("")
        return lines

    @staticmethod
    def _pipeline_steps(descriptor: Mapping[str, Any]) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = [
            {"name": "Checkout", "uses": "actions/checkout@v4"},
        ]
        commands = {
            "READY_TO_IMPLEMENT": "python -m intelligence.realization plan",
            "IMPLEMENTED": "python -m intelligence.realization realize",
            "VALIDATED": "python -m intelligence.realization govern",
            "CERTIFIED": "python -m intelligence.realization evidence",
            "READY_TO_COMMIT": "python -m intelligence.realization verify",
            "READY_FOR_PRODUCTION": "python -m intelligence.realization trace",
        }
        for stage in descriptor["stages"]:
            gate = stage["gate"]
            steps.append(
                {
                    "name": f"Gate {stage['order']} — {gate}",
                    "run": commands[gate],
                }
            )
        return steps


__all__ = ["DEPLOYMENT_DOCUMENT_FORMAT", "UCIC_GATES", "DeploymentGenerator"]

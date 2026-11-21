"""URKE-000001 Part 09 — the bridge to disposition. This capability decides nothing.

UCON-000001 owns disposition. Every subject in the ledger is presented into its construct registry
and receives whatever disposition the declared rules there select. Nothing here overrides it,
nothing here retries for a better answer, and nothing here treats a quarantine as a failure — a
governed subject that UCON has quarantined is exactly as governed as one it admitted.

That is the reason "governed" in this capability never means "true", and the reason this module is
thirty lines of presentation rather than a second rule engine.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from engine.construct.model import Evidence as ConstructEvidence
from engine.construct.model import Lineage as ConstructLineage
from engine.construct.model import Presentation
from engine.construct.registry import ConstructRegistry
from engine.recursive_knowledge.ledger import KnowledgeLedger
from engine.recursive_knowledge.model import GovernedEntity, RecursiveKnowledgeError


class BridgeError(RecursiveKnowledgeError):
    """The subject cannot be presented for disposition. A fault, never a disposition."""


def present_plain(registry: ConstructRegistry, entity: GovernedEntity, *, kind: str) -> Any:
    """Present a subject as itself and let the construct foundation dispose of it.

    The only handler there is. An earlier draft had one per facet; they differed in nothing that
    mattered, and a handler per shape would have been a place for a shape to receive special
    treatment.
    """
    evidence = tuple(
        ConstructEvidence(
            source=item.source, statement=item.statement, independent=item.independent
        )
        for item in entity.evidence
    )
    return registry.present(
        Presentation(
            kind=kind,
            natural_key=f"{entity.entity_class}:{entity.natural_key}",
            title=entity.title,
            payload={
                "classification": entity.classification,
                "domain": str(entity.payload.get("domain") or ""),
                "state": entity.state,
                "urke_identity": entity.identity,
            },
            evidence=evidence,
            lineage=ConstructLineage(
                derived_from=entity.lineage.derived_from,
                presented_by=entity.governance,
            ),
        )
    )


#: Every declared entity class, mapped to the handler that presents it. Bound both ways at
#: load time.
HANDLERS: Mapping[str, Callable[..., Any]] = MappingProxyType({"present_plain": present_plain})


def available_handlers() -> frozenset[str]:
    return frozenset(HANDLERS)


def govern(ledger: KnowledgeLedger, *, registry: ConstructRegistry | None = None) -> dict[str, Any]:
    """Present every subject for disposition and report what came back.

    Returns the disposition histogram and, more importantly, the list of subjects that reached no
    active disposition — which must be empty, and which is the whole measurement behind the claim
    that nothing here exists outside governance.
    """
    declaration = ledger.declaration
    store = registry if registry is not None else ConstructRegistry()
    dispositions: dict[str, int] = {}
    ungoverned: list[str] = []
    for entity in ledger.all():
        spec = declaration.entity_class(entity.entity_class)
        handler = HANDLERS.get(spec.bridge_handler)
        if handler is None:
            raise BridgeError(
                f"entity class {entity.entity_class!r} names handler {spec.bridge_handler!r}, "
                "which nothing implements"
            )
        construct = handler(store, entity, kind=spec.ucon_kind)
        record = construct.disposition
        if record is None or not record.active:
            ungoverned.append(entity.identity)
            continue
        dispositions[record.disposition] = dispositions.get(record.disposition, 0) + 1
    return {
        "dispositions": dict(sorted(dispositions.items())),
        "presented_count": len(ledger.all()),
        "registry_constructs": len(store.all()),
        "ungoverned": sorted(ungoverned),
    }


__all__ = ["HANDLERS", "BridgeError", "available_handlers", "govern", "present_plain"]

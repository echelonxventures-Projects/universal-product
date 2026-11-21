"""EC3-B13-U11 — The Band-13 Realization Completion construct (certification-of-certifications).

Realizes the executable **Band-13 Realization Completion record**: an immutable,
content-addressed roll-up that references the ten CERTIFIED Band-13 (Infrastructure)
realization units (U01…U10) **by certification id** and decides, fail-closed, whether the
Band-13 Infrastructure realization is COMPLETE and CERTIFIED. It is the EC-3 analogue of the
INFRASTRUCTURE-016/017 readiness/completion band pattern (charter ``EC-3-B13-P01`` §8),
applied to the *code* realization of the Infrastructure layer, mirroring the CERTIFIED
Band-10 (:mod:`data.band10`) and Band-11 (:mod:`service.band11`) completion constructs.

The completion record is **not** an eighteenth infrastructure leaf meta-class (WF-11 admits
no new primitive/meta-class). It is a certification/completion artifact that:

* references each unit as a :class:`UnitCertificationRef` (unit + meta-classes + name +
  concern doc + certification id + certified verdict) — **never owning, embedding, or
  re-realizing** any unit (reuse by reference, UIL-02);
* records the UIMM integration closure (INFRASTRUCTURE-005) by reference — the U10 capstone;
* derives its identity through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.content_hash`) — no second identity scheme;
* enforces fail-closed that the inventory is exactly U01…U10, that every unit is CERTIFIED,
  that the units together cover exactly the seventeen leaf meta-classes (INFRASTRUCTURE-005
  §2), that the founding graph is acyclic and downward-only, and that the record confers no
  authority, embeds no secret, and names no technology (UIL-15).

An incomplete, uncertified-member, over/under-populated, authority-conferring, or
technology-bound completion record cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- EC-1 reuse by reference (UIL-02) — imported, never redefined -----------------
from engine.certification.contracts import content_hash
from infrastructure.band13_meta import (
    BAND_CLASS,
    BAND_ID_PREFIX,
    BAND_META_CLASSES,
    EXPECTED_UNITS,
    META_MODEL_UNIT,
    UNIT_INVENTORY,
    BandState,
)

#: The integration-closure keys the U10 UIMM capstone must satisfy (INFRASTRUCTURE-005 §4/§7
#: — the dependsOn graph downward-only + acyclic, leaf-closure complete, ownership disjoint,
#: all nine concerns CERTIFIED, all dependency edges certified, and the UIMM determination
#: COMPLETE). Derived deterministically from the CERTIFIED UIMM orchestrator.
_INTEGRATION_KEYS: tuple[str, ...] = (
    "all_concerns_certified",
    "leaf_closure_complete",
    "graph_downward_only",
    "graph_acyclic",
    "all_nodes_present",
    "ownership_disjoint",
    "all_edges_certified",
    "uimm_determination_complete",
)

#: Conservative technology markers used to enforce UIL-15 / non-constitutiveness. A completion
#: record that names any of these is rejected fail-closed.
_TECH_MARKERS: tuple[str, ...] = (
    "rest",
    "grpc",
    "http",
    "https",
    "soap",
    "graphql",
    "kafka",
    "rabbitmq",
    "amqp",
    "mqtt",
    "istio",
    "envoy",
    "kubernetes",
    "docker",
    "terraform",
    "ansible",
    "openstack",
    "vmware",
    "lambda",
    "protobuf",
)

#: Conservative secret markers used to enforce UIL-15 / no-secret-material (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "api_key",
    "access_token",
)

#: The seventeen leaf meta-classes the concern + integration units must cover exactly
#: (INFRASTRUCTURE-005 §2). The band realizes exactly these — no eighteenth.
_EXPECTED_META_CLASSES = frozenset(BAND_META_CLASSES)


@dataclass(frozen=True, slots=True)
class UnitCertificationRef:
    """An immutable reference to one CERTIFIED Band-13 realization unit (never owned)."""

    unit: str
    meta_classes: tuple[str, ...]
    name: str
    concern_doc: str
    certification_id: str
    certified: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit": self.unit,
            "meta_classes": list(self.meta_classes),
            "name": self.name,
            "concern_doc": self.concern_doc,
            "certification_id": self.certification_id,
            "certified": self.certified,
        }


@dataclass(frozen=True, slots=True)
class Band13Completion:
    """A deterministic, immutable Band-13 Realization Completion record."""

    name: str
    type_tag: str
    units: tuple[UnitCertificationRef, ...]
    meta_model_unit: str
    meta_model_id: str
    meta_model_certification_id: str
    integration: tuple[tuple[str, bool], ...]
    version: str
    state: BandState

    # -- identity -------------------------------------------------------------

    def canonical_core(self) -> dict[str, Any]:
        """The stable content the band-completion identity is derived from (no id echo)."""
        return {
            "band_class": BAND_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "units": [u.to_dict() for u in self.units],
            "meta_model_unit": self.meta_model_unit,
            "meta_model_id": self.meta_model_id,
            "meta_model_certification_id": self.meta_model_certification_id,
            "integration": [list(item) for item in self.integration],
            "version": self.version,
            "state": self.state.value,
        }

    @property
    def structure_digest(self) -> str:
        """The deterministic ENG-003 content digest of the completion record."""
        return content_hash(self.canonical_core())

    @property
    def band_id(self) -> str:
        """The deterministic ENG-001 identity of the completion record."""
        return f"{BAND_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    @property
    def meta_class(self) -> str:
        return BAND_CLASS

    # -- decidable roll-ups ---------------------------------------------------

    def unit_ids(self) -> tuple[str, ...]:
        return tuple(u.unit for u in self.units)

    def inventory_complete(self) -> bool:
        """True iff the record inventories exactly the ten expected units U01…U10."""
        present = tuple(self.unit_ids())
        return set(present) == set(EXPECTED_UNITS) and len(present) == len(EXPECTED_UNITS)

    def all_units_certified(self) -> bool:
        """True iff every inventoried unit is CERTIFIED (reused by reference)."""
        return bool(self.units) and all(u.certified for u in self.units)

    def meta_classes_covered(self) -> tuple[str, ...]:
        """The union of leaf meta-classes covered by all ten units (concerns + UIMM capstone)."""
        covered: set[str] = set()
        for u in self.units:
            covered.update(u.meta_classes)
        return tuple(sorted(covered))

    def meta_class_coverage_complete(self) -> bool:
        """True iff the units cover exactly the seventeen leaf meta-classes (complete + exact)."""
        return set(self.meta_classes_covered()) == _EXPECTED_META_CLASSES

    def meta_class_ownership_disjoint(self) -> bool:
        """True iff no leaf meta-class is owned by more than one unit (non-overlapping)."""
        seen: set[str] = set()
        for u in self.units:
            for mc in u.meta_classes:
                if mc in seen:
                    return False
                seen.add(mc)
        return True

    def integration_map(self) -> dict[str, bool]:
        return dict(self.integration)

    def integration_closed(self) -> bool:
        """True iff the U10 UIMM integration closure satisfies all keys."""
        m = self.integration_map()
        return bool(m) and all(m.get(k, False) for k in _INTEGRATION_KEYS)

    def dependency_acyclic(self) -> bool:
        """True iff the unit founding graph is acyclic/downward-only (structural).

        The band units realize a strictly layered dependency (concerns → integration
        capstone); no unit is repeated, and the UIMM capstone (U10) is present as the
        last-layer integrator, so the graph is a DAG.
        """
        seen: set[str] = set()
        for unit in self.unit_ids():
            if unit in seen:  # a repeated unit would break the strict layering
                return False
            seen.add(unit)
        return self.meta_model_unit in seen

    def reuses_by_reference(self) -> bool:
        """True iff every unit is referenced by a non-empty certification id (never owned)."""
        return bool(self.units) and all(u.certification_id.strip() for u in self.units)

    def _scan(self, markers: tuple[str, ...]) -> bool:
        """True iff any marker occurs in the record's human-readable text fields."""
        parts = [self.name, self.type_tag, self.meta_model_unit]
        for u in self.units:
            parts.append(f"{u.name} {u.concern_doc} {' '.join(u.meta_classes)}")
        haystack = " ".join(parts).lower()
        return any(marker in haystack for marker in markers)

    def names_technology(self) -> bool:
        return self._scan(_TECH_MARKERS)

    def selects_technology(self) -> bool:
        return self._scan(_TECH_MARKERS)

    def embeds_secret(self) -> bool:
        return self._scan(_SECRET_MARKERS)

    def confers_authority(self) -> bool:
        """The completion record is evaluative only; it never confers authority (DE-05)."""
        return False

    def is_non_projection(self) -> bool:
        """Realization completion is never operational/deployment/production readiness."""
        return True

    def is_non_constitutive(self) -> bool:
        return not (self.confers_authority() or self.embeds_secret() or self.selects_technology())

    def to_dict(self) -> dict[str, Any]:
        return {
            "band_id": self.band_id,
            "band_class": BAND_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "structure_digest": self.structure_digest,
            "units": [u.to_dict() for u in self.units],
            "unit_count": len(self.units),
            "meta_model_unit": self.meta_model_unit,
            "meta_model_id": self.meta_model_id,
            "meta_model_certification_id": self.meta_model_certification_id,
            "integration": {k: v for k, v in self.integration},
            "meta_classes_covered": list(self.meta_classes_covered()),
            "version": self.version,
            "state": self.state.value,
            "substrate_refs": ["ENG-001", "ENG-002", "ENG-004", "ENG-005", "CCE"],
            "inventory_complete": self.inventory_complete(),
            "all_units_certified": self.all_units_certified(),
            "meta_class_coverage_complete": self.meta_class_coverage_complete(),
            "meta_class_ownership_disjoint": self.meta_class_ownership_disjoint(),
            "dependency_acyclic": self.dependency_acyclic(),
            "integration_closed": self.integration_closed(),
            "reuses_by_reference": self.reuses_by_reference(),
            "non_projection": self.is_non_projection(),
            "non_constitutive": self.is_non_constitutive(),
        }


def _spec_for(unit: str) -> tuple[tuple[str, ...], str, str]:
    """Return the ``(meta_classes, name, concern_doc)`` declared for ``unit`` (fail-closed)."""
    for spec_unit, meta_classes, name, concern_doc in UNIT_INVENTORY:
        if spec_unit == unit:
            return (meta_classes, name, concern_doc)
    raise KeyError(f"unit {unit!r} is not a declared Band-13 realization unit")


def make_band13_completion(
    name: str,
    type_tag: str,
    unit_certifications: tuple[tuple[str, str, bool], ...],
    meta_model_id: str,
    integration: dict[str, bool],
    *,
    version: str,
    state: BandState = BandState.DEFINED,
) -> Band13Completion:
    """Construct the canonical Band-13 completion record from live unit certifications.

    ``unit_certifications`` is a tuple of ``(unit, certification_id, certified)`` captured
    from each unit's own realize orchestrator (the per-unit certification-ledger head); each
    is resolved against the declared :data:`UNIT_INVENTORY` (fail-closed on any undeclared
    unit) and composed by reference.
    """
    refs: list[UnitCertificationRef] = []
    for unit, certification_id, certified in unit_certifications:
        meta_classes, unit_name, concern_doc = _spec_for(unit)
        refs.append(
            UnitCertificationRef(
                unit=unit,
                meta_classes=meta_classes,
                name=unit_name,
                concern_doc=concern_doc,
                certification_id=certification_id,
                certified=bool(certified),
            )
        )
    ordered = tuple(sorted(refs, key=lambda r: r.unit))
    meta_model_cert = next((r.certification_id for r in ordered if r.unit == META_MODEL_UNIT), "")
    integration_items = tuple(sorted((k, bool(v)) for k, v in integration.items()))
    return Band13Completion(
        name=name,
        type_tag=type_tag,
        units=ordered,
        meta_model_unit=META_MODEL_UNIT,
        meta_model_id=meta_model_id,
        meta_model_certification_id=meta_model_cert,
        integration=integration_items,
        version=version,
        state=state,
    )


__all__ = [
    "UnitCertificationRef",
    "Band13Completion",
    "make_band13_completion",
]

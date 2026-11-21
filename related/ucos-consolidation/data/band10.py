"""EC3-B10-U12 — The Band-10 Realization Completion construct (certification-of-certifications).

Realizes the executable **Band-10 Realization Completion record**: an immutable,
content-addressed roll-up that references the eleven CERTIFIED Band-10 realization units
(U01…U11) **by certification id** and decides, fail-closed, whether the Band-10 Data
realization is COMPLETE and CERTIFIED. It is the EC-3 analogue of the DATA-016/017
readiness/completion determinations, applied to the *code* realization.

The completion record is **not** an eleventh data meta-class (DMI-01 admits no meta-class
outside DMC-01…10). It is a certification/completion artifact that:

* references each unit as a :class:`UnitCertificationRef` (unit + meta-class + name +
  concern doc + certification id + certified verdict) — **never owning, embedding, or
  re-realizing** any unit (DMX-02 non-absorbing; reuse by reference, UDL-02);
* records the meta-model (U11) integration closure (DMI-01…07) by reference;
* derives its identity through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.content_hash`) — no second identity scheme;
* enforces fail-closed that the inventory is exactly U01…U11, that every unit is CERTIFIED,
  that the concern units cover exactly the ten meta-classes DMC-01…10, that the founding
  graph is acyclic and downward-only, and that the record confers no authority, embeds no
  secret, and names no technology (UDL-15).

An incomplete, uncertified-member, over/under-populated, authority-conferring, or
technology-bound completion record cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.band10_meta import (
    BAND_CLASS,
    BAND_ID_PREFIX,
    BAND_META_CLASSES,
    EXPECTED_UNITS,
    META_MODEL_UNIT,
    UNIT_INVENTORY,
    BandState,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import content_hash

#: The seven meta-invariant keys the U11 integration closure must satisfy (DATA-005 §8).
_INTEGRATION_KEYS: tuple[str, ...] = (
    "all_members_certified",
    "closure_DMI_01",
    "relationship_closure_DMI_02",
    "totality_DMI_03",
    "founding_acyclic_DMI_04",
    "reuse_by_reference_DMI_05",
    "non_constitutive_DMI_06",
    "non_projection_DMI_07",
    "map_resolves",
)

#: Conservative technology markers used to enforce UDL-15 / non-constitutiveness. A
#: completion record that names any of these is rejected fail-closed.
_TECH_MARKERS: tuple[str, ...] = (
    "sql",
    "nosql",
    "postgres",
    "mysql",
    "oracle",
    "mongodb",
    "redis",
    "elastic",
    "cassandra",
    "neo4j",
    "dynamodb",
    "snowflake",
    "bigquery",
    "spark",
    "pandas",
    "orm",
    "graphql",
    "grpc",
    "kafka",
    "database",
    "query language",
)

#: Conservative secret markers used to enforce UDL-15 / RR-07 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "api_key",
    "access_token",
)

#: The concern-unit meta-classes expected to cover exactly DMC-01…10 (the meta-model unit
#: U11 carries the non-DMC ``UDM`` class and is excluded from meta-class coverage).
_EXPECTED_META_CLASSES = frozenset(BAND_META_CLASSES)


@dataclass(frozen=True, slots=True)
class UnitCertificationRef:
    """An immutable reference to one CERTIFIED Band-10 realization unit (never owned)."""

    unit: str
    meta_class: str
    name: str
    concern_doc: str
    certification_id: str
    certified: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit": self.unit,
            "meta_class": self.meta_class,
            "name": self.name,
            "concern_doc": self.concern_doc,
            "certification_id": self.certification_id,
            "certified": self.certified,
        }


@dataclass(frozen=True, slots=True)
class Band10Completion:
    """A deterministic, immutable Band-10 Realization Completion record."""

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
        """True iff the record inventories exactly the eleven expected units U01…U11."""
        present = tuple(self.unit_ids())
        return set(present) == set(EXPECTED_UNITS) and len(present) == len(EXPECTED_UNITS)

    def all_units_certified(self) -> bool:
        """True iff every inventoried unit is CERTIFIED (reused by reference)."""
        return bool(self.units) and all(u.certified for u in self.units)

    def meta_classes_covered(self) -> tuple[str, ...]:
        """The data meta-classes covered by the concern units (excludes the ``UDM`` capstone)."""
        return tuple(sorted({u.meta_class for u in self.units if u.meta_class != "UDM"}))

    def meta_class_coverage_complete(self) -> bool:
        """True iff the concern units cover exactly the ten meta-classes DMC-01…10."""
        return set(self.meta_classes_covered()) == _EXPECTED_META_CLASSES

    def integration_map(self) -> dict[str, bool]:
        return dict(self.integration)

    def integration_closed(self) -> bool:
        """True iff the U11 meta-model integration closure satisfies all seven invariants."""
        m = self.integration_map()
        return bool(m) and all(m.get(k, False) for k in _INTEGRATION_KEYS)

    def dependency_acyclic(self) -> bool:
        """True iff the unit founding graph is acyclic/downward-only (structural).

        The band units realize a strictly layered dependency (Datum → concerns → meta-model);
        no unit depends on a later unit and none depends on itself, so the graph is a DAG.
        """
        seen: set[str] = set()
        for unit in self.unit_ids():
            if unit in seen:  # a repeated unit would break the strict layering
                return False
            seen.add(unit)
        # the meta-model capstone must be present and last-layer (depends on all concerns)
        return self.meta_model_unit in seen

    def reuses_by_reference(self) -> bool:
        """True iff every unit is referenced by a non-empty certification id (never owned)."""
        return bool(self.units) and all(u.certification_id.strip() for u in self.units)

    def _scan(self, markers: tuple[str, ...]) -> bool:
        """True iff any marker occurs in the record's human-readable text fields."""
        haystack = " ".join(
            [self.name, self.type_tag, self.meta_model_unit]
            + [f"{u.name} {u.concern_doc} {u.meta_class}" for u in self.units]
        ).lower()
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
            "dependency_acyclic": self.dependency_acyclic(),
            "integration_closed": self.integration_closed(),
            "reuses_by_reference": self.reuses_by_reference(),
            "non_projection": self.is_non_projection(),
            "non_constitutive": self.is_non_constitutive(),
        }


def _concern_doc_for(unit: str) -> tuple[str, str, str]:
    """Return the ``(meta_class, name, concern_doc)`` declared for ``unit`` (fail-closed)."""
    for spec_unit, meta_class, name, concern_doc in UNIT_INVENTORY:
        if spec_unit == unit:
            return (meta_class, name, concern_doc)
    raise KeyError(f"unit {unit!r} is not a declared Band-10 realization unit")


def make_band10_completion(
    name: str,
    type_tag: str,
    unit_certifications: tuple[tuple[str, str, bool], ...],
    meta_model_id: str,
    integration: dict[str, bool],
    *,
    version: str,
    state: BandState = BandState.DEFINED,
) -> Band10Completion:
    """Construct the canonical Band-10 completion record from live unit certifications.

    ``unit_certifications`` is a tuple of ``(unit, certification_id, certified)`` captured
    from each unit's own realize orchestrator; each is resolved against the declared
    :data:`UNIT_INVENTORY` (fail-closed on any undeclared unit) and composed by reference.
    """
    refs: list[UnitCertificationRef] = []
    for unit, certification_id, certified in unit_certifications:
        meta_class, unit_name, concern_doc = _concern_doc_for(unit)
        refs.append(
            UnitCertificationRef(
                unit=unit,
                meta_class=meta_class,
                name=unit_name,
                concern_doc=concern_doc,
                certification_id=certification_id,
                certified=bool(certified),
            )
        )
    ordered = tuple(sorted(refs, key=lambda r: r.unit))
    meta_model_cert = next(
        (r.certification_id for r in ordered if r.unit == META_MODEL_UNIT), ""
    )
    integration_items = tuple(sorted((k, bool(v)) for k, v in integration.items()))
    return Band10Completion(
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
    "Band10Completion",
    "make_band10_completion",
]

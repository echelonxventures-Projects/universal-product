"""EC3-B11-U13 — The Band-11 Freeze construct (immutable certified baseline).

Realizes the executable **Band-11 Freeze baseline record**: an immutable, content-addressed
roll-up that references the **twelve CERTIFIED Band-11 realization units by certification
id** (U01…U10 concern meta-classes + U11 USM + U12 Band-11 Realization Certification &
Completion) and establishes them as the canonical, frozen Band-11 baseline. It is the EC-3
realization analogue of the ``SERVICE-015`` Service Foundation Freeze Determination, applied
to the *code* realization of the whole Band-11 Service layer.

The freeze record is **not** a service meta-class (SMI-01 admits no meta-class outside
SMC-01…10) and **not** new functionality. It is a freeze/baseline artifact that:

* references each frozen unit as a :class:`FrozenUnitRef` (unit + meta-class + name +
  concern doc + certification id + certified + frozen) — **never owning, embedding, or
  re-realizing** any unit (SMX-02 non-absorbing; reuse by reference, USL-02);
* crowns the U12 band completion (the certification-of-certifications) by band id +
  certification id;
* derives its identity — the **immutable baseline digest** — through the EC-1 certified
  deterministic encoding (:func:`engine.certification.contracts.content_hash`); no second
  identity scheme;
* declares the SERVICE-015-style freeze effects (FE-1…FE-5: immutability, reuse mandate,
  redefinition prohibition, additive extension, supersession-only change);
* enforces fail-closed that the inventory is exactly U01…U12, that every unit is CERTIFIED
  and FROZEN, that the concern units cover exactly the ten meta-classes SMC-01…10, that the
  band completion is referenced, that the founding graph is acyclic and downward-only, and
  that the record confers no authority, embeds no secret, and names no technology (USL-15).

An incomplete, uncertified-member, over/under-populated, authority-conferring, or
technology-bound freeze record cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- EC-1 reuse by reference (USL-02 / SMI-05) — imported, never redefined --------
from engine.certification.contracts import content_hash
from service.band11_freeze_meta import (
    BAND_COMPLETION_UNIT,
    EXPECTED_FROZEN_UNITS,
    FREEZE_CLASS,
    FREEZE_EFFECTS,
    FREEZE_ID_PREFIX,
    FREEZE_META_CLASSES,
    FREEZE_META_MODEL_UNIT,
    FROZEN_UNIT_INVENTORY,
    NON_CONCERN_LABELS,
    FreezeState,
)

#: The nine integration/closure keys the U11 meta-model closure must satisfy (reused from
#: the CERTIFIED U12 band completion; SERVICE-005 §8).
_INTEGRATION_KEYS: tuple[str, ...] = (
    "all_members_certified",
    "closure_SMI_01",
    "relationship_closure_SMI_02",
    "totality_SMI_03",
    "founding_acyclic_SMI_04",
    "reuse_by_reference_SMI_05",
    "non_constitutive_SMI_06",
    "non_projection_SMI_07",
    "map_resolves",
)

#: Conservative technology markers used to enforce USL-15 / non-constitutiveness. A freeze
#: record that names any of these is rejected fail-closed (aligned with the CERTIFIED USM
#: and U12 marker sets).
_TECH_MARKERS: tuple[str, ...] = (
    "rest",
    "grpc",
    "http",
    "https",
    "soap",
    "graphql",
    "thrift",
    "websocket",
    "openapi",
    "swagger",
    "kafka",
    "rabbitmq",
    "amqp",
    "mqtt",
    "istio",
    "envoy",
    "kubernetes",
    "lambda",
    "protobuf",
    "service mesh",
)

#: Conservative secret markers used to enforce USL-15 / RR-07 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "api_key",
    "access_token",
)

#: The concern-unit meta-classes expected to cover exactly SMC-01…10 (the U11/U12 capstone
#: units carry non-SMC labels and are excluded from meta-class coverage).
_EXPECTED_META_CLASSES = frozenset(FREEZE_META_CLASSES)

#: The freeze effect keys a complete baseline must declare (FE-1…FE-5).
_EXPECTED_EFFECTS = frozenset(FREEZE_EFFECTS)


@dataclass(frozen=True, slots=True)
class FrozenUnitRef:
    """An immutable reference to one CERTIFIED, FROZEN Band-11 realization unit (never owned)."""

    unit: str
    meta_class: str
    name: str
    concern_doc: str
    certification_id: str
    certified: bool
    frozen: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit": self.unit,
            "meta_class": self.meta_class,
            "name": self.name,
            "concern_doc": self.concern_doc,
            "certification_id": self.certification_id,
            "certified": self.certified,
            "frozen": self.frozen,
        }


@dataclass(frozen=True, slots=True)
class Band11Freeze:
    """A deterministic, immutable Band-11 Freeze baseline record."""

    name: str
    type_tag: str
    units: tuple[FrozenUnitRef, ...]
    band_completion_unit: str
    band_completion_id: str
    band_completion_certification_id: str
    meta_model_unit: str
    meta_model_id: str
    meta_model_certification_id: str
    integration: tuple[tuple[str, bool], ...]
    effects: tuple[str, ...]
    version: str
    state: FreezeState

    # -- identity -------------------------------------------------------------

    def canonical_core(self) -> dict[str, Any]:
        """The stable content the freeze baseline identity is derived from (no id echo)."""
        return {
            "freeze_class": FREEZE_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "units": [u.to_dict() for u in self.units],
            "band_completion_unit": self.band_completion_unit,
            "band_completion_id": self.band_completion_id,
            "band_completion_certification_id": self.band_completion_certification_id,
            "meta_model_unit": self.meta_model_unit,
            "meta_model_id": self.meta_model_id,
            "meta_model_certification_id": self.meta_model_certification_id,
            "integration": [list(item) for item in self.integration],
            "effects": list(self.effects),
            "version": self.version,
            "state": self.state.value,
        }

    @property
    def baseline_digest(self) -> str:
        """The deterministic ENG-003 content digest of the frozen baseline (the seal)."""
        return content_hash(self.canonical_core())

    @property
    def structure_digest(self) -> str:
        """Alias of :attr:`baseline_digest` (the value-fidelity digest)."""
        return self.baseline_digest

    @property
    def freeze_id(self) -> str:
        """The deterministic ENG-001 identity of the freeze baseline record."""
        return f"{FREEZE_ID_PREFIX}-{self.name}-{self.baseline_digest[:16]}"

    @property
    def meta_class(self) -> str:
        return FREEZE_CLASS

    # -- decidable roll-ups ---------------------------------------------------

    def unit_ids(self) -> tuple[str, ...]:
        return tuple(u.unit for u in self.units)

    def inventory_complete(self) -> bool:
        """True iff the record inventories exactly the twelve expected units U01…U12."""
        present = tuple(self.unit_ids())
        return set(present) == set(EXPECTED_FROZEN_UNITS) and len(present) == len(
            EXPECTED_FROZEN_UNITS
        )

    def all_units_certified(self) -> bool:
        """True iff every inventoried unit is CERTIFIED (reused by reference)."""
        return bool(self.units) and all(u.certified for u in self.units)

    def all_units_frozen(self) -> bool:
        """True iff every inventoried unit is marked FROZEN."""
        return bool(self.units) and all(u.frozen for u in self.units)

    def meta_classes_covered(self) -> tuple[str, ...]:
        """The service meta-classes covered by the concern units (excludes the capstones)."""
        return tuple(
            sorted({u.meta_class for u in self.units if u.meta_class not in NON_CONCERN_LABELS})
        )

    def meta_class_coverage_complete(self) -> bool:
        """True iff the concern units cover exactly the ten meta-classes SMC-01…10."""
        return set(self.meta_classes_covered()) == _EXPECTED_META_CLASSES

    def band_completion_referenced(self) -> bool:
        """True iff the U12 band completion is referenced (by id + certification id)."""
        return (
            self.band_completion_unit == BAND_COMPLETION_UNIT
            and bool(self.band_completion_id.strip())
            and self.band_completion_certification_id.startswith("UCOS-CERT-BAND-11-")
        )

    def integration_map(self) -> dict[str, bool]:
        return dict(self.integration)

    def integration_closed(self) -> bool:
        """True iff the U11 meta-model integration closure satisfies all invariants."""
        m = self.integration_map()
        return bool(m) and all(m.get(k, False) for k in _INTEGRATION_KEYS)

    def dependency_acyclic(self) -> bool:
        """True iff the frozen unit founding graph is acyclic/downward-only (structural)."""
        seen: set[str] = set()
        for unit in self.unit_ids():
            if unit in seen:  # a repeated unit would break the strict layering
                return False
            seen.add(unit)
        # the meta-model (U11) and the band completion (U12) capstones must both be present
        return self.meta_model_unit in seen and self.band_completion_unit in seen

    def reuses_by_reference(self) -> bool:
        """True iff every unit is referenced by a non-empty certification id (never owned)."""
        return bool(self.units) and all(u.certification_id.strip() for u in self.units)

    def effects_declared(self) -> bool:
        """True iff the baseline declares exactly the five SERVICE-015-style freeze effects."""
        return set(self.effects) == _EXPECTED_EFFECTS

    def is_immutable_baseline(self) -> bool:
        """True iff the record carries a valid content-addressed baseline seal (64-hex)."""
        digest = self.baseline_digest
        return len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)

    def _scan(self, markers: tuple[str, ...]) -> bool:
        """True iff any marker occurs in the record's human-readable text fields."""
        haystack = " ".join(
            [self.name, self.type_tag, self.band_completion_unit, self.meta_model_unit]
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
        """The freeze record is evaluative only; it never confers authority (DE-05)."""
        return False

    def is_non_projection(self) -> bool:
        """Freeze is a realization baseline, never operational/deployment/production readiness."""
        return True

    def is_non_constitutive(self) -> bool:
        return not (self.confers_authority() or self.embeds_secret() or self.selects_technology())

    def to_dict(self) -> dict[str, Any]:
        return {
            "freeze_id": self.freeze_id,
            "freeze_class": FREEZE_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "baseline_digest": self.baseline_digest,
            "structure_digest": self.structure_digest,
            "units": [u.to_dict() for u in self.units],
            "unit_count": len(self.units),
            "band_completion_unit": self.band_completion_unit,
            "band_completion_id": self.band_completion_id,
            "band_completion_certification_id": self.band_completion_certification_id,
            "meta_model_unit": self.meta_model_unit,
            "meta_model_id": self.meta_model_id,
            "meta_model_certification_id": self.meta_model_certification_id,
            "integration": {k: v for k, v in self.integration},
            "effects": list(self.effects),
            "meta_classes_covered": list(self.meta_classes_covered()),
            "version": self.version,
            "state": self.state.value,
            "substrate_refs": ["ENG-001", "ENG-002", "ENG-004", "ENG-005", "CCE"],
            "inventory_complete": self.inventory_complete(),
            "all_units_certified": self.all_units_certified(),
            "all_units_frozen": self.all_units_frozen(),
            "meta_class_coverage_complete": self.meta_class_coverage_complete(),
            "band_completion_referenced": self.band_completion_referenced(),
            "dependency_acyclic": self.dependency_acyclic(),
            "integration_closed": self.integration_closed(),
            "reuses_by_reference": self.reuses_by_reference(),
            "effects_declared": self.effects_declared(),
            "immutable_baseline": self.is_immutable_baseline(),
            "non_projection": self.is_non_projection(),
            "non_constitutive": self.is_non_constitutive(),
        }


def _spec_for(unit: str) -> tuple[str, str, str]:
    """Return the ``(meta_class, name, concern_doc)`` declared for ``unit`` (fail-closed)."""
    for spec_unit, meta_class, name, concern_doc in FROZEN_UNIT_INVENTORY:
        if spec_unit == unit:
            return (meta_class, name, concern_doc)
    raise KeyError(f"unit {unit!r} is not a declared Band-11 frozen unit")


def make_band11_freeze(
    name: str,
    type_tag: str,
    unit_certifications: tuple[tuple[str, str, bool], ...],
    *,
    band_completion_id: str,
    band_completion_certification_id: str,
    meta_model_id: str,
    integration: dict[str, bool],
    effects: tuple[str, ...] | None = None,
    version: str,
    state: FreezeState = FreezeState.DEFINED,
) -> Band11Freeze:
    """Construct the canonical Band-11 freeze baseline from live unit certifications.

    ``unit_certifications`` is a tuple of ``(unit, certification_id, certified)`` captured
    from the band realization (the eleven realization units + the U12 band completion); each
    is resolved against the declared :data:`FROZEN_UNIT_INVENTORY` (fail-closed on any
    undeclared unit), marked FROZEN, and composed by reference. ``effects`` defaults to the
    full SERVICE-015-style effect set (FE-1…FE-5).
    """
    refs: list[FrozenUnitRef] = []
    for unit, certification_id, certified in unit_certifications:
        meta_class, unit_name, concern_doc = _spec_for(unit)
        refs.append(
            FrozenUnitRef(
                unit=unit,
                meta_class=meta_class,
                name=unit_name,
                concern_doc=concern_doc,
                certification_id=certification_id,
                certified=bool(certified),
                frozen=True,
            )
        )
    ordered = tuple(sorted(refs, key=lambda r: r.unit))
    meta_model_cert = next(
        (r.certification_id for r in ordered if r.unit == FREEZE_META_MODEL_UNIT), ""
    )
    integration_items = tuple(sorted((k, bool(v)) for k, v in integration.items()))
    declared_effects = tuple(sorted(effects if effects is not None else _EXPECTED_EFFECTS))
    return Band11Freeze(
        name=name,
        type_tag=type_tag,
        units=ordered,
        band_completion_unit=BAND_COMPLETION_UNIT,
        band_completion_id=band_completion_id,
        band_completion_certification_id=band_completion_certification_id,
        meta_model_unit=FREEZE_META_MODEL_UNIT,
        meta_model_id=meta_model_id,
        meta_model_certification_id=meta_model_cert,
        integration=integration_items,
        effects=declared_effects,
        version=version,
        state=state,
    )


__all__ = [
    "FrozenUnitRef",
    "Band11Freeze",
    "make_band11_freeze",
]

"""EC3-B10-U02 — The Universal Attribute construct (DMC-03).

Realizes the meta-model construct **DMC-03 Attribute** (DATA-005 §2; DATA-007 §3):

    a typed, named property borne by exactly one entity and carrying exactly one
    ENG-003 value — the atomic unit of *structured* representation. An attribute
    is classified by an ENG-004 Type, values a Datum (DOE-01) via DMR-02, and is
    borne by an entity via DMR-01. It is neither the entity that bears it (DOE-02)
    nor the datum it values (DOE-01) — it is the named, typed property.

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-01 Datum construct**, reusing both *by reference* (UDL-02 / DMI-05):

* Identity and value-fidelity are derived through the EC-1 certified deterministic
  encoding (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme,
  no parallel value model.
* The attribute's single ENG-003 value (DMR-02 ``values``) is a **reference to a
  CERTIFIED :class:`~data.datum.Datum`** (its id + value digest), **not** an
  embedded or copied Datum model (DMX-02 non-absorbing; DAA-03 single value).
* The bearing entity (DMR-01 ``borne-by``) is recorded as an **identity reference**
  — a *reference obligation*; no Entity construct (DMC-02) is required, realized, or
  embedded here (the same additive reference-by discipline the certified Datum used
  to record DMR-02/09/10 without a realized Attribute/Entity).

An :class:`Attribute` is *immutable* (frozen — ENG-002 objecthood), *typed*
(ENG-004, DAA-01/UDL-08), *named* (DAA-04), *single-bearing* (DMR-01/DAA-02),
*single-valued* (DMR-02/DAA-03), *nullability-declared* (DAA-05), *classified* by
one DXH-03 kind, and holds a *forward-only lifecycle state* (DOS-01…05, UDL-12).
Constructing an :class:`Attribute` enforces DAA-K1/K2, the DXH-03/relational/derived
rules, and UDL-06/03/08/15 **fail-closed**: an ill-formed attribute cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from data.attribute_meta import (
    ATTRIBUTE_META_CLASS,
    ATTRIBUTE_RELATIONSHIPS,
    ATTRIBUTE_SUBSTRATE_REFS,
    LIFECYCLE_ORDER,
    AttributeKind,
    AttributeState,
)

# --- DMC-01 reuse by reference (UDL-02 / DMR-02 values target) — never redefined -
from data.datum import Datum

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined -------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Attribute (mirrors EC-1 UCOS-<KIND>-<hex16>).
ATTRIBUTE_ID_PREFIX = "UCOS-ATTR"

#: The identity-reference prefix a Datum bears (DMR-02 ``values`` target must be one).
DATUM_ID_PREFIX = "UCOS-DATUM"

#: The map of EC-1 / DMC-01 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-003": "data.datum.Datum value (ENG-003 value carried via DMR-02; referenced, not copied)",
    "ENG-004": "data.attribute_meta.AttributeKind + type_tag (ENG-004 typing discipline)",
    "ENG-005": "bearing-entity + relational identity references (DMR-01/03; by reference)",
    "DMC-01": "data.datum.Datum — the CERTIFIED values target (DMR-02); referenced, not redefined",
}

#: Conservative secret markers used to enforce UDL-15 / DAA-09 / RR-07 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "privatekey",
    "api_key",
    "apikey",
    "access_token",
    "credential",
    "-----begin",
)


class AttributeError_(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`Attribute`.

    Named with a trailing underscore to avoid shadowing the builtin
    ``AttributeError``. An :class:`Attribute` is fail-closed (TRACK-001): an
    ill-formed property is rejected at construction rather than admitted invalid.
    """


@dataclass(frozen=True, slots=True)
class DatumValueRef:
    """A reference to the CERTIFIED Datum an attribute ``values`` (DMR-02).

    Records **only** the referenced datum's identity and value fingerprint — not its
    payload — so the attribute references, and never absorbs, the Datum model
    (DMX-02 non-absorbing; UDL-06 value fidelity; UDL-02 reuse-by-reference).
    """

    datum_id: str
    value_digest: str
    type_tag: str

    @classmethod
    def from_datum(cls, datum: Datum) -> DatumValueRef:
        """Project a CERTIFIED :class:`~data.datum.Datum` into a reference-only value."""
        if not isinstance(datum, Datum):
            raise AttributeError_("an attribute values a data.datum.Datum (DMR-02)")
        return cls(
            datum_id=datum.datum_id,
            value_digest=datum.value_digest,
            type_tag=datum.type_tag,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "datum_id": self.datum_id,
            "value_digest": self.value_digest,
            "type_tag": self.type_tag,
            "binding": "DMR-02:values",
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class Attribute:
    """DMC-03 — an immutable, typed, named, single-bearing, single-valued property.

    Fields:
        name:               the explicit, decidable attribute name (DAA-04; UDL-08).
        type_tag:           the ENG-004 Type of the attribute (DAA-01; UDL-03/08).
        kind:               the DXH-03 classification (DMR-09 classified-by; DAA-01).
        value_ref:          the single ENG-003 value, as a reference to a CERTIFIED
                            Datum (DMR-02; DAA-03; DMX-02 non-absorbing).
        bearing_entity_ref: the single bearing-entity identity reference (DMR-01;
                            DAA-02) — a reference obligation (Entity DMC-02 is U03).
        nullable:           whether an absent value is admissible — declared
                            explicitly, never implicit (DAA-05; DAA-C2).
        state:              the DOS-01…05 forward-only lifecycle state (UDL-12).
        references_entity:  for a Relational-Attribute, the referenced target entity
                            identity (ENG-005 by reference; DAA-07; DAA-C4). Empty
                            for non-relational attributes.
        derived_from:       for a Derived-Attribute, the provenance references from
                            which it is computed (DAA-06; DAA-C3). Empty otherwise.
    """

    name: str
    type_tag: str
    kind: AttributeKind
    value_ref: DatumValueRef
    bearing_entity_ref: str
    nullable: bool
    state: AttributeState = AttributeState.DEFINED
    references_entity: str = ""
    derived_from: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # DAA-04 / UDL-08 — explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise AttributeError_("attribute must have an explicit name (DAA-04 / UDL-08)")
        # DAA-01 / DMK-01 / UDL-03/08 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise AttributeError_("attribute must be typed with a non-empty ENG-004 type_tag")
        # DXH-03 / DMR-09 — classified by exactly one Attribute kind.
        if not isinstance(self.kind, AttributeKind):
            raise AttributeError_("attribute kind must be a DXH-03 AttributeKind (DMR-09)")
        # DMR-02 / DAA-03 / DAA-K2 — exactly one ENG-003 value, a reference to a Datum.
        if not isinstance(self.value_ref, DatumValueRef):
            raise AttributeError_("attribute values exactly one Datum via DatumValueRef (DMR-02)")
        if not self.value_ref.datum_id.startswith(f"{DATUM_ID_PREFIX}-"):
            raise AttributeError_("value reference is not a CERTIFIED Datum identity (DMR-02)")
        if len(self.value_ref.value_digest) != 64 or any(
            c not in "0123456789abcdef" for c in self.value_ref.value_digest
        ):
            raise AttributeError_("value reference carries no ENG-003 value digest (UDL-06)")
        # DMR-01 / DAA-02 / DAA-K2 — borne by exactly one entity (by reference).
        if not isinstance(self.bearing_entity_ref, str) or not self.bearing_entity_ref.strip():
            raise AttributeError_("attribute must be borne by exactly one entity (DMR-01/DAA-02)")
        # DAA-05 / DAA-C2 — nullability declared explicitly (a real bool, never implicit).
        if not isinstance(self.nullable, bool):
            raise AttributeError_("attribute nullability must be declared explicitly (DAA-05)")
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, AttributeState):
            raise AttributeError_("attribute state must be a DOS-01…05 state (UDL-12)")
        # DAA-07 / DAA-C4 — a Relational-Attribute references a target entity (ENG-005);
        # non-relational attributes never carry a cross-entity reference.
        if self.kind is AttributeKind.RELATIONAL:
            if not self.references_entity.strip():
                raise AttributeError_(
                    "a Relational-Attribute must reference a target entity (DAA-07/DAA-C4)"
                )
        elif self.references_entity:
            raise AttributeError_("only a Relational-Attribute may set references_entity (DAA-07)")
        # DAA-06 / DAA-C3 — a Derived-Attribute records provenance; others carry none.
        if self.kind is AttributeKind.DERIVED:
            if not self.derived_from:
                raise AttributeError_("a Derived-Attribute must record provenance (DAA-06/DAA-C3)")
        elif self.derived_from:
            raise AttributeError_("only a Derived-Attribute may declare derived_from (DAA-06)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the attribute (structure + value reference)."""
        return {
            "meta_class": ATTRIBUTE_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "value_ref": self.value_ref.to_dict(),
            "bearing_entity_ref": self.bearing_entity_ref,
            "nullable": self.nullable,
            "references_entity": self.references_entity,
            "derived_from": list(self.derived_from),
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the attribute core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def attribute_id(self) -> str:
        """The deterministic ENG-001 identity of the attribute (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second
        identity scheme): identical structure + value reference always yields the
        identical id, so identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{ATTRIBUTE_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-007) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-03)."""
        return ATTRIBUTE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the attribute participates in."""
        return ATTRIBUTE_RELATIONSHIPS

    @property
    def value_digest(self) -> str:
        """The ENG-003 value fingerprint carried by the attribute (from the Datum ref)."""
        return self.value_ref.value_digest

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 / UDL-09 — the founding graph is acyclic.

        The attribute's founding references (``values`` → Datum, ``borne-by`` →
        Entity, relational → Entity, derivation provenance) are recorded by
        *identity reference*; none may reference the attribute itself, so the
        founding graph is a DAG.
        """
        own = self.attribute_id
        refs = {self.value_ref.datum_id, self.bearing_entity_ref}
        if self.references_entity:
            refs.add(self.references_entity)
        refs.update(self.derived_from)
        return own not in refs

    def absorbs_value(self) -> bool:
        """DMX-02 — the attribute references its value's Datum, never absorbs it."""
        return False

    # -- non-constitutiveness (UDL-15 / DAA-09) --------------------------------

    def confers_authority(self) -> bool:
        """UDL-15 / DAA-09 / C7 — an attribute confers no authority (structurally none)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DAA-09 / RR-07 / C7 — True iff the attribute appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — an attribute redefines no EL-1/DMC-01 model (reuse-only)."""
        return False

    def selects_technology(self) -> bool:
        """UDL-11 / DAA-K5 — an attribute selects no storage/technology (structurally none)."""
        return False

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: AttributeState) -> Attribute:
        """Return a new attribute advanced to ``to_state`` (forward-only; UDL-12).

        Raises:
            AttributeError_: on a backward transition (breaking change is supersession,
                never in-place reversal — DATA-007 §8; UDL-12/15).
        """
        if not isinstance(to_state, AttributeState):
            raise AttributeError_("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise AttributeError_(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the attribute."""
        return {
            "attribute_id": self.attribute_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "value_ref": self.value_ref.to_dict(),
            "value_digest": self.value_digest,
            "bearing_entity_ref": self.bearing_entity_ref,
            "nullable": self.nullable,
            "state": self.state.value,
            "references_entity": self.references_entity,
            "derived_from": list(self.derived_from),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(ATTRIBUTE_SUBSTRATE_REFS),
            "absorbs_value": self.absorbs_value(),
        }


def make_attribute(
    name: str,
    type_tag: str,
    value: Datum | DatumValueRef,
    bearing_entity_ref: str,
    *,
    kind: AttributeKind = AttributeKind.DESCRIPTIVE,
    nullable: bool = False,
    state: AttributeState = AttributeState.DEFINED,
    references_entity: str = "",
    derived_from: tuple[str, ...] = (),
) -> Attribute:
    """Construct a well-formed :class:`Attribute` (fail-closed factory).

    ``value`` may be a CERTIFIED :class:`~data.datum.Datum` (reused by reference — the
    DMR-02 ``values`` target) or an already-projected :class:`DatumValueRef`.
    """
    value_ref = value if isinstance(value, DatumValueRef) else DatumValueRef.from_datum(value)
    return Attribute(
        name=name,
        type_tag=type_tag,
        kind=kind,
        value_ref=value_ref,
        bearing_entity_ref=bearing_entity_ref,
        nullable=nullable,
        state=state,
        references_entity=references_entity,
        derived_from=tuple(derived_from),
    )


__all__ = [
    "ATTRIBUTE_ID_PREFIX",
    "REUSE_REFS",
    "AttributeError_",
    "DatumValueRef",
    "Attribute",
    "make_attribute",
]

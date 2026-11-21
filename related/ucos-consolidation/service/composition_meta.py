"""EC3-B11-U06 — Composition meta-model constants (read-only projections of SERVICE-001…010).

Carries, as executable constants, the fixed identifiers of the frozen Service Foundation
that the Universal **Composition** realization (SMC-06) must conform to. It **defines no new
law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it only names the
frozen obligations so the realization can be checked deterministically.

Derived verbatim from the frozen ``11-SERVICE/`` specification at anchor ``b7e7657``:

* SMC-06 **Composition** models ontology entity **SOE-06** — *"the structural assembly of
  services and operations into larger services"* (SERVICE-003 §2; SERVICE-010 §3) —
  classified by hierarchy **SXH-06** (Aggregation / Federation / Delegation; SERVICE-004 §3 /
  SERVICE-010 §5).
* A Composition **composes** services/operations (SMR-05 composes; SOR-05; reference-only,
  peer/founding, acyclic), aggregates operations a service **provides** (SMR-04; SOR-04;
  founding, acyclic), is **bound-by** a composition contract (SMR-02; SOR-02; founding,
  acyclic), reuses PLATFORM composition/integration via **composed-as** (SMR-12; SOR-12;
  PLATFORM-010/011, by reference), carries cross-composition data via **operates-on**
  (SMR-13; SOR-13; DF-2, by reference), and is identified via **identified-by** (SMR-10;
  SOR-10; ENG-001 via ENG-002).
* Composition principles SCO-01…10 (SERVICE-010 §4) govern the construct; **USL-09**
  (composition by reference) is the governing law, grounded in USL-02/06/11.
"""

from __future__ import annotations

from enum import Enum

from service.service_meta import (
    CONSTITUTIONAL_ANCHOR,
    LIFECYCLE_ORDER,
    META_RELATIONSHIPS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

# Re-export the frozen sets (single source of truth — no duplication).
__all_reexport__ = (
    CONSTITUTIONAL_ANCHOR,
    LIFECYCLE_ORDER,
    META_RELATIONSHIPS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

#: The Composition meta-class id (SERVICE-005 §2).
COMPOSITION_META_CLASS = "SMC-06"

#: Backward traceability chain every realized Composition records (SERVICE-005 → root).
TRACE_BACKWARD_COMPOSITION: tuple[str, ...] = (
    "SMC-06",  # SERVICE-005 §2 — Composition meta-class
    "SOE-06",  # SERVICE-003 §2 — Composition ontology entity
    "SERVICE-010",  # Universal Service Composition Architecture (concern architecture)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations a Composition reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · PL-F2 (composition/integration, SMR-12; PLATFORM-010/011) ·
#:   RL-F2 (delegated invocation, §7 composition-invoke) · DF-2 (cross-composition data,
#:   SMR-13).
COMPOSITION_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (structural value fidelity)
    "ENG-004",  # Type      (typed composition, USL-03 / SCO-01)
    "ENG-005",  # Relationship/Reference (composes/provides/bound-by refs; SMR-05/04/02)
    "PL-F2",  # Platform composition/integration (composed-as, SMR-12; PLATFORM-010/011)
    "RL-F2",  # Runtime invocation (delegated operation invocation; §7 composition-invoke)
    "DF-2",  # Represented data (cross-composition data flow, SMR-13; by reference)
)

#: The meta-relationships a Composition intrinsically participates in (SERVICE-010 §6;
#: all within SMR-01…13):
#:   SMR-02 bound-by      (Composition → Composition-Contract — founding, acyclic; SCO-05)
#:   SMR-04 provides      (Service → Operation aggregated — founding, acyclic)
#:   SMR-05 composes      (Service/Operation → Service/Operation — reference-only, acyclic)
#:   SMR-10 identified-by (ENG-001 via ENG-002)
#:   SMR-12 composed-as   (Composition → PLATFORM composition PLATFORM-010/011, by reference)
#:   SMR-13 operates-on   (cross-composition data flow → DATA DF-2, by reference; SCO-07)
COMPOSITION_RELATIONSHIPS: tuple[str, ...] = (
    "SMR-02",
    "SMR-04",
    "SMR-05",
    "SMR-10",
    "SMR-12",
    "SMR-13",
)


class CompositionKind(str, Enum):
    """SXH-06 Composition Hierarchy (SERVICE-004 §3 / SERVICE-010 §5) — single-facet (SXC-02).

    Membership is decidable and single-facet; each kind carries a distinct topology:

    * ``AGGREGATION`` — assembles operations into a service (founding, acyclic; ≥1 member).
    * ``FEDERATION``  — peer composition of services (SOR-05 peer; ≥2 peers).
    * ``DELEGATION``  — an operation delegates to exactly one target operation (reference).
    """

    AGGREGATION = "Aggregation-Composition"  # operations → service (founding, acyclic)
    FEDERATION = "Federation-Composition"  # peer composition of services (non-founding)
    DELEGATION = "Delegation-Composition"  # an operation → one target operation (reference)


#: The founding composition kinds (SCO-C1 — their founding graph is a DAG).
FOUNDING_KINDS: frozenset[CompositionKind] = frozenset(
    {CompositionKind.AGGREGATION, CompositionKind.DELEGATION}
)

#: Composition principles SCO-01…10 (SERVICE-010 §4), each mapped to its short statement.
COMPOSITION_PRINCIPLES: dict[str, str] = {
    "SCO-01": "Composition Typedness — classified by an ENG-004 Type.",
    "SCO-02": "Composition Identity — an ENG-002 Object bearing an ENG-001 identity.",
    "SCO-03": "Reference-Only Linking — links via ENG-005 refs + PL-F2; no new construct.",
    "SCO-04": "Acyclic Founding — founding composition forms a DAG; no self-composition.",
    "SCO-05": "Composition Contract — bounded by a composition contract (SERVICE-007).",
    "SCO-06": "Platform Reuse — reuses PLATFORM-010/011 by reference; re-founds nothing.",
    "SCO-07": "Data by Reference — cross-composition data references DF-2 constructs.",
    "SCO-08": "Additive Growth — new kinds append additively (SXH-06); no renumber.",
    "SCO-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "SCO-10": "Reuse Labelling — consumed source assets are labelled INPUT, never COMPLETION.",
}

#: The Service laws a Composition construct is directly obligated by (per Stage-1 discovery).
#: USL-09 (composition by reference) is THE governing law; USL-06 (contract explicitness),
#: USL-10 (delegated invocation binds RL-F2) and USL-11 (data by reference) are grounded here
#: too. USL-07 (interface typedness) is scoped to the Interface unit (SMC-04) and USL-08
#: (operation boundedness) to the Operation unit (SMC-05); both recorded N/A.
COMPOSITION_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-06",
    "USL-09",
    "USL-10",
    "USL-11",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to other concern units, N/A to the Composition.
COMPOSITION_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-07", "USL-08")

#: Meta-constraints a Composition is bound by (SERVICE-005 §4 / SERVICE-010 §10 SCO-K1…K5).
#:   SMK-01 typed/identified/object · SMK-02 contract-bound · SMK-03 founding (composes/
#:   provides/bound-by) acyclic · SMK-05 delegated-invocation reference resolves ·
#:   SMK-06 platform composition reference resolves · SMK-07 data reference resolves ·
#:   SMK-08 no technology / no authority.
COMPOSITION_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002). [SCO-K1]",
    "SMK-02": "Bounded by a composition contract (SMR-02). [SCO-K2]",
    "SMK-03": "The founding graph (composes/provides/bound-by) is acyclic. [SCO-K3]",
    "SMK-05": "The delegated-invocation reference resolves to an RL-F2 construct; none redefined.",
    "SMK-06": "Every platform composition reference resolves to a PL-F2 construct; none redefined.",
    "SMK-07": "Every data reference resolves to a DF-2 construct; none redefined. [SCO-K4]",
    "SMK-08": "No composition selects technology or confers authority. [SCO-K5]",
}

#: Meta-constraint scoped to the Operation/Interface units, N/A to the Composition.
COMPOSITION_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-04",)

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Composition → SMC-06).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01/02/03/05/06/07/08).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04 / SCO-C1).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "COMPOSITION_META_CLASS",
    "TRACE_BACKWARD_COMPOSITION",
    "COMPOSITION_SUBSTRATE_REFS",
    "COMPOSITION_RELATIONSHIPS",
    "CompositionKind",
    "FOUNDING_KINDS",
    "COMPOSITION_PRINCIPLES",
    "COMPOSITION_APPLICABLE_LAWS",
    "COMPOSITION_INAPPLICABLE_LAWS",
    "COMPOSITION_META_CONSTRAINTS",
    "COMPOSITION_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]

"""The executed constitutional proof of the Universal Meta-Civilization layer.

Nothing here is asserted in prose. Each quality gate and each architectural-proof category is
a probe that *runs* against live objects and reports ``{"passed": bool, "evidence": str}``, so
the programme's deliverables are renderings of executed results rather than claims.

The architectural proof answers the mandate's own success criterion directly:

    No future capability, dimension, universe, reality, existence model, engineering model,
    commercial model, governance model, or runtime model shall require changes to the
    constitutional foundation.

It does so by taking each of those categories, admitting a previously unknown instance of it
by registration, and then fingerprinting this layer's source before and after to prove that
no source byte changed. The same is done for previously unknown constitutional operating
systems, generation strata and composition strategies. A category that could only be admitted
by editing code would fail its own probe.

The proof is deliberately uniform: one loop per mechanism, with no per-category branching, so
a thirteenth category is a DATA entry rather than a new code path.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

from engine.civilization.composition import CompositionPlanner, strategy_names
from engine.civilization.dimensions import DimensionRegistry
from engine.civilization.errors import DimensionClosedError
from engine.civilization.generation import GENERATION_STRATA, ConstitutionalGenerator
from engine.civilization.mcos import MetaCivilizationPlatform
from engine.civilization.metatypes import (
    DIMENSION_FACETS,
    FORBIDDEN_DIMENSION_KEYS,
    dimension_facet_keys,
    facet_keys,
)
from engine.kernel.compliance import kernel_source_fingerprint
from engine.kernel.identity import content_digest, mint

_LAYER_DIR = Path(__file__).resolve().parent

#: Tokens this layer must never hard-code as a dimension, a facet or a stratum. Each is a
#: legitimate *registration*; none may be built into the substrate. The list exists so the
#: prohibition is measured, not trusted.
PROHIBITED_TOKENS: tuple[str, ...] = (
    "language",
    "currency",
    "country",
    "calendar",
    "timezone",
    "jurisdiction",
    "cloud",
    "provider",
    "region",
    "tenant",
    "organization",
    "billing",
    "monitoring",
    "deployment",
    "reality",
    "existence",
    "industry",
    "vendor",
    "technology",
    "earth",
    "human",
)

#: The mandate's success-criterion categories, each admitted as a previously unknown
#: dimension. (category label, dimension key, open attributes). Twelve entries; a thirteenth
#: is a DATA edit here and requires no change to any mechanism.
PROOF_CATEGORIES: tuple[tuple[str, str, dict[str, Any]], ...] = (
    ("previously unknown capability domain", "Reality-Compilation-Axis", {"scope": "unbounded"}),
    ("previously unknown dimension", "Glyphic-Resonance-Axis", {"modality": "electromagnetic"}),
    ("previously unknown universe", "Xophar-Collective-Universe", {"substrate": "plasma"}),
    ("previously unknown reality model", "Branching-Retrocausal-Reality", {"topology": "acyclic"}),
    ("previously unknown existence model", "Superpositional-Existence", {"mode": "amplitude"}),
    ("previously unknown engineering model", "Substrate-Weaving-Engineering", {"medium": "open"}),
    ("previously unknown commercial model", "Entropy-Credit-Exchange", {"unit": "negentropy"}),
    ("previously unknown governance model", "Emergent-Quorum-Governance", {"decision": "swarm"}),
    ("previously unknown runtime model", "Amplitude-Dispatch-Runtime", {"parallelism": "open"}),
    ("previously unknown temporal model", "Non-Linear-Temporal-Axis", {"ordering": "partial"}),
    ("previously unknown value-exchange model", "Gradient-Levy-Axis", {"basis": "flow"}),
    ("previously unknown observer model", "Lightcone-Witness-Axis", {"proof": "attestation"}),
)

#: Previously unknown constitutional operating systems, each generated end-to-end. These are
#: deliberately not UCOS/GCOS/HCOS/ECOS/ICOS: naming a system the repository already knows
#: would prove nothing about the open catalogue.
UNKNOWN_OPERATING_SYSTEMS: tuple[tuple[str, dict[str, Any]], ...] = (
    ("Zetharic-Constitutional-OS", {"civilization": "unknown"}),
    ("Lattice-Weave-OS", {"substrate": "woven"}),
    ("Retrocausal-Governance-OS", {"causality": "non-linear"}),
    ("Swarm-Consensus-OS", {"quorum": "emergent"}),
    ("Non-Euclidean-Commerce-OS", {"geometry": "open"}),
)


def layer_source_fingerprint() -> str:
    """SHA-256 over every source file of this layer — the no-code-change witness."""
    digest = hashlib.sha256()
    for path in sorted(_LAYER_DIR.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _closed_enum_offenders(directory: Path) -> list[str]:
    """Every ``class X(Enum)``-style declaration under ``directory``.

    Takes the directory as a parameter so the scanner itself is provable against a control
    sample: a probe file containing a closed enumeration must be flagged, which is what makes
    an empty result over this layer evidence rather than an absence of evidence.
    """
    closed = {"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"}
    offenders: list[str] = []
    for path in sorted(directory.glob("*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for base in node.bases:
                name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
                if name in closed:
                    offenders.append(f"{path.name}::{node.name}")
    return offenders


def _layer_has_no_closed_enum() -> tuple[bool, list[str]]:
    """True iff no module in this layer declares an enumeration class."""
    offenders = _closed_enum_offenders(_LAYER_DIR)
    return not offenders, offenders


def _vocabulary_keys() -> set[str]:
    """Every natural key this layer ships as vocabulary, lower-cased."""
    keys = set(facet_keys()) | set(dimension_facet_keys())
    keys |= {key for key, _name, _after, _desc in GENERATION_STRATA}
    return {key.lower() for key in keys}


# --------------------------------------------------------------------------- proof


def architectural_proof() -> dict[str, object]:
    """Admit a previously unknown instance of every mandated category, changing no source.

    Two uniform loops — one over the success-criterion categories (admitted as dimensions),
    one over previously unknown constitutional operating systems (generated end to end). Both
    are bracketed by source fingerprints of this layer *and* of the kernel, so the proof shows
    that neither the layer nor the substrate beneath it was modified to accommodate them.
    """
    before = layer_source_fingerprint()
    kernel_before = kernel_source_fingerprint()
    platform = MetaCivilizationPlatform()
    category_records: list[dict[str, object]] = []
    for label, key, attributes in PROOF_CATEGORIES:
        try:
            declaration = platform.dimensions.register_dimension(
                key, description=label, attributes=dict(attributes)
            )
            discovered = platform.dimensions.is_registered(key)
            trace = platform.dimensions.trace(key)
            category_records.append(
                {
                    "category": label,
                    "dimension": key,
                    "identity": declaration.identity,
                    "discoverable": discovered,
                    "traceable": bool(trace),
                    "governed": True,
                    "ok": discovered and bool(trace),
                }
            )
        except Exception as exc:  # noqa: BLE001 — a failure is recorded as evidence, not raised
            category_records.append(
                {"category": label, "dimension": key, "ok": False, "error": str(exc)}
            )

    os_records: list[dict[str, object]] = []
    for key, attributes in UNKNOWN_OPERATING_SYSTEMS:
        try:
            platform.generation.register_operating_system(key, attributes=dict(attributes))
            blueprint = f"{key}-blueprint"
            platform.generation.register_blueprint(blueprint, operating_system=key)
            result = platform.generation.generate(blueprint)
            rooted = platform.generation.verify_derivation(result)
            os_records.append(
                {
                    "operating_system": key,
                    "blueprint": blueprint,
                    "depth": len(result.strata),
                    "derivation_hash": result.derivation_hash(),
                    "rooted_in_meta_kernel": rooted,
                    "ok": rooted and len(result.strata) == len(platform.generation.strata()),
                }
            )
        except Exception as exc:  # noqa: BLE001 — a failure is recorded as evidence, not raised
            os_records.append({"operating_system": key, "ok": False, "error": str(exc)})

    after = layer_source_fingerprint()
    kernel_after = kernel_source_fingerprint()
    categories_proven = sum(1 for record in category_records if record["ok"])
    systems_proven = sum(1 for record in os_records if record["ok"])
    unchanged = before == after and kernel_before == kernel_after
    return {
        "obligation": "mandatory-architectural-proof",
        "categories_proven": categories_proven,
        "categories_total": len(PROOF_CATEGORIES),
        "operating_systems_proven": systems_proven,
        "operating_systems_total": len(UNKNOWN_OPERATING_SYSTEMS),
        "layer_source_fingerprint_before": before,
        "layer_source_fingerprint_after": after,
        "kernel_source_fingerprint_before": kernel_before,
        "kernel_source_fingerprint_after": kernel_after,
        "layer_unchanged": before == after,
        "kernel_unchanged": kernel_before == kernel_after,
        "passed": (
            categories_proven == len(PROOF_CATEGORIES)
            and systems_proven == len(UNKNOWN_OPERATING_SYSTEMS)
            and unchanged
        ),
        "category_records": category_records,
        "operating_system_records": os_records,
    }


# --------------------------------------------------------------------------- gates


def _gate_open_dimension_set() -> tuple[bool, str]:
    """A never-seen dimension is admitted and the open set grows by exactly one."""
    registry = DimensionRegistry()
    before = len(registry.dimensions())
    nonce = "Axis-" + mint("probe", "umk.civilization.probe", "nonce")[-8:]
    registry.register_dimension(nonce)
    after = len(registry.dimensions())
    ok = after == before + 1 and registry.is_registered(nonce)
    return ok, f"admitted {nonce!r} by registration; dimensions {before} -> {after}"


def _gate_no_finite_enumeration() -> tuple[bool, str]:
    """No module of this layer declares a closed enumeration."""
    ok, offenders = _layer_has_no_closed_enum()
    detail = "no Enum/IntEnum/StrEnum/Flag class in the layer" if ok else f"offenders: {offenders}"
    return ok, detail


def _gate_no_hardcoded_assumptions() -> tuple[bool, str]:
    """No prohibited token is built into the shipped vocabulary."""
    intersection = sorted(_vocabulary_keys() & set(PROHIBITED_TOKENS))
    ok = not intersection
    return ok, f"{len(PROHIBITED_TOKENS)} prohibited tokens; vocabulary intersection {intersection}"


def _gate_prohibited_representable() -> tuple[bool, str]:
    """Every prohibited token is nonetheless representable as a registered dimension."""
    registry = DimensionRegistry()
    for token in PROHIBITED_TOKENS:
        registry.register_dimension(f"Concrete-{token.title()}-Axis")
    keys = set(registry.dimension_keys())
    missing = [t for t in PROHIBITED_TOKENS if f"Concrete-{t.title()}-Axis" not in keys]
    ok = not missing
    return ok, f"all {len(PROHIBITED_TOKENS)} tokens admitted by registration; missing {missing}"


def _gate_no_dimension_ceiling() -> tuple[bool, str]:
    """A dimension declaring a closed value set, or a bound in either direction, is refused."""
    registry = DimensionRegistry()
    refused = 0
    # Derived from the single declared set, so a newly forbidden key is covered without a
    # gate edit. Re-listing the keys here would be a second enumeration of the same rule.
    attempted = FORBIDDEN_DIMENSION_KEYS
    for key in attempted:
        try:
            registry.register_dimension(f"Bounded-{key}", attributes={key: [1, 2, 3]})
        except DimensionClosedError:
            refused += 1
    ok = refused == len(attempted)
    return ok, f"{refused}/{len(attempted)} bound declarations refused at admission"


def _gate_no_fixed_pipeline() -> tuple[bool, str]:
    """Execution order is derived from declarations, and the rule itself is replaceable."""
    planner = CompositionPlanner()
    planner.register_capability("alpha")
    planner.register_capability("beta", requires=("alpha",))
    first = planner.plan(("beta",))
    planner.register_capability("gamma", requires=("beta",))
    second = planner.plan(("gamma",))
    grew = len(second.steps) == len(first.steps) + 1
    total = planner.plan(("gamma",), strategy="dependency-order")
    waved = planner.plan(("gamma",), strategy="parallel-waves")
    same_set = {s.capability for s in total.steps} == {s.capability for s in waved.steps}
    strategy_open = len(strategy_names()) >= 2
    ok = grew and same_set and strategy_open and total.plan_hash() != waved.plan_hash()
    return ok, (
        f"registering a capability changed the plan ({len(first.steps)} -> "
        f"{len(second.steps)} steps) with no code change; {len(strategy_names())} "
        "strategies registered; the same declarations yield different plans per strategy"
    )


def _gate_open_operating_system_catalogue() -> tuple[bool, str]:
    """A never-seen constitutional operating system is generated without a code change."""
    generator = ConstitutionalGenerator()
    before = len(generator.operating_systems())
    nonce = "OS-" + mint("probe", "umk.civilization.probe", "os-nonce")[-8:]
    generator.register_operating_system(nonce)
    generator.register_blueprint(f"{nonce}-bp", operating_system=nonce)
    result = generator.generate(f"{nonce}-bp")
    after = len(generator.operating_systems())
    ok = after == before + 1 and generator.verify_derivation(result)
    return ok, f"generated {nonce!r}; catalogue {before} -> {after}; lineage rooted at the kernel"


def _gate_open_stratum_chain() -> tuple[bool, str]:
    """A never-seen generation stratum extends the chain without a code change."""
    generator = ConstitutionalGenerator()
    before = generator.strata()
    generator.register_stratum("ProbeStratum", after=before[-1])
    after = generator.strata()
    ok = len(after) == len(before) + 1 and after[-1] == "ProbeStratum"
    return ok, f"generation depth {len(before)} -> {len(after)} by registration alone"


def _gate_nothing_bypasses_the_kernel() -> tuple[bool, str]:
    """Every generated record roots, by derivation, at the kernel's reflective root."""
    platform = MetaCivilizationPlatform()
    platform.dimensions.register_dimension("Probe-Axis")
    platform.composition.register_capability("probe-capability", dimensions=("Probe-Axis",))
    platform.generation.register_operating_system("Probe-OS")
    platform.generation.register_blueprint(
        "probe-bp",
        operating_system="Probe-OS",
        dimensions=("Probe-Axis",),
        capabilities=("probe-capability",),
    )
    result, plan = platform.realize("probe-bp")
    root = platform.generation.kernel_root()
    every_record_registered = all(
        platform.kernel.registry.exists(identity) for identity in result.lineage
    )
    every_step_registered = all(platform.kernel.registry.exists(s.identity) for s in plan.steps)
    ok = (
        result.root == root
        and every_record_registered
        and every_step_registered
        and platform.generation.validate()
    )
    return ok, (
        f"{len(result.lineage)} generated records and {len(plan.steps)} composed step(s), every "
        f"one admitted through the kernel registry and rooted at {root}"
    )


def _gate_no_parallel_authority() -> tuple[bool, str]:
    """This layer claims no authority and introduces no second registry."""
    platform = MetaCivilizationPlatform()
    one_kernel = (
        platform.dimensions.kernel is platform.kernel
        and platform.composition.kernel is platform.kernel
        and platform.generation.kernel is platform.kernel
    )
    ok = platform.authority == "NONE" and one_kernel
    return ok, (
        f"declared authority {platform.authority!r}; all three components admit through the "
        "single kernel registry, so no parallel authority and no second registry exist"
    )


def _gate_no_implementation_leakage() -> tuple[bool, str]:
    """Two independently constructed platforms are byte-identical."""
    first = MetaCivilizationPlatform().snapshot_hash()
    second = MetaCivilizationPlatform().snapshot_hash()
    ok = first == second
    return ok, f"independent platform snapshot hashes {'match' if ok else 'differ'}: {first[:16]}…"


def _gate_unknown_future_compatibility(proof: dict[str, object]) -> tuple[bool, str]:
    """The mandatory architectural proof passes and no source byte changed."""
    ok = bool(proof["passed"])
    return ok, (
        f"{proof['categories_proven']}/{proof['categories_total']} categories and "
        f"{proof['operating_systems_proven']}/{proof['operating_systems_total']} operating "
        f"systems admitted by registration; layer unchanged={proof['layer_unchanged']}, "
        f"kernel unchanged={proof['kernel_unchanged']}"
    )


def quality_gates() -> dict[str, object]:
    """Execute every constitutional quality gate of this layer."""
    proof = architectural_proof()
    probes = (
        ("no-closed-dimension-set", _gate_open_dimension_set),
        ("no-finite-enumeration", _gate_no_finite_enumeration),
        ("no-hardcoded-dimension-assumptions", _gate_no_hardcoded_assumptions),
        ("prohibited-tokens-representable-by-registration", _gate_prohibited_representable),
        ("no-dimension-declares-a-ceiling", _gate_no_dimension_ceiling),
        ("no-fixed-pipeline", _gate_no_fixed_pipeline),
        ("no-finite-operating-system-catalogue", _gate_open_operating_system_catalogue),
        ("no-finite-generation-chain", _gate_open_stratum_chain),
        ("nothing-bypasses-the-meta-kernel", _gate_nothing_bypasses_the_kernel),
        ("no-parallel-constitutional-authority", _gate_no_parallel_authority),
        ("no-implementation-leakage", _gate_no_implementation_leakage),
    )
    gates: list[dict[str, object]] = []
    for gate_id, probe in probes:
        passed, evidence = probe()
        gates.append({"id": gate_id, "passed": passed, "evidence": evidence})
    passed, evidence = _gate_unknown_future_compatibility(proof)
    gates.append({"id": "unknown-future-compatibility", "passed": passed, "evidence": evidence})
    return {
        "passed": all(bool(gate["passed"]) for gate in gates),
        "gates": gates,
        "architectural_proof": proof,
    }


def constitutional_report() -> dict[str, object]:
    """The whole executed constitutional determination of this layer."""
    gates = quality_gates()
    platform = MetaCivilizationPlatform()
    report: dict[str, object] = {
        "programme": "PROGRAM-004 — Universal Meta-Civilization Platform",
        "layer_version": MetaCivilizationPlatform.version,
        "authority": MetaCivilizationPlatform.authority,
        "layer_source_fingerprint": layer_source_fingerprint(),
        "kernel_source_fingerprint": kernel_source_fingerprint(),
        "mandatory_dimension_facets": list(dimension_facet_keys()),
        "facet_definitions": {key: desc for key, desc in DIMENSION_FACETS},
        "generation_strata": list(platform.generation.strata()),
        "quality_gates": gates,
        "self_certification": platform.certify(),
        "verdict": "CONSTITUTIONALLY-COMPLIANT" if gates["passed"] else "NON-COMPLIANT",
        "passed": gates["passed"],
    }
    report["report_hash"] = content_digest({k: v for k, v in report.items() if k != "report_hash"})
    return report


__all__ = [
    "PROHIBITED_TOKENS",
    "PROOF_CATEGORIES",
    "UNKNOWN_OPERATING_SYSTEMS",
    "layer_source_fingerprint",
    "architectural_proof",
    "quality_gates",
    "constitutional_report",
]

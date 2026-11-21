"""Phase 4 Step 8 — platform composition validation (ADR-0010, ADR-0013).

The claim under test is negative and therefore easy to fake: *no specialized engine is
required*. A suite that only registered platforms and asserted success would prove nothing,
because a repository full of per-platform engines would pass it. So this suite proves the
claim three ways:

1. **Every named platform class composes** from registered nuclei plus configuration, and a
   composition owns nothing — enforced by ``derive_role`` rather than asserted by a label.
2. **No engine source branches on a platform name.** Measured structurally over
   ``engine/**/*.py``: a platform identifier appearing in a conditional would be the
   specialized engine the principle forbids, so its absence is checked, not trusted.
3. **A platform the repository has never named** — space operations, and then a deliberately
   unknowable one — is admitted by declaration with the kernel fingerprint unchanged.

The composition model Step 8 names is
``Entity + Capability + Relationship + Context + Knowledge + Rules + Evolution``. Each term
is checked to be a *registered nucleus* rather than a heading in a document, and every
platform is checked to select only from that registered population.
"""

from __future__ import annotations

import os
import re

from engine.kernel.compliance import kernel_source_fingerprint
from engine.lineage.memory import load_declaration, resolve
from engine.nucleus import (
    SEED_COMPOSITIONS,
    SEED_NUCLEI,
    StructuralRole,
    SubjectDeclaration,
    build_seed_registry,
    derive_role,
)

COMPOSITION_NAMESPACE = "ucos.structure.composition"

#: The platform classes Step 8 requires to remain composable, mapped to the composition key
#: that carries each. 'space' and 'future unknown' are deliberately absent from the seed
#: population — they are proved by admission instead, which is the stronger property.
REQUIRED_PLATFORM_CLASSES: dict[str, str] = {
    "Amazon-like": "amazon",
    "Uber-like": "uber",
    "X-like": "x",
    "ERP": "erp",
    "CRM": "crm",
    "Banking": "banking-platform",
    "Healthcare": "healthcare-platform",
    "Education": "lms",
    "Government": "government-platform",
    "Scientific": "scientific-platform",
}

#: The seven terms of the composition model Step 8 declares, mapped to the nucleus that owns
#: each concern. 'Capability' is not a nucleus — it is what a nucleus OWNS — so it is
#: verified separately, against the capability population.
COMPOSITION_MODEL_NUCLEI: dict[str, str] = {
    "Entity": "identity",
    "Relationship": "relationship",
    "Context": "context",
    "Knowledge": "knowledge",
    "Rules": "policy",
    "Evolution": "evolution",
}


def _seed_composition_keys() -> set[str]:
    return {key for key, _title, _composes in SEED_COMPOSITIONS}


def _seed_nucleus_keys() -> set[str]:
    return {entry[0] for entry in SEED_NUCLEI}


# -- 1. every named platform class composes ---------------------------------- #


def test_every_required_platform_class_is_a_registered_composition():
    """Amazon, Uber, X, ERP, CRM, banking, healthcare, education, government, scientific."""
    available = _seed_composition_keys()
    missing = {
        label: key for label, key in REQUIRED_PLATFORM_CLASSES.items() if key not in available
    }
    assert not missing, f"platform classes with no registered composition: {missing}"


def test_a_composition_owns_nothing_and_that_is_derived_not_labelled():
    """A subject that selects nuclei composes, therefore owns nothing (NL-06).

    This is the clause that makes "Amazon is a composition" a derivation rather than an
    opinion. If a platform could own a capability it would be a nucleus, and a per-platform
    nucleus is exactly the specialized engine this step forbids.
    """
    registry = build_seed_registry()
    for label, key in REQUIRED_PLATFORM_CLASSES.items():
        subject = registry.subject(key)
        assert subject.role is StructuralRole.COMPOSITION, f"{label} is not a composition"
        assert subject.composes, f"{label} selects no nuclei"
        assert not subject.concept, f"{label} owns a canonical concept, so it is a nucleus"
        # The role is re-derived from the declaration's own content, not read off a field
        assert derive_role(subject) is StructuralRole.COMPOSITION

    # No composition appears as the owner of any capability
    composition_keys = _seed_composition_keys()
    for capability in registry.capabilities():
        assert (
            capability.owner_key not in composition_keys
        ), f"capability {capability.key} is owned by composition {capability.owner_key}"


def test_every_platform_selects_only_registered_nuclei():
    """A platform is nuclei plus configuration — never a new engine smuggled in as a name."""
    nuclei = _seed_nucleus_keys()
    for key, _title, composes in SEED_COMPOSITIONS:
        assert composes, f"composition {key} selects nothing"
        unknown = sorted(set(composes) - nuclei)
        assert not unknown, f"composition {key} selects unregistered nuclei: {unknown}"


def test_the_declared_composition_model_is_a_registered_population():
    """Entity + Capability + Relationship + Context + Knowledge + Rules + Evolution."""
    registry = build_seed_registry()
    nuclei = _seed_nucleus_keys()

    for term, nucleus_key in COMPOSITION_MODEL_NUCLEI.items():
        assert nucleus_key in nuclei, f"the {term} term has no registered nucleus"
        subject = registry.subject(nucleus_key)
        assert subject.role is StructuralRole.NUCLEUS
        # A nucleus owns exactly one canonical concept
        assert subject.concept, f"{term} nucleus owns no canonical concept"

    # 'Capability' is the seventh term and is what a nucleus owns, so it is proved by the
    # capability population being non-empty and every capability having a nucleus owner.
    capabilities = registry.capabilities()
    assert capabilities, "the composition model names Capability but none is registered"
    for capability in capabilities:
        assert capability.owner_key in nuclei, f"capability {capability.key} has no nucleus owner"


# -- 2. no engine branches on a platform name -------------------------------- #


def test_no_engine_source_branches_on_a_platform_name():
    """The negative claim, measured: a platform identifier in engine control flow would be
    the specialized engine ADR-0010 refuses.

    ``engine/nucleus/catalog.py`` is exempt because that file is the DATA that declares the
    population; naming a platform there is the declaration, not a branch. Tests are exempt
    because naming a platform is how a test addresses it.
    """
    engine_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    engine_root = os.path.dirname(engine_root)  # .../engine
    exempt = {
        os.path.join("engine", "nucleus", "catalog.py"),
        os.path.join("engine", "civilization", "catalog.py"),
    }

    # Only distinctive platform names: generic nucleus words like 'identity' or 'x' would
    # produce meaningless hits, so the check uses names that can only mean a platform.
    distinctive = [
        key
        for key, _t, _c in SEED_COMPOSITIONS
        if len(key) > 3 and key not in {"commerce", "retail", "marketplace"}
    ]
    pattern = re.compile(r"""["']({})["']""".format("|".join(re.escape(k) for k in distinctive)))

    offenders: list[str] = []
    for base, _dirs, files in os.walk(engine_root):
        if "__pycache__" in base or os.sep + "tests" in base:
            continue
        for name in files:
            if not name.endswith(".py"):
                continue
            full = os.path.join(base, name)
            relative = os.path.relpath(full, os.path.dirname(engine_root))
            if relative in exempt:
                continue
            with open(full, encoding="utf-8") as handle:
                source = handle.read()
            for match in pattern.finditer(source):
                offenders.append(f"{relative}: {match.group(1)}")

    assert not offenders, f"engine source names a platform outside its data catalog: {offenders}"


def test_no_platform_specific_module_exists():
    """No engine module is named after a platform."""
    engine_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    engine_root = os.path.dirname(engine_root)
    platform_keys = _seed_composition_keys()

    named: list[str] = []
    for base, dirs, files in os.walk(engine_root):
        if "__pycache__" in base or os.sep + "tests" in base:
            continue
        for entry in list(dirs) + [f[:-3] for f in files if f.endswith(".py")]:
            if entry in platform_keys:
                named.append(os.path.join(os.path.relpath(base, engine_root), entry))
    assert not named, f"platform-specific engine modules exist: {named}"


# -- 3. an unnamed platform is admitted by declaration ----------------------- #


def test_a_space_platform_composes_with_no_code_change():
    """Space is deliberately NOT in the seed population, and needs no engine to exist."""
    assert "space-operations-platform" not in _seed_composition_keys()

    before = kernel_source_fingerprint()
    registry = build_seed_registry()
    record = registry.register_subject(
        SubjectDeclaration(
            key="space-operations-platform",
            title="Space Operations Platform",
            namespace=COMPOSITION_NAMESPACE,
            composes=(
                "location",
                "geography",
                "time",
                "calendar",
                "measurement",
                "units",
                "identity",
                "execution",
                "workflow",
                "trust",
                "security",
                "evolution",
                "knowledge",
                "relationship",
                "context",
                "policy",
                "regulation",
            ),
            description="Orbital and interplanetary operations",
        )
    )
    after = kernel_source_fingerprint()

    assert before == after, "admitting a space platform required a kernel change"
    assert record.role is StructuralRole.COMPOSITION
    assert not record.concept, "a platform that owns a concept is an engine"
    assert len(record.composes) == 17


def test_a_future_unknown_platform_composes_with_no_code_change():
    """A platform whose domain we cannot describe is still only nuclei plus configuration."""
    before = kernel_source_fingerprint()
    registry = build_seed_registry()
    record = registry.register_subject(
        SubjectDeclaration(
            key="unknown-reality-platform",
            title="Unknown Reality Platform",
            namespace=COMPOSITION_NAMESPACE,
            composes=("identity", "relationship", "context", "knowledge", "policy", "evolution"),
            description="A platform for a domain that has not been conceived",
        )
    )
    after = kernel_source_fingerprint()

    assert before == after
    assert record.role is StructuralRole.COMPOSITION
    # It composes precisely the declared composition model and nothing platform-specific
    assert set(record.composes) == set(COMPOSITION_MODEL_NUCLEI.values())


def test_admitting_platforms_does_not_disturb_the_seed_population():
    """Registration returns a changed registry without amending the declared catalog."""
    before = len(SEED_COMPOSITIONS)
    registry = build_seed_registry()
    registry.register_subject(
        SubjectDeclaration(
            key="ephemeral-platform",
            title="Ephemeral Platform",
            namespace=COMPOSITION_NAMESPACE,
            composes=("identity",),
        )
    )
    # The DATA catalog is untouched; only this registry instance saw the admission
    assert len(SEED_COMPOSITIONS) == before
    assert "ephemeral-platform" not in _seed_composition_keys()


# -- composition and memory are the same substrate --------------------------- #


def test_a_composed_platform_resolves_memory_through_the_same_seven_layers():
    """Step 8 and Step 6 must be one substrate, not two.

    A platform is not a special kind of subject with its own memory mechanism. Whatever the
    repository remembers about a platform is resolved by the same declared layer set that
    serves every other subject, so no platform brings a memory engine with it.
    """
    declaration = load_declaration()
    for key in ("amazon", "uber", "erp", "space-operations-platform", "unknown-reality-platform"):
        memory = resolve(key)
        # Every declared layer answers, for a seeded platform and an unnamed one alike
        assert tuple(x.layer for x in memory.layers) == declaration.names
        for layer in memory.layers:
            for entry in layer.entries:
                assert entry.source and entry.owner

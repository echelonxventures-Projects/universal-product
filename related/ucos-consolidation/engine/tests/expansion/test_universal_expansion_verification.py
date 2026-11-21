"""WP-UCDA-023 — Universal Expansion Verification Suite (ADR-0008).

One test suite proving admission of unknown entity, context, relationship, technology,
language, currency, measurement, intelligence, platform composition and future concept
through ordinary registration while asserting the kernel source fingerprint is unchanged.

Each case proves open-world reach, not domain support — the substrate must admit something
that is deliberately NOT an Earth/known concept without requiring any code change. That
is the property that distinguishes an open substrate from merely an extensible one.

The registry contract these tests hold it to, read from ``engine/ceu/existence.py``:

* ``find(universal_id)`` resolves by IDENTIFIER, not by key. ``has(form, key)`` and
  ``unit(form, key)`` are the key-addressed lookups.
* ``classification`` on a unit is a UNIVERSAL IDENTIFIER of a registered classification
  unit, obtained with ``id_of("classification", key)`` — not a bare key.
* A form that no seed catalog declares must be declared with ``declare_form`` first. That
  declaration IS the open-world admission path, so calling it is the proof, not a workaround.
"""

from __future__ import annotations

from engine.ceu.catalog import bootstrap
from engine.ceu.existence import ExistenceRegistry, ExistenceUnit
from engine.context.taxonomy import ROOT_TAXON, UNIVERSAL_TAXONOMY, ContextTaxon
from engine.kernel.compliance import kernel_source_fingerprint


def test_unknown_entity_form_needs_no_code_change():
    """Admit a previously-unknown form of existence — no code change required."""
    before = kernel_source_fingerprint()
    registry = ExistenceRegistry()
    # Declare a form that has never appeared in any seed catalog
    registry.declare_form(
        "trans-dimensional-resonance", title="Trans-Dimensional Resonance", code="TDIM"
    )
    # Register a unit of that form
    unit = registry.register(
        ExistenceUnit(
            form="trans-dimensional-resonance",
            key="amplitude-nexus-1",
            title="Amplitude Nexus Alpha",
            definition="A resonance pattern across dimensional boundaries",
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert unit.universal_id.startswith("UCOS-TDIM-")
    assert registry.counts()["trans-dimensional-resonance"] == 1
    # Resolvable by identifier, which is what find() addresses
    assert registry.find(unit.universal_id) is not None


def test_unknown_context_kind_needs_no_code_change():
    """Admit a previously-unknown context kind — no code change required."""
    before = kernel_source_fingerprint()
    # Extend the taxonomy with a future kind
    extended = UNIVERSAL_TAXONOMY.extend(
        ContextTaxon(
            taxon_id="CTX-PROBABILISTIC",
            kind="probabilistic",
            title="Probabilistic Context",
            parent=ROOT_TAXON,
            description="The probability distribution over possible states",
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert "probabilistic" in extended.kinds()
    assert len(extended) == 18  # 16 universal + root + this one
    # The owner taxonomy is untouched — extension returns a new taxonomy
    assert "probabilistic" not in UNIVERSAL_TAXONOMY.kinds()


def test_unknown_relationship_type_needs_no_code_change():
    """Admit a previously-unknown relationship type — no code change required."""
    before = kernel_source_fingerprint()
    registry = bootstrap()  # Seed forms including relationship-type
    # Register a relationship type that has never appeared in SEED_RELATIONSHIP_TYPES
    unit = registry.register(
        ExistenceUnit(
            form="relationship-type",
            key="entangles-with",
            title="Entangles With",
            definition="A quantum entanglement relationship",
            attributes={"topologies": ("quantum",)},
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert registry.has("relationship-type", "entangles-with")
    assert registry.find(unit.universal_id) is not None


def test_unknown_technology_type_needs_no_code_change():
    """Admit a previously-unknown technology execution kind — no code change required."""
    before = kernel_source_fingerprint()
    registry = bootstrap()
    # 'technology' is deliberately NOT a seeded form: declaring it IS the admission path
    assert not registry.has_form("technology")
    registry.declare_form("technology", title="Technology", code="TECH")
    unit = registry.register(
        ExistenceUnit(
            form="technology",
            key="plasma-lattice-compute",
            title="Plasma Lattice Compute",
            definition="Computation through plasma state manipulation",
            attributes={"substrate": "non-silicon", "known": False},
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert registry.has("technology", "plasma-lattice-compute")
    assert registry.find(unit.universal_id) is not None


def test_unknown_language_needs_no_code_change():
    """Admit a previously-unknown language — no code change required."""
    before = kernel_source_fingerprint()
    registry = bootstrap()
    if not registry.has_form("language-family"):
        registry.declare_form("language-family", title="Language Family", code="LANG")
    # A language modality no human civilization uses
    unit = registry.register(
        ExistenceUnit(
            form="language-family",
            key="electromagnetic-resonance",
            title="Electromagnetic Resonance Communication",
            definition="A language modality using electromagnetic field patterns",
            attributes={"modality": "electromagnetic", "scripts": "open"},
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert registry.has("language-family", "electromagnetic-resonance")
    assert registry.find(unit.universal_id) is not None


def test_unknown_currency_needs_no_code_change():
    """Admit a previously-unknown currency — no code change required."""
    before = kernel_source_fingerprint()
    registry = bootstrap()
    if not registry.has_form("currency"):
        registry.declare_form("currency", title="Currency", code="CRCY")
    # A value system with no monetary authority and no planetary origin
    unit = registry.register(
        ExistenceUnit(
            form="currency",
            key="entropy-credit",
            title="Entropy Credit",
            definition="A value exchange system based on reversible negentropy",
            attributes={"unit": "reversible-negentropy", "divisibility": "continuous"},
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert registry.has("currency", "entropy-credit")
    assert registry.find(unit.universal_id) is not None


def test_unknown_measurement_unit_needs_no_code_change():
    """Admit a previously-unknown measurement unit — no code change required."""
    before = kernel_source_fingerprint()
    registry = bootstrap()  # Seed forms including unit
    # A unit from no human measurement system
    unit = registry.register(
        ExistenceUnit(
            form="unit",
            key="resonance-amplitude",
            title="Resonance Amplitude",
            definition="A unit of dimensional resonance intensity",
            attributes={"system": "non-human", "quantity": "energy"},
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert registry.has("unit", "resonance-amplitude")
    assert registry.find(unit.universal_id) is not None


def test_unknown_intelligence_form_needs_no_code_change():
    """Admit a previously-unknown intelligence form — no code change required."""
    before = kernel_source_fingerprint()
    registry = bootstrap()
    if not registry.has_form("intelligence-classification"):
        registry.declare_form(
            "intelligence-classification", title="Intelligence Classification", code="INTL"
        )
    # Neither human nor machine
    unit = registry.register(
        ExistenceUnit(
            form="intelligence-classification",
            key="swarm-emergent",
            title="Swarm-Emergent Intelligence",
            definition="Intelligence emerging from collective interaction patterns",
            attributes={"substrate": "distributed", "emergence": "collective"},
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert registry.has("intelligence-classification", "swarm-emergent")
    assert registry.find(unit.universal_id) is not None


def test_unknown_platform_nucleus_needs_no_code_change():
    """Admit a previously-unknown platform nucleus — no code change required."""
    before = kernel_source_fingerprint()
    registry = bootstrap()  # Seed forms including entity, and the classification units
    # classification is addressed by IDENTIFIER, so resolve the seeded classification first
    nucleus = registry.id_of("classification", "nucleus")
    unit = registry.register(
        ExistenceUnit(
            form="entity",
            key="reality-compilation",
            title="Reality Compilation",
            definition="Capability to compile and execute reality models",
            classification=nucleus,
            attributes={"domain": "cross-universe", "scope": "unbounded"},
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    # The nucleus is registered, discoverable, and classified by the seeded classification
    assert registry.has("entity", "reality-compilation")
    assert registry.find(unit.universal_id) is not None
    assert unit.classification == nucleus
    assert unit in registry.units(form="entity", classification=nucleus)


def test_unknown_future_concept_needs_no_code_change():
    """Admit a concept of a kind not yet named — no code change required."""
    before = kernel_source_fingerprint()
    registry = ExistenceRegistry()
    # Declare a form that represents a concept category we have not yet conceived
    registry.declare_form("unknown-concept-category", title="Unknown Concept Category", code="UNKC")
    # Register an instance of it
    unit = registry.register(
        ExistenceUnit(
            form="unknown-concept-category",
            key="concept-beyond-description",
            title="Concept Beyond Current Description",
            definition="A concept whose nature is not yet fully understood",
            attributes={"described": False, "discoverable": True},
        )
    )
    after = kernel_source_fingerprint()
    # The substrate admitted it without any kernel change
    assert before == after
    assert registry.counts()["unknown-concept-category"] == 1
    assert registry.find(unit.universal_id) is not None


def test_every_admission_is_journalled_and_the_journal_verifies():
    """Admission of the unknown is RECORDED, not merely permitted.

    Openness without memory would be a substrate that forgets what it admitted. Every
    admission above goes through the same append-only hash-chained journal, and that chain
    must verify after admitting concepts the catalog never named.
    """
    before = kernel_source_fingerprint()
    registry = ExistenceRegistry()
    registry.declare_form("unknown-form-a", title="Unknown Form A", code="UNFA")
    registry.declare_form("unknown-form-b", title="Unknown Form B", code="UNFB")
    admitted = [
        registry.register(
            ExistenceUnit(form=form, key=f"{form}-instance", title=form, definition=form)
        )
        for form in ("unknown-form-a", "unknown-form-b")
    ]
    after = kernel_source_fingerprint()

    assert before == after
    # The append-only chain still verifies after admitting unnamed concepts.
    # verify_audit() returns FINDINGS; empty means the chain reproduces end to end.
    assert registry.verify_audit() == []
    # Nothing admitted is left without a journal entry
    assert registry.unlineaged() == ()
    for unit in admitted:
        assert registry.find(unit.universal_id) is not None


def test_suite_proves_every_principle_axis():
    """Every principle axis named in WP-UCDA-023 is covered by a test in this suite.

    This is a meta-test ensuring no test is removed without replacement.
    """
    import inspect
    import sys

    current_module = sys.modules[__name__]
    test_functions = {
        name
        for name, obj in inspect.getmembers(current_module)
        if inspect.isfunction(obj) and name.startswith("test_unknown_")
    }

    required_axes = {
        "entity": "test_unknown_entity_form_needs_no_code_change",
        "context": "test_unknown_context_kind_needs_no_code_change",
        "relationship": "test_unknown_relationship_type_needs_no_code_change",
        "technology": "test_unknown_technology_type_needs_no_code_change",
        "language": "test_unknown_language_needs_no_code_change",
        "currency": "test_unknown_currency_needs_no_code_change",
        "measurement": "test_unknown_measurement_unit_needs_no_code_change",
        "intelligence": "test_unknown_intelligence_form_needs_no_code_change",
        "platform": "test_unknown_platform_nucleus_needs_no_code_change",
        "future-concept": "test_unknown_future_concept_needs_no_code_change",
    }
    # Each named axis is proved by a test that is actually present, so removing one fails
    missing = {axis: fn for axis, fn in required_axes.items() if fn not in test_functions}
    assert not missing, f"axes named by WP-UCDA-023 with no test: {sorted(missing)}"
    assert len(test_functions) >= len(required_axes)

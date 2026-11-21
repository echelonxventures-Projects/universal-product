"""UCOS-NUC-001 — the registry, the ownership gate, and the catalogue."""

from __future__ import annotations

import pytest

from engine.nucleus import catalog
from engine.nucleus.errors import (
    CompositionOwnershipViolation,
    LayerOwnershipViolation,
    OwnershipViolation,
    RegistrationError,
)
from engine.nucleus.law import LAW_ID, StructuralRole
from engine.nucleus.model import CapabilityDeclaration, SubjectDeclaration
from engine.nucleus.ownership import GATE_ID, enforce, gate
from engine.nucleus.registry import (
    STRUCTURAL_ROLE_VOCABULARY,
    NucleusRegistry,
    build_seed_registry,
    declarations_from_mapping,
)
from engine.uckp.vocabulary import build_vocabulary_registry


@pytest.fixture(scope="module")
def registry() -> NucleusRegistry:
    return build_seed_registry()


# -- the catalogue and the correction ---------------------------------------- #


def test_commerce_is_not_in_the_nucleus_population():
    keys = catalog.nucleus_keys()
    for aggregate in ("commerce", "retail", "marketplace", "erp", "crm", "amazon", "uber"):
        assert aggregate not in keys, f"{aggregate} must not be a nucleus"


def test_every_named_platform_is_a_composition():
    compositions = set(catalog.composition_keys())
    for named in (
        "commerce",
        "amazon",
        "uber",
        "paytm",
        "whatsapp",
        "facebook",
        "instagram",
        "x",
        "linkedin",
        "youtube",
        "erp",
        "crm",
        "lms",
        "edtech",
        "banking-platform",
        "insurance-platform",
        "healthcare-platform",
        "government-platform",
        "defence-platform",
        "industrial-platform",
        "scientific-platform",
        "research-platform",
        "civilizational-platform",
    ):
        assert named in compositions


def test_layers_come_from_the_governed_layer_vocabulary():
    from engine.uckp.vocabulary import ARCHITECTURE_LAYER, DEFAULT_VOCABULARIES

    vocabulary = DEFAULT_VOCABULARIES.require(ARCHITECTURE_LAYER)
    assert set(catalog.layer_keys()) == set(vocabulary.term_ids())


def test_every_composition_selects_only_declared_nuclei():
    nuclei = set(catalog.nucleus_keys())
    for key, _title, composes in catalog.SEED_COMPOSITIONS:
        assert composes, f"{key} selects nothing"
        assert set(composes) <= nuclei, f"{key} selects a non-nucleus"


def test_catalogue_document_declares_no_ceiling():
    document = catalog.to_document()
    assert document["closed_set"] is False
    assert document["upper_limit"] is None
    assert "Commerce is a Composition" in document["correction"]


# -- registration ------------------------------------------------------------ #


def test_seed_population_is_registered(registry: NucleusRegistry):
    counts = registry.counts()
    assert counts["nuclei"] == len(catalog.SEED_NUCLEI)
    assert counts["compositions"] == len(catalog.SEED_COMPOSITIONS)
    assert counts["layers"] == len(catalog.layer_keys())
    assert counts["capabilities"] == counts["assignments"]
    assert counts["capabilities"] == len(catalog.SEED_NUCLEI) * len(
        catalog.SEED_CAPABILITY_SUFFIXES
    )


def test_a_layer_and_a_nucleus_may_share_a_name(registry: NucleusRegistry):
    layer = registry.subject("governance", role="layer")
    nucleus = registry.subject("governance", role=StructuralRole.NUCLEUS)
    assert layer.universal_id != nucleus.universal_id
    with pytest.raises(RegistrationError) as exc:
        registry.subject("governance")
    assert sorted(exc.value.detail["roles"]) == ["layer", "nucleus"]


def test_composition_owning_a_capability_is_refused(registry: NucleusRegistry):
    with pytest.raises(CompositionOwnershipViolation) as exc:
        registry.register_capability(
            CapabilityDeclaration(key="probe-a", title="probe", owner="commerce")
        )
    assert exc.value.detail["clause"] == "NL-03"


def test_layer_owning_a_capability_is_refused(registry: NucleusRegistry):
    with pytest.raises(LayerOwnershipViolation) as exc:
        registry.register_capability(
            CapabilityDeclaration(key="probe-b", title="probe", owner="platform")
        )
    assert exc.value.detail["clause"] == "NL-02"


def test_composition_specific_capability_is_refused(registry: NucleusRegistry):
    with pytest.raises(OwnershipViolation):
        registry.register_capability(
            CapabilityDeclaration(key="commerce.checkout", title="checkout", owner="payment")
        )


def test_unregistered_owner_is_refused(registry: NucleusRegistry):
    with pytest.raises(RegistrationError):
        registry.register_capability(
            CapabilityDeclaration(key="probe-c", title="probe", owner="nothing-here")
        )


def test_duplicate_registration_is_refused():
    fresh = NucleusRegistry()
    declaration = SubjectDeclaration(key="payment", title="Payment", concept="payment")
    fresh.register_subject(declaration)
    with pytest.raises(RegistrationError):
        fresh.register_subject(declaration)


def test_composition_selecting_an_unregistered_nucleus_is_refused():
    fresh = NucleusRegistry()
    with pytest.raises(RegistrationError):
        fresh.register_subject(
            SubjectDeclaration(key="commerce", title="Commerce", composes=("absent",))
        )


def test_composition_may_not_select_a_layer():
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="platform", title="Platform Layer"))
    with pytest.raises(RegistrationError):
        fresh.register_subject(
            SubjectDeclaration(key="commerce", title="Commerce", composes=("platform",))
        )


def test_unregistered_parent_is_refused():
    fresh = NucleusRegistry()
    with pytest.raises(RegistrationError):
        fresh.register_subject(
            SubjectDeclaration(key="child", title="Child", parent="absent-layer")
        )


def test_parent_may_be_any_registered_subject():
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="platform", title="Platform Layer"))
    child = fresh.register_subject(
        SubjectDeclaration(key="child", title="Child", parent="platform")
    )
    assert child.parent == "platform"
    assert fresh.has_subject("child")
    assert fresh.has_subject("child", role="layer")
    assert not fresh.has_subject("absent")


def test_duplicate_capability_is_refused(registry: NucleusRegistry):
    with pytest.raises(RegistrationError):
        registry.register_capability(
            CapabilityDeclaration(
                key="payment.authority", title="dup", owner="payment", namespace="ucos.capability"
            )
        )


# -- ownership movement ------------------------------------------------------ #


def test_reassignment_supersedes_and_preserves_the_chain():
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    fresh.register_subject(SubjectDeclaration(key="billing", title="Billing", concept="billing"))
    fresh.register_capability(
        CapabilityDeclaration(key="invoice", title="Invoice", owner="payment")
    )
    first = fresh.assignment_for("invoice")
    moved = fresh.reassign_capability("invoice", new_owner="billing", authority="TEST", note="move")
    assert moved.supersedes == first.assignment_id
    assert fresh.owner_of("invoice").key == "billing"
    assert len(fresh.assignments(capability_key="invoice")) == 2


def test_reassignment_to_an_unlawful_owner_is_refused():
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    fresh.register_subject(SubjectDeclaration(key="platform", title="Platform Layer"))
    fresh.register_capability(
        CapabilityDeclaration(key="invoice", title="Invoice", owner="payment")
    )
    with pytest.raises(LayerOwnershipViolation):
        fresh.reassign_capability("invoice", new_owner="platform", authority="TEST")


def test_reassignment_of_an_unregistered_capability_is_refused():
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    with pytest.raises(RegistrationError):
        fresh.reassign_capability("absent", new_owner="payment", authority="TEST")


def test_missing_lookups_fail_closed(registry: NucleusRegistry):
    with pytest.raises(RegistrationError):
        registry.subject("absent")
    with pytest.raises(RegistrationError):
        registry.subject("payment", role="layer")
    with pytest.raises(RegistrationError):
        registry.subject_by_id("UCOS-NUC-ffffffffffff")
    with pytest.raises(RegistrationError):
        registry.capability("absent")
    with pytest.raises(RegistrationError):
        registry.assignment_for("absent")


# -- composition ------------------------------------------------------------- #


def test_commerce_composes_entirely_from_registered_nuclei(registry: NucleusRegistry):
    composed = registry.compose("commerce")
    assert composed["owns_capabilities"] is False
    assert composed["nucleus_count"] == 13
    assert composed["capability_count"] == 13 * len(catalog.SEED_CAPABILITY_SUFFIXES)
    owners = {c["owner"] for c in composed["capabilities"]}
    assert owners == set(registry.subject("commerce", role="composition").composes)


def test_every_composition_composes(registry: NucleusRegistry):
    for composition in registry.compositions():
        composed = registry.compose(composition.key)
        assert composed["nucleus_count"] >= 1
        assert composed["owns_capabilities"] is False


def test_only_a_composition_can_be_composed(registry: NucleusRegistry):
    with pytest.raises(RegistrationError):
        registry.compose("payment")


def test_composition_order_is_derived_and_acyclic(registry: NucleusRegistry):
    order = registry.composition_order()
    assert len(order) == registry.counts()["subjects"]
    assert registry.selection_cycles() == ()
    placement = {key: wave for wave, key in order}
    for composition in registry.compositions():
        vertex = f"composition:{composition.key}"
        for selected in composition.composes:
            assert placement[f"nucleus:{selected}"] < placement[vertex]


def test_composition_order_supports_parallel_waves(registry: NucleusRegistry):
    waves = registry.composition_order(strategy="parallel-waves")
    assert max(w for w, _k in waves) >= 1


# -- the gate ---------------------------------------------------------------- #


def test_gate_passes_over_the_seed_population(registry: NucleusRegistry):
    report = enforce(registry)
    assert report.gate_id == GATE_ID
    assert report.law_id == LAW_ID
    assert report.status == "PASS"
    assert report.blocking_failures == ()
    assert set(report.measurements.values()) == {0}
    assert report.findings == ()
    assert report.digest() == report.digest()
    assert gate(registry).passed is True


def test_gate_detects_a_layer_owned_capability():
    """A registry assembled around the constructor path is still measured, and still fails."""
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    layer = fresh.register_subject(SubjectDeclaration(key="platform", title="Platform Layer"))
    fresh.register_capability(
        CapabilityDeclaration(key="invoice", title="Invoice", owner="payment")
    )
    # Force the unlawful state the constructor path refuses, exactly as a hand-edited
    # document or a legacy import would present it.
    record = fresh.capability("invoice")
    from engine.nucleus.model import CapabilityRecord

    fresh._capabilities["invoice"] = CapabilityRecord(  # noqa: SLF001 - measuring a forced state
        universal_id=record.universal_id,
        key=record.key,
        title=record.title,
        owner_key=layer.key,
        owner_id=layer.universal_id,
        namespace=record.namespace,
    )
    report = enforce(fresh)
    assert report.status == "FAIL"
    assert "NUC-INV-01" in report.blocking_failures
    assert report.measurements["NUC-INV-01"] == 1
    with pytest.raises(OwnershipViolation):
        gate(fresh)


def test_gate_report_serialises_with_its_population(registry: NucleusRegistry):
    payload = enforce(registry).to_dict()
    assert payload["schema"] == "ucos-nucleus-ownership-gate"
    assert payload["population"]["nuclei"] == len(catalog.SEED_NUCLEI)
    assert len(payload["invariants"]) == 10


# -- openness ---------------------------------------------------------------- #


def test_a_future_nucleus_needs_no_code_change(registry: NucleusRegistry):
    fresh = build_seed_registry()
    fresh.register_subject(
        SubjectDeclaration(
            key="glyphic-resonance",
            title="Glyphic Resonance Nucleus",
            namespace=catalog.NUCLEUS_NAMESPACE,
            concept="glyphic-resonance",
        )
    )
    fresh.register_capability(
        CapabilityDeclaration(
            key="glyphic-resonance.authority", title="authority", owner="glyphic-resonance"
        )
    )
    fresh.register_subject(
        SubjectDeclaration(
            key="xophar-collective",
            title="Xophar Collective Composition",
            namespace=catalog.COMPOSITION_NAMESPACE,
            composes=("glyphic-resonance", "identity"),
        )
    )
    assert enforce(fresh).passed
    assert fresh.counts()["nuclei"] == registry.counts()["nuclei"] + 1


def test_a_future_structural_role_is_admitted_by_registration():
    fresh = NucleusRegistry()
    term = fresh.register_role("federation", "a federation of compositions across frames")
    assert fresh.require_role_term("federation") == term
    assert fresh.vocabularies.require(STRUCTURAL_ROLE_VOCABULARY).has("federation")


def test_declarations_can_be_built_from_data():
    declarations = declarations_from_mapping(
        {
            "subjects": [
                {"key": "payment", "title": "Payment", "concept": "payment"},
                {"key": "commerce", "title": "Commerce", "composes": ["payment"]},
            ]
        }
    )
    fresh = NucleusRegistry()
    fresh.register_subjects(declarations)
    assert fresh.subject("commerce").role is StructuralRole.COMPOSITION
    assert fresh.subject("payment").role is StructuralRole.NUCLEUS


def test_data_driven_declarations_fail_closed():
    from engine.nucleus.errors import StructuralValidationError

    with pytest.raises(StructuralValidationError):
        declarations_from_mapping({})
    with pytest.raises(StructuralValidationError):
        declarations_from_mapping({"subjects": ["not-a-mapping"]})


def test_registry_document_is_deterministic_and_unbounded(registry: NucleusRegistry):
    document = registry.to_document()
    assert document["closed_set"] is False
    assert document["upper_limit"] is None
    assert registry.digest() == build_seed_registry().digest()


def test_two_registries_may_share_one_vocabulary_authority():
    """ARTICLE 17 PUTS THE ROLES IN A REGISTRY, AND A REGISTRY IS REGISTERED ONCE.

    Every registry here builds its own vocabulary registry, so the role vocabulary was always
    absent and always registered — the arm that finds it ALREADY there had no case. It is
    what lets two nucleus registries share one vocabulary authority, which is the whole point
    of the vocabulary being injectable: registering the terms a second time would either
    raise or create a second answer to "what is a structural role".
    """
    vocabularies = build_vocabulary_registry()

    first = NucleusRegistry(vocabularies=vocabularies)
    second = NucleusRegistry(vocabularies=vocabularies)

    assert first.vocabularies is second.vocabularies
    assert first.require_role_term("nucleus") == second.require_role_term("nucleus")
    assert vocabularies.get(STRUCTURAL_ROLE_VOCABULARY) is not None


def test_two_subjects_that_mint_one_identity_are_refused():
    """THE KEY COLLISION WAS TESTED AND THE IDENTITY COLLISION WAS NOT.

    A (role, key) pair registered twice is refused by the first check. This is the second:
    two DIFFERENT declarations whose deterministic identity is the same. It cannot arise from
    the seed catalogue, because identity is derived from role, namespace and key and those
    three are exactly what the first check already made unique — which is why the arm was
    dead. It is the registry's guarantee that the derivation stays injective: two subjects
    under one universal id would make every lookup answer arbitrarily, and the refusal names
    both so the collision can be read.
    """
    registry = NucleusRegistry()
    first = registry.register_subject(SubjectDeclaration(key="tax", title="Tax", concept="tax"))

    class _Colliding(SubjectDeclaration):
        @property
        def identity(self) -> str:
            return first.universal_id

    with pytest.raises(RegistrationError, match="identity collision") as raised:
        registry.register_subject(_Colliding(key="levy", title="Levy", concept="levy"))

    assert raised.value.detail["universal_id"] == first.universal_id
    assert raised.value.detail["subject"] == "levy"


def test_a_role_no_clause_names_is_still_refused_ownership():
    """THE DECISION IS THE FIRST LINE; THE BRANCHES BELOW ARE ONLY REPORTING.

    ``may_own_capability`` resolves to the CEU registry, so what may own is a registered
    fact — and the three roles that exist each have a clause naming them, which leaves the
    final refusal unreachable through any declared role. It is what the docstring says it is:
    the catch for a role with no specific clause, so an owner is refused WHETHER OR NOT a
    clause names its role. Without it a fourth role admitted by registration would fall off
    the end of the function and be granted ownership by omission — which is the exact failure
    Article 17's open registration makes possible.
    """
    registry = build_seed_registry()

    class _Role:
        # A role admitted by registration and named by no clause. It cannot be a
        # StructuralRole member, because the enum is exactly the three roles that DO have
        # clauses — which is why this arm is unreachable through any declared subject.
        value = "an-unregistered-role"

    class _Owner:
        key = "future"
        role = _Role()
        may_own_capability = False

    with pytest.raises(OwnershipViolation) as raised:
        registry._require_lawful_owner(_Owner(), capability="tax.rate")

    assert raised.value.detail["clause"] == "NL-01"
    assert type(raised.value) is OwnershipViolation

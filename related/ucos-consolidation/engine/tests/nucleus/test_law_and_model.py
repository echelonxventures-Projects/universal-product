"""UCOS-NUC-001 — the ownership law, the structural model, and the Commerce correction."""

from __future__ import annotations

import pytest

from engine.nucleus import law
from engine.nucleus.errors import MisclassificationError, StructuralValidationError
from engine.nucleus.law import LAW_ID, OWNERSHIP_CLAUSES, OWNERSHIP_INVARIANTS, StructuralRole
from engine.nucleus.model import (
    CapabilityDeclaration,
    CapabilityRecord,
    OwnershipAssignment,
    SubjectDeclaration,
    SubjectRecord,
    derive_role,
)


def test_only_the_nucleus_role_may_own():
    assert StructuralRole.NUCLEUS.may_own_capability is True
    assert StructuralRole.LAYER.may_own_capability is False
    assert StructuralRole.COMPOSITION.may_own_capability is False
    assert StructuralRole.COMPOSITION.may_select_nuclei is True
    assert StructuralRole.NUCLEUS.may_select_nuclei is False


def test_role_coercion_fails_closed():
    assert StructuralRole.coerce("nucleus") is StructuralRole.NUCLEUS
    assert StructuralRole.coerce(StructuralRole.LAYER) is StructuralRole.LAYER
    with pytest.raises(StructuralValidationError):
        StructuralRole.coerce("universe")
    assert set(StructuralRole.values()) == {"nucleus", "layer", "composition"}


def test_law_document_is_complete_and_deterministic():
    document = law.to_document()
    assert document["law_id"] == law.LAW_ID
    assert len(document["clauses"]) == len(OWNERSHIP_CLAUSES) == 10
    assert len(document["invariants"]) == len(OWNERSHIP_INVARIANTS) == 10
    assert law.digest() == law.digest()
    assert law.clause("NL-02").refuses
    with pytest.raises(StructuralValidationError):
        law.clause("NL-99")


def test_law_carries_the_negative_clauses_that_were_absent():
    statements = " ".join(c.statement for c in OWNERSHIP_CLAUSES)
    assert "Layer SHALL NOT own a capability" in statements
    assert "Composition SHALL NOT own a capability" in statements
    assert "Commerce" in statements


def test_role_is_derived_from_the_declaration_itself():
    nucleus = SubjectDeclaration(key="payment", title="Payment", concept="payment")
    layer = SubjectDeclaration(key="platform", title="Platform Layer")
    composition = SubjectDeclaration(key="commerce", title="Commerce", composes=("payment",))
    assert derive_role(nucleus) is StructuralRole.NUCLEUS
    assert derive_role(layer) is StructuralRole.LAYER
    assert derive_role(composition) is StructuralRole.COMPOSITION
    assert composition.structural_role is StructuralRole.COMPOSITION


def test_commerce_cannot_be_declared_a_nucleus():
    with pytest.raises(MisclassificationError) as exc:
        SubjectDeclaration(
            key="commerce", title="Commerce Nucleus", role="nucleus", composes=("payment",)
        )
    assert exc.value.detail["derived"] == "composition"
    assert exc.value.detail["declared"] == "nucleus"


def test_a_subject_may_not_both_own_a_concept_and_compose():
    with pytest.raises(MisclassificationError):
        SubjectDeclaration(key="hybrid", title="Hybrid", concept="x", composes=("payment",))


def test_declared_role_must_match_derived_role():
    with pytest.raises(MisclassificationError):
        SubjectDeclaration(key="platform", title="Platform", role="nucleus")
    with pytest.raises(MisclassificationError):
        SubjectDeclaration(key="payment", title="Payment", role="layer", concept="payment")


def test_identity_is_derived_and_kind_specific():
    nucleus = SubjectDeclaration(key="governance", title="G", concept="governance")
    layer = SubjectDeclaration(key="governance", title="G Layer")
    assert nucleus.identity.startswith("UCOS-NUC-")
    assert layer.identity.startswith("UCOS-LYR-")
    assert nucleus.identity != layer.identity
    twin = SubjectDeclaration(key="governance", title="G", concept="governance")
    assert nucleus.identity == twin.identity


def test_records_are_sealed_and_reproduce_themselves():
    record = SubjectRecord.of(SubjectDeclaration(key="tax", title="Tax", concept="taxation"))
    assert record.is_intact()
    assert record.content_hash
    assert record.expected_identity() == record.universal_id
    tampered = SubjectRecord(
        universal_id=record.universal_id,
        key="tax",
        title="Tampered",
        role=StructuralRole.NUCLEUS,
        namespace=record.namespace,
        concept="taxation",
        content_hash=record.content_hash,
    )
    assert tampered.is_intact() is False


def test_capability_declaration_requires_an_owner():
    with pytest.raises(StructuralValidationError):
        CapabilityDeclaration(key="orphan", title="Orphan", owner="")
    declaration = CapabilityDeclaration(key="tax.rate", title="Rate", owner="tax")
    assert declaration.identity.startswith("UCOS-CAP-")


def test_declaration_refuses_malformed_fields():
    with pytest.raises(StructuralValidationError):
        SubjectDeclaration(key="k", title="")
    with pytest.raises(StructuralValidationError):
        SubjectDeclaration(key="k", title="T", composes="payment")
    with pytest.raises(StructuralValidationError):
        SubjectDeclaration(key="k", title="T", composes=("a", "a"))


def test_ownership_assignment_lawfulness_follows_the_role():
    lawful = OwnershipAssignment(
        capability_id="UCOS-CAP-000000000001",
        capability_key="tax.rate",
        owner_id="UCOS-NUC-000000000001",
        owner_key="tax",
        owner_role=StructuralRole.NUCLEUS,
        authority=law.LAW_ID,
    )
    unlawful = OwnershipAssignment(
        capability_id="UCOS-CAP-000000000001",
        capability_key="tax.rate",
        owner_id="UCOS-CMPO-000000000001",
        owner_key="commerce",
        owner_role=StructuralRole.COMPOSITION,
        authority=law.LAW_ID,
    )
    assert lawful.is_lawful is True
    assert unlawful.is_lawful is False
    assert lawful.assignment_id != unlawful.assignment_id
    assert lawful.to_dict()["owner_role"] == "nucleus"


def test_assignment_requires_an_authority():
    with pytest.raises(StructuralValidationError):
        OwnershipAssignment(
            capability_id="UCOS-CAP-000000000001",
            capability_key="tax.rate",
            owner_id="UCOS-NUC-000000000001",
            owner_key="tax",
            owner_role=StructuralRole.NUCLEUS,
            authority="",
        )


def test_structural_role_terms_are_data():
    terms = dict(law.structural_role_terms())
    assert set(terms) == {"nucleus", "layer", "composition"}
    assert "owns nothing" in terms["layer"]
    assert "owns nothing" in terms["composition"]


def test_a_declared_role_that_agrees_with_the_derived_one_is_kept():
    """THREE MISMATCHES WERE TESTED AND THE AGREEMENT WAS NOT.

    NL-06 refuses a declaration whose stated role contradicts the role its own content
    implies, and each contradiction has a case. The agreeing arm is the one every honest
    declaration takes, and until now nothing showed that stating the correct role is ALLOWED
    — a check that only ever refused would make the field unusable and push every author to
    omit it, which is the opposite of what declaring a role is for.
    """
    for key, extra in (
        ("payment", {"concept": "payment", "role": "nucleus"}),
        ("platform", {"role": "layer"}),
        ("commerce", {"composes": ("payment",), "role": "composition"}),
    ):
        declared = SubjectDeclaration(key=key, title=key.title(), **extra)
        assert declared.structural_role is derive_role(declared)
        assert declared.role is declared.structural_role


def test_an_absent_sequence_field_is_empty_rather_than_a_fault():
    """OPTIONAL MEANS ABSENT, AND ABSENT IS NOT MALFORMED.

    Every declaration in this suite either omits its sequence fields entirely (taking the
    default) or supplies a real tuple, so the explicit-``None`` arm had no case. It is the
    shape a rehydrated declaration arrives in — a JSON document carrying ``"composes": null``
    — and refusing it would make a round trip through JSON impossible for a field whose whole
    point is that it may be left unsaid.
    """
    subject = SubjectDeclaration(key="k", title="T", composes=None)
    capability = CapabilityDeclaration(key="k.c", title="C", owner="k", depends_on=None)

    assert subject.composes == ()
    assert capability.depends_on == ()


def test_every_declaration_renders_the_fields_it_carries():
    """A DECLARATION IS DATA, AND ITS RENDER IS HOW IT LEAVES THE PROCESS.

    Records are sealed and their payloads are tested; the DECLARATIONS they are built from
    had no render exercised at all. It is what writes a declaration back to a catalogue —
    with the role RESOLVED rather than as it was written, so a declaration that omitted its
    role round-trips carrying the role the model derived for it.
    """
    subject = SubjectDeclaration(key="tax", title="Tax", concept="taxation")
    capability = CapabilityDeclaration(
        key="tax.rate", title="Rate", owner="tax", description="a rate", depends_on=("tax.base",)
    )

    assert subject.to_dict()["role"] == StructuralRole.NUCLEUS.value
    assert subject.to_dict()["key"] == "tax"
    assert capability.to_dict() == {
        "key": "tax.rate",
        "title": "Rate",
        "owner": "tax",
        "namespace": capability.namespace,
        "description": "a rate",
        "depends_on": ["tax.base"],
    }


def test_a_rehydrated_record_keeps_the_seal_it_was_given():
    """A SEAL IS EVIDENCE OF WHAT WAS RECORDED, NOT A FIELD THE MODEL FILLS IN.

    Every record here is built through ``of``, which seals it — so the arm that KEEPS a
    supplied hash had never run for the capability or the assignment. It is what lets a
    record be read back from a document and still be checkable: re-sealing on construction
    would overwrite the recorded digest with one computed from the values just parsed, so a
    tampered document would seal itself clean and ``is_intact`` could never answer False.
    """
    capability = CapabilityRecord(
        universal_id="UCOS-CAP-000000000001",
        key="tax.rate",
        title="Rate",
        owner_key="tax",
        owner_id="UCOS-NUC-000000000001",
        namespace="ucos.nucleus",
        content_hash="a-recorded-seal",
    )
    assignment = OwnershipAssignment(
        capability_id="UCOS-CAP-000000000001",
        capability_key="tax.rate",
        owner_id="UCOS-NUC-000000000001",
        owner_key="tax",
        owner_role=StructuralRole.NUCLEUS,
        authority=LAW_ID,
        content_hash="another-recorded-seal",
    )

    assert capability.content_hash == "a-recorded-seal"
    assert assignment.content_hash == "another-recorded-seal"

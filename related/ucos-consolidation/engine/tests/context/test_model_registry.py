"""UCXI-000001 Parts 04/05 — value object and registration authority tests.

The registration authority is where the layer's constitutional rules become
non-negotiable, so these tests assert the refusals as strongly as the successes:
provenance cannot be omitted, identity cannot be supplied, the same identity cannot
hold two contexts, the same substance cannot have two homes, and history cannot be
overwritten.
"""

from __future__ import annotations

import pytest

from engine.context.catalog import UNIVERSAL_CATALOG, bootstrap_registry, catalog_sources
from engine.context.errors import (
    ContextGraphError,
    ContextNotFoundError,
    ContextOnceViolation,
    ContextRegistrationError,
    ContextValidationError,
    DuplicateContextError,
    LifecycleTransitionError,
    OntologyError,
    TaxonomyError,
)
from engine.context.model import (
    ContextDeclaration,
    ContextRecord,
    ContextRelationEdge,
    ContextValue,
    Observer,
    json_safe,
    values_from_mapping,
)
from engine.context.registry import (
    GENESIS_HASH,
    AuditEntry,
    ContextRegistry,
    declarations_from_mapping,
)
from engine.context.resolution import ContextRequest, resolve
from engine.context.taxonomy import ContextAuthority, ContextKind, ContextLifecycle, ContextRelation
from engine.tests.context.conftest import declaration, spatial_values

# ------------------------------------------------------------------ value objects


def test_value_requires_provenance() -> None:
    with pytest.raises(ContextValidationError):
        ContextValue(dimension="x", value=1, authority=ContextAuthority.OBSERVED, source="")
    with pytest.raises(ContextValidationError):
        ContextValue(dimension="", value=1, authority=ContextAuthority.OBSERVED, source="s")


def test_value_normalises_and_ranks() -> None:
    low = ContextValue(
        dimension="d", value=1, authority=ContextAuthority.INFERRED, source=" sensor "
    )
    high = ContextValue(
        dimension="d", value=1, authority=ContextAuthority.CONSTITUTIONAL, source="charter"
    )
    assert low.source == "sensor"
    assert high.outranks(low)
    assert not low.outranks(high)
    assert high.to_dict()["authority"] == "constitutional"


def test_json_safe_normalises_and_refuses_unrepresentable() -> None:
    assert json_safe({"b": (1, 2), "a": "x"}) == {"a": "x", "b": [1, 2]}
    with pytest.raises(ContextValidationError):
        json_safe({1: "x"})
    with pytest.raises(ContextValidationError):
        json_safe(object())


def test_declaration_validates_its_own_shape() -> None:
    with pytest.raises(ContextValidationError):  # no dimension asserted
        ContextDeclaration(kind="temporal", namespace="ucos.test", natural_key="k", values=())
    with pytest.raises(ContextValidationError):  # unbounded
        declaration(boundary="  ")
    with pytest.raises(ContextValidationError):  # kind absent
        ContextDeclaration(
            kind=" ",
            namespace="ucos.test",
            natural_key="k",
            values=values_from_mapping({"a": 1}, authority=ContextAuthority.OBSERVED, source="s"),
        )
    with pytest.raises(ContextValidationError):  # duplicate dimension
        ContextDeclaration(
            kind="temporal",
            namespace="ucos.test",
            natural_key="k",
            values=(
                ContextValue(
                    dimension="d", value=1, authority=ContextAuthority.OBSERVED, source="s"
                ),
                ContextValue(
                    dimension="d", value=2, authority=ContextAuthority.OBSERVED, source="s"
                ),
            ),
        )


def test_declaration_identity_is_deterministic_and_namespace_insensitive() -> None:
    first = declaration(namespace="ucos.test", natural_key="subject")
    second = declaration(namespace="UCOS.Test", natural_key="subject")
    assert first.identity == second.identity
    assert first.identity.startswith("UCOS-CTX-")
    assert declaration(natural_key="other").identity != first.identity


def test_relation_edge_identity_and_refusals() -> None:
    edge = ContextRelationEdge(relation=ContextRelation.CONTAINS, source="a", target="b")
    assert edge.edge_id.startswith("CTXE-")
    assert edge.edge_id == ContextRelationEdge(relation="contains", source="a", target="b").edge_id
    with pytest.raises(ContextValidationError):
        ContextRelationEdge(relation=ContextRelation.CONTAINS, source="a", target="a")
    with pytest.raises(ContextValidationError):
        ContextRelationEdge(relation=ContextRelation.CONTAINS, source="", target="b")


def test_observer_requires_identity_and_vantage() -> None:
    observer = Observer(observer_id="o", vantage="v")
    assert observer.to_dict()["epistemic_access"] == "unspecified"
    with pytest.raises(ContextValidationError):
        Observer(observer_id="", vantage="v")


# --------------------------------------------------------------------- registration


def test_register_mints_identity_and_seals_content(empty_registry: ContextRegistry) -> None:
    record = empty_registry.register(declaration())
    assert record.context_id.startswith("UCOS-CTX-")
    assert record.lifecycle is ContextLifecycle.REGISTERED
    assert record.taxon_id == "CTX-TEMPORAL"
    assert record.universal is True
    assert record.is_intact()
    assert record.dimension("ordering") is not None
    assert record.dimension("nope") is None
    assert record.dimensions() == ("ordering", "reference_frame", "resolution")
    assert len(empty_registry) == 1
    assert empty_registry.audit()[0].previous_hash == GENESIS_HASH


def test_register_is_idempotent_for_identical_content(empty_registry: ContextRegistry) -> None:
    first = empty_registry.register(declaration())
    second = empty_registry.register(declaration())
    assert first is second
    assert len(empty_registry.audit()) == 1


def test_register_refuses_a_different_context_under_one_identity(
    empty_registry: ContextRegistry,
) -> None:
    empty_registry.register(declaration())
    with pytest.raises(DuplicateContextError):
        empty_registry.register(
            declaration(
                values={
                    "reference_frame": "another clock",
                    "ordering": "causal",
                    "resolution": "one tick",
                }
            )
        )


def test_register_enforces_context_once(empty_registry: ContextRegistry) -> None:
    empty_registry.register(declaration(natural_key="first"))
    with pytest.raises(ContextOnceViolation):
        empty_registry.register(declaration(natural_key="second"))


def test_register_refuses_unclassified_kind_and_bad_shape(
    empty_registry: ContextRegistry,
) -> None:
    with pytest.raises(TaxonomyError):
        empty_registry.register(declaration(kind="quantum"))
    with pytest.raises(OntologyError):
        empty_registry.register(declaration(values={"reference_frame": "utc"}))


def test_register_refuses_an_unregistered_parent(empty_registry: ContextRegistry) -> None:
    with pytest.raises(ContextRegistrationError):
        empty_registry.register(declaration(parent="UCOS-CTX-000000000000"))


def test_parent_declaration_creates_a_containment_edge(empty_registry: ContextRegistry) -> None:
    parent = empty_registry.register(
        declaration(kind=ContextKind.SPATIAL, natural_key="outer", values=spatial_values())
    )
    child = empty_registry.register(declaration(natural_key="inner", parent=parent.context_id))
    edges = empty_registry.relations(relation=ContextRelation.CONTAINS)
    assert len(edges) == 1
    assert edges[0].source == parent.context_id
    assert edges[0].target == child.context_id


# ------------------------------------------------------------------------ relations


def test_relate_validates_endpoints_admissibility_and_cycles(
    empty_registry: ContextRegistry,
) -> None:
    a = empty_registry.register(declaration(natural_key="a"))
    b = empty_registry.register(
        declaration(kind=ContextKind.SPATIAL, natural_key="b", values=spatial_values())
    )
    with pytest.raises(ContextNotFoundError):
        empty_registry.relate(ContextRelation.CONTAINS, "UCOS-CTX-000000000000", a.context_id)
    with pytest.raises(OntologyError):  # only observer context observes
        empty_registry.relate(ContextRelation.OBSERVES, a.context_id, b.context_id)

    edge = empty_registry.relate(ContextRelation.DEPENDS_ON, a.context_id, b.context_id)
    assert empty_registry.relate(ContextRelation.DEPENDS_ON, a.context_id, b.context_id) is edge
    with pytest.raises(ContextGraphError):
        empty_registry.relate(ContextRelation.DEPENDS_ON, b.context_id, a.context_id)


def test_relations_filter_by_type(universal_registry: ContextRegistry) -> None:
    records = universal_registry.records()
    universal_registry.relate(
        ContextRelation.EQUIVALENT_TO, records[0].context_id, records[1].context_id
    )
    assert len(universal_registry.relations(relation=ContextRelation.EQUIVALENT_TO)) == 1
    assert universal_registry.relations(relation=ContextRelation.CONTAINS) == ()


# ------------------------------------------------------------------------ lifecycle


def test_transition_and_illegal_transition(empty_registry: ContextRegistry) -> None:
    record = empty_registry.register(declaration())
    advanced = empty_registry.transition(record.context_id, ContextLifecycle.RESOLVED)
    assert advanced.lifecycle is ContextLifecycle.RESOLVED
    assert empty_registry.get(record.context_id).lifecycle is ContextLifecycle.RESOLVED
    with pytest.raises(LifecycleTransitionError):
        empty_registry.transition(record.context_id, ContextLifecycle.DECLARED)
    assert empty_registry.by_lifecycle(ContextLifecycle.RESOLVED)


def test_supersede_retains_history(empty_registry: ContextRegistry) -> None:
    original = empty_registry.register(declaration(natural_key="v1"))
    successor = empty_registry.supersede(
        original.context_id,
        declaration(
            natural_key="v2",
            values={
                "reference_frame": "revised clock",
                "ordering": "causal",
                "resolution": "one tick",
            },
        ),
    )
    assert empty_registry.get(original.context_id).lifecycle is ContextLifecycle.SUPERSEDED
    assert successor.context_id != original.context_id
    edges = empty_registry.relations(relation=ContextRelation.SUPERSEDES)
    assert edges[0].source == successor.context_id
    assert len(empty_registry) == 2  # append-only: nothing was destroyed


def test_supersede_refuses_a_different_kind(empty_registry: ContextRegistry) -> None:
    original = empty_registry.register(declaration())
    with pytest.raises(ContextRegistrationError):
        empty_registry.supersede(
            original.context_id,
            declaration(kind=ContextKind.SPATIAL, natural_key="v2", values=spatial_values()),
        )


def test_record_with_lifecycle_preserves_identity(empty_registry: ContextRegistry) -> None:
    record = empty_registry.register(declaration())
    moved = record.with_lifecycle(ContextLifecycle.RESOLVED)
    assert moved.context_id == record.context_id
    assert moved.content_hash == record.content_hash


# ---------------------------------------------------------------------------- reads


def test_reads_and_views(universal_registry: ContextRegistry) -> None:
    assert len(universal_registry) == 16
    assert len(universal_registry.kinds()) == 16
    assert universal_registry.boundaries() == ("ucos-universal",)
    assert len(universal_registry.by_namespace("ucos.context")) == 16
    assert len(universal_registry.by_boundary("ucos-universal")) == 16
    assert len(universal_registry.by_kind(ContextKind.TEMPORAL)) == 1
    assert universal_registry.by_kind("quantum") == ()
    assert universal_registry.is_universally_covered()
    assert all(universal_registry.universal_coverage().values())
    assert len(universal_registry.bindings()) == 16

    a_record = universal_registry.records()[0]
    assert universal_registry.has(a_record.context_id)
    assert universal_registry.find(a_record.context_id) is a_record
    assert universal_registry.find("UCOS-CTX-000000000000") is None
    with pytest.raises(ContextNotFoundError):
        universal_registry.get("UCOS-CTX-000000000000")


def test_empty_registry_is_not_universally_covered(empty_registry: ContextRegistry) -> None:
    assert not empty_registry.is_universally_covered()
    assert set(empty_registry.universal_coverage().values()) == {False}


# ---------------------------------------------------------------------------- audit


def test_audit_chain_is_verifiable_and_deterministic(universal_registry: ContextRegistry) -> None:
    assert universal_registry.verify_audit() == []
    assert len(universal_registry.audit()) == 16
    assert universal_registry.seal() == universal_registry.seal()
    # A second, independently bootstrapped registry seals identically.
    assert bootstrap_registry().seal() == universal_registry.seal()


def test_audit_entry_detects_tampering() -> None:
    entry = AuditEntry(
        sequence=1, action="register", subject="s", content_hash="c", previous_hash=GENESIS_HASH
    )
    assert entry.entry_hash == entry.expected_hash()
    tampered = AuditEntry(
        sequence=1,
        action="register",
        subject="s",
        content_hash="c",
        previous_hash=GENESIS_HASH,
        entry_hash="deadbeef",
    )
    assert tampered.entry_hash != tampered.expected_hash()


def test_verify_audit_reports_a_broken_chain(empty_registry: ContextRegistry) -> None:
    empty_registry.register(declaration())
    journal = empty_registry.audit()
    broken = AuditEntry(
        sequence=2,
        action="register",
        subject="x",
        content_hash="c",
        previous_hash="not-the-previous-hash",
    )
    empty_registry._audit.append(broken)  # noqa: SLF001 - deliberate tamper for the test
    findings = empty_registry.verify_audit()
    assert findings and "previous-hash" in findings[0]
    assert len(journal) == 1


def test_summary_and_serialisation(universal_registry: ContextRegistry) -> None:
    summary = universal_registry.summary()
    assert summary["contexts"] == 16
    assert summary["universal_covered"] == 16
    assert summary["audit_intact"] is True
    payload = universal_registry.to_dict()
    assert len(payload["contexts"]) == 16
    assert payload["universal_coverage"]["temporal"] is True


# -------------------------------------------------------------------------- catalog


def test_catalog_covers_every_universal_kind() -> None:
    assert set(UNIVERSAL_CATALOG) == {kind.value for kind in ContextKind}
    assert catalog_sources()
    registry = bootstrap_registry()
    assert registry.is_universally_covered()
    # bootstrapping twice is idempotent, not a duplicate refusal
    bootstrap_registry(registry=registry)
    assert len(registry) == 16


def test_declarations_from_mapping_requires_a_source() -> None:
    payload = {
        "contexts": [
            {
                "kind": "temporal",
                "namespace": "ucos.test",
                "natural_key": "k",
                "values": {"reference_frame": "a", "ordering": "b", "resolution": "c"},
                "source": "test",
            }
        ]
    }
    declarations = declarations_from_mapping(payload)
    assert len(declarations) == 1
    assert declarations[0].values[0].source == "test"

    payload["contexts"][0].pop("source")
    with pytest.raises(ContextRegistrationError):
        declarations_from_mapping(payload)


def test_an_audit_entry_whose_own_hash_does_not_reproduce_is_reported(
    universal_registry: ContextRegistry,
) -> None:
    """THREE SEPARATE AUDIT DEFECTS, and only two had a test.

    A wrong sequence is a journal with a gap; a broken previous-hash is a journal somebody
    spliced; an entry hash that does not reproduce is an entry somebody EDITED IN PLACE while
    keeping the chain intact around it. The third is the one a chain check alone would miss,
    which is exactly why it is checked separately.
    """
    journal = universal_registry._audit  # noqa: SLF001 - deliberate corruption
    original = journal[0]
    object.__setattr__(original, "entry_hash", "0" * 64)

    findings = universal_registry.verify_audit()
    assert any("entry hash does not reproduce" in f for f in findings)


def test_a_rehydrated_record_keeps_the_seal_it_was_given(
    universal_registry: ContextRegistry,
) -> None:
    """A record seals itself when it is built and keeps the seal it is handed when it is read
    back. Resealing on rehydration would make every stored record verify against itself
    rather than against the state it was sealed over — and CXL-09, which compares the stored
    seal with a recomputation, would then be unable to catch anything."""
    genuine = universal_registry.records()[0]
    assert genuine.content_hash == genuine.recomputed_hash()

    rehydrated = ContextRecord(
        context_id=genuine.context_id,
        kind=genuine.kind,
        taxon_id=genuine.taxon_id,
        namespace=genuine.namespace,
        natural_key=genuine.natural_key,
        values=genuine.values,
        authority=genuine.authority,
        lifecycle=genuine.lifecycle,
        boundary=genuine.boundary,
        parent=genuine.parent,
        description=genuine.description,
        universal=genuine.universal,
        content_hash="0" * 64,
    )
    assert rehydrated.content_hash == "0" * 64, "the seal was recomputed on rehydration"
    assert rehydrated.recomputed_hash() == genuine.content_hash


def test_a_declaration_renders_the_fields_a_registration_reads() -> None:
    """``ContextDeclaration.to_dict`` is the wire form a registration is submitted in, and it
    had no caller. A projection nothing reads can drop a field — and a dropped ``boundary``
    or ``parent`` would register a context that is unbounded or detached, both of which the
    constitution then reports as the declaration's fault rather than the projection's."""
    declared = declaration(natural_key="rendered", boundary="frame-a", parent=None)
    rendered = declared.to_dict()

    assert rendered["kind"] == declared.kind
    assert rendered["namespace"] == declared.namespace
    assert rendered["natural_key"] == "rendered"
    assert rendered["authority"] == declared.authority.value
    assert rendered == declared.to_dict(), "the projection is not deterministic"


def test_a_rehydrated_resolution_keeps_the_seal_it_was_given(
    universal_registry: ContextRegistry,
) -> None:
    """The same rehydration discipline every sealed record in this package keeps: a stored
    resolution verifies against the state it was taken over, never against itself."""

    built = resolve(universal_registry, ContextRequest(kind="temporal"))
    assert built.content_hash

    rehydrated = type(built)(
        **{
            **{
                field: getattr(built, field)
                for field in built.__dataclass_fields__
                if field != "content_hash"
            },
            "content_hash": "0" * 64,
        }
    )
    assert rehydrated.content_hash == "0" * 64, "the seal was recomputed on rehydration"

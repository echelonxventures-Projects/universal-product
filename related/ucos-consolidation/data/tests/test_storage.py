"""EC3-B10-U05 — Storage construct tests (DMC-06 + DTA-01…10 + UDL-11/03/04/12)."""

from __future__ import annotations

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.schema import entity_schema_for
from data.storage import (
    PersistedEntityRef,
    Storage,
    StorageError,
    make_storage,
    runtime_ref_for,
)
from data.storage_meta import (
    STORAGE_META_CLASS,
    STORAGE_RELATIONSHIPS,
    DurabilityLevel,
    StorageKind,
    StorageState,
)

ENTITY_NAME = "ucos.demo.entity"
STORAGE_NAME = "ucos.demo.storage"
RUNTIME_REF = runtime_ref_for("state.persist")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _schema(entity):
    return entity_schema_for(entity, name="ucos.demo.schema", type_tag="ucos.core.schema")


def _storage(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    schema = overrides.pop("schema", None) or _schema(entity)
    kwargs = dict(
        kind=overrides.pop("kind", StorageKind.LOCAL),
        durability=overrides.pop("durability", DurabilityLevel.DURABLE),
    )
    kwargs.update(overrides)
    loci = kwargs.pop("loci", ("locus.primary",))
    runtime = kwargs.pop("runtime_ref", RUNTIME_REF)
    name = kwargs.pop("name", STORAGE_NAME)
    return make_storage(
        name,
        kwargs.pop("type_tag", "ucos.core.storage"),
        loci,
        ((entity, schema),),
        runtime,
        **kwargs,
    )


def test_storage_is_typed_named_identified_and_placement_explicit():
    s = _storage()
    assert s.meta_class == STORAGE_META_CLASS  # V1 (DMC-06)
    assert s.name == STORAGE_NAME  # DTA-03 named
    assert s.type_tag == "ucos.core.storage"  # DTA-01 / UDL-03 typed
    assert s.storage_id.startswith("UCOS-STORAGE-")  # UDL-04 identified (ENG-001)
    assert s.locus_count == 1  # DTA-03 / DTA-C1 explicit placement
    assert s.kind is StorageKind.LOCAL  # DXH-06 classified


def test_storage_persists_entity_by_reference_not_owning():
    entity = _entity()
    s = _storage(entity=entity)
    assert s.persisted_entity_ids() == (entity.entity_id,)  # DMR-05 persists
    assert s.absorbs_persisted() is False  # DTA-09 / DMX-02 — referenced, not owned
    ref_dict = s.persisted_refs[0].to_dict()
    assert ref_dict["owned"] is False
    assert ref_dict["binding"] == "DMR-05:persists"


def test_persisted_ref_requires_schema_conformance():
    entity = _entity()
    other = _entity(name="ucos.demo.other")
    schema_for_other = _schema(other)
    with pytest.raises(StorageError):  # DTA-K3 / DTA-C4 — persisted entity must conform
        PersistedEntityRef.from_entity(entity, schema_for_other)


def test_storage_is_schema_aligned():
    entity = _entity()
    schema = _schema(entity)
    s = _storage(entity=entity, schema=schema)
    assert s.is_schema_aligned() is True  # DTA-07 / DTA-K3
    assert s.schema_refs() == (schema.schema_id,)


def test_storage_binds_runtime_by_reference():
    s = _storage()
    assert s.binds_runtime_by_reference() is True  # DMR-11 / DTA-02 / DTA-K2
    assert s.runtime_ref.startswith("UCOS-RUNTIME-REF:")


def test_storage_identity_is_deterministic_and_structure_derived():
    a = _storage()
    b = _storage()
    c = _storage(name="different.storage")
    assert a.storage_id == b.storage_id  # same structure → same ENG-001 identity
    assert a.storage_id != c.storage_id  # different name → different identity


def test_storage_is_immutable_objecthood():
    s = _storage()
    with pytest.raises((AttributeError, TypeError)):
        s.name = "other"  # frozen object (ENG-002 objecthood)


def test_unnamed_storage_is_rejected_fail_closed():
    with pytest.raises(StorageError):
        _storage(name="")  # DTA-03


def test_untyped_storage_is_rejected_fail_closed():
    with pytest.raises(StorageError):
        _storage(type_tag="")  # DTA-01 / DTA-K1 / UDL-03


def test_storage_with_no_loci_is_rejected_fail_closed():
    with pytest.raises(StorageError):
        _storage(loci=())  # DTA-03 / DTA-C1 — explicit placement required


def test_local_topology_requires_single_locus():
    with pytest.raises(StorageError):  # DXH-06 / DTA-C3
        _storage(kind=StorageKind.LOCAL, loci=("a", "b"))


def test_distributed_topology_requires_multiple_loci():
    with pytest.raises(StorageError):  # DXH-06 / DTA-C3
        _storage(kind=StorageKind.DISTRIBUTED, loci=("only.one",))


def test_distributed_topology_with_multiple_loci_is_valid():
    s = _storage(kind=StorageKind.DISTRIBUTED, loci=("locus.a", "locus.b"))
    assert s.locus_count == 2
    assert s.is_topology_consistent() is True  # DTA-C3


def test_tiered_topology_requires_tiered_durability():
    with pytest.raises(StorageError):  # DXH-06 / DTA-04
        _storage(kind=StorageKind.TIERED, durability=DurabilityLevel.DURABLE)
    s = _storage(kind=StorageKind.TIERED, durability=DurabilityLevel.TIERED)
    assert s.is_topology_consistent() is True


def test_storage_naming_a_technology_is_rejected_fail_closed():
    # UDL-11 / DTA-01 / DTA-K5 — abstract topology only; names no engine/product.
    with pytest.raises(StorageError):
        _storage(loci=("postgres.primary",))
    with pytest.raises(StorageError):
        _storage(name="redis.cache")
    with pytest.raises(StorageError):
        _storage(type_tag="mongodb.collection")


def test_storage_persists_must_be_a_certified_entity_reference():
    with pytest.raises(StorageError):
        PersistedEntityRef.from_entity(object(), _schema(_entity()))  # DMR-05


def test_duplicate_locus_is_rejected():
    with pytest.raises(StorageError):  # DTA-C1
        _storage(kind=StorageKind.DISTRIBUTED, loci=("dup", "dup"))


def test_relationships_are_within_dmr_closure():
    s = _storage()
    assert set(s.meta_relationships()) <= set(STORAGE_RELATIONSHIPS)  # V2
    assert s.meta_relationships() == ("DMR-05", "DMR-10", "DMR-11")


def test_lifecycle_is_forward_only():
    s = _storage(state=StorageState.DEFINED)
    active = s.transition(StorageState.ACTIVE)
    assert active.state is StorageState.ACTIVE
    with pytest.raises(StorageError):
        active.transition(StorageState.DEFINED)  # UDL-12 — no backward transition


def test_durability_is_declared():
    s = _storage(durability=DurabilityLevel.TRANSIENT)
    assert s.durability is DurabilityLevel.TRANSIENT  # DTA-04
    assert s.is_durability_declared() is True


def test_versioned_evolution_is_recorded():
    s = _storage(version="2.0.0")
    assert s.version == "2.0.0"  # DTA-08 / UDL-12
    with pytest.raises(StorageError):
        _storage(version="")


def test_founding_graph_is_acyclic():
    s = _storage()
    assert s.is_founding_acyclic() is True  # V4 / DMK-03 / DTA-C3


def test_invalid_runtime_ref_is_rejected():
    with pytest.raises(StorageError):  # DMR-11 / DTA-K2 — must bind a RUNTIME reference
        _storage(runtime_ref="not-a-runtime-ref")


def test_non_constitutive_and_no_secret():
    s = _storage()
    assert s.confers_authority() is False  # UDL-15 / DTA-09 / C7
    assert s.redefines_el1() is False  # UDL-02 / DMI-05
    assert s.selects_technology() is False  # UDL-11 / DTA-K5 (abstract topology)
    assert s.embeds_secret() is False


def test_secret_bearing_storage_is_detected():
    leaky = _storage(name="password")
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_storage_to_dict_records_substrate_reuse():
    s = _storage()
    payload = s.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005"]
    assert payload["meta_class"] == "DMC-06"
    assert payload["absorbs_persisted"] is False
    assert payload["placement_explicit"] is True
    assert payload["schema_aligned"] is True
    assert payload["names_technology"] is False


def test_storage_type_is_the_realized_construct():
    assert isinstance(_storage(), Storage)


# --------------------------------------------------------------------------------------
# Every constructor guard, shown refusing (see data/tests/test_schema.py for the argument).
# --------------------------------------------------------------------------------------

from engine.tests import assert_every_guard_can_refuse  # noqa: E402


def test_every_persisted_entity_ref_guard_can_refuse():
    assert_every_guard_can_refuse(_storage().persisted_refs[0])


def test_every_storage_guard_can_refuse():
    """Three modes, because the topology rules are mutually exclusive: a Local storage
    cannot reach the distributed-cardinality guard and vice versa.

    Two guards are named as unreachable BY ARGUMENT MUTATION and proven directly below:
    the schema-alignment rule lives on a member of ``persisted_refs`` rather than on a
    declared field of the storage, and the technology scan reads the rendered document
    rather than any single value. Naming them here is what keeps the claim checkable
    instead of silently dropping two guards.
    """
    from dataclasses import replace as _replace

    local = _storage()
    distributed = _storage(kind=StorageKind.DISTRIBUTED, loci=("locus.a", "locus.b"))
    tiered = _storage(kind=StorageKind.TIERED, durability=DurabilityLevel.TIERED)
    witnesses = assert_every_guard_can_refuse(local, distributed, tiered, unreachable=(292, 311))
    assert witnesses

    # the two named guards, reached the only way they can be
    misaligned = _replace(local.persisted_refs[0], schema_ref="not-a-schema-id")
    with pytest.raises(StorageError, match="not schema-aligned"):
        _replace(local, persisted_refs=(misaligned,))
    with pytest.raises(StorageError, match="storage technology"):
        _storage(name="ucos.demo.postgres")


def test_persisting_requires_a_schema_object_not_a_lookalike() -> None:
    """DTA-07: the schema half of the pairing is refused on type, not duck-typed."""
    with pytest.raises(StorageError, match="must reference a data.schema.Schema"):
        PersistedEntityRef.from_entity(_entity(), "ucos.demo.schema")  # type: ignore[arg-type]


def test_storage_transition_refuses_a_state_that_is_not_a_lifecycle_member() -> None:
    """UDL-12 for the storage class: a string naming a state is not one."""
    stored = _storage(state=StorageState.ACTIVE)
    with pytest.raises(StorageError, match="DOS-01…05 state"):
        stored.transition("ACTIVE")  # type: ignore[arg-type]

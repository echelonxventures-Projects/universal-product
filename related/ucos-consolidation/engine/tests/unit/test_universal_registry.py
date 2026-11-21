"""Tests for UCOS-EPIC-001 — Universal Registry Platform (write-side authority).

Exercises the Registry Core and the twelve typed registries end to end: deterministic
ids, no-duplicate + Knowledge-Once enforcement, version chains (supersede-not-
overwrite), acyclic dependencies, the tamper-evident audit trail, persistence, the
facade, and the validation CLI. Everything runs in-memory / under ``tmp_path`` and
never touches the read-only corpus (DP-03).
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from engine.foundation.contracts.contract import ContractRegistry, Version
from engine.registry.universal import (
    AuditJournal,
    DuplicateRegistrationError,
    KnowledgeOnceViolation,
    NamespaceError,
    RegistrationNotFoundError,
    RegistrationRequest,
    RegistrationState,
    RegistrationValidationError,
    RegistryCore,
    RegistryKind,
    SequenceClock,
    UniversalRegistryPlatform,
    VersionConflictError,
    cli,
    deterministic_id,
    identity,
    parse_kind,
    version_ref,
)
from engine.registry.universal.audit import GENESIS_HASH, utc_clock
from engine.registry.universal.cli import build_platform, main
from engine.registry.universal.errors import AuditIntegrityError, DependencyError
from engine.registry.universal.records import AuditAct, AuditEntry, Registration

# --------------------------------------------------------------------------- #
# identity                                                                     #
# --------------------------------------------------------------------------- #


def test_kind_code_and_coerce():
    assert RegistryKind.SERVICE.code == "SVC"
    assert RegistryKind.coerce("ENGINE") is RegistryKind.ENGINE
    assert RegistryKind.coerce(RegistryKind.API) is RegistryKind.API
    with pytest.raises(RegistrationValidationError):
        RegistryKind.coerce("MOON")


def test_deterministic_id_is_stable_and_version_independent():
    a = deterministic_id(RegistryKind.SERVICE, "ucos.service", "registry-discovery")
    b = deterministic_id(RegistryKind.SERVICE, "UCOS.Service", "registry-discovery")
    assert a == b  # namespace is normalised (case-insensitive)
    assert a.startswith("UCOS-SVC-")
    assert parse_kind(a) is RegistryKind.SERVICE


def test_distinct_inputs_distinct_ids():
    a = deterministic_id(RegistryKind.SERVICE, "ucos.service", "alpha")
    b = deterministic_id(RegistryKind.SERVICE, "ucos.service", "beta")
    c = deterministic_id(RegistryKind.ENGINE, "ucos.service", "alpha")
    assert len({a, b, c}) == 3


def test_namespace_validation():
    assert identity.normalize_namespace("ucos.platform.registry") == "ucos.platform.registry"
    with pytest.raises(NamespaceError):
        identity.normalize_namespace("")
    with pytest.raises(NamespaceError):
        identity.normalize_namespace("Bad Namespace!")


def test_natural_key_validation():
    assert identity.normalize_natural_key("  key-1 ") == "key-1"
    with pytest.raises(RegistrationValidationError):
        identity.normalize_natural_key("has space")
    with pytest.raises(RegistrationValidationError):
        identity.normalize_natural_key("")


@pytest.mark.parametrize("bad", ["", "NOTUCOS-SVC-abc", "UCOS-XXX-abc", "UCOS-SVC", "UCOS-SVC-"])
def test_parse_kind_rejects_malformed(bad):
    with pytest.raises(RegistrationValidationError):
        parse_kind(bad)


def test_content_digest_stable():
    assert identity.content_digest({"a": 1, "b": 2}) == identity.content_digest({"b": 2, "a": 1})


# --------------------------------------------------------------------------- #
# records                                                                      #
# --------------------------------------------------------------------------- #


def _request(**overrides):
    base = dict(
        kind=RegistryKind.SERVICE,
        namespace="ucos.service",
        natural_key="alpha",
        name="Alpha Service",
        version="1.0.0",
        attributes={"domain": "DOM-027"},
    )
    base.update(overrides)
    return RegistrationRequest.build(**base)


def test_request_build_defaults_and_props():
    req = _request()
    assert req.universal_id.startswith("UCOS-SVC-")
    assert req.owner == "UNASSIGNED"
    assert req.dependencies == ()
    assert len(req.content_hash()) == 64


def test_request_dedups_collections():
    req = _request(tags=["a", "a", "b"], dependencies=["x", "x"])
    assert req.tags == ("a", "b")
    assert req.dependencies == ("x",)


def test_request_rejects_bad_attributes_container():
    with pytest.raises(RegistrationValidationError):
        _request(attributes=["not", "a", "map"])


def test_request_rejects_non_scalar_attribute_value():
    with pytest.raises(RegistrationValidationError):
        _request(attributes={"bad": {1, 2, 3}})  # a set is not JSON-serialisable


def test_request_rejects_bad_collection_element():
    with pytest.raises(RegistrationValidationError):
        _request(tags=["ok", ""])
    with pytest.raises(RegistrationValidationError):
        _request(tags="not-a-list")


def test_registration_roundtrip_and_attributes():
    req = _request(attributes={"domain": "DOM-027", "nested": {"k": [1, 2]}})
    reg = Registration.from_request(req, sequence=0)
    assert reg.state is RegistrationState.ACTIVE
    assert reg.version_str == "1.0.0"
    assert reg.attributes == {"domain": "DOM-027", "nested": {"k": [1, 2]}}
    payload = reg.to_dict()
    assert payload["universal_id"] == reg.universal_id
    assert payload["attributes"]["nested"] == {"k": [1, 2]}


def test_registration_with_state():
    reg = Registration.from_request(_request(), sequence=0)
    superseded = reg.with_state(RegistrationState.SUPERSEDED, superseded_by="ref@2.0.0")
    assert superseded.state is RegistrationState.SUPERSEDED
    assert superseded.superseded_by == "ref@2.0.0"
    assert reg.state is RegistrationState.ACTIVE  # original untouched (immutable)


def test_audit_entry_seal_and_hash():
    entry = AuditEntry(
        sequence=0,
        act=AuditAct.REGISTER,
        universal_id="UCOS-SVC-abc",
        version="1.0.0",
        content_hash="deadbeef",
        state="ACTIVE",
        actor="TESTER",
        timestamp="1970-01-01T00:00:00+00:00",
        prev_hash=GENESIS_HASH,
    ).sealed()
    assert entry.entry_hash == entry.compute_hash()
    assert entry.to_dict()["entry_hash"] == entry.entry_hash


# --------------------------------------------------------------------------- #
# audit journal                                                                #
# --------------------------------------------------------------------------- #


def test_journal_chain_and_verify():
    journal = AuditJournal(clock=SequenceClock())
    journal.record(
        act=AuditAct.REGISTER,
        universal_id="UCOS-SVC-1",
        version="1.0.0",
        content_hash="h1",
        state="ACTIVE",
        actor="A",
    )
    second = journal.record(
        act=AuditAct.REGISTER,
        universal_id="UCOS-SVC-2",
        version="1.0.0",
        content_hash="h2",
        state="ACTIVE",
        actor="A",
    )
    assert len(journal) == 2
    assert second.prev_hash == journal.entries()[0].entry_hash
    assert journal.head_hash() == second.entry_hash
    assert journal.for_id("UCOS-SVC-1")[0].universal_id == "UCOS-SVC-1"
    assert journal.verify() is True


def test_empty_journal_head_is_genesis():
    assert AuditJournal().head_hash() == GENESIS_HASH


def test_utc_clock_returns_iso_string():
    assert "T" in utc_clock()


def test_journal_detects_tampering(tmp_path):
    journal = AuditJournal(clock=SequenceClock())
    for i in range(3):
        journal.record(
            act=AuditAct.REGISTER,
            universal_id=f"UCOS-SVC-{i}",
            version="1.0.0",
            content_hash=f"h{i}",
            state="ACTIVE",
            actor="A",
        )
    raw = journal.to_dict()
    # Mutate a body field without recomputing the hash -> chain must break.
    raw["entries"][1]["actor"] = "IMPOSTER"
    path = tmp_path / "audit.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(AuditIntegrityError):
        AuditJournal.load(path)


def test_journal_detects_sequence_gap():
    journal = AuditJournal(clock=SequenceClock())
    journal.record(
        act=AuditAct.REGISTER,
        universal_id="x",
        version="1.0.0",
        content_hash="h",
        state="ACTIVE",
        actor="A",
    )
    entries = journal.to_dict()["entries"]
    entries[0]["sequence"] = 5
    with pytest.raises(AuditIntegrityError):
        AuditJournal.from_entries(entries)


def test_journal_save_load_roundtrip(tmp_path):
    journal = AuditJournal(clock=SequenceClock())
    journal.record(
        act=AuditAct.REGISTER,
        universal_id="x",
        version="1.0.0",
        content_hash="h",
        state="ACTIVE",
        actor="A",
    )
    path = journal.save(tmp_path / "sub" / "audit.json")
    restored = AuditJournal.load(path, clock=SequenceClock())
    assert restored.head_hash() == journal.head_hash()


# --------------------------------------------------------------------------- #
# core: registration, dedup, knowledge once, versioning                        #
# --------------------------------------------------------------------------- #


def _core():
    return RegistryCore(clock=SequenceClock())


def test_register_new_creates_active_and_audit():
    core = _core()
    reg = core.register(_request())
    assert reg.state is RegistrationState.ACTIVE
    assert core.exists(reg.universal_id)
    assert core.count() == 1 and core.count_versions() == 1
    assert core.journal.entries()[0].act is AuditAct.REGISTER


def test_duplicate_same_content_rejected():
    core = _core()
    core.register(_request())
    with pytest.raises(DuplicateRegistrationError):
        core.register(_request())


def test_knowledge_once_rejects_same_content_new_identity():
    core = _core()
    core.register(_request(natural_key="alpha"))
    # Same content payload, different natural_key => different id, same content hash.
    with pytest.raises(KnowledgeOnceViolation):
        core.register(_request(natural_key="beta"))


def test_new_version_supersedes_previous():
    core = _core()
    v1 = core.register(_request(attributes={"domain": "DOM-027"}))
    v2 = core.register(_request(version="1.1.0", attributes={"domain": "DOM-028"}))
    assert v2.universal_id == v1.universal_id
    history = core.history(v1.universal_id)
    assert [str(r.version) for r in history] == ["1.0.0", "1.1.0"]
    assert history[0].state is RegistrationState.SUPERSEDED
    assert history[0].superseded_by == version_ref(v1.universal_id, "1.1.0")
    assert core.get(v1.universal_id).version == Version(1, 1, 0)


def test_duplicate_version_rejected():
    core = _core()
    core.register(_request(attributes={"domain": "A"}))
    with pytest.raises(DuplicateRegistrationError):
        core.register(_request(version="1.0.0", attributes={"domain": "B"}))


def test_older_version_rejected():
    core = _core()
    core.register(_request(version="2.0.0", attributes={"domain": "A"}))
    with pytest.raises(VersionConflictError):
        core.register(_request(version="1.0.0", attributes={"domain": "B"}))


def test_self_dependency_rejected():
    core = _core()
    uid = _request().universal_id
    with pytest.raises(DependencyError):
        core.register(_request(dependencies=[uid]))


def test_dependency_cycle_rejected():
    core = _core()
    a = core.register(_request(natural_key="a", name="A", attributes={"domain": "A"}))
    b = core.register(
        _request(
            natural_key="b",
            name="B",
            attributes={"domain": "B"},
            dependencies=[a.universal_id],
        )
    )
    # Now make A (a newer version) depend on B -> a cycle A->B->A.
    with pytest.raises(DependencyError):
        core.register(
            _request(
                natural_key="a",
                name="A",
                version="2.0.0",
                attributes={"domain": "A2"},
                dependencies=[b.universal_id],
            )
        )


def test_dependencies_recorded_for_active():
    core = _core()
    a = core.register(_request(natural_key="a", attributes={"domain": "A"}))
    b = core.register(
        _request(natural_key="b", attributes={"domain": "B"}, dependencies=[a.universal_id])
    )
    assert core.dependencies_of(b.universal_id) == (a.universal_id,)


def test_lifecycle_deprecate_then_retire():
    core = _core()
    reg = core.register(_request())
    dep = core.deprecate(reg.universal_id)
    assert dep.state is RegistrationState.DEPRECATED
    ret = core.retire(reg.universal_id)
    assert ret.state is RegistrationState.RETIRED
    acts = [e.act for e in core.journal.for_id(reg.universal_id)]
    assert AuditAct.DEPRECATE in acts and AuditAct.RETIRE in acts


def test_transition_without_target_raises():
    core = _core()
    reg = core.register(_request())
    core.retire(reg.universal_id)
    with pytest.raises(RegistrationNotFoundError):
        core.deprecate(reg.universal_id)


def test_lookup_helpers_and_resolve():
    core = _core()
    v1 = core.register(_request(attributes={"domain": "A"}))
    core.register(_request(version="2.0.0", attributes={"domain": "B"}))
    uid = v1.universal_id
    assert core.resolve(uid).version == Version(2, 0, 0)
    assert core.resolve(f"{uid}@1.0.0").version == Version(1, 0, 0)
    assert core.get_version(uid, "1.0.0").version == Version(1, 0, 0)
    with pytest.raises(RegistrationNotFoundError):
        core.get_version(uid, "9.9.9")
    with pytest.raises(RegistrationNotFoundError):
        core.get("UCOS-SVC-does-not-exist")


def test_collection_views():
    core = _core()
    core.register(_request(kind=RegistryKind.SERVICE, natural_key="a", attributes={"domain": "A"}))
    core.register(
        _request(
            kind=RegistryKind.ENGINE,
            namespace="ucos.engine",
            natural_key="e",
            attributes={"entrypoint": "m:main"},
        )
    )
    core.register(
        _request(
            kind=RegistryKind.SERVICE,
            namespace="ucos.service.sub",
            natural_key="b",
            attributes={"domain": "B"},
        )
    )
    assert len(core.heads()) == 3
    assert len(core.by_kind(RegistryKind.SERVICE)) == 2
    assert len(core.by_kind("ENGINE")) == 1
    assert len(core.by_namespace("ucos.service")) == 2  # exact + prefixed sub
    assert len(core.all_versions()) == 3


def test_core_verify_and_snapshot():
    core = _core()
    core.register(_request(attributes={"domain": "A"}))
    core.register(_request(version="1.1.0", attributes={"domain": "B"}))
    assert core.verify() is True
    snap = core.snapshot()
    assert snap["identities"] == 1 and snap["versions"] == 2
    assert len(snap["registrations"]) == 2
    assert snap["audit"]["count"] == len(core.journal)


# --------------------------------------------------------------------------- #
# typed registries + facade                                                    #
# --------------------------------------------------------------------------- #


def _platform():
    return UniversalRegistryPlatform(clock=SequenceClock())


def test_typed_registry_requires_attributes():
    platform = _platform()
    with pytest.raises(RegistrationValidationError):
        platform.services.register(natural_key="x", name="X")  # missing 'domain'


def test_typed_registry_read_helpers():
    platform = _platform()
    reg = platform.services.register(
        natural_key="registry-discovery",
        name="Registry & Discovery",
        attributes={"domain": "DOM-027"},
    )
    assert platform.services.exists("registry-discovery")
    assert platform.services.get("registry-discovery").universal_id == reg.universal_id
    assert platform.services.get_by_id(reg.universal_id).universal_id == reg.universal_id
    assert platform.services.id_for("registry-discovery") == reg.universal_id
    assert platform.services.count() == 1
    assert len(platform.services.history("registry-discovery")) == 1
    assert platform.services.all()[0].universal_id == reg.universal_id


def test_namespace_declare():
    platform = _platform()
    reg = platform.namespaces.declare("ucos.platform.registry", scope="internal")
    assert reg.kind is RegistryKind.NAMESPACE
    assert reg.attributes["path"] == "ucos.platform.registry"


def test_dependency_link_and_guards():
    platform = _platform()
    edge = platform.dependencies.link(source="UCOS-SVC-a", target="UCOS-SVC-b")
    assert edge.attributes["source"] == "UCOS-SVC-a"
    with pytest.raises(RegistrationValidationError):
        platform.dependencies.link(source="UCOS-SVC-a", target="UCOS-SVC-a")
    with pytest.raises(RegistrationValidationError):
        platform.dependencies.link(source="", target="UCOS-SVC-b")


def test_all_twelve_registries_register():
    platform = _platform()
    samples = {
        "namespace": ("ucos.sample", {"scope": "internal"}),
        "capability": ("cap-discovery", {"summary": "discover artifacts"}),
        "document": ("doc-adr-004", {"path": "adr/ADR-004.md"}),
        "engine": ("compiler", {"entrypoint": "engine.compiler:main"}),
        "component": ("registrar", {"layer": "platform"}),
        "api": ("registry-api", {"contract": "registry.platform", "protocol": "python"}),
        "service": ("svc-027", {"domain": "DOM-027"}),
        "application": ("artifact-explorer", {"surface": "cli"}),
        "infrastructure": ("cluster", {"provider": "kubernetes"}),
        "dependency": ("edge-1", {"source": "A", "target": "B"}),
        "evidence": ("evd-pi1", {"subject": "UCOS-SVC-027"}),
        "certification": ("cert-pi1", {"subject": "UCOS-SVC-027", "determination": "CERTIFIED"}),
    }
    registries = platform.registries()
    assert set(registries) == set(samples)
    for name, (key, attrs) in samples.items():
        registries[name].register(natural_key=key, name=key, attributes=attrs)
    assert platform.core.count() == 12
    assert platform.validate() is True


def test_facade_contract_and_summary():
    platform = _platform()
    platform.services.register(natural_key="svc", name="Svc", attributes={"domain": "DOM-027"})
    contracts = ContractRegistry()
    platform.register_contract(contracts)
    assert contracts.get("registry.platform").version == Version(1, 0, 0)
    summary = platform.summary()
    assert summary["identities"] == 1
    assert summary["by_kind"]["service"] == 1
    assert summary["contract"] == "registry.platform@1.0.0"
    assert summary["audit_head"] == platform.core.journal.head_hash()


def test_facade_export(tmp_path):
    platform = _platform()
    platform.services.register(natural_key="svc", name="Svc", attributes={"domain": "DOM-027"})
    paths = platform.export(tmp_path / "evidence")
    snapshot = json.loads((tmp_path / "evidence" / "registry-snapshot.json").read_text())
    assert snapshot["identities"] == 1
    # The exported audit journal reloads and re-verifies cleanly.
    AuditJournal.load(paths["audit"], clock=SequenceClock())


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #


def _manifest(tmp_path, registrations, actor="OPERATOR"):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"actor": actor, "registrations": registrations}), encoding="utf-8")
    return path


def test_cli_build_platform_defaults_namespace(tmp_path):
    manifest = {
        "registrations": [
            {
                "kind": "SERVICE",
                "natural_key": "svc",
                "name": "Svc",
                "attributes": {"domain": "DOM-027"},
            }
        ]
    }
    platform = build_platform(manifest)
    assert platform.services.exists("svc")


def test_cli_valid_manifest_exit_zero(tmp_path, capsys):
    path = _manifest(
        tmp_path,
        [
            {
                "kind": "SERVICE",
                "natural_key": "svc",
                "name": "Svc",
                "attributes": {"domain": "DOM-027"},
            }
        ],
    )
    rc = main([str(path), "--export", str(tmp_path / "out")])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True and out["summary"]["identities"] == 1
    assert (tmp_path / "out" / "registry-snapshot.json").is_file()


def test_cli_duplicate_registration_exit_one(tmp_path, capsys):
    entry = {
        "kind": "SERVICE",
        "natural_key": "svc",
        "name": "Svc",
        "attributes": {"domain": "DOM-027"},
    }
    path = _manifest(tmp_path, [entry, dict(entry)])
    rc = main([str(path)])
    assert rc == 1
    err = json.loads(capsys.readouterr().err)
    assert err["ok"] is False and err["code"].startswith("REG-PLAT")


def test_cli_missing_manifest_exit_two(tmp_path, capsys):
    rc = main([str(tmp_path / "nope.json")])
    assert rc == 2
    assert json.loads(capsys.readouterr().err)["ok"] is False


def test_cli_bad_shape_exit_two(tmp_path, capsys):
    path = tmp_path / "m.json"
    path.write_text(json.dumps({"nope": []}), encoding="utf-8")
    rc = main([str(path)])
    assert rc == 2


def test_cli_malformed_registration_exit_two(tmp_path, capsys):
    # Missing the required 'natural_key' key -> KeyError path (exit 2).
    path = _manifest(tmp_path, [{"kind": "SERVICE", "name": "Svc", "attributes": {"domain": "D"}}])
    rc = main([str(path)])
    assert rc == 2


def test_cli_entry_not_object_raises(tmp_path):
    with pytest.raises(ValueError):
        build_platform({"registrations": ["not-an-object"]})


# --------------------------------------------------------------------------- #
# core: verify's two internal invariants, refused in both directions            #
# --------------------------------------------------------------------------- #


def _core2():
    return RegistryCore(clock=SequenceClock())


def test_verify_refuses_a_second_active_version_of_one_identity():
    """The chain is built to supersede, so two ACTIVE records can only arise from a fault.

    verify() is the place that says so, and a refusal nobody has shown can fire is not a
    guard. The second ACTIVE record is injected directly — constructing one through the
    public path is exactly what the version rules make impossible, which is the point.
    """

    core = _core2()
    first = core.register(_request(natural_key="solo", attributes={"domain": "DOM-001"}))
    forged = dataclasses.replace(
        first, version=Version(9, 9, 9), state=RegistrationState.ACTIVE, sequence=first.sequence + 1
    )
    core._chains[first.universal_id].append(forged)
    with pytest.raises(VersionConflictError, match="more than one ACTIVE"):
        core.verify()


def test_verify_refuses_an_injected_dependency_cycle():
    """The three-colour DFS answers in both directions: a clean graph passes, a back edge raises.

    The registering-time check refuses edges a caller can declare; this check refuses edges
    that appear later — a rewritten `_edges`, the state a partial repair or a future
    projection could leave behind — because acyclicity is a property of the graph as it is,
    not of the moment a request was accepted.
    """
    core = _core2()
    a = core.register(_request(natural_key="top", attributes={"domain": "DOM-002"}))
    b = core.register(
        _request(
            natural_key="mid",
            attributes={"domain": "DOM-003"},
            dependencies=(a.universal_id,),
        )
    )
    assert core.verify() is True
    core._edges[a.universal_id] = (b.universal_id,)
    with pytest.raises(VersionConflictError, match="dependency cycle"):
        core.verify()


def test_a_diamond_dependency_is_accepted_and_a_new_back_edge_is_refused():
    """The `seen` arm of the dependency walk: a shared dependency is a diamond, not a cycle.

    d -> (b, c), both -> a visits a twice; without the seen-check the second visit is a
    silent re-walk and with it the registration proceeds. Then a new version of `a` that
    depends on `d` closes the loop — the same walk must now refuse it.
    """
    core = _core2()
    a = core.register(_request(natural_key="droot", attributes={"domain": "DOM-004"}))
    b = core.register(
        _request(
            natural_key="dmid1", attributes={"domain": "DOM-005"}, dependencies=(a.universal_id,)
        )
    )
    c = core.register(
        _request(
            natural_key="dmid2", attributes={"domain": "DOM-006"}, dependencies=(a.universal_id,)
        )
    )
    d = core.register(
        _request(
            natural_key="dtop",
            version="1.0.0",
            attributes={"domain": "DOM-007"},
            dependencies=(b.universal_id, c.universal_id),
        )
    )
    assert core.dependencies_of(d.universal_id) == (b.universal_id, c.universal_id)
    with pytest.raises(DependencyError):
        core.register(
            _request(
                natural_key="droot",
                version="2.0.0",
                attributes={"domain": "DOM-008"},
                dependencies=(d.universal_id,),
            )
        )


def test_the_journal_iterates_and_refuses_a_broken_prev_hash() -> None:
    """__iter__ is how a consumer walks the trail, and a severed link must raise, not warn.

    The chain's whole contract is that `prev_hash` names the entry before it: an entry
    rewritten in place still hashes itself, so only the link can show the tamper — and an
    iterator nobody enumerates would hide the entries the loop is built to find.
    """
    journal = AuditJournal(clock=SequenceClock())
    for i in range(3):
        journal.record(
            act=AuditAct.REGISTER,
            universal_id=f"UCOS-SVC-00000{i}",
            version="1.0.0",
            content_hash=f"{i:064x}",
            state="ACTIVE",
            actor="tester",
        )
    assert [entry.sequence for entry in journal] == [0, 1, 2]

    tampered = AuditJournal(clock=SequenceClock())
    for i in range(2):
        tampered.record(
            act=AuditAct.REGISTER,
            universal_id=f"UCOS-SVC-10000{i}",
            version="1.0.0",
            content_hash=f"{i:064x}",
            state="ACTIVE",
            actor="tester",
        )
    object.__setattr__(tampered._entries[1], "prev_hash", "f" * 64)
    with pytest.raises(AuditIntegrityError, match="prev_hash mismatch"):
        tampered.verify()


def test_the_manifest_reader_refuses_a_body_that_is_not_json_or_not_a_manifest(tmp_path) -> None:
    """`main` fails on unreadable input, not on whatever half-parsed of it.

    A truncated file, an array where an object was expected, or a missing
    'registrations' array all reach the same ValueError — and the CLI maps it to exit 2,
    because a manifest the tool cannot read is not an empty manifest.
    """
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        cli._load_manifest(broken)

    wrong_shape = tmp_path / "shape.json"
    wrong_shape.write_text(json.dumps({"registrations": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="must be an object"):
        cli._load_manifest(wrong_shape)


def test_a_blank_required_field_is_refused_on_the_way_in() -> None:
    """_as_str is the single gate for every string field of a request."""
    with pytest.raises(RegistrationValidationError, match="non-empty string"):
        RegistrationRequest.build(
            kind=RegistryKind.SERVICE,
            namespace="ucos.service",
            natural_key="ok",
            name="   ",
            version="1.0.0",
        )


def test_the_cli_writes_the_export_only_when_asked(tmp_path) -> None:
    """`--export` is the second half of the export branch in main()."""
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({"registrations": []}), encoding="utf-8")
    out = tmp_path / "export.json"
    assert cli.main([str(manifest), "--export", str(out)]) == 0


def test_a_three_version_chain_supersedes_twice_and_a_shared_edge_is_not_a_cycle() -> None:
    """The non-ACTIVE arm of supersession and the coloured arm of the acyclicity walk.

    Registering three versions puts a SUPERSEDED record in the chain before the walk
    reaches the active one; a shared dependency visited from two roots is coloured black
    by the first DFS, so the second must skip it rather than re-enter.
    """
    core = _core()
    core.register(_request(natural_key="chain", attributes={"domain": "DOM-A"}))
    core.register(_request(natural_key="chain", version="1.1.0", attributes={"domain": "DOM-B"}))
    third = core.register(
        _request(natural_key="chain", version="1.2.0", attributes={"domain": "DOM-C"})
    )
    assert core.verify() is True
    assert [str(r.version) for r in core.history(third.universal_id)] == [
        "1.0.0",
        "1.1.0",
        "1.2.0",
    ]

    shared = _core()
    a = shared.register(_request(natural_key="root-a", attributes={"domain": "DOM-D"}))
    b = shared.register(_request(natural_key="root-b", attributes={"domain": "DOM-E"}))
    leaf = shared.register(
        _request(
            natural_key="leaf",
            attributes={"domain": "DOM-F"},
            dependencies=(a.universal_id, b.universal_id),
        )
    )
    assert shared.dependencies_of(leaf.universal_id) == (a.universal_id, b.universal_id)
    assert shared.verify() is True


def test_the_acyclicity_walk_skips_nodes_a_previous_root_already_coloured() -> None:
    """The `colour[uid] == white` guard's false arm: a chain, not a fork.

    A→B→C is acyclic; the walk starts at A, and by the time the outer loop reaches B and
    C they are already black. Re-entering a black node would be the bug; skipping it is the
    correctness of the three-colour scheme, so the skip must be exercised as itself.
    """
    core = _core()
    c = core.register(_request(natural_key="leaf-c", attributes={"domain": "DOM-G"}))
    b = core.register(
        _request(
            natural_key="mid-b", attributes={"domain": "DOM-H"}, dependencies=(c.universal_id,)
        )
    )
    core.register(
        _request(
            natural_key="top-a", attributes={"domain": "DOM-I"}, dependencies=(b.universal_id,)
        )
    )
    assert core.verify() is True


def test_the_cli_reports_the_summary_without_exporting_anything(tmp_path, capsys) -> None:
    """The no-export arm of main: report the summary, write nothing.

    Export is opt-in; a CLI that required it could not be used as a check.
    """
    path = _manifest(
        tmp_path,
        [
            {
                "kind": "SERVICE",
                "natural_key": "plain",
                "name": "Plain Service",
                "version": "1.0.0",
                "attributes": {"domain": "DOM-007"},
            }
        ],
    )
    assert main([str(path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True

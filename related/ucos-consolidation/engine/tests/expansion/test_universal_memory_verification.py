"""WP-UCDA-025 — Universal Persistent Evolutionary Graph Memory verification (ADR-0013).

Phase 4 Step 7 names six memory properties that must hold, and Step 3 names four things that
must NOT have been built. This suite proves both halves, because a memory capability that
quietly became a memory engine would satisfy the first half and violate the whole point.

    memory persistence          — memory outlives the process, because it is resolved from
                                  persisted governed records rather than runtime state
    lineage preservation        — nothing is deleted; supersession and resurrection preserve
                                  the superseded state as resolvable
    historical reconstruction   — a past state can be rebuilt, repeatably and byte-identically
    no duplicate truth          — every remembered value cites exactly one governed record
    no duplicate authority      — every layer has exactly one owner, and this projection is
                                  not one of them
    no orphan memory            — no entry exists without a subject, a layer, an owner and a
                                  source

Openness is asserted the same way the expansion suite asserts it: by admitting something the
repository has never named and checking ``kernel_source_fingerprint()`` is unchanged.
"""

from __future__ import annotations

import hashlib
import json
import os

import pytest

from engine.ceu.existence import ExistenceRegistry, ExistenceUnit
from engine.kernel.compliance import kernel_source_fingerprint
from engine.lineage.memory import (
    ACCESS_MODES,
    MODE_LIST_MATCH,
    MemoryAccess,
    MemoryDeclaration,
    MemoryLayer,
    duplicate_owners,
    load_declaration,
    owners,
    reconstruct,
    resolve,
    to_document,
)
from engine.lineage.model import LineageError
from engine.lineage.sources import repo_root

# A subject the corpus records across several layers, and one it has never heard of.
KNOWN_ARTIFACT = "UCOS-BOOK-000000"
DEEP_IDENTITY_SUBJECT = "UCOS-CANONICALOWN-000001"
KNOWN_KNOWLEDGE = "UCKO-ANTI-0001"
UNKNOWN_SUBJECT = "ZZZ-NO-SUCH-SUBJECT-IN-ANY-REALITY-99999"


# -- the declaration itself -------------------------------------------------- #


def test_the_layer_set_is_data_not_code():
    """The seven layers are DECLARED, so an eighth needs no code change (ADR-0007)."""
    declaration = load_declaration()
    assert declaration.declaration_id == "ULP-MEMORY-LAYERS-001"
    assert declaration.names == (
        "identity",
        "context",
        "relationship",
        "knowledge",
        "evidence",
        "decision",
        "evolution",
    )
    # The declaration lives in a data file, not in a Python literal
    here = os.path.dirname(
        os.path.abspath(__import__("engine.lineage.memory", fromlist=["x"]).__file__)
    )
    assert os.path.isfile(os.path.join(here, "memory-layers.json"))


def test_an_eighth_memory_layer_is_admitted_by_declaration_alone():
    """A kind of memory the repository has never named is admitted without a code change."""
    before = kernel_source_fingerprint()
    declaration = load_declaration()
    # A layer over a register that does not exist, of a kind never conceived here
    extended = declaration.extend(
        MemoryLayer(
            layer="sensory-substrate",
            ordinal=99,
            question="What did this perceive, in a modality we have not named?",
            owner="UNKNOWN-FUTURE-OWNER",
            record="00-FUTURE/does-not-exist-yet.json",
            access=MemoryAccess.of(
                {"mode": MODE_LIST_MATCH, "at": ["perceptions"], "match_fields": ["subject"]},
                "sensory-substrate",
            ),
        )
    )
    after = kernel_source_fingerprint()

    assert before == after  # no kernel change admitted this layer
    assert "sensory-substrate" in extended.names
    assert len(extended.names) == len(declaration.names) + 1
    # The owner declaration is untouched — extend returns a new declaration
    assert "sensory-substrate" not in load_declaration().names

    # And the new layer RESOLVES: its record is absent, which is reported, not guessed
    memory = resolve(UNKNOWN_SUBJECT, declaration=extended)
    layer = memory.layer("sensory-substrate")
    assert layer is not None
    assert layer.record_present is False
    assert layer.entries == ()


def test_an_undeclared_access_mode_is_refused_rather_than_silently_empty():
    """An unreadable layer must never masquerade as a layer with nothing recorded."""
    with pytest.raises(LineageError):
        MemoryAccess.of({"mode": "telepathic-broadcast", "at": ["x"]}, "bad-layer")
    assert "telepathic-broadcast" not in ACCESS_MODES


def test_two_layers_may_not_share_one_ordinal():
    """The resolution order is declared, so it may not be ambiguous."""
    with pytest.raises(LineageError):
        MemoryDeclaration.of(
            {
                "declaration_id": "TEST",
                "layers": [
                    {
                        "layer": "a",
                        "ordinal": 1,
                        "question": "?",
                        "owner": "o",
                        "record": "r",
                        "access": {"mode": MODE_LIST_MATCH, "at": ["x"], "match_fields": ["s"]},
                    },
                    {
                        "layer": "b",
                        "ordinal": 1,
                        "question": "?",
                        "owner": "o",
                        "record": "r2",
                        "access": {"mode": MODE_LIST_MATCH, "at": ["x"], "match_fields": ["s"]},
                    },
                ],
            }
        )


# -- STEP 7: memory persistence ---------------------------------------------- #


def test_memory_persistence():
    """Memory outlives the process because every layer resolves from a PERSISTED record.

    This is the property that distinguishes substrate memory from a runtime cache. Nothing
    is resolved from in-process state, so a fresh process remembers the same thing.
    """
    declaration = load_declaration()
    repo = repo_root()

    # Every declared layer names a record that is a real, persisted file
    present = [
        layer.layer
        for layer in declaration.layers
        if os.path.isfile(os.path.join(repo, layer.record))
    ]
    assert present == list(declaration.names), "every declared layer must have a persisted record"

    # A resolution carried out with NO shared state reproduces the same memory
    first = resolve(KNOWN_ARTIFACT)
    second = resolve(KNOWN_ARTIFACT, declaration=load_declaration())
    assert first.as_dict() == second.as_dict()
    assert first.is_remembered

    # The remembered content is genuinely non-empty across multiple owners
    assert len(first.recorded_layers()) >= 3


def test_resolution_creates_no_store():
    """Step 3: no memory store may be created. Resolving must not write anything.

    Proven by content digest, not by trusting the docstring: every governed record is
    hashed before and after a resolution, and the projection's own directory is checked for
    a file that resolving might have dropped there.
    """
    declaration = load_declaration()
    repo = repo_root()

    def digests() -> dict[str, str]:
        found = {}
        for layer in declaration.layers:
            target = os.path.join(repo, layer.record)
            if os.path.isfile(target):
                with open(target, "rb") as handle:
                    found[layer.record] = hashlib.sha256(handle.read()).hexdigest()
        return found

    lineage_dir = os.path.dirname(
        os.path.abspath(__import__("engine.lineage.memory", fromlist=["x"]).__file__)
    )
    before_files = {f for f in os.listdir(lineage_dir) if not f.startswith("__")}
    before = digests()

    resolve(KNOWN_ARTIFACT)
    resolve(KNOWN_KNOWLEDGE)
    resolve(UNKNOWN_SUBJECT)

    assert digests() == before, "resolving a memory must not modify any governed record"
    after_files = {f for f in os.listdir(lineage_dir) if not f.startswith("__")}
    assert after_files == before_files, "resolving a memory must not create a store"


# -- STEP 7: lineage preservation --------------------------------------------- #


def test_lineage_preservation_nothing_is_ever_deleted():
    """Supersession and resurrection PRESERVE the prior state as resolvable.

    Append-only evolution means a superseded unit stays resolvable forever; only its
    admissibility for NEW registrations ends. This asserts the substrate never forgets.
    """
    registry = ExistenceRegistry()
    registry.declare_form("preserved-form", title="Preserved Form", code="PRSV")
    original = registry.register(
        ExistenceUnit(form="preserved-form", key="v1", title="V1", definition="the first")
    )
    successor = registry.register(
        ExistenceUnit(form="preserved-form", key="v2", title="V2", definition="the second")
    )

    registry.supersede(
        original.universal_id,
        successors=[successor.universal_id],
        authority="TEST-AUTHORITY",
    )

    # The superseded unit is STILL resolvable — superseded is not deleted
    assert registry.find(original.universal_id) is not None
    assert registry.resolve(original.universal_id) == original
    assert registry.is_superseded(original.universal_id)
    assert successor.universal_id in registry.successors_of(original.universal_id)

    # Resurrection preserves both the unit and the record of its supersession
    registry.resurrect(original.universal_id, authority="TEST-AUTHORITY")
    assert registry.find(original.universal_id) is not None
    assert not registry.is_superseded(original.universal_id)

    # The append-only journal recorded every transition and still verifies
    assert registry.verify_audit() == []
    assert registry.unlineaged() == ()
    actions = [e.action for e in registry.audit()]
    assert "supersede" in actions and "resurrect" in actions


def test_lineage_preservation_is_surfaced_by_the_projection():
    """Where an owner records supersession, memory surfaces it rather than hiding it."""
    memory = resolve(KNOWN_KNOWLEDGE)
    knowledge = memory.layer("knowledge")
    assert knowledge is not None and knowledge.recorded
    fields = {k for entry in knowledge.entries for k, _ in entry.values}
    # The supersession field is carried through, so a superseded object stays visible
    assert "superseded_by" in fields
    assert "lifecycle" in fields


# -- STEP 7: historical reconstruction ---------------------------------------- #


def test_historical_reconstruction_is_repeatable():
    """A reconstruction that is not repeatable is not a reconstruction."""
    memory = reconstruct(KNOWN_ARTIFACT)
    assert memory.is_remembered
    # to_document emits no timestamp, so the document is replayable
    document = to_document(memory)
    assert "generated_at" not in json.dumps(document)
    assert document["schema"] == "ucos-ulp-subject-memory"
    assert document["memory"] == reconstruct(KNOWN_ARTIFACT).as_dict()


def test_historical_reconstruction_recovers_the_full_identity_series():
    """The whole recorded version series is recoverable, not merely the creation event.

    This is the measured Phase 4 gap: ``engine/lineage/query.py`` reads element [0] of the
    identity history and discards the rest. Memory must recover all of it, in the owner's
    own recorded sequence.
    """
    memory = resolve(DEEP_IDENTITY_SUBJECT)
    identity = memory.layer("identity")
    assert identity is not None and identity.recorded

    # More than one recorded state, i.e. a genuine history and not just a birth
    assert len(identity.entries) > 1
    # Ordered by the OWNER's own sequence field, with no clock involved
    sequences = [e.sequence for e in identity.entries]
    assert sequences == sorted(sequences)
    assert sequences[0] == 1
    # Every state cites the governed record it came from
    assert {e.source for e in identity.entries} == {"00-BOOK/DATA/id-ledger.json"}


def test_a_ceu_registry_reconstructs_from_its_own_document():
    """Entity memory can be rebuilt from Repository Truth alone, and prove it matches.

    ``engine.ceu.existence.reconstruct`` is Steering 022 as a measurement: any divergence
    names state that lived only in memory, which is the hidden runtime state the principle
    forbids. Memory that cannot be rebuilt from the record is not persistent memory.
    """
    from engine.ceu.existence import reconstruct as reconstruct_registry

    registry = ExistenceRegistry()
    registry.declare_form("rebuilt-form", title="Rebuilt Form", code="RBLT")
    registry.register(
        ExistenceUnit(form="rebuilt-form", key="one", title="One", definition="first")
    )
    report = reconstruct_registry(registry)
    # No dimension diverges, i.e. the document was sufficient to rebuild the whole registry
    assert not report.get("divergent"), report
    for key, value in report.items():
        if isinstance(value, bool):
            assert value is True, f"{key} did not reproduce: {report}"


# -- STEP 7: no duplicate truth ---------------------------------------------- #


def test_no_duplicate_truth():
    """Every remembered value cites exactly ONE governed record, and never invents one."""
    declaration = load_declaration()
    for subject in (KNOWN_ARTIFACT, KNOWN_KNOWLEDGE, DEEP_IDENTITY_SUBJECT):
        memory = resolve(subject)
        for layer in memory.layers:
            declared = declaration.layer_of(layer.layer)
            assert declared is not None
            # The layer's source is the declared owner's record — not a copy of it
            assert layer.source == declared.record
            for entry in layer.entries:
                # One entry, one source. A second source would be a forked truth.
                assert entry.source == declared.record
                assert entry.owner == declared.owner


def test_the_projection_declares_itself_derived_and_not_a_source_of_truth():
    """The graph is a projection of canonical truth, never the source of truth."""
    here = os.path.dirname(
        os.path.abspath(__import__("engine.lineage.memory", fromlist=["x"]).__file__)
    )
    with open(os.path.join(here, "memory-layers.json"), encoding="utf-8") as handle:
        document = json.load(handle)
    assert document["authority"].startswith("NONE — DERIVED TRUTH")
    # The declaration states the prohibition it is bound by, so a reader cannot miss it
    for refused in (
        "NO MEMORY STORE",
        "NO MEMORY ENGINE",
        "NO KNOWLEDGE MEMORY AUTHORITY",
        "NO HISTORY AUTHORITY",
    ):
        assert refused in document["authority"]
    assert "$not_a_source_of_truth" in document
    assert to_document(resolve(KNOWN_ARTIFACT))["authority"].startswith("NONE — DERIVED TRUTH")


# -- STEP 7: no duplicate authority ------------------------------------------ #


def test_no_duplicate_authority():
    """Each layer has exactly one owner, and no owner holds one concern twice."""
    declaration = load_declaration()
    owner_map = owners(declaration)

    # Exactly one owner per layer, and every layer accounted for
    assert set(owner_map) == set(declaration.names)
    assert all(isinstance(v, str) and v for v in owner_map.values())

    # No (owner, record) pair answers two layers. Two layers may lawfully share a RECORD
    # while asking different questions; one authority answering one concern twice may not.
    assert duplicate_owners(declaration) == {}


def test_the_projection_claims_no_ownership_of_any_layer():
    """This module must not appear as an owner of the memory it resolves."""
    for owner in owners().values():
        assert "engine/lineage" not in owner
        assert "engine.lineage" not in owner
    # The layers are owned by the pre-existing authorities named in ADR-0013
    joined = " ".join(owners().values())
    for expected in ("REG-AUTO", "UCXI", "UCKP ART-07", "UKDA", "UCDA", "UAUE"):
        assert expected in joined


# -- STEP 7: no orphan memory ------------------------------------------------ #


def test_no_orphan_memory():
    """No entry may exist without a subject, a layer, an owner and a source."""
    declaration = load_declaration()
    declared = set(declaration.names)
    checked = 0
    for subject in (KNOWN_ARTIFACT, KNOWN_KNOWLEDGE, DEEP_IDENTITY_SUBJECT, "DEC-ADR-0013"):
        memory = resolve(subject)
        for entry in memory.entries():
            assert entry.layer in declared, "an entry outside every declared layer is an orphan"
            assert entry.subject == subject
            assert entry.owner, "an entry with no owner is an orphan"
            assert entry.source, "an entry that cannot name its source is an orphan"
            assert entry.values, "an entry carrying no value is an orphan"
            checked += 1
    assert checked > 0


def test_every_declared_layer_answers_even_when_it_remembers_nothing():
    """A layer never silently disappears; empty and absent are different, disclosed facts."""
    memory = resolve(UNKNOWN_SUBJECT)
    declaration = load_declaration()

    # Every declared layer is present in the answer
    assert tuple(x.layer for x in memory.layers) == declaration.names
    # Nothing is remembered, and that is reported rather than raised
    assert memory.is_remembered is False
    assert memory.empty_layers() == declaration.names
    assert memory.entries() == ()
    # 'the owner records nothing' is distinguished from 'the record is absent'
    assert memory.absent_records() == ()


# -- open world for memory itself -------------------------------------------- #


def test_memory_of_an_unknown_subject_never_raises_and_never_guesses():
    """Open world: an unknown subject is a normal answer, not an error."""
    before = kernel_source_fingerprint()
    for subject in (
        UNKNOWN_SUBJECT,
        "",
        "🜁-non-latin-identifier-∞",
        "urn:unknown:reality:7:entity:0",
    ):
        memory = resolve(subject)
        assert memory.subject == str(subject)
        assert tuple(x.layer for x in memory.layers) == load_declaration().names
        for layer in memory.layers:
            for entry in layer.entries:
                # If anything IS matched it must still be sourced — never fabricated
                assert entry.source and entry.owner
    after = kernel_source_fingerprint()
    assert before == after


def test_memory_reads_no_clock():
    """Ordering comes from each owner's recorded sequence, so a resolution is replayable."""
    memory = resolve(DEEP_IDENTITY_SUBJECT)
    document = json.dumps(to_document(memory))
    # The projection emits no time field of its own
    for forbidden in ('"generated_at"', '"resolved_at"', '"now"', '"timestamp"'):
        assert forbidden not in document
    # An owner's own recorded wall-clock string is carried verbatim as opaque data
    identity = memory.layer("identity")
    assert identity is not None
    carried = dict(identity.entries[0].values)
    assert carried["at"], "the owner's recorded 'at' is preserved verbatim, not dropped"

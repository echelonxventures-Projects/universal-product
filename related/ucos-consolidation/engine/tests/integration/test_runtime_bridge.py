"""EPIC-RTE-003 — Runtime Bridge end-to-end integration (Repository Execution Bridge).

Proves the single canonical Runtime Bridge threads a **real, assembled** runtime
unit — produced by the genuine EPIC-003 compiler pipeline and EPIC-005 assembly
engine (see ``conftest``) — through the entire repository lifecycle:
RepositorySubject → Composition → Execution → Validation → Certification →
Acceptance, and Execution Evidence → Knowledge, reusing every engine verbatim and
duplicating no runtime logic. No fixture short-circuits any stage.
"""

from __future__ import annotations

import json

from engine.knowledge.model import KnowledgeKind
from engine.runtime import PublishedPackage, Universe, assemble
from engine.runtime.bridge import RuntimeBridge
from engine.runtime.disclosure import DISCLOSURE_ID, disclosure_present


def _unit(published_package, runtime_signer):
    return assemble(published_package, verify_with=runtime_signer)


def test_real_unit_flows_through_all_bridges(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    subject = {"repository_id": "UCOS-REPO-REAL-0001", "epic_id": "EPIC-RTE-003"}

    bridge = RuntimeBridge()
    record = bridge.run(subject, [unit])

    # composition bridged the real assembled universe
    assert record.composition.universe_ids() == (unit.blueprint_id,)
    # execution modelled the run over the composition
    assert record.run_id.startswith("UCOS-EXEC-RUN-")
    # validation + certification bridged for the real unit
    assert len(record.assurances) == 1
    assurance = record.assurances[0]
    assert assurance.runtime_id == unit.runtime_id
    assert assurance.blueprint_id == unit.blueprint_id
    # acceptance bridged over the assimilated subject
    assert record.acceptance.repository_id == "UCOS-REPO-REAL-0001"
    # execution evidence recorded into knowledge
    assert record.knowledge_object.kind is KnowledgeKind.EVIDENCE
    assert record.evidence_refs()  # non-empty reproducible references
    # EC-1 provisional-state disclosure preserved end to end
    assert disclosure_present(record.disclosure)
    assert record.disclosure["disclosure_id"] == DISCLOSURE_ID
    assert record.verify_integrity()


def test_real_unit_bridge_is_deterministic(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    subject = {"repository_id": "UCOS-REPO-REAL-0001", "epic_id": "EPIC-RTE-003"}

    a = RuntimeBridge().run(subject, [unit])
    b = RuntimeBridge().run(subject, [unit])
    assert a.bridge_id == b.bridge_id
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)


def test_real_unit_bridge_is_replayable(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    subject = {"repository_id": "UCOS-REPO-REAL-0001", "epic_id": "EPIC-RTE-003"}

    bridge = RuntimeBridge()
    record = bridge.run(subject, [unit])
    assert bridge.verify_replay(record).valid
    assert bridge.replay(record).run_id == record.run_id


def test_real_multi_unit_composition_with_dependency(
    published_package, dependency_published_package, runtime_signer
):
    root = assemble(
        published_package,
        verify_with=runtime_signer,
        dependencies=[PublishedPackage.from_published(dependency_published_package)],
    )
    dep = assemble(dependency_published_package, verify_with=runtime_signer)

    subject = {"repository_id": "UCOS-REPO-REAL-0002", "epic_id": "EPIC-RTE-003"}
    universes = [
        Universe.of(dep),
        Universe.of(root, depends_on=[dep.blueprint_id]),
    ]
    record = RuntimeBridge().run(subject, universes)
    assert set(record.composition.universe_ids()) == {root.blueprint_id, dep.blueprint_id}
    assert len(record.assurances) == 2
    assert record.verify_integrity()

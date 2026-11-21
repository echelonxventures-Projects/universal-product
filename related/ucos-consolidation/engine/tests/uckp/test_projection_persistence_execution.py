"""Articles 4, 9, 10, 11: views hold no authority, and technologies are interchangeable.

The interchangeability tests are the load-bearing ones. "Replacing persistence requires
zero constitutional change" is only a claim until two different technologies are shown
to produce the identical universe, so these tests compare digests across all ten
adapters rather than checking that each adapter runs.
"""

from __future__ import annotations

import pytest

from engine.uckp.errors import ExecutionContractError, ProjectionAuthorityError
from engine.uckp.execution import (
    KNOWN_EXECUTION_KINDS,
    OPERATIONS,
    ExecutionRequest,
    PythonExecution,
    build_execution_suite,
    resolve_operation,
    verify_execution_interchangeable,
)
from engine.uckp.persistence import (
    KNOWN_PERSISTENCE_KINDS,
    DatabasePersistence,
    DistributedLedgerPersistence,
    MemoryPersistence,
    build_persistence_suite,
    universe_digest,
    verify_interchangeable,
)
from engine.uckp.projection import (
    KNOWN_PROJECTION_KINDS,
    ProjectedArtifact,
    ProjectionEngine,
    RepositoryProjection,
    assert_no_projection_authority,
    build_projection_engine,
)

# --- projection -----------------------------------------------------------------


def test_ten_projection_kinds_ship_and_the_declared_list_is_derived_from_them():
    """A declared kind nothing implements is a declaration mistaken for a capability."""
    engine = build_projection_engine()
    assert len(engine.kinds()) == 10
    assert set(KNOWN_PROJECTION_KINDS) == set(engine.kinds())
    engine.require_covers(KNOWN_PROJECTION_KINDS)


def test_the_repository_and_the_document_are_both_only_projections():
    engine = build_projection_engine()
    assert "repository" in engine.kinds()
    assert "markdown" in engine.kinds()
    assert "source" in engine.kinds()
    assert "database" in engine.kinds()
    assert "user-interface" in engine.kinds()


def test_no_projected_artifact_may_hold_authority(universe):
    artifacts = universe.projections.project_all(universe.objects())
    assert len(artifacts) == 10
    assert assert_no_projection_authority(artifacts) == ()


def test_an_artifact_claiming_authority_is_refused_at_construction():
    with pytest.raises(ProjectionAuthorityError, match="may not hold authority"):
        ProjectedArtifact(
            projection_id="X",
            kind="json",
            locator="l",
            payload="{}",
            generated_from=("urn:x",),
            authoritative=True,
        )


def test_an_artifact_naming_no_source_object_is_refused():
    """A projection with no source is an independent authority wearing a view's clothes."""
    with pytest.raises(ProjectionAuthorityError, match="names no source object"):
        ProjectedArtifact(projection_id="X", kind="json", locator="l", payload="{}")


def test_every_projection_regenerates_byte_identically(universe):
    objects = universe.objects()
    assert universe.projections.replays_identically(objects)
    for kind in universe.projections.kinds():
        assert universe.projections.regenerates_identically(kind, objects)


def test_every_projection_names_the_objects_it_was_generated_from(universe):
    ids = set(universe.ids())
    for artifact in universe.projections.project_all(universe.objects()):
        assert artifact.generated_from
        assert set(artifact.generated_from) <= ids


def test_projection_payload_digest_is_content_addressed(universe):
    artifact = universe.projections.project("json", universe.objects())
    assert artifact.payload_digest == artifact.payload_digest
    assert artifact.to_dict()["payload_digest"] == artifact.payload_digest
    assert artifact.to_dict()["authoritative"] is False


def test_an_unknown_projection_kind_is_refused(universe):
    with pytest.raises(ProjectionAuthorityError, match="no such projection kind"):
        universe.projections.project("holo-deck", universe.objects())


def test_registering_the_same_kind_twice_is_refused():
    engine = ProjectionEngine((RepositoryProjection(),))
    with pytest.raises(ProjectionAuthorityError, match="already registered"):
        engine.register(RepositoryProjection())


def test_a_projection_kind_that_did_not_exist_before_may_be_registered():
    """Article 17: a future view is admitted by registration."""

    class HoloProjection:
        kind = "holo-deck"
        locator = "projection/holo.json"

        def project(self, objects):
            return ProjectedArtifact(
                projection_id="UCKP-PROJ-HOLO",
                kind=self.kind,
                locator=self.locator,
                payload="{}",
                generated_from=tuple(sorted(o.ucko_id for o in objects)),
            )

    engine = build_projection_engine()
    engine.register(HoloProjection())
    assert "holo-deck" in engine.kinds()


def test_unimplemented_names_declared_kinds_with_no_implementation():
    engine = build_projection_engine()
    assert engine.unimplemented(("holo-deck", "json")) == ("holo-deck",)
    with pytest.raises(ProjectionAuthorityError, match="no implementation"):
        engine.require_covers(("holo-deck",))


def test_the_repository_path_is_derived_from_identity_never_the_reverse(universe):
    obj = universe.registry.require(universe.root_id())
    path = RepositoryProjection.path_for(obj)
    assert obj.local_name in path
    assert obj.taxonomy.category in path


def test_the_projection_engine_describes_itself(universe):
    described = universe.projections.describe()
    assert len(described["kinds"]) == 10
    assert all(entry["implementation"] for entry in described["projections"])


def test_the_projection_document_covers_every_kind(universe):
    document = universe.projections.to_document(universe.objects())
    assert document["counts"]["kinds"] == 10


def test_the_generated_source_and_schema_declare_they_hold_no_authority(universe):
    source = universe.projections.project("source", universe.objects())
    database = universe.projections.project("database", universe.objects())
    assert "no authority" in source.payload
    assert "no authority" in database.payload


# --- persistence ----------------------------------------------------------------


def test_ten_persistence_technologies_ship(universe):
    assert len(universe.persistence) == 10
    kinds = {adapter.describe()["kind"] for adapter in universe.persistence}
    assert kinds == set(KNOWN_PERSISTENCE_KINDS)


def test_every_persistence_technology_round_trips_the_universe_identically(universe):
    """Article 9 / UCKP-INV-11: replacing storage requires zero constitutional change."""
    report = verify_interchangeable(universe.persistence, universe.objects())
    assert report.failures == ()
    assert len(report.kinds()) == 10
    assert report.expected_digest == universe_digest(universe.objects())
    assert len({digest for _, digest in report.observed}) == 1


def test_a_round_trip_preserves_every_object_exactly(universe, tmp_path):
    for adapter in build_persistence_suite(tmp_path / "rt"):
        restored = adapter.round_trip(universe.objects())
        assert universe_digest(restored) == universe_digest(universe.objects())


def test_the_suite_is_constructible_over_a_path_that_does_not_exist_yet(tmp_path):
    """No caller of the abstraction should need to know a database file lives inside it."""
    base = tmp_path / "absent" / "nested"
    assert not base.exists()
    assert len(build_persistence_suite(base)) == 10
    assert base.is_dir()


def test_no_persistence_adapter_owns_knowledge(universe):
    for adapter in universe.persistence:
        described = adapter.describe()
        assert described.get("owns_knowledge") in (False, None)


def test_a_write_returns_a_receipt_naming_what_it_stored(universe, tmp_path):
    adapter = MemoryPersistence()
    receipt = adapter.write(universe.objects())
    assert receipt.count == len(universe.objects())
    assert receipt.digest == universe_digest(universe.objects())
    assert receipt.to_dict()["kind"] == "memory"


def test_the_contract_is_identical_across_technologies(universe, tmp_path):
    for adapter in build_persistence_suite(tmp_path / "contract"):
        adapter.verify_contract(universe.objects())
        assert adapter.capabilities()


def test_the_ledger_chains_and_verifies_its_blocks(universe, tmp_path):
    ledger = DistributedLedgerPersistence(tmp_path / "ledger.jsonl")
    ledger.write(universe.objects())
    assert ledger.verify_chain()
    assert ledger.blocks()
    assert ledger.head()


def test_the_database_adapter_closes_cleanly(universe):
    database = DatabasePersistence()
    database.write(universe.objects())
    assert universe_digest(database.read()) == universe_digest(universe.objects())
    database.close()


def test_interchangeability_report_serializes(universe):
    report = verify_interchangeable(universe.persistence, universe.objects())
    record = report.to_dict()
    assert record["failures"] == []


def test_a_future_storage_technology_is_already_admitted():
    """Article 20: the law must hold for storage media that do not exist yet."""
    assert "future-storage" in KNOWN_PERSISTENCE_KINDS


# --- execution ------------------------------------------------------------------


def test_ten_execution_technologies_ship(universe):
    assert len(universe.execution) == 10
    kinds = {adapter.describe()["kind"] for adapter in universe.execution}
    assert kinds == set(KNOWN_EXECUTION_KINDS)


@pytest.mark.parametrize("operation", sorted(OPERATIONS))
def test_every_declared_operation_is_interchangeable_across_every_technology(universe, operation):
    """Article 10 / UCKP-INV-09: one identical contract, many technologies."""
    subject = universe.root_id()
    request = ExecutionRequest.of(operation, subject)
    report = verify_execution_interchangeable(universe.execution, request, universe.registry)
    assert report.failures == ()
    # ONE CLAIMANT, NINE TRANSCRIPTION TARGETS, AND THE OLD ASSERTION WAS A TAUTOLOGY. This
    # asserted all ten kinds agreed on one digest. They could not do otherwise: no adapter
    # overrides `execute`, so every one called the same `resolve_operation` that produced the
    # expected digest, and the report compared Python's answer to Python's answer once per
    # adapter name. Claiming computation is now an act rather than an inheritance.
    assert report.kinds() == ("python",)
    assert len(report.transcription_only) == 9
    assert len({digest for _, digest in report.observed}) == 1


def test_an_adapter_that_claims_computation_and_disagrees_is_refused(universe):
    """THE CASE THAT COULD NOT EXIST BEFORE, and the reason the check means anything now.

    Every adapter's `execute` calls the base resolver, so comparing all of them compared one
    answer to itself once per name — a report that could not refuse any adapter, present or
    future, which is what engine/conformance scores as ENVELOPE_ONLY.

    This constructs an adapter that CLAIMS computation and returns a different digest. It must be
    named in `failures`. Without this test, `failures == ()` in the test above would be
    indistinguishable from a check that cannot produce a failure at all.
    """
    import dataclasses

    class LyingExecution(PythonExecution):
        kind = "liar"

        def execute(self, request, registry):
            answer = super().execute(request, registry)
            return dataclasses.replace(answer, output_digest="0" * 64)

    report = verify_execution_interchangeable(
        [*universe.execution, LyingExecution()],
        ExecutionRequest.of("universe-seal"),
        universe.registry,
    )
    assert report.interchangeable is False
    assert any(f.startswith("liar:") for f in report.failures), report.failures


def test_a_transcription_target_is_reported_rather_than_counted_as_agreement(universe):
    """A technology that computes nothing is not broken, and is not agreement either."""
    report = verify_execution_interchangeable(
        universe.execution, ExecutionRequest.of("universe-seal"), universe.registry
    )
    assert set(report.transcription_only).isdisjoint(report.kinds())
    assert len(report.transcription_only) + len(report.kinds()) == len(universe.execution)


def test_no_execution_technology_owns_knowledge(universe):
    request = ExecutionRequest.of("universe-seal")
    report = verify_execution_interchangeable(universe.execution, request, universe.registry)
    assert report.knowledge_owners == ()
    for adapter in universe.execution:
        assert not adapter.owns_knowledge()


def test_an_execution_request_is_content_addressed_and_deterministic():
    left = ExecutionRequest.of("describe", "urn:x", depth="1")
    right = ExecutionRequest.of("describe", "urn:x", depth="1")
    assert left.digest() == right.digest()
    assert left.envelope() == right.envelope()
    assert left.to_dict()["operation"] == "describe"


def test_an_unknown_operation_is_refused(universe):
    with pytest.raises(ExecutionContractError):
        resolve_operation(ExecutionRequest.of("no-such-operation"), universe.registry)


def test_every_adapter_can_transcribe_a_request_into_its_own_technology(universe):
    request = ExecutionRequest.of("universe-seal")
    for adapter in universe.execution:
        assert adapter.transcribe(request)


def test_execution_results_carry_the_request_digest_they_answered(universe):
    request = ExecutionRequest.of("universe-seal")
    for adapter in universe.execution:
        result = adapter.execute(request, universe.registry)
        assert result.request_digest == request.digest()
        assert result.to_dict()["operation"] == "universe-seal"


def test_a_future_execution_technology_is_already_admitted():
    assert "future-language" in KNOWN_EXECUTION_KINDS
    assert "future-compute" in KNOWN_EXECUTION_KINDS
    assert "quantum" in KNOWN_EXECUTION_KINDS


def test_the_execution_suite_is_built_not_enumerated_by_the_caller():
    assert len(build_execution_suite()) == len(KNOWN_EXECUTION_KINDS)


def test_interchangeability_needs_two_technologies_to_mean_anything(universe):
    single = universe.execution[:1]
    request = ExecutionRequest.of("universe-seal")
    report = verify_execution_interchangeable(single, request, universe.registry)
    assert len(report.kinds()) == 1


# --- persistence: reading a mechanism nothing has been written to -----------------


def _unwritten_adapters(tmp_path):
    """One instance of every path-bound mechanism, over paths that do not exist yet."""
    from engine.uckp.persistence import (
        CloudPersistence,
        FilesystemPersistence,
        FutureStoragePersistence,
        GitPersistence,
        KnowledgeGraphPersistence,
        ObjectStoragePersistence,
        OfflineArchivePersistence,
    )

    return (
        FilesystemPersistence(tmp_path / "filesystem"),
        GitPersistence(tmp_path / "git"),
        ObjectStoragePersistence(tmp_path / "objects"),
        KnowledgeGraphPersistence(tmp_path / "graph"),
        DistributedLedgerPersistence(tmp_path / "ledger" / "chain.jsonl"),
        CloudPersistence(tmp_path / "cloud"),
        OfflineArchivePersistence(tmp_path / "archive" / "universe.tar.gz"),
        FutureStoragePersistence(tmp_path / "future" / "universe.opaque"),
    )


def test_every_mechanism_reads_an_empty_universe_before_anything_is_written(tmp_path):
    """Absence must read as "nothing", never as a native error escaping the abstraction."""
    for adapter in _unwritten_adapters(tmp_path):
        assert adapter.read() == (), adapter.kind
        assert universe_digest(adapter.read()) == universe_digest(())


def test_an_archive_whose_member_is_not_a_file_reads_as_empty(tmp_path):
    """A directory named ``universe.json`` is not a universe, and must not be read as one."""
    import tarfile

    from engine.uckp.persistence import OfflineArchivePersistence

    path = tmp_path / "foreign.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo(OfflineArchivePersistence._MEMBER)
        info.type = tarfile.DIRTYPE
        archive.addfile(info)
    assert OfflineArchivePersistence(path).read() == ()


def test_the_ledger_detects_a_rewritten_block_and_a_broken_link(tmp_path, universe):
    """Tamper-evidence is the property; a chain check with no reachable False is not one."""
    import json

    path = tmp_path / "chain.jsonl"
    ledger = DistributedLedgerPersistence(path)
    objects = universe.objects()[:3]
    ledger.write(objects)
    ledger.write(objects)
    assert ledger.verify_chain() is True

    lines = path.read_text(encoding="utf-8").splitlines()
    rewritten = json.loads(lines[0])
    rewritten["records"] = []
    path.write_text(
        "\n".join([json.dumps(rewritten, sort_keys=True), *lines[1:]]) + "\n", encoding="utf-8"
    )
    assert ledger.verify_chain() is False

    relinked = json.loads(lines[1])
    relinked["previous"] = "a block that never existed"
    path.write_text(
        "\n".join([lines[0], json.dumps(relinked, sort_keys=True)]) + "\n", encoding="utf-8"
    )
    assert ledger.verify_chain() is False


# --- persistence: the contract check must be able to fail ------------------------


def test_the_contract_check_detects_a_mechanism_that_loses_an_object(universe):
    """A mechanism that returns fewer objects than it was given has lost knowledge."""
    from engine.uckp.errors import PersistenceContractError

    class Lossy(MemoryPersistence):
        kind = "lossy"

        def read(self):
            return super().read()[:-1]

    objects = universe.objects()[:3]
    with pytest.raises(PersistenceContractError, match="did not preserve the universe"):
        Lossy().verify_contract(objects)


def test_the_contract_check_detects_a_mechanism_that_returns_objects_out_of_order(universe):
    """The digest is order-free, so order is exactly what the digest cannot catch."""
    from engine.uckp.errors import PersistenceContractError

    class Shuffling(MemoryPersistence):
        kind = "shuffling"

        def read(self):
            return tuple(reversed(super().read()))

    objects = universe.objects()[:3]
    with pytest.raises(PersistenceContractError, match="altered an object"):
        Shuffling().verify_contract(objects)


# --- execution: a technology that fails, and one that claims to own knowledge -----


def test_an_adapter_reraises_a_contract_error_rather_than_reporting_a_failed_result(universe):
    """ "Unknown operation" is a fault in the request, not a property of the technology."""
    adapter = build_execution_suite()[0]
    with pytest.raises(ExecutionContractError):
        adapter.execute(ExecutionRequest.of("teleport", ""), universe.registry)


def test_an_adapter_reports_an_unexpected_fault_as_a_failed_result(universe, monkeypatch):
    """A transport that breaks must produce a verdict, not a traceback."""

    def explode(request, registry):
        raise ValueError("the resolver fell over")

    monkeypatch.setattr("engine.uckp.execution.resolve_operation", explode)
    adapter = build_execution_suite()[0]
    result = adapter.execute(ExecutionRequest.of("universe-seal", ""), universe.registry)
    assert result.succeeded is False
    assert result.outcome == "failed:ValueError"


def test_interchangeability_reports_a_failing_technology_and_one_claiming_ownership(universe):
    """Both are disqualifying, and both must be named rather than averaged away."""

    class Claiming:
        """An adapter that says it owns the knowledge it merely transports."""

        kind = "claiming"

        def owns_knowledge(self) -> bool:
            return True

        def describe(self) -> dict[str, object]:
            return {"kind": self.kind, "authoritative": True}

        def execute(self, request, registry):
            return build_execution_suite()[0].execute(request, registry)

    class Failing:
        kind = "failing"

        def owns_knowledge(self) -> bool:
            return False

        def describe(self) -> dict[str, object]:
            return {"kind": self.kind, "authoritative": False}

        def execute(self, request, registry):
            from engine.uckp.execution import ExecutionResult

            return ExecutionResult(
                adapter_kind=self.kind,
                operation=request.operation,
                subject=request.subject,
                outcome="failed:Unavailable",
                request_digest=request.digest(),
                output_digest="",
            )

    request = ExecutionRequest.of("universe-seal", "")
    report = verify_execution_interchangeable(
        (build_execution_suite()[0], Claiming(), Failing()), request, universe.registry
    )
    assert report.knowledge_owners == ("claiming",)
    assert any("failing: failed:Unavailable" in failure for failure in report.failures)


def test_a_cloud_mechanism_asserting_a_region_writes_and_locates_inside_it(tmp_path):
    """A REGION IS A LOCALITY ASSERTION, and every test made none.

    ``CloudPersistence`` is constructed without a region everywhere here, so all three of its
    region-aware members answered the same way and the arm that HONOURS one had never run. A
    region is a real constitutional fact — where the universe physically resides — so it has
    to be visible in the locator (an operator reading a receipt must be able to tell two
    regions apart) and it has to change where the bytes go, or two regions would overwrite
    one another in the same directory.
    """
    from engine.uckp.persistence import CloudPersistence

    unlocated = CloudPersistence(tmp_path / "cloud")
    located = CloudPersistence(tmp_path / "cloud", region="eu-west-1")

    assert unlocated.region is None
    assert located.region == "eu-west-1"
    assert unlocated.locator == "cloud://cloud"
    assert located.locator == "cloud://eu-west-1/cloud"

    receipt = located.write(())
    assert receipt.locator == located.locator
    assert (tmp_path / "cloud" / "eu-west-1" / "universe.json").is_file()
    assert not (tmp_path / "cloud" / "universe.json").exists()
    assert located.read() == ()
    assert unlocated.read() == (), "a region is a different location, not a different view"

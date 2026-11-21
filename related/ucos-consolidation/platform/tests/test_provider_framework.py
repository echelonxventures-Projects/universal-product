"""UPA-000011 — the Provider Framework façade, driven end to end.

WHY THIS MODULE EXISTS, STATED AS A MEASUREMENT. Every collaborator of the Universal
Provider Architecture has a suite — registry, lifecycle, discovery, validation,
certification, composition — and the object that WIRES THEM TOGETHER had none. Nothing in
the repository ever constructed a :class:`ProviderFramework`, so the pipeline PC-11 is
written in (discover → admit → realize → validate → certify → activate) existed only as a
sequence of individually-tested parts, and the two properties that only the façade can have
were untested: that a provider which fails certification STOPS, recorded, at the phase it
reached; and that :meth:`ProviderFramework.provider` refuses to hand a non-serving provider
to a consumer. A pipeline is exactly the place where correct parts compose into a wrong
whole, so this is the layer the guarantee lives at.
"""

from __future__ import annotations

import json
from pathlib import Path
from platform.tests.universal_provider_helpers import (
    MEMO_ENTRY_POINT,
    memo_descriptor,
    memo_manifest,
    write_manifest,
)
from platform.universal_provider.certification import CertificationTier
from platform.universal_provider.composition import CompositionStrategy
from platform.universal_provider.errors import (
    ProviderEvidenceError,
    ProviderFrameworkError,
    ProviderLifecycleError,
    ProviderRegistryError,
)
from platform.universal_provider.evidence import (
    MANIFEST_FILENAME,
    build_evidence,
    verify_evidence,
    write_evidence,
)
from platform.universal_provider.framework import (
    PROVIDER_FRAMEWORK_VERSION,
    OnboardingResult,
    ProviderFramework,
)
from platform.universal_provider.lifecycle import ProviderPhase
from platform.universal_provider.registry import ProviderRegistry

import pytest

BROKEN_ENTRY_POINT = "platform.tests.universal_provider_helpers:exploding_factory"


@pytest.fixture
def framework() -> ProviderFramework:
    return ProviderFramework()


def _onboarded(framework: ProviderFramework, **overrides) -> OnboardingResult:
    return framework.onboard(memo_descriptor(**overrides))


# -- composition of the collaborators --------------------------------------------------


def test_the_framework_assembles_a_complete_architecture_by_default(framework):
    assert framework.registry is not None
    assert framework.lifecycle is not None
    assert framework.validator is not None
    assert framework.certifier is not None
    assert framework.discovery is not None
    assert len(framework.constitution_hash()) == 64


def test_every_collaborator_is_injectable(framework):
    registry = ProviderRegistry()
    other = ProviderFramework(registry=registry)
    assert other.registry is registry
    assert other.registry is not framework.registry


# -- the pipeline ----------------------------------------------------------------------


def test_a_conformant_provider_is_onboarded_all_the_way_to_active(framework):
    result = _onboarded(framework)
    assert result.active is True
    assert result.phase is ProviderPhase.ACTIVE
    assert result.realized is True
    assert result.registration_id
    assert result.certificate is not None
    assert result.tier == CertificationTier.UNIVERSAL.value
    assert result.report is not None and result.report.passed
    assert framework.serving() == (result.qualified_id,)
    assert framework.provider(result.qualified_id) is framework.realized(result.qualified_id)


def test_a_provider_that_cannot_be_built_stops_recorded_rather_than_in_limbo(framework):
    """PC-09: onboarding a catalog must not be aborted by one bad member, and PC-11: a
    provider that is not certified may not serve. Both are visible in one outcome."""
    result = _onboarded(framework, entry_point=BROKEN_ENTRY_POINT)
    assert result.active is False
    assert result.realized is False
    assert any("not realized" in reason for reason in result.reasons)
    assert any("activation withheld" in reason for reason in result.reasons)
    assert framework.serving() == ()
    assert framework.realized(result.qualified_id) is None
    with pytest.raises(ProviderLifecycleError):
        framework.provider(result.qualified_id)


def test_an_admission_the_registry_refuses_marks_the_provider_rejected(framework):
    descriptor = memo_descriptor()
    framework.admit(descriptor)
    with pytest.raises(ProviderRegistryError):
        framework.admit(descriptor)
    assert framework.lifecycle.phase(descriptor.qualified_id) is ProviderPhase.REJECTED


def test_onboarding_a_provider_the_registry_refuses_reports_it_rather_than_raising(framework):
    descriptor = memo_descriptor()
    framework.admit(descriptor)
    result = framework.onboard(descriptor)
    assert result.registration_id == ""
    assert any("admission refused" in reason for reason in result.reasons)
    assert result.report is None and result.certificate is None
    assert result.tier == "none"


def test_realization_is_cached_so_one_substrate_is_observed(framework):
    record = framework.admit(memo_descriptor())
    first = framework.realize(record.qualified_id)
    assert framework.realize(record.qualified_id) is first
    assert framework.realized(record.qualified_id) is first


def test_a_provider_that_cannot_be_built_is_still_validated(framework):
    """The report has to distinguish 'not yet built' from 'built wrong', which is the whole
    reason the gates are tri-state."""
    record = framework.admit(memo_descriptor(entry_point=BROKEN_ENTRY_POINT))
    with pytest.raises(ProviderFrameworkError):
        framework.realize(record.qualified_id)
    report = framework.validate(record.qualified_id)
    assert report.indeterminate()
    assert not report.passed


def test_activation_requires_a_certificate_that_authorizes_it(framework):
    record = framework.admit(memo_descriptor(entry_point=BROKEN_ENTRY_POINT))
    with pytest.raises(ProviderLifecycleError, match="PC-11"):
        framework.activate(record.qualified_id)
    framework.validate(record.qualified_id)
    certificate = framework.certify(record.qualified_id)
    assert certificate.authorizes_activation is False
    with pytest.raises(ProviderLifecycleError, match="PC-11"):
        framework.activate(record.qualified_id)


def test_a_certificate_may_be_issued_from_evidence_already_gathered(framework):
    record = framework.admit(memo_descriptor())
    framework.realize(record.qualified_id)
    report = framework.validate(record.qualified_id)
    assert framework.certify(record.qualified_id, report).tier is CertificationTier.UNIVERSAL


# -- withdrawal ------------------------------------------------------------------------


def test_a_suspended_provider_stops_serving_and_can_be_reinstated(framework):
    result = _onboarded(framework)
    assert framework.suspend(result.qualified_id, reason="under review") is (
        ProviderPhase.SUSPENDED
    )
    assert framework.serving() == ()
    with pytest.raises(ProviderLifecycleError):
        framework.provider(result.qualified_id)
    assert framework.activate(result.qualified_id) is ProviderPhase.ACTIVE
    assert framework.serving() == (result.qualified_id,)


def test_retirement_is_terminal_and_releases_the_instance(framework):
    result = _onboarded(framework)
    assert framework.retire(result.qualified_id, reason="superseded") is ProviderPhase.RETIRED
    assert framework.realized(result.qualified_id) is None
    assert framework.serving() == ()


# -- consumers -------------------------------------------------------------------------


def test_a_consumer_resolves_the_highest_serving_version(framework):
    older = _onboarded(framework, version="1.0.0")
    newer = _onboarded(framework, version="2.0.0")
    resolved = framework.resolve(memo_descriptor().provider_id)
    assert resolved is framework.provider(newer.qualified_id)
    assert resolved is not framework.provider(older.qualified_id)


def test_a_composition_may_only_be_built_from_providers_permitted_to_serve(framework):
    """PC-12 rests on PC-11: composing a suspended member would let a withdrawn provider
    serve through a wrapper."""
    first = _onboarded(framework, provider_id="memo.one")
    second = _onboarded(framework, provider_id="memo.two")
    composite = framework.compose(
        "memo.composite",
        memo_descriptor().kind,
        "1.0.0",
        (first.qualified_id, second.qualified_id),
        strategy=CompositionStrategy.FEDERATED,
        name="Composite",
        authority="TEST",
    )
    assert len(composite.members) == 2

    framework.suspend(second.qualified_id)
    with pytest.raises(ProviderLifecycleError):
        framework.compose(
            "memo.composite",
            memo_descriptor().kind,
            "1.0.0",
            (first.qualified_id, second.qualified_id),
        )


def test_a_reference_that_is_not_version_pinned_is_refused(framework):
    with pytest.raises(ProviderRegistryError, match="version-pinned"):
        framework.realize("memo.fixture")


# -- discovery -------------------------------------------------------------------------


def test_a_catalog_directory_is_discovered_and_onboarded_in_order(framework, tmp_path: Path):
    def _manifest(provider_id: str) -> dict:
        payload = memo_manifest()
        payload["identity"] = {**payload["identity"], "provider_id": provider_id}
        return payload

    catalog = tmp_path / "catalog"
    write_manifest(catalog, "a.json", _manifest("memo.alpha"))
    write_manifest(catalog, "b.json", _manifest("memo.beta"))
    assert framework.add_catalog(catalog) is framework

    discovered = framework.discover()
    assert len(discovered.descriptors()) == 2

    results = framework.onboard_discovered(discovered)
    assert [r.qualified_id for r in results] == [d.qualified_id for d in discovered.descriptors()]
    assert all(r.active for r in results)

    # onboarding without a supplied result re-runs discovery for itself
    again = ProviderFramework().add_catalog(catalog).onboard_discovered()
    assert len(again) == 2


# -- the state report ------------------------------------------------------------------


def test_the_framework_state_is_deterministic_and_content_addressed(framework):
    result = _onboarded(framework)
    state = framework.state()
    assert state["framework_version"] == PROVIDER_FRAMEWORK_VERSION
    assert state["constitution_hash"] == framework.constitution_hash()
    assert state["registry"]["providers"] == [result.qualified_id]
    assert state["lifecycle"]["serving"] == [result.qualified_id]
    assert state["lifecycle"]["intact"] is True
    assert state["certification"]["intact"] is True
    assert state["certification"]["tiers"][result.qualified_id] == result.tier
    assert state["realized"] == [result.qualified_id]
    assert framework.state_hash() == framework.state_hash()
    assert len(framework.state_hash()) == 64
    assert json.dumps(state, sort_keys=True)


def test_an_onboarding_result_serialises_everything_it_decided(framework):
    payload = _onboarded(framework).to_dict()
    assert payload["phase"] == ProviderPhase.ACTIVE.value
    assert payload["realized"] is True
    assert payload["validation"]["status"] == "passed"
    assert payload["certificate"]["tier"] == CertificationTier.UNIVERSAL.value
    assert payload["reasons"] == []


def test_an_unrealized_result_serialises_as_a_reported_absence():
    payload = OnboardingResult(
        qualified_id="memo.fixture@1.0.0",
        phase=ProviderPhase.REGISTERED,
        registration_id="",
    ).to_dict()
    assert payload["validation"] is None
    assert payload["certificate"] is None
    assert payload["tier"] == "none"
    assert payload["realized"] is False


def test_the_entry_point_the_fixture_declares_is_the_one_resolved(framework):
    assert memo_descriptor().entry_point == MEMO_ENTRY_POINT


# --------------------------------------------------------------------------- #
# The evidence bundle: what it refuses, and what it reports as unverifiable
# --------------------------------------------------------------------------- #


def test_evidence_requires_the_real_types_and_says_what_it_received(framework, tmp_path) -> None:
    """A DUCK-TYPED FRAMEWORK IS NOT A FRAMEWORK.

    Both entry points read attributes the caller cannot be assumed to have — the framework's
    state, the bundle's artifacts — and an object that merely looks similar would produce a
    bundle that is missing pieces rather than one that failed to be built. The refusal names
    the type that arrived, so the caller is told what they passed instead of what is wrong
    with it.
    """

    with pytest.raises(ProviderEvidenceError) as excinfo:
        build_evidence("not a framework")
    assert excinfo.value.detail["received"] == "str"

    with pytest.raises(ProviderEvidenceError) as excinfo:
        write_evidence({"manifest": {}}, tmp_path)
    assert excinfo.value.detail["received"] == "dict"


def test_an_evidence_bundle_renders_both_halves_of_itself(framework) -> None:
    """``to_dict`` is how a bundle is handed to anything that is not this module. Without it
    a consumer would rebuild the pairing of manifest and artifacts itself, and the two would
    be able to drift — which is exactly what a manifest exists to prevent."""

    bundle = build_evidence(framework)
    rendered = bundle.to_dict()

    assert rendered["manifest"] == bundle.manifest()
    assert rendered["artifacts"] == bundle.artifacts()
    assert rendered == bundle.to_dict()


def test_a_directory_that_cannot_be_created_or_written_is_a_typed_refusal(
    framework, tmp_path
) -> None:
    """AN OSError FROM THE FILESYSTEM IS NOT A PROVIDER FAULT UNTIL IT IS TYPED.

    A caller writing evidence gets one error class from this module whatever went wrong, and
    the path and the reason are carried on it. Letting the raw OSError escape would make the
    caller catch two unrelated exception families to write one bundle, and the message would
    name a path with no indication that evidence was what was being written.
    """

    bundle = build_evidence(framework)

    blocked = tmp_path / "blocked"
    blocked.write_text("a file where a directory must go", encoding="utf-8")
    with pytest.raises(ProviderEvidenceError, match="directory could not be created") as excinfo:
        write_evidence(bundle, blocked)
    assert excinfo.value.detail["directory"] == str(blocked)

    # An artifact name already taken by a DIRECTORY: the target directory is created and
    # the individual write is what fails, which is the second arm.
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    first_artifact = sorted(bundle.artifacts())[0]
    (occupied / first_artifact).mkdir()
    with pytest.raises(ProviderEvidenceError, match="artifact could not be written") as excinfo:
        write_evidence(bundle, occupied)
    assert excinfo.value.detail["path"].endswith(first_artifact)


def test_a_materialized_bundle_that_no_longer_matches_its_manifest_does_not_verify(
    framework, tmp_path
) -> None:
    """VERIFICATION IS ABOUT THE BYTES ON DISK, and there are three ways for them to stop
    matching: a declared artifact that is gone, one that is no longer readable as JSON, and
    one whose content hash has moved. Each answers ``False`` — a missing or corrupt artifact
    is a bundle that does not verify, not an error, because "does this still match" is a
    question with a boolean answer.
    """

    bundle = build_evidence(framework)

    intact = tmp_path / "intact"
    write_evidence(bundle, intact)
    assert verify_evidence(intact) is True

    manifest = json.loads((intact / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    artifact = sorted(manifest["artifacts"])[0]

    removed = tmp_path / "removed"
    write_evidence(bundle, removed)
    (removed / artifact).unlink()
    assert verify_evidence(removed) is False

    unreadable = tmp_path / "unreadable"
    write_evidence(bundle, unreadable)
    (unreadable / artifact).write_text("{ not json", encoding="utf-8")
    assert verify_evidence(unreadable) is False

    altered = tmp_path / "altered"
    write_evidence(bundle, altered)
    (altered / artifact).write_text(json.dumps({"replaced": True}) + "\n", encoding="utf-8")
    assert verify_evidence(altered) is False


def test_a_bundle_with_no_manifest_or_an_unusable_one_is_a_refusal(framework, tmp_path) -> None:
    """A MISSING ARTIFACT IS A FALSE; A MISSING MANIFEST IS AN ERROR.

    The distinction is the point. Without a manifest there is nothing to verify against, so
    "does this bundle match itself" cannot be answered at all — returning ``False`` would say
    the bundle is corrupt when what actually happened is that the caller pointed at a
    directory that is not a bundle. The same holds for a manifest that will not parse or
    declares no artifacts.
    """

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ProviderEvidenceError, match="has no manifest"):
        verify_evidence(empty)

    corrupt = tmp_path / "corrupt"
    write_evidence(build_evidence(framework), corrupt)
    (corrupt / MANIFEST_FILENAME).write_text("{ not json", encoding="utf-8")
    with pytest.raises(ProviderEvidenceError, match="manifest is unreadable"):
        verify_evidence(corrupt)

    artifactless = tmp_path / "artifactless"
    write_evidence(build_evidence(framework), artifactless)
    (artifactless / MANIFEST_FILENAME).write_text(
        json.dumps({"artifacts": "not a mapping"}), encoding="utf-8"
    )
    with pytest.raises(ProviderEvidenceError, match="declares no artifacts"):
        verify_evidence(artifactless)


def test_a_provider_permitted_to_serve_but_never_realized_is_refused(framework) -> None:
    """SERVING IS TWO FACTS: the lifecycle permits it, and an instance exists.

    The framework realizes an instance during onboarding, so the two normally move together
    — which is why this arm was dead. It is the check that separates "not allowed to serve"
    from "allowed, and there is nothing here", and collapsing them would return ``None`` to a
    consumer that asked for a provider and was told it could have one.
    """

    result = _onboarded(framework)
    qualified_id = result.qualified_id
    assert framework.provider(qualified_id) is not None

    framework._instances.pop(qualified_id)  # noqa: SLF001 - deliberate corruption
    with pytest.raises(ProviderLifecycleError, match="has not been realized") as excinfo:
        framework.provider(qualified_id)
    assert excinfo.value.detail["qualified_id"] == qualified_id


def test_admission_marks_a_refused_provider_rejected_unless_it_is_already_serving(
    framework,
) -> None:
    """A DECLARED PROVIDER THAT NEVER REGISTERS MUST NOT STAY DECLARED — but a provider that
    is already ACTIVE must not be demoted by a second declaration either.

    ``admit`` declares first and registers second, so a registration refusal would otherwise
    leave a provider the lifecycle has heard of and nothing has decided about. It is moved to
    REJECTED with the refusal's own code as the reason, and the error still propagates: the
    caller learns why, and the ledger records that the provider was considered and refused.

    The guard on that transition is what stops the second case from becoming a regression.
    Re-admitting a provider that is already serving is refused too — registration is
    append-only — and rejecting it would take a live provider out of service because somebody
    tried to register its id twice. The lifecycle refuses ACTIVE→REJECTED, so the transition
    is skipped and only the error is raised.
    """

    fresh = memo_descriptor(provider_id="fixture.refused")
    framework.admit(fresh)
    collision = memo_descriptor(provider_id="fixture.refused", name="A Second Declaration")
    with pytest.raises(ProviderRegistryError):
        framework.admit(collision)
    history = framework.lifecycle.history(collision.qualified_id)
    assert any("registration refused" in (entry.reason or "") for entry in history)
    assert framework.lifecycle.phase(collision.qualified_id) is ProviderPhase.REJECTED

    # An ACTIVE provider is refused the same way and stays active.
    active = _onboarded(framework, provider_id="fixture.serving")
    assert framework.lifecycle.phase(active.qualified_id) is ProviderPhase.ACTIVE
    again = memo_descriptor(provider_id="fixture.serving", name="Another Declaration")
    with pytest.raises(ProviderRegistryError):
        framework.admit(again)
    assert framework.lifecycle.phase(again.qualified_id) is ProviderPhase.ACTIVE

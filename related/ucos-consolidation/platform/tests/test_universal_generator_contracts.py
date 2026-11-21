"""UCOS-UNG-001 — the generation vocabulary: targets, artifacts, plans.

What is proven here is the vocabulary's two structural claims. First, that every identity is
content-addressed from inputs alone, so the same declaration always yields the same artifact
and the same plan — that is what makes a generated artifact re-derivable rather than merely
reproducible-in-principle. Second, that every absence is a refusal: an incomplete target, an
unknown kind, an empty plan and a destination collision are all raised, never defaulted.
"""

from __future__ import annotations

from platform.tests.universal_generator_helpers import target
from platform.universal_generator.contracts import (
    GENERATION_CONTRACT_VERSION,
    GENERATION_CONTRACTS,
    UNG_ID,
    ArtifactKind,
    GeneratedArtifact,
    GenerationPlan,
    GenerationTarget,
    generation_contract_names,
)
from platform.universal_generator.errors import GenerationPlanError, GenerationTargetError

import pytest


def artifact(
    target_id: str = "GT-01",
    destination: str = "pkg/a.py",
    content: str = "alpha\n",
    kind: ArtifactKind = ArtifactKind.CONTRACT,
) -> GeneratedArtifact:
    return GeneratedArtifact.create(target(target_id, kind=kind), destination, content)


# ---------------------------------------------------------------------------
# ArtifactKind
# ---------------------------------------------------------------------------


def test_the_kind_set_is_the_constitutional_shape_of_a_nucleus():
    """Ten kinds, each answering an obligation — a new file format is a template, not a kind."""
    assert {kind.value for kind in ArtifactKind} == {
        "constitutional",
        "contract",
        "errors",
        "registry",
        "bootstrap",
        "runtime",
        "policy",
        "documentation",
        "tests",
        "build",
    }


def test_coerce_returns_a_member_unchanged():
    assert ArtifactKind.coerce(ArtifactKind.TESTS) is ArtifactKind.TESTS


def test_coerce_resolves_a_declared_string():
    assert ArtifactKind.coerce("build") is ArtifactKind.BUILD


def test_an_unknown_kind_is_refused_rather_than_defaulted():
    with pytest.raises(GenerationTargetError) as exc:
        ArtifactKind.coerce("screenshot", subject="GT-42")
    assert "GT-42" in str(exc.value)


def test_a_non_string_kind_is_refused():
    with pytest.raises(GenerationTargetError):
        ArtifactKind.coerce(7)


# ---------------------------------------------------------------------------
# GenerationTarget
# ---------------------------------------------------------------------------


def test_a_declared_target_round_trips_through_its_projection():
    original = target("GT-05", kind=ArtifactKind.BOOTSTRAP, rationale="UFC-02")
    assert GenerationTarget.from_document(original.to_dict()) == original


def test_a_target_missing_a_required_key_names_what_is_missing():
    with pytest.raises(GenerationTargetError) as exc:
        GenerationTarget.from_document({"target_id": "GT-01", "kind": "contract"})
    message = str(exc.value)
    assert "template" in message and "destination" in message


def test_a_target_that_is_not_a_mapping_is_refused():
    with pytest.raises(GenerationTargetError):
        GenerationTarget.from_document(["GT-01"])  # type: ignore[arg-type]


@pytest.mark.parametrize("blank", ("target_id", "template", "destination"))
def test_a_target_with_a_blank_identity_template_or_destination_is_refused(blank):
    payload = {
        "target_id": "GT-01",
        "kind": "contract",
        "template": "contract-surface",
        "destination": "pkg/contracts.py",
    }
    payload[blank] = "   "
    with pytest.raises(GenerationTargetError):
        GenerationTarget.from_document(payload)


def test_target_fields_are_stripped_and_the_rationale_defaults_to_empty():
    built = GenerationTarget.from_document(
        {
            "target_id": " GT-01 ",
            "kind": "contract",
            "template": " contract-surface ",
            "destination": " pkg/contracts.py ",
        }
    )
    assert built.target_id == "GT-01"
    assert built.template == "contract-surface"
    assert built.destination == "pkg/contracts.py"
    assert built.rationale == ""


# ---------------------------------------------------------------------------
# GeneratedArtifact
# ---------------------------------------------------------------------------


def test_an_artifact_identity_covers_its_destination_as_well_as_its_bytes():
    """The same bytes at two destinations are two artifacts, not one relocated artifact."""
    here = artifact(destination="pkg/a.py")
    there = artifact(destination="pkg/b.py")
    assert here.content == there.content
    assert here.digest == there.digest
    assert here.artifact_id != there.artifact_id


def test_identical_inputs_yield_an_identical_artifact_identity():
    assert artifact().artifact_id == artifact().artifact_id
    assert artifact().artifact_id.startswith("UCOS-UNGA-")


def test_the_digest_is_over_the_bytes_alone():
    assert artifact(content="one\n").digest != artifact(content="two\n").digest


def test_line_count_counts_the_rendered_lines():
    assert artifact(content="a\nb\nc\n").line_count == 3
    assert artifact(content="").line_count == 0


def test_the_full_projection_carries_the_bytes_and_the_summary_does_not():
    item = artifact(content="alpha\nbeta\n")
    full = item.to_dict()
    compact = item.summary()
    assert full["content"] == "alpha\nbeta\n"
    assert "content" not in compact
    assert compact.items() <= full.items()


# ---------------------------------------------------------------------------
# GenerationPlan
# ---------------------------------------------------------------------------


def test_a_plan_orders_its_artifacts_by_destination_never_by_supply_order():
    plan = GenerationPlan.create(
        "UCOS-X-001",
        [artifact("GT-02", "pkg/z.py"), artifact("GT-01", "pkg/a.py")],
    )
    assert plan.destinations() == ("pkg/a.py", "pkg/z.py")


def test_two_plans_over_the_same_artifacts_share_one_identity():
    first = GenerationPlan.create("UCOS-X-001", [artifact("GT-01", "pkg/a.py")])
    second = GenerationPlan.create("UCOS-X-001", [artifact("GT-01", "pkg/a.py")])
    assert first.plan_id == second.plan_id
    assert first.fingerprint() == second.fingerprint()
    assert first.plan_id.startswith("UCOS-UNGP-")


def test_a_plan_for_a_different_nucleus_is_a_different_plan():
    first = GenerationPlan.create("UCOS-X-001", [artifact("GT-01", "pkg/a.py")])
    second = GenerationPlan.create("UCOS-Y-001", [artifact("GT-01", "pkg/a.py")])
    assert first.plan_id != second.plan_id


def test_an_empty_plan_is_refused():
    """A nucleus with no artifacts is not a determination anyone can act on."""
    with pytest.raises(GenerationPlanError) as exc:
        GenerationPlan.create("UCOS-X-001", [])
    assert "UCOS-X-001" in str(exc.value)


def test_two_targets_rendering_to_one_destination_are_refused():
    """A collision would let one obligation silently overwrite another."""
    with pytest.raises(GenerationPlanError) as exc:
        GenerationPlan.create(
            "UCOS-X-001",
            [artifact("GT-01", "pkg/same.py"), artifact("GT-02", "pkg/same.py")],
        )
    message = str(exc.value)
    assert "pkg/same.py" in message
    assert "GT-01" in message and "GT-02" in message


def test_the_plan_reports_its_size_and_the_kinds_it_covers():
    plan = GenerationPlan.create(
        "UCOS-X-001",
        [
            artifact("GT-01", "pkg/a.py", kind=ArtifactKind.CONTRACT),
            artifact("GT-02", "pkg/b.py", kind=ArtifactKind.TESTS),
        ],
    )
    assert plan.total == 2
    assert plan.kinds() == ("contract", "tests")


def test_by_kind_selects_in_destination_order_and_accepts_a_declared_string():
    plan = GenerationPlan.create(
        "UCOS-X-001",
        [
            artifact("GT-02", "pkg/z.py", kind=ArtifactKind.TESTS),
            artifact("GT-01", "pkg/a.py", kind=ArtifactKind.TESTS),
            artifact("GT-03", "pkg/m.py", kind=ArtifactKind.BUILD),
        ],
    )
    assert [item.destination for item in plan.by_kind("tests")] == ["pkg/a.py", "pkg/z.py"]
    assert plan.by_kind(ArtifactKind.BUILD) == plan.by_kind("build")


def test_by_kind_refuses_an_unknown_kind_rather_than_returning_nothing():
    """An empty tuple would read as "this plan covers no such artifacts", which is a lie."""
    plan = GenerationPlan.create("UCOS-X-001", [artifact()])
    with pytest.raises(GenerationTargetError):
        plan.by_kind("screenshot")


def test_require_returns_the_artifact_rendered_for_a_target():
    plan = GenerationPlan.create(
        "UCOS-X-001", [artifact("GT-01", "pkg/a.py"), artifact("GT-02", "pkg/b.py")]
    )
    assert plan.require("GT-02").destination == "pkg/b.py"


def test_require_refuses_a_target_the_plan_does_not_hold():
    plan = GenerationPlan.create("UCOS-X-001", [artifact("GT-01", "pkg/a.py")])
    with pytest.raises(GenerationPlanError) as exc:
        plan.require("GT-09")
    assert "GT-09" in str(exc.value)


def test_the_plan_summary_drops_the_bytes_the_full_projection_carries():
    plan = GenerationPlan.create("UCOS-X-001", [artifact(content="alpha\n")])
    full = plan.to_dict()
    compact = plan.summary()
    assert "content" in full["artifacts"][0]
    assert "content" not in compact["artifacts"][0]
    assert full["plan_id"] == compact["plan_id"]
    assert full["total"] == compact["total"] == 1


def test_the_fingerprint_changes_when_the_rendered_bytes_change():
    first = GenerationPlan.create("UCOS-X-001", [artifact(content="alpha\n")])
    second = GenerationPlan.create("UCOS-X-001", [artifact(content="beta\n")])
    assert first.fingerprint() != second.fingerprint()


# ---------------------------------------------------------------------------
# published contract surface
# ---------------------------------------------------------------------------


def test_the_published_contract_surface_is_versioned_and_named():
    names = generation_contract_names()
    assert names == tuple(ref.name for ref in GENERATION_CONTRACTS)
    assert names  # a nucleus with no published contract is not a nucleus
    assert all(ref.version == GENERATION_CONTRACT_VERSION for ref in GENERATION_CONTRACTS)


def test_the_generator_declares_its_own_identity():
    assert UNG_ID == "UCOS-UNG-001"

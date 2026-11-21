"""EC2-TASK-000102 — Blueprint derived-status tests (EC2-EPIC-006, P5)."""

from __future__ import annotations

from platform.blueprints.associations import BlueprintAssociation, BlueprintAssociationKind
from platform.blueprints.contracts import Blueprint, BlueprintFamily, BlueprintStatus
from platform.blueprints.errors import BlueprintStatusError
from platform.blueprints.status import BlueprintPosture, derive_status

import pytest


def _bp(status=BlueprintStatus.DRAFT):
    return Blueprint.create("bp", "n", "w", "o", BlueprintFamily.DATA).with_status(status)


@pytest.mark.parametrize(
    ("status", "posture"),
    [
        (BlueprintStatus.DRAFT, BlueprintPosture.DRAFT),
        (BlueprintStatus.VALIDATED, BlueprintPosture.VALIDATED),
        (BlueprintStatus.CATALOGUED, BlueprintPosture.CATALOGUED),
        (BlueprintStatus.SUPERSEDED, BlueprintPosture.SUPERSEDED),
        (BlueprintStatus.RETIRED, BlueprintPosture.RETIRED),
    ],
)
def test_posture_tracks_lifecycle(status, posture):
    st = derive_status(_bp(status), (), has_provenance=False)
    assert st.posture is posture


def test_traceable_only_when_catalogued_with_provenance():
    catalogued = derive_status(_bp(BlueprintStatus.CATALOGUED), (), has_provenance=True)
    assert catalogued.is_traceable is True
    no_prov = derive_status(_bp(BlueprintStatus.CATALOGUED), (), has_provenance=False)
    assert no_prov.is_traceable is False
    draft_prov = derive_status(_bp(BlueprintStatus.DRAFT), (), has_provenance=True)
    assert draft_prov.is_traceable is False


def test_association_counts_and_totals():
    bp = _bp(BlueprintStatus.CATALOGUED)
    assocs = [
        BlueprintAssociation.create(bp.blueprint_id, BlueprintAssociationKind.PROJECT, "P-1"),
        BlueprintAssociation.create(
            bp.blueprint_id, BlueprintAssociationKind.GENERATION_ARTIFACT, "BP-DATA-0001"
        ),
    ]
    st = derive_status(bp, assocs, has_provenance=True)
    assert st.association_total == 2
    assert st.is_associated is True
    counts = dict(st.association_counts)
    assert counts["project"] == 1
    assert counts["generation-artifact"] == 1
    assert st.status_id.startswith("UCOS-BDST-")
    assert st.to_dict()["is_traceable"] is True


def test_status_is_deterministic():
    bp = _bp(BlueprintStatus.CATALOGUED)
    a = derive_status(bp, (), has_provenance=True)
    b = derive_status(bp, (), has_provenance=True)
    assert a.fingerprint() == b.fingerprint()


def test_status_fail_closed_on_bad_inputs():
    with pytest.raises(BlueprintStatusError):
        derive_status("nope", (), has_provenance=True)  # type: ignore[arg-type]
    with pytest.raises(BlueprintStatusError):
        derive_status(_bp(), (), has_provenance="yes")  # type: ignore[arg-type]
    with pytest.raises(BlueprintStatusError):
        derive_status(_bp(), ["nope"], has_provenance=True)  # type: ignore[list-item]

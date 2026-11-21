"""EPIC-RTE-002 — Execution Federation unit tests."""

from __future__ import annotations

import pytest

from engine.runtime.execution.errors import ExecutionFederationError
from engine.runtime.execution.federation import (
    FEDERATION_FORMAT,
    FederatedLink,
    assert_federated,
    federate,
)
from engine.runtime.execution.isolation import isolate


def test_federate_single_context_has_no_links(composition):
    view = federate(composition)
    assert view.links == ()
    assert view.targets_of("A") == ()


def test_federate_projects_composition_links(federated_composition):
    view = federate(federated_composition)
    assert view.links == (FederatedLink(source="B", target="A"),)
    assert view.is_federated("B", "A")
    assert not view.is_federated("A", "B")
    assert view.targets_of("B") == ("A",)


def test_assert_federated_passes_when_authorised(federated_composition):
    isolation = isolate(federated_composition)
    federation = federate(federated_composition)
    # no exception
    assert assert_federated(federated_composition, isolation, federation) is None


def test_assert_federated_intra_context_is_fine(composition):
    isolation = isolate(composition)
    federation = federate(composition)
    assert assert_federated(composition, isolation, federation) is None


def test_assert_federated_detects_missing_link(federated_composition):
    isolation = isolate(federated_composition)
    empty_federation = federate(federated_composition)
    # drop the link so the cross-context dependency is unauthorised
    stripped = type(empty_federation)(composition_id=empty_federation.composition_id, links=())
    with pytest.raises(ExecutionFederationError) as exc:
        assert_federated(federated_composition, isolation, stripped)
    assert exc.value.code == "RT-EXEC-FED-001"


def test_federation_view_to_dict(federated_composition):
    blob = federate(federated_composition).to_dict()
    assert blob["federation_format"] == FEDERATION_FORMAT
    assert blob["link_count"] == 1


def test_federated_link_to_dict():
    assert FederatedLink("B", "A").to_dict() == {"source": "B", "target": "A"}

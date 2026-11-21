"""EPIC-RTE-002 — Execution Authorization unit tests."""

from __future__ import annotations

import dataclasses

import pytest

from engine.runtime.execution.authorization import (
    AUTHORIZATION_FORMAT,
    EXECUTION_AUTHORITY,
    Authorization,
    authorize,
    require_authorization,
)
from engine.runtime.execution.errors import ExecutionAuthorizationError


def test_authorize_grants_engineering_execution(composition):
    auth = authorize(composition)
    assert auth.granted
    assert auth.authority == EXECUTION_AUTHORITY
    assert auth.composition_id == composition.composition_id
    assert auth.authorization_id.startswith("UCOS-EXEC-AUTH-")


def test_authorize_is_deterministic(composition):
    assert authorize(composition).authorization_id == authorize(composition).authorization_id


def test_authorize_subject_changes_identity(composition):
    a = authorize(composition, subject="engineering")
    b = authorize(composition, subject="operator")
    assert a.authorization_id != b.authorization_id


def test_authorize_refuses_missing_disclosure(composition):
    undisclosed = dataclasses.replace(composition, disclosure={})
    with pytest.raises(ExecutionAuthorizationError) as exc:
        authorize(undisclosed)
    assert exc.value.code == "RT-EXEC-AUTH-001"


def test_authorization_to_dict(composition):
    blob = authorize(composition).to_dict()
    assert blob["authorization_format"] == AUTHORIZATION_FORMAT
    assert blob["granted"] is True


def test_require_authorization_passes_granted(composition):
    auth = authorize(composition)
    assert require_authorization(auth) is auth


def test_require_authorization_rejects_ungranted():
    bad = Authorization(
        authorization_id="X",
        composition_id="C",
        subject="s",
        authority=EXECUTION_AUTHORITY,
        granted=False,
    )
    with pytest.raises(ExecutionAuthorizationError):
        require_authorization(bad)


def test_require_authorization_rejects_foreign_authority():
    bad = Authorization(
        authorization_id="X",
        composition_id="C",
        subject="s",
        authority="CONSTITUTIONAL",
        granted=True,
    )
    with pytest.raises(ExecutionAuthorizationError):
        require_authorization(bad)

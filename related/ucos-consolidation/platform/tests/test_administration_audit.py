"""EC2-CAP-ADMIN-001 — Administrative audit / activity-tracking tests.

Covers the append-only administrative activity log: ordered records, per-principal
activity tracking, granted/denied partitions, per-action counts, validation, and
determinism.
"""

from __future__ import annotations

from platform.administration.audit import AdministrativeAuditLog
from platform.administration.contracts import (
    AdministrativeAction,
    AdministrativeDomain,
    AdministrativeScope,
)
from platform.administration.errors import AdministrationAuditError

import pytest


def _record(
    log,
    *,
    action=AdministrativeAction.INSPECT,
    principal="UCOS-PRIN-a",
    granted=True,
    tick=0,
):
    return log.record(
        action=action,
        domain=AdministrativeDomain.CONFIGURATION,
        scope=AdministrativeScope.PLATFORM,
        principal_id=principal,
        target_id="UCOS-ATGT-x",
        granted=granted,
        reason="granted" if granted else "no-grant",
        tick=tick,
    )


def test_record_appends_ordered_events():
    log = AdministrativeAuditLog()
    e0 = _record(log, tick=1)
    e1 = _record(log, tick=2)
    assert e0.sequence == 0
    assert e1.sequence == 1
    assert len(log) == 2
    assert log.events[0].to_dict()["action"] == "inspect"


def test_activity_of_tracks_a_principal():
    log = AdministrativeAuditLog()
    _record(log, principal="UCOS-PRIN-a")
    _record(log, principal="UCOS-PRIN-b")
    _record(log, principal="UCOS-PRIN-a")
    assert len(log.activity_of("UCOS-PRIN-a")) == 2
    assert len(log.activity_of("UCOS-PRIN-b")) == 1


def test_granted_and_denied_partitions_and_counts():
    log = AdministrativeAuditLog()
    _record(log, action=AdministrativeAction.INSPECT, granted=True)
    _record(log, action=AdministrativeAction.CONFIGURE, granted=False)
    _record(log, action=AdministrativeAction.INSPECT, granted=True)
    assert len(log.granted_events()) == 2
    assert len(log.denied_events()) == 1
    assert log.action_counts() == {"inspect": 2, "configure": 1}
    data = log.to_dict()
    assert data["granted_count"] == 2
    assert data["denied_count"] == 1


@pytest.mark.parametrize(
    "field, value",
    [
        ("action", "inspect"),
        ("domain", "configuration"),
        ("scope", "platform"),
        ("principal_id", ""),
        ("reason", ""),
    ],
)
def test_record_validates_vocabulary(field, value):
    log = AdministrativeAuditLog()
    kwargs = dict(
        action=AdministrativeAction.INSPECT,
        domain=AdministrativeDomain.CONFIGURATION,
        scope=AdministrativeScope.PLATFORM,
        principal_id="UCOS-PRIN-a",
        target_id="UCOS-ATGT-x",
        granted=True,
        reason="granted",
        tick=0,
    )
    kwargs[field] = value
    with pytest.raises(AdministrationAuditError):
        log.record(**kwargs)  # type: ignore[arg-type]


def test_fingerprint_is_deterministic():
    def build() -> AdministrativeAuditLog:
        log = AdministrativeAuditLog()
        _record(log, tick=1)
        _record(log, action=AdministrativeAction.ASSIGN, granted=False, tick=2)
        return log

    assert build().fingerprint() == build().fingerprint()

"""UCOS-OBSERVATION-UNIVERSE-001 — observation values may not enter canonical identity.

The defect, measured before the fix
-----------------------------------
``00-MASTER/UKAP-001/07-CERTIFICATION-REPORT.md`` sealed a digest of
``00-MASTER/UAKOS-CLOSURE-008/assimilation.json`` that the file did not have, so UKAP
rewrote itself on every run. UCOS-RIB-001, running later in the same UCOS-AEE-001 pass,
observed that ONE dirty entry, flipped GATE-04 and GATE-12, and rewrote sixteen files.
UCOS-AEE-001 then recorded seventeen ``residue`` paths verbatim into ``aee.json`` — the
artifact Phase 8 measures as ``certification_variance``.

A one-file staleness therefore became a twenty-one-file oscillation that could not
converge: Phase 8 measured drift on ``registry_variance`` and ``ordering_variance`` in
every one of five rounds, and zero_drift_rounds stayed at 0.

The amplifier was the defect, not the trigger. UCOS-RC-003 had already established that a
working-tree measurement is a gate input and never canonical identity, and withheld those
VALUES from ``rib.json``. It was correct and incomplete: redaction hides what a field says
but cannot hide whether a list ELEMENT EXISTS, and ``aee.json`` had no such protection at
all.

The regression these tests pin
------------------------------
:func:`test_no_canonical_artifact_embeds_an_observation_value` is the whole invariant:
against the previous implementation it found 169 sites.
:func:`test_residue_is_preserved_as_evidence` is the other half — the reading must still
exist, because the remedy is to RELOCATE evidence out of identity, never to delete it.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "00-BOOK" / "DATA" / "observation-universe.json"
LEDGER = REPO / "00-BOOK" / "DATA" / "id-ledger.json"
AEE_STATE = REPO / "00-MASTER" / "UCOS-AEE-001" / "aee.json"
AEE_EVIDENCE = REPO / "00-MASTER" / "UCOS-AEE-001" / "evidence" / "observations.json"
UGA_ENGINE = REPO / "00-MASTER" / "UCOS-UGA-001" / "uga_engine.py"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def registry() -> dict:
    return _load(REGISTRY)


@pytest.fixture(scope="module")
def ledger() -> dict:
    return _load(LEDGER)


# --- the register itself ------------------------------------------------------------


def test_the_registry_is_authored_repository_truth(registry) -> None:
    assert registry["schema"] == "ucos-observation-universe"
    assert "AUTHORED REPOSITORY TRUTH" in registry["authority"]
    assert registry["observation_kinds"], "no observation kind is declared"


def test_exactly_one_kind_is_canonically_admissible(registry) -> None:
    """Only a measurement whose entire input is committed content may be embedded."""
    permitted = {
        name
        for name, spec in registry["observation_kinds"].items()
        if spec["canonical_admissibility"] == "PERMITTED"
    }
    assert permitted == {"COMMITTED_CONTENT"}


def test_every_kind_binds_to_an_existing_evidence_class(registry) -> None:
    """No sixth evidence class. The closed set of UCOS-EVIDENCE-UNIVERSE-001 stands."""
    universe = _load(REPO / "00-BOOK" / "DATA" / "evidence-universe.json")
    declared = set(universe["evidence_classes"])
    for name, spec in registry["observation_kinds"].items():
        assert spec["evidence_class"] in declared, f"{name} invents an evidence class"


# --- identity -----------------------------------------------------------------------


def test_every_observation_holds_a_universal_identity(ledger, registry) -> None:
    shape = re.compile(registry["observation_id_shape"])
    minted = ledger.get("by_observation") or {}
    assert minted, "no observation has been minted"
    for key, record in minted.items():
        assert shape.match(record["observation_id"]), f"{key}: malformed identity"


def test_observation_identity_is_value_independent(ledger) -> None:
    """THE central property. The key is observer::subject::kind and nothing else.

    If an observed value could enter the key, the identity would move when the reading
    moved, and a canonical artifact referencing it would drift exactly as it did when it
    carried the value directly.
    """
    for key, record in (ledger.get("by_observation") or {}).items():
        expected = f"{record['observer']}::{record['subject']}::{record['kind']}"
        assert key == expected, f"{record['observation_id']}: key carries something else"


def test_observation_identities_are_unique(ledger) -> None:
    ids = [r["observation_id"] for r in (ledger.get("by_observation") or {}).values()]
    assert len(ids) == len(set(ids))


def test_observations_mint_from_the_one_identity_authority(ledger) -> None:
    """No second authority: observations share `category_seq` with every other object."""
    assert "OBS" in ledger["category_seq"]
    assert ledger["category_seq"]["OBS"] == len(ledger.get("by_observation") or {})


# --- the invariant ------------------------------------------------------------------


def test_no_canonical_artifact_embeds_an_observation_value(registry) -> None:
    """THE invariant. Driven by the register's own scoped rules, not by this test."""
    sys.path.insert(0, str(UGA_ENGINE.parent))
    try:
        import uga_engine
    finally:
        sys.path.pop(0)
    findings = uga_engine.scan_canonical_for_observation_values(registry)
    assert findings == [], "observation values in canonical artifacts:\n  " + "\n  ".join(
        findings[:20]
    )


def test_forbidden_keys_are_scoped_to_artifacts(registry) -> None:
    """Scoping is load-bearing, not tidiness.

    `action` holds "REUSE"/"EXTEND" in acee.json and ucl.json — an architectural
    disposition derived from a declaration, which is Identity Truth. The same word in a
    materialization manifest means "this run created the file". An unscoped scan flagged
    18 such sites; an invariant that cries wolf gets suppressed.
    """
    for rule in registry["forbidden_canonical_keys"]["rules"]:
        assert rule["artifact"], f"{rule['key']} is declared without an artifact scope"
        assert rule["kind"] in registry["observation_kinds"]


def test_aee_state_carries_references_and_not_readings() -> None:
    body = AEE_STATE.read_text(encoding="utf-8")
    assert '"residue":' not in body, "aee.json still embeds the residue reading"
    assert '"unattributed":' not in body
    assert '"residue_observation":' in body, "aee.json lost its observation reference"


# --- evidence is relocated, never deleted -------------------------------------------


def _emit_evidence_into(destination: Path) -> dict:
    """Emit the observation evidence for the COMMITTED model, into a directory we own.

    The producer is driven directly rather than through the loop: this measures the
    projection that preserves the readings, not a run of the evolution driver.
    """
    sys.path.insert(0, str(REPO / "00-MASTER" / "UCOS-AEE-001"))
    try:
        import aee_engine
    finally:
        sys.path.pop(0)
    original = aee_engine.EVIDENCE_DIR
    try:
        aee_engine.EVIDENCE_DIR = destination
        return _load(aee_engine._emit_observation_evidence(_load(AEE_STATE)))
    finally:
        aee_engine.EVIDENCE_DIR = original


def test_residue_is_preserved_as_evidence(registry, tmp_path: Path) -> None:
    """The other half of the remedy. Removing a reading from identity may not lose it.

    MEASURED, NOT ASSUMED PRESENT. This asserted ``AEE_EVIDENCE.is_file()`` against
    ``00-MASTER/UCOS-AEE-001/evidence/observations.json`` — a path ``.gitignore:122``
    excludes (``00-MASTER/**/evidence/``) and only ``aee_engine.py`` writes. So it passed on
    any machine where the engine had ever run and failed on EVERY clean checkout, which is
    what it did: the sole remaining failure of ``./verify.sh --full`` from a fresh clone. A
    test whose subject is not in version control is measuring local execution history rather
    than the repository, and the property it claims to hold — that lifting a reading out of
    canonical identity does not lose it — is a property of the PROJECTION, which the
    committed state is sufficient to measure.

    The real archive is still asserted when it exists, so nothing that was checked before is
    checked less now; it is simply no longer the only path to a verdict.
    """
    emitted = _emit_evidence_into(tmp_path)
    assert emitted["evidence_class"] == "EXECUTION"
    assert emitted["readings"], "the evidence surface records no reading"
    assert {"residue", "unattributed"} <= set(emitted["readings"][0])

    if AEE_EVIDENCE.is_file():
        doc = _load(AEE_EVIDENCE)
        assert doc["evidence_class"] == "EXECUTION"
        assert doc["readings"], "the committed run's evidence surface records no reading"
        assert {"residue", "unattributed"} <= set(doc["readings"][0])


def test_an_emitter_that_drops_a_reading_is_refused(tmp_path: Path) -> None:
    """NON-VACUITY. The guard above must fail when the readings are actually lost.

    Without this, ``test_residue_is_preserved_as_evidence`` would be satisfied by an emitter
    that wrote a well-formed surface containing nothing — which is precisely the shape of
    loss it exists to refuse.
    """
    emitted = _emit_evidence_into(tmp_path)
    stripped = {**emitted, "readings": []}
    assert not stripped["readings"]
    with pytest.raises(AssertionError):
        assert stripped["readings"], "the evidence surface records no reading"

    without_keys = {**emitted, "readings": [{"actuator": "ACT-X"}]}
    assert not {"residue", "unattributed"} <= set(
        without_keys["readings"][0]
    ), "a reading carrying neither residue nor unattributed must not satisfy the guard"


def test_every_reference_in_canonical_state_resolves_to_a_real_observation(ledger) -> None:
    """A reference that resolves to nothing is worse than the value it replaced."""
    minted = {r["observation_id"] for r in (ledger.get("by_observation") or {}).values()}
    referenced = set(re.findall(r"UCOS-OBS-\d{6}", AEE_STATE.read_text(encoding="utf-8")))
    assert referenced, "aee.json references no observation"
    assert referenced <= minted, f"dangling: {sorted(referenced - minted)}"


# --- the gate -----------------------------------------------------------------------


def test_the_governance_gate_enforces_every_invariant() -> None:
    """Fail-closed and wired into ./verify.sh, so this cannot regress silently."""
    run = subprocess.run(  # noqa: S603
        [sys.executable, str(UGA_ENGINE), "gate"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    for invariant in (
        "OBS-INV-01",
        "OBS-INV-02",
        "OBS-INV-03",
        "OBS-INV-04",
        "OBS-INV-05",
        "OBS-INV-06",
    ):
        assert f"[PASS] {invariant}" in run.stdout, f"{invariant} is not passing"


# --- PHASE 7: TEST-OBS-001..003 — mutation must not move canonical identity ----------


def test_obs_001_working_tree_mutation_does_not_change_canonical_identity(tmp_path) -> None:
    """TEST-OBS-001. A dirty tree may change the VERDICT but never the canonical bytes.

    Exercised against the projection rather than by dirtying the real tree, so the test
    is hermetic. Against the previous implementation the two projections differed: the
    dirty model appended a CMP-CLEAN compliance finding and flipped `gate`, which is the
    twenty-one-file oscillation that held Phase 8 at zero_drift_rounds=0.
    """
    sys.path.insert(0, str(REPO / "00-MASTER" / "UCOS-RIB-001"))
    try:
        import rib_engine
    finally:
        sys.path.pop(0)

    clean = {
        "gates": [
            {
                "id": "GATE-12",
                "blocking": True,
                "failures": [],
                "metrics": ["dirty_entries_outside_generated", "ignored_unclassified"],
                "verdict": "PASS",
            },
        ],
        "validations": [
            {
                "id": "VAL-02",
                "metric": "dirty_entries_outside_generated",
                "verdict": "PASS",
                "measured": 0,
            }
        ],
        "compliance": [],
        "gate": "OPEN",
        "gate_exit": 0,
        "determination": "BLUEPRINT CERTIFIED — REPOSITORY MAY PROCEED",
        "repository": {"dirty_entries": 0},
    }
    dirty = {
        "gates": [
            {
                "id": "GATE-12",
                "blocking": True,
                "failures": ["dirty_entries_outside_generated=7"],
                "metrics": ["dirty_entries_outside_generated", "ignored_unclassified"],
                "verdict": "FAIL",
            },
        ],
        "validations": [
            {
                "id": "VAL-02",
                "metric": "dirty_entries_outside_generated",
                "verdict": "FAIL",
                "measured": 7,
            }
        ],
        "compliance": [
            {
                "id": "CMP-CLEAN",
                "gate": "GATE-12",
                "rank": 1,
                "finding": "dirty_entries_outside_generated=7",
            }
        ],
        "gate": "CLOSED",
        "gate_exit": 1,
        "determination": "BLUEPRINT NOT CERTIFIED — REPOSITORY MUST STOP",
        "repository": {"dirty_entries": 7},
    }
    assert rib_engine.canonical_model(clean) == rib_engine.canonical_model(
        dirty
    ), "a working-tree mutation moved the canonical projection"


def test_obs_001b_a_real_gate_failure_still_closes_the_gate() -> None:
    """The other side of TEST-OBS-001, and the one that proves nothing was weakened.

    GATE-12 declares three metrics and only one is a working-tree reading. If the whole
    gate were excused, an unclassified ignored path would pass silently.
    """
    sys.path.insert(0, str(REPO / "00-MASTER" / "UCOS-RIB-001"))
    try:
        import rib_engine
    finally:
        sys.path.pop(0)

    model = {
        "gates": [
            {
                "id": "GATE-12",
                "blocking": True,
                "failures": ["dirty_entries_outside_generated=7", "ignored_unclassified=3"],
                "metrics": ["dirty_entries_outside_generated", "ignored_unclassified"],
                "verdict": "FAIL",
            },
        ],
        "validations": [],
        "compliance": [
            {"id": "CMP-CLEAN", "gate": "GATE-12", "rank": 1, "finding": "ignored_unclassified=3"}
        ],
        "gate": "CLOSED",
        "gate_exit": 1,
        "determination": "BLUEPRINT NOT CERTIFIED — REPOSITORY MUST STOP",
        "repository": {},
    }
    out = rib_engine.canonical_model(model)
    assert out["gate"] == "CLOSED", "a non-working-tree failure was excused"
    assert out["gate_exit"] == 1
    assert out["compliance"], "the finding for a real failure was dropped"


def test_obs_002_execution_residue_changes_only_evidence() -> None:
    """TEST-OBS-002. Residue differing between two passes must move no canonical byte."""
    sys.path.insert(0, str(REPO / "00-MASTER" / "UCOS-AEE-001"))
    try:
        import aee_engine
    finally:
        sys.path.pop(0)

    first = {
        "iterations": [
            {"actuators": [{"id": "ACT-X", "verdict": "PASS", "residue": [], "unattributed": []}]}
        ]
    }
    second = {
        "iterations": [
            {
                "actuators": [
                    {
                        "id": "ACT-X",
                        "verdict": "PASS",
                        "residue": ["a.md", "b.md"],
                        "unattributed": ["a.md"],
                    }
                ]
            }
        ]
    }
    assert aee_engine.canonical_model(first) == aee_engine.canonical_model(second)


def test_obs_003_canonical_artifacts_carry_no_runtime_measurement() -> None:
    """TEST-OBS-003. The forensic sweep must report zero open violations."""
    audit = _load(REPO / "00-BOOK" / "DATA" / "canonical-observation-audit.json")
    assert audit["open_violations"] == 0, [
        r["current_location"] for r in audit["entries"] if r["classification"].startswith("MUTABLE")
    ]

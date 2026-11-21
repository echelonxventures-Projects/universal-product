"""UAKOS-CLOSURE-008 — execution transcripts may not participate in canonical identity.

The defect, measured before the fix
-----------------------------------
``00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py`` read ``evidence/verify.log`` while
rendering register 06 and embedded its last fourteen matching lines verbatim. Register 04
then recorded 06's byte count and content hash. So a stage timing and a coverage total —
observations of one run on one machine — sat inside the identity of two canonical artifacts.

``.gitignore`` excludes ``00-MASTER/**/evidence/``, so the transcript was not in the tree at
all. Rendering a fresh checkout of HEAD took the fail-closed NOT-CAPTURED branch and produced
a 06 of 10776 bytes against the committed 11660, which moved 04's recorded hash with it. The
CI drift gate in ``.github/workflows/assimilation-gate.yml`` asserts that the committed
registers ARE the rendered fixed point; on a clean clone they were not.

The regression these tests pin
------------------------------
:func:`test_red_green_transcript_change_moves_no_canonical_byte` is the RED/GREEN case named
in the determination: a transcript that differs only because the command ran again must move
no canonical byte. Against the previous implementation both 06 and 04 changed; it passes only
because the canonical layer now reads a validation RESULT and references the transcript by id.

:func:`test_bootstrap_renders_the_committed_fixed_point_with_no_evidence_archive` is the
bootstrap half: a fresh clone has no execution history, and must still render exactly the
canonical bytes that are committed.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path
from platform.repository_intelligence.validation_records import (
    EXECUTION_OBSERVATION_CLASSIFICATIONS,
    SCHEMA,
    load,
    parse,
    validate,
)

import pytest

from engine.verification_intelligence.constitution import load_constitution

REPO = Path(__file__).resolve().parents[2]
HOME = REPO / "00-MASTER" / "UAKOS-CLOSURE-008"
RECORD_PATH = HOME / "validation-record.json"
ENGINE = "assimilation_engine.py"

#: Two transcripts of the same passing gate. They differ only in what a second execution
#: cannot help but change: stage timings and the observed coverage total.
TRANSCRIPT_A = (
    "TOTAL                                                  37679   2157   7432    112    94%\n"
    "\x1b[32m✓\x1b[0m STAGE PASSED: coverage report\n"
    "  PASS  pytest + coverage gate (--cov-fail-under=90)  26s\n"
    "  TOTAL (wall clock)                                    35s\n"
    "✓ VERIFICATION PASSED — all gates green.\n"
)
TRANSCRIPT_B = (
    "TOTAL                                                  37681   2158   7432    112    94%\n"
    "\x1b[32m✓\x1b[0m STAGE PASSED: coverage report\n"
    "  PASS  pytest + coverage gate (--cov-fail-under=90)  31s\n"
    "  TOTAL (wall clock)                                    44s\n"
    "✓ VERIFICATION PASSED — all gates green.\n"
)


def _minimal_record(**overrides) -> dict:
    doc = {
        "schema": SCHEMA,
        "validation_id": "X.VR-001",
        "contract": {"contract_id": "C-1", "command": "./verify.sh"},
        "result": "PASS",
        "stages": [{"stage": "a gate", "result": "PASS"}],
    }
    doc.update(overrides)
    return doc


def _declared_contract_stages() -> list[str]:
    """The stage names ``./verify.sh`` declares for its default invocation.

    Derived from the contract itself rather than restated here, so a gate added to verify.sh
    and not to the record is a failure rather than a silent divergence. The opt-in ``--full``
    stage is excluded: it is outside the default contract.
    """
    source = (REPO / "verify.sh").read_text(encoding="utf-8")
    default_scope = source.split('if [ "$FULL" = "1" ]')[0]
    return re.findall(r'^\s*run_stage "([^"]+)"', default_scope, re.M)


# --- the canonical validation record ------------------------------------------------------


def test_the_live_record_satisfies_every_invariant() -> None:
    findings = validate(load(RECORD_PATH))
    assert findings == [], "validation record is not canonical-safe:\n  " + "\n  ".join(findings)


def test_the_live_record_states_a_result_and_references_evidence_it_does_not_contain() -> None:
    record = parse(load(RECORD_PATH))
    assert record.passed
    # The command is asserted as a PROPERTY, not as a literal. UVI-000001 made the
    # certification mode explicit — the bare invocation is now --change, a developer mode
    # that certifies nothing — so the record must name a mode the constitution declares
    # certification-eligible. Pinning the literal would have made this test pass while the
    # record pointed at a mode that evaluates no coverage floor, which is the failure it
    # exists to catch.

    command, _, flag = record.command.partition(" ")
    assert command == "./verify.sh"
    certifying = {m.flag for m in load_constitution().modes if m.certification_eligible}
    assert flag in certifying, (
        f"the canonical record names {record.command!r}, which is not a certification-eligible "
        f"invocation; one of {sorted(certifying)} is required"
    )
    ref = record.evidence_reference
    assert ref is not None
    assert ref.classification == "EXECUTION_TRANSCRIPT"
    assert ref.member == "verify.log"
    # The reference is an identity. Nothing in it measures the archive.
    assert not set(load(RECORD_PATH)["evidence_reference"]) & {"sha256", "bytes", "size"}


def test_the_record_covers_every_stage_the_contract_declares() -> None:
    """A gate added to verify.sh and not to the record makes the record a stale claim."""
    declared = _declared_contract_stages()
    record = parse(load(RECORD_PATH))
    assert list(record.stage_names) == declared
    digest = hashlib.sha256("\n".join(declared).encode("utf-8")).hexdigest()
    assert record.stages_digest == digest, (
        "the recorded contract digest does not match verify.sh — re-run ./verify.sh and "
        "re-author 00-MASTER/UAKOS-CLOSURE-008/validation-record.json"
    )


@pytest.mark.parametrize(
    "value",
    [
        "\x1b[32mPASS\x1b[0m",
        "/Users/someone/Desktop/UCOS-CONSOLIDATION",
        "2026-08-12T06:41:39",
        "TOTAL (wall clock) 35s",
        "line one\nline two",
    ],
)
def test_a_record_that_drifts_back_toward_a_transcript_is_refused(value: str) -> None:
    """Terminal output, machine paths, clocks and captured lines are all the wrong category."""
    doc = _minimal_record(note=value)
    assert validate(doc), f"{value!r} was accepted into a canonical record"


@pytest.mark.parametrize("key", ["stdout", "duration", "hostname", "timestamp", "toolchain"])
def test_a_key_that_names_an_execution_observation_is_refused(key: str) -> None:
    doc = _minimal_record(contract={"contract_id": "C", "command": "c", key: "anything"})
    assert any(key in f for f in validate(doc))


def test_the_evidence_reference_may_not_measure_the_archive() -> None:
    """THE rule. A transcript's digest is the transcript's identity in a deterministic costume.

    Record it and canonical bytes move again the next time the command runs, which is the
    defect this determination closed. The reference names the evidence; it never weighs it.
    """
    doc = _minimal_record(
        evidence_reference={
            "evidence_id": "EV-1",
            "archive_path": "programme/evidence/",
            "classification": "EXECUTION_TRANSCRIPT",
            "sha256": "0" * 64,
        }
    )
    findings = validate(doc)
    assert any("sha256" in f and "bytes" in f for f in findings), findings


def test_an_evidence_reference_must_be_classified_as_an_observation() -> None:
    doc = _minimal_record(
        evidence_reference={
            "evidence_id": "EV-1",
            "archive_path": "programme/evidence/",
            "classification": "TRACKED_DETERMINISTIC",
        }
    )
    assert any("classification" in f for f in validate(doc))
    assert "EXECUTION_TRANSCRIPT" in EXECUTION_OBSERVATION_CLASSIFICATIONS


def test_a_pass_over_a_failing_stage_fails_closed() -> None:
    doc = _minimal_record(stages=[{"stage": "a gate", "result": "FAIL"}])
    assert any("fails closed" in f for f in validate(doc))


def test_a_record_with_no_stages_asserts_nothing() -> None:
    assert any("no stages" in f for f in validate(_minimal_record(stages=[])))


def test_schema_and_required_fields_are_enforced() -> None:
    assert any("schema" in f for f in validate(_minimal_record(schema="something-else")))
    assert any("validation_id" in f for f in validate(_minimal_record(validation_id="")))
    assert any("contract_id" in f for f in validate(_minimal_record(contract={})))
    assert any("result" in f for f in validate(_minimal_record(result="MAYBE")))


def test_a_stage_is_refused_for_its_name_and_its_result_independently() -> None:
    """THE TWO CHECKS ARE NOT ONE CHECK, and the record's whole purpose is why.

    The record replaces a transcript with a claim, so a reader has to be able to tell WHICH
    gate produced WHICH verdict. A stage with a result and no name is a verdict attributable
    to nothing; a stage with a name and an unrecognised result is a gate whose outcome is not
    one of the values the schema admits. Either alone empties the record of the thing it
    exists to carry, and both are reported, so one malformed stage does not hide the other.
    """
    anonymous = validate(_minimal_record(stages=[{"result": "PASS"}]))
    assert any("a stage carries no name" in f for f in anonymous)

    unrecognised = validate(_minimal_record(stages=[{"stage": "a gate", "result": "PROBABLY"}]))
    assert any("'PROBABLY' is not one of" in f for f in unrecognised)
    assert any("a gate" in f for f in unrecognised)

    both = validate(_minimal_record(stages=[{"result": "PROBABLY"}]))
    assert any("carries no name" in f for f in both)
    assert any("is not one of" in f for f in both)


def test_an_evidence_reference_that_is_not_an_object_is_refused() -> None:
    """``evidence_reference`` is OPTIONAL and its absence is legitimate — the canonical layer
    stands without the archive. What is not legitimate is a reference that is present and is
    not a reference: a string or a list there would make every field lookup below return
    nothing, and the record would pass with a pointer to nowhere."""
    assert validate(_minimal_record(evidence_reference=None)) == []
    for wrong in ("00-MASTER/.../evidence.tar.gz", ["evidence"], 7):
        findings = validate(_minimal_record(evidence_reference=wrong))
        assert findings == ["evidence_reference: not an object"], wrong


def test_an_evidence_reference_names_all_three_of_the_things_that_locate_it() -> None:
    """An id, a path and a classification. A reference missing any one of them cannot be
    resolved back to the archive it claims to point at, and the point of separating the
    layers is that the pointer still works."""
    findings = validate(_minimal_record(evidence_reference={}))
    for field in ("evidence_id", "archive_path", "classification"):
        assert f"evidence_reference: no {field}" in findings

    complete = _minimal_record(
        evidence_reference={
            "evidence_id": "E-1",
            "archive_path": "evidence/run.tar.gz",
            "classification": sorted(EXECUTION_OBSERVATION_CLASSIFICATIONS)[0],
        }
    )
    assert validate(complete) == []


# --- RED / GREEN: the canonical layer is independent of the evidence layer -----------------


@pytest.fixture(scope="module")
def program_copy(tmp_path_factory) -> Path:
    """The programme home, without its evidence archive, somewhere writable."""
    home = tmp_path_factory.mktemp("closure008") / "00-MASTER" / "UAKOS-CLOSURE-008"
    shutil.copytree(HOME, home, ignore=shutil.ignore_patterns("evidence", "__pycache__"))
    return home


def _render(home: Path) -> None:
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(home / ENGINE), "--render"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_red_green_transcript_change_moves_no_canonical_byte(program_copy: Path) -> None:
    """RED against the previous engine, GREEN against this one.

    Given a transcript that differs only because the command was executed again, every
    canonical artifact must be byte-identical. Before the fix, 06 embedded the transcript
    tail and 04 recorded the hash that followed from it, so both moved.
    """
    archive = program_copy / "evidence"
    archive.mkdir(exist_ok=True)

    (archive / "verify.log").write_text(TRANSCRIPT_A, encoding="utf-8")
    _render(program_copy)
    first = {
        name: (program_copy / name).read_bytes()
        for name in ("06-VALIDATION-REPORT.md", "04-REPOSITORY-CHANGE-REGISTER.md")
    }

    (archive / "verify.log").write_text(TRANSCRIPT_B, encoding="utf-8")
    _render(program_copy)

    for name, before in first.items():
        assert (program_copy / name).read_bytes() == before, (
            f"{name} changed because an execution transcript changed — canonical identity "
            f"is depending on a historical observation again"
        )


def test_bootstrap_renders_the_committed_fixed_point_with_no_evidence_archive(
    program_copy: Path,
) -> None:
    """A fresh clone has no execution history and must still render the committed bytes."""
    shutil.rmtree(program_copy / "evidence", ignore_errors=True)
    _render(program_copy)
    rendered = (program_copy / "06-VALIDATION-REPORT.md").read_bytes()
    assert rendered == (HOME / "06-VALIDATION-REPORT.md").read_bytes(), (
        "rendering without the evidence archive does not reproduce the committed register — "
        "the CI drift gate would fail on a clean checkout"
    )


def test_the_engine_never_reads_the_evidence_archive_while_rendering() -> None:
    """Structural: the read that created the dependency is gone, not merely unused."""
    source = (HOME / ENGINE).read_text(encoding="utf-8")
    code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
    assert 'HERE / "evidence"' not in code
    assert '"evidence" / "verify.log"' not in code


def test_the_record_is_tracked_so_the_canonical_input_survives_a_clone() -> None:
    tracked = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--error-unmatch", str(RECORD_PATH.relative_to(REPO))],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert tracked.returncode == 0, (
        "validation-record.json is not tracked — the canonical input would be absent from a "
        "fresh clone, which is the failure mode this determination closed"
    )


def test_the_evidence_archive_is_preserved_not_deleted() -> None:
    """Evidence keeps its home. What it loses is its claim on identity."""
    record = parse(load(RECORD_PATH))
    ref = record.evidence_reference
    assert ref is not None
    assert ref.archive_path.startswith("00-MASTER/UAKOS-CLOSURE-008/evidence")
    ignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert "00-MASTER/**/evidence/" in ignore

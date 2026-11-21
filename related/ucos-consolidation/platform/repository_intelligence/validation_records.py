"""UAKOS-CLOSURE-008 — the canonical validation record, and what may not enter one.

The category error this closes
------------------------------
``00-MASTER/UAKOS-CLOSURE-008/06-VALIDATION-REPORT.md`` embedded the last fourteen matching
lines of ``evidence/verify.log`` verbatim, and ``04-REPOSITORY-CHANGE-REGISTER.md`` recorded
the resulting byte count and content hash. Two canonical artifacts therefore carried, inside
their identity, the stdout of one historical execution on one machine — wall-clock stage
timings, a coverage total, an artifact count. ``.gitignore`` excludes ``00-MASTER/**/evidence/``,
so that transcript was never in the tree at all: a fresh clone rendered the fail-closed
"NOT CAPTURED" branch instead, and the committed registers were provably NOT the rendered
fixed point the CI drift gate asserts them to be.

Two different categories were mixed:

    a deterministic validation RESULT     — repository truth; same commit, same bytes
    an execution TRANSCRIPT               — a historical observation of one run

The result belongs to the canonical layer. The transcript belongs to an evidence archive that
is preserved, referenced, and outside canonical identity.

What this module is
-------------------
The deterministic half. A :data:`SCHEMA` record states WHAT was validated, under WHICH
contract, and WITH WHAT RESULT — and nothing that a second run of the same command could
change. :func:`validate` refuses a record that has drifted back toward a transcript, so
"put the log back in the report" is unrepresentable rather than merely undone once.

The sharpest rule is :data:`_DIGEST_KEYS` on the evidence reference. A record may name the
archive it came from; it may NOT carry that archive's content hash or byte count. A digest of
a transcript is the transcript's identity wearing a deterministic costume — re-run the
command and the canonical bytes move again, which is the exact defect being closed. The
reference is an ID, never a measurement.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

SCHEMA = "ucos-canonical-validation-record"

#: The two terminal results. A validation is a decision, not a narrative.
RESULTS: frozenset[str] = frozenset({"PASS", "FAIL"})

#: Input classes that are historical observations of an execution event rather than
#: repository truth. Shared with the generated-artifact registry, which refuses them as
#: inputs to any CANONICAL artifact.
EXECUTION_OBSERVATION_CLASSIFICATIONS: frozenset[str] = frozenset(
    {"EXECUTION_TRANSCRIPT", "LOCAL_RUNTIME", "ENVIRONMENTAL_OBSERVATION"}
)

#: Keys that name an execution observation. Their presence anywhere in a record is a finding
#: regardless of what they hold — the field name alone declares the wrong category.
FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "cwd",
        "duration",
        "duration_s",
        "elapsed",
        "env",
        "environment",
        "finished_at",
        "hostname",
        "log",
        "machine",
        "output",
        "pid",
        "python_version",
        "runtime",
        "seconds",
        "started_at",
        "stderr",
        "stdout",
        "timestamp",
        "toolchain",
        "transcript",
        "user",
        "wall_clock",
    }
)

#: Keys that would re-couple canonical identity to transcript BYTES. Refused on the evidence
#: reference specifically: naming the archive is a pointer, measuring it is a dependency.
_DIGEST_KEYS: frozenset[str] = frozenset({"bytes", "digest", "sha1", "sha256", "size"})

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_ABS_PATH = re.compile(r"/(?:Users|home|private|var|tmp|opt|Volumes)/")
_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}|\b\d{1,2}:\d{2}:\d{2}\b")
_WALL_CLOCK = re.compile(r"\b\d+(?:\.\d+)?\s*(?:s|ms|sec|secs|seconds|minutes)\b")

_CONTENT_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (_ANSI, "an ANSI escape (terminal output)"),
    (_ABS_PATH, "a machine-local absolute path"),
    (_TIMESTAMP, "a timestamp"),
    (_WALL_CLOCK, "a wall-clock measurement"),
)


@dataclass(frozen=True)
class EvidenceReference:
    """A pointer INTO the non-canonical evidence archive. Never its content."""

    evidence_id: str
    archive_path: str
    member: str
    classification: str


@dataclass(frozen=True)
class ValidationRecord:
    """The deterministic result of running one declared validation contract."""

    validation_id: str
    contract_id: str
    command: str
    result: str
    stages: tuple[tuple[str, str], ...]
    artifact_references: tuple[str, ...]
    stages_digest: str
    evidence_reference: EvidenceReference | None

    @property
    def passed(self) -> bool:
        return self.result == "PASS"

    @property
    def stage_names(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self.stages)


def load(path: Path) -> dict:
    """The record document. Absence is the caller's decision to make, not this module's."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse(doc: Mapping) -> ValidationRecord:
    """Project a validated document onto the record model."""
    ref = doc.get("evidence_reference") or None
    return ValidationRecord(
        validation_id=str(doc.get("validation_id", "")),
        contract_id=str(doc.get("contract", {}).get("contract_id", "")),
        command=str(doc.get("contract", {}).get("command", "")),
        result=str(doc.get("result", "")),
        stages=tuple(
            (str(s.get("stage", "")), str(s.get("result", ""))) for s in doc.get("stages", ())
        ),
        artifact_references=tuple(
            str(a) for a in doc.get("contract", {}).get("artifact_references", ())
        ),
        stages_digest=str(doc.get("contract", {}).get("stages_digest", "")),
        evidence_reference=(
            EvidenceReference(
                evidence_id=str(ref.get("evidence_id", "")),
                archive_path=str(ref.get("archive_path", "")),
                member=str(ref.get("member", "")),
                classification=str(ref.get("classification", "")),
            )
            if ref
            else None
        ),
    )


def _walk(node: object, trail: str = "") -> list[tuple[str, str, object]]:
    """Every (trail, key, value) in the document, so no rule can be evaded by nesting."""
    found: list[tuple[str, str, object]] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            here = f"{trail}.{key}" if trail else str(key)
            found.append((here, str(key), value))
            found.extend(_walk(value, here))
    elif isinstance(node, Sequence) and not isinstance(node, str | bytes):
        for i, value in enumerate(node):
            here = f"{trail}[{i}]"
            found.extend(_walk(value, here))
    return found


def validate(doc: Mapping) -> list[str]:
    """Every record invariant, as findings. Empty means the record is canonical-safe."""
    findings: list[str] = []

    if doc.get("schema") != SCHEMA:
        findings.append(f"schema is {doc.get('schema')!r}, expected {SCHEMA!r}")

    for field in ("validation_id", "result"):
        if not doc.get(field):
            findings.append(f"no {field}")
    for field in ("contract_id", "command"):
        if not doc.get("contract", {}).get(field):
            findings.append(f"contract: no {field}")

    result = doc.get("result")
    if result is not None and result not in RESULTS:
        findings.append(f"result {result!r} is not one of {sorted(RESULTS)}")

    stages = doc.get("stages") or []
    if not stages:
        findings.append("no stages — a validation with no gates asserts nothing")
    for stage in stages:
        name, outcome = stage.get("stage"), stage.get("result")
        if not name:
            findings.append("a stage carries no name")
        if outcome not in RESULTS:
            findings.append(f"stage {name!r}: result {outcome!r} is not one of {sorted(RESULTS)}")
    if result == "PASS" and any(s.get("result") != "PASS" for s in stages):
        findings.append("result is PASS while a stage is not — fails closed")

    for trail, key, value in _walk(doc):
        if key in FORBIDDEN_KEYS:
            findings.append(
                f"{trail}: key {key!r} names an execution observation; the canonical layer "
                f"records the result, not the run"
            )
        if isinstance(value, str):
            for pattern, what in _CONTENT_RULES:
                if pattern.search(value):
                    findings.append(f"{trail}: value carries {what}")
            if "\n" in value:
                findings.append(f"{trail}: value is multi-line — captured output, not a result")

    findings.extend(_validate_evidence_reference(doc.get("evidence_reference")))
    return findings


def _validate_evidence_reference(ref: object) -> list[str]:
    if ref is None:
        return []
    if not isinstance(ref, Mapping):
        return ["evidence_reference: not an object"]

    findings: list[str] = []
    for field in ("evidence_id", "archive_path", "classification"):
        if not ref.get(field):
            findings.append(f"evidence_reference: no {field}")

    klass = ref.get("classification")
    if klass and klass not in EXECUTION_OBSERVATION_CLASSIFICATIONS:
        findings.append(
            f"evidence_reference: classification {klass!r} is not one of "
            f"{sorted(EXECUTION_OBSERVATION_CLASSIFICATIONS)} — an evidence archive is a "
            f"historical observation by definition"
        )
    for key in sorted(set(ref) & _DIGEST_KEYS):
        findings.append(
            f"evidence_reference: {key!r} measures the archive's CONTENT; a canonical record "
            f"may reference execution evidence but may not depend on its bytes"
        )
    return findings

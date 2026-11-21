"""UCOS-CL-015 — the generated-artifact registry, and the derived views over it.

One fact, one owner, many views
-------------------------------
"This path is generated output" was expressed in three independent places: each
programme's own declaration, ``00-BOOK/tools/config.py::EXCLUDE_DIR_PREFIXES`` for
registration eligibility, and ``.gitignore`` for the version-control boundary. They
drifted. UCOS-RECON-C2 records the consequence: the eleven RIE outputs were admitted to
the Repository Corpus and given permanent identities because ``EXCLUDE_DIR_PREFIXES``
enumerated generated outputs only where they lived under ``00-BOOK/``, and ``intelligence/``
did not exist when that list was authored.

Two producers declared nothing at all — UCOS-AEE-001 and UAIE-000001 emit 33 tracked files
between them and carried no ``outputs`` section.

This module reads the one upstream register and serves the views. It is deliberately
UPSTREAM of every engine it describes: the register is authored, and nothing here consults
an engine's output to decide what that engine produces. That direction is what keeps the
dependency acyclic.

The structural bar
------------------
:func:`validate` refuses a canonical artifact that declares an ENVIRONMENTAL input. That is
the UCOS-CL-005 coverage defect expressed as a rule rather than as a fix: an RIE artifact
naming ``coverage.xml`` in its input closure cannot be declared, so the leak becomes
unrepresentable instead of merely removed once.

CANONICAL_ARTIFACT_INPUT_CLASSIFICATION
---------------------------------------
UAKOS-CLOSURE-008 found the same class of leak one category over: register 06 embedded the
tail of an execution transcript, and register 04 recorded the byte count and content hash that
resulted. The transcript was untracked, so a fresh clone rendered different canonical bytes
than the ones committed. The named invariant closes the class — a CANONICAL artifact may not
declare an ``EXECUTION_TRANSCRIPT``, ``LOCAL_RUNTIME`` or ``ENVIRONMENTAL_OBSERVATION`` input.

The escape is a declaration, not a loophole: mark the artifact ``NON_CANONICAL`` and it may
depend on whatever it likes, because it is then evidence rather than identity. Evidence is
kept. What it may not do is claim to be repository truth.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from platform.repository_intelligence import evidence_universe, validation_records

from engine.omega_infinite.git_provider import GitDiscoveryProvider

REGISTRY_PATH = "00-BOOK/DATA/generated-artifact-registry.json"

#: Input classes that are a historical OBSERVATION of an execution event rather than
#: repository truth (UAKOS-CLOSURE-008). Held as one fact with the canonical validation
#: record model, which classifies the other side of the same boundary.
EXECUTION_OBSERVATION_CLASSIFICATIONS: frozenset[str] = (
    validation_records.EXECUTION_OBSERVATION_CLASSIFICATIONS
)

#: Every input of every declared artifact carries one of these.
INPUT_CLASSIFICATIONS: frozenset[str] = (
    frozenset(
        {
            "TRACKED_DETERMINISTIC",
            "GENERATED_DETERMINISTIC",
            "ENVIRONMENTAL",
            "OPERATIONAL",
            "EXTERNAL",
            "UNKNOWN",
        }
    )
    | EXECUTION_OBSERVATION_CLASSIFICATIONS
)

#: Classifications a *canonical* artifact may depend on. UNKNOWN is absent by design.
#:
#: ``GENERATED_DETERMINISTIC`` is admitted on ONE condition, enforced below: the input must be
#: declared in ``generated_inputs`` with a producer and a bootstrap path. Without that it is an
#: input a pristine clone cannot obtain, which is how 114 artifacts came to depend on trees
#: whose creation lived only inside one stage of one shell script.
CANONICAL_SAFE_INPUTS: frozenset[str] = frozenset(
    {"TRACKED_DETERMINISTIC", "GENERATED_DETERMINISTIC"}
)

#: The roles that place an artifact OUTSIDE canonical identity. ``EXCLUDED`` says the artifact
#: is not part of the corpus at all; ``NON_CANONICAL`` says it is kept and referenced but makes
#: no identity claim — the marker an execution-evidence archive carries.
NON_CANONICAL_IDENTITY_ROLES: frozenset[str] = frozenset({"EXCLUDED", "NON_CANONICAL"})

#: Every recognised identity role.
IDENTITY_ROLES: frozenset[str] = frozenset({"CANONICAL"}) | NON_CANONICAL_IDENTITY_ROLES


@dataclass(frozen=True)
class GeneratedArtifact:
    artifact_id: str
    canonical_path: str
    producer: str
    owner: str
    capability: str
    lifecycle: str
    input_closure: tuple[str, ...]
    input_classification: dict[str, str]
    deterministic: bool
    environmental_dependencies: tuple[str, ...]
    canonical_identity_role: str
    consumers: tuple[str, ...]
    registration_status: str
    validation_owner: str
    regeneration_command: str
    certification_role: str

    @property
    def canonical(self) -> bool:
        return self.canonical_identity_role == "CANONICAL"


def _artifact(raw: dict) -> GeneratedArtifact:
    return GeneratedArtifact(
        artifact_id=str(raw.get("artifact_id", "")),
        canonical_path=str(raw.get("canonical_path", "")),
        producer=str(raw.get("producer", "")),
        owner=str(raw.get("owner", "")),
        capability=str(raw.get("capability", "")),
        lifecycle=str(raw.get("lifecycle", "")),
        input_closure=tuple(raw.get("input_closure", ())),
        input_classification=dict(raw.get("input_classification", {})),
        deterministic=bool(raw.get("deterministic", False)),
        environmental_dependencies=tuple(raw.get("environmental_dependencies", ())),
        canonical_identity_role=str(raw.get("canonical_identity_role", "")),
        consumers=tuple(raw.get("consumers", ())),
        registration_status=str(raw.get("registration_status", "")),
        validation_owner=str(raw.get("validation_owner", "")),
        regeneration_command=str(raw.get("regeneration_command", "")),
        certification_role=str(raw.get("certification_role", "")),
    )


@dataclass(frozen=True)
class GeneratedInput:
    """A generated file a producer READS. Declared so a pristine clone can obtain it."""

    path: str
    producer: str
    bootstrap_command: str
    bootstrap_stage: str
    tracked: bool
    deterministic: bool

    @property
    def bootstrap_complete(self) -> bool:
        """A stage that says it is not in the bootstrap is a gap, not a path."""
        return bool(self.bootstrap_stage) and "NOT IN THE BOOTSTRAP" not in self.bootstrap_stage

    def covers(self, path: str) -> bool:
        return path == self.path or (self.path.endswith("/") and path.startswith(self.path))


@dataclass(frozen=True)
class ProducerHome:
    """A programme directory and the split between what is authored and what is emitted."""

    owner: str
    home: str
    producer: str
    authored_inputs: tuple[str, ...]


@lru_cache(maxsize=8)
def load(repo: Path) -> tuple[GeneratedArtifact, ...]:
    """Every declared artifact, canonical and environmental alike."""
    doc = _document(Path(repo))
    return tuple(
        _artifact(raw) for raw in [*doc.get("entries", []), *doc.get("environmental_artifacts", [])]
    )


@lru_cache(maxsize=8)
def _document(repo: Path) -> dict:
    return json.loads((Path(repo) / REGISTRY_PATH).read_text(encoding="utf-8"))


def generated_inputs(repo: Path) -> tuple[GeneratedInput, ...]:
    return tuple(
        GeneratedInput(
            path=str(raw.get("path", "")),
            producer=str(raw.get("producer", "")),
            bootstrap_command=str(raw.get("bootstrap_command", "")),
            bootstrap_stage=str(raw.get("bootstrap_stage", "")),
            tracked=bool(raw.get("tracked", False)),
            deterministic=bool(raw.get("deterministic", False)),
        )
        for raw in _document(Path(repo)).get("generated_inputs", [])
    )


def producer_homes(repo: Path) -> tuple[ProducerHome, ...]:
    return tuple(
        ProducerHome(
            owner=str(raw.get("owner", "")),
            home=str(raw.get("home", "")),
            producer=str(raw.get("producer", "")),
            authored_inputs=tuple(raw.get("authored_inputs", ())),
        )
        for raw in _document(Path(repo)).get("producer_homes", [])
    )


def generated_input_for(repo: Path, path: str) -> GeneratedInput | None:
    return next((g for g in generated_inputs(Path(repo)) if g.covers(path)), None)


# --- derived views ----------------------------------------------------------------------


def paths_for_owner(repo: Path, owner: str) -> set[str]:
    """The canonical paths one programme produces.

    This is the view that replaces a hard-coded per-engine list. UCOS-RIB-001 previously
    computed its own from its declaration; it now asks the register, so its answer and the
    registration boundary's answer are the same fact rather than two that can disagree.
    """
    return {a.canonical_path for a in load(Path(repo)) if a.owner == owner}


def producer_of(repo: Path, path: str) -> str | None:
    for a in load(Path(repo)):
        if a.canonical_path == path:
            return a.producer
    return None


def canonical_paths(repo: Path) -> set[str]:
    return {a.canonical_path for a in load(Path(repo)) if a.canonical}


# --- invariants -------------------------------------------------------------------------


def validate(repo: Path) -> list[str]:
    """Every registry invariant, as a list of findings. Empty means the register holds."""
    artifacts = load(Path(repo))
    findings: list[str] = []

    seen: dict[str, str] = {}
    for a in artifacts:
        if not a.canonical_path:
            findings.append(f"{a.artifact_id}: no canonical_path")
            continue
        if a.canonical_path in seen:
            findings.append(
                f"{a.canonical_path}: claimed by two producers "
                f"({seen[a.canonical_path]} and {a.producer})"
            )
        seen[a.canonical_path] = a.producer

        for field, value in (
            ("producer", a.producer),
            ("owner", a.owner),
            ("lifecycle", a.lifecycle),
        ):
            if not value:
                findings.append(f"{a.canonical_path}: no {field}")
        if not a.input_closure:
            findings.append(f"{a.canonical_path}: empty input_closure")

        if a.canonical_identity_role not in IDENTITY_ROLES:
            findings.append(
                f"{a.canonical_path}: unrecognised canonical_identity_role "
                f"{a.canonical_identity_role!r} — expected one of {sorted(IDENTITY_ROLES)}"
            )

        for inp in a.input_closure:
            klass = a.input_classification.get(inp)
            if klass is None:
                findings.append(f"{a.canonical_path}: input {inp!r} has no classification")
            elif klass not in INPUT_CLASSIFICATIONS:
                findings.append(
                    f"{a.canonical_path}: input {inp!r} has unrecognised class {klass!r}"
                )
            elif klass == "UNKNOWN":
                findings.append(f"{a.canonical_path}: input {inp!r} is UNKNOWN — fails closed")
            elif a.canonical and klass in EXECUTION_OBSERVATION_CLASSIFICATIONS:
                # CANONICAL_ARTIFACT_INPUT_CLASSIFICATION — UAKOS-CLOSURE-008.
                findings.append(
                    f"{a.canonical_path}: CANONICAL_ARTIFACT_INPUT_CLASSIFICATION — input "
                    f"{inp!r} is classified {klass}, a historical observation of an execution "
                    f"event; canonical identity may not depend on one. Keep the evidence and "
                    f"reference it, or declare this artifact NON_CANONICAL."
                )
            elif a.canonical and klass not in CANONICAL_SAFE_INPUTS:
                # THE bar. UCOS-CL-005 as a rule rather than a repair.
                findings.append(
                    f"{a.canonical_path}: CANONICAL artifact declares a {klass} input "
                    f"({inp!r}) — canonical identity may not depend on non-tracked state"
                )
            elif klass == "GENERATED_DETERMINISTIC":
                findings.extend(_check_generated_input(repo, a, inp))
            if klass in EXECUTION_OBSERVATION_CLASSIFICATIONS:
                findings.extend(_check_evidence_input(repo, a, inp, klass))
        if a.canonical and a.environmental_dependencies:
            findings.append(
                f"{a.canonical_path}: CANONICAL artifact declares environmental "
                f"dependencies {list(a.environmental_dependencies)}"
            )
        if a.canonical and not a.deterministic:
            findings.append(f"{a.canonical_path}: CANONICAL artifact is not deterministic")
    return findings


def _check_generated_input(repo: Path, a: GeneratedArtifact, inp: str) -> list[str]:
    """GENERATED_INPUT_HAS_PRODUCER_AND_BOOTSTRAP.

    A generated input is admissible into canonical identity only if a pristine clone can
    OBTAIN it: someone produces it, and a named bootstrap path runs that producer. Measured
    consequence of the alternative: 114 artifacts depended on four generated trees whose
    creation existed only inside stage 1b of verify.sh, and a clone that skipped that stage
    rendered different bytes — or, for UCDA, refused to render at all.
    """
    declared = generated_input_for(repo, inp)
    if declared is None:
        return [
            f"{a.canonical_path}: GENERATED_DETERMINISTIC input {inp!r} is not declared in "
            f"generated_inputs — a generated input with no declared producer is an input a "
            f"pristine clone cannot obtain"
        ]
    findings = []
    if not declared.producer:
        findings.append(f"{a.canonical_path}: generated input {inp!r} declares no producer")
    if not declared.bootstrap_command:
        findings.append(
            f"{a.canonical_path}: generated input {inp!r} declares no bootstrap_command"
        )
    if a.canonical and not declared.bootstrap_complete:
        findings.append(
            f"{a.canonical_path}: CANONICAL artifact consumes generated input {inp!r} whose "
            f"bootstrap path is incomplete ({declared.bootstrap_stage!r}) — a clone running the "
            f"declared bootstrap would not have it"
        )
    return findings


def _check_evidence_input(repo: Path, a: GeneratedArtifact, inp: str, klass: str) -> list[str]:
    """EVIDENCE_INPUT_MUST_BE_DECLARED and CERTIFICATION_EVIDENCE_CLASS.

    Evidence may support truth; it may not arrive from a surface nobody declared, and a
    diagnosis or an improvement measurement may never reach a certification outcome.
    """
    try:
        surface = evidence_universe.surface_for(repo, inp)
    except FileNotFoundError:
        return [
            f"{a.canonical_path}: input {inp!r} is classified {klass} but "
            f"{evidence_universe.REGISTRY_PATH} is absent — the class of an evidence input "
            f"cannot be checked against a register that does not exist"
        ]
    if surface is None:
        return [
            f"{a.canonical_path}: input {inp!r} is classified {klass} but resolves to no "
            f"declared evidence surface — see {evidence_universe.REGISTRY_PATH}"
        ]
    findings = []
    if surface.canonical_identity_role != evidence_universe.REQUIRED_IDENTITY_ROLE:
        findings.append(
            f"{a.canonical_path}: evidence surface {surface.surface_id} is not "
            f"{evidence_universe.REQUIRED_IDENTITY_ROLE}"
        )
    if (
        a.certification_role
        and a.certification_role not in {"NONE", "QUALITY_GATE_ONLY"}
        and surface.evidence_class in evidence_universe.CERTIFICATION_FORBIDDEN_CLASSES
    ):
        findings.append(
            f"{a.canonical_path}: certification artifact ({a.certification_role}) consumes a "
            f"{surface.evidence_class} surface ({surface.surface_id}) — R-EV-4"
        )
    return findings


def unregistered_paths(repo: Path) -> list[str]:
    """EVERY_CANONICAL_ARTIFACT_REGISTERED, over every declared producer home.

    A tracked file inside a declared home is one of three things: the producer, an authored
    input, or a generated artifact. Anything else is a file the register does not know about,
    and the register is what every other view derives from — so an unknown file is a hole in
    all of them at once. Adding one now fails closed instead of being discovered by a phase
    gate months later.
    """
    repo = Path(repo)
    # THE PROVIDER, NOT THE TOOL. `ls-files -z` with no further flags is the tracked population,
    # which is TRACKED_CONTENT and the provider's default. Measured before the swap: both return
    # 7,126 paths and the sets are identical, so no verdict here can move.
    tracked = {
        artifact.location.locator for artifact in GitDiscoveryProvider(root=str(repo)).enumerate()
    }
    declared = {a.canonical_path for a in load(repo)}
    findings: list[str] = []
    for home in producer_homes(repo):
        prefix = home.home.rstrip("/") + "/"
        known = declared | {home.producer} | {f"{prefix}{rel}" for rel in home.authored_inputs}
        for path in sorted(p for p in tracked if p.startswith(prefix)):
            if path not in known and path != home.producer:
                findings.append(
                    f"{path}: inside declared home {home.home} but neither a declared generated "
                    f"artifact nor a declared authored input of {home.owner}"
                )
    return findings


def reconcile_owner_view(repo: Path, owner: str, engine_view: Iterable[str]) -> list[str]:
    """Findings where a producer's own idea of its outputs differs from the register."""
    registry = paths_for_owner(repo, owner)
    engine = set(engine_view)
    findings = []
    for missing in sorted(registry - engine):
        findings.append(f"{owner}: registry declares {missing} but the engine does not claim it")
    for extra in sorted(engine - registry):
        findings.append(f"{owner}: engine claims {extra} but the registry does not declare it")
    return findings

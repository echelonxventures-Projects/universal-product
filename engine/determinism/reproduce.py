"""TASK-000032 — Reproducibility harness (EPIC-004, IMP-007 §5/§11).

Proves constitutional determinism by *measuring* it: the same certified blueprint
compiled by the same compiler under the same hermetic environment definition must
produce **byte-identical** output every time (Mandatory Rule 5).

:func:`double_build` compiles a blueprint twice in two isolated environments (A
and B) and compares, byte for byte:

    * generated source (``artifacts/**``)
    * package manifests (``manifest.json``)
    * SBOM (``sbom.json``)
    * signatures (``signature.json``)
    * registry publication payloads (``artifact-record.json``)

On success it returns ``byte_identical = True``. On any divergence it returns
``byte_identical = False`` and a diff report suitable for writing to
``reproducibility_report.json`` (Mandatory Rule 6 — every failure yields evidence).

Blueprints are resolved by id through a :class:`BlueprintProvider`; a canonical
BP-DATA-0001 fixture ships with the framework so the success criterion is directly
executable. The harness reuses the Compiler pipeline verbatim (Mandatory Rule 4)
and writes only to caller-provided temp/output locations (never the corpus).

:func:`compare_initialization` measures the *other* determinism property, which
double_build structurally cannot see: whether a verdict depends on when, or in which
order, a process was initialized. It runs three scenarios in three child interpreters
and compares their verdict digests. See the section comment above it — the two are
deliberately separate instruments over one subject, not one instrument with a flag.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.compiler.pipeline import CompilerPipeline
from engine.compiler.signing import Signer
from engine.determinism.errors import (
    BlueprintResolutionError,
    NonDeterministicOutputError,
    ReproducibilityError,
)
from engine.determinism.hermetic import HermeticEnvironment, hermetic_env
from engine.foundation.config.config import SecretRef
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.registry.adapter import RegistryAdapter

_logger = get_logger("determinism.reproduce")

#: A non-secret, fixed harness signing key. The signature is byte-identical across
#: the two builds because the same key is used for both; this key is a determinism
#: fixture, never a production credential (SEC-04 — production uses ``env://``).
DEFAULT_SIGNING_KEY = b"ec1-determinism-harness-key"

#: Where the shipped example blueprint inputs live (never the certified corpus).
DEFAULT_BLUEPRINTS_DIR = Path(__file__).resolve().parent / "blueprints"

_BP_ID = re.compile(r"^BP-[A-Z]+-\d+$")

#: How a materialised, relative artifact path maps to a comparison category.
_CATEGORY_RULES: tuple[tuple[str, str], ...] = (
    ("manifest.json", "manifests"),
    ("sbom.json", "sbom"),
    ("signature.json", "signatures"),
    ("artifact-record.json", "publication_payloads"),
)
CATEGORIES: tuple[str, ...] = (
    "generated_source",
    "manifests",
    "sbom",
    "signatures",
    "publication_payloads",
)


class BlueprintProvider:
    """Resolves a blueprint id to its declarative document (input to the compiler)."""

    def get(self, blueprint_id: str) -> Mapping[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError


class DirectoryBlueprintProvider(BlueprintProvider):
    """Resolves ``<blueprint_id>.json`` from a directory of blueprint inputs."""

    __slots__ = ("_directory",)

    def __init__(self, directory: str | Path | None = None) -> None:
        self._directory = Path(directory) if directory is not None else DEFAULT_BLUEPRINTS_DIR

    @property
    def directory(self) -> Path:
        return self._directory

    def get(self, blueprint_id: str) -> Mapping[str, Any]:
        if not _BP_ID.match(blueprint_id):
            raise BlueprintResolutionError("invalid blueprint id", blueprint_id=blueprint_id)
        path = self._directory / f"{blueprint_id}.json"
        if not path.is_file():
            raise BlueprintResolutionError(
                "blueprint input not found", blueprint_id=blueprint_id, path=str(path)
            )
        return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True, slots=True)
class FileDiff:
    """A per-file comparison finding between build A and build B."""

    path: str
    category: str
    status: str  # "identical" | "differs" | "only_in_a" | "only_in_b"
    sha256_a: str | None
    sha256_b: str | None

    @property
    def is_identical(self) -> bool:
        return self.status == "identical"

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "category": self.category,
            "status": self.status,
            "sha256_a": self.sha256_a,
            "sha256_b": self.sha256_b,
        }


@dataclass(frozen=True, slots=True)
class ReproducibilityResult:
    """The outcome of a double build (IMP-007 §5/§11)."""

    blueprint_id: str
    byte_identical: bool
    environment_fingerprint: str
    artifact_id_a: str
    artifact_id_b: str
    category_identical: dict[str, bool]
    diffs: tuple[FileDiff, ...]

    @property
    def divergences(self) -> tuple[FileDiff, ...]:
        """Only the non-identical findings."""
        return tuple(d for d in self.diffs if not d.is_identical)

    def to_report_dict(self) -> dict[str, Any]:
        """A complete, auditable reproducibility report (reproducibility_report.json)."""
        return {
            "reproducibility_report": True,
            "blueprint_id": self.blueprint_id,
            "byte_identical": self.byte_identical,
            "environment_fingerprint": self.environment_fingerprint,
            "artifact_id_a": self.artifact_id_a,
            "artifact_id_b": self.artifact_id_b,
            "artifact_id_match": self.artifact_id_a == self.artifact_id_b,
            "categories": dict(self.category_identical),
            "file_count": len(self.diffs),
            "divergence_count": len(self.divergences),
            "diffs": [d.to_dict() for d in self.diffs],
        }

    def write_report(self, path: str | Path) -> Path:
        """Write the report to ``path`` (used as ``reproducibility_report.json``)."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_report_dict(), sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return target


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _categorize(relative_path: str) -> str:
    for suffix, category in _CATEGORY_RULES:
        if relative_path == suffix:
            return category
    # Everything else is generated source (under ``artifacts/``).
    return "generated_source"


def _index_build_dir(base: Path) -> dict[str, str]:
    """Map every file under ``base`` to its SHA-256, keyed by relative POSIX path."""
    index: dict[str, str] = {}
    for path in sorted(base.rglob("*")):
        if path.is_file():
            index[path.relative_to(base).as_posix()] = _sha256_file(path)
    return index


def compare_builds(base_a: Path, base_b: Path) -> tuple[tuple[FileDiff, ...], dict[str, bool]]:
    """Compare two materialised build directories, byte for byte.

    Returns the ordered per-file diffs and a per-category identical/divergent map.
    """
    index_a = _index_build_dir(base_a)
    index_b = _index_build_dir(base_b)
    all_paths = sorted(set(index_a) | set(index_b))

    diffs: list[FileDiff] = []
    category_identical = dict.fromkeys(CATEGORIES, True)
    seen_category = dict.fromkeys(CATEGORIES, False)
    for relative in all_paths:
        category = _categorize(relative)
        seen_category[category] = True
        digest_a = index_a.get(relative)
        digest_b = index_b.get(relative)
        if digest_a is None:
            status = "only_in_b"
        elif digest_b is None:
            status = "only_in_a"
        elif digest_a == digest_b:
            status = "identical"
        else:
            status = "differs"
        if status != "identical":
            category_identical[category] = False
        diffs.append(
            FileDiff(
                path=relative,
                category=category,
                status=status,
                sha256_a=digest_a,
                sha256_b=digest_b,
            )
        )
    # A category with no files present at all cannot be asserted identical.
    for category in CATEGORIES:
        if not seen_category[category]:
            category_identical[category] = False
    return tuple(diffs), category_identical


def _make_signer(signing_key: bytes | None, key_ref: SecretRef | str | None) -> Signer:
    if key_ref is not None:
        return Signer(key_ref=key_ref)
    return Signer(key=signing_key if signing_key is not None else DEFAULT_SIGNING_KEY)


def _execute_build(
    *,
    blueprint_id: str,
    document: Mapping[str, Any],
    registry: RegistryAdapter,
    signer: Signer,
    output_dir: Path,
    env: HermeticEnvironment,
) -> Path:
    """Compile ``document`` in an isolated environment and return the artifact dir."""
    with env.apply():
        pipeline = CompilerPipeline(registry, signer=signer, output_dir=output_dir)
        result = pipeline.compile_one(document)
    if not result.success or result.published is None:
        gap = result.gap_report.to_dict() if result.gap_report else {}
        raise ReproducibilityError(
            "a reproducibility build failed to produce artifacts",
            blueprint_id=blueprint_id,
            gap=gap,
        )
    return Path(result.published.output_dir)


def double_build(
    bp_id: str,
    *,
    registry: RegistryAdapter | None = None,
    provider: BlueprintProvider | None = None,
    signing_key: bytes | None = None,
    key_ref: SecretRef | str | None = None,
    output_root: str | Path | None = None,
    strict: bool = False,
) -> ReproducibilityResult:
    """Build ``bp_id`` twice in isolated environments and compare byte for byte.

    Returns a :class:`ReproducibilityResult` with ``byte_identical`` set. With
    ``strict=True`` a divergence additionally raises
    :class:`NonDeterministicOutputError` (evidence is still attached).
    """
    env = hermetic_env()
    env.verify_toolchain()
    resolver = provider if provider is not None else DirectoryBlueprintProvider()
    document = resolver.get(bp_id)
    adapter = registry if registry is not None else RegistryAdapter.open()

    # BC-2: each build constructs its own signer and environment. A single reused
    # signer can carry state from the first compile into the second and mask exactly
    # the initialization-order dependence this harness exists to detect. The registry
    # is a caller-owned read-only view and is shared deliberately.
    with trace("determinism.double_build", blueprint=bp_id):
        with tempfile.TemporaryDirectory(prefix="ec1-repro-") as root:
            base = Path(output_root) if output_root is not None else Path(root)
            base_a = _execute_build(
                blueprint_id=bp_id,
                document=document,
                registry=adapter,
                signer=_make_signer(signing_key, key_ref),
                output_dir=base / "env-a",
                env=hermetic_env(),
            )
            base_b = _execute_build(
                blueprint_id=bp_id,
                document=document,
                registry=adapter,
                signer=_make_signer(signing_key, key_ref),
                output_dir=base / "env-b",
                env=hermetic_env(),
            )
            artifact_id_a = json.loads((base_a / "artifact-record.json").read_text())["artifact_id"]
            artifact_id_b = json.loads((base_b / "artifact-record.json").read_text())["artifact_id"]
            diffs, category_identical = compare_builds(base_a, base_b)

    byte_identical = all(d.is_identical for d in diffs) and all(category_identical.values())
    result = ReproducibilityResult(
        blueprint_id=bp_id,
        byte_identical=byte_identical,
        environment_fingerprint=env.fingerprint(),
        artifact_id_a=artifact_id_a,
        artifact_id_b=artifact_id_b,
        category_identical=category_identical,
        diffs=diffs,
    )
    if byte_identical:
        _logger.info("determinism.reproducible", blueprint=bp_id, files=len(diffs))
    else:
        _logger.error(
            "determinism.divergence",
            blueprint=bp_id,
            divergences=len(result.divergences),
        )
        if strict:
            raise NonDeterministicOutputError(
                "independent executions produced divergent output",
                blueprint_id=bp_id,
                divergences=[d.to_dict() for d in result.divergences],
            )
    return result


# --------------------------------------------------------------------------- #
# BC-2 — cross-process initialization independence                             #
# --------------------------------------------------------------------------- #
#
# WHAT THIS IS NOT. :func:`double_build` proves PATH REPRODUCIBILITY — the same input
# compiled twice yields the same bytes. Both of its builds run inside ONE interpreter, so
# every module global either side touches is already whatever the first side left it. That
# is the right shape for the property it measures and the wrong shape for a different one:
# whether a verdict depends on WHEN, or IN WHICH ORDER, the process was initialized. TA-26
# records that the two properties are distinct, and until this comparator existed nothing
# in the repository measured the second — which is the whole of blocker BC-2. The defect
# it detects is a separate transformation's to fix; BC-2 is the inability to SEE it.
#
# THE CONDITION IT CAN NOW SEE. The identifier kind space is process-global mutable module
# state: ``engine/registry/universal/identity.py`` fixes 29 core kinds in an enum and holds
# an initially empty ``_EXTENSION_KIND_CODES`` that only a *call* fills. Same commit, zero
# file changes, ``is_well_formed("UCOS-CLSS-8966ca9e8d02")`` is False in a fresh
# interpreter and True after ``engine.ceu.catalog.bootstrap()``; 43 of the 72 admissible
# kinds are in that state.
#
# THREE CHILD PROCESSES, NOT THREE FUNCTION CALLS. A scenario is honest only if its
# interpreter has never seen the others: a fresh ``sys.executable`` per scenario is the
# only arrangement in which "before initialization" is a real state rather than a name for
# whatever the previous call happened to leave behind.
#
#   A  fresh interpreter, no initialization call at all
#   B  fresh interpreter, the declared bootstrap
#   C  fresh interpreter, the same declared state reached by the reverse arrival order
#
# THE CHILD IMPORTS NOTHING OF THIS MODULE. It is handed a source string and a request,
# and imports only the identity authority plus whatever a named step needs. Re-entering
# this module would drag the compiler, the registry adapter and their transitive imports
# into scenario A, and "no initialization call" would then mean "no initialization call
# except the several hundred this harness performed on the way in".
#
# WHAT IT REFUSES AND WHAT IT DISCLOSES. A ≠ B over an EXTENSION kind is the open
# extension space behaving exactly as UCKP-ART-17 declares — admitted by registration,
# never by amendment — so it is reported with its localised authority and does not move
# the verdict. A ≠ B over a CORE kind is hidden runtime state deciding truth, and is
# refused. B ≠ C is refused unconditionally: two admissible orders that reach one declared
# state may not disagree, and an order-dependent verdict has no innocent reading.
# Collapsing the two classes into one would leave the gate either blind or permanently
# red, and neither of those is a measurement.
#
# PURE. Children import, initialize and answer on stdout; nothing writes. The comparator
# spawns, reads and compares. No clock, no network, no file written anywhere — including
# gitignored paths — so a verdict is reproducible and the gate cannot dirty the tree.

#: The subject the closure plan names as the known initialization-dependent identifier.
#: It is the positive control: a comparator that reports clean on this one is worthless,
#: so the gate refuses when its own control goes undetected.
POSITIVE_CONTROL_SUBJECT = "UCOS-CLSS-8966ca9e8d02"

#: The module a child imports to ask whether an identifier is well formed. It is a
#: import path and nothing else: the authority over identity is UCKP-ART-05, and a
#: constant here naming one would be a second place to look for it.
IDENTITY_MODULE = "engine.registry.universal.identity"

#: What a child interpreter executes. Held as source rather than imported for the reason
#: the section comment gives: the child must not import this module. A step is a
#: ``"module:attribute"`` reference the child resolves by import — never source from the
#: caller, which would measure the caller rather than the repository, and never a name
#: this module maps to a target, which would be one more table to keep in step with the
#: modules it dispatches to.
_PROBE_SOURCE = """\
import importlib, json, os, sys

request = json.loads(sys.stdin.read())
for step in request["steps"]:
    module_name, _, attribute = step.partition(":")
    getattr(importlib.import_module(module_name), attribute)()

identity = importlib.import_module(request["authority"])
kinds = list(identity.kind_names())
json.dump(
    {
        "pid": os.getpid(),
        "kinds": kinds,
        "core": sorted(kind.value for kind in identity.RegistryKind),
        "codes": {kind: identity.resolve_kind_code(kind) for kind in kinds},
        "prefix": identity.ID_PREFIX,
        "verdicts": [[s, bool(identity.is_well_formed(s))] for s in request["subjects"]],
    },
    sys.stdout,
)
"""


@dataclass(frozen=True, slots=True)
class InitializationScenario:
    """One initialization arrangement, executed in an interpreter of its own."""

    name: str
    description: str
    steps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "steps": list(self.steps)}


#: The three arrangements the closure plan declares. Ordered; A is the uninitialized one,
#: and the pair rule below reads "neither side is A" as "order only".
SCENARIOS: tuple[InitializationScenario, ...] = (
    InitializationScenario("A", "fresh interpreter, no initialization call", ()),
    InitializationScenario(
        "B", "fresh interpreter, the declared bootstrap", ("engine.ceu.catalog:bootstrap",)
    ),
    InitializationScenario(
        "C",
        "fresh interpreter, the declared state reached in the reverse arrival order",
        (
            "engine.ceu.catalog:declare_forms_reversed",
            "engine.ceu.catalog:bootstrap",
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class ScenarioObservation:
    """What one child interpreter saw, and the pid proving it was its own process."""

    scenario: str
    steps: tuple[str, ...]
    pid: int
    kinds: tuple[str, ...]
    verdicts: tuple[tuple[str, bool], ...]

    @property
    def verdict_map(self) -> dict[str, bool]:
        return dict(self.verdicts)

    def digest(self) -> str:
        """A canonical digest of the verdict set — the comparison primitive, not prose."""
        payload = json.dumps(
            {"kinds": list(self.kinds), "verdicts": [list(v) for v in self.verdicts]},
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario,
            "steps": list(self.steps),
            "pid": self.pid,
            "kinds_visible": len(self.kinds),
            "verdict_digest": self.digest(),
        }


@dataclass(frozen=True, slots=True)
class InitializationDivergence:
    """One subject on which two interpreters disagreed, with the authority localised."""

    left: str
    right: str
    subject: str
    kind: str
    left_verdict: bool
    right_verdict: bool
    standing: str
    authority: str

    @property
    def refused(self) -> bool:
        return self.standing == "REFUSED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair": f"{self.left}|{self.right}",
            "subject": self.subject,
            "kind": self.kind,
            "left_verdict": self.left_verdict,
            "right_verdict": self.right_verdict,
            "standing": self.standing,
            "authority": self.authority,
        }


@dataclass(frozen=True, slots=True)
class InitializationIndependenceResult:
    """The A/B, A/C and B/C comparison, with its coverage stated rather than implied."""

    observations: tuple[ScenarioObservation, ...]
    divergences: tuple[InitializationDivergence, ...]
    core_kinds: tuple[str, ...]
    extension_kinds: tuple[str, ...]
    compared_kinds: tuple[str, ...]
    subjects: tuple[str, ...]

    @property
    def refusals(self) -> tuple[InitializationDivergence, ...]:
        return tuple(d for d in self.divergences if d.refused)

    @property
    def disclosed(self) -> tuple[InitializationDivergence, ...]:
        return tuple(d for d in self.divergences if not d.refused)

    @property
    def positive_control_detected(self) -> bool:
        """Was the known initialization-dependent subject actually caught?"""
        return any(d.subject == POSITIVE_CONTROL_SUBJECT for d in self.divergences)

    @property
    def isolated(self) -> bool:
        """True iff every scenario ran in a process of its own."""
        pids = [o.pid for o in self.observations]
        return len(set(pids)) == len(pids)

    @property
    def independent(self) -> bool:
        """True iff nothing was refused, the control was caught and isolation held."""
        return self.isolated and self.positive_control_detected and not self.refusals

    def matrix(self) -> dict[str, bool]:
        """Pairwise identity of the verdict digests — ``{"A|B": False, ...}``."""
        digests = {o.scenario: o.digest() for o in self.observations}
        names = [o.scenario for o in self.observations]
        return {
            f"{left}|{right}": digests[left] == digests[right]
            for index, left in enumerate(names)
            for right in names[index + 1 :]
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "independent": self.independent,
            "isolated": self.isolated,
            "positive_control": {
                "subject": POSITIVE_CONTROL_SUBJECT,
                "detected": self.positive_control_detected,
            },
            "coverage": {
                "admissible_kinds": len(self.compared_kinds),
                "compared_kinds": list(self.compared_kinds),
                "core_kinds": len(self.core_kinds),
                "extension_kinds": len(self.extension_kinds),
                "subjects": len(self.subjects),
                "$statement": (
                    "Every admissible kind the declared initialization reaches was compared, "
                    "one probe identifier each, plus the named positive control. Coverage is "
                    "stated as a list rather than claimed as total: a kind registered after "
                    "this run is outside it and has to be measured again."
                ),
            },
            "observations": [o.to_dict() for o in self.observations],
            "matrix": self.matrix(),
            "refused": [d.to_dict() for d in self.refusals],
            "disclosed": [d.to_dict() for d in self.disclosed],
        }


def _repository_root() -> Path:
    """The directory a child interpreter must start in to import this package."""
    return Path(__file__).resolve().parents[2]


def _probe_subject(prefix: str, code: str) -> str:
    """A well-formed probe identifier for ``code``, derived rather than authored.

    The suffix is a digest of the code, so the subject set is a function of the kind space
    and never a list somebody has to remember to extend.
    """
    return f"{prefix}-{code}-{hashlib.sha256(code.encode('utf-8')).hexdigest()[:12]}"


def _run_scenario(
    scenario: InitializationScenario, subjects: Sequence[str], *, cwd: Path
) -> ScenarioObservation:
    """Run one scenario in a child interpreter and return what that interpreter saw."""
    request = json.dumps(
        {
            "steps": list(scenario.steps),
            "authority": IDENTITY_MODULE,
            "subjects": list(subjects),
        }
    )
    completed = subprocess.run(  # noqa: S603 - fixed argv, no shell, request is our own json
        [sys.executable, "-c", _PROBE_SOURCE],
        input=request,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        check=False,
    )
    if completed.returncode != 0:
        raise ReproducibilityError(
            "an initialization probe did not complete",
            scenario=scenario.name,
            returncode=completed.returncode,
            stderr=completed.stderr[-2000:],
        )
    try:
        answer = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ReproducibilityError(
            "an initialization probe produced no readable verdict",
            scenario=scenario.name,
            stdout=completed.stdout[-2000:],
        ) from exc
    return ScenarioObservation(
        scenario=scenario.name,
        steps=scenario.steps,
        pid=int(answer["pid"]),
        kinds=tuple(answer["kinds"]),
        verdicts=tuple((str(s), bool(v)) for s, v in answer["verdicts"]),
    )


def _classify(
    left: ScenarioObservation, right: ScenarioObservation, kind: str, core: frozenset[str]
) -> tuple[str, str]:
    """The standing of one divergence, and where its authority localises."""
    if "A" not in (left.scenario, right.scenario):
        return (
            "REFUSED",
            "two admissible arrival orders reached one declared state and disagreed — "
            "arrival order is deciding truth, which no ordering is entitled to do",
        )
    if kind in core:
        return (
            "REFUSED",
            f"{IDENTITY_MODULE}.RegistryKind — a core kind is fixed at import, so a "
            "verdict about one that moves with initialization is hidden runtime state",
        )
    return (
        "DISCLOSED",
        f"{IDENTITY_MODULE}._EXTENSION_KIND_CODES — the open extension space "
        "UCKP-ART-17 requires. A kind admitted by registration is unknown before that "
        "registration and known after it: that is the mechanism working, not a defect",
    )


def compare_initialization(
    *, cwd: Path | str | None = None, scenarios: Sequence[InitializationScenario] | None = None
) -> InitializationIndependenceResult:
    """Run the declared scenarios in separate interpreters and compare their verdicts.

    The subject set is derived in two passes: a census child reports every kind the
    declared initialization reaches together with the code each mints under, and the
    scenarios are then asked about one probe identifier per kind. Deriving it means a kind
    registered next year is compared without editing anything here.
    """
    root = Path(cwd) if cwd is not None else _repository_root()
    arrangement = tuple(scenarios) if scenarios is not None else SCENARIOS

    census_request = json.dumps(
        {
            "steps": ["engine.ceu.catalog:bootstrap"],
            "authority": IDENTITY_MODULE,
            "subjects": [],
        }
    )
    census = subprocess.run(  # noqa: S603 - fixed argv, no shell, request is our own json
        [sys.executable, "-c", _PROBE_SOURCE],
        input=census_request,
        capture_output=True,
        text=True,
        cwd=str(root),
        check=False,
    )
    if census.returncode != 0:
        raise ReproducibilityError(
            "the kind-space census did not complete",
            returncode=census.returncode,
            stderr=census.stderr[-2000:],
        )
    seen = json.loads(census.stdout)
    codes: dict[str, str] = dict(seen["codes"])
    prefix = str(seen["prefix"])
    core = frozenset(seen["core"])

    by_code = {code: kind for kind, code in codes.items()}
    subjects = [_probe_subject(prefix, code) for code in sorted(by_code)]
    subjects.append(POSITIVE_CONTROL_SUBJECT)
    kind_of = {subject: by_code.get(subject.split("-")[1], "") for subject in subjects}

    observations = tuple(_run_scenario(s, subjects, cwd=root) for s in arrangement)

    divergences: list[InitializationDivergence] = []
    for index, left in enumerate(observations):
        left_map = left.verdict_map
        for right in observations[index + 1 :]:
            right_map = right.verdict_map
            for subject in subjects:
                if left_map.get(subject) == right_map.get(subject):
                    continue
                kind = kind_of.get(subject, "")
                standing, authority = _classify(left, right, kind, core)
                divergences.append(
                    InitializationDivergence(
                        left=left.scenario,
                        right=right.scenario,
                        subject=subject,
                        kind=kind,
                        left_verdict=bool(left_map.get(subject)),
                        right_verdict=bool(right_map.get(subject)),
                        standing=standing,
                        authority=authority,
                    )
                )

    admissible = tuple(sorted(codes))
    return InitializationIndependenceResult(
        observations=observations,
        divergences=tuple(divergences),
        core_kinds=tuple(sorted(core)),
        extension_kinds=tuple(k for k in admissible if k not in core),
        compared_kinds=admissible,
        subjects=tuple(subjects),
    )


def initialization_gate(argv: Sequence[str] | None = None) -> int:
    """``--gate`` entry: 0 independent, 1 a divergence was refused, 2 no verdict reached."""
    quiet = "--quiet" in tuple(argv or ())
    try:
        result = compare_initialization()
    except (ReproducibilityError, OSError, ValueError) as exc:
        print(f"initialization independence: FAULT — no verdict could be reached: {exc}")
        return 2

    if not quiet or not result.independent:
        print("-- BC-2 cross-process initialization independence -------------------")
        print(f"  scenarios               : {', '.join(o.scenario for o in result.observations)}")
        print(f"  genuine isolation       : {result.isolated} (distinct child pids)")
        print(f"  admissible kinds        : {len(result.compared_kinds)} compared")
        print(f"    core, fixed at import : {len(result.core_kinds)}")
        print(f"    extension, registered : {len(result.extension_kinds)}")
        print(f"  subjects                : {len(result.subjects)}")
        print(f"  positive control        : detected={result.positive_control_detected}")
        print(f"  verdict digest identity : {result.matrix()}")
        print(f"  disclosed divergences   : {len(result.disclosed)} (open extension space)")
        print(f"  refused divergences     : {len(result.refusals)}")
    if not result.isolated:
        print("  REFUSED isolation — two scenarios shared one interpreter")
    if not result.positive_control_detected:
        print(
            "  REFUSED positive control — the known initialization-dependent subject went "
            "undetected, so a clean verdict from this comparator would mean nothing"
        )
    for divergence in result.refusals:
        print(f"  REFUSED {divergence.left}|{divergence.right} {divergence.subject}")
        print(f"          {divergence.authority}")
    return 0 if result.independent else 1


def main(argv: list[str] | None = None) -> int:
    """CLI entry: ``python -m engine.determinism.reproduce [BP-ID ...]``.

    Runs a double build per blueprint against the real registry, writes
    determinism evidence and (on divergence) ``reproducibility_report.json``, and
    exits non-zero on any byte-level divergence (the CI gate contract).
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="ec1-determinism", description="EC-1 reproducibility gate"
    )
    parser.add_argument("blueprints", nargs="*", default=["BP-DATA-0001"])
    parser.add_argument("--evidence-dir", default="determinism-evidence")
    parser.add_argument(
        "--gate",
        action="store_true",
        help="run the cross-process initialization-independence comparator instead",
    )
    parser.add_argument("--quiet", action="store_true", help="print only on a refusal")
    args = parser.parse_args(argv)

    # The two gates share an entry point and never a run: the comparator writes nothing
    # and takes no evidence directory, so mixing them would give one verdict two planes
    # and make a refusal ambiguous about which property failed.
    if args.gate:
        return initialization_gate(["--quiet"] if args.quiet else [])

    blueprints = args.blueprints or ["BP-DATA-0001"]

    evidence_dir = Path(args.evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    key_ref = "env://UCOS_DETERMINISM_KEY" if "UCOS_DETERMINISM_KEY" in _os_environ() else None
    overall_ok = True
    summary: list[dict[str, Any]] = []
    for bp_id in blueprints:
        result = double_build(bp_id, key_ref=key_ref)
        summary.append(
            {
                "blueprint_id": bp_id,
                "byte_identical": result.byte_identical,
                "artifact_id": result.artifact_id_a,
                "divergence_count": len(result.divergences),
            }
        )
        result.write_report(evidence_dir / f"{bp_id}-reproducibility_report.json")
        status = "PASS" if result.byte_identical else "FAIL"
        print(f"[{status}] double_build({bp_id!r}) byte_identical={result.byte_identical}")
        overall_ok = overall_ok and result.byte_identical

    evidence = {
        "determinism_evidence": True,
        "environment": hermetic_env().to_dict(),
        "environment_fingerprint": hermetic_env().fingerprint(),
        "results": summary,
        "byte_identical": overall_ok,
    }
    (evidence_dir / "determinism-evidence.json").write_text(
        json.dumps(evidence, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if overall_ok else 1


def _os_environ() -> Mapping[str, str]:
    import os

    return os.environ


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "DEFAULT_SIGNING_KEY",
    "DEFAULT_BLUEPRINTS_DIR",
    "CATEGORIES",
    "IDENTITY_MODULE",
    "POSITIVE_CONTROL_SUBJECT",
    "SCENARIOS",
    "BlueprintProvider",
    "DirectoryBlueprintProvider",
    "FileDiff",
    "InitializationDivergence",
    "InitializationIndependenceResult",
    "InitializationScenario",
    "ReproducibilityResult",
    "ScenarioObservation",
    "compare_builds",
    "compare_initialization",
    "double_build",
    "initialization_gate",
    "main",
]

"""UEC-000001 Part 4 — the laws.

THE RATCHET IS TWO-SIDED, AND THAT IS THE WHOLE MECHANISM.

A repository-wide invariant introduced over a repository that already violates it has exactly
two honest options. Fail on arrival, and be switched off within a week. Or declare a ceiling and
refuse only what exceeds it — at which point the ceiling absorbs every future violation and the
law becomes decoration. This repository contains an instance of the second failure:
``00-MASTER/BASELINE-001/baseline_engine.py:726`` computes ``"vacuous": len(declared) == 0``,
renders it, and does not close the gate on it.

UEC takes neither option. Each ratcheted law refuses when ``measured > ceiling`` — so a NEW
violation fails the build the moment it appears — and ``UEC-L-11`` refuses when
``measured < ceiling`` — so a REPAIRED violation must tighten the ceiling. The satisfied state
is ``measured == ceiling`` exactly. There is no slack for a new defect to hide in, and paying
down debt is a governed edit to the declaration rather than a silent improvement nobody records.

WHAT EACH LAW REFUSES, STATED AS THE ATTACK IT DEFEATS:

    UEC-L-01  a discoverer that went blind reports success over an empty world
    UEC-L-02  an enforcement artifact is deleted                          (measured: E4)
    UEC-L-03  an enforcement artifact is added outside governance
    UEC-L-04  an engine exists that nothing invokes
    UEC-L-05  a detector ships with no test that can kill it             (measured: 18 of 46)
    UEC-L-06  a protection has exactly one point of failure              (measured: 14 of 46)
    UEC-L-07  a declaration is loaded by nothing                         (measured: 3 inert)
    UEC-L-08  a certification identity does not exist at all             (measured: UISD)
    UEC-L-09  the closure mechanism is outside its own closure           (discovery D-09)
    UEC-L-10  an artifact belongs to neither plane, so no mechanism sees it
    UEC-L-11  assurance falls without anyone recording that it fell
    UEC-L-12  the escape hatch grows without an owner, a reason or a bound
"""

from __future__ import annotations

import copy
import importlib
import json
import os
import pathlib
import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from engine.enforcement_closure import discovery
from engine.enforcement_closure.declaration import Declaration, load
from engine.enforcement_closure.model import (
    HOLDS,
    KIND_DECLARATION,
    KIND_ENGINE,
    KIND_MODULE_GATE,
    REFUSED,
    Artifact,
    EnforcementError,
)
from engine.uckp.canonical import content_hash

Findings = list[str]

#: Substrings that constitute a certification identity. Deliberately three, because the
#: repository mints digests three ways: ``content_hash`` (Layer Zero), a bare ``sha256``, and a
#: local ``digest``/``seal`` helper. A law recognising only one of them would report a false
#: absence for two thirds of the surface.
DIGEST_MARKERS = ("content_hash", "sha256", "def digest", "def seal")


class Probe:
    """Everything the laws measure, computed once.

    A law that re-derives its own population is a law whose population can disagree with its
    neighbour's, which ``UCOS-UFC-001 UFC-16`` forbids and which this repository has already
    paid for once: two ownership determinations over one population reported different numbers.
    """

    def __init__(self, declaration: Declaration, *, repository: str) -> None:
        self.declaration = declaration
        self.root = repository
        self.paths = discovery.tracked_paths(repository)
        self.located = discovery.discover(declaration.rules, repository, self.paths)
        self.artifacts: tuple[Artifact, ...] = tuple(
            artifact for group in self.located.values() for artifact in group
        )
        workflows = [
            artifact
            for artifact in self.artifacts
            if artifact.kind == declaration.rule(artifact.rule_id).kind
            and artifact.identity.startswith(".github/workflows/")
        ]
        self.corpus = discovery.invocation_corpus(repository, workflows)
        self.tests = discovery.test_corpus(repository, self.paths, declaration.testpaths)
        #: ``source_evidence`` per tracked module, with only the TEST roots excluded. UEC's own
        #: package is deliberately NOT excluded: it consumes its own declaration through the
        #: evaluated constant ``DECLARATION_RELATIVE``, and exempting the package would make
        #: UEC's declaration report as inert — a self-serving exclusion in the opposite
        #: direction. Docstring mentions are already excluded by ``source_evidence``, which is
        #: what separates "this module explains that nothing loads ceu-declaration.json" from
        #: "this module loads it".
        self.sources = discovery.source_corpus(
            repository, self.paths, exclude=tuple(declaration.testpaths)
        )
        self.engines: tuple[Artifact, ...] = tuple(
            a for a in self.artifacts if a.kind in (KIND_ENGINE, KIND_MODULE_GATE)
        )
        self.declarations: tuple[Artifact, ...] = tuple(
            a for a in self.artifacts if a.kind == KIND_DECLARATION
        )
        self._invokers: dict[str, tuple[str, ...]] = {
            a.key(): discovery.invokers(a, self.corpus) for a in self.artifacts
        }
        self._tests: dict[str, tuple[str, ...]] = {
            a.key(): discovery.test_bindings(a, self.tests) for a in self.artifacts
        }
        self._refusals: dict[str, frozenset[str]] = {}
        self._consumers: dict[str, tuple[str, ...]] = {
            a.key(): discovery.consumers(a, self.sources) for a in self.declarations
        }

    def invokers(self, artifact: Artifact) -> tuple[str, ...]:
        return self._invokers[artifact.key()]

    def canonical_lane_text(self) -> str:
        """The canonical verification entry point's own source, read once.

        Declared rather than hardcoded: the path comes from the declaration, so a repository
        that renames its entry point says so there and not here.
        """
        entry = str(self.declaration.canonical_entry_point or "verify.sh")
        target = pathlib.Path(self.root) / entry
        try:
            return target.read_text(encoding="utf-8")
        except OSError:
            return ""

    def reaches_canonical_lane(self, artifact: Artifact, lane: str) -> bool:
        """True iff the canonical lane invokes this engine, by path OR by module form.

        Both forms count because verify.sh uses both: `$PY -m engine.universal_discovery`
        never names engine/universal_discovery/gate.py. Matching paths alone reported a
        false gap when this was first measured.
        """
        if not lane:
            return False
        path = artifact.key().split("::", 1)[-1]
        if path in lane:
            return True
        if any(str(name).endswith("verify.sh") for name in self.invokers(artifact)):
            return True
        parts = path.split("/")
        if len(parts) >= 2:
            package = f"{parts[0]}.{parts[1]}"
            if re.search(r"-m\s+" + re.escape(package) + r"\b", lane):
                return True
        return False

    def refusal_shapes(self, where: str) -> frozenset[str]:
        """The refusal shapes one test module contains, read from its AST and memoised.

        Deliberately NOT read from ``self.tests``: that corpus holds ``source_evidence``,
        which keeps string constants and imports and therefore cannot see a call or an
        assertion. A forged refusal is a code shape.
        """
        cached = self._refusals.get(where)
        if cached is None:
            witness = self.declaration.refusal_witness
            cached = discovery.refusal_shapes(
                discovery.read_text(self.root, where),
                raise_names=witness.get("raise_names", ()),
                finding_names=witness.get("finding_names", ()),
                closed_exits=witness.get("closed_exit_values", ()),
            )
            self._refusals[where] = cached
        return cached

    def test_bindings(self, artifact: Artifact) -> tuple[str, ...]:
        return self._tests[artifact.key()]

    def consumers(self, artifact: Artifact) -> tuple[str, ...]:
        return self._consumers[artifact.key()]

    @property
    def discovered_keys(self) -> frozenset[str]:
        return frozenset(a.key() for a in self.artifacts)

    def counts(self) -> dict[str, int]:
        return {
            "artifacts": len(self.artifacts),
            "engines": len(self.engines),
            "declarations": len(self.declarations),
            "governed": len(self.declaration.governed),
            "withdrawn": len(self.declaration.withdrawals),
            "tests": len(self.tests),
            "tracked": len(self.paths),
        }


# --- the ratcheted measurements -----------------------------------------------------------
#
# Each returns the offending identities. The count is compared to the declared ceiling from
# BOTH sides; the identities are reported so a failure names its subject rather than its size.


def engines_with_no_invoker(probe: Probe) -> list[str]:
    """Engines nothing could actually run. See :func:`every_engine_has_an_invoker`."""
    return sorted(a.identity for a in probe.engines if not probe.invokers(a))


def engines_without_a_test(probe: Probe) -> list[str]:
    return sorted(a.identity for a in probe.engines if not probe.test_bindings(a))


def engines_without_a_refusal_witness(probe: Probe) -> list[str]:
    """Verifiers no OTHER verifier has shown can refuse. UEC-L-14.

    THE GAP THIS CLOSES IS ONE THIS MODULE ALREADY NAMED. ``test_bindings`` says it plainly:
    "Naming is necessary and not sufficient: a test that references an engine has not been
    shown to kill a mutant in it. UEC-L-05 measures the necessary condition and says so."
    Nothing measured the sufficient side, so a verifier could be invoked from two planes,
    named by a test, counted as governed — and still be incapable of refusing anything. A
    verifier that cannot refuse certifies nothing, and a green tick from one is worse than no
    tick, because it licenses the belief that the property was checked.

    A WITNESS FORGES THE VIOLATION. Not "a test mentions this engine" but "a test constructs
    the condition this engine must refuse and observes the refusal". The shapes that count are
    declared in ``refusal_witness_patterns``, never written here: a raised refusal, an
    assertion that findings are non-empty, an assertion of the closed exit code. Holding the
    patterns in data is what lets a future verification plane — one that refuses in a way
    nobody has invented — be admitted by registration rather than by editing this function.

    IT IS EXTERNAL BY CONSTRUCTION. ``test_bindings`` already excludes the artifact's own
    identity, so no verifier can witness itself. That is the property D6 asks for — no
    verifier is self-authoritative — expressed as something this repository can measure,
    rather than as a cycle of mutual attestations nothing could compute.
    """
    witness = probe.declaration.refusal_witness
    accepted = frozenset(witness.get("accepted_shapes", ()))
    if not accepted:
        return sorted(a.identity for a in probe.engines)
    unwitnessed: list[str] = []
    for artifact in probe.engines:
        if not any(
            probe.refusal_shapes(where) & accepted for where in probe.test_bindings(artifact)
        ):
            unwitnessed.append(artifact.identity)
    return sorted(unwitnessed)


def artifacts_with_one_invocation_plane(probe: Probe) -> list[str]:
    return sorted(a.identity for a in probe.engines if len(probe.invokers(a)) < 2)


def declarations_no_code_consumes(probe: Probe) -> list[str]:
    """A declaration no module loads. Every field in it is inert.

    Measured over ``source_evidence`` — evaluated string constants and imports, docstrings
    excluded — because prose that MENTIONS a declaration does not load it. This module's own
    docstrings name the three inert declarations while explaining that nothing reads them, and
    the first draft of this law counted that as consumption.
    """
    return sorted(
        artifact.identity for artifact in probe.declarations if not probe.consumers(artifact)
    )


def declarations_without_a_certification_identity(probe: Probe) -> list[str]:
    """A declaration whose consuming package mints no digest at all.

    The owner is derived from who LOADS the declaration, never from its name: ``UCON-000001`` is
    owned by ``engine/construct/`` and ``UISD-000001`` by ``engine/infinite_scope/``, so a
    name-based guess reported UCON — which demonstrably has a digest — as having none.

    Declarations with no consumer at all are excluded here and counted by UEC-L-07 instead. One
    defect, one law: double-counting would make both ceilings move together and neither
    diagnostic.

    HONEST LIMIT, RECORDED RATHER THAN PAPERED OVER. This measures the NECESSARY condition, that
    a certification identity exists somewhere in the owner. It does NOT measure the SUFFICIENT
    condition, that every semantic edit moves it. ``engine/construct`` passes this law and still
    carries the defect proven by execution: flipping ``blocking`` on ``UCON-L-01`` leaves
    ``declaration_digest`` at ``192c63af…`` byte-identical while ``contract.py:1018`` makes the
    verdict depend on it. The sufficient condition is measured by mutation for UEC's own
    declaration in ``test_enforcement_closure.py`` and for no other programme. Reporting the
    weaker property as the stronger one would be the certification fraud this programme refuses.
    """
    missing: list[str] = []
    for artifact in probe.declarations:
        consuming = probe.consumers(artifact)
        if not consuming:
            continue  # counted by UEC-L-07
        packages = {os.path.dirname(path) for path in consuming}
        text = "".join(
            probe.sources[path]
            for package in packages
            for path in probe.sources
            if os.path.dirname(path) == package
        )
        if not any(marker in text for marker in DIGEST_MARKERS):
            missing.append(artifact.identity)
    return sorted(missing)


def engines_outside_the_canonical_lane(probe: Probe) -> list[str]:
    """Gate engines CI can refuse on and ./verify.sh cannot reach. UEC-L-15.

    UEC-L-04 asks whether an engine is invoked by ANY plane, and UEC-L-06 whether it is
    reachable from more than one. Neither asks whether the CANONICAL one reaches it, and
    that gap has a measured cost. UCL-000001 breached its blocking UCL-V-41 ratchet and
    stayed breached for seventy-seven commits: every one of them landed on a green
    ./verify.sh, because verify.sh has no UCL stage and the gate lives only in a workflow.
    CLAUDE.md tells every contributor that ./verify.sh is the one repository-standard
    command; a gate outside it is a gate the discipline that governs commits cannot see.

    SO THE MEASURE IS NARROW ON PURPOSE. Not "every engine belongs in verify.sh" — several
    are mutation authorities (AEE, RIB, CMG) that must never run inside a read-only lane,
    and forcing them in would be worse than the gap. What is refused is the specific shape
    that let UCL-V-41 hide: CI can fail the build on this engine and the local lane cannot
    tell you so.

    REACHABILITY IS NOT A PATH MATCH. verify.sh invokes several engines as
    `$PY -m engine.<package>`, never by gate-file path, so a matcher keyed on paths reports
    a false gap. That error was made while first measuring this: it read 42 outside the lane
    before the module form was counted, and 41 after. Both forms count here.

    Declaring an engine CI-only is lawful and ratcheted SEPARATELY, for the reason
    DECLARED_DIRECT_CEILING gives in engine/omega_infinite/direct_callers.py: a single
    ceiling can always be satisfied by writing a paragraph, and a ratchet satisfiable by
    explaining measures nothing.
    """
    lane = probe.canonical_lane_text()
    outside: list[str] = []
    for artifact in probe.engines:
        if probe.reaches_canonical_lane(artifact, lane):
            continue
        if not any(str(name).startswith(".github/workflows/") for name in probe.invokers(artifact)):
            continue  # UEC-L-04 owns "invoked by nothing"; this law owns "CI only".
        outside.append(artifact.identity)
    return sorted(outside)


def workflows_that_cannot_run(probe: Probe) -> list[str]:
    """Workflows a runner would reject before executing a step. UEC-L-16.

    TWO REAL DEFECTS, BOTH FROM THIS REPOSITORY, MOTIVATE THIS.

    ``uec-gate.yml`` carried an unquoted plain scalar containing ": " ::

        run: echo "enforcement closure: governed, self-covered, and mutation-resistant"

    YAML forbids that, GitHub could not parse the file, and the run failed with NO step
    name — so UEC-000001, the programme that measures whether every protection is invoked
    from two independent planes, HAD NEVER RUN IN CI. Its own UEC-L-09 asserts that plane
    exists and passed the whole time, because it measures that the workflow file is present
    and names the engine, never that a runner could execute it.

    ``urke-gate.yml`` was then broken a second way, by me, hours after the first was found:
    an edit cut from a step to the next ``- name:`` at the same indent, and because that
    step was the LAST in its job the cut removed the following job's header, ``runs-on``
    and ``steps``, merging its remainder into the previous job. The file still parsed as
    YAML. A parse check alone would not have caught it.

    So this measures BOTH: the scalar shape a parser rejects, and the structure a runner
    requires. It is stdlib-only by necessity — PyYAML is not in the pinned toolchain and
    adding a dependency to measure YAML would engage ISD-L-09.

    IT IS A NECESSARY CONDITION AND NOT A SUFFICIENT ONE, and that is stated rather than
    implied: this is not GitHub's parser, and a workflow passing here can still be rejected
    for something neither defect resembles. The same relationship UEC-L-05 has to UEC-L-14 —
    naming is weaker than witnessing — holds here between "no known-fatal shape" and "a
    runner accepted it". The ceiling is zero because both known shapes are fatal.
    """
    problems: list[str] = []
    for artifact in probe.artifacts:
        if not artifact.identity.startswith(".github/workflows/"):
            continue
        text = discovery.read_text(probe.root, artifact.identity)
        if not text:
            continue
        problems.extend(_workflow_defects(artifact.identity, text))
    return sorted(problems)


def _plain_scalar_holds_a_colon(value: str) -> bool:
    """A plain (unquoted) scalar may not contain ": ". Quoted or block scalars may."""
    value = value.strip()
    if not value or value[0] in "\"'|>&*!{[":
        return False
    return ": " in value


def _workflow_defects(name: str, text: str) -> list[str]:
    """The two shapes a runner refuses, found without a YAML library."""
    found: list[str] = []
    lines = text.splitlines()

    for number, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:]
        key, separator, value = stripped.partition(": ")
        if separator and key and " " not in key and _plain_scalar_holds_a_colon(value):
            found.append(
                f"{name}:{number}: unquoted scalar contains ': ', which no YAML parser "
                f"accepts: {key}"
            )

    in_jobs = False
    current: str | None = None
    declared: list[str] = []
    needed: list[tuple[str, str]] = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 0:
            in_jobs = stripped.startswith("jobs:")
            current = None
            continue
        if not in_jobs:
            continue
        if indent == 2 and stripped.endswith(":") and not stripped.startswith("- "):
            current = stripped[:-1]
            declared.append(current)
        elif current and indent == 4 and stripped.startswith("needs:"):
            value = stripped.partition(":")[2].strip().strip("[]")
            for dependency in (item.strip().strip("\"'") for item in value.split(",")):
                if dependency:
                    needed.append((current, dependency))

    # A `needs:` naming a job that does not exist is refused by the runner BEFORE any step
    # runs, and it is how urke-gate.yml broke: the deleted job was still depended upon, so
    # a file that parsed perfectly was rejected. This is the rule the structural guess
    # missed — the remaining jobs each had runs-on and steps and were entirely well formed.
    known = set(declared)
    for job, dependency in needed:
        if dependency not in known:
            found.append(
                f"{name}: job {job!r} needs {dependency!r}, which this workflow does not "
                f"declare"
            )
    return found


RATCHETED: Mapping[str, tuple[str, Callable[[Probe], list[str]]]] = {
    "engines_with_no_invoker": ("UEC-L-04", engines_with_no_invoker),
    "engines_without_a_test": ("UEC-L-05", engines_without_a_test),
    "engines_without_a_refusal_witness": ("UEC-L-14", engines_without_a_refusal_witness),
    "engines_outside_the_canonical_lane": ("UEC-L-15", engines_outside_the_canonical_lane),
    "workflows_that_cannot_run": ("UEC-L-16", workflows_that_cannot_run),
    "artifacts_with_one_invocation_plane": ("UEC-L-06", artifacts_with_one_invocation_plane),
    "declarations_no_code_consumes": ("UEC-L-07", declarations_no_code_consumes),
    "declarations_without_a_certification_identity": (
        "UEC-L-08",
        declarations_without_a_certification_identity,
    ),
}


# --- the laws -----------------------------------------------------------------------------


def discovery_rules_are_non_vacuous(probe: Probe) -> Findings:
    """UEC-L-01 — every discovery rule meets its declared floor, and no floor is zero."""
    findings: Findings = []
    for rule in probe.declaration.rules:
        located = probe.located.get(rule.rule_id, [])
        if len(located) < rule.floor:
            findings.append(
                f"{rule.rule_id} ({rule.kind}) located {len(located)} artifacts against a "
                f"declared floor of {rule.floor}: the rule has stopped seeing, so every law "
                "quantified over it would be satisfied by absence"
            )
    if not probe.artifacts:
        findings.append(
            "no enforcement artifact was located at all, so the enforcement plane is empty and "
            "every law below would hold vacuously"
        )
    # A FLOOR THAT CAN BE LOWERED IS NOT A FLOOR. A hostile audit set every declared floor to 1
    # and this law stayed green: each rule still located far more than one artifact, so the
    # non-vacuity guarantee evaporated while the measurement kept reporting satisfaction. The
    # floors are the whole substance of this law, so they are ratcheted like every other ceiling
    # — two-sided, on their total, so lowering ANY floor fails immediately and raising one
    # requires the same deliberate act as repairing a violation.
    declared_total = sum(rule.floor for rule in probe.declaration.rules)
    expected_total = probe.declaration.ratchet.get("discovery_floor_total")
    if not isinstance(expected_total, int):
        findings.append(
            "UEC-L-01 has no declared `ratchet.discovery_floor_total`, so the floors that carry "
            "its entire non-vacuity guarantee are enforced by nothing and could be lowered to 1"
        )
    elif declared_total != expected_total:
        direction = "lowered" if declared_total < expected_total else "raised"
        findings.append(
            f"the declared discovery floors total {declared_total} against a ratchet of "
            f"{expected_total}: they were {direction} without a governance act. A floor is a "
            "non-vacuity guarantee, and a guarantee that can be edited downward guarantees "
            "nothing"
        )

    return findings


def declared_enforcement_exists(probe: Probe) -> Findings:
    """UEC-L-02 — every governed enforcement artifact is still there. DELETION."""
    findings: Findings = []
    discovered = probe.discovered_keys
    for row in probe.declaration.governed:
        key = f"{row['kind']}::{row['identity']}"
        if key in discovered:
            continue
        if key in probe.declaration.withdrawn_keys:
            findings.append(
                f"{row['identity']} is both governed and withdrawn; an artifact cannot be "
                "simultaneously required and released"
            )
            continue
        findings.append(
            f"a governed enforcement artifact is gone: {row['kind']} {row['identity']} "
            f"(owner {row['owner']}). Withdrawing it requires a declared withdrawal with an "
            "owner and a reason; deleting it does not"
        )
    return findings


def discovered_enforcement_is_governed(probe: Probe) -> Findings:
    """UEC-L-03 — every located enforcement artifact is governed. UNGOVERNED ADDITION."""
    findings: Findings = []
    governed = probe.declaration.governed_keys | probe.declaration.withdrawn_keys
    for artifact in probe.artifacts:
        if artifact.key() in governed:
            continue
        findings.append(
            f"an ungoverned enforcement artifact is present: {artifact.kind} "
            f"{artifact.identity} (located by {artifact.rule_id}). An enforcement artifact "
            "outside the governed inventory is a protection nothing knows it depends on"
        )
    return findings


def every_engine_has_an_invoker(probe: Probe) -> Findings:
    """UEC-L-04 — nothing enforces by existing. DEAD ENGINE.

    THIS LAW WAS SATISFIED BY A FALSE POSITIVE UNTIL A HOSTILE AUDIT SAID OTHERWISE. Invocation
    was matched with the same generous needles that answer "does a TEST name this engine", where
    a package or a programme directory is honest evidence. For invocation it is not, and the
    audit measured the cost: it pointed every caller of `engine/recursive_knowledge/gate.py` at
    `engine.recursive_knowledge.NOTHING` — the Makefile target, the verify.sh stage and the
    workflow, all three at once — and this law stayed green, because the bare package was still
    a needle and still appeared in every one of those lines. The gate had stopped running and
    nothing said so, which is the same observable state as deleting it.

    `discovery._invocation_needles` now requires a form that could actually execute the
    artifact, and the truth that exposed is recorded here rather than smoothed away: SIX engines
    are invoked by nothing at all. Four are archived UAKOS/USIS phase engines whose only mention
    is the `uakos-archive` target checking that their DIRECTORY exists, and two are
    UAKOS-CLOSURE-008 engines with no caller anywhere in the repository. Every one of them was
    reported as invoked before, on the strength of a directory name appearing in a shell loop.

    A CEILING RATHER THAN ZERO, AND THAT IS MORE ASSURANCE, NOT LESS. The previous state was a
    law that could not fail; this one names its six offenders, caps them, and refuses a seventh.
    UEC-L-11 refuses the ceiling being left above the measurement, so the only way it moves down
    is by wiring an engine to something that runs it.
    """
    return _ratcheted(probe, "engines_with_no_invoker")


def _ratcheted(probe: Probe, key: str) -> Findings:
    law_id, measure = RATCHETED[key]
    offenders = measure(probe)
    ceiling = probe.declaration.ratchet.get(key)
    findings: Findings = []
    if ceiling is None:
        return [
            f"{law_id} has no declared ceiling in `ratchet`, so its measurement is recorded and "
            "enforced by nothing"
        ]
    if len(offenders) > ceiling:
        new = len(offenders) - ceiling
        findings.append(
            f"{len(offenders)} artifacts violate {law_id} against a declared ceiling of "
            f"{ceiling}: {new} NEW violation(s). The class may not grow. Offenders: "
            + ", ".join(offenders[:8])
            + (f" … +{len(offenders) - 8} more" if len(offenders) > 8 else "")
        )
    return findings


def every_workflow_can_run(probe: Probe) -> Findings:
    """UEC-L-16 — a workflow a runner rejects is a plane that does not exist."""
    return _ratcheted(probe, "workflows_that_cannot_run")


def every_ci_gate_is_reachable_from_the_canonical_lane(probe: Probe) -> Findings:
    """UEC-L-15 — a gate only CI can run is one the standard command cannot see."""
    return _ratcheted(probe, "engines_outside_the_canonical_lane")


def every_engine_is_witnessed_refusing(probe: Probe) -> Findings:
    """UEC-L-14 — no verifier is trusted on the strength of being named."""
    return _ratcheted(probe, "engines_without_a_refusal_witness")


def every_engine_has_a_test(probe: Probe) -> Findings:
    """UEC-L-05 — a detector with no test is a detector no one has shown can fail."""
    return _ratcheted(probe, "engines_without_a_test")


def no_single_invocation_plane(probe: Probe) -> Findings:
    """UEC-L-06 — two independent invocation planes, so deleting one leaves a signal."""
    return _ratcheted(probe, "artifacts_with_one_invocation_plane")


def every_declaration_is_consumed(probe: Probe) -> Findings:
    """UEC-L-07 — a declaration nothing loads has no enforced field."""
    return _ratcheted(probe, "declarations_no_code_consumes")


def certification_identity_exists(probe: Probe) -> Findings:
    """UEC-L-08 — a declaration whose owner mints no digest cannot be certified at all."""
    return _ratcheted(probe, "declarations_without_a_certification_identity")


# --- UEC-L-13: the SUFFICIENT condition of certification identity ---------------------------
#
# UEC-L-08 asks whether a certification identity EXISTS. That is the necessary condition, and
# on its own it is the weaker half of a two-part property whose stronger half is where the
# defects live. A declaration can mint a perfectly stable digest that no semantic edit ever
# moves, and a stable digest over a projection is indistinguishable, from the outside, from a
# stable digest over the whole declaration. `engine/construct` passed UEC-L-08 for its whole
# life and carried exactly that defect: flipping `blocking` on UCON-L-01 — the flag its own
# contract reads to choose OPEN or CLOSED — left `declaration_digest` byte-identical at
# `192c63af…`. `engine/recursive_knowledge` carried it too, over 101 of 115 parsed fields.
#
# THAT DEFECT WAS FOUND BY A TEST THAT ONLY EVER LOOKED AT UEC ITSELF. `test_enforcement_
# closure.py` proves by mutation that every semantic edit moves UEC's OWN identity, and the
# first version of this module said, in a docstring, that it measured this "for UEC's own
# declaration and for no other programme". A detector scoped to its own author is the
# single-point-of-failure this programme exists to refuse: it can be deleted, or simply never
# extended, and every other declaration in the repository stays unmeasured while the report
# reads green. Rule 8 — can this detector disappear while certification remains green — was
# answerable YES.
#
# So the mutation experiment is lifted out of one test file and made a law over the whole
# governed population. It PERFORMS the mutation rather than inspecting a description of one:
# each declaration is loaded, edited in memory, re-parsed, and re-digested, and the law refuses
# unless the identity moved.
#
# SCOPE, STATED RATHER THAN IMPLIED. It reaches every governed declaration whose owning package
# exposes the uniform interface — a `declaration` module with `parse()` returning an object with
# `digest_payload()`. Three of nineteen do. The other sixteen mint digests through paths of
# their own shape, and this law reports that population rather than quietly excluding it: the
# ratchet `declarations_with_uniform_identity` is two-sided, so a fourth package implementing
# the interface fails until the ceiling is raised deliberately, and a package that DROPS the
# interface fails too. What this law does not do is claim the sixteen are proven; UEC-L-08 holds
# the necessary condition over them and the residual is recorded, not certified.
#
# A mutation the declaration REFUSES at parse counts as killed. A declaration that rejects an
# edit is a declaration that edit cannot silently pass through, which is the property under
# test; a fault would be a mutation that parsed cleanly and changed nothing.
#
# HERMETIC. Imports in-process, never writes, never subprocesses, reads no clock and no network.


#: The generic semantic mutations. Each targets a value that a programme's own contract reads
#: to reach a verdict, so a surviving mutant is a demonstrated certification bypass, not a
#: theoretical one.
#: The generic semantic mutations UEC-L-13 applies. Each is a pair: a GUARD that says whether
#: the document actually carries the field, and the EDIT itself. The guard is not decoration —
#: without it the law invents fields. `ucpa-declaration.json` declares no `blocking` on its
#: laws (every UCPA law is unconditionally blocking), and an edit that ADDED the key would be
#: dropped by a parser that never reads it, leaving the digest unchanged and the law reporting a
#: certification bypass that does not exist. A detector whose failures are its own artefacts
#: gets disabled, so a mutation that does not apply is SKIPPED and counted, never assumed.
#:
#: Each entry targets a value some programme's contract reads to reach a verdict — a law's
#: blocking flag, its statement, its bound check, the declared authority, the declared version —
#: so a surviving mutant is a demonstrated bypass rather than a theoretical one.
IDENTITY_MUTATIONS: Mapping[
    str, tuple[Callable[[dict[str, Any]], bool], Callable[[dict[str, Any]], None]]
] = {
    "flip the first law's blocking flag": (
        lambda d: isinstance(d.get("laws"), list)
        and bool(d["laws"])
        and "blocking" in d["laws"][0],
        lambda d: d["laws"][0].__setitem__("blocking", not d["laws"][0]["blocking"]),
    ),
    "rewrite the first law's statement": (
        lambda d: isinstance(d.get("laws"), list)
        and bool(d["laws"])
        and "statement" in d["laws"][0],
        lambda d: d["laws"][0].__setitem__(
            "statement", "this law now says something else entirely"
        ),
    ),
    "rewrite the first law's bound check": (
        lambda d: isinstance(d.get("laws"), list) and bool(d["laws"]) and "check" in d["laws"][0],
        lambda d: d["laws"][0].__setitem__("check", "a_check_that_does_not_exist"),
    ),
    "change the declared authority": (
        lambda d: isinstance(d.get("authority"), str),
        lambda d: d.__setitem__("authority", "SOME OTHER AUTHORITY"),
    ),
    "change the declared version": (
        lambda d: isinstance(d.get("version"), str),
        lambda d: d.__setitem__("version", "999.999"),
    ),
}

#: The fewest mutations that must APPLY to one declaration for the law to have measured it. A
#: declaration none of them reach is not a passing declaration; it is an unmeasured one, and
#: reporting the two as the same colour is the vacuity this programme exists to refuse.
IDENTITY_MUTATION_FLOOR = 2


def _uniform_identity_owners(probe: Probe) -> dict[str, tuple[str, Any]]:
    """Governed declarations whose owning package exposes the uniform identity interface.

    The owner is derived from who LOADS the declaration, never from its name — the same
    derivation UEC-L-08 uses, and for the same measured reason: a name-based guess reported
    UCON, which demonstrably has a digest, as having none.
    """
    found: dict[str, tuple[str, Any]] = {}
    for artifact in probe.declarations:
        for consumer in probe.consumers(artifact):
            package = os.path.dirname(consumer)
            module_name = package.replace("/", ".") + ".declaration"
            try:
                module = importlib.import_module(module_name)
            except Exception:  # noqa: BLE001, S112 - see below
                # A package with no `declaration` module simply does not expose the uniform
                # interface, which is a measured fact reported by the ratchet rather than an
                # error. Nothing is logged because this gate is declared hermetic and
                # deterministic: a log line is an output, and an output that varies with the
                # import environment would make two measurements of one state differ.
                continue
            if not hasattr(module, "parse"):
                continue
            found[artifact.identity] = (module_name, module)
            break
    return found


def certification_identity_is_complete(probe: Probe) -> Findings:
    """UEC-L-13 — every semantic mutation MOVES the identity, performed rather than described."""
    findings: Findings = []
    owners = _uniform_identity_owners(probe)

    ceiling = probe.declaration.ratchet.get("declarations_with_uniform_identity")
    if not isinstance(ceiling, int):
        return [
            "UEC-L-13 has no declared ceiling in `ratchet.declarations_with_uniform_identity`, "
            "so the population it measures is recorded and enforced by nothing"
        ]
    if len(owners) != ceiling:
        findings.append(
            f"{len(owners)} governed declaration(s) expose the uniform identity interface "
            f"against a declared ceiling of {ceiling}. The population may not move without a "
            "deliberate governance act in either direction. Measured: "
            + (", ".join(sorted(owners)) or "none")
        )

    for identity in sorted(owners):
        module_name, module = owners[identity]
        path = os.path.join(probe.root, identity)
        try:
            with open(path, encoding="utf-8") as handle:
                document = json.load(handle)
            baseline = content_hash(
                module.parse(copy.deepcopy(document), source=path).digest_payload()
            )
        except Exception as error:  # noqa: BLE001 - an unmeasurable identity is never a pass
            findings.append(
                f"{identity}: its identity could not be measured through {module_name} "
                f"({type(error).__name__}: {error}). An identity that cannot be measured is "
                "not an identity that holds."
            )
            continue

        applied = 0
        for name in sorted(IDENTITY_MUTATIONS):
            guard, mutate = IDENTITY_MUTATIONS[name]
            mutated = copy.deepcopy(document)
            if not guard(mutated):
                # The declaration does not carry this field. Inventing one would measure
                # nothing: a parser that never reads the key leaves the digest unchanged, and
                # the law would report a bypass that is its own artefact.
                continue
            applied += 1
            try:
                mutate(mutated)
                moved = content_hash(module.parse(mutated, source=path).digest_payload())
            except Exception:  # noqa: BLE001, S112 - see below
                # A declaration that REFUSES the edit at parse is a declaration that edit
                # cannot silently pass through, which is exactly the property under test — so
                # this is a killed mutant, not a swallowed error. The failure this law reports
                # is the opposite case: a mutation that parsed cleanly and changed nothing.
                continue
            if moved == baseline:
                findings.append(
                    f"{identity}: {name} — the declaration changed its meaning and its "
                    f"certification identity stayed at {baseline[:16]}…. A value that can alter "
                    "a verdict is outside the identity that certifies it, so the same digest "
                    "certifies two different declarations."
                )
        if applied < IDENTITY_MUTATION_FLOOR:
            findings.append(
                f"{identity}: only {applied} of {len(IDENTITY_MUTATIONS)} semantic mutations "
                f"applied, below the floor of {IDENTITY_MUTATION_FLOOR}. Its identity was not "
                "shown to move under ANY meaningful edit, so this law holds over it by "
                "describing nothing rather than by measuring it."
            )
    return findings


def self_coverage_is_a_fixed_point(probe: Probe) -> Findings:
    """UEC-L-09 — UEC is inside UEC. The closure mechanism is not exempt from closure.

    This is discovery ``D-09`` — "trust anchor → REG-AUTO-001, itself unregistered" — promoted
    from a dependency edge into an executable invariant. ``00-BOOK/tools/`` is excluded from the
    registration boundary on the stated ground that "the registry must not list itself", and the
    consequence was never governed. UEC lists itself, and refuses if it does not.
    """
    findings: Findings = []
    declared = probe.declaration.self_coverage
    required = declared.get("artifacts") or []
    if not required:
        findings.append(
            "self_coverage declares no artifacts, so this law would hold by describing nothing"
        )
        return findings
    governed = probe.declaration.governed_keys
    discovered = probe.discovered_keys
    for entry in required:
        identity = str(entry.get("identity") or "")
        kind = str(entry.get("kind") or "")
        key = f"{kind}::{identity}"
        if identity not in {p for p in probe.paths} and kind not in (
            "MAKE_GATE_TARGET",
            "VERIFY_STAGE",
        ):
            findings.append(f"UEC's own artifact is not tracked: {identity}")
            continue
        if key not in discovered:
            findings.append(
                f"UEC's own artifact is not located by UEC's own discovery rules: {kind} "
                f"{identity}. A closure mechanism outside its own closure is the D-09 defect"
            )
        if key not in governed:
            findings.append(
                f"UEC's own artifact is not in UEC's governed inventory: {kind} {identity}"
            )
    # The registrar must also satisfy the laws it applies to everything else.
    for artifact in probe.artifacts:
        if not artifact.identity.startswith(
            ("engine/enforcement_closure/", "00-MASTER/UEC-000001/")
        ):
            continue
        if artifact.kind in (KIND_ENGINE, KIND_MODULE_GATE):
            if not probe.test_bindings(artifact):
                findings.append(f"UEC's own gate has no test binding: {artifact.identity}")
            if len(probe.invokers(artifact)) < 2:
                findings.append(
                    f"UEC's own gate has fewer than two invocation planes: {artifact.identity} "
                    f"(invokers: {probe.invokers(artifact) or 'none'})"
                )
    return findings


def planes_are_disjoint(probe: Probe) -> Findings:
    """UEC-L-10 — the corpus plane and the enforcement plane do not overlap.

    REG-AUTO-001 registers ``.md``/``.txt``/``.docx``/``.json`` outside its excluded prefixes.
    UEC governs the executable enforcement surface. If an artifact were in both, two mechanisms
    would answer one question and could answer it differently; if in neither, no mechanism sees
    it. The declaration states the corpus boundary and this law measures the overlap rather than
    trusting the statement.
    """
    findings: Findings = []
    boundary = probe.declaration.corpus_plane
    extensions = tuple(boundary.get("include_extensions") or ())
    excluded = tuple(boundary.get("exclude_dir_prefixes") or ())
    if not extensions or not excluded:
        findings.append(
            "the corpus plane boundary is not declared, so disjointness cannot be measured"
        )
        return findings
    for artifact in probe.artifacts:
        identity = artifact.identity
        if "/" not in identity and not identity.endswith(extensions):
            continue  # a Makefile target or a stage label is not a path
        if not identity.endswith(extensions):
            continue
        if identity.startswith(excluded):
            continue
        findings.append(
            f"{identity} is an enforcement artifact AND inside the corpus registration "
            "boundary; two closure mechanisms would each claim it and could disagree"
        )
    return findings


def no_assurance_reduction(probe: Probe) -> Findings:
    """UEC-L-11 — a repaired violation must tighten the ceiling. NO SLACK.

    The other half of the ratchet. Without this, a ceiling declared once absorbs every future
    violation and the law becomes the thing it was written to prevent.
    """
    findings: Findings = []
    for key, (law_id, measure) in sorted(RATCHETED.items()):
        ceiling = probe.declaration.ratchet.get(key)
        if ceiling is None:
            continue
        measured = len(measure(probe))
        if measured < ceiling:
            findings.append(
                f"{law_id} now measures {measured} violations against a declared ceiling of "
                f"{ceiling}. The debt was repaired and the ceiling was not tightened, so the "
                f"declaration is carrying {ceiling - measured} units of slack a future "
                "violation could occupy silently. Lower the ceiling to "
                f"{measured} in `ratchet.{key}`"
            )
    declared_total = probe.declaration.ratchet.get("governed_artifacts")
    if declared_total is not None and len(probe.declaration.governed) != declared_total:
        findings.append(
            f"the governed inventory holds {len(probe.declaration.governed)} entries but "
            f"`ratchet.governed_artifacts` declares {declared_total}: the inventory changed "
            "without the count that guards it"
        )
    return findings


def withdrawals_are_reasoned_and_capped(probe: Probe) -> Findings:
    """UEC-L-12 — the escape hatch has an owner, a reason and a bound."""
    findings: Findings = []
    withdrawals = probe.declaration.withdrawals
    if len(withdrawals) > probe.declaration.withdrawal_cap:
        findings.append(
            f"{len(withdrawals)} withdrawals against a declared cap of "
            f"{probe.declaration.withdrawal_cap}: raising the cap is a governed edit, and "
            "exceeding it is not available"
        )
    discovered = probe.discovered_keys
    for item in withdrawals:
        key = f"{item.kind}::{item.identity}"
        if key in discovered:
            findings.append(
                f"{item.identity} is declared withdrawn but is still present and still located "
                "by discovery; a withdrawal releases governance, it does not hide an artifact"
            )
    return findings


LAW_CHECKS: Mapping[str, Callable[[Probe], Findings]] = {
    "discovery_rules_are_non_vacuous": discovery_rules_are_non_vacuous,
    "declared_enforcement_exists": declared_enforcement_exists,
    "discovered_enforcement_is_governed": discovered_enforcement_is_governed,
    "every_engine_has_an_invoker": every_engine_has_an_invoker,
    "every_engine_has_a_test": every_engine_has_a_test,
    "every_engine_is_witnessed_refusing": every_engine_is_witnessed_refusing,
    "every_ci_gate_is_reachable_from_the_canonical_lane": (
        every_ci_gate_is_reachable_from_the_canonical_lane
    ),
    "every_workflow_can_run": every_workflow_can_run,
    "no_single_invocation_plane": no_single_invocation_plane,
    "every_declaration_is_consumed": every_declaration_is_consumed,
    "certification_identity_exists": certification_identity_exists,
    "certification_identity_is_complete": certification_identity_is_complete,
    "self_coverage_is_a_fixed_point": self_coverage_is_a_fixed_point,
    "planes_are_disjoint": planes_are_disjoint,
    "no_assurance_reduction": no_assurance_reduction,
    "withdrawals_are_reasoned_and_capped": withdrawals_are_reasoned_and_capped,
}


def load_contract(
    path: str | None = None, *, repository: str | None = None
) -> tuple[Declaration, Probe]:
    root = repository or discovery.repo_root()
    declaration = load(path, repository=root)
    _require_two_way_law_binding(declaration)
    _require_every_law_blocks(declaration)
    return declaration, Probe(declaration, repository=root)


def _require_every_law_blocks(declaration: Declaration) -> None:
    """A law that can be switched off in data is not a law. Refused at LOAD, never as a law.

    WHY THIS IS NOT ITSELF A LAW, WHICH IS THE WHOLE POINT. It was written as one first, and a
    hostile audit walked straight through it: ``measure()`` closes the gate only on a law that is
    REFUSED *and* blocking, so setting ``blocking: false`` on UEC-L-01 — the law then carrying
    the check — made the check report the violation and made the report unable to close anything.
    The detector was disabled by the exact mutation it detects, and any law-level formulation has
    that hole whichever law hosts it, because the attacker picks the host.

    So it runs at load, before a single law is measured, and a non-blocking law is a FAULT
    (exit 2, "no verdict could be reached") rather than a verdict. That is the honest code: a
    declaration that has switched one of its own laws off is not one this programme can reach a
    verdict from.
    """
    switched_off = [law.law_id for law in declaration.laws if not law.blocking]
    if switched_off:
        raise EnforcementError(
            "these laws declare themselves non-blocking, so refusing them would not close the "
            f"gate: {switched_off}. Every law in this programme blocks; a non-blocking one is a "
            "law switched off in data, and a declaration carrying one cannot be certified"
        )


def _require_two_way_law_binding(declaration: Declaration) -> None:
    """Every declared law has a check, and every check is a declared law.

    One-way binding is how a law becomes decidable-but-unimplemented — the exact shape of
    ``BC-1``, where the register declares ``R-01…R-09`` and the predicates implement
    ``R-01…R-08``, so ``classify()`` returns ERROR for every subject.
    """
    declared = {law.check for law in declaration.laws}
    implemented = set(LAW_CHECKS)
    problems = [
        f"law {law.law_id} names check {law.check!r}, which is not implemented"
        for law in declaration.laws
        if law.check not in implemented
    ]
    problems += [
        f"check {name!r} is implemented but no law declares it"
        for name in sorted(implemented - declared)
    ]
    if problems:
        raise EnforcementError("the law set is not two-way bound:\n  " + "\n  ".join(problems))


def measure(
    path: str | None = None,
    *,
    repository: str | None = None,
    laws: Sequence[str] | None = None,
) -> dict[str, Any]:
    declaration, probe = load_contract(path, repository=repository)
    selected = set(laws) if laws else None
    rows: list[dict[str, Any]] = []
    for law in declaration.laws:
        if selected is not None and law.law_id not in selected:
            continue
        violations = [str(item) for item in LAW_CHECKS[law.check](probe)]
        rows.append(
            {
                "blocking": law.blocking,
                "check": law.check,
                "concern": law.concern,
                "law_id": law.law_id,
                "statement": law.statement,
                "verdict": HOLDS if not violations else REFUSED,
                "violations": violations,
            }
        )
    refused = [row for row in rows if row["verdict"] == REFUSED]
    blocking = [row for row in refused if row["blocking"]]
    measured = {key: len(fn(probe)) for key, (_law, fn) in sorted(RATCHETED.items())}
    return {
        "schema": "ucos-enforcement-closure-report",
        "version": "1.0.0",
        "authority": declaration.authority,
        "declaration": declaration.artifact_id,
        "declaration_digest": content_hash(declaration.digest_payload()),
        "declaration_version": declaration.version,
        "laws": rows,
        "counts": {
            **probe.counts(),
            "blocking_refusals": len(blocking),
            "holds": len(rows) - len(refused),
            "laws": len(rows),
            "refused": len(refused),
        },
        "ratchet_declared": dict(sorted(declaration.ratchet.items())),
        "ratchet_measured": measured,
        "by_kind": {
            kind: sum(1 for a in probe.artifacts if a.kind == kind)
            for kind in sorted({a.kind for a in probe.artifacts})
        },
        "status": "OPEN" if not blocking else "CLOSED",
    }


def inventory(path: str | None = None, *, repository: str | None = None) -> dict[str, Any]:
    """The discovered enforcement surface, as the governed inventory would record it.

    Emitted so adoption is reproducible rather than hand-typed. It is deliberately NOT written
    into the declaration by any command: if the observation could rewrite the expectation, then
    deleting a workflow and re-running the generator would produce a green gate, which is the
    bypass this whole programme exists to close. Adoption is a human paste into a governed file,
    and the diff is the record.
    """
    declaration, probe = load_contract(path, repository=repository)
    return {
        "governed_enforcement": [
            {
                "identity": artifact.identity,
                "kind": artifact.kind,
                "owner": declaration.rule(artifact.rule_id).owner,
                "rule_id": artifact.rule_id,
            }
            for artifact in sorted(probe.artifacts, key=lambda a: (a.kind, a.identity))
        ],
        "ratchet": {
            "governed_artifacts": len(probe.artifacts),
            **{key: len(fn(probe)) for key, (_law, fn) in sorted(RATCHETED.items())},
        },
    }

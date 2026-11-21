"""UCKP — the seventeen constitutional invariants, as executable probes.

:mod:`engine.uckp.law` declares what must be true. This module decides whether it *is*
true, for a real assembled universe, by measurement. Nothing here restates an
invariant: each probe is bound to an ``invariant_id`` and the name, statement and
blocking flag are read from :data:`engine.uckp.law.ROOT_LAW`. A probe that carried its
own copy of the statement could drift from the law it claims to measure, which is the
duplication Article 3 forbids.

Three rules govern this module, and they are the difference between a validator and a
rubber stamp.

**An unmeasured invariant is not a satisfied invariant.** If the law declares an
invariant and no probe is bound to its id, the result is ``unmeasured`` and — because
every invariant in the root law is blocking — the report is refused. Absence of a
measurement is never evidence of compliance. This repository has already recorded the
opposite defect once, as UCCEP-F-001 (a gate that could fail but never pass); the
symmetric defect is a gate that can pass because it never looked.

**A probe that raises has found a violation, not an accident.** Exceptions are captured
as findings and reported as ``violated``. A validator that crashes tells you nothing;
a validator that reports why it could not conclude tells you everything.

**Every probe reports its measurements, not just its verdict.** ``evidence`` on each
result carries the numbers the verdict was derived from, so a reader can disagree with
the conclusion and check the arithmetic.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from engine.uckp.canonical import canonical_json, content_hash
from engine.uckp.errors import UCKPValidationError
from engine.uckp.evolution import EVOLUTION_CYCLE, is_terminal, next_stage
from engine.uckp.execution import verify_execution_interchangeable
from engine.uckp.law import ROOT_LAW, Invariant
from engine.uckp.persistence import verify_interchangeable
from engine.uckp.projection import (
    ProjectionEngine,
    assert_no_projection_authority,
)
from engine.uckp.ucko import UCKO
from engine.uckp.universe import ConstitutionalUniverse, universe_execution_request
from engine.uckp.vocabulary import Term, Vocabulary, VocabularyRegistry

#: Verdicts a single invariant can receive. Closed set, so a verdict is machine-checkable.
SATISFIED = "satisfied"
VIOLATED = "violated"
UNMEASURED = "unmeasured"
INVARIANT_VERDICTS: tuple[str, ...] = (SATISFIED, UNMEASURED, VIOLATED)

#: Verdicts the whole report can receive.
CERTIFIED = "certified"
REFUSED = "refused"

#: The canonical primitive that Article 13 says exists exactly once, and the one module
#: permitted to define it. Any other definition is a competing authority (UCKP-INV-03).
CANONICAL_PRIMITIVE_NAMES: tuple[str, ...] = (
    "canonical_json",
    "canonical_bytes",
    "content_hash",
)
CANONICAL_PRIMITIVE_HOME = "engine/uckp/canonical.py"

#: Source trees searched for redefinitions of the canonical primitive.
SOURCE_PACKAGES: tuple[str, ...] = ("engine", "platform")

#: A term no vocabulary declares, used to prove that an unknown future member is
#: admissible by registration (Article 17). It is registered into a *copy*, never into
#: the universe's own vocabulary registry — a probe that mutated what it measures would
#: be manufacturing the result it reports.
FUTURE_PROBE_TERM = "uckp.probe.unknown-future-member"

Findings = tuple[str, ...]
Evidence = tuple[tuple[str, str], ...]
ProbeResult = tuple[Findings, Evidence]


def _evidence(**measurements: object) -> Evidence:
    return tuple(sorted((str(key), str(value)) for key, value in measurements.items()))


#: Modules a body must not reach for if it is merely forwarding to Layer Zero.
_PRIMITIVE_IMPLEMENTATION_MODULES = frozenset({"json", "hashlib"})


def _inlines_primitive(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True iff this function body implements the primitive rather than forwarding it.

    The test is whether the body calls into ``json`` or ``hashlib`` directly. A
    function that computes the digest itself is a second authority over every hash
    derived through it; a function that returns Layer Zero's answer is a name, and a
    name is free.
    """
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        target = child.func
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
            if target.value.id in _PRIMITIVE_IMPLEMENTATION_MODULES:
                return True
    return False


@dataclass(frozen=True, slots=True)
class InvariantResult:
    """The measured outcome for one constitutional invariant."""

    invariant_id: str
    name: str
    statement: str
    blocking: bool
    verdict: str
    findings: Findings = field(default_factory=tuple)
    evidence: Evidence = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.verdict not in INVARIANT_VERDICTS:
            raise UCKPValidationError(
                "invariant verdict is not machine-checkable",
                invariant_id=self.invariant_id,
                verdict=self.verdict,
            )

    @property
    def satisfied(self) -> bool:
        return self.verdict == SATISFIED

    @property
    def blocks(self) -> bool:
        """True iff this result must stop the report from certifying."""
        return self.blocking and not self.satisfied

    def to_dict(self) -> dict[str, object]:
        return {
            "invariant_id": self.invariant_id,
            "name": self.name,
            "statement": self.statement,
            "blocking": self.blocking,
            "verdict": self.verdict,
            "findings": list(self.findings),
            "evidence": {key: value for key, value in self.evidence},
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The judgement of the whole law against one universe."""

    law_id: str
    law_version: str
    law_digest: str
    universe_seal: str
    universe_fingerprint: str
    results: tuple[InvariantResult, ...]

    def result(self, invariant_id: str) -> InvariantResult:
        for item in self.results:
            if item.invariant_id == invariant_id:
                return item
        raise UCKPValidationError("no result for that invariant", invariant_id=invariant_id)

    def blocking_failures(self) -> tuple[InvariantResult, ...]:
        return tuple(item for item in self.results if item.blocks)

    def unmeasured(self) -> tuple[InvariantResult, ...]:
        return tuple(item for item in self.results if item.verdict == UNMEASURED)

    @property
    def verdict(self) -> str:
        return REFUSED if self.blocking_failures() else CERTIFIED

    @property
    def certified(self) -> bool:
        return self.verdict == CERTIFIED

    def satisfied_count(self) -> int:
        return sum(1 for item in self.results if item.satisfied)

    def stop_conditions(self) -> tuple[dict[str, object], ...]:
        """Each stop condition, decided from the invariants it names.

        A stop condition is not an independent measurement — it is a statement about
        which invariants must hold. Deriving it here keeps the thirteen conditions from
        becoming a fourteenth thing to maintain.
        """
        decided: list[dict[str, object]] = []
        for condition in ROOT_LAW.stop_conditions:
            unmet = [
                invariant_id
                for invariant_id in condition.invariants
                if not self.result(invariant_id).satisfied
            ]
            decided.append(
                {
                    "condition_id": condition.condition_id,
                    "statement": condition.statement,
                    "invariants": list(condition.invariants),
                    "met": not unmet,
                    "unmet_invariants": unmet,
                }
            )
        return tuple(decided)

    def all_stop_conditions_met(self) -> bool:
        return all(bool(item["met"]) for item in self.stop_conditions())

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "ucos-uckp-validation",
            "version": "1.0.0",
            "law_id": self.law_id,
            "law_version": self.law_version,
            "law_digest": self.law_digest,
            "universe_seal": self.universe_seal,
            "universe_fingerprint": self.universe_fingerprint,
            "verdict": self.verdict,
            "counts": {
                "invariants": len(self.results),
                "satisfied": self.satisfied_count(),
                "violated": sum(1 for item in self.results if item.verdict == VIOLATED),
                "unmeasured": len(self.unmeasured()),
                "blocking_failures": len(self.blocking_failures()),
            },
            "invariants": [item.to_dict() for item in self.results],
            "stop_conditions": list(self.stop_conditions()),
            "all_stop_conditions_met": self.all_stop_conditions_met(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())

    def summary(self) -> str:
        """One line per invariant, for a terminal."""
        lines = [
            f"{self.law_id} v{self.law_version} against universe {self.universe_seal[:16]}",
            f"verdict: {self.verdict.upper()} "
            f"({self.satisfied_count()}/{len(self.results)} invariants satisfied)",
            "",
        ]
        for item in self.results:
            mark = {SATISFIED: "PASS", VIOLATED: "FAIL", UNMEASURED: "UNMEASURED"}[item.verdict]
            lines.append(f"  {mark:10s} {item.invariant_id}  {item.name}")
            for finding in item.findings[:4]:
                lines.append(f"             - {finding}")
            if len(item.findings) > 4:
                lines.append(f"             - ... {len(item.findings) - 4} more")
        met = sum(1 for item in self.stop_conditions() if item["met"])
        lines.extend(("", f"stop conditions met: {met}/{len(self.stop_conditions())}"))
        return "\n".join(lines)


class ConstitutionalValidator:
    """Measures one assembled universe against all seventeen invariants."""

    __slots__ = ("_universe", "_source_root")

    def __init__(
        self, universe: ConstitutionalUniverse, *, source_root: str | Path | None = None
    ) -> None:
        self._universe = universe
        self._source_root = (
            Path(source_root) if source_root is not None else Path(__file__).resolve().parents[2]
        )

    # --- probe binding ----------------------------------------------------------

    def probes(self) -> Mapping[str, Callable[[], ProbeResult]]:
        """One probe per invariant id. The keys are what makes coverage checkable."""
        return {
            "UCKP-INV-01": self._probe_knowledge_once,
            "UCKP-INV-02": self._probe_single_authority,
            "UCKP-INV-03": self._probe_zero_duplication,
            "UCKP-INV-04": self._probe_zero_ambiguity,
            "UCKP-INV-05": self._probe_zero_orphans,
            "UCKP-INV-06": self._probe_zero_circular_authority,
            "UCKP-INV-07": self._probe_zero_hardcoded_knowledge,
            "UCKP-INV-08": self._probe_zero_projection_authority,
            "UCKP-INV-09": self._probe_zero_technology_lock_in,
            "UCKP-INV-10": self._probe_zero_repository_lock_in,
            "UCKP-INV-11": self._probe_zero_storage_lock_in,
            "UCKP-INV-12": self._probe_zero_runtime_lock_in,
            "UCKP-INV-13": self._probe_infinite_evolvability,
            "UCKP-INV-14": self._probe_infinite_extensibility,
            "UCKP-INV-15": self._probe_infinite_replayability,
            "UCKP-INV-16": self._probe_infinite_discoverability,
            "UCKP-INV-17": self._probe_infinite_auditability,
        }

    def unprobed(self) -> tuple[str, ...]:
        """Declared invariants with no probe. Must be empty for a report to certify."""
        return tuple(sorted(set(ROOT_LAW.invariant_ids()) - set(self.probes())))

    def orphan_probes(self) -> tuple[str, ...]:
        """Probes bound to an id the law does not declare — a measurement of nothing."""
        return tuple(sorted(set(self.probes()) - set(ROOT_LAW.invariant_ids())))

    # --- judgement --------------------------------------------------------------

    def validate_invariant(self, invariant: Invariant | str) -> InvariantResult:
        """Measure one invariant. Never raises: a failure to measure is a verdict."""
        declared = (
            invariant if isinstance(invariant, Invariant) else ROOT_LAW.invariant(str(invariant))
        )
        probe = self.probes().get(declared.invariant_id)
        if probe is None:
            return InvariantResult(
                invariant_id=declared.invariant_id,
                name=declared.name,
                statement=declared.statement,
                blocking=declared.blocking,
                verdict=UNMEASURED,
                findings=("no probe is bound to this invariant, so no verdict may be asserted",),
            )
        try:
            findings, evidence = probe()
        except Exception as exc:  # noqa: BLE001 - a probe that cannot conclude is a failure
            return InvariantResult(
                invariant_id=declared.invariant_id,
                name=declared.name,
                statement=declared.statement,
                blocking=declared.blocking,
                verdict=VIOLATED,
                findings=(f"probe could not conclude: {type(exc).__name__}: {exc}",),
            )
        return InvariantResult(
            invariant_id=declared.invariant_id,
            name=declared.name,
            statement=declared.statement,
            blocking=declared.blocking,
            verdict=SATISFIED if not findings else VIOLATED,
            findings=tuple(findings),
            evidence=evidence,
        )

    def validate(self) -> ValidationReport:
        """Measure every declared invariant, in the order the law declares them."""
        return ValidationReport(
            law_id=ROOT_LAW.law_id,
            law_version=ROOT_LAW.version,
            law_digest=ROOT_LAW.digest(),
            universe_seal=self._universe.seal(),
            universe_fingerprint=self._universe.fingerprint(),
            results=tuple(self.validate_invariant(invariant) for invariant in ROOT_LAW.invariants),
        )

    # --- probes: existence and identity -----------------------------------------

    def _probe_knowledge_once(self) -> ProbeResult:
        """INV-01 — no two canonical objects carry the same semantic identity."""
        registry = self._universe.registry
        findings = [
            f"meaning homed {len(group)} times: {', '.join(group)}"
            for group in registry.duplicate_semantics()
        ]
        objects = self._universe.objects()
        digests = {obj.semantic_digest() for obj in objects}
        return tuple(findings), _evidence(
            objects=len(objects),
            distinct_meanings=len(digests),
            duplicate_groups=len(registry.duplicate_semantics()),
        )

    def _probe_single_authority(self) -> ProbeResult:
        """INV-02 — exactly one parent per object, grounding in the root law."""
        universe = self._universe
        graph = universe.graph()
        root_id = universe.root_id()
        findings: list[str] = []
        for obj in universe.objects():
            parent = obj.authority.derives_from
            if not parent:
                findings.append(f"{obj.ucko_id} names no parent authority")
                continue
            if parent != obj.ucko_id and graph.node(parent) is None:
                findings.append(f"{obj.ucko_id} derives from {parent}, which does not exist")
                continue
            chain = graph.authority_chain(obj.ucko_id)
            if not chain or chain[-1] != root_id:
                findings.append(
                    f"{obj.ucko_id} does not ground in the root law "
                    f"(chain terminates at {chain[-1] if chain else 'nothing'})"
                )
        roots = universe.registry.root_ids()
        if len(roots) != 1:
            findings.append(f"the universe declares {len(roots)} self-grounding roots")
        return tuple(findings), _evidence(
            objects=len(universe.objects()), roots=len(roots), root_id=root_id
        )

    def _probe_zero_duplication(self) -> ProbeResult:
        """INV-03 — no identity, content digest or canonical primitive defined twice.

        The third clause is the one that reaches outside the universe. A digest
        primitive redefined in a second module is a second authority over every hash in
        the system, and it is invisible to any check that only looks at objects — so
        this probe reads the source tree. If the source tree cannot be read the probe
        reports that as a finding rather than concluding compliance.
        """
        findings: list[str] = []
        objects = self._universe.objects()

        by_uuid: dict[str, list[str]] = {}
        by_content: dict[str, list[str]] = {}
        for obj in objects:
            by_uuid.setdefault(obj.identity.uuid, []).append(obj.ucko_id)
            by_content.setdefault(obj.content_sha256, []).append(obj.ucko_id)
        for uuid_value, owners in sorted(by_uuid.items()):
            if len(owners) > 1:
                findings.append(f"uuid {uuid_value} claimed by {len(owners)}: {', '.join(owners)}")
        for digest, owners in sorted(by_content.items()):
            if len(owners) > 1:
                findings.append(
                    f"content digest {digest[:16]} shared by {len(owners)}: {', '.join(owners)}"
                )

        redefinitions, scanned = self._canonical_primitive_redefinitions()
        if scanned == 0:
            findings.append(
                "no source file could be read, so the single-primitive clause is unmeasured"
            )
        findings.extend(
            f"{name} redefined in {location} (canonical home is {CANONICAL_PRIMITIVE_HOME})"
            for location, name in redefinitions
        )
        return tuple(findings), _evidence(
            objects=len(objects),
            distinct_uuids=len(by_uuid),
            distinct_content_digests=len(by_content),
            source_files_scanned=scanned,
            primitive_redefinitions=len(redefinitions),
        )

    def _canonical_primitive_redefinitions(self) -> tuple[tuple[tuple[str, str], ...], int]:
        """Locate every *reimplementation* of the canonical primitive outside its home.

        Three distinctions matter, because getting them wrong makes the probe either
        blind or hysterical:

        * Only **module-level** functions count. A method named ``content_hash`` that
          delegates to the primitive is a caller, not a rival definition.
        * Only functions that **inline the implementation** count — a body reaching
          for ``json.dumps`` or ``hashlib`` directly. A function that forwards to
          Layer Zero is a re-export, which is precisely the remedy, so flagging it
          would make the invariant unsatisfiable.
        * Only the **exact Layer Zero names** count. ``platform.foundation.canonical``
          defines a profile-aware ``content_digest`` returning a structured digest;
          that is a richer primitive, not a second copy of this one.
        """
        home = (self._source_root / CANONICAL_PRIMITIVE_HOME).resolve()
        found: list[tuple[str, str]] = []
        scanned = 0
        for package in SOURCE_PACKAGES:
            root = self._source_root / package
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*.py")):
                resolved = path.resolve()
                if resolved == home:
                    continue
                try:
                    tree = ast.parse(resolved.read_text(encoding="utf-8"))
                except (OSError, SyntaxError):
                    continue
                scanned += 1
                relative = resolved.relative_to(self._source_root).as_posix()
                for node in tree.body:
                    if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        continue
                    if node.name not in CANONICAL_PRIMITIVE_NAMES:
                        continue
                    if _inlines_primitive(node):
                        found.append((f"{relative}:{node.lineno}", node.name))
        return tuple(found), scanned

    def _probe_zero_ambiguity(self) -> ProbeResult:
        """INV-04 — every facet answered, every relationship target real."""
        universe = self._universe
        findings: list[str] = []
        incomplete = 0
        for obj in universe.objects():
            missing = obj.missing_facets()
            if missing:
                incomplete += 1
                findings.append(
                    f"{obj.ucko_id} leaves {len(missing)} facet(s) absent: "
                    f"{', '.join(facet.value for facet in missing)}"
                )
        dangling = universe.graph().dangling()
        findings.extend(
            f"{edge.source} -{edge.relation}-> {edge.target} resolves to nothing"
            for edge in dangling
        )
        return tuple(findings), _evidence(
            objects=len(universe.objects()),
            incomplete_objects=incomplete,
            edges=len(universe.graph().edges()),
            dangling_edges=len(dangling),
        )

    def _probe_zero_orphans(self) -> ProbeResult:
        """INV-05 — every object reachable from the root law."""
        universe = self._universe
        graph = universe.graph()
        root_id = universe.root_id()
        orphans = graph.orphans(root_id)
        reachable = graph.reachable_from(root_id)
        findings = [f"{orphan} is unreachable from the root law" for orphan in orphans]
        return tuple(findings), _evidence(
            objects=len(universe.objects()),
            reachable=len(reachable),
            orphans=len(orphans),
            root_id=root_id,
        )

    def _probe_zero_circular_authority(self) -> ProbeResult:
        """INV-06 — the authority relation is acyclic."""
        graph = self._universe.graph()
        cycles = graph.cycles("authority")
        findings = [f"authority cycle: {' -> '.join(cycle)}" for cycle in cycles]
        try:
            graph.require_acyclic_authority()
        except Exception as exc:  # noqa: BLE001 - reported, never swallowed
            findings.append(f"authority acyclicity refused: {exc}")
        return tuple(findings), _evidence(
            authority_edges=len(graph.edges_of_class("authority")), cycles=len(cycles)
        )

    def _probe_zero_hardcoded_knowledge(self) -> ProbeResult:
        """INV-07 — every object names the declaration it was derived from."""
        findings: list[str] = []
        sourced = 0
        for obj in self._universe.objects():
            if not obj.provenance:
                findings.append(f"{obj.ucko_id} carries no provenance")
                continue
            unsourced = [step for step in obj.provenance if not step.source.strip()]
            if unsourced:
                findings.append(
                    f"{obj.ucko_id} has {len(unsourced)} provenance step(s) naming no source"
                )
                continue
            sourced += 1
        return tuple(findings), _evidence(
            objects=len(self._universe.objects()), objects_with_sourced_provenance=sourced
        )

    # --- probes: non-authority of representations -------------------------------

    def _probe_zero_projection_authority(self) -> ProbeResult:
        """INV-08 — no projection, binding or generated artifact claims authority."""
        universe = self._universe
        objects = universe.objects()
        engine: ProjectionEngine = universe.projections
        findings: list[str] = []

        missing_kinds = engine.unimplemented(
            {binding.projection_kind for obj in objects for binding in obj.projection_bindings}
        )
        findings.extend(
            f"objects bind to projection kind {kind!r}, which no projection implements"
            for kind in missing_kinds
        )
        artifacts = engine.project_all(objects)
        findings.extend(
            f"projected artifact {projection_id} claims authority"
            for projection_id in assert_no_projection_authority(artifacts)
        )
        for obj in objects:
            findings.extend(
                f"{obj.ucko_id} declares projection {binding.projection_kind!r} as authoritative"
                for binding in obj.projection_bindings
                if binding.authoritative
            )
            findings.extend(
                f"{obj.ucko_id} declares persistence {binding.persistence_kind!r} as authoritative"
                for binding in obj.persistence_bindings
                if binding.authoritative
            )
        return tuple(findings), _evidence(
            artifacts=len(artifacts),
            projection_kinds=len(engine.kinds()),
            authority_claims=len(assert_no_projection_authority(artifacts)),
        )

    def _probe_zero_repository_lock_in(self) -> ProbeResult:
        """INV-10 — the repository appears only as a binding, never as authority."""
        universe = self._universe
        law = universe.law
        findings: list[str] = []
        for obj in universe.objects():
            if law.is_non_authoritative(obj.taxonomy.category):
                findings.append(
                    f"{obj.ucko_id} is categorised {obj.taxonomy.category!r}, which Article 4 "
                    "says may only ever be a view"
                )
        repository_bindings = tuple(
            binding
            for obj in universe.objects()
            for binding in obj.persistence_bindings
            if binding.persistence_kind in {"git", "filesystem"}
        )
        repository_projections = tuple(
            binding
            for obj in universe.objects()
            for binding in obj.projection_bindings
            if binding.projection_kind == "repository"
        )
        findings.extend(
            f"repository persistence binding {binding.locator!r} claims authority"
            for binding in repository_bindings
            if binding.authoritative
        )
        if not repository_bindings and not repository_projections:
            findings.append(
                "no object binds the repository at all, so the claim that the repository is "
                "merely a binding is untested"
            )
        for name in ("repository", "file", "folder", "source-code", "document"):
            if not law.is_non_authoritative(name):
                findings.append(f"{name!r} is not declared non-authoritative by the law")
        return tuple(findings), _evidence(
            repository_persistence_bindings=len(repository_bindings),
            repository_projection_bindings=len(repository_projections),
            non_authoritative_categories=len(law.non_authoritative_categories),
        )

    # --- probes: interchangeability ---------------------------------------------

    def _probe_zero_technology_lock_in(self) -> ProbeResult:
        """INV-09 — two or more execution technologies satisfy the identical contract."""
        universe = self._universe
        adapters = universe.execution
        findings: list[str] = []
        if len(adapters) < 2:
            findings.append(
                f"only {len(adapters)} execution adapter(s) exist, so interchangeability "
                "cannot be demonstrated"
            )
        reports = []
        for operation in ("universe-seal", "graph-fingerprint"):
            report = verify_execution_interchangeable(
                adapters, universe_execution_request(operation), universe.registry
            )
            reports.append(report)
            findings.extend(f"{operation}: {failure}" for failure in report.failures)
            findings.extend(
                f"{operation}: execution adapter {kind!r} claims to own knowledge"
                for kind in report.knowledge_owners
            )
        return tuple(findings), _evidence(
            execution_adapters=len(adapters),
            operations_probed=len(reports),
            kinds=",".join(sorted({kind for report in reports for kind in report.kinds()})),
        )

    def _probe_zero_storage_lock_in(self) -> ProbeResult:
        """INV-11 — two or more persistence technologies round-trip identically."""
        universe = self._universe
        adapters = universe.persistence
        objects = universe.objects()
        findings: list[str] = []
        if len(adapters) < 2:
            findings.append(
                f"only {len(adapters)} persistence adapter(s) exist, so interchangeability "
                "cannot be demonstrated"
            )
        report = verify_interchangeable(adapters, objects)
        findings.extend(report.failures)
        return tuple(findings), _evidence(
            persistence_adapters=len(adapters),
            objects=len(objects),
            expected_digest=report.expected_digest[:16],
            kinds=",".join(report.kinds()),
        )

    def _probe_zero_runtime_lock_in(self) -> ProbeResult:
        """INV-12 — two or more runtimes, and no object bound to exactly one."""
        objects = self._universe.objects()
        findings: list[str] = []
        kinds: set[str] = set()
        single = 0
        unbound = 0
        for obj in objects:
            bound = {binding.execution_kind for binding in obj.runtime_bindings}
            kinds |= bound
            if len(bound) == 1:
                single += 1
                findings.append(
                    f"{obj.ucko_id} binds exactly one runtime ({next(iter(bound))}), which is "
                    "lock-in at the object level"
                )
            elif not bound:
                unbound += 1
                findings.append(f"{obj.ucko_id} binds no runtime at all, so it cannot be acted on")
        if len(kinds) < 2:
            findings.append(
                f"the universe reaches only {len(kinds)} runtime technolog(y/ies) in total"
            )
        return tuple(findings), _evidence(
            objects=len(objects),
            distinct_runtimes=len(kinds),
            objects_bound_to_one=single,
            objects_bound_to_none=unbound,
        )

    # --- probes: infinity properties --------------------------------------------

    def _probe_infinite_evolvability(self) -> ProbeResult:
        """INV-13 — the evolution cycle is append-only and has no terminal stage."""
        ledger = self._universe.evolution
        findings: list[str] = []
        for stage in EVOLUTION_CYCLE:
            if is_terminal(stage):
                findings.append(f"stage {stage.value!r} is terminal, so evolution can stop")
            successor = next_stage(stage)
            if successor not in EVOLUTION_CYCLE:
                findings.append(f"stage {stage.value!r} has no successor inside the cycle")
        if ledger.is_terminated():
            findings.append("the evolution ledger reports itself terminated")
        records = ledger.records()
        if not records:
            findings.append("the evolution ledger is empty, so append-only is untested")
        if ledger.cycles() < 2:
            findings.append(
                "the ledger has not yet wrapped past the final stage, so non-termination "
                "is asserted rather than shown"
            )
        if not hasattr(ledger, "append"):  # pragma: no cover - structural guard
            findings.append("the ledger exposes no append operation")
        for forbidden in ("remove", "delete", "truncate", "rewrite", "update"):
            if hasattr(ledger, forbidden):
                findings.append(f"the ledger exposes {forbidden!r}, which is not append-only")
        return tuple(findings), _evidence(
            cycle_length=len(EVOLUTION_CYCLE),
            records=len(records),
            cycles=ledger.cycles(),
            completed_cycles=ledger.completed_cycles(),
            terminated=ledger.is_terminated(),
        )

    def _probe_infinite_extensibility(self) -> ProbeResult:
        """INV-14 — every vocabulary, adapter set and relationship class admits a stranger.

        Proven by actually admitting one. A copy of each vocabulary is extended with a
        term no vocabulary declares; if the extension is refused, the vocabulary is
        closed no matter what it says about itself.
        """
        universe = self._universe
        vocabularies: VocabularyRegistry = universe.vocabularies()
        findings: list[str] = []
        if not vocabularies.is_extensible():
            findings.append("the vocabulary registry reports itself closed")
        extended = 0
        for vocabulary_id in vocabularies.vocabulary_ids():
            declared: Vocabulary = vocabularies.require(vocabulary_id)
            probe_term = Term(
                term_id=FUTURE_PROBE_TERM,
                definition="an unknown future member, admitted by registration",
            )
            try:
                widened = declared.extended_with(probe_term)
            except Exception as exc:  # noqa: BLE001 - a refusal is the finding
                findings.append(f"{vocabulary_id} refused an unknown future term: {exc}")
                continue
            if not widened.has(FUTURE_PROBE_TERM):
                findings.append(
                    f"{vocabulary_id} accepted the extension but did not admit the term"
                )
                continue
            if declared.has(FUTURE_PROBE_TERM):
                findings.append(
                    f"{vocabulary_id} was mutated by the probe, so extension is not a pure "
                    "derivation of a new vocabulary"
                )
                continue
            extended += 1

        engine = universe.projections
        try:
            engine.unimplemented(("uckp.probe.future-projection",))
        except Exception as exc:  # noqa: BLE001
            findings.append(f"the projection engine cannot reason about unknown kinds: {exc}")
        adapter_kinds = (
            ("persistence", {a.describe().get("kind", "") for a in universe.persistence}),
            ("execution", {a.describe().get("kind", "") for a in universe.execution}),
        )
        for label, kinds in adapter_kinds:
            future = {kind for kind in kinds if str(kind).startswith("future")}
            if not future:
                findings.append(
                    f"the {label} adapter set names no future member, so it is closed to "
                    "technologies that do not exist yet"
                )
        return tuple(findings), _evidence(
            vocabularies=len(vocabularies.vocabulary_ids()),
            vocabularies_extended=extended,
            registry_extensible=vocabularies.is_extensible(),
        )

    def _probe_infinite_replayability(self) -> ProbeResult:
        """INV-15 — every state carries a proof and everything replays identically."""
        universe = self._universe
        findings: list[str] = []
        timeline = universe.timeline

        if not timeline.states():
            findings.append("the timeline is empty, so replayability is untested")
        if not timeline.proofs_complete():
            findings.append("at least one constitutional state carries an incomplete proof set")
        if not timeline.replays_identically():
            findings.append("replaying the timeline does not reproduce it")
        if not timeline.verify():
            findings.append("the timeline refuses its own verification")
        for state in timeline.states():
            if not state.verify_integrity():
                findings.append(f"state {state.state_id[:16]} was altered after sealing")
            if not state.proofs_hold():
                findings.append(f"state {state.state_id[:16]} carries a proof that does not hold")

        unreplayable = [obj.ucko_id for obj in universe.objects() if not obj.verify_replay()]
        findings.extend(f"{ucko_id} carries no holding replay proof" for ucko_id in unreplayable)
        unsealed = [obj.ucko_id for obj in universe.objects() if not obj.verify_integrity()]
        findings.extend(f"{ucko_id} was mutated after sealing" for ucko_id in unsealed)

        if not universe.governance.replays_identically():
            findings.append("at least one governance decision does not re-derive itself")
        if not universe.projections.replays_identically(universe.objects()):
            findings.append("at least one projection does not regenerate byte-identically")
        if universe.fingerprint() != universe.fingerprint():  # pragma: no cover
            findings.append("the universe fingerprint is not stable within one process")
        return tuple(findings), _evidence(
            states=len(timeline.states()),
            objects=len(universe.objects()),
            objects_without_replay_proof=len(unreplayable),
            objects_unsealed=len(unsealed),
            governance_decisions=len(universe.governance.decisions()),
        )

    def _probe_infinite_discoverability(self) -> ProbeResult:
        """INV-16 — everything self-describes and is found without enumeration."""
        universe = self._universe
        report = universe.discovery
        findings: list[str] = []
        if not report.providers_found:
            findings.append("discovery found no provider, so the universe was enumerated by hand")
        findings.extend(f"discovery failure: {failure}" for failure in report.failures)
        if report.objects_admitted == 0:
            findings.append("discovery admitted no object")

        undiscoverable = 0
        for obj in universe.objects():
            descriptor = obj.discovery
            if not descriptor.discoverable:
                undiscoverable += 1
                findings.append(f"{obj.ucko_id} declares itself undiscoverable")
                continue
            if not descriptor.self_describing:
                undiscoverable += 1
                findings.append(f"{obj.ucko_id} does not self-describe")
                continue
            if not descriptor.provider.strip():
                undiscoverable += 1
                findings.append(f"{obj.ucko_id} names no provider, so nothing can offer it")
                continue
            described = obj.describe()
            if not described.get("ucko_id"):
                undiscoverable += 1
                findings.append(f"{obj.ucko_id} produces a self-description with no identity")
        return tuple(findings), _evidence(
            modules_scanned=report.modules_scanned,
            providers=len(report.providers_found),
            admitted=report.objects_admitted,
            objects=len(universe.objects()),
            undiscoverable=undiscoverable,
            failures=len(report.failures),
        )

    def _probe_infinite_auditability(self) -> ProbeResult:
        """INV-17 — every object and every transition carries a complete audit trail."""
        universe = self._universe
        findings: list[str] = []
        unaudited = 0
        for obj in universe.objects():
            if not obj.audit:
                unaudited += 1
                findings.append(f"{obj.ucko_id} carries no audit entry")
                continue
            incomplete = [
                entry
                for entry in obj.audit
                if not (entry.actor.strip() and entry.action.strip() and entry.subject.strip())
            ]
            if incomplete:
                unaudited += 1
                findings.append(
                    f"{obj.ucko_id} carries {len(incomplete)} audit entr(y/ies) missing "
                    "an actor, action or subject"
                )
        timeline = universe.timeline
        if not timeline.audit_complete():
            findings.append("at least one constitutional state carries no audit trail")
        for state in timeline.states():
            if not state.audit_trail:
                findings.append(f"state {state.state_id[:16]} records no audit entry")
        if not universe.governance.audit():
            findings.append("the governance runtime has recorded no audit entry")
        if not universe.evolution.records():
            findings.append("the evolution ledger records nothing, so no history is auditable")
        return tuple(findings), _evidence(
            objects=len(universe.objects()),
            unaudited_objects=unaudited,
            states=len(timeline.states()),
            governance_audit_entries=len(universe.governance.audit()),
            evolution_records=len(universe.evolution.records()),
        )


def validate_universe(
    universe: ConstitutionalUniverse, *, source_root: str | Path | None = None
) -> ValidationReport:
    """Measure ``universe`` against all seventeen invariants."""
    return ConstitutionalValidator(universe, source_root=source_root).validate()


def require_certified(report: ValidationReport) -> None:
    """Fail closed unless the report certifies."""
    if not report.certified:
        raise UCKPValidationError(
            "the universe does not satisfy the root constitutional law",
            verdict=report.verdict,
            failures=[item.invariant_id for item in report.blocking_failures()],
        )


def report_json(report: ValidationReport) -> str:
    """The canonical JSON encoding of a validation report."""
    return canonical_json(report.to_dict())


def _unused(objects: Iterable[UCKO], sequence: Sequence[object]) -> None:  # pragma: no cover
    """Kept out of the public surface; exists only to pin the imported types."""
    del objects, sequence


__all__ = [
    "CANONICAL_PRIMITIVE_HOME",
    "CANONICAL_PRIMITIVE_NAMES",
    "CERTIFIED",
    "INVARIANT_VERDICTS",
    "REFUSED",
    "SATISFIED",
    "UNMEASURED",
    "VIOLATED",
    "ConstitutionalValidator",
    "InvariantResult",
    "ValidationReport",
    "report_json",
    "require_certified",
    "validate_universe",
]

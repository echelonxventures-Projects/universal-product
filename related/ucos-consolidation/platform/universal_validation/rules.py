"""UCOS-EPIC-005 — Universal Validation rules (Terminal T5).

A validation **rule** is an immutable, deterministic predicate over a
:class:`~platform.universal_validation.contracts.ValidationTarget`. Each rule has a
stable id, a domain, a severity, and an ``evaluate`` method returning a
:class:`~platform.universal_validation.contracts.RuleResult`. Rules are pure functions
of the target facts — no secrets, no registry access, no wall-clock — so identical
targets yield identical results.

**Fail-closed** is the mission mandate: a rule that cannot *prove* its invariant holds
— because the evidence it needs is absent or malformed — returns FAIL, never PASS and
never a swallowed exception. Absence of evidence is never evidence of correctness.

The built-in suite covers the seven universal domains:

    * **Architecture** — declared layers, an acyclic dependency graph, layering
      respected (no upward edges), and no writes to the read-only certified corpus.
    * **Implementation** — declared modules present, entrypoints resolved, and (advisory)
      no open work markers.
    * **Dependency** — every dependency pinned, resolved to a known provider, and the
      graph acyclic.
    * **Registry** — entries well-formed, ids unique, and references intact.
    * **Schema** — every schema versioned and every record conformant to its schema.
    * **Runtime** — EC-1 provisional-state disclosure present, deterministic runtime
      identities, and digest-pinned images.
    * **Quality** — coverage threshold met, tests passing, and (advisory) lint clean.

The architecture is open: callers may supply their own rules to the engine.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from platform.universal_validation.contracts import (
    RuleResult,
    RuleSeverity,
    RuleStatus,
    ValidationDomain,
    ValidationTarget,
)
from typing import Any, ClassVar

from engine.foundation.guards.frozen_paths import FROZEN_PREFIXES, find_frozen_writes
from engine.runtime.disclosure import disclosure_present

_RUNTIME_ID = re.compile(r"^UCOS-RUN-.+-[0-9a-f]{16}$")


# ---------------------------------------------------------------------------
# rule architecture
# ---------------------------------------------------------------------------
class ValidationRule(ABC):
    """The common contract for a single validation rule (the architecture unit)."""

    rule_id: ClassVar[str]
    domain: ClassVar[ValidationDomain]
    severity: ClassVar[RuleSeverity]
    description: ClassVar[str] = ""

    @abstractmethod
    def evaluate(self, target: ValidationTarget) -> RuleResult:
        """Return a finding for ``target`` (never raises for a well-formed target)."""
        raise NotImplementedError  # pragma: no cover

    # -- helpers ---------------------------------------------------------------

    def facts(self, target: ValidationTarget) -> Mapping[str, Any]:
        return target.domain_facts(self.domain)

    def _passed(self, message: str = "", **details: Any) -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            domain=self.domain,
            severity=self.severity,
            status=RuleStatus.PASS,
            message=message or f"{self.rule_id} satisfied",
            details=details,
        )

    def _failed(self, message: str, **details: Any) -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            domain=self.domain,
            severity=self.severity,
            status=RuleStatus.FAIL,
            message=message,
            details=details,
        )


def _as_sequence(value: Any) -> list[Any] | None:
    """Return ``value`` as a list if it is a non-string sequence, else ``None``."""
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return list(value)
    return None


def _detect_cycle(edges: list[tuple[str, str]]) -> list[str] | None:
    """Return a cycle (as an ordered node list) in a directed graph, or ``None``.

    Deterministic: adjacency and traversal follow sorted node/edge order so an
    identical edge set always yields the identical cycle report.
    """
    adjacency: dict[str, list[str]] = {}
    for src, dst in edges:
        adjacency.setdefault(src, []).append(dst)
        adjacency.setdefault(dst, [])
    for node in adjacency:
        adjacency[node] = sorted(adjacency[node])

    WHITE, GREY, BLACK = 0, 1, 2
    color: dict[str, int] = dict.fromkeys(adjacency, WHITE)

    def visit(node: str, stack: list[str]) -> list[str] | None:
        color[node] = GREY
        stack.append(node)
        for neighbour in adjacency[node]:
            if color[neighbour] == GREY:
                return stack[stack.index(neighbour) :] + [neighbour]
            if color[neighbour] == WHITE:
                found = visit(neighbour, stack)
                if found is not None:
                    return found
        color[node] = BLACK
        stack.pop()
        return None

    for node in sorted(adjacency):
        if color[node] == WHITE:
            found = visit(node, [])
            if found is not None:
                return found
    return None


# ---------------------------------------------------------------------------
# Architecture domain
# ---------------------------------------------------------------------------
class LayersDeclaredRule(ValidationRule):
    """The architecture declares a non-empty, unique, ordered set of layers."""

    rule_id = "architecture.layers-declared"
    domain = ValidationDomain.ARCHITECTURE
    severity = RuleSeverity.BLOCKING
    description = "Architecture declares a non-empty, unique list of named layers."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        layers = _as_sequence(self.facts(target).get("layers"))
        if not layers:
            return self._failed("no architecture layers declared")
        if not all(isinstance(name, str) and name for name in layers):
            return self._failed("architecture layers contain an empty or non-string name")
        if len(set(layers)) != len(layers):
            return self._failed("architecture layers are not unique", layers=list(layers))
        return self._passed(layers=len(layers))


class ArchitectureAcyclicRule(ValidationRule):
    """The architecture dependency graph between layers/modules is acyclic."""

    rule_id = "architecture.dependencies-acyclic"
    domain = ValidationDomain.ARCHITECTURE
    severity = RuleSeverity.BLOCKING
    description = "The declared architecture dependency graph contains no cycle."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        deps = _as_sequence(self.facts(target).get("dependencies"))
        if deps is None:
            return self._failed("architecture dependencies are absent or malformed")
        edges: list[tuple[str, str]] = []
        for edge in deps:
            if not isinstance(edge, Mapping) or not edge.get("from") or not edge.get("to"):
                return self._failed("an architecture dependency edge is malformed", edge=edge)
            edges.append((str(edge["from"]), str(edge["to"])))
        cycle = _detect_cycle(edges)
        if cycle is not None:
            return self._failed("architecture dependency graph has a cycle", cycle=cycle)
        return self._passed(edges=len(edges))


class LayeringRespectedRule(ValidationRule):
    """Dependencies flow downward only: no layer depends on a higher layer."""

    rule_id = "architecture.layering-respected"
    domain = ValidationDomain.ARCHITECTURE
    severity = RuleSeverity.BLOCKING
    description = "Every dependency edge points from a higher layer to a same/lower layer."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        facts = self.facts(target)
        layers = _as_sequence(facts.get("layers"))
        deps = _as_sequence(facts.get("dependencies"))
        if not layers or deps is None:
            return self._failed("layers and/or dependencies are absent or malformed")
        rank = {str(name): index for index, name in enumerate(layers)}
        violations: list[dict[str, str]] = []
        for edge in deps:
            if not isinstance(edge, Mapping):
                return self._failed("an architecture dependency edge is malformed", edge=edge)
            src, dst = str(edge.get("from")), str(edge.get("to"))
            if src not in rank or dst not in rank:
                return self._failed(
                    "a dependency references an undeclared layer",
                    edge={"from": src, "to": dst},
                )
            if rank[dst] < rank[src]:
                violations.append({"from": src, "to": dst})
        if violations:
            return self._failed(
                "upward (layering-violating) dependencies found", violations=violations
            )
        return self._passed(edges=len(deps))


class NoFrozenWritesRule(ValidationRule):
    """No change targets the read-only certified corpus (DP-03 / C-01)."""

    rule_id = "architecture.no-frozen-writes"
    domain = ValidationDomain.ARCHITECTURE
    severity = RuleSeverity.BLOCKING
    description = (
        "No changed path writes to the frozen certified corpus (00-BOOK/00-SOURCE/99-FREEZE)."
    )

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        changed = _as_sequence(self.facts(target).get("changed_paths"))
        if changed is None:
            return self._failed("changed_paths are absent or malformed")
        paths = [str(p) for p in changed]
        violations = find_frozen_writes(paths)
        if violations:
            return self._failed(
                "writes to the read-only certified corpus detected",
                violations=violations,
                frozen_prefixes=list(FROZEN_PREFIXES),
            )
        return self._passed(checked=len(paths))


# ---------------------------------------------------------------------------
# Implementation domain
# ---------------------------------------------------------------------------
class ModulesPresentRule(ValidationRule):
    """Every declared implementation module is present."""

    rule_id = "implementation.modules-present"
    domain = ValidationDomain.IMPLEMENTATION
    severity = RuleSeverity.BLOCKING
    description = "A non-empty set of declared modules, each marked present."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        modules = _as_sequence(self.facts(target).get("modules"))
        if not modules:
            return self._failed("no implementation modules declared")
        missing: list[str] = []
        for module in modules:
            if not isinstance(module, Mapping) or not module.get("id"):
                return self._failed("an implementation module is malformed", module=module)
            if not bool(module.get("present", False)):
                missing.append(str(module["id"]))
        if missing:
            return self._failed("declared modules are missing", missing=missing)
        return self._passed(modules=len(modules))


class EntrypointsResolvedRule(ValidationRule):
    """Every declared entrypoint resolves."""

    rule_id = "implementation.entrypoints-resolved"
    domain = ValidationDomain.IMPLEMENTATION
    severity = RuleSeverity.BLOCKING
    description = "A non-empty set of declared entrypoints, each marked resolved."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        entrypoints = _as_sequence(self.facts(target).get("entrypoints"))
        if not entrypoints:
            return self._failed("no entrypoints declared")
        unresolved: list[str] = []
        for entry in entrypoints:
            if not isinstance(entry, Mapping) or not entry.get("name"):
                return self._failed("an entrypoint declaration is malformed", entry=entry)
            if not bool(entry.get("resolved", False)):
                unresolved.append(str(entry["name"]))
        if unresolved:
            return self._failed("declared entrypoints are unresolved", unresolved=unresolved)
        return self._passed(entrypoints=len(entrypoints))


class NoOpenMarkersRule(ValidationRule):
    """No open work markers (TODO/FIXME) remain (advisory)."""

    rule_id = "implementation.no-open-markers"
    domain = ValidationDomain.IMPLEMENTATION
    severity = RuleSeverity.ADVISORY
    description = "The declared open-marker (TODO/FIXME) count is zero."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        raw = self.facts(target).get("open_markers")
        if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
            return self._failed("open_markers count is absent or malformed")
        if raw > 0:
            return self._failed("open work markers remain", open_markers=raw)
        return self._passed(open_markers=0)


# ---------------------------------------------------------------------------
# Dependency domain
# ---------------------------------------------------------------------------
class DependenciesPinnedRule(ValidationRule):
    """Every dependency is pinned by an explicit version or digest."""

    rule_id = "dependency.all-pinned"
    domain = ValidationDomain.DEPENDENCY
    severity = RuleSeverity.BLOCKING
    description = "Every declared dependency carries a non-empty version or digest."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        deps = _as_sequence(self.facts(target).get("dependencies"))
        if deps is None:
            return self._failed("dependencies are absent or malformed")
        unpinned: list[str] = []
        for dep in deps:
            if not isinstance(dep, Mapping) or not dep.get("id"):
                return self._failed("a dependency declaration is malformed", dependency=dep)
            if not (dep.get("version") or dep.get("digest")):
                unpinned.append(str(dep["id"]))
        if unpinned:
            return self._failed("dependencies are not pinned", unpinned=unpinned)
        return self._passed(dependencies=len(deps))


class DependenciesResolvedRule(ValidationRule):
    """Every dependency resolves to a known provider."""

    rule_id = "dependency.resolved"
    domain = ValidationDomain.DEPENDENCY
    severity = RuleSeverity.BLOCKING
    description = "Every dependency's provider is present in the declared provider set."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        facts = self.facts(target)
        deps = _as_sequence(facts.get("dependencies"))
        providers_raw = _as_sequence(facts.get("providers"))
        if deps is None or providers_raw is None:
            return self._failed("dependencies and/or providers are absent or malformed")
        providers = {str(p) for p in providers_raw}
        unresolved: list[str] = []
        for dep in deps:
            if not isinstance(dep, Mapping) or not dep.get("id"):
                return self._failed("a dependency declaration is malformed", dependency=dep)
            provider = str(dep.get("provider", dep["id"]))
            if provider not in providers:
                unresolved.append(provider)
        if unresolved:
            return self._failed("dependencies resolve to unknown providers", unresolved=unresolved)
        return self._passed(dependencies=len(deps), providers=len(providers))


class DependencyAcyclicRule(ValidationRule):
    """The dependency graph is acyclic."""

    rule_id = "dependency.acyclic"
    domain = ValidationDomain.DEPENDENCY
    severity = RuleSeverity.BLOCKING
    description = "The declared dependency edge set contains no cycle."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        edges_raw = _as_sequence(self.facts(target).get("edges"))
        if edges_raw is None:
            return self._failed("dependency edges are absent or malformed")
        edges: list[tuple[str, str]] = []
        for edge in edges_raw:
            if not isinstance(edge, Mapping) or not edge.get("from") or not edge.get("to"):
                return self._failed("a dependency edge is malformed", edge=edge)
            edges.append((str(edge["from"]), str(edge["to"])))
        cycle = _detect_cycle(edges)
        if cycle is not None:
            return self._failed("dependency graph has a cycle", cycle=cycle)
        return self._passed(edges=len(edges))


# ---------------------------------------------------------------------------
# Registry domain
# ---------------------------------------------------------------------------
class RegistryEntriesWellFormedRule(ValidationRule):
    """Every registry entry is well-formed (id + kind + content hash)."""

    rule_id = "registry.entries-well-formed"
    domain = ValidationDomain.REGISTRY
    severity = RuleSeverity.BLOCKING
    description = "A non-empty registry whose every entry has an id, a kind, and a content_hash."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        entries = _as_sequence(self.facts(target).get("entries"))
        if not entries:
            return self._failed("registry has no entries")
        malformed: list[Any] = []
        for entry in entries:
            if not isinstance(entry, Mapping) or not all(
                entry.get(key) for key in ("id", "kind", "content_hash")
            ):
                malformed.append(entry.get("id") if isinstance(entry, Mapping) else entry)
        if malformed:
            return self._failed("registry entries are malformed", malformed=malformed)
        return self._passed(entries=len(entries))


class RegistryIdsUniqueRule(ValidationRule):
    """Registry entry ids are unique."""

    rule_id = "registry.ids-unique"
    domain = ValidationDomain.REGISTRY
    severity = RuleSeverity.BLOCKING
    description = "No two registry entries share an id."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        entries = _as_sequence(self.facts(target).get("entries"))
        if not entries:
            return self._failed("registry has no entries")
        seen: set[str] = set()
        duplicates: set[str] = set()
        for entry in entries:
            if not isinstance(entry, Mapping) or not entry.get("id"):
                return self._failed("a registry entry is malformed", entry=entry)
            entry_id = str(entry["id"])
            if entry_id in seen:
                duplicates.add(entry_id)
            seen.add(entry_id)
        if duplicates:
            return self._failed("registry entry ids are not unique", duplicates=sorted(duplicates))
        return self._passed(entries=len(entries))


class RegistryReferentialIntegrityRule(ValidationRule):
    """Every registry reference points to an existing entry."""

    rule_id = "registry.referential-integrity"
    domain = ValidationDomain.REGISTRY
    severity = RuleSeverity.BLOCKING
    description = "Every reference target resolves to a declared registry entry id."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        facts = self.facts(target)
        entries = _as_sequence(facts.get("entries"))
        references = _as_sequence(facts.get("references"))
        if entries is None or references is None:
            return self._failed("registry entries and/or references are absent or malformed")
        ids = {str(e["id"]) for e in entries if isinstance(e, Mapping) and e.get("id")}
        dangling: list[dict[str, str]] = []
        for ref in references:
            if not isinstance(ref, Mapping) or not ref.get("from") or not ref.get("to"):
                return self._failed("a registry reference is malformed", reference=ref)
            if str(ref["to"]) not in ids:
                dangling.append({"from": str(ref["from"]), "to": str(ref["to"])})
        if dangling:
            return self._failed("registry references are dangling", dangling=dangling)
        return self._passed(references=len(references))


# ---------------------------------------------------------------------------
# Schema domain
# ---------------------------------------------------------------------------
class SchemaVersionedRule(ValidationRule):
    """Every declared schema carries a version."""

    rule_id = "schema.versioned"
    domain = ValidationDomain.SCHEMA
    severity = RuleSeverity.BLOCKING
    description = "A non-empty schema set whose every schema has a non-empty version."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        schemas = self.facts(target).get("schemas")
        if not isinstance(schemas, Mapping) or not schemas:
            return self._failed("no schemas declared")
        unversioned: list[str] = []
        for name, definition in schemas.items():
            if not isinstance(definition, Mapping) or not definition.get("version"):
                unversioned.append(str(name))
        if unversioned:
            return self._failed("schemas are missing a version", unversioned=sorted(unversioned))
        return self._passed(schemas=len(schemas))


class RecordsConformRule(ValidationRule):
    """Every record conforms to its declared schema's required fields."""

    rule_id = "schema.records-conform"
    domain = ValidationDomain.SCHEMA
    severity = RuleSeverity.BLOCKING
    description = "Every record names a known schema and carries all its required fields."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        facts = self.facts(target)
        schemas = facts.get("schemas")
        records = _as_sequence(facts.get("records"))
        if not isinstance(schemas, Mapping) or records is None:
            return self._failed("schemas and/or records are absent or malformed")
        nonconforming: list[dict[str, Any]] = []
        for record in records:
            if not isinstance(record, Mapping) or not record.get("schema"):
                return self._failed("a record is malformed", record=record)
            schema_name = str(record["schema"])
            definition = schemas.get(schema_name)
            if not isinstance(definition, Mapping):
                nonconforming.append({"schema": schema_name, "reason": "unknown-schema"})
                continue
            required = _as_sequence(definition.get("required")) or []
            fields = record.get("fields")
            present = set(fields.keys()) if isinstance(fields, Mapping) else set()
            missing = [str(f) for f in required if str(f) not in present]
            if missing:
                nonconforming.append({"schema": schema_name, "missing": missing})
        if nonconforming:
            return self._failed(
                "records do not conform to their schema", nonconforming=nonconforming
            )
        return self._passed(records=len(records))


# ---------------------------------------------------------------------------
# Runtime domain
# ---------------------------------------------------------------------------
class DisclosurePresentRule(ValidationRule):
    """The EC-1 provisional-state disclosure is present and well-formed (DE-05)."""

    rule_id = "runtime.disclosure-present"
    domain = ValidationDomain.RUNTIME
    severity = RuleSeverity.BLOCKING
    description = "The EC-1 provisional-state disclosure is present and asserts no finality."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        disclosure = self.facts(target).get("disclosure")
        if not disclosure_present(disclosure if isinstance(disclosure, dict) else None):
            return self._failed("EC-1 provisional-state disclosure is absent or malformed")
        return self._passed(disclosure_id=disclosure.get("disclosure_id"))


class RuntimeIdentityRule(ValidationRule):
    """Every runtime unit has a deterministic, well-formed identity."""

    rule_id = "runtime.identity-deterministic"
    domain = ValidationDomain.RUNTIME
    severity = RuleSeverity.BLOCKING
    description = (
        "Every runtime unit id matches the deterministic UCOS-RUN-<blueprint>-<hex16> form."
    )

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        units = _as_sequence(self.facts(target).get("units"))
        if not units:
            return self._failed("no runtime units declared")
        malformed: list[str] = []
        for unit in units:
            if not isinstance(unit, Mapping):
                return self._failed("a runtime unit is malformed", unit=unit)
            runtime_id = str(unit.get("runtime_id", ""))
            if not _RUNTIME_ID.match(runtime_id):
                malformed.append(runtime_id)
        if malformed:
            return self._failed(
                "runtime ids are not in the deterministic form", malformed=malformed
            )
        return self._passed(units=len(units))


class RuntimeImagePinnedRule(ValidationRule):
    """Every runtime image is pinned by digest to its package hash."""

    rule_id = "runtime.image-digest-pinned"
    domain = ValidationDomain.RUNTIME
    severity = RuleSeverity.BLOCKING
    description = "Every runtime image reference is pinned by @sha256:<package_sha256>."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        units = _as_sequence(self.facts(target).get("units"))
        if not units:
            return self._failed("no runtime units declared")
        unpinned: list[str] = []
        for unit in units:
            if not isinstance(unit, Mapping):
                return self._failed("a runtime unit is malformed", unit=unit)
            package_sha256 = str(unit.get("package_sha256", ""))
            image_reference = str(unit.get("image_reference", ""))
            expected = f"@sha256:{package_sha256}"
            if not package_sha256 or expected not in image_reference:
                unpinned.append(image_reference)
        if unpinned:
            return self._failed("runtime images are not digest-pinned", unpinned=unpinned)
        return self._passed(units=len(units))


# ---------------------------------------------------------------------------
# Quality domain
# ---------------------------------------------------------------------------
class CoverageThresholdRule(ValidationRule):
    """Line coverage meets or exceeds the required threshold."""

    rule_id = "quality.coverage-threshold"
    domain = ValidationDomain.QUALITY
    severity = RuleSeverity.BLOCKING
    description = "Reported line coverage meets or exceeds the declared minimum (default 90%)."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        facts = self.facts(target)
        actual = facts.get("line_percent")
        if not isinstance(actual, int | float) or isinstance(actual, bool):
            return self._failed("line coverage is absent or malformed")
        try:
            minimum = float(facts.get("min_percent", 90.0))
        except (TypeError, ValueError):
            return self._failed("coverage minimum is malformed")
        actual_f = float(actual)
        if actual_f < minimum:
            return self._failed(
                "line coverage is below the minimum",
                line_percent=actual_f,
                min_percent=minimum,
            )
        return self._passed(line_percent=actual_f, min_percent=minimum)


class TestsPassingRule(ValidationRule):
    """The test suite passed with at least one test and zero failures."""

    rule_id = "quality.tests-passing"
    domain = ValidationDomain.QUALITY
    severity = RuleSeverity.BLOCKING
    description = "A non-empty test run with zero failures."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        tests = self.facts(target).get("tests")
        if not isinstance(tests, Mapping):
            return self._failed("test results are absent or malformed")
        passed = tests.get("passed")
        failed = tests.get("failed")
        if not isinstance(passed, int) or isinstance(passed, bool) or passed < 0:
            return self._failed("test passed-count is malformed")
        if not isinstance(failed, int) or isinstance(failed, bool) or failed < 0:
            return self._failed("test failed-count is malformed")
        if failed > 0:
            return self._failed("the test suite has failures", passed=passed, failed=failed)
        if passed == 0:
            return self._failed("no tests were run")
        return self._passed(passed=passed, failed=0)


class LintCleanRule(ValidationRule):
    """No lint violations remain (advisory)."""

    rule_id = "quality.lint-clean"
    domain = ValidationDomain.QUALITY
    severity = RuleSeverity.ADVISORY
    description = "The declared lint-violation count is zero."

    def evaluate(self, target: ValidationTarget) -> RuleResult:
        raw = self.facts(target).get("lint_violations")
        if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
            return self._failed("lint-violation count is absent or malformed")
        if raw > 0:
            return self._failed("lint violations remain", lint_violations=raw)
        return self._passed(lint_violations=0)


# ---------------------------------------------------------------------------
# the built-in suite
# ---------------------------------------------------------------------------
def default_rules() -> tuple[ValidationRule, ...]:
    """Return the built-in universal validation suite, ordered deterministically.

    Ordering is by (domain declaration order, rule id) so the suite is stable across
    runs and processes (IMP-007 §5).
    """
    rules: tuple[ValidationRule, ...] = (
        # architecture
        LayersDeclaredRule(),
        ArchitectureAcyclicRule(),
        LayeringRespectedRule(),
        NoFrozenWritesRule(),
        # implementation
        ModulesPresentRule(),
        EntrypointsResolvedRule(),
        NoOpenMarkersRule(),
        # dependency
        DependenciesPinnedRule(),
        DependenciesResolvedRule(),
        DependencyAcyclicRule(),
        # registry
        RegistryEntriesWellFormedRule(),
        RegistryIdsUniqueRule(),
        RegistryReferentialIntegrityRule(),
        # schema
        SchemaVersionedRule(),
        RecordsConformRule(),
        # runtime
        DisclosurePresentRule(),
        RuntimeIdentityRule(),
        RuntimeImagePinnedRule(),
        # quality
        CoverageThresholdRule(),
        TestsPassingRule(),
        LintCleanRule(),
    )
    return tuple(sorted(rules, key=lambda r: (r.domain.order, r.rule_id)))


__all__ = [
    "ValidationRule",
    # architecture
    "LayersDeclaredRule",
    "ArchitectureAcyclicRule",
    "LayeringRespectedRule",
    "NoFrozenWritesRule",
    # implementation
    "ModulesPresentRule",
    "EntrypointsResolvedRule",
    "NoOpenMarkersRule",
    # dependency
    "DependenciesPinnedRule",
    "DependenciesResolvedRule",
    "DependencyAcyclicRule",
    # registry
    "RegistryEntriesWellFormedRule",
    "RegistryIdsUniqueRule",
    "RegistryReferentialIntegrityRule",
    # schema
    "SchemaVersionedRule",
    "RecordsConformRule",
    # runtime
    "DisclosurePresentRule",
    "RuntimeIdentityRule",
    "RuntimeImagePinnedRule",
    # quality
    "CoverageThresholdRule",
    "TestsPassingRule",
    "LintCleanRule",
    "default_rules",
]

"""UCON-000001 Part 02 — the declaration, rehydrated, and refused when unusable.

Every vocabulary this capability has is DATA in ``00-MASTER/UCON-000001/ucon-declaration.json``:
the construct kinds, the dispositions and what each permits, the reality states and their
transitions, the ordered disposition rules, the unknown and contradiction classes, the
research states, the discovery scales, the extension points, the audit configuration and the
laws. There is no kind name, no disposition name, no reality state, no rule and no operator
literal below except the four structural tokens the model itself is made of — the reflective
root key, the catch-all marker, and the two names the two-way binding is expressed in.

A declaration that cannot be read is a FAULT, and a fault is not a verdict. That distinction
is why :class:`DeclarationError` exists separately from a closed gate: "the rule set refused
this construct" and "the rule set could not be loaded" are different facts about the world,
and a gate that collapses them lets an unreadable declaration pass as whichever answer was
more convenient at the time.

The binding between declared laws and implemented checks is enforced in BOTH directions by
:meth:`Declaration.validate`. A law naming a check that does not exist is manual governance
wearing an engine's costume; a check that exists but no law claims is dead code that looks
like enforcement. UISD-000001 established that both are hard failures in this repository, and
the same rule is applied here to laws, to disposition operators and to facets.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.construct.model import ConstructError
from engine.uckp.payload import canonical_payload

#: The declaration's home, relative to the repository root. Read; never written.
DECLARATION_PATH = os.path.join("00-MASTER", "UCON-000001", "ucon-declaration.json")

#: The marker on the one rule that must be last. Structural, not a vocabulary member.
CATCH_ALL_KEY = "catch_all"


class DeclarationError(ConstructError):
    """The declaration is absent, unparseable or incoherent. A fault, never a verdict."""


#: Parsed fields deliberately outside the certification identity, each with the reason it
#: cannot reach a verdict. Inclusion is the default: a field absent from the identity and
#: absent from here is a defect, and the suite fails in BOTH directions — on an undeclared
#: omission and on an exclusion that names a field this declaration no longer has.
DIGEST_EXCLUSIONS: Mapping[str, str] = {
    "source": (
        "the path the declaration was read from. A digest that changed with the reader would "
        "not be a digest of the declaration."
    ),
}


def repo_root() -> str:
    """The repository root, derived from this file's location rather than a cwd guess."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _require(document: Mapping[str, Any], key: str) -> Any:
    if key not in document or document[key] in (None, "", [], {}):
        raise DeclarationError(f"declaration section {key!r} is absent or empty")
    return document[key]


def _rows(value: Any, *, section: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str) or not value:
        raise DeclarationError(f"declaration section {section!r} must be a non-empty list")
    for row in value:
        if not isinstance(row, Mapping):
            raise DeclarationError(f"declaration section {section!r} holds a non-object row")
    return tuple(value)


# --- declared vocabularies ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Facet:
    """The fields a construct of a facet-bearing kind must and may supply."""

    name: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    definition: str


@dataclass(frozen=True, slots=True)
class KindSpec:
    """One declared construct kind. A seed member, not a member of a closed universe."""

    kind: str
    title: str
    facet: str
    parent: str | None
    definition: str


@dataclass(frozen=True, slots=True)
class DispositionSpec:
    """One disposition, what it permits, and what it may become."""

    identifier: str
    title: str
    definition: str
    terminal: bool
    permits: frozenset[str]
    successors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RealitySpec:
    """One reality state, its evidence floors, what it permits, and what it may become."""

    identifier: str
    title: str
    definition: str
    evidence_floor: int
    independent_sources_floor: int
    permits: frozenset[str]
    successors: tuple[str, ...]
    ceu_binding: Mapping[str, str] | None
    binding_gap: Mapping[str, Any] | None


@dataclass(frozen=True, slots=True)
class Clause:
    """One predicate clause of a rule: the operator name plus its declared arguments."""

    operator: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class Rule:
    """One disposition rule. Ordered; first match wins; exactly one is the catch-all."""

    rule_id: str
    disposition: str
    when: tuple[Clause, ...]
    rationale: str
    catch_all: bool


@dataclass(frozen=True, slots=True)
class DiscoverySource:
    """One declared source of discovery: what to select, and how the opportunity is scored."""

    source_id: str
    selector: str
    arguments: Mapping[str, Any]
    priority: str
    impact: str
    opportunity: str
    definition: str


@dataclass(frozen=True, slots=True)
class ExtensionPoint:
    """One declared self-extension: the subject, the kind that carries it, and its owner."""

    point_id: str
    subject: str
    kind: str
    owner: str
    admission: str
    exercised_by: str


@dataclass(frozen=True, slots=True)
class ClosureForm:
    """One form of closure the audit detects, with its limitation and migration path."""

    form: str
    detection: str
    limitation: str
    migration: str


@dataclass(frozen=True, slots=True)
class Disclosure:
    """One closure inside governed scope that is declared, with its admission path."""

    closure_id: str
    module: str
    symbol: str
    form: str
    intentional: bool
    closing_invariant: str
    admission: str
    gap: str | None


@dataclass(frozen=True, slots=True)
class AuditSpec:
    """The audit configuration: where to look, what counts, who owns it, and the ratchet."""

    roots: tuple[str, ...]
    extensions: tuple[str, ...]
    exclude_dir_names: frozenset[str]
    exclude_dir_prefixes: tuple[str, ...]
    forms: tuple[ClosureForm, ...]
    risk_tiers: tuple[Mapping[str, str], ...]
    declared_tiers: tuple[Mapping[str, str], ...]
    governed_scope: tuple[str, ...]
    undeclared_tier: str
    deliberate_tier: str
    disclosures: tuple[Disclosure, ...]
    baseline: Mapping[str, int]

    @property
    def intentional_disclosures(self) -> frozenset[str]:
        """The closure ids disclosed as intentional — the population the R4 criterion names."""
        return frozenset(
            disclosure.closure_id for disclosure in self.disclosures if disclosure.intentional
        )

    def tier_for(self, module: str) -> tuple[str, str]:
        """The declared (tier, owner) for a module, by longest declared prefix.

        Longest-prefix rather than first-match, so declaring a narrower owner never depends
        on where in the list it was written. A module no prefix claims is the caller's to
        classify conservatively; this method reports the absence rather than inventing a tier.
        """
        best: tuple[str, str] | None = None
        best_len = -1
        for row in self.declared_tiers:
            prefix = str(row.get("prefix") or "")
            if prefix and module.startswith(prefix) and len(prefix) > best_len:
                best, best_len = (str(row.get("tier")), str(row.get("owner"))), len(prefix)
        return best if best is not None else ("", "")

    def in_governed_scope(self, module: str) -> bool:
        return any(module.startswith(prefix) for prefix in self.governed_scope)


@dataclass(frozen=True, slots=True)
class Law:
    """One law: the statement, the check that measures it, and whether it blocks."""

    law_id: str
    statement: str
    check: str
    blocking: bool


# --- the declaration ------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Declaration:
    """The whole declaration as a value. Holds no list of its own beyond what it read.

    None of the accessors default. ``disposition("MADE-UP")`` raises rather than returning a
    fallback, because a fallback here would be an undeclared vocabulary member admitted at a
    call site — the exact closure mechanism this capability exists to inventory.
    """

    artifact_id: str
    version: str
    authority: str
    principle: Mapping[str, Any]
    initial_reality_state: str
    seed_reality_state: str
    reflective_root: str
    registration_dispositions: frozenset[str]
    facets: Mapping[str, Facet]
    kinds: tuple[KindSpec, ...]
    dispositions: tuple[DispositionSpec, ...]
    reality_states: tuple[RealitySpec, ...]
    operational_acts: tuple[str, ...]
    rules: tuple[Rule, ...]
    claimed_operators: frozenset[str]
    catch_all_disposition: str
    claim_scan: Mapping[str, Any]
    unknown_classes: tuple[str, ...]
    contradiction_classes: tuple[str, ...]
    resolution_states: tuple[str, ...]
    contradicting_states: frozenset[str]
    research_states: tuple[str, ...]
    priority_scale: tuple[str, ...]
    impact_scale: tuple[str, ...]
    discovery_sources: tuple[DiscoverySource, ...]
    claimed_selectors: frozenset[str]
    research_key_prefix: str
    discovery_key_prefix: str
    extension_points: tuple[ExtensionPoint, ...]
    probe_key_prefix: str
    claimed_admissions: frozenset[str]
    audit: AuditSpec
    laws: tuple[Law, ...]
    self_application: Mapping[str, Any]
    evidence_home: str
    evidence_records: tuple[Mapping[str, Any], ...]
    gate: Mapping[str, Any]
    source: str = field(default="", compare=False, repr=False)

    # --- accessors, none of which default --------------------------------------------------

    @property
    def disposition_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.dispositions)

    @property
    def reality_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.reality_states)

    @property
    def kind_names(self) -> tuple[str, ...]:
        return tuple(spec.kind for spec in self.kinds)

    @property
    def catch_all(self) -> Rule:
        """The one catch-all rule. Its existence is checked at load, so this cannot fail."""
        return next(rule for rule in self.rules if rule.catch_all)

    def disposition(self, identifier: str) -> DispositionSpec:
        for spec in self.dispositions:
            if spec.identifier == identifier:
                return spec
        raise DeclarationError(f"no declared disposition {identifier!r}")

    def reality(self, identifier: str) -> RealitySpec:
        for spec in self.reality_states:
            if spec.identifier == identifier:
                return spec
        raise DeclarationError(f"no declared reality state {identifier!r}")

    def kind(self, name: str) -> KindSpec:
        for spec in self.kinds:
            if spec.kind == name:
                return spec
        raise DeclarationError(f"no declared construct kind {name!r}")

    def facet(self, name: str) -> Facet:
        if name not in self.facets:
            raise DeclarationError(f"no declared facet {name!r}")
        return self.facets[name]

    def law(self, law_id: str) -> Law:
        for law in self.laws:
            if law.law_id == law_id:
                return law
        raise DeclarationError(f"no declared law {law_id!r}")

    def extension_point(self, point_id: str) -> ExtensionPoint:
        for point in self.extension_points:
            if point.point_id == point_id:
                return point
        raise DeclarationError(f"no declared extension point {point_id!r}")

    # --- the two-way bindings --------------------------------------------------------------

    def validate(
        self,
        available_checks: frozenset[str],
        available_operators: frozenset[str],
        available_selectors: frozenset[str] = frozenset(),
        available_admissions: frozenset[str] = frozenset(),
        available_forms: frozenset[str] = frozenset(),
    ) -> list[str]:
        """Every structural incoherence in the declaration, or an empty list.

        Refuses in both directions for laws and for operators. Also refuses a rule set that
        is not total, a catch-all that is not last, a permission naming an undeclared act, a
        successor naming an undeclared state, and a kind naming an undeclared facet or an
        absent parent — each of which would make some later measurement report a verdict it
        never computed.
        """
        problems: list[str] = []

        claimed_checks = {law.check for law in self.laws}
        for law in self.laws:
            if law.check not in available_checks:
                problems.append(
                    f"{law.law_id}: names check {law.check!r}, which is not implemented"
                )
        for orphan in sorted(available_checks - claimed_checks):
            problems.append(f"check {orphan!r} is implemented but no law claims it")

        used_operators = {clause.operator for rule in self.rules for clause in rule.when}
        for rule in self.rules:
            for clause in rule.when:
                if clause.operator not in available_operators:
                    problems.append(
                        f"{rule.rule_id}: names operator {clause.operator!r}, "
                        "which is not implemented"
                    )
        for orphan in sorted(available_operators - used_operators):
            problems.append(f"operator {orphan!r} is implemented but no rule claims it")
        for orphan in sorted(self.claimed_operators - available_operators):
            problems.append(
                f"operator {orphan!r} is claimed by the declaration but not implemented"
            )
        for orphan in sorted(available_operators - self.claimed_operators):
            problems.append(f"operator {orphan!r} is implemented but the declaration omits it")

        catch_alls = [rule for rule in self.rules if rule.catch_all]
        if len(catch_alls) != 1:
            problems.append(
                f"the rule set declares {len(catch_alls)} catch-all rules; exactly one is "
                "required or disposition is not a total function"
            )
        elif self.rules[-1] is not catch_alls[0]:
            problems.append(
                f"the catch-all rule {catch_alls[0].rule_id!r} is not last, so the rules "
                "after it are unreachable"
            )

        acts = set(self.operational_acts)
        declared_dispositions = set(self.disposition_ids)
        for spec in self.dispositions:
            for act in sorted(spec.permits - acts):
                problems.append(f"disposition {spec.identifier}: permits undeclared act {act!r}")
            for successor in spec.successors:
                if successor not in declared_dispositions:
                    problems.append(
                        f"disposition {spec.identifier}: names undeclared successor {successor!r}"
                    )
        for rule in self.rules:
            if rule.disposition not in declared_dispositions:
                problems.append(
                    f"{rule.rule_id}: assigns undeclared disposition {rule.disposition!r}"
                )

        declared_reality = set(self.reality_ids)
        if self.initial_reality_state not in declared_reality:
            problems.append(
                f"initial_reality_state {self.initial_reality_state!r} is not a declared state"
            )
        if self.seed_reality_state not in declared_reality:
            problems.append(
                f"seed_reality_state {self.seed_reality_state!r} is not a declared state"
            )
        for spec in self.reality_states:
            for act in sorted(spec.permits - acts):
                problems.append(f"reality state {spec.identifier}: permits undeclared act {act!r}")
            for successor in spec.successors:
                if successor not in declared_reality:
                    problems.append(
                        f"reality state {spec.identifier}: names undeclared successor "
                        f"{successor!r}"
                    )
            if spec.ceu_binding is None and not spec.binding_gap:
                problems.append(
                    f"reality state {spec.identifier}: binds to no CEU row and discloses no gap"
                )

        for name in sorted(self.registration_dispositions - declared_dispositions):
            problems.append(f"registration_dispositions names undeclared disposition {name!r}")
        if not self.registration_dispositions:
            problems.append(
                "registration_dispositions is empty, so no registration could ever take effect"
            )

        names = set(self.kind_names)
        if self.reflective_root not in names:
            problems.append(f"the reflective root {self.reflective_root!r} is not a declared kind")
        for spec in self.kinds:
            if spec.facet not in self.facets:
                problems.append(f"kind {spec.kind}: names undeclared facet {spec.facet!r}")
            if spec.parent is not None and spec.parent not in names:
                problems.append(f"kind {spec.kind}: names absent parent {spec.parent!r}")

        for point in self.extension_points:
            if point.kind not in names:
                problems.append(f"{point.point_id}: carries undeclared kind {point.kind!r}")
            if point.exercised_by not in {law.law_id for law in self.laws}:
                problems.append(
                    f"{point.point_id}: names {point.exercised_by!r} as its exercise, "
                    "which is not a declared law"
                )
            if available_admissions and point.admission not in available_admissions:
                problems.append(
                    f"{point.point_id}: names admission {point.admission!r}, "
                    "which is not implemented"
                )
        used_admissions = {point.admission for point in self.extension_points}
        for orphan in sorted(available_admissions - used_admissions):
            problems.append(f"admission {orphan!r} is implemented but no extension point claims it")
        if available_admissions:
            for orphan in sorted(self.claimed_admissions - available_admissions):
                problems.append(
                    f"admission {orphan!r} is claimed by the declaration but not implemented"
                )
            for orphan in sorted(available_admissions - self.claimed_admissions):
                problems.append(f"admission {orphan!r} is implemented but the declaration omits it")

        used_selectors = {source.selector for source in self.discovery_sources}
        for source in self.discovery_sources:
            if available_selectors and source.selector not in available_selectors:
                problems.append(
                    f"{source.source_id}: names selector {source.selector!r}, "
                    "which is not implemented"
                )
            if source.priority not in self.priority_scale:
                problems.append(
                    f"{source.source_id}: names undeclared priority {source.priority!r}"
                )
            if source.impact not in self.impact_scale:
                problems.append(f"{source.source_id}: names undeclared impact {source.impact!r}")
        for orphan in sorted(available_selectors - used_selectors):
            problems.append(f"selector {orphan!r} is implemented but no discovery source claims it")
        if available_selectors:
            for orphan in sorted(self.claimed_selectors - available_selectors):
                problems.append(
                    f"selector {orphan!r} is claimed by the declaration but not implemented"
                )
            for orphan in sorted(available_selectors - self.claimed_selectors):
                problems.append(f"selector {orphan!r} is implemented but the declaration omits it")

        declared_forms = {form.form for form in self.audit.forms}
        for orphan in sorted(available_forms - declared_forms):
            problems.append(f"closure form {orphan!r} is detectable but the declaration omits it")
        for form in sorted(declared_forms - available_forms) if available_forms else []:
            problems.append(f"closure form {form!r} is declared but no detector implements it")
        if self.audit.undeclared_tier not in {str(row["tier"]) for row in self.audit.risk_tiers}:
            problems.append(
                f"undeclared_tier {self.audit.undeclared_tier!r} is not a declared risk tier"
            )
        if self.audit.deliberate_tier not in {str(row["tier"]) for row in self.audit.risk_tiers}:
            problems.append(
                f"deliberate_tier {self.audit.deliberate_tier!r} is not a declared risk tier"
            )
        for disclosure in self.audit.disclosures:
            if disclosure.form not in declared_forms:
                problems.append(
                    f"{disclosure.closure_id}: names undeclared closure form {disclosure.form!r}"
                )
            if not disclosure.intentional and not disclosure.gap:
                problems.append(
                    f"{disclosure.closure_id}: is not intentional and names no gap, so it is "
                    "an undisclosed finite assumption wearing a disclosure's name"
                )
        for form in declared_forms:
            if form not in self.audit.baseline:
                problems.append(f"closure form {form!r} has no declared baseline")

        return problems

    def require_valid(
        self,
        available_checks: frozenset[str],
        available_operators: frozenset[str],
        available_selectors: frozenset[str] = frozenset(),
        available_admissions: frozenset[str] = frozenset(),
        available_forms: frozenset[str] = frozenset(),
    ) -> None:
        """Raise on the first structural incoherence, naming every one of them."""
        problems = self.validate(
            available_checks,
            available_operators,
            available_selectors,
            available_admissions,
            available_forms,
        )
        if problems:
            raise DeclarationError("the declaration is incoherent:\n  " + "\n  ".join(problems))

    def digest_payload(self) -> dict[str, Any]:
        """The declaration's certification identity: the WHOLE parsed declaration, minus
        the exclusions ``DIGEST_EXCLUSIONS`` names and states a reason for.

        THIS USED TO BE A PROJECTION, AND THE PROJECTION WAS WRONG. Eleven keys were listed
        here by hand and ten of them collapsed to bare identifier lists — ``laws`` was
        ``[law.law_id ...]``, ``rules`` was ``[rule.rule_id ...]``, ``reality_states`` was
        ``[spec.identifier ...]``. Everything those specs actually SAY was outside the
        identity. Measured, not supposed: flipping ``blocking`` on ``UCON-L-01`` — the flag
        ``contract.py`` reads to choose ``OPEN`` or ``CLOSED`` — left this digest byte-identical
        at ``192c63af…``, and so did rewriting a rule's assigned disposition and zeroing an
        evidence floor. A certification identity that does not move when the verdict's inputs
        move certifies nothing.

        Inclusion is now the default, derived from :func:`dataclasses.fields`, so a field added
        to :class:`Declaration` is inside the identity on the day it is written. Omitting one
        requires writing it into ``DIGEST_EXCLUSIONS`` with the reason it cannot reach a
        verdict, and ``test_construct_foundation.py`` refuses a stale exclusion in the other
        direction — an exclusion naming a field that no longer exists.

        The payload is taken over the PARSED structure rather than the raw document, because
        the parsed structure is the influence surface: it is what every law reads. It also
        keeps in-memory extension honest — ``extension.extended_with_disposition`` returns a
        declaration whose dispositions differ, and its identity now differs with them, which a
        digest over the unchanged source document would not have shown.
        """
        return canonical_payload(self, exclude=tuple(DIGEST_EXCLUSIONS))


def _facets(document: Mapping[str, Any]) -> dict[str, Facet]:
    raw = _require(document, "facets")
    if not isinstance(raw, Mapping):
        raise DeclarationError("declaration section 'facets' must be an object")
    return {
        str(name): Facet(
            name=str(name),
            required_fields=tuple(str(f) for f in (body.get("required_fields") or ())),
            optional_fields=tuple(str(f) for f in (body.get("optional_fields") or ())),
            definition=str(body.get("definition") or ""),
        )
        for name, body in raw.items()
    }


def _ids(section: Any, *, name: str) -> tuple[str, ...]:
    return tuple(str(row["id"]) for row in _rows(section, section=name))


def parse(document: Mapping[str, Any], *, source: str = "") -> Declaration:
    """Rehydrate a declaration document. Raises :class:`DeclarationError` when unusable."""
    if not isinstance(document, Mapping):
        raise DeclarationError("the declaration must be a JSON object")

    kinds_section = _require(document, "construct_kinds")
    unknown_section = _require(document, "unknown_classes")
    contradiction_section = _require(document, "contradiction_classes")
    discovery_section = _require(document, "discovery")
    audit_section = _require(document, "audit")
    rules_section = _require(document, "disposition_rules")

    try:
        rules = tuple(
            Rule(
                rule_id=str(row["rule_id"]),
                disposition=str(row["disposition"]),
                when=tuple(
                    Clause(
                        operator=str(clause["operator"]),
                        arguments={str(k): v for k, v in clause.items() if k != "operator"},
                    )
                    for clause in _rows(row.get("when"), section=f"{row['rule_id']}.when")
                ),
                rationale=str(row.get("rationale") or ""),
                catch_all=bool(row.get(CATCH_ALL_KEY, False)),
            )
            for row in _rows(rules_section.get("rules"), section="disposition_rules.rules")
        )

        audit = AuditSpec(
            roots=tuple(str(r) for r in _require(audit_section, "roots")),
            extensions=tuple(str(e) for e in _require(audit_section, "extensions")),
            exclude_dir_names=frozenset(
                str(d) for d in (audit_section.get("exclude_dir_names") or ())
            ),
            exclude_dir_prefixes=tuple(
                str(d) for d in (audit_section.get("exclude_dir_prefixes") or ())
            ),
            forms=tuple(
                ClosureForm(
                    form=str(row["form"]),
                    detection=str(row["detection"]),
                    limitation=str(row["limitation"]),
                    migration=str(row["migration"]),
                )
                for row in _rows(audit_section.get("closure_forms"), section="audit.closure_forms")
            ),
            risk_tiers=_rows(audit_section.get("risk_tiers"), section="audit.risk_tiers"),
            declared_tiers=_rows(
                audit_section.get("declared_tiers"), section="audit.declared_tiers"
            ),
            governed_scope=tuple(str(p) for p in _require(audit_section, "governed_scope")),
            undeclared_tier=str(_require(audit_section, "undeclared_tier")),
            deliberate_tier=str(_require(audit_section, "deliberate_tier")),
            disclosures=tuple(
                Disclosure(
                    closure_id=str(row["closure_id"]),
                    module=str(row["module"]),
                    symbol=str(row["symbol"]),
                    form=str(row["form"]),
                    intentional=bool(row.get("intentional", False)),
                    closing_invariant=str(row.get("closing_invariant") or ""),
                    admission=str(row.get("admission") or ""),
                    gap=(str(row["gap"]) if row.get("gap") else None),
                )
                for row in (audit_section.get("disclosed_closures") or ())
            ),
            baseline={
                str(k): int(v)
                for k, v in (audit_section.get("baseline") or {}).items()
                if not k.startswith("$") and isinstance(v, int) and not isinstance(v, bool)
            },
        )

        return Declaration(
            artifact_id=str(_require(document, "artifact_id")),
            version=str(_require(document, "version")),
            authority=str(_require(document, "authority")),
            principle=_require(document, "principle"),
            initial_reality_state=str(_require(document, "initial_reality_state")),
            seed_reality_state=str(_require(kinds_section, "seed_reality_state")),
            reflective_root=str(_require(kinds_section, "reflective_root")),
            registration_dispositions=frozenset(
                str(name) for name in _require(kinds_section, "registration_dispositions")
            ),
            facets=_facets(document),
            kinds=tuple(
                KindSpec(
                    kind=str(row["kind"]),
                    title=str(row.get("title") or row["kind"]),
                    facet=str(row.get("facet") or "none"),
                    parent=(str(row["parent"]) if row.get("parent") else None),
                    definition=str(row.get("definition") or ""),
                )
                for row in _rows(kinds_section.get("seed"), section="construct_kinds.seed")
            ),
            dispositions=tuple(
                DispositionSpec(
                    identifier=str(row["id"]),
                    title=str(row.get("title") or row["id"]),
                    definition=str(row.get("definition") or ""),
                    terminal=bool(row.get("terminal", False)),
                    permits=frozenset(str(a) for a in (row.get("permits") or ())),
                    successors=tuple(str(s) for s in (row.get("successors") or ())),
                )
                for row in _rows(document.get("dispositions"), section="dispositions")
            ),
            reality_states=tuple(
                RealitySpec(
                    identifier=str(row["id"]),
                    title=str(row.get("title") or row["id"]),
                    definition=str(row.get("definition") or ""),
                    evidence_floor=int(row.get("evidence_floor", 0)),
                    independent_sources_floor=int(row.get("independent_sources_floor", 0)),
                    permits=frozenset(str(a) for a in (row.get("permits") or ())),
                    successors=tuple(str(s) for s in (row.get("successors") or ())),
                    ceu_binding=(
                        {str(k): str(v) for k, v in row["ceu_binding"].items()}
                        if row.get("ceu_binding")
                        else None
                    ),
                    binding_gap=row.get("binding_gap"),
                )
                for row in _rows(document.get("reality_states"), section="reality_states")
            ),
            operational_acts=_ids(document.get("operational_acts"), name="operational_acts"),
            rules=rules,
            claimed_operators=frozenset(
                str(o) for o in ((rules_section.get("$operators") or {}).get("claimed") or ())
            ),
            catch_all_disposition=str(_require(rules_section, "catch_all_disposition")),
            claim_scan=_require(document["principle"], "$claim_scan"),
            unknown_classes=_ids(unknown_section.get("seed"), name="unknown_classes.seed"),
            contradiction_classes=_ids(
                contradiction_section.get("seed"), name="contradiction_classes.seed"
            ),
            resolution_states=_ids(
                contradiction_section.get("resolution_states"),
                name="contradiction_classes.resolution_states",
            ),
            contradicting_states=frozenset(
                str(row["id"])
                for row in _rows(
                    contradiction_section.get("resolution_states"),
                    section="contradiction_classes.resolution_states",
                )
                if bool(row.get("contradicting", False))
            ),
            research_states=_ids(document.get("research_states"), name="research_states"),
            priority_scale=_ids(discovery_section.get("priority_scale"), name="priority_scale"),
            impact_scale=_ids(discovery_section.get("impact_scale"), name="impact_scale"),
            discovery_sources=tuple(
                DiscoverySource(
                    source_id=str(row["source_id"]),
                    selector=str(row["selector"]),
                    arguments={
                        str(k): v
                        for k, v in row.items()
                        if k
                        not in {
                            "source_id",
                            "selector",
                            "priority",
                            "impact",
                            "opportunity",
                            "definition",
                        }
                    },
                    priority=str(row["priority"]),
                    impact=str(row["impact"]),
                    opportunity=str(row["opportunity"]),
                    definition=str(row.get("definition") or ""),
                )
                for row in _rows(discovery_section.get("sources"), section="discovery.sources")
            ),
            claimed_selectors=frozenset(
                str(s) for s in ((discovery_section.get("$selectors") or {}).get("claimed") or ())
            ),
            research_key_prefix=str(
                _require(discovery_section, "derived_key_prefixes")["research"]
            ),
            discovery_key_prefix=str(
                _require(discovery_section, "derived_key_prefixes")["discovery"]
            ),
            extension_points=tuple(
                ExtensionPoint(
                    point_id=str(row["point_id"]),
                    subject=str(row["subject"]),
                    kind=str(row["kind"]),
                    owner=str(row["owner"]),
                    admission=str(row["admission"]),
                    exercised_by=str(row["exercised_by"]),
                )
                for row in _rows(
                    (document.get("extension_points") or {}).get("points"),
                    section="extension_points.points",
                )
            ),
            probe_key_prefix=str(
                _require(document.get("extension_points") or {}, "probe_key_prefix")
            ),
            claimed_admissions=frozenset(
                str(a)
                for a in (
                    ((document.get("extension_points") or {}).get("$admissions") or {}).get(
                        "claimed"
                    )
                    or ()
                )
            ),
            audit=audit,
            laws=tuple(
                Law(
                    law_id=str(row["law_id"]),
                    statement=str(row["statement"]),
                    check=str(row["check"]),
                    blocking=bool(row.get("blocking", True)),
                )
                for row in _rows(document.get("laws"), section="laws")
            ),
            self_application=_require(document, "self_application"),
            evidence_home=str(_require(document, "evidence").get("home") or ""),
            evidence_records=_rows(
                (document.get("evidence") or {}).get("records"), section="evidence.records"
            ),
            gate=_require(document, "gate"),
            source=source,
        )
    except DeclarationError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise DeclarationError(f"the declaration is malformed: {exc}") from exc


def load_declaration(path: str | None = None, *, repository: str | None = None) -> Declaration:
    """Read and rehydrate the declaration. Absence and malformation are both FAULTs."""
    root = repository or repo_root()
    target = path or os.path.join(root, DECLARATION_PATH)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError as exc:
        raise DeclarationError(f"the declaration is absent: {target}") from exc
    except (json.JSONDecodeError, IsADirectoryError, OSError) as exc:
        raise DeclarationError(f"the declaration cannot be read: {target}: {exc}") from exc
    return parse(document, source=target)


__all__ = [
    "CATCH_ALL_KEY",
    "DECLARATION_PATH",
    "AuditSpec",
    "Clause",
    "ClosureForm",
    "Declaration",
    "DeclarationError",
    "Disclosure",
    "DiscoverySource",
    "DispositionSpec",
    "ExtensionPoint",
    "Facet",
    "KindSpec",
    "Law",
    "RealitySpec",
    "Rule",
    "load_declaration",
    "parse",
    "repo_root",
]

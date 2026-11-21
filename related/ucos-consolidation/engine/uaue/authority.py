"""UAUE — canonical authority rehydration (UAUE-000001, Epoch 2B).

:func:`load_evolution_authority` is the single entry point by which the UAUE engine learns
what it is. Everything the engine needs — the classification rules, the registers, the
phases, the dependency edges, the ownership map and the lifecycle states — is reconstructed
here from repository truth on every call. Nothing is cached across calls, and nothing is
enumerated in Python.

Three properties are structural rather than reviewed:

*No hard-coded register list.* The registers come from the declaration's ``registers`` block.
This module names no register file, and the only thing it knows about register *files* is the
shape of their names (:data:`~engine.uaue.resolution.REGISTER_FILE`), which is what lets it
refuse a duplicated or skipped ordinal.

*No duplicated declarations.* The stage set is imported from :mod:`engine.uckp.evolution`, the
Article 14 authority that owns it. Every canonical stage must be claimed by exactly one phase;
a stage appended there under Article 17 makes this loader refuse until a phase claims it,
which is how an open-world cycle stays governed instead of quietly growing an unowned stage.

*No manual synchronisation.* There is no generated file to regenerate and no cache to
invalidate. Adding a register to the declaration changes what the authority contains on the
next call; deleting an owner home changes a phase's classification on the next call.
"""

from __future__ import annotations

from collections.abc import Mapping

from engine.uaue.model import (
    PRESENT,
    Boundary,
    Classification,
    Criterion,
    Dependency,
    DiscoveryDuty,
    DiscoverySource,
    EvolutionAuthority,
    EvolutionAuthorityError,
    ExitCriterion,
    Gate,
    HistorySpec,
    IdentityRule,
    Invariant,
    LifecycleState,
    ObjectKind,
    Owner,
    Ownership,
    Phase,
    PlanContract,
    Register,
    RequiredField,
    SelfEvolution,
    SourceCondition,
    UnknownProbe,
)
from engine.uaue.resolution import (
    OWN_PREFIX,
    REGISTER_FILE,
    DeclarationReader,
    Substrate,
    declared_entries,
    declared_flag,
    declared_integer,
    declared_strings,
    declared_text,
)
from engine.uckp.evolution import EVOLUTION_CYCLE, is_terminal, next_stage

#: The ``include_when`` operators this engine implements. A source declared under any other
#: operator is refused rather than silently included: an unimplemented filter would turn a
#: conditional source into an unconditional one, which is the opposite of what it declares.
SUPPORTED_OPS: frozenset[str] = frozenset({"gt", "lt", "ge", "le", "eq", "ne"})

#: The source forms this engine can read. Declared here because they are *code paths*, not
#: declarations: adding a form means writing a reader for it, so an undeclared form must fail
#: closed rather than yield zero candidates from a source that declares many.
SUPPORTED_FORMS: frozenset[str] = frozenset(
    {
        "list_of_objects",
        "list_of_strings",
        "mapping_of_objects",
        "symbol_obligation",
        "unknown_probe",
    }
)

#: The classification identifiers this loader must be able to reach, and the rule each one is
#: recognised by. This is **not** a second declaration of the classifications: the meanings,
#: ranks and rules are read from the declaration, and this mapping only asserts that the
#: declaration still defines the five outcomes the classifier can produce, under the rules it
#: implements. A declaration that renamed a rule would make the classifier unable to justify
#: its own verdict, so it must refuse rather than classify under a rule nobody declared.
REQUIRED_RULES: Mapping[str, str] = {
    "IMPLEMENTED": "every_declared_home_resolves_with_its_symbols_and_the_gate_is_wired",
    "PARTIALLY_IMPLEMENTED": "at_least_one_declared_home_resolves",
    "MISSING": "no_declared_home_resolves",
    "DUPLICATE": "another_phase_declares_an_identical_home_set",
    "FUTURE_EVOLUTION": "no_home_is_declared",
}


def _load_classifications(reader: DeclarationReader) -> tuple[Classification, ...]:
    classifications: list[Classification] = []
    seen: set[str] = set()
    for entry in reader.entries("classifications"):
        identifier = declared_text(entry, "id", what="a classification")
        if identifier in seen:
            raise EvolutionAuthorityError(
                "the declaration defines the same classification twice",
                classification=identifier,
            )
        seen.add(identifier)
        classifications.append(
            Classification(
                identifier=identifier,
                rule=declared_text(entry, "rule", what=f"classification {identifier}"),
                meaning=declared_text(entry, "meaning", what=f"classification {identifier}"),
                rank=declared_integer(entry, "rank", what=f"classification {identifier}"),
            )
        )
    declared = {entry.identifier: entry.rule for entry in classifications}
    for identifier, rule in REQUIRED_RULES.items():
        if identifier not in declared:
            raise EvolutionAuthorityError(
                "the declaration defines no classification the classifier can produce",
                classification=identifier,
            )
        if declared[identifier] != rule:
            raise EvolutionAuthorityError(
                "a classification is declared under a rule this loader does not implement",
                classification=identifier,
                declared=declared[identifier],
                implemented=rule,
            )
    ranks = [entry.rank for entry in classifications]
    if len(set(ranks)) != len(ranks):
        raise EvolutionAuthorityError(
            "two classifications share a rank, so severity would not be orderable",
            ranks=sorted(ranks),
        )
    return tuple(classifications)


def _load_object_kinds(reader: DeclarationReader) -> tuple[ObjectKind, ...]:
    kinds: list[ObjectKind] = []
    seen: set[str] = set()
    for entry in reader.entries("object_kinds"):
        identifier = declared_text(entry, "id", what="an object kind")
        if identifier in seen:
            raise EvolutionAuthorityError(
                "the declaration defines the same object kind twice", object_kind=identifier
            )
        seen.add(identifier)
        kinds.append(
            ObjectKind(
                identifier=identifier,
                name=declared_text(entry, "name", what=f"object kind {identifier}"),
                phase=declared_text(entry, "phase", what=f"object kind {identifier}"),
                mandated=declared_flag(entry, "mandated", what=f"object kind {identifier}"),
                purpose=declared_text(
                    entry, "purpose", what=f"object kind {identifier}", required=False
                ),
            )
        )
    return tuple(kinds)


def _load_required_fields(reader: DeclarationReader) -> tuple[RequiredField, ...]:
    fields: list[RequiredField] = []
    seen: set[str] = set()
    for entry in reader.entries("required_fields"):
        identifier = declared_text(entry, "id", what="a required field")
        field_name = declared_text(entry, "field", what=f"required field {identifier}")
        if field_name in seen:
            raise EvolutionAuthorityError(
                "the declaration mandates the same field twice", field=field_name
            )
        seen.add(field_name)
        fields.append(
            RequiredField(
                identifier=identifier,
                field_name=field_name,
                name=declared_text(entry, "name", what=f"required field {identifier}"),
                non_empty=declared_flag(entry, "non_empty", what=f"required field {identifier}"),
                derivation=declared_text(
                    entry, "derivation", what=f"required field {identifier}", required=False
                ),
            )
        )
    return tuple(fields)


def _load_registers(reader: DeclarationReader, phase_ids: frozenset[str]) -> tuple[Register, ...]:
    """The declared registers, with ownership resolved and the ordinal set proved complete.

    Two failures are refused here rather than reported, because both would make every later
    measurement unattributable. A register declared twice would give one file two renderers,
    and a gap in the ordinal set means a register the declaration intends was never written —
    the "duplicate register" and "missing register" detections Epoch 2B requires.
    """
    registers: list[Register] = []
    by_file: dict[str, int] = {}
    by_ordinal: dict[int, str] = {}
    for index, entry in enumerate(reader.entries("registers")):
        file = declared_text(entry, "file", what="a register")
        match = REGISTER_FILE.match(file)
        if match is None:
            raise EvolutionAuthorityError(
                "a register filename is not in canonical NN-NAME.md form", register=file
            )
        ordinal = int(match.group(1))
        if file in by_file:
            raise EvolutionAuthorityError(
                "the declaration declares the same register twice",
                register=file,
                first_index=by_file[file],
                second_index=index,
            )
        if ordinal in by_ordinal:
            raise EvolutionAuthorityError(
                "two registers claim the same ordinal, so one would overwrite the other",
                ordinal=ordinal,
                first=by_ordinal[ordinal],
                second=file,
            )
        if ordinal != index:
            raise EvolutionAuthorityError(
                "a register's ordinal does not match its position, so a register is missing",
                register=file,
                declared_ordinal=ordinal,
                position=index,
            )
        by_file[file] = index
        by_ordinal[ordinal] = file
        owner_phase = declared_text(entry, "phase", what=f"register {file}", required=False)
        if owner_phase and owner_phase not in phase_ids:
            raise EvolutionAuthorityError(
                "a register is owned by a phase the declaration does not declare",
                register=file,
                phase=owner_phase,
            )
        registers.append(
            Register(
                ordinal=ordinal,
                file=file,
                renderer=declared_text(entry, "renderer", what=f"register {file}"),
                title=declared_text(entry, "title", what=f"register {file}"),
                purpose=declared_text(entry, "purpose", what=f"register {file}", required=False),
                owner_phase=owner_phase,
            )
        )
    expected = set(range(len(registers)))
    if set(by_ordinal) != expected:
        raise EvolutionAuthorityError(
            "the register ordinal set is not contiguous from zero",
            missing=sorted(expected - set(by_ordinal)),
            unexpected=sorted(set(by_ordinal) - expected),
        )
    return tuple(registers)


def _load_phase_owners(
    entry: Mapping[str, object], identifier: str, substrate: Substrate
) -> tuple[Owner, ...]:
    """One phase's owners, with home resolution and symbol binding measured.

    Symbols are checked against the union of names bound across the phase's *resolving* homes,
    so a symbol that moved between two homes of the same phase is still bound, while a symbol
    that exists nowhere is missing from every home that declared it — which is what makes the
    shortfall attributable to a declaration rather than to a file.
    """
    declared = entry.get("owners", [])
    if not isinstance(declared, list):
        raise EvolutionAuthorityError(
            f"phase {identifier} declares 'owners' as {type(declared).__name__}, not a list"
        )
    homes: list[str] = []
    symbol_sets: list[tuple[str, ...]] = []
    for owner in declared:
        if not isinstance(owner, Mapping):
            raise EvolutionAuthorityError(
                f"every owner of phase {identifier} must be a JSON object",
                received=type(owner).__name__,
            )
        home = declared_text(owner, "home", what=f"an owner of phase {identifier}")
        if home.startswith(OWN_PREFIX):
            raise EvolutionAuthorityError(
                "a phase declares an owner home inside this programme's own home, "
                "which would make the register its own authority",
                phase=identifier,
                home=home,
            )
        if home in homes:
            raise EvolutionAuthorityError(
                "a phase declares the same owner home twice", phase=identifier, home=home
            )
        homes.append(home)
        symbol_sets.append(
            declared_strings(owner, "symbols", what=f"owner {home} of phase {identifier}")
        )
    resolving = [home for home in homes if substrate.resolves(home)]
    bound = substrate.bound_across(resolving)
    return tuple(
        Owner(
            home=home,
            symbols=symbols,
            state=substrate.state(home),
            missing_symbols=tuple(symbol for symbol in symbols if symbol not in bound),
        )
        for home, symbols in zip(homes, symbol_sets, strict=True)
    )


def _classify(phase_homes: Mapping[str, frozenset[str]], identifier: str, phase: Phase) -> str:
    """The classification of one phase under the declaration's five rules, in rule order.

    Order matters and is the declaration's own precedence. A phase with no declared home is a
    disclosed absence before it is anything else (FUTURE_EVOLUTION); a phase whose home set is
    another phase's home set is two authorities over one home (DUPLICATE) regardless of whether
    those homes resolve; only then do resolution and symbol binding decide between MISSING,
    PARTIALLY_IMPLEMENTED and IMPLEMENTED.
    """
    if not phase.owners:
        return "FUTURE_EVOLUTION"
    mine = phase_homes[identifier]
    for other, homes in phase_homes.items():
        if other != identifier and homes and homes == mine:
            return "DUPLICATE"
    resolving = phase.resolving_homes
    if not resolving:
        return "MISSING"
    if len(resolving) == len(phase.owners) and not phase.missing_symbols and phase.gate.wired:
        return "IMPLEMENTED"
    return "PARTIALLY_IMPLEMENTED"


def _load_phases(reader: DeclarationReader, substrate: Substrate) -> tuple[Phase, ...]:
    raw = reader.entries("phases")
    staged: list[tuple[str, Mapping[str, object], tuple[Owner, ...], Gate, int]] = []
    seen: set[str] = set()
    for index, entry in enumerate(raw):
        identifier = declared_text(entry, "id", what="a phase")
        if identifier in seen:
            raise EvolutionAuthorityError(
                "the declaration declares the same phase twice", phase=identifier
            )
        seen.add(identifier)
        ordinal = declared_integer(entry, "ordinal", what=f"phase {identifier}")
        if ordinal != index + 1:
            raise EvolutionAuthorityError(
                "a phase's ordinal does not match its position, so the loop order is ambiguous",
                phase=identifier,
                declared_ordinal=ordinal,
                position=index + 1,
            )
        owners = _load_phase_owners(entry, identifier, substrate)
        command = declared_text(entry, "gate", what=f"phase {identifier}", required=False)
        wired, detail = substrate.gate_state(command)
        staged.append((identifier, entry, owners, Gate(command, wired, detail), ordinal))

    phase_homes = {
        identifier: frozenset(owner.home for owner in owners)
        for identifier, _, owners, _, _ in staged
    }
    phases: list[Phase] = []
    for identifier, entry, owners, gate, ordinal in staged:
        declared_evidence = declared_strings(entry, "evidence", what=f"phase {identifier}")
        provisional = Phase(
            identifier=identifier,
            ordinal=ordinal,
            name=declared_text(entry, "name", what=f"phase {identifier}"),
            duty=declared_text(entry, "duty", what=f"phase {identifier}"),
            canonical_stages=declared_strings(
                entry, "canonical_stages", what=f"phase {identifier}"
            ),
            produces=declared_text(entry, "produces", what=f"phase {identifier}"),
            owners=owners,
            gate=gate,
            declared_evidence=declared_evidence,
            resolving_evidence=tuple(
                path for path in declared_evidence if substrate.resolves(path)
            ),
            authority=declared_text(entry, "authority", what=f"phase {identifier}", required=False),
            reuse=declared_text(entry, "reuse", what=f"phase {identifier}", required=False),
            classification="",
        )
        classification = _classify(phase_homes, identifier, provisional)
        phases.append(
            Phase(
                identifier=provisional.identifier,
                ordinal=provisional.ordinal,
                name=provisional.name,
                duty=provisional.duty,
                canonical_stages=provisional.canonical_stages,
                produces=provisional.produces,
                owners=provisional.owners,
                gate=provisional.gate,
                declared_evidence=provisional.declared_evidence,
                resolving_evidence=provisional.resolving_evidence,
                authority=provisional.authority,
                reuse=provisional.reuse,
                classification=classification,
            )
        )
    return tuple(phases)


def _load_lifecycle_states(phases: tuple[Phase, ...]) -> tuple[LifecycleState, ...]:
    """The canonical stage set, with the phase that claims each stage.

    The stages are :data:`engine.uckp.evolution.EVOLUTION_CYCLE` and are never declared here.
    Both failure directions are refused: a stage no phase claims would be an unowned stage of a
    governed cycle, and a stage two phases claim would be two authorities over one stage.
    """
    canonical = tuple(stage.value for stage in EVOLUTION_CYCLE)
    known = set(canonical)
    claims: dict[str, list[str]] = {stage: [] for stage in canonical}
    for phase in phases:
        for stage in phase.canonical_stages:
            if stage not in known:
                raise EvolutionAuthorityError(
                    "a phase claims a stage the canonical stage authority does not declare",
                    phase=phase.identifier,
                    stage=stage,
                    authority="engine/uckp/evolution.py",
                )
            claims[stage].append(phase.identifier)
    unclaimed = sorted(stage for stage, owners in claims.items() if not owners)
    if unclaimed:
        raise EvolutionAuthorityError(
            "a canonical evolution stage is claimed by no phase",
            stages=unclaimed,
            authority="engine/uckp/evolution.py",
        )
    contested = sorted(stage for stage, owners in claims.items() if len(owners) > 1)
    if contested:
        raise EvolutionAuthorityError(
            "a canonical evolution stage is claimed by more than one phase",
            stages=contested,
        )
    return tuple(
        LifecycleState(
            name=stage,
            ordinal=index,
            successor=next_stage(stage).value,
            terminal=is_terminal(stage),
            claimed_by=tuple(claims[stage]),
        )
        for index, stage in enumerate(canonical)
    )


def _load_dependencies(phases: tuple[Phase, ...]) -> tuple[Dependency, ...]:
    """The dependency edges the plan contract derives: the preceding phase, and owner homes.

    Phase edges are emitted in loop order and always point at a lower ordinal, so the
    dependency-integrity verification has something to measure rather than to assume. The
    first phase has no phase edge — a backward edge from it would make the loop's entry depend
    on its own successor.
    """
    dependencies: list[Dependency] = []
    for index, phase in enumerate(phases):
        if index > 0:
            dependencies.append(
                Dependency(
                    phase=phase.identifier, depends_on=phases[index - 1].identifier, kind="phase"
                )
            )
        for home in phase.homes:
            dependencies.append(Dependency(phase=phase.identifier, depends_on=home, kind="home"))
    return tuple(dependencies)


def _load_ownership(phases: tuple[Phase, ...], substrate: Substrate) -> tuple[Ownership, ...]:
    """Every declared owner home and the phases that bind it, sorted by home.

    Sorted rather than in declaration order because this is a map, not a sequence: a stable
    key order is what makes the authority digest independent of which phase mentioned a shared
    home first.
    """
    owners: dict[str, list[str]] = {}
    for phase in phases:
        for home in phase.homes:
            owners.setdefault(home, []).append(phase.identifier)
    return tuple(
        Ownership(home=home, phases=tuple(owners[home]), state=substrate.state(home))
        for home in sorted(owners)
    )


def _load_identity(reader: DeclarationReader) -> IdentityRule:
    entry = reader.block("identity")
    width = declared_integer(entry, "width", what="the identity block")
    if width <= 0:
        raise EvolutionAuthorityError("the identity width must be positive", width=width)
    inputs = declared_strings(entry, "inputs", what="the identity block")
    if not inputs:
        raise EvolutionAuthorityError(
            "the identity rule declares no inputs, so every object would share one identity"
        )
    if len(set(inputs)) != len(inputs):
        raise EvolutionAuthorityError(
            "the identity rule declares the same input twice", inputs=list(inputs)
        )
    return IdentityRule(
        prefix=declared_text(entry, "prefix", what="the identity block"),
        width=width,
        inputs=inputs,
        derivation_home=declared_text(entry, "derivation_home", what="the identity block"),
        derivation_symbol=declared_text(entry, "derivation_symbol", what="the identity block"),
        digest_home=declared_text(entry, "digest_home", what="the identity block"),
        digest_symbol=declared_text(entry, "digest_symbol", what="the identity block"),
        anonymity_rule=declared_text(entry, "anonymity_rule", what="the identity block"),
    )


def _load_conditions(entry: Mapping[str, object], identifier: str) -> tuple[SourceCondition, ...]:
    declared = entry.get("include_when", [])
    if not isinstance(declared, list):
        raise EvolutionAuthorityError(
            f"source {identifier} declares 'include_when' as {type(declared).__name__}"
        )
    conditions: list[SourceCondition] = []
    for condition in declared:
        if not isinstance(condition, Mapping):
            raise EvolutionAuthorityError(
                f"every include_when of source {identifier} must be a JSON object"
            )
        op = declared_text(condition, "op", what=f"an include_when of source {identifier}")
        if op not in SUPPORTED_OPS:
            raise EvolutionAuthorityError(
                "an include_when declares an operator this engine does not implement",
                source=identifier,
                op=op,
                implemented=sorted(SUPPORTED_OPS),
            )
        conditions.append(
            SourceCondition(
                field_name=declared_text(
                    condition, "field", what=f"an include_when of source {identifier}"
                ),
                op=op,
                value=condition.get("value"),
            )
        )
    return tuple(conditions)


def _load_discovery_sources(reader: DeclarationReader) -> tuple[DiscoverySource, ...]:
    sources: list[DiscoverySource] = []
    seen: set[str] = set()
    for entry in reader.entries("discovery_sources"):
        identifier = declared_text(entry, "id", what="a discovery source")
        if identifier in seen:
            raise EvolutionAuthorityError(
                "the declaration declares the same discovery source twice", source=identifier
            )
        seen.add(identifier)
        form = declared_text(entry, "form", what=f"source {identifier}")
        if form not in SUPPORTED_FORMS:
            raise EvolutionAuthorityError(
                "a discovery source declares a form this engine cannot read",
                source=identifier,
                form=form,
                implemented=sorted(SUPPORTED_FORMS),
            )
        selector = declared_strings(entry, "selector", what=f"source {identifier}")
        if not selector:
            raise EvolutionAuthorityError(
                "a discovery source declares no selector, so nothing could be read from it",
                source=identifier,
            )
        fields = entry.get("fields", {})
        if not isinstance(fields, Mapping):
            raise EvolutionAuthorityError(
                f"source {identifier} declares 'fields' as {type(fields).__name__}"
            )
        path = entry.get("path")
        if path is not None and not isinstance(path, str):
            raise EvolutionAuthorityError(
                f"source {identifier} declares 'path' as {type(path).__name__}"
            )
        sources.append(
            DiscoverySource(
                identifier=identifier,
                name=declared_text(entry, "name", what=f"source {identifier}"),
                owner=declared_text(entry, "owner", what=f"source {identifier}"),
                path=path or "",
                selector=selector,
                form=form,
                candidate_class=declared_text(
                    entry, "candidate_class", what=f"source {identifier}"
                ),
                fields=tuple(sorted((str(k), str(v)) for k, v in fields.items())),
                reason_template=declared_text(
                    entry, "reason_template", what=f"source {identifier}"
                ),
                target_template=declared_text(
                    entry, "target_template", what=f"source {identifier}"
                ),
                include_when=_load_conditions(entry, identifier),
            )
        )
    return tuple(sources)


def _load_discovery_duties(
    reader: DeclarationReader, source_ids: frozenset[str]
) -> tuple[DiscoveryDuty, ...]:
    duties: list[DiscoveryDuty] = []
    for entry in reader.entries("discovery_duties"):
        identifier = declared_text(entry, "id", what="a discovery duty")
        satisfied_by = declared_strings(entry, "satisfied_by", what=f"duty {identifier}")
        if not satisfied_by:
            raise EvolutionAuthorityError(
                "a discovery duty names no source that could satisfy it", duty=identifier
            )
        for source in satisfied_by:
            if source not in source_ids:
                raise EvolutionAuthorityError(
                    "a discovery duty names a source the declaration does not declare",
                    duty=identifier,
                    source=source,
                )
        duties.append(
            DiscoveryDuty(
                identifier=identifier,
                duty=declared_text(entry, "duty", what=f"duty {identifier}"),
                satisfied_by=satisfied_by,
            )
        )
    return tuple(duties)


def _load_criteria(
    reader: DeclarationReader, block: str, subject_key: str, *, gated: bool
) -> tuple[Criterion, ...]:
    """One criterion block. ``subject_key`` is 'dimension' or 'proof', as declared."""
    criteria: list[Criterion] = []
    seen: set[str] = set()
    for entry in reader.entries(block):
        identifier = declared_text(entry, "id", what=f"a '{block}' entry")
        if identifier in seen:
            raise EvolutionAuthorityError(
                f"the '{block}' block declares the same criterion twice", criterion=identifier
            )
        seen.add(identifier)
        criteria.append(
            Criterion(
                identifier=identifier,
                subject=declared_text(entry, subject_key, what=f"{block} {identifier}"),
                obligation=declared_text(entry, "obligation", what=f"{block} {identifier}"),
                blocking=declared_flag(entry, "blocking", what=f"{block} {identifier}"),
                bound_gate=(
                    declared_text(entry, "bound_gate", what=f"{block} {identifier}")
                    if gated
                    else ""
                ),
            )
        )
    if not criteria:
        raise EvolutionAuthorityError(f"the '{block}' block declares no criterion")
    return tuple(criteria)


def _load_mandatory(reader: DeclarationReader) -> tuple[Invariant, ...]:
    invariants: list[Invariant] = []
    seen: set[str] = set()
    for entry in reader.entries("mandatory"):
        identifier = declared_text(entry, "id", what="a mandatory invariant")
        measure = declared_text(entry, "measure", what=f"invariant {identifier}")
        if measure in seen:
            raise EvolutionAuthorityError(
                "two invariants share a measure name, so one would overwrite the other",
                measure=measure,
            )
        seen.add(measure)
        invariants.append(
            Invariant(
                identifier=identifier,
                invariant=declared_text(entry, "invariant", what=f"invariant {identifier}"),
                measure=measure,
                expect=declared_integer(entry, "expect", what=f"invariant {identifier}"),
                blocking=declared_flag(entry, "blocking", what=f"invariant {identifier}"),
            )
        )
    return tuple(invariants)


def _load_history(reader: DeclarationReader, substrate: Substrate) -> HistorySpec:
    entry = reader.block("history")
    projection = entry.get("projection_of")
    if not isinstance(projection, Mapping):
        raise EvolutionAuthorityError(
            "the history block declares no 'projection_of', so its append rules have no owner"
        )
    home = declared_text(projection, "home", what="the history projection")
    if not substrate.resolves(home):
        raise EvolutionAuthorityError(
            "the history's projection owner does not resolve, "
            "so the append-only claim could not be re-verified on read",
            home=home,
        )
    bound = substrate.symbols(home)
    for key in ("ledger_symbol", "document_symbol", "rehydration_symbol"):
        symbol = declared_text(projection, key, what="the history projection")
        if symbol not in bound:
            raise EvolutionAuthorityError(
                "the history's projection owner does not bind a symbol it is read through",
                home=home,
                symbol=symbol,
                declared_as=key,
            )
    dimensions = tuple(
        declared_text(record, "dimension", what="a history record")
        for record in declared_entries(entry.get("records", []), what="the history records")
    )
    if not dimensions:
        raise EvolutionAuthorityError("the history block declares no recorded dimension")
    return HistorySpec(
        file=declared_text(entry, "file", what="the history block"),
        schema=declared_text(entry, "schema", what="the history block"),
        version=declared_text(entry, "version", what="the history block"),
        append_only=declared_flag(entry, "append_only", what="the history block"),
        ledger_home=home,
        ledger_symbol=declared_text(projection, "ledger_symbol", what="the history projection"),
        document_symbol=declared_text(projection, "document_symbol", what="the history projection"),
        rehydration_symbol=declared_text(
            projection, "rehydration_symbol", what="the history projection"
        ),
        dimensions=dimensions,
        queryable_by=declared_strings(entry, "queryable_by", what="the history block"),
    )


def _load_plan_contract(reader: DeclarationReader) -> PlanContract:
    entry = reader.block("plan_contract")
    what = "the plan contract"
    return PlanContract(
        identifier=declared_text(entry, "id", what=what),
        objectives_from=declared_text(entry, "objectives_from", what=what),
        steps_from=declared_text(entry, "steps_from", what=what),
        dependencies_from=declared_text(entry, "dependencies_from", what=what),
        risk_from=declared_text(entry, "risk_from", what=what),
        validation_criteria_from=declared_text(entry, "validation_criteria_from", what=what),
        verification_criteria_from=declared_text(entry, "verification_criteria_from", what=what),
        certification_criteria_from=declared_text(entry, "certification_criteria_from", what=what),
        rollback_strategy=declared_text(entry, "rollback_strategy", what=what),
    )


def _load_unknown_probe(reader: DeclarationReader) -> UnknownProbe:
    entry = reader.block("unknown_probe")
    what = "the unknown probe"
    must_not_require = declared_strings(entry, "must_not_require", what=what)
    if not must_not_require:
        raise EvolutionAuthorityError(
            "the unknown probe forbids nothing, so it would prove nothing about the engine"
        )
    return UnknownProbe(
        identifier=declared_text(entry, "id", what=what),
        subject=declared_text(entry, "subject", what=what),
        subject_class=declared_text(entry, "subject_class", what=what),
        unknown_stage_term=declared_text(entry, "unknown_stage_term", what=what),
        must_not_require=must_not_require,
    )


def _load_boundaries(reader: DeclarationReader, substrate: Substrate) -> tuple[Boundary, ...]:
    """The declared non-duplication boundaries, with the other owner's existence measured.

    A boundary is the register's answer to "why is this not a duplicate of that". Measuring
    whether the other owner still resolves is what stops the answer from outliving the thing it
    was drawn against: a boundary against a home that has been deleted is unverifiable, and an
    unverifiable boundary must be reported rather than counted as satisfied.
    """
    boundaries: list[Boundary] = []
    seen: set[str] = set()
    for entry in reader.entries("boundaries"):
        identifier = declared_text(entry, "id", what="a boundary")
        if identifier in seen:
            raise EvolutionAuthorityError(
                "the 'boundaries' block declares the same boundary twice", boundary=identifier
            )
        seen.add(identifier)
        other_owner = declared_text(entry, "other_owner", what=f"boundary {identifier}")
        boundaries.append(
            Boundary(
                identifier=identifier,
                other_owner=other_owner,
                other_subject=declared_text(entry, "other_subject", what=f"boundary {identifier}"),
                this_subject=declared_text(entry, "this_subject", what=f"boundary {identifier}"),
                why_not_duplicate=declared_text(
                    entry, "why_not_duplicate", what=f"boundary {identifier}"
                ),
                other_owner_state=substrate.state(other_owner),
            )
        )
    if not boundaries:
        raise EvolutionAuthorityError(
            "the declaration draws no non-duplication boundary, "
            "so reuse-before-create is unanswered"
        )
    return tuple(boundaries)


def _load_exit_criteria(reader: DeclarationReader) -> tuple[ExitCriterion, ...]:
    """The declared exit criteria of the programme's implementation phases."""
    criteria: list[ExitCriterion] = []
    seen: set[str] = set()
    for entry in reader.entries("exit_criteria"):
        identifier = declared_text(entry, "id", what="an exit criterion")
        if identifier in seen:
            raise EvolutionAuthorityError(
                "the 'exit_criteria' block declares the same criterion twice",
                criterion=identifier,
            )
        seen.add(identifier)
        criteria.append(
            ExitCriterion(
                identifier=identifier,
                phase=declared_text(entry, "phase", what=f"exit criterion {identifier}"),
                criterion=declared_text(entry, "criterion", what=f"exit criterion {identifier}"),
                measure=declared_text(entry, "measure", what=f"exit criterion {identifier}"),
                expect=declared_integer(entry, "expect", what=f"exit criterion {identifier}"),
            )
        )
    if not criteria:
        raise EvolutionAuthorityError("the declaration declares no exit criterion")
    return tuple(criteria)


def _load_self_evolution(
    reader: DeclarationReader, substrate: Substrate, source_ids: frozenset[str]
) -> SelfEvolution:
    """The programme's own self-evolution subject, with its closure re-measured.

    The closure is never read from the declaration. ``missing_symbols`` is computed against the
    names actually bound in the declared home and ``unresolved_evidence`` against the paths that
    actually resolve, so removing the surface reopens the gap on the next run instead of leaving
    a declaration that still claims it closed.
    """
    entry = reader.block("self_evolution")
    what = "the self-evolution block"
    identifier = declared_text(entry, "id", what=what)
    detected_by = declared_text(entry, "detected_by", what=what)
    if detected_by not in source_ids:
        raise EvolutionAuthorityError(
            "the self-evolution subject was detected by a source the declaration does not declare",
            self_evolution=identifier,
            detected_by=detected_by,
        )
    home = declared_text(entry, "home", what=what)
    required_symbols = declared_strings(entry, "required_symbols", what=what)
    if not required_symbols:
        raise EvolutionAuthorityError(
            "the self-evolution subject requires no symbol, so its closure is unmeasurable",
            self_evolution=identifier,
        )
    evidence = declared_strings(entry, "evidence", what=what)
    if not evidence:
        raise EvolutionAuthorityError(
            "the self-evolution subject cites no evidence", self_evolution=identifier
        )
    home_state = substrate.state(home)
    bound = substrate.symbols(home) if home_state == PRESENT else frozenset()
    return SelfEvolution(
        identifier=identifier,
        subject_identity=declared_text(entry, "subject_identity", what=what),
        detected_by=detected_by,
        gap=declared_text(entry, "gap", what=what),
        previous_state=declared_text(entry, "previous_state", what=what),
        target_state=declared_text(entry, "target_state", what=what),
        required_symbols=required_symbols,
        home=home,
        authority=declared_text(entry, "authority", what=what),
        executed_through=declared_text(entry, "executed_through", what=what),
        evidence=evidence,
        home_state=home_state,
        missing_symbols=tuple(symbol for symbol in required_symbols if symbol not in bound),
        unresolved_evidence=tuple(path for path in evidence if substrate.state(path) != PRESENT),
    )


def load_evolution_authority(
    reader: DeclarationReader | None = None, substrate: Substrate | None = None
) -> EvolutionAuthority:
    """Reconstruct the UAUE authority from repository truth.

    Args:
        reader: the declaration to load. Defaults to the canonical declaration at
            ``00-MASTER/UAUE-000001/uaue-evolution.json``.
        substrate: the repository tree to measure declared homes, evidence and gates against.
            Defaults to the tree this module is installed in.

    Returns:
        A frozen :class:`~engine.uaue.model.EvolutionAuthority`. Two calls over the same
        declaration and the same tree return equal models with an equal
        :meth:`~engine.uaue.model.EvolutionAuthority.digest`.

    Raises:
        EvolutionAuthorityError: the declaration is absent, unreadable, structurally invalid,
            internally inconsistent, or inconsistent with the canonical stage authority. The
            loader fails closed: it never returns a partially resolved authority, because a
            consumer cannot tell a partial authority from a complete one.
    """
    reader = reader if reader is not None else DeclarationReader.canonical()
    substrate = substrate if substrate is not None else Substrate()

    programme = reader.block("programme")
    programme_id = declared_text(programme, "id", what="the programme block")
    version = declared_text(programme, "version", what="the programme block")

    stage_authority = reader.block("stage_authority")
    stage_home = declared_text(stage_authority, "home", what="the stage authority block")
    if not substrate.resolves(stage_home):
        raise EvolutionAuthorityError(
            "the declared canonical stage authority does not resolve, "
            "so the stage set cannot be read from the owner that defines it",
            home=stage_home,
        )
    stage_bound = substrate.symbols(stage_home)
    for key in (
        "enum_symbol",
        "cycle_symbol",
        "successor_symbol",
        "terminal_symbol",
        "ledger_symbol",
        "record_symbol",
        "rehydration_symbol",
    ):
        symbol = declared_text(stage_authority, key, what="the stage authority block")
        if symbol not in stage_bound:
            raise EvolutionAuthorityError(
                "the stage authority does not bind a symbol the declaration reads it through",
                home=stage_home,
                symbol=symbol,
                declared_as=key,
            )

    classifications = _load_classifications(reader)
    phases = _load_phases(reader, substrate)
    phase_ids = frozenset(phase.identifier for phase in phases)
    registers = _load_registers(reader, phase_ids)
    object_kinds = _load_object_kinds(reader)
    required_fields = _load_required_fields(reader)
    lifecycle_states = _load_lifecycle_states(phases)

    produced: dict[str, str] = {}
    for kind in object_kinds:
        if kind.phase not in phase_ids:
            raise EvolutionAuthorityError(
                "an object kind is produced by a phase the declaration does not declare",
                object_kind=kind.identifier,
                phase=kind.phase,
            )
        if kind.phase in produced:
            raise EvolutionAuthorityError(
                "a phase produces more than one object kind",
                phase=kind.phase,
                first=produced[kind.phase],
                second=kind.identifier,
            )
        produced[kind.phase] = kind.identifier
    for phase in phases:
        if phase.produces not in {kind.identifier for kind in object_kinds}:
            raise EvolutionAuthorityError(
                "a phase produces an object kind the declaration does not declare",
                phase=phase.identifier,
                produces=phase.produces,
            )
        if produced.get(phase.identifier) != phase.produces:
            raise EvolutionAuthorityError(
                "a phase and its object kind disagree about which produces which",
                phase=phase.identifier,
                phase_produces=phase.produces,
                kind_of_phase=produced.get(phase.identifier, "<none>"),
            )

    sources = _load_discovery_sources(reader)
    source_ids = frozenset(entry.identifier for entry in sources)
    for source in sources:
        if source.candidate_class == "":
            raise EvolutionAuthorityError(
                "a discovery source declares no candidate class", source=source.identifier
            )

    return EvolutionAuthority(
        programme_id=programme_id,
        version=version,
        source=reader.source,
        stage_authority_home=stage_home,
        identity=_load_identity(reader),
        classifications=classifications,
        registers=registers,
        phases=phases,
        dependencies=_load_dependencies(phases),
        ownership=_load_ownership(phases, substrate),
        lifecycle_states=lifecycle_states,
        object_kinds=object_kinds,
        required_fields=required_fields,
        discovery_sources=sources,
        discovery_duties=_load_discovery_duties(reader, source_ids),
        validations=_load_criteria(reader, "validations", "dimension", gated=False),
        verifications=_load_criteria(reader, "verifications", "dimension", gated=True),
        certifications=_load_criteria(reader, "certifications", "proof", gated=False),
        mandatory=_load_mandatory(reader),
        history=_load_history(reader, substrate),
        plan_contract=_load_plan_contract(reader),
        unknown_probe=_load_unknown_probe(reader),
        boundaries=_load_boundaries(reader, substrate),
        exit_criteria=_load_exit_criteria(reader),
        self_evolution=_load_self_evolution(reader, substrate, source_ids),
    )


def dependencies_of(authority: EvolutionAuthority, phase: str) -> tuple[str, ...]:
    """The declared dependencies of one phase. Delegates to the authority that derives them."""
    return authority.dependencies_of(phase)


def authority_is_grounded(authority: EvolutionAuthority) -> bool:
    """True when every owner home the authority binds resolves in the measured tree.

    Not a gate and not a verdict on the programme: a phase carried as a disclosed absence is
    lawful, so this is only the question "is anything the authority points at unreachable",
    which a report quotes rather than acts on.
    """
    return all(entry.state == PRESENT for entry in authority.ownership)


__all__ = [
    "REQUIRED_RULES",
    "SUPPORTED_FORMS",
    "SUPPORTED_OPS",
    "authority_is_grounded",
    "dependencies_of",
    "load_evolution_authority",
]

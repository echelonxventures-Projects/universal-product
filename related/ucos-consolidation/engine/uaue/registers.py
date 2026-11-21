"""UAUE — the declared register surface (UAUE-000001, Epoch 6).

The declaration names eighteen registers and fourteen renderers. Until this module existed it
named them and nothing produced them: the gate measured every certification proof in memory and
then discarded it, so the programme's own certification was real, correct and unreadable. A
certification nobody can open is indistinguishable from a certification nobody performed, which is
precisely the defect class the register surface closes.

Three properties are load-bearing and each one is the negation of a way this surface could look
present while being absent:

1. **Nothing here holds a register list.** :data:`RENDERERS` maps a *renderer name* the
   declaration chooses to the function that realises it, and :func:`rendered_surface` iterates
   ``authority.registers``. Adding a nineteenth register is a declaration edit; a register list
   in this module would be the declaration kept in two places, which is the defect
   :mod:`engine.uaue.model` was written to prevent.
2. **Every rendered value is measured, never declared.** A register that restated the
   declaration's own claims would be a mirror, not evidence. Where the declaration says a gap is
   closed, the register prints the measurement of whether the symbols actually bind.
3. **No wall clock, no ambient state.** Every byte is a deterministic function of the
   declaration and the measured tree, so :func:`replay_drift` can prove a committed register is
   the product of its declaration rather than something a hand edit left behind. A register that
   embedded a timestamp would drift on every run and the proof would have to be abandoned.

The renderers write Markdown because the audience is a reviewer, and the history projection stays
canonical JSON because its audience is :meth:`engine.uckp.evolution.EvolutionLedger.from_document`.
Both are projections of the same runs; neither is a truth, and :mod:`engine.uaue.gate` owns the
measurement they both project.

**This module writes nothing.** It returns rendered bytes and the gate performs the write. The
separation is an invariant of the package rather than a preference: the repository holds this
engine to *one* writing module so that "what may this programme mutate, and where" has a single
answer, and a renderer that reached for a path of its own would make that answer a survey of
eighteen call sites. So :func:`rendered_surface` hands the gate a file-name-to-body mapping,
:func:`register_path` computes a destination without touching it, and every ``mkdir`` and
``write_text`` in the UAUE surface lives in :mod:`engine.uaue.gate`.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from engine.uaue.exits import exit_measures
from engine.uaue.model import EvolutionAuthorityError, Register
from engine.uaue.resolution import PROGRAMME_HOME
from engine.uckp.canonical import content_hash

if TYPE_CHECKING:  # pragma: no cover - import cycle guard, types only
    from engine.uaue.controller import EvolutionContext, EvolutionRun
    from engine.uaue.gate import GateReport

#: The banner every rendered register carries. It states the authority relation in the artifact
#: itself so a register read in isolation cannot be mistaken for a source of authority.
DERIVED_TRUTH = "AUTHORITY = NONE — DERIVED TRUTH"

#: Rendered by the declaration's own `history` renderer as a pointer, because the canonical bytes
#: of the history live in the JSON projection the ledger owns and must not be duplicated here.
HISTORY_IS_JSON = (
    "The canonical history is the JSON projection named by the declaration's `history` block. "
    "This register summarises it and never restates its records: a second copy of an append-only "
    "ledger is a second ledger, and the two could disagree."
)


def _cell(value: object) -> str:
    """One Markdown table cell: pipes escaped and newlines flattened.

    A declaration sentence containing a pipe would otherwise split a row and silently shift every
    later column, which turns a correct measurement into a wrong-looking table.
    """
    text = str(value).replace("|", "\\|")
    return " ".join(text.split())


def _table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> list[str]:
    """A Markdown table, or an explicit empty-set line when there are no rows.

    An empty table is rendered as a named absence rather than as a header with nothing under it:
    a reader cannot tell an empty measurement from a broken renderer, and this repository's
    convention is that an absence is always stated.
    """
    materialised = [[_cell(cell) for cell in row] for row in rows]
    if not materialised:
        return ["*(the measured set is empty)*", ""]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in materialised)
    lines.append("")
    return lines


def _mark(satisfied: bool) -> str:
    """PASS/FAIL rather than a symbol: a verdict must survive a plain-text pipe."""
    return "PASS" if satisfied else "FAIL"


def _heading(register: Register, report: GateReport) -> list[str]:
    """The common header of every register: title, authority relation, and what produced it."""
    authority = report.context.authority
    lines = [
        f"# {register.title}",
        "",
        f"> **Register:** `{register.file}` (ordinal {register.ordinal:02d})  ",
        f"> **Programme:** {authority.programme_id} v{authority.version}  ",
        f"> **Renderer:** `{register.renderer}`  ",
        f"> **{DERIVED_TRUTH}**  ",
        f"> **Declaration digest:** `{authority.digest()[:16]}`  ",
        "> **Regenerate:** `make uaue-render` — this file is a projection and never a source.",
        "",
    ]
    if register.purpose:
        lines.extend([f"*{register.purpose}*", ""])
    return lines


def mandatory_measures(report: GateReport) -> dict[str, int]:
    """The ten declared mandatory invariant measures, computed from the conducted runs.

    Every measure is named by the declaration (``mandatory[*].measure``) and computed here from
    the runs rather than reported by the thing being measured. A measure the declaration names and
    this function cannot compute is a refusal, not a zero: a missing measure that defaulted to
    zero would read as a satisfied invariant.

    Returns:
        A mapping from the declared measure name to the measured count. Deterministic over a
        fixed declaration and tree.

    Raises:
        EvolutionAuthorityError: the declaration names a measure this function cannot compute.
    """
    runs = report.runs
    authority = report.context.authority
    objects = [obj for run in runs for obj in run.chain.objects]
    phase_count = len(authority.phases)

    history_ids: set[str] = set()
    ledger = report.projection.get("ledger", {})
    if isinstance(ledger, Mapping):
        for record in ledger.get("records", []) or []:
            if isinstance(record, Mapping):
                subject = record.get("subject")
                if isinstance(subject, str):
                    history_ids.add(subject)

    duplicate_authorities = 0
    seen_home_sets: dict[frozenset[str], str] = {}
    for phase in authority.phases:
        key = phase.home_set
        if key in seen_home_sets:
            duplicate_authorities += 1
        else:
            seen_home_sets[key] = phase.identifier

    computed = {
        "anonymous_objects": sum(1 for obj in objects if not obj.evolution_id),
        "unmanaged_objects": sum(1 for obj in objects if not obj.authority),
        "objects_absent_from_history": sum(
            1 for obj in objects if obj.evolution_id not in history_ids
        ),
        "objects_without_evidence": sum(1 for obj in objects if not obj.evidence),
        "objects_without_validation": sum(1 for run in runs if run.validation is None),
        "objects_without_verification": sum(1 for run in runs if run.verification is None),
        "objects_without_certification": sum(1 for run in runs if run.certification is None),
        "duplicate_authorities": duplicate_authorities,
        "lifecycle_bypasses": sum(1 for run in runs if len(run.stage_results) != phase_count),
        "uncontrolled_mutations": sum(
            1 for run in runs if run.mutation_performed and not run.execution_authorized
        ),
    }
    unknown = [entry.measure for entry in authority.mandatory if entry.measure not in computed]
    if unknown:
        raise EvolutionAuthorityError(
            "the declaration names a mandatory measure this renderer cannot compute, "
            "so the invariant would be reported as satisfied without being measured",
            measures=unknown,
        )
    return computed


# --------------------------------------------------------------------------------------------
# Renderers. One per declared renderer name. Each takes the measured report and the register the
# declaration asked it to produce, and returns the complete file body.
# --------------------------------------------------------------------------------------------


def _render_dashboard(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    runs = report.runs
    measures = mandatory_measures(report)
    certified = sum(1 for run in runs if run.certified)
    halted = sum(1 for run in runs if run.halted)
    lines = _heading(register, report)
    lines.extend(["## Gate", "", f"**{report.summary}**", ""])
    lines.extend(
        _table(
            ("Obligation", "Verdict", "Detail"),
            (
                (entry.identifier, _mark(entry.satisfied), entry.detail)
                for entry in report.obligations
            ),
        )
    )
    lines.extend(["## Traversal", ""])
    lines.extend(
        _table(
            ("Measure", "Value"),
            (
                ("runs conducted", len(runs)),
                ("runs certified", certified),
                ("runs halted", halted),
                ("positions per run", len(authority.phases)),
                ("canonical stages", len(authority.lifecycle_states)),
                ("owner homes", len(authority.ownership)),
                ("declared registers", len(authority.registers)),
                ("evolution objects", sum(len(run.chain.objects) for run in runs)),
            ),
        )
    )
    lines.extend(["## Mandatory invariants", ""])
    lines.extend(
        _table(
            ("Invariant", "Measure", "Expected", "Measured", "Verdict"),
            (
                (
                    entry.identifier,
                    entry.measure,
                    entry.expect,
                    measures[entry.measure],
                    _mark(measures[entry.measure] == entry.expect),
                )
                for entry in authority.mandatory
            ),
        )
    )
    lines.extend(["## Registers", ""])
    lines.extend(
        _table(
            ("Ordinal", "File", "Renderer"),
            ((f"{entry.ordinal:02d}", entry.file, entry.renderer) for entry in authority.registers),
        )
    )
    return "\n".join(lines)


def _render_capability_matrix(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    lines = _heading(register, report)
    lines.extend(
        [
            "Every position of the loop, the owner homes that discharge it, the gate that closes "
            "it, and the classification the declaration's own rule measures it into.",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Position", "Name", "Duty", "Stages", "Owner homes", "Gate", "Wired", "Class"),
            (
                (
                    phase.identifier,
                    phase.name,
                    phase.duty,
                    ", ".join(phase.canonical_stages),
                    " · ".join(phase.homes),
                    phase.gate.command,
                    _mark(phase.gate.wired),
                    phase.classification,
                )
                for phase in authority.phases
            ),
        )
    )
    lines.extend(["## Classification vocabulary", ""])
    lines.extend(
        _table(
            ("Classification", "Rank", "Rule", "Meaning"),
            (
                (entry.identifier, entry.rank, entry.rule, entry.meaning)
                for entry in sorted(authority.classifications, key=lambda e: -e.rank)
            ),
        )
    )
    lines.extend(
        [
            "## Exit criteria",
            "",
            "Every criterion, and the violation count the declaration binds it to. A criterion "
            "is satisfied when its measure holds its declared expectation — measured on this run, "
            "not asserted by the declaration that states it.",
            "",
        ]
    )
    exits = exit_measures(report)
    lines.extend(
        _table(
            ("Criterion", "Phase", "Obligation", "Measure", "Expected", "Measured", "Verdict"),
            (
                (
                    entry.identifier,
                    entry.phase,
                    entry.criterion,
                    entry.measure,
                    entry.expect,
                    exits.get(entry.measure, "*(uncomputed)*"),
                    _mark(exits.get(entry.measure) == entry.expect),
                )
                for entry in authority.exit_criteria
            ),
        )
    )
    lines.extend(["## Discovery duties and the sources that satisfy them", ""])
    lines.extend(
        _table(
            ("Duty", "Obligation", "Satisfied by"),
            (
                (entry.identifier, entry.duty, ", ".join(entry.satisfied_by) or "—")
                for entry in authority.discovery_duties
            ),
        )
    )
    return "\n".join(lines)


def _render_object_model(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    runs = report.runs
    lines = _heading(register, report)
    lines.extend(["## Object kinds", ""])
    lines.extend(
        _table(
            ("Kind", "Name", "Position", "Mandated", "Purpose"),
            (
                (kind.identifier, kind.name, kind.phase, _mark(kind.mandated), kind.purpose)
                for kind in authority.object_kinds
            ),
        )
    )
    lines.extend(
        [
            "## Mandated fields",
            "",
            "Every mandated field, and the measurement of whether every object of every "
            "conducted run carries it. A field declared non-empty and measured empty is a "
            "refusal, which is why the count is rendered rather than a checkmark.",
            "",
        ]
    )
    objects = [obj for run in runs for obj in run.chain.objects]
    rows = []
    for field in authority.required_fields:
        if field.non_empty:
            empty = sum(1 for obj in objects if not obj.field_value(field.field_name))
        else:
            empty = 0
        rows.append(
            (
                field.identifier,
                field.field_name,
                _mark(field.non_empty),
                len(objects) - empty,
                empty,
                _mark(empty == 0),
            )
        )
    lines.extend(
        _table(
            ("Field", "Name", "Non-empty required", "Carried", "Empty", "Verdict"),
            rows,
        )
    )
    lines.extend(
        [
            "## Identity rule",
            "",
            "Identity is derived, never minted: no corpus serial is consumed and no registry is "
            "written, so this register cannot become a second identity authority.",
            "",
        ]
    )
    identity = authority.identity
    lines.extend(
        _table(
            ("Property", "Value"),
            (
                ("prefix", identity.prefix),
                ("width", identity.width),
                ("derivation", f"{identity.derivation_home}::{identity.derivation_symbol}"),
                ("digest", f"{identity.digest_home}::{identity.digest_symbol}"),
                ("inputs", ", ".join(identity.inputs)),
                ("anonymity rule", identity.anonymity_rule),
            ),
        )
    )
    return "\n".join(lines)


def _render_candidates(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    lines = _heading(register, report)
    lines.extend(
        [
            "What discovery found, from which owner's measurement, and why each is a candidate. "
            "Discovery reads sealed derived-truth artifacts other owners publish; it never scans "
            "the working tree, so every candidate is attributable to an owner that measured it.",
            "",
            "## Declared sources",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Source", "Name", "Owner", "Path", "Candidate class"),
            (
                (
                    entry.identifier,
                    entry.name,
                    entry.owner,
                    entry.path or "*(internal to the declaration)*",
                    entry.candidate_class,
                )
                for entry in authority.discovery_sources
            ),
        )
    )
    lines.extend(["## Candidates conducted", ""])
    lines.extend(
        _table(
            ("Identity", "Class", "Subject", "Positions", "Certified", "Halted at"),
            (
                (
                    run.candidate_identity,
                    run.candidate_class,
                    run.subject_identity,
                    len(run.stage_results),
                    _mark(run.certified),
                    run.halted_at or "—",
                )
                for run in report.runs
            ),
        )
    )
    return "\n".join(lines)


def _render_phase_objects(report: GateReport, register: Register) -> str:
    """One register per position that produces an inspectable object.

    Driven entirely by ``register.owner_phase``: five registers share this renderer and differ
    only in which position they render, so a sixth is a declaration entry rather than new code.
    """
    authority = report.context.authority
    phase = authority.phase(register.owner_phase)
    kind = authority.object_kind_of(phase.identifier)
    lines = _heading(register, report)
    lines.extend(
        _table(
            ("Property", "Value"),
            (
                ("position", f"{phase.identifier} — {phase.name}"),
                ("duty", phase.duty),
                ("produces", f"{kind.identifier} — {kind.name}"),
                ("canonical stages", ", ".join(phase.canonical_stages)),
                ("gate", f"`{phase.gate.command}` ({_mark(phase.gate.wired)})"),
                ("authority", phase.authority),
                ("classification", phase.classification),
            ),
        )
    )
    lines.extend([f"**Reuse basis.** {phase.reuse}", "", "## Owner homes", ""])
    lines.extend(
        _table(
            ("Home", "State", "Symbols read", "Unbound"),
            (
                (
                    owner.home,
                    owner.state,
                    ", ".join(owner.symbols) or "—",
                    ", ".join(owner.missing_symbols) or "—",
                )
                for owner in phase.owners
            ),
        )
    )
    lines.extend(["## Objects produced at this position", ""])
    rows = []
    for run in report.runs:
        for result in run.stage_results:
            if result.phase != phase.identifier:
                continue
            rows.append(
                (
                    result.evolution_id,
                    run.subject_identity,
                    result.lifecycle_state,
                    result.digest[:16] or "—",
                    _mark(result.discharged),
                    ", ".join(result.refusals) or "—",
                )
            )
    lines.extend(
        _table(
            ("Object", "Subject", "Stage", "Digest", "Discharged", "Refusals"),
            rows,
        )
    )
    return "\n".join(lines)


def _criteria_register(
    report: GateReport,
    register: Register,
    criteria: Sequence[Any],
    selector: Callable[[EvolutionRun], Any],
    *,
    gated: bool,
) -> str:
    """Shared body of the validation, verification and certification registers.

    The three differ only in which criterion block they quote and which verdict they read off the
    run. Rendering them through one function is what keeps the three reports from drifting into
    three different opinions about what a satisfied criterion looks like.
    """
    lines = _heading(register, report)
    headers: tuple[str, ...] = ("Criterion", "Subject", "Obligation", "Blocking")
    if gated:
        headers = headers + ("Bound gate",)
    lines.extend(["## Declared criteria", ""])
    lines.extend(
        _table(
            headers,
            (
                (
                    (entry.identifier, entry.subject, entry.obligation, _mark(entry.blocking))
                    + ((entry.bound_gate,) if gated else ())
                )
                for entry in criteria
            ),
        )
    )
    lines.extend(["## Measured outcome per run", ""])
    rows = []
    for run in report.runs:
        verdict = selector(run)
        if verdict is None:
            rows.append((run.candidate_identity, run.subject_identity, "—", "*(unmeasured)*"))
            continue
        failures = [entry.identifier for entry in verdict.outcomes if not entry.satisfied]
        rows.append(
            (
                run.candidate_identity,
                run.subject_identity,
                _mark(verdict.passed),
                ", ".join(failures) or "every criterion satisfied",
            )
        )
    lines.extend(_table(("Run", "Subject", "Verdict", "Unsatisfied"), rows))
    lines.extend(["## Aggregate by criterion", ""])
    totals: dict[str, tuple[int, int]] = {}
    for run in report.runs:
        verdict = selector(run)
        if verdict is None:
            continue
        for entry in verdict.outcomes:
            satisfied, total = totals.get(entry.identifier, (0, 0))
            totals[entry.identifier] = (satisfied + (1 if entry.satisfied else 0), total + 1)
    lines.extend(
        _table(
            ("Criterion", "Satisfied", "Measured", "Verdict"),
            (
                (
                    entry.identifier,
                    totals.get(entry.identifier, (0, 0))[0],
                    totals.get(entry.identifier, (0, 0))[1],
                    _mark(
                        totals.get(entry.identifier, (0, 0))[0]
                        == totals.get(entry.identifier, (0, 0))[1]
                        and totals.get(entry.identifier, (0, 0))[1] > 0
                    ),
                )
                for entry in criteria
            ),
        )
    )
    return "\n".join(lines)


def _render_validation_report(report: GateReport, register: Register) -> str:
    return _criteria_register(
        report,
        register,
        report.context.authority.validations,
        lambda run: run.validation,
        gated=False,
    )


def _render_verification_report(report: GateReport, register: Register) -> str:
    return _criteria_register(
        report,
        register,
        report.context.authority.verifications,
        lambda run: run.verification,
        gated=True,
    )


def _render_certification_report(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    body = _criteria_register(
        report,
        register,
        authority.certifications,
        lambda run: run.certification,
        gated=False,
    )
    measures = mandatory_measures(report)
    certified = sum(1 for run in report.runs if run.certified)
    blocking_unmet = [
        entry.identifier
        for entry in authority.mandatory
        if entry.blocking and measures[entry.measure] != entry.expect
    ]
    exits = exit_measures(report)
    exits_unmet = [
        entry.identifier
        for entry in authority.exit_criteria
        if exits.get(entry.measure) != entry.expect
    ]
    lines = [body, "", "## Certification determination", ""]
    lines.extend(
        _table(
            ("Question", "Answer"),
            (
                ("runs certified", f"{certified}/{len(report.runs)}"),
                (
                    "gate obligations satisfied",
                    f"{len(report.obligations) - len(report.failures)}"
                    f"/{len(report.obligations)}",
                ),
                ("blocking invariants unmet", ", ".join(blocking_unmet) or "none"),
                (
                    "exit criteria satisfied",
                    f"{len(authority.exit_criteria) - len(exits_unmet)}"
                    f"/{len(authority.exit_criteria)}",
                ),
                ("exit criteria unmet", ", ".join(exits_unmet) or "none"),
                ("unknown subject traversed", _mark(_unknown_satisfied(report))),
                ("self-evolution gap closed", _mark(authority.self_evolution.closed)),
            ),
        )
    )
    determination = (
        "CERTIFIED-PROVISIONAL"
        if certified == len(report.runs) and report.open and not blocking_unmet and not exits_unmet
        else "NOT-CERTIFIED"
    )
    lines.extend(
        [
            f"**Determination: {determination}**",
            "",
            "`CERTIFIED-PROVISIONAL` is the ceiling any engineering certification in this "
            "repository can reach: certification confers engineering readiness and never "
            "constitutional authority, and the corpus contains no instrument competent to ratify "
            "finality. The verdict is withheld rather than inflated.",
            "",
        ]
    )
    return "\n".join(lines)


def _unknown_satisfied(report: GateReport) -> bool:
    """Whether the unknown-subject obligation was measured satisfied.

    Selected by the probe's own subject rather than by an obligation identifier written here: an
    identifier literal would couple this register to the gate's numbering.
    """
    subject = report.context.authority.unknown_probe.subject
    for run in report.runs:
        if run.subject_identity == subject:
            return run.certified and not run.halted
    return False


#: Patterns that make a rendered register irreproducible. A memory address differs per process
#: and an absolute path differs per machine, so either one turns the replay proof into a proof
#: that only holds where the bytes were written. Both were real defects caught by the gate.
_IRREPRODUCIBLE = (
    re.compile(r"0x[0-9a-f]{6,}"),
    re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}"),
)


def irreproducible_content(report: GateReport) -> tuple[str, ...]:
    """Registers whose rendered bytes could not reproduce elsewhere.

    Scans every rendered body for a memory address, a wall clock, and the absolute repository
    root. This is measured rather than trusted because the first render of this surface shipped
    an object ``repr`` containing a heap address: the bytes were the right length, the diff was
    one line, and every count in the register was correct — exactly the shape of defect a
    length check or a spot read does not catch.
    """
    root = str(report.context.substrate.root)
    findings: list[str] = []
    for file, body in rendered_surface(report).items():
        for pattern in _IRREPRODUCIBLE:
            match = pattern.search(body)
            if match:
                findings.append(f"{file}: irreproducible token {match.group(0)!r}")
        if root in body:
            findings.append(f"{file}: embeds the absolute repository root")
    return tuple(findings)


def _relative(path: object, root: Path) -> str:
    """A repository-relative path, so a rendered register is machine-independent.

    An absolute path would make the surface reproduce only on the machine that wrote it, which
    would defeat the cross-process replay proof the gate performs in CI.
    """
    try:
        return str(Path(str(path)).relative_to(root))
    except ValueError:
        return str(path)


def _render_controller(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    context = report.context
    lines = _heading(register, report)
    lines.extend(
        [
            "The controller traverses every position for every candidate with no phase-specific "
            "and no subject-specific branch. That is the property that makes an unknown subject "
            "traversable: if the controller needed to know what the subject was, the unknown "
            "probe could not settle.",
            "",
            "## Conducting context",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Property", "Value"),
            (
                ("observer", context.observer),
                (
                    "evidence source",
                    _relative(context.evidence_source.source, context.substrate.root),
                ),
                ("validation policy", context.validation_policy),
                ("verification policy", context.verification_policy),
                ("certification policy", context.certification_policy),
                ("execution permissions", ", ".join(context.execution_permissions) or "none"),
                ("settlement ceiling", context.max_settlement_rounds),
                ("context digest", context.digest()[:16]),
            ),
        )
    )
    lines.extend(["## Position order and dependencies", ""])
    lines.extend(
        _table(
            ("Position", "Ordinal", "Depends on"),
            (
                (
                    phase.identifier,
                    phase.ordinal,
                    ", ".join(authority.dependencies_of(phase.identifier)) or "—",
                )
                for phase in authority.phases
            ),
        )
    )
    lines.extend(["## Settlement per run", ""])
    lines.extend(
        _table(
            ("Run", "Subject", "Rounds", "Ceiling", "Converged", "State digest"),
            (
                (
                    run.run_id[:16],
                    run.subject_identity,
                    run.settlement.rounds if run.settlement else "—",
                    run.settlement.ceiling if run.settlement else "—",
                    _mark(bool(run.settlement and run.settlement.converged)),
                    run.settlement.digest[:16] if run.settlement else "—",
                )
                for run in report.runs
            ),
        )
    )
    return "\n".join(lines)


def _render_history(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    history = authority.history
    ledger = report.projection.get("ledger", {})
    counts = ledger.get("counts", {}) if isinstance(ledger, Mapping) else {}
    lines = _heading(register, report)
    lines.extend([HISTORY_IS_JSON, "", "## Projection", ""])
    lines.extend(
        _table(
            ("Property", "Value"),
            (
                ("canonical file", f"`{PROGRAMME_HOME}/{history.file}`"),
                ("schema", f"{history.schema} v{history.version}"),
                ("append only", _mark(history.append_only)),
                ("ledger owner", f"{history.ledger_home}::{history.ledger_symbol}"),
                ("written through", history.document_symbol),
                ("read back through", history.rehydration_symbol),
                ("projection digest", content_hash(report.projection)[:16]),
            ),
        )
    )
    lines.extend(["## Ledger counts", ""])
    lines.extend(
        _table(
            ("Count", "Value"),
            ((key, counts.get(key, 0)) for key in sorted(counts)),
        )
    )
    lines.extend(
        [
            "## Recorded dimensions",
            "",
            "`when` is logical (`cycle=N stage=S ordinal=K`) and never a timestamp, so the "
            "history replays byte-identically.",
            "",
        ]
    )
    lines.extend(_table(("Dimension",), ((entry,) for entry in history.dimensions)))
    lines.extend(["## Queryable keys", ""])
    lines.extend(_table(("Key",), ((entry,) for entry in history.queryable_by)))
    return "\n".join(lines)


def _render_self_evolution(report: GateReport, register: Register) -> str:
    subject = report.context.authority.self_evolution
    lines = _heading(register, report)
    lines.extend(
        [
            "The programme's own demonstration that the platform can detect a gap in itself, "
            "understand it, plan it, execute it through a located owner, and have the closure "
            "measured for ever after. The measurement stays live: if the surface is removed this "
            "register reopens the candidate and the gate closes.",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Property", "Value"),
            (
                ("subject", subject.identifier),
                ("subject identity", subject.subject_identity),
                ("detected by", subject.detected_by),
                ("home", subject.home),
                ("home state", subject.home_state),
                ("authority", subject.authority),
                ("executed through", subject.executed_through),
            ),
        )
    )
    lines.extend(
        [
            "## The gap",
            "",
            f"{subject.gap}",
            "",
            "| Before | After |",
            "|---|---|",
            f"| {_cell(subject.previous_state)} | {_cell(subject.target_state)} |",
            "",
            "## Closure measurement",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Required symbol", "Bound in home"),
            (
                (symbol, _mark(symbol not in subject.missing_symbols))
                for symbol in subject.required_symbols
            ),
        )
    )
    lines.extend(
        _table(
            ("Evidence path", "Resolves"),
            ((path, _mark(path not in subject.unresolved_evidence)) for path in subject.evidence),
        )
    )
    lines.extend(
        [
            f"**Gap closed: {_mark(subject.closed)}**",
            "",
        ]
    )
    return "\n".join(lines)


def _render_unknown_evolution(report: GateReport, register: Register) -> str:
    probe = report.context.authority.unknown_probe
    authority = report.context.authority
    lines = _heading(register, report)
    lines.extend(
        [
            "The only obligation that measures the claim the whole programme is *for*, and it is "
            "measured by conducting it rather than by asserting it. The probe is not a fixture "
            "beside the code: it is discovered by a declared source and carried through the same "
            "controller as every other candidate.",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Property", "Value"),
            (
                ("probe", probe.identifier),
                ("subject", probe.subject),
                ("subject class", probe.subject_class),
                ("unknown stage term", probe.unknown_stage_term),
            ),
        )
    )
    lines.extend(
        [
            "## What the traversal must not require",
            "",
            "Each row is a thing a future unknown domain must be able to enter without. A "
            "traversal that needed any of them would mean the platform requires architectural "
            "redesign per domain, which is the failure this probe exists to detect.",
            "",
        ]
    )
    own = f"{PROGRAMME_HOME}/"
    invented = sorted(
        home for home in (entry.home for entry in authority.ownership) if home.startswith(own)
    )
    lines.extend(
        _table(
            ("Must not require", "Required"),
            ((entry, _mark(False)) for entry in probe.must_not_require),
        )
    )
    lines.extend(
        [
            f"Owner homes created inside this programme's own home: "
            f"**{', '.join(invented) if invented else 'none'}** — every position resolves to an "
            f"owner that exists independently of this register "
            f"({len(authority.ownership)} pre-existing homes).",
            "",
            "## The traversal",
            "",
        ]
    )
    rows = []
    for run in report.runs:
        if run.subject_identity != probe.subject:
            continue
        for result in run.stage_results:
            rows.append(
                (
                    result.ordinal,
                    result.phase,
                    result.object_kind,
                    result.lifecycle_state,
                    result.evolution_id,
                    _mark(result.discharged),
                )
            )
    lines.extend(
        _table(
            ("Ordinal", "Position", "Object kind", "Stage", "Object", "Discharged"),
            rows,
        )
    )
    lines.extend(
        [f"**Unknown subject traversed and certified: {_mark(_unknown_satisfied(report))}**", ""]
    )
    return "\n".join(lines)


def _render_mandatory_ledger(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    measures = mandatory_measures(report)
    lines = _heading(register, report)
    lines.extend(
        [
            "Every mandatory invariant the declaration carries, its declared expectation, and "
            "the measured value. A blocking invariant whose measured value differs from its "
            "expectation closes the gate.",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Invariant", "Statement", "Measure", "Expected", "Measured", "Blocking", "Verdict"),
            (
                (
                    entry.identifier,
                    entry.invariant,
                    entry.measure,
                    entry.expect,
                    measures[entry.measure],
                    _mark(entry.blocking),
                    _mark(measures[entry.measure] == entry.expect),
                )
                for entry in authority.mandatory
            ),
        )
    )
    unmet = [
        entry.identifier for entry in authority.mandatory if measures[entry.measure] != entry.expect
    ]
    lines.extend([f"**Invariants unmet: {', '.join(unmet) if unmet else 'none'}**", ""])
    return "\n".join(lines)


def _render_boundaries(report: GateReport, register: Register) -> str:
    authority = report.context.authority
    lines = _heading(register, report)
    lines.extend(
        [
            "The reuse-before-create answer, recorded rather than re-litigated. Each row names "
            "another located owner, that owner's subject, this register's subject, and why the "
            "two are not two authorities over one thing. The other owner's existence is measured: "
            "a boundary drawn against a home that has vanished is unverifiable, not satisfied.",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Boundary", "Other owner", "Resolves", "Other subject", "This subject"),
            (
                (
                    entry.identifier,
                    entry.other_owner,
                    _mark(entry.other_owner_resolves),
                    entry.other_subject,
                    entry.this_subject,
                )
                for entry in authority.boundaries
            ),
        )
    )
    lines.extend(["## Why each is not a duplicate", ""])
    for entry in authority.boundaries:
        lines.extend(
            [
                f"**{entry.identifier} — `{entry.other_owner}`**",
                "",
                f"{entry.why_not_duplicate}",
                "",
            ]
        )
    unverifiable = [
        entry.identifier for entry in authority.boundaries if not entry.other_owner_resolves
    ]
    lines.extend(
        [
            f"**Boundaries drawn against an unresolvable owner: "
            f"{', '.join(unverifiable) if unverifiable else 'none'}**",
            "",
        ]
    )
    return "\n".join(lines)


#: Renderer name to implementation. The declaration chooses the names; this maps them to code.
#: A declared renderer with no entry here is a refusal in :func:`rendered_surface`, never a
#: skipped register: silently omitting a register the declaration named is how a surface rots.
RENDERERS: dict[str, Callable[[GateReport, Register], str]] = {
    "boundaries": _render_boundaries,
    "candidates": _render_candidates,
    "capability_matrix": _render_capability_matrix,
    "certification_report": _render_certification_report,
    "controller": _render_controller,
    "dashboard": _render_dashboard,
    "history": _render_history,
    "mandatory_ledger": _render_mandatory_ledger,
    "object_model": _render_object_model,
    "phase_objects": _render_phase_objects,
    "self_evolution": _render_self_evolution,
    "unknown_evolution": _render_unknown_evolution,
    "validation_report": _render_validation_report,
    "verification_report": _render_verification_report,
}


def register_path(context: EvolutionContext, file: str, root: Path | None = None) -> Path:
    """Where one register is written: this programme's own home, and nowhere else."""
    base = root if root is not None else context.substrate.root
    return base / PROGRAMME_HOME / file


def render_register(report: GateReport, register: Register) -> str:
    """The complete body of one register, with a trailing newline.

    Raises:
        EvolutionAuthorityError: the declaration names a renderer that does not exist.
    """
    renderer = RENDERERS.get(register.renderer)
    if renderer is None:
        raise EvolutionAuthorityError(
            "the declaration names a renderer this module does not implement, "
            "so the register it declares could never be produced",
            register=register.file,
            renderer=register.renderer,
            implemented=sorted(RENDERERS),
        )
    body = renderer(report, register)
    return body if body.endswith("\n") else body + "\n"


def rendered_surface(report: GateReport) -> dict[str, str]:
    """Every declared register, rendered, in declared order: file name to complete body.

    This module renders and never writes. The whole surface is materialised in one call and
    returned, so the caller either receives all eighteen bodies or receives none — the property
    that makes a partial write impossible downstream. A surface that wrote sixteen of eighteen
    files and reported success would leave two registers carrying the previous run's
    measurements, and the honest place to make that unrepresentable is here, before any path is
    touched: :func:`engine.uaue.gate.render_registers` cannot write a file whose body was not
    produced, because it is handed bodies rather than a licence to render.

    Raises:
        EvolutionAuthorityError: the declaration names a renderer this module does not implement.
    """
    return {
        register.file: render_register(report, register)
        for register in report.context.authority.registers
    }


def replay_drift(report: GateReport, root: Path | None = None) -> tuple[str, ...]:
    """Empty when every committed register is exactly what the declaration produces.

    Each register is compared as bytes rather than as parsed Markdown, for the same reason the
    history projection is: a register that only matches after normalisation is a register whose
    canonical form nobody is holding to.

    Reading is not mutating. This module may open a committed register to compare it against the
    bytes the declaration produces, because that is a measurement; what it may not do is write
    one, which is why :func:`rendered_surface` returns bodies and the gate owns every path that
    is touched.
    """
    drift: list[str] = []
    surface = rendered_surface(report)
    for register in report.context.authority.registers:
        target = register_path(report.context, register.file, root)
        expected = surface[register.file]
        if not target.is_file():
            drift.append(f"{register.file}: not rendered")
            continue
        try:
            actual = target.read_text(encoding="utf-8")
        except OSError as error:
            drift.append(f"{register.file}: unreadable ({error})")
            continue
        if actual != expected:
            drift.append(
                f"{register.file}: committed bytes are not the product of the declaration "
                f"({len(actual)} committed, {len(expected)} projected)"
            )
    return tuple(drift)


def surface_digest(report: GateReport) -> str:
    """One digest over the whole rendered surface, for a single-value replay comparison."""
    return content_hash(rendered_surface(report))


__all__ = [
    "DERIVED_TRUTH",
    "RENDERERS",
    "irreproducible_content",
    "mandatory_measures",
    "register_path",
    "render_register",
    "rendered_surface",
    "replay_drift",
    "surface_digest",
]

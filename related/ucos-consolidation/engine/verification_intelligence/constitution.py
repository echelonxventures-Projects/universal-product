"""UVI-000001 Part 02 — the Verification Mode Constitution and the Stage Registry.

Both are DATA. ``00-MASTER/UVI-000001/uvi-declaration.json`` holds every mode, every
stage classification and every law; this module holds no mode name, no stage label and
no law text. That is the discipline ``engine/context/constitution.py`` applies to
CXL-01..12 and ``engine/object_birth/contract.py`` applies to UOBC-L-01..08, and the
reason is the same in all three: a law that lives in the engine that checks it is a law
the engine can quietly rewrite.

The one thing this module refuses at construction time is an incoherent declaration —
a law naming a check nothing implements, a check nothing claims, a stage naming a
dependency that is not declared, or a mode listing a stage that does not exist. A
constitution that cannot be constructed is a FAULT, deliberately not a verdict.
"""

from __future__ import annotations

import json
import os
import re
import shlex
from dataclasses import dataclass
from typing import Any

from engine.verification_intelligence.model import (
    Coverage,
    Mode,
    Selection,
    StageSpec,
    VerificationIntelligenceError,
)

#: The declaration this engine is the realization of. Read; never written.
DECLARATION = "00-MASTER/UVI-000001/uvi-declaration.json"

#: The measured-cost table the shard planner prices test objects from. Absent or stale
#: entries are priced at the default; a missing cost table is a slower plan, never a
#: wrong one.
COST_MODEL = "00-MASTER/UVI-000001/test-cost-model.json"

#: The entry point that IS the execution contract. A stage's identity is not its label
#: alone — it is the label together with the command the script actually runs under it.
#: This is the same file ``gate.py`` reads for UVI-L-03, read here for the argv rather
#: than for the label.
VERIFY = "verify.sh"

#: ``run_stage "<label>" <argv…>``, after backslash-continuations have been folded away.
#: The label is interpolated per lookup (and escaped), so no label text lives here.
_RUN_STAGE = r'^[ \t]*run_stage[ \t]+"{label}"[ \t]*(.*)$'

#: A backslash-continuation and the indentation that follows it. Folding these is what
#: makes the contract insensitive to how the invocation is WRAPPED while remaining
#: sensitive to what it RUNS.
_CONTINUATION = re.compile(r"\\\n[ \t]*")


def repo_root() -> str:
    """The repository root, derived from this file's location."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def verify_source(root: str | None = None) -> str:
    """The text of ``./verify.sh``.

    Raises:
        VerificationIntelligenceError: the entry point is unreadable. A contract that
            cannot be read is a FAULT, never an empty contract — an empty one would
            make every stage's key agree with every other stage's key.
    """
    target = os.path.join(root or repo_root(), VERIFY)
    try:
        with open(target, encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:  # pragma: no cover - only on a broken checkout
        raise VerificationIntelligenceError(f"{VERIFY} is unreadable") from exc


def execution_contract(
    label: str, *, root: str | None = None, source: str | None = None
) -> tuple[str, ...] | None:
    """The argv ``./verify.sh`` runs under ``label``, tokenised — or None.

    THE SOURCE TEXT IS THE CONTRACT, AND THAT IS THE POINT. The tokens returned are the
    ones the script DECLARES, not the ones a process would receive after the shell has
    expanded them. ``"$PY"`` comes back as the literal ``$PY``, never as
    ``/…/.ec1-venv/bin/python``. Binding the expanded form would put this machine's
    absolute venv path into every cache key — the key would stop being comparable
    between two machines, and UVI-L-10's prohibition on an absolute path reaching a plan
    would be violated by the very field added to make the plan honest.

    Two normalisations, each chosen so the key tracks WHAT RUNS and not HOW IT IS
    WRITTEN:

    * backslash-continuations are folded, so re-wrapping a long invocation across lines
      does not invalidate the cache;
    * the remainder is tokenised with :mod:`shlex`, so ``"$PY"`` and ``$PY`` are one
      token and runs of whitespace collapse.

    What it deliberately does NOT normalise is ORDER. ``--gate --quiet`` and
    ``--quiet --gate`` are different tuples and therefore different keys, because a
    shell passes them in the order written and nothing here may assume a flag parser
    is order-insensitive.

    Returns None — never a placeholder, and never an empty tuple standing in for
    "unknown" — when the label appears no times or more than once. Both are drift
    between the registry and the script. UVI-L-03 measures that drift and refuses it as
    a verdict; this function's obligation is narrower and simpler: refuse the key, so
    the stage runs. A stage that runs when its contract is ambiguous is correct; a
    stage answered from a cache keyed on a guess is not.
    """
    text = source if source is not None else verify_source(root)
    folded = _CONTINUATION.sub(" ", text)
    matches = re.findall(_RUN_STAGE.format(label=re.escape(label)), folded, re.M)
    if len(matches) != 1:
        return None
    try:
        return tuple(shlex.split(matches[0]))
    except ValueError:
        # Unbalanced quoting in the invocation. Unparseable is unknown, and unknown
        # refuses the key rather than guessing at a tokenisation.
        return None


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VerificationIntelligenceError(f"declaration field is missing or empty: {field}")
    return value


def _tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise VerificationIntelligenceError(f"expected a list, found {type(value).__name__}")
    return tuple(str(item) for item in value)


@dataclass(frozen=True, slots=True)
class Law:
    """One declared law and the check that computes it."""

    law_id: str
    title: str
    statement: str
    check: str


@dataclass(frozen=True, slots=True)
class Constitution:
    """The whole declared verification constitution, validated on construction."""

    artifact_id: str
    version: str
    modes: tuple[Mode, ...]
    default_mode_id: str
    stages: tuple[StageSpec, ...]
    laws: tuple[Law, ...]
    substrates: tuple[dict[str, Any], ...]
    layers: tuple[dict[str, Any], ...]
    evidence_home: str
    evidence_reuse_conditions: tuple[str, ...]
    sharding: dict[str, Any]

    # --- lookups ---------------------------------------------------------------

    @property
    def mode_ids(self) -> tuple[str, ...]:
        return tuple(mode.mode_id for mode in self.modes)

    @property
    def flags(self) -> tuple[str, ...]:
        return tuple(mode.flag for mode in self.modes)

    @property
    def stage_labels(self) -> tuple[str, ...]:
        """Every declared stage label, in declared order — the ``UVI-L-03`` subject."""
        return tuple(stage.label for stage in self.stages)

    @property
    def default_mode(self) -> Mode:
        return self.mode(self.default_mode_id)

    def mode(self, mode_id: str) -> Mode:
        for candidate in self.modes:
            if candidate.mode_id == mode_id:
                return candidate
        raise VerificationIntelligenceError(f"no such declared mode: {mode_id}")

    def stage(self, stage_id: str) -> StageSpec:
        for candidate in self.stages:
            if candidate.stage_id == stage_id:
                return candidate
        raise VerificationIntelligenceError(f"no such declared stage: {stage_id}")

    def stages_for(self, mode: Mode) -> tuple[StageSpec, ...]:
        """Every stage the mode declares, in declared order.

        A mode declaring ``stages`` as a list runs exactly that list. A mode declaring
        the string ``CONTRACT`` runs every stage whose own ``modes`` admits it and
        whose phase is inside the default contract; ``CONTRACT_AND_EXTENDED`` adds the
        opt-in phase. The stage's own membership is authoritative either way, so a
        stage cannot be dragged into a mode it refuses.
        """
        admitted = tuple(s for s in self.stages if mode.mode_id in s.modes)
        if isinstance(mode.stages, tuple):
            requested = set(mode.stages)
            unknown = requested - {s.stage_id for s in self.stages}
            if unknown:
                raise VerificationIntelligenceError(
                    f"mode {mode.mode_id} lists undeclared stage(s): {sorted(unknown)}"
                )
            return tuple(s for s in admitted if s.stage_id in requested)
        if mode.stages == "CONTRACT_AND_EXTENDED":
            return admitted
        if mode.stages == "CONTRACT":
            return tuple(s for s in admitted if s.phase != "EXTENDED")
        raise VerificationIntelligenceError(
            f"mode {mode.mode_id} declares an unknown stage selector: {mode.stages!r}"
        )


def _parse_mode(raw: dict[str, Any]) -> Mode:
    stages: str | tuple[str, ...]
    declared = raw.get("stages")
    stages = declared if isinstance(declared, str) else _tuple(declared)
    try:
        selection = Selection(_text(raw.get("selection"), "mode.selection"))
        coverage = Coverage(_text(raw.get("coverage"), "mode.coverage"))
    except ValueError as exc:
        raise VerificationIntelligenceError(f"mode declares an unknown vocabulary: {exc}") from exc
    return Mode(
        mode_id=_text(raw.get("id"), "mode.id"),
        flag=_text(raw.get("flag"), "mode.flag"),
        purpose=_text(raw.get("purpose"), "mode.purpose"),
        claim=_text(raw.get("claim"), "mode.claim"),
        claims_not=_tuple(raw.get("claims_not")),
        selection=selection,
        coverage=coverage,
        certification_eligible=bool(raw.get("certification_eligible")),
        evidence_reuse=bool(raw.get("evidence_reuse")),
        parallel=bool(raw.get("parallel")),
        stages=stages,
        budget_seconds=int(raw.get("budget_seconds", 0)),
    )


def _parse_stage(raw: dict[str, Any]) -> StageSpec:
    return StageSpec(
        stage_id=_text(raw.get("id"), "stage.id"),
        label=_text(raw.get("label"), "stage.label"),
        phase=_text(raw.get("phase"), "stage.phase"),
        plane=_text(raw.get("plane"), "stage.plane"),
        depends_on=_tuple(raw.get("depends_on")),
        modes=_tuple(raw.get("modes")),
        reusable=bool(raw.get("reusable")),
        reuse_inputs=_tuple(raw.get("reuse_inputs")),
        owner=_text(raw.get("owner"), "stage.owner"),
        shardable=bool(raw.get("shardable")),
        read_set=_tuple(raw.get("read_set")),
    )


def load_declaration(path: str | None = None) -> dict[str, Any]:
    """Read the declaration document.

    Raises:
        VerificationIntelligenceError: it is absent or unparseable. The engine has no
            fallback constitution and deliberately declares none — a hardcoded default
            would be a second constitution, which is the condition this design refuses.
    """
    target = path or os.path.join(repo_root(), DECLARATION)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationIntelligenceError(f"declaration is unreadable: {target}") from exc
    if not isinstance(document, dict):
        raise VerificationIntelligenceError(f"declaration is not an object: {target}")
    return document


def load_constitution(path: str | None = None, *, checks: frozenset[str] | None = None):
    """Build the constitution, refusing every incoherence it can compute.

    Args:
        path: declaration override, for tests.
        checks: the check names the gate actually implements. When supplied, a law
            naming a missing check and a check no law claims are both refused — the
            bidirectional binding UISD-000001 and UOBC-000001 both hold themselves to.

    Raises:
        VerificationIntelligenceError: the declaration cannot be constructed into a
            coherent constitution. That is a FAULT, not a verdict.
    """
    document = load_declaration(path)
    constitution_block = document.get("mode_constitution")
    registry_block = document.get("stage_registry")
    if not isinstance(constitution_block, dict) or not isinstance(registry_block, dict):
        raise VerificationIntelligenceError(
            "the declaration holds no mode_constitution or no stage_registry"
        )

    modes = tuple(
        _parse_mode(raw) for raw in constitution_block.get("modes", []) if isinstance(raw, dict)
    )
    if not modes:
        raise VerificationIntelligenceError("the constitution declares no modes")
    if len({mode.mode_id for mode in modes}) != len(modes):
        raise VerificationIntelligenceError("two modes share one id")

    stages = tuple(
        _parse_stage(raw) for raw in registry_block.get("stages", []) if isinstance(raw, dict)
    )
    if not stages:
        raise VerificationIntelligenceError("the stage registry declares no stages")
    if len({stage.stage_id for stage in stages}) != len(stages):
        raise VerificationIntelligenceError("two stages share one id")
    if len({stage.label for stage in stages}) != len(stages):
        raise VerificationIntelligenceError(
            "two stages share one label; the label is the join key to verify.sh and to the "
            "canonical validation record, so it must identify exactly one stage"
        )

    declared_phases = {entry.get("id") for entry in registry_block.get("phases", [])}
    declared_planes = {entry.get("id") for entry in registry_block.get("planes", [])}
    stage_ids = {stage.stage_id for stage in stages}
    for stage in stages:
        if stage.phase not in declared_phases:
            raise VerificationIntelligenceError(
                f"stage {stage.stage_id} declares an undeclared phase: {stage.phase}"
            )
        if stage.plane not in declared_planes:
            raise VerificationIntelligenceError(
                f"stage {stage.stage_id} declares an undeclared plane: {stage.plane}"
            )
        missing = set(stage.depends_on) - stage_ids
        if missing:
            raise VerificationIntelligenceError(
                f"stage {stage.stage_id} depends on undeclared stage(s): {sorted(missing)}"
            )
        unknown_modes = set(stage.modes) - {mode.mode_id for mode in modes}
        if unknown_modes:
            raise VerificationIntelligenceError(
                f"stage {stage.stage_id} admits undeclared mode(s): {sorted(unknown_modes)}"
            )
        if stage.reusable and not stage.reuse_inputs:
            raise VerificationIntelligenceError(
                f"stage {stage.stage_id} is declared reusable but names no reuse_inputs, so its "
                "cache key would cover nothing and every run would be a false hit"
            )

    default_mode_id = _text(constitution_block.get("default_mode"), "default_mode")
    if default_mode_id not in {mode.mode_id for mode in modes}:
        raise VerificationIntelligenceError(
            f"the declared default mode is not a declared mode: {default_mode_id}"
        )

    laws = tuple(
        Law(
            law_id=_text(raw.get("id"), "law.id"),
            title=_text(raw.get("title"), "law.title"),
            statement=_text(raw.get("statement"), "law.statement"),
            check=_text(raw.get("check"), "law.check"),
        )
        for raw in document.get("laws", [])
        if isinstance(raw, dict)
    )
    if not laws:
        raise VerificationIntelligenceError("the declaration states no laws")
    # A DUPLICATE LAW ID IS A SHADOWED VERDICT, AND IT WAS ACCEPTED SILENTLY. Adding a law
    # that reused an existing id produced a report reading "15/15 laws hold" over fourteen
    # distinct ids: two different obligations answered to one name, so a reader auditing the
    # verdict for a given id could be shown either. Refused at LOAD rather than as a law,
    # for the reason recorded on the sibling refusals here — a law that can be switched off
    # by the data it reads is not a law, and this one's subject is the law list itself.
    duplicate_ids = sorted(
        {law.law_id for law in laws if [x.law_id for x in laws].count(law.law_id) > 1}
    )
    if duplicate_ids:
        raise VerificationIntelligenceError(
            f"law id(s) declared more than once: {duplicate_ids}. Two obligations answering to "
            "one identity means one verdict shadows the other."
        )
    if checks is not None:
        claimed = {law.check for law in laws}
        unimplemented = sorted(claimed - checks)
        if unimplemented:
            raise VerificationIntelligenceError(
                f"law(s) name a check that is not implemented: {unimplemented}"
            )
        unclaimed = sorted(checks - claimed)
        if unclaimed:
            raise VerificationIntelligenceError(
                f"check(s) are implemented but claimed by no law: {unclaimed}"
            )

    selection_block = document.get("selection") or {}
    evidence_block = document.get("evidence_registry") or {}
    execution_block = document.get("execution") or {}

    return Constitution(
        artifact_id=_text(document.get("artifact_id"), "artifact_id"),
        version=_text(document.get("version"), "version"),
        modes=modes,
        default_mode_id=default_mode_id,
        stages=stages,
        laws=laws,
        substrates=tuple(selection_block.get("substrates") or ()),
        layers=tuple(selection_block.get("layers") or ()),
        evidence_home=str(evidence_block.get("home") or ".ucos-verification-evidence/"),
        evidence_reuse_conditions=_tuple(evidence_block.get("reuse_conditions")),
        sharding=dict(execution_block.get("test_sharding") or {}),
    )

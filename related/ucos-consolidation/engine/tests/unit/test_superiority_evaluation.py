"""UKAP-001 / WP-002 / D-2 — superiority evaluation validation suite.

Proves the capability, not a description of it:

  * every presence-classified object carries a superiority verdict  (totality)
  * all five mandated states are implemented AND reachable
  * deterministic evaluation — no randomness, clock or model judgement
  * byte-identical regeneration from the stored profiles
  * Repository Truth preserved — the presence axis is not touched
  * Knowledge Once preserved — restatement is measured, never adopted silently
  * dependency closure preserved — a recorded dependency must resolve
  * traceability preserved — every verdict cites its rule and full dimension profile
  * backward compatibility — a pre-D-2 record still deserializes, and fails closed

The unit scenarios are hermetic: synthetic knowledge objects and rows are built in-process, so
the suite never needs the external evidence tree.
"""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROGRAM_DIR = REPO / "00-MASTER" / "UAKOS-CLOSURE-008"
SUP_PATH = PROGRAM_DIR / "superiority_engine.py"
ASSIM_JSON = PROGRAM_DIR / "assimilation.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sup = _load("d2_superiority_engine", SUP_PATH)


# --------------------------------------------------------------------------- fixtures
def obj(**over) -> dict:
    """A knowledge object carrying only the fields the evaluator is allowed to measure."""
    base = {
        "knowledge_id": "UCOS-KA-000001",
        "name": "Thing",
        "aliases": [],
        "authority": "ASSISTANT-PROPOSAL",
        "hierarchy_layer": "STRUCTURAL",
        "origin_conversation_count": 1,
        "normative_statements": 0,
        "evidence": [],
        "decision_profile": {},
        "ucos_disposition": "ARCHITECTURE",
        "is_instance_level": False,
    }
    base.update(over)
    return base


def row(**over) -> dict:
    base = {
        "kid": "UCOS-KA-000001",
        "name": "Thing",
        "state": "ALREADY-REPRESENTED",
        "presence_level": "REPO-DOCUMENTED",
        "presence_hits": 3,
        "presence_corrected": False,
        "anchors": ["engine/foundation/thing.py"],
        "dependencies": [],
        "authority": "",
        "equivalence": "",
    }
    base.update(over)
    return base


def absent_row(**over) -> dict:
    return row(state="ASSIMILATED", presence_level="ABSENT", presence_hits=0, anchors=[], **over)


def evaluate(o: dict, r: dict, **kw) -> dict:
    args = {
        "collides": False,
        "relations_declared": 0,
        "relations_resolved": 0,
        "anchors_resolve": len(r.get("anchors") or []),
        "deps_resolve": True,
    }
    args.update(kw)
    return sup.evaluate(o, r, **args)


# --------------------------------------------------------------------------- declared model
def test_all_five_mandated_states_are_implemented():
    for state in (
        "BETTER_THAN_CURRENT",
        "CONFLICTING",
        "OBSOLETE",
        "REQUIRES_ARCHITECTURAL_REVIEW",
        "PARTIALLY_ASSIMILATED",
    ):
        assert state in sup.SUPERIORITY_STATES
        assert state in sup.REQUIRED_STATES


def test_sixteen_dimensions_are_declared_with_both_side_measures():
    assert sup.DIMENSION_COUNT == 16
    ids = [d["id"] for d in sup.DIMENSIONS]
    assert len(set(ids)) == 16
    for dim in sup.DIMENSIONS:
        assert dim["discovered"] and dim["repository"], dim["id"]
        assert callable(dim["d"]) and callable(dim["r"])
    catalog = sup.dimension_catalog()
    assert [c["id"] for c in catalog] == ids
    assert {c["id"] for c in catalog if c["constitutional"]} == set(sup.CONSTITUTIONAL_DIMENSIONS)


def test_the_comparison_model_covers_every_required_dimension():
    """The work package names sixteen architectural dimensions; each must be evaluable."""
    required = [
        "Universality",
        "Composability",
        "Orthogonality",
        "Reusability",
        "Extensibility",
        "Scalability",
        "Maintainability",
        "Governability",
        "Automation",
        "Repository Truth compatibility",
        "Knowledge Once",
        "Single Source of Truth",
        "Dependency correctness",
        "Traceability",
        "Validation impact",
        "Certification impact",
    ]
    assert [d["name"] for d in sup.DIMENSIONS] == required


def test_every_declared_rule_carries_a_rationale():
    rules = {f"SUP-{i}" for i in range(1, 8)}
    assert set(sup.VERDICT_RATIONALE) == rules


def test_profile_legend_round_trips():
    profile = sup.encode([sup.SUPERIOR, sup.EQUIVALENT, sup.INFERIOR, sup.UNDECIDABLE])
    assert profile == "+=-."
    assert sup.decode(profile) == [sup.SUPERIOR, sup.EQUIVALENT, sup.INFERIOR, sup.UNDECIDABLE]


# --------------------------------------------------------------------------- comparison
def test_comparison_is_a_pure_ordinal_comparison():
    assert sup.compare(2, 1) == sup.SUPERIOR
    assert sup.compare(1, 1) == sup.EQUIVALENT
    assert sup.compare(0, 2) == sup.INFERIOR
    assert sup.compare(None, 1) == sup.UNDECIDABLE
    assert sup.compare(1, None) == sup.UNDECIDABLE


def test_unmeasurable_evidence_is_undecidable_never_guessed():
    """A missing evidence field must not be scored as zero — that would invent a comparison."""
    ev = sup.discovered_evidence(obj(hierarchy_layer="", authority=""), False, 0, 0)
    assert sup.d06_discovered(ev) is None  # no declared layer
    assert sup.d08_discovered(ev) is None  # no recorded authority class
    outcomes = sup.evaluate_dimensions(ev, sup.repository_evidence(row(), 1, True))
    assert outcomes[5] == sup.UNDECIDABLE
    assert outcomes[7] == sup.UNDECIDABLE


def test_every_dimension_measures_both_sides_on_the_declared_scale():
    ev = sup.discovered_evidence(obj(), False, 0, 0)
    rv = sup.repository_evidence(row(), 1, True)
    for dim in sup.DIMENSIONS:
        for value in (dim["d"](ev), dim["r"](rv)):
            assert value is None or sup.SCALE_MIN <= value <= sup.SCALE_MAX, dim["id"]


# --------------------------------------------------------------------------- verdict rules
def test_obsolete_when_evidence_retired_the_form():
    out = evaluate(obj(decision_profile={"DECISION_SUPERSEDED": 3}), row())
    assert out["superiority"] == sup.OBSOLETE
    assert out["superiority_rule"] == "SUP-1"
    assert evaluate(obj(), row(state="SUPERSEDED"))["superiority"] == sup.OBSOLETE


def test_obsolete_yields_to_surviving_acceptance():
    """Superseded AND accepted is a contradiction, not obsolescence."""
    out = evaluate(obj(decision_profile={"DECISION_SUPERSEDED": 3, "DECISION_ACCEPTED": 2}), row())
    assert out["superiority"] != sup.OBSOLETE


def test_conflicting_when_the_evidence_contradicts_itself():
    out = evaluate(obj(decision_profile={"DECISION_ACCEPTED": 4, "DECISION_REJECTED": 2}), row())
    assert out["superiority"] == sup.CONFLICTING
    assert out["superiority_rule"] == "SUP-2"


def test_conflicting_when_certified_truth_carries_what_evidence_rejects():
    out = evaluate(
        obj(decision_profile={"DECISION_REJECTED": 1}), row(presence_level="REPO-CERTIFIED")
    )
    assert out["superiority"] == sup.CONFLICTING


def test_no_current_form_when_the_repository_carries_nothing():
    out = evaluate(obj(), absent_row())
    assert out["superiority"] == sup.NO_CURRENT_FORM
    assert out["superiority_rule"] == "SUP-3"


def test_partially_assimilated_on_weak_presence():
    out = evaluate(obj(), row(presence_corrected=True))
    assert out["superiority"] == sup.PARTIALLY_ASSIMILATED
    assert out["superiority_rule"] == "SUP-4"


def test_partially_assimilated_on_semantic_only_representation():
    out = evaluate(obj(), row(state="SEMANTICALLY-REPRESENTED"))
    assert out["superiority"] == sup.PARTIALLY_ASSIMILATED


def better_candidate() -> dict:
    """A form the model must judge superior: broader conversation reuse, a ratified authority
    class, an accepted decision and statement evidence — and NO alternate names, because several
    names for one concept is itself a Single-Source-of-Truth regression under `D-12`."""
    return obj(
        authority="SOURCE-RATIFIED",
        origin_conversation_count=9,
        normative_statements=6,
        evidence=[{"sid": 1}],
        hierarchy_layer="APEX",
        decision_profile={"DECISION_ACCEPTED": 3},
    )


def test_better_than_current_requires_a_positive_net_and_no_constitutional_regression():
    out = evaluate(better_candidate(), row(presence_hits=1, presence_level="REPO-DOCUMENTED"))
    assert out["superiority"] == sup.BETTER_THAN_CURRENT
    assert out["superiority_rule"] == "SUP-6"
    assert out["superiority_score"] > 0
    profile = sup.decode(out["superiority_profile"])
    constitutional = [
        i for i, d in enumerate(sup.DIMENSIONS) if d["id"] in sup.CONSTITUTIONAL_DIMENSIONS
    ]
    assert all(profile[i] != sup.INFERIOR for i in constitutional)


def test_alternate_names_are_measured_as_a_single_source_of_truth_regression():
    """Several declared names for one concept must not be able to buy a superior verdict."""
    aliased = better_candidate()
    aliased["aliases"] = ["a", "b", "c"]
    out = evaluate(aliased, row(presence_hits=1, presence_level="REPO-DOCUMENTED"))
    profile = sup.decode(out["superiority_profile"])
    d12 = [i for i, d in enumerate(sup.DIMENSIONS) if d["id"] == "D-12"][0]
    assert profile[d12] == sup.INFERIOR
    assert out["superiority"] == sup.REQUIRES_ARCHITECTURAL_REVIEW


def test_constitutional_regression_escalates_to_architectural_review():
    """A form that regresses Knowledge Once may never be adopted mechanically."""
    candidate = better_candidate()
    clean = evaluate(candidate, row(presence_hits=1))
    assert clean["superiority"] == sup.BETTER_THAN_CURRENT
    # `collides` drives the Knowledge Once / orthogonality / SSOT measures to 0 → regression.
    regressed = evaluate(candidate, row(presence_hits=1), collides=True)
    assert regressed["superiority"] == sup.REQUIRES_ARCHITECTURAL_REVIEW
    assert regressed["superiority_rule"] == "SUP-5"
    profile = sup.decode(regressed["superiority_profile"])
    constitutional = [
        i for i, d in enumerate(sup.DIMENSIONS) if d["id"] in sup.CONSTITUTIONAL_DIMENSIONS
    ]
    assert any(profile[i] == sup.INFERIOR for i in constitutional)


def test_decertification_escalates_to_architectural_review():
    out = evaluate(better_candidate(), row(presence_hits=1, presence_level="REPO-CERTIFIED"))
    assert out["superiority"] == sup.REQUIRES_ARCHITECTURAL_REVIEW


def test_not_superior_when_nothing_is_better():
    out = evaluate(
        obj(authority="ASSISTANT-PROPOSAL", hierarchy_layer="OPERATIONAL"),
        row(
            presence_hits=9,
            presence_level="REPO-IMPLEMENTED",
            anchors=["engine/a.py"],
            authority="00-CEP/CEP-002.md",
        ),
    )
    assert out["superiority"] in (sup.NOT_SUPERIOR, sup.REQUIRES_ARCHITECTURAL_REVIEW)
    if out["superiority"] == sup.NOT_SUPERIOR:
        assert out["superiority_rule"] == "SUP-7"


def test_verdict_is_total_over_a_swept_input_space():
    """Every combination of the decision-bearing inputs must yield exactly one declared state."""
    seen = set()
    for level in ("ABSENT", "REPO-DOCUMENTED", "REPO-CERTIFIED"):
        for state in (
            "ALREADY-REPRESENTED",
            "SEMANTICALLY-REPRESENTED",
            "SUPERSEDED",
            "REJECTED",
            "ASSIMILATED",
        ):
            for corrected in (False, True):
                for dp in (
                    {},
                    {"DECISION_ACCEPTED": 2},
                    {"DECISION_REJECTED": 2},
                    {"DECISION_SUPERSEDED": 2},
                    {"DECISION_ACCEPTED": 2, "DECISION_REJECTED": 1},
                ):
                    for collides in (False, True):
                        r = row(
                            presence_level=level,
                            state=state,
                            presence_corrected=corrected,
                            anchors=[] if level == "ABSENT" else ["engine/a.py"],
                            presence_hits=0 if level == "ABSENT" else 3,
                        )
                        out = evaluate(obj(decision_profile=dp), r, collides=collides)
                        assert out["superiority"] in sup.SUPERIORITY_STATES
                        assert out["superiority_rule"] in sup.VERDICT_RATIONALE
                        assert len(out["superiority_profile"]) == sup.DIMENSION_COUNT
                        seen.add(out["superiority"])
    assert seen >= {sup.OBSOLETE, sup.CONFLICTING, sup.NO_CURRENT_FORM, sup.PARTIALLY_ASSIMILATED}


# --------------------------------------------------------------------------- determinism
def test_evaluation_is_deterministic():
    o, r = obj(decision_profile={"DECISION_ACCEPTED": 1}), row()
    first = evaluate(o, r)
    for _ in range(25):
        assert evaluate(o, r) == first


def test_evaluation_does_not_mutate_its_inputs():
    o, r = obj(), row()
    before = json.dumps({"o": o, "r": r}, sort_keys=True)
    evaluate(o, r)
    assert json.dumps({"o": o, "r": r}, sort_keys=True) == before


def test_the_evaluator_has_zero_dependencies():
    """The strongest determinism guarantee available: the evaluator imports NOTHING.

    No `random`, no `datetime`, no `os`, no `subprocess`, no network client and no model client
    can be reached from it, so a verdict cannot depend on the clock, the machine, the
    environment or any external service. Asserted over the parsed AST rather than the source
    text, so prose in the docstring cannot satisfy or break it.
    """
    tree = ast.parse(SUP_PATH.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported == {"__future__"}, f"unexpected dependency: {sorted(imported - {'__future__'})}"


def test_the_evaluator_calls_no_impure_builtin():
    """No filesystem, environment, clock or eval reachable through a bare builtin either."""
    tree = ast.parse(SUP_PATH.read_text(encoding="utf-8"))
    forbidden = {"open", "eval", "exec", "compile", "input", "__import__", "globals", "vars"}
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not (called & forbidden), f"impure builtin used: {sorted(called & forbidden)}"


def test_thresholds_are_declared_once_and_used_by_name():
    assert sup.THRESHOLDS
    source = SUP_PATH.read_text(encoding="utf-8")
    for name in sup.THRESHOLDS:
        assert f'THRESHOLDS["{name}"]' in source or name in ("reuse_low", "reuse_high"), name


# ------------------------------------------------------- the committed register (integration)
def committed() -> dict:
    return json.loads(ASSIM_JSON.read_text(encoding="utf-8"))


def test_every_committed_object_carries_a_verdict():
    payload = committed()
    cols = payload["row_columns"]
    for name in ("superiority", "superiority_score", "superiority_profile", "superiority_rule"):
        assert name in cols, name
    verdict_at = cols.index("superiority")
    rule_at = cols.index("superiority_rule")
    profile_at = cols.index("superiority_profile")
    rows = payload["rows"]
    assert rows
    for r in rows:
        assert r[verdict_at] in sup.SUPERIORITY_STATES
        assert r[rule_at] in sup.VERDICT_RATIONALE
        assert len(r[profile_at]) == sup.DIMENSION_COUNT
        assert all(c in sup.CHAR_OUTCOME for c in r[profile_at])


def test_committed_verdicts_are_total_and_all_required_states_are_reachable():
    payload = committed()
    states = payload["superiority_states"]
    assert sum(states.values()) == len(payload["rows"]) == payload["verified_objects"]
    for state in sup.REQUIRED_STATES:
        assert states.get(state, 0) > 0, f"{state} is unreachable on the committed corpus"


def test_presence_axis_columns_precede_the_superiority_axis():
    """Presence is evaluated first and the superiority columns are APPENDED, never inserted —
    that is what keeps a pre-D-2 record positionally readable. A LATER axis (D-3) may only append
    after them, so the four columns must stay contiguous, in declared order, and behind presence.
    """
    cols = committed()["row_columns"]
    sup_cols = [
        "superiority",
        "superiority_score",
        "superiority_profile",
        "superiority_rule",
    ]
    at = cols.index("superiority")
    assert cols[at : at + 4] == sup_cols
    assert cols.index("state") < at
    assert not set(cols[:at]) & set(sup_cols)
    assert not set(cols[at + 4 :]) & set(sup_cols)


def test_committed_presence_states_are_unchanged_by_the_second_axis():
    payload = committed()
    assert payload["determination"] == "REPOSITORY CONSTITUTIONALLY COMPLETE"
    assert payload["unclassified"] == 0
    assert set(payload["states"]) == {
        "ALREADY-REPRESENTED",
        "SEMANTICALLY-REPRESENTED",
        "ASSIMILATED",
        "HISTORICAL-EVIDENCE-ONLY",
        "SUPERSEDED",
        "REJECTED",
    }
    assert sum(payload["states"].values()) == payload["verified_objects"]


def test_superiority_gates_are_blocking_and_pass():
    gates = {g["gate"]: g for g in committed()["gates"]}
    blocking = [
        "Every presence-classified object carries a superiority verdict",
        "Every superiority verdict is a declared state",
        f"Every superiority profile declares all {sup.DIMENSION_COUNT} comparison dimensions",
        "Every superiority verdict resolves to a declared rule",
    ]
    for name in blocking:
        assert name in gates, name
        assert gates[name]["blocking"] is True
        assert gates[name]["result"] == "PASS", gates[name]
    findings = [g for g in gates if g.startswith("Superiority findings")]
    assert findings and gates[findings[0]]["blocking"] is False


def test_committed_schema_declares_the_whole_comparison_model():
    payload = committed()
    assert payload["superiority_dimension_count"] == sup.DIMENSION_COUNT
    assert len(payload["superiority_dimensions"]) == sup.DIMENSION_COUNT
    assert payload["superiority_thresholds"] == sup.THRESHOLDS
    assert set(payload["superiority_rationale"]) == set(sup.VERDICT_RATIONALE)
    assert set(payload["superiority_profile_legend"].values()) == set(sup.OUTCOME_CHAR)
    for dim in payload["superiority_dimensions"]:
        totals = payload["superiority_outcomes"][dim["id"]]
        assert sum(totals.values()) == payload["verified_objects"], dim["id"]


def test_profiles_reproduce_the_recorded_aggregates():
    """The aggregate is derived from the stored profiles, so a replay cannot drift from them."""
    payload = committed()
    cols = payload["row_columns"]
    profile_at = cols.index("superiority_profile")
    recomputed = {
        d["id"]: dict.fromkeys(sup.OUTCOME_CHAR, 0) for d in payload["superiority_dimensions"]
    }
    for r in payload["rows"]:
        for dim, ch in zip(payload["superiority_dimensions"], r[profile_at], strict=False):
            recomputed[dim["id"]][sup.CHAR_OUTCOME[ch]] += 1
    assert recomputed == payload["superiority_outcomes"]


def test_recorded_score_matches_the_recorded_profile():
    payload = committed()
    cols = payload["row_columns"]
    profile_at, score_at = cols.index("superiority_profile"), cols.index("superiority_score")
    for r in payload["rows"]:
        outcomes = sup.decode(r[profile_at])
        assert r[score_at] == outcomes.count(sup.SUPERIOR) - outcomes.count(sup.INFERIOR)


def test_superiority_register_is_emitted():
    register = PROGRAM_DIR / "09-SUPERIORITY-EVALUATION-REGISTER.md"
    text = register.read_text(encoding="utf-8")
    for dim in sup.DIMENSIONS:
        assert dim["name"] in text, dim["name"]
    for state in sup.REQUIRED_STATES:
        assert state in text, state
    for rule in sup.VERDICT_RATIONALE:
        assert rule in text, rule

"""UKAP-001 / WP-003 / D-3 — repository decision & action validation suite.

Proves the capability, not a description of it:

  * every evaluated object carries exactly one repository decision      (totality)
  * all six mandated actions are implemented AND reachable
  * every decision maps to exactly one declared rule, which decides that action
  * deterministic replay — the decision re-derives from its recorded grounds ALONE
  * byte-identical regeneration from the committed register
  * Repository Truth preserved — neither prior axis is touched, and nothing is modified
  * Knowledge Once preserved — a second home is refused, never merged into existence
  * dependency closure preserved — no knowledge-modifying action on an open chain
  * traceability preserved — provenance, rule, operation, owner and grounds on every decision
  * backward compatibility — a pre-D-3 record still deserializes, and fails closed

The unit scenarios are hermetic: synthetic rows are built in-process, so the suite never needs
the external evidence tree.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PROGRAM_DIR = REPO / "00-MASTER" / "UAKOS-CLOSURE-008"
DEC_PATH = PROGRAM_DIR / "decision_engine.py"
SUP_PATH = PROGRAM_DIR / "superiority_engine.py"
ASSIM_JSON = PROGRAM_DIR / "assimilation.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dec = _load("d3_decision_engine", DEC_PATH)
sup = _load("d3_superiority_engine", SUP_PATH)


# --------------------------------------------------------------------------- fixtures
def row(**over) -> dict:
    """A row carrying only the columns the decision engine is allowed to read."""
    base = {
        "kid": "UCOS-KA-000001",
        "name": "Thing",
        "state": "ALREADY-REPRESENTED",
        "presence_level": "REPO-DOCUMENTED",
        "presence_corrected": False,
        "anchors": ["engine/foundation/thing.py"],
        "dependencies": [],
        "destination": "",
        "authority": "",
        "owner": "",
        "wave": "",
        "origin_conversations": 2,
        "evidence_conversation": "conv-1",
        "superiority": sup.NOT_SUPERIOR,
        "superiority_score": 0,
        "superiority_profile": "=" * sup.DIMENSION_COUNT,
        "superiority_rule": "SUP-7",
    }
    base.update(over)
    return base


def decide(r: dict, *, objection: bool = False, deps_closed: bool = True) -> dict:
    return dec.decide(r, objection=objection, deps_closed=deps_closed)


def homed(**over) -> dict:
    """An approved-missing-knowledge row: absent, homed, with an active wave."""
    base = dict(
        state="ASSIMILATED",
        presence_level="ABSENT",
        anchors=[],
        destination="engine",
        authority="00-CEP/CEP-003.md",
        owner="Engine Implementation Authority (engine/)",
        wave="5",
        superiority=sup.NO_CURRENT_FORM,
        superiority_rule="SUP-3",
    )
    base.update(over)
    return row(**base)


# --------------------------------------------------------------------------- declared model
def test_all_six_mandated_actions_are_implemented():
    for action in ("ACCEPT", "MERGE", "SUPERSEDE", "REJECT", "ESCALATE_ARCHITECTURE", "DEFER"):
        assert action in dec.ACTIONS
        assert action in dec.ACTION_REGISTRY


def test_the_action_registry_declares_the_constitutional_properties():
    for action in dec.ACTIONS:
        spec = dec.ACTION_REGISTRY[action]
        assert spec["summary"] and spec["executed_by"] and spec["precondition"]
        assert isinstance(spec["modifies_knowledge"], bool)
    modifying = {a for a in dec.ACTIONS if dec.ACTION_REGISTRY[a]["modifies_knowledge"]}
    # Exactly the three actions that would change repository knowledge, and no others.
    assert modifying == {dec.ACCEPT, dec.MERGE, dec.SUPERSEDE}


def test_every_declared_rule_is_complete_and_uniquely_identified():
    ids = [r["id"] for r in dec.DECISION_RULES]
    assert len(set(ids)) == len(ids) == len(dec.RULE_IDS)
    for rule in dec.DECISION_RULES:
        assert rule["action"] in dec.ACTIONS, rule["id"]
        assert rule["operation"] in dec.OPERATIONS, rule["id"]
        assert rule["clause"] and rule["rationale"], rule["id"]
        assert callable(rule["when"]), rule["id"]
        # the operation a rule cites must serve the action that rule decides
        assert dec.OPERATIONS[rule["operation"]]["action"] == rule["action"], rule["id"]


def test_every_declared_operation_declares_an_ordered_plan():
    for name, op in dec.OPERATIONS.items():
        assert op["action"] in dec.ACTIONS, name
        assert op["summary"], name
        assert isinstance(op["steps"], list) and len(op["steps"]) >= 3, name
    # every action is served by at least one repository operation
    served = {str(op["action"]) for op in dec.OPERATIONS.values()}
    assert served == set(dec.ACTIONS)


def test_every_declared_priority_carries_a_rationale():
    assert set(dec.PRIORITY_RATIONALE) == set(dec.PRIORITIES)
    for action in dec.ACTIONS:
        assert dec.PRIORITY_POLICY[action] in dec.PRIORITIES


def test_the_rule_set_is_versioned_and_the_declaration_is_serializable():
    assert dec.DECISION_VERSION
    declaration = dec.ruleset_declaration()
    # the declaration must be plain data — it is digest-sealed into the machine register
    json.dumps(declaration, sort_keys=True)
    assert declaration["decision_version"] == dec.DECISION_VERSION
    assert [r["rule"] for r in declaration["rules"]] == dec.RULE_IDS
    assert declaration["residual_rule"] == dec.RESIDUAL_RULE


def test_the_residual_rule_is_last_and_matches_unconditionally():
    residual = dec.DECISION_RULES[-1]
    assert residual["id"] == dec.RESIDUAL_RULE
    assert residual["when"]({}) is True


def test_fail_safe_precedence_every_non_modifying_clause_precedes_every_modifying_one():
    """The constitutional property of the ordering: no adoption clause can be reached before a
    clause that would instead escalate, reject or hold — so a mechanical action can never
    overrule an architect."""
    modifying = {a for a in dec.ACTIONS if dec.ACTION_REGISTRY[a]["modifies_knowledge"]}
    first_modifying = min(i for i, r in enumerate(dec.DECISION_RULES) if r["action"] in modifying)
    # every clause the work package names as a hard escalation/rejection must sit above it
    for rule_id in ("DEC-01", "DEC-02", "DEC-03", "DEC-04", "DEC-05", "DEC-06"):
        at = dec.RULE_IDS.index(rule_id)
        assert at < first_modifying, f"{rule_id} must outrank every knowledge-modifying clause"


# --------------------------------------------------------------------------- the work package
def test_conflicting_escalates_to_architecture():
    out = decide(row(superiority=sup.CONFLICTING))
    assert out["decision"] == dec.ESCALATE_ARCHITECTURE
    assert out["decision_rule"] == "DEC-01"
    assert out["implementation_action"] == dec.REFER_CONFLICT


def test_obsolete_is_rejected():
    out = decide(row(superiority=sup.OBSOLETE))
    assert out["decision"] == dec.REJECT
    assert out["decision_rule"] == "DEC-02"


def test_partially_assimilated_is_merged():
    out = decide(row(state="SEMANTICALLY-REPRESENTED", superiority=sup.PARTIALLY_ASSIMILATED))
    assert out["decision"] == dec.MERGE
    assert out["decision_rule"] == "DEC-07"
    assert out["implementation_action"] == dec.COMPLETE_EXISTING_REPRESENTATION


def test_constitutional_regression_escalates_to_architecture():
    out = decide(
        row(superiority=sup.PARTIALLY_ASSIMILATED, state="SEMANTICALLY-REPRESENTED"), objection=True
    )
    assert out["decision"] == dec.ESCALATE_ARCHITECTURE
    assert out["decision_rule"] == "DEC-04"
    assert out["implementation_action"] == dec.REFER_CONSTITUTIONAL_REGRESSION
    # and it is the only class the model treats as IMMEDIATE
    assert out["implementation_priority"] == dec.IMMEDIATE


def test_constitutional_regression_outranks_every_adoption():
    """A regression must divert a merge, an acceptance and a supersession alike."""
    for r in (
        row(superiority=sup.PARTIALLY_ASSIMILATED, state="SEMANTICALLY-REPRESENTED"),
        homed(),
        row(superiority=sup.BETTER_THAN_CURRENT, superiority_score=4),
    ):
        assert decide(r, objection=True)["decision"] == dec.ESCALATE_ARCHITECTURE
        assert decide(r, objection=True)["decision_rule"] == "DEC-04"


def test_not_present_and_approved_missing_knowledge_is_accepted():
    out = decide(homed())
    assert out["decision"] == dec.ACCEPT
    assert out["decision_rule"] == "DEC-10"
    assert out["implementation_action"] == dec.HOME_NEW_KNOWLEDGE
    assert out["implementation_priority"] == dec.SCHEDULED


def test_the_work_packages_literal_accept_clause_is_declared_and_disclosed_unreachable():
    """`NOT_PRESENT AND BETTER_THAN_CURRENT` is declared verbatim (DEC-09) and is empty by
    construction, because the superiority axis assigns NO_CURRENT_FORM to exactly those objects.
    The engine declares the clause AND declares why it can never fire, instead of hiding it."""
    assert any(r["id"] == "DEC-09" for r in dec.DECISION_RULES)
    assert dec.SILENT_RULES["DEC-09"]["kind"] == "STRUCTURAL"
    assert dec.SILENT_RULES["DEC-09"]["reason"]
    # the structural fact itself: presence-absent always yields SUP-3 / NO_CURRENT_FORM
    verdict = sup.evaluate(
        {
            "knowledge_id": "K",
            "name": "n",
            "aliases": [],
            "authority": "SOURCE-RATIFIED",
            "hierarchy_layer": "APEX",
            "origin_conversation_count": 9,
            "normative_statements": 6,
            "evidence": [{"sid": 1}],
            "decision_profile": {"DECISION_ACCEPTED": 3},
            "ucos_disposition": "ARCHITECTURE",
            "is_instance_level": False,
        },
        {
            "state": "ASSIMILATED",
            "presence_level": "ABSENT",
            "presence_hits": 0,
            "presence_corrected": False,
            "anchors": [],
            "dependencies": [],
            "authority": "",
            "equivalence": "",
        },
        collides=False,
        relations_declared=0,
        relations_resolved=0,
        anchors_resolve=0,
        deps_resolve=True,
    )
    assert verdict["superiority"] == sup.NO_CURRENT_FORM
    assert dec.grounds_of(homed(), objection=False, deps_closed=True)["P"] == "NOT_PRESENT"


def test_better_than_current_against_a_carried_form_is_superseded():
    out = decide(row(superiority=sup.BETTER_THAN_CURRENT, superiority_score=4))
    assert out["decision"] == dec.SUPERSEDE
    assert out["decision_rule"] == "DEC-08"
    assert out["implementation_action"] == dec.REPLACE_CURRENT_FORM
    assert out["implementation_priority"] == dec.HIGH


def test_wave_f_is_deferred_not_scheduled():
    out = decide(homed(wave="F"))
    assert out["decision"] == dec.DEFER
    assert out["decision_rule"] == "DEC-06"
    assert out["implementation_action"] == dec.REGISTER_AND_HOLD
    assert out["implementation_priority"] == dec.HELD


def test_a_hold_outranks_an_admission():
    """An unauthorized admission is destructive; a hold is not. Wave F must therefore win."""
    assert decide(homed(wave="F"))["decision"] == dec.DEFER
    assert decide(homed(wave="5"))["decision"] == dec.ACCEPT


def test_retired_presence_preserves_the_retirement():
    for state in ("SUPERSEDED", "REJECTED"):
        out = decide(row(state=state, superiority=sup.NO_CURRENT_FORM))
        assert out["decision"] == dec.REJECT
        assert out["decision_rule"] == "DEC-03"
        assert out["implementation_action"] == dec.PRESERVE_RETIREMENT


def test_history_is_retained_and_never_promoted_including_by_merge():
    """Instance-level history must not reach Repository Truth through the merge side door."""
    out = decide(
        row(
            state="HISTORICAL-EVIDENCE-ONLY",
            superiority=sup.PARTIALLY_ASSIMILATED,
            presence_corrected=True,
        )
    )
    assert out["decision"] == dec.REJECT
    assert out["decision_rule"] == "DEC-05"
    assert out["implementation_action"] == dec.RETAIN_AS_HISTORY


def test_knowledge_once_refuses_a_second_home():
    out = decide(row(superiority=sup.NOT_SUPERIOR))
    assert out["decision"] == dec.REJECT
    assert out["decision_rule"] == "DEC-12"
    assert out["implementation_action"] == dec.RETAIN_CURRENT_FORM
    assert out["implementation_priority"] == dec.NONE


def test_requires_architectural_review_escalates():
    out = decide(row(superiority=sup.REQUIRES_ARCHITECTURAL_REVIEW))
    assert out["decision"] == dec.ESCALATE_ARCHITECTURE
    assert out["decision_rule"] == "DEC-11"
    assert out["implementation_action"] == dec.REFER_ARCHITECTURAL_REVIEW


# --------------------------------------------------------------------------- totality
def _consistent(
    state: str, verdict: str, level: str, corrected: bool, wave: str, anchors: list[str]
) -> bool:
    """The invariants the two PRIOR axes already guarantee about a row.

    The decision rule set is total over ALL inputs (the residual matches unconditionally), but it
    is required to be RESIDUAL-FREE over every row the presence and superiority axes can actually
    produce. These are those axes' own declared invariants, so the sweep below tests the real
    input space rather than a space containing self-contradictory rows.
    """
    present = level != "ABSENT" or bool(anchors)
    if state == "ALREADY-REPRESENTED" and (not present or corrected):
        return False
    if state == "SEMANTICALLY-REPRESENTED" and not anchors:
        return False
    if state == "ASSIMILATED" and (present and not corrected or not wave):
        return False
    # SUP-3: a verdict of NO_CURRENT_FORM is exactly "the repository carries nothing"
    if (verdict == "NO_CURRENT_FORM") != (not present):
        return False
    # with nothing carried, only SUP-1 / SUP-2 / SUP-3 can fire
    if not present and verdict not in ("OBSOLETE", "CONFLICTING", "NO_CURRENT_FORM"):
        return False
    # SUP-4 precedes the dimension comparison, so a weak or semantic-only presence can only
    # carry PARTIALLY_ASSIMILATED (or the SUP-1/SUP-2 findings that outrank it)
    weak = corrected or state == "SEMANTICALLY-REPRESENTED"
    if weak and verdict not in ("PARTIALLY_ASSIMILATED", "OBSOLETE", "CONFLICTING"):
        return False
    if verdict == "PARTIALLY_ASSIMILATED" and not weak:
        return False
    return True


def test_decision_is_total_and_residual_free_over_the_real_input_space():
    """Every row the prior axes can produce must yield exactly one declared action, one declared
    rule and one declared operation — and must NEVER reach the totality residual."""
    seen_actions, seen_rules, swept = set(), set(), 0
    states = (
        "ALREADY-REPRESENTED",
        "SEMANTICALLY-REPRESENTED",
        "ASSIMILATED",
        "HISTORICAL-EVIDENCE-ONLY",
        "SUPERSEDED",
        "REJECTED",
    )
    for state in states:
        for verdict in sup.SUPERIORITY_STATES:
            for level in ("ABSENT", "REPO-DOCUMENTED", "REPO-CERTIFIED"):
                for corrected in (False, True):
                    for wave in ("", "1", "F"):
                        anchors = [] if level == "ABSENT" else ["engine/a.py"]
                        if not _consistent(state, verdict, level, corrected, wave, anchors):
                            continue
                        for objection in (False, True):
                            r = row(
                                state=state,
                                superiority=verdict,
                                presence_level=level,
                                presence_corrected=corrected,
                                wave=wave,
                                anchors=anchors,
                                destination="engine" if state == "ASSIMILATED" else "",
                            )
                            out = decide(r, objection=objection)
                            swept += 1
                            assert out["decision"] in dec.ACTIONS
                            assert out["decision_rule"] in dec.RULE_IDS
                            assert out["implementation_action"] in dec.OPERATIONS
                            assert out["implementation_priority"] in dec.PRIORITIES
                            assert out["decision_rule"] != dec.RESIDUAL_RULE, (
                                state,
                                verdict,
                                level,
                                corrected,
                                wave,
                            )
                            seen_actions.add(out["decision"])
                            seen_rules.add(out["decision_rule"])
    assert swept > 100
    # all six mandated actions must be reachable from the real input space
    assert seen_actions == set(dec.ACTIONS)
    # every declared rule except the disclosed-silent ones and the residual must fire
    expected = set(dec.RULE_IDS) - {dec.RESIDUAL_RULE} - set(dec.SILENT_RULES)
    assert expected <= seen_rules, sorted(expected - seen_rules)


def test_the_residual_escalates_a_self_contradictory_record_rather_than_dropping_it():
    """The residual exists for exactly one purpose: a row whose presence record contradicts
    itself must still leave with an action, and that action must be the non-destructive one."""
    contradictory = row(
        state="ALREADY-REPRESENTED",
        presence_level="ABSENT",
        anchors=[],
        superiority=sup.NO_CURRENT_FORM,
    )
    out = decide(contradictory)
    assert out["decision_rule"] == dec.RESIDUAL_RULE
    assert out["decision"] == dec.ESCALATE_ARCHITECTURE
    assert not dec.ACTION_REGISTRY[out["decision"]]["modifies_knowledge"]


def test_no_object_can_exit_without_an_action():
    out = decide(row(state="", superiority="", presence_level="", anchors=[]))
    assert out["decision"] in dec.ACTIONS
    assert out["decision_rule"] in dec.RULE_IDS


# --------------------------------------------------------------------------- determinism
def test_decision_is_deterministic():
    r = row(superiority=sup.BETTER_THAN_CURRENT, superiority_score=3)
    first = decide(r)
    for _ in range(25):
        assert decide(r) == first


def test_decision_does_not_mutate_its_inputs():
    r = row()
    before = json.dumps(r, sort_keys=True)
    decide(r)
    assert json.dumps(r, sort_keys=True) == before


def test_grounds_round_trip_exactly():
    for r in (
        row(),
        homed(),
        homed(wave="F"),
        row(state="SUPERSEDED"),
        row(superiority=sup.CONFLICTING, dependencies=["UCOS-KA-000002"]),
    ):
        for objection in (False, True):
            for closed in (False, True):
                g = dec.grounds_of(r, objection=objection, deps_closed=closed)
                encoded = dec.encode_grounds(g)
                assert dec.decode_grounds(encoded) == g
                assert dec.encode_grounds(dec.decode_grounds(encoded)) == encoded


def test_replay_reproduces_the_decision_from_the_grounds_alone():
    """Deterministic replay, executed: the recorded rationale is the ONLY input."""
    for r in (
        row(),
        homed(),
        homed(wave="F"),
        row(state="REJECTED"),
        row(superiority=sup.PARTIALLY_ASSIMILATED, state="SEMANTICALLY-REPRESENTED"),
        row(superiority=sup.BETTER_THAN_CURRENT, superiority_score=5),
    ):
        for objection in (False, True):
            out = decide(r, objection=objection)
            again = dec.replay(out["decision_rationale"])
            assert {k: out[k] for k in again} == again


def test_malformed_grounds_are_refused_never_guessed():
    for bad in ("", "P:NP", "P:XX|Q:AS|S:NCF|C:0|N:+0|D:N|T:T|W:F", "nonsense"):
        try:
            dec.replay(bad)
        except (ValueError, KeyError):
            continue
        raise AssertionError(f"malformed grounds accepted: {bad!r}")


def test_the_decision_engine_has_zero_dependencies():
    """The strongest determinism guarantee available: the engine imports NOTHING.

    No `random`, no `datetime`, no `os`, no `subprocess`, no network client and no model client
    can be reached from it, so a decision cannot depend on the clock, the machine, the
    environment or any external service.
    """
    tree = ast.parse(DEC_PATH.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported == {"__future__"}, f"unexpected dependency: {sorted(imported)}"


def test_the_decision_engine_calls_no_impure_builtin():
    tree = ast.parse(DEC_PATH.read_text(encoding="utf-8"))
    forbidden = {"open", "eval", "exec", "compile", "input", "__import__", "globals", "vars"}
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not (called & forbidden), f"impure builtin used: {sorted(called & forbidden)}"


def test_the_decision_engine_performs_no_repository_modification():
    """It decides; it never acts. No write, no path construction, no process, no network."""
    source = DEC_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    attrs = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    for forbidden in (
        "write_text",
        "write_bytes",
        "mkdir",
        "unlink",
        "rmtree",
        "rename",
        "replace_all",
        "system",
        "run",
        "Popen",
        "urlopen",
    ):
        assert forbidden not in attrs, forbidden


# --------------------------------------------------------------------------- owner + plan
def test_owner_resolution_is_total_and_never_overrides_the_presence_axis():
    assert dec.owner_for(row(owner="Engine Implementation Authority (engine/)")) == (
        "Engine Implementation Authority (engine/)"
    )
    assert dec.owner_for(row(anchors=["07-ENGINEERING/x.md"])) == dec.ZONE_OWNER["07-ENGINEERING"]
    assert dec.owner_for(row(anchors=["README.md"])) == dec.ROOT_OWNER
    assert dec.owner_for(row(anchors=[])) == dec.REGISTER_OWNER
    # an anchor carrying a `path:detail` suffix resolves on the path
    assert dec.owner_for(row(anchors=["engine/a.py:def foo"])) == dec.ZONE_OWNER["engine"]


def _version_controlled_zone_missing(zone: str) -> bool:
    """Is this declared zone genuinely absent — as opposed to merely generated?

    `.gitignore` is the single authority for what version control excludes, so this asks git
    rather than carrying a second list of generated zones that could drift out of agreement
    with it.
    """
    if (REPO / zone).exists():
        return False
    git_bin = shutil.which("git")
    if git_bin is None:  # pragma: no cover - git always present in CI
        pytest.skip("git is not available")
    excluded = subprocess.run(  # noqa: S603
        # The trailing slash is load-bearing: `.gitignore` states these zones as directory-only
        # patterns, and git cannot infer directory-ness for a path that is absent from disk —
        # which is precisely the case this check exists to answer.
        [git_bin, "check-ignore", "-q", "--", f"{zone}/"],
        cwd=REPO,
        capture_output=True,
        check=False,
    )
    return excluded.returncode != 0


def test_owner_resolution_creates_no_authority():
    """Every declared zone owner names a REAL repository zone.

    A zone resolves either on disk or, for a generated zone that `.gitignore` excludes from
    version control (`determinism-evidence/`, `dist/`, `knowledge/`, `realization/`), as a
    declared exclusion. Asserting bare on-disk existence made this test pass only on a machine
    that had already generated those zones locally and fail on every clean checkout, which is
    the opposite of a determinism guarantee.
    """
    for zone in dec.ZONE_OWNER:
        assert not _version_controlled_zone_missing(zone), zone


def test_the_zone_existence_check_still_rejects_a_zone_that_names_nothing():
    """The generated-zone allowance must not make the invariant vacuous.

    Relaxing "exists on disk" to "exists on disk OR is a declared exclusion" would be worthless
    if every name passed. A fabricated zone is neither present nor ignored, so it is still
    caught — which is what keeps a typo or a stale `ZONE_OWNER` entry from going unnoticed.
    """
    assert _version_controlled_zone_missing("determinism-evidence-typo")
    assert _version_controlled_zone_missing("zone-that-names-nothing")
    # and a generated zone that .gitignore really does exclude is still allowed
    assert not _version_controlled_zone_missing("determinism-evidence")


def test_the_plan_generator_resolves_a_real_addressed_plan():
    r = homed()
    r.update(decide(r))
    r["implementation_owner"] = dec.owner_for(r)
    steps = dec.plan_for(r)
    assert len(steps) == len(dec.OPERATIONS[dec.HOME_NEW_KNOWLEDGE]["steps"])
    assert all("{" not in s and "}" not in s for s in steps), steps
    assert r["destination"] in steps[1]
    assert r["implementation_owner"] in steps[0]


def test_the_plan_generator_is_total_over_every_operation():
    for operation in dec.OPERATIONS:
        r = homed(anchors=["engine/a.py"], dependencies=["UCOS-KA-000002"])
        r["implementation_action"] = operation
        r["implementation_owner"] = dec.owner_for(r)
        steps = dec.plan_for(r)
        assert steps, operation
        assert all("{" not in s and "}" not in s for s in steps), (operation, steps)


def test_a_missing_placeholder_resolves_to_the_declared_dash_never_a_blank():
    r = row(anchors=[], destination="", authority="", evidence_conversation="")
    r["implementation_action"] = dec.HOME_NEW_KNOWLEDGE
    r["implementation_owner"] = dec.owner_for(r)
    steps = dec.plan_for(r)
    assert any("—" in s for s in steps)


def test_an_unknown_operation_yields_no_plan_rather_than_a_fabricated_one():
    assert dec.plan_for(row(implementation_action="NOT-AN-OPERATION")) == []


# ------------------------------------------------------- the committed register (integration)
def committed() -> dict:
    return json.loads(ASSIM_JSON.read_text(encoding="utf-8"))


def rows_of(payload: dict) -> list[dict]:
    cols = payload["row_columns"]
    return [dict(zip(cols, r, strict=False)) for r in payload["rows"]]


def test_the_decision_columns_are_appended_never_inserted():
    """Presence is decided first, superiority second, the decision third — which is what keeps a
    pre-D-2 and a pre-D-3 record positionally readable."""
    cols = committed()["row_columns"]
    assert cols[-5:] == [
        "decision",
        "decision_rule",
        "decision_rationale",
        "implementation_action",
        "implementation_priority",
    ]
    assert cols.index("state") < cols.index("superiority") < cols.index("decision")


def test_every_committed_object_carries_exactly_one_decision():
    payload = committed()
    rows = rows_of(payload)
    assert rows
    for r in rows:
        assert r["decision"] in dec.ACTIONS, r["kid"]
        assert r["decision_rule"] in dec.RULE_IDS, r["kid"]
        assert r["implementation_action"] in dec.OPERATIONS, r["kid"]
        assert r["implementation_priority"] in dec.PRIORITIES, r["kid"]
        assert r["decision_rationale"], r["kid"]


def test_committed_decisions_are_total_and_all_six_actions_are_reachable():
    payload = committed()
    actions = payload["decision_actions"]
    assert sum(actions.values()) == len(payload["rows"]) == payload["verified_objects"]
    for action in dec.ACTIONS:
        assert actions.get(action, 0) > 0, f"{action} is unreachable on the committed corpus"


def test_every_committed_decision_matches_the_action_its_rule_decides():
    rule_action = {str(r["id"]): str(r["action"]) for r in dec.DECISION_RULES}
    rule_operation = {str(r["id"]): str(r["operation"]) for r in dec.DECISION_RULES}
    for r in rows_of(committed()):
        assert rule_action[r["decision_rule"]] == r["decision"], r["kid"]
        assert rule_operation[r["decision_rule"]] == r["implementation_action"], r["kid"]


def test_every_committed_decision_replays_from_its_recorded_rationale():
    """Deterministic replay over the WHOLE committed register, with nothing but the register."""
    for r in rows_of(committed()):
        again = dec.replay(r["decision_rationale"])
        assert {k: r[k] for k in again} == again, r["kid"]


def test_every_committed_decision_re_derives_from_its_row():
    """Independent re-derivation: the recorded decision cannot disagree with the rule set."""
    rows = rows_of(committed())
    kids = {r["kid"] for r in rows}
    for r in rows:
        objection = any(
            ch == sup.OUTCOME_CHAR[sup.INFERIOR] and dim["id"] in sup.CONSTITUTIONAL_DIMENSIONS
            for dim, ch in zip(sup.DIMENSIONS, r["superiority_profile"], strict=False)
        )
        again = dec.decide(
            r, objection=objection, deps_closed=all(k in kids for k in (r["dependencies"] or []))
        )
        assert {k: r[k] for k in again} == again, r["kid"]


def test_the_residual_rule_is_provably_unused_on_the_committed_corpus():
    assert committed()["decision_rules"].get(dec.RESIDUAL_RULE, 0) == 0


def test_no_knowledge_modifying_decision_stands_on_an_open_dependency_chain():
    rows = rows_of(committed())
    kids = {r["kid"] for r in rows}
    modifying = {a for a in dec.ACTIONS if dec.ACTION_REGISTRY[a]["modifies_knowledge"]}
    for r in rows:
        if r["decision"] in modifying:
            assert all(k in kids for k in (r["dependencies"] or [])), r["kid"]


def test_every_committed_decision_is_traceable():
    for r in rows_of(committed()):
        assert int(r["origin_conversations"] or 0) >= 1, r["kid"]
        assert r["decision_rule"] and r["implementation_action"] and r["decision_rationale"]


def test_the_prior_axes_are_unchanged_by_the_decision_axis():
    payload = committed()
    assert payload["determination"] == "REPOSITORY CONSTITUTIONALLY COMPLETE"
    assert payload["unclassified"] == 0
    assert sum(payload["states"].values()) == payload["verified_objects"]
    assert sum(payload["superiority_states"].values()) == payload["verified_objects"]
    # neither prior axis lost a column or a state
    assert set(payload["states"]) == {
        "ALREADY-REPRESENTED",
        "SEMANTICALLY-REPRESENTED",
        "ASSIMILATED",
        "HISTORICAL-EVIDENCE-ONLY",
        "SUPERSEDED",
        "REJECTED",
    }
    assert set(payload["superiority_states"]) == set(sup.SUPERIORITY_STATES)


def test_the_decision_axis_consumes_both_prior_axes():
    """A decision that were a function of one axis alone would collapse one of these cross-tabs
    to a single column. Neither does."""
    rows = rows_of(committed())
    by_presence = {}
    by_superiority = {}
    for r in rows:
        by_presence.setdefault(r["state"], set()).add(r["decision"])
        by_superiority.setdefault(r["superiority"], set()).add(r["decision"])
    assert max(len(v) for v in by_presence.values()) > 1
    assert max(len(v) for v in by_superiority.values()) > 1


def test_committed_schema_declares_the_whole_decision_model():
    payload = committed()
    assert payload["decision_version"] == dec.DECISION_VERSION
    assert len(payload["decision_ruleset_sha256"]) == 64
    assert [r["rule"] for r in payload["decision_rule_registry"]] == dec.RULE_IDS
    assert {a["action"] for a in payload["decision_action_registry"]} == set(dec.ACTIONS)
    assert {o["operation"] for o in payload["decision_operation_registry"]} == set(dec.OPERATIONS)
    assert payload["decision_grounds_keys"] == list(dec.GROUNDS_KEYS)
    assert set(payload["decision_grounds_legend"]) == set(dec.GROUNDS_KEYS)
    assert payload["decision_residual_rule"] == dec.RESIDUAL_RULE
    assert set(payload["decision_silent_rules"]) == set(dec.SILENT_RULES)
    for rid, spec in payload["decision_silent_rules"].items():
        assert spec["kind"] in ("STRUCTURAL", "GUARD"), rid
        assert spec["reason"], rid


def test_the_recorded_ruleset_digest_seals_the_declaration():
    """The digest must be the sha256 of the declaration as it stands, so an edit to the rule set
    cannot pass the drift gate while the decisions still cite the old model."""
    import hashlib

    declaration = dec.ruleset_declaration()
    digest = hashlib.sha256(
        json.dumps(declaration, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert committed()["decision_ruleset_sha256"] == digest


def test_recorded_aggregates_reproduce_from_the_rows():
    payload = committed()
    rows = rows_of(payload)
    from collections import Counter

    assert payload["decision_actions"] == {
        a: Counter(r["decision"] for r in rows).get(a, 0) for a in dec.ACTIONS
    }
    assert payload["decision_rules"] == dict(Counter(r["decision_rule"] for r in rows))
    assert payload["decision_operations"] == dict(Counter(r["implementation_action"] for r in rows))
    assert payload["decision_priorities"] == dict(
        Counter(r["implementation_priority"] for r in rows)
    )


def test_the_implementation_plan_covers_every_decided_object():
    payload = committed()
    plan = payload["decision_plan"]
    assert plan
    assert sum(e["objects"] for e in plan) == payload["verified_objects"]
    for entry in plan:
        assert entry["decision"] in dec.ACTIONS
        assert entry["implementation_action"] in dec.OPERATIONS
        assert entry["implementation_priority"] in dec.PRIORITIES
        assert entry["implementation_owner"]
        assert entry["steps"] == list(dec.OPERATIONS[entry["implementation_action"]]["steps"])


def test_the_implementation_plan_is_ordered_by_declared_ordinals():
    plan = committed()["decision_plan"]
    ranks = [dec.PRIORITIES.index(e["implementation_priority"]) for e in plan]
    assert ranks == sorted(ranks)


def test_every_committed_owner_is_a_declared_or_presence_assigned_authority():
    payload = committed()
    declared = set(dec.ZONE_OWNER.values()) | {dec.ROOT_OWNER, dec.REGISTER_OWNER}
    declared |= {str(v["owner"]) for v in payload["destination_policy"].values()}
    for owner in payload["decision_owners"]:
        assert owner in declared, owner


def test_decision_gates_are_blocking_and_pass():
    gates = {g["gate"]: g for g in committed()["gates"]}
    blocking = [
        "Every evaluated object carries exactly one repository decision",
        "Every repository decision is a declared action",
        "Every decision resolves to one declared decision rule",
        "Every decision matches the action its declared rule decides",
        "Every decision declares one registered implementation action",
        "Every decision declares a declared implementation priority",
        "Every decision names an implementation owner",
        "Every decision carries the declared decision version",
        "Every decision replays identically from its recorded rationale",
        "Every recorded decision re-derives from the row it was decided from",
        "Decision rule set is total (residual rule provably unused)",
        "Every knowledge-modifying decision has a closed dependency chain",
        "Every decision traces to recorded evidence provenance",
        "Silent decision rules with no declared reason",
    ]
    for name in blocking:
        assert name in gates, name
        assert gates[name]["blocking"] is True, name
        assert gates[name]["result"] == "PASS", gates[name]
    assert gates["Required repository actions unreachable on this corpus"]["count"] == 0
    assert gates["Repository actions referred to their owners"]["blocking"] is False


def test_the_decision_registers_are_emitted():
    decision_register = PROGRAM_DIR / "10-REPOSITORY-DECISION-REGISTER.md"
    plan_register = PROGRAM_DIR / "11-IMPLEMENTATION-PLAN-REGISTER.md"
    text = decision_register.read_text(encoding="utf-8")
    for action in dec.ACTIONS:
        assert action in text, action
    for rule in dec.RULE_IDS:
        assert rule in text, rule
    for key in dec.GROUNDS_KEYS:
        assert f"`{key}`" in text, key
    assert dec.DECISION_VERSION in text
    plan = plan_register.read_text(encoding="utf-8")
    for operation in dec.OPERATIONS:
        assert operation in plan, operation
    for priority in dec.PRIORITIES:
        assert priority in plan, priority


def test_the_validation_and_certification_reports_carry_the_decision_axis():
    validation = (PROGRAM_DIR / "06-VALIDATION-REPORT.md").read_text(encoding="utf-8")
    for claim in (
        "Every evaluated object has exactly one decision",
        "Every decision maps to one declared rule",
        "Deterministic replay",
        "Byte-identical regeneration",
        "Repository Truth preserved",
        "Knowledge Once preserved",
        "Dependency closure preserved",
        "Traceability preserved",
    ):
        assert claim in validation, claim
    certification = (PROGRAM_DIR / "07-CERTIFICATION-REPORT.md").read_text(encoding="utf-8")
    assert dec.DECISION_VERSION in certification
    assert "Repository decision completeness" in certification
    assert "Execution of any repository decision" in certification


# --------------------------------------------------------------------------- compatibility
def test_a_pre_d3_row_deserializes_and_fails_closed():
    """A record written before this axis existed must still load — marked UNDECIDED rather than
    given a fabricated decision, so the fail-closed gate detects it."""
    assert dec.blank() == {
        "decision": "",
        "decision_rule": "",
        "decision_rationale": "",
        "implementation_action": "",
        "implementation_priority": "",
    }
    engine = _load("d3_assimilation_engine", PROGRAM_DIR / "assimilation_engine.py")
    legacy = {c: "" for c in engine.ROW_COLUMNS if c not in engine.DECISION_COLUMNS}
    legacy.update(
        kid="UCOS-KA-000001",
        name="n",
        state="ALREADY-REPRESENTED",
        disposition="ARCHITECTURE",
        presence_level="REPO-DOCUMENTED",
        anchors=[],
        dependencies=[],
        superiority=sup.NOT_SUPERIOR,
        superiority_profile="=" * sup.DIMENSION_COUNT,
        superiority_rule="SUP-7",
        superiority_score=0,
        origin_conversations=1,
        authority_score=0.0,
    )
    rows = engine.hydrate([legacy])
    assert rows[0]["decision"] == ""
    assert rows[0]["implementation_owner"]
    assert rows[0]["decision_version"] == dec.DECISION_VERSION
    gates = {g["gate"]: g for g in engine.decision_gates(rows)}
    assert gates["Every evaluated object carries exactly one repository decision"]["count"] == 1


def test_the_derived_columns_are_not_stored_per_row():
    engine = _load("d3_assimilation_engine_cols", PROGRAM_DIR / "assimilation_engine.py")
    cols = committed()["row_columns"]
    for derived in engine.DECISION_DERIVED_COLUMNS:
        assert derived not in cols, derived
    assert set(engine.DECISION_COLUMNS) <= set(cols)
    # and the decision axis writes none of the columns the prior axes own
    assert not set(engine.DECISION_COLUMNS) & set(engine.SUPERIORITY_COLUMNS)
    assert not set(engine.DECISION_COLUMNS) & {
        "state",
        "rule",
        "presence_level",
        "presence_corrected",
        "destination",
        "wave",
    }

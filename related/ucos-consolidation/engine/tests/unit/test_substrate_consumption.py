"""UCOS as a consumer of the UAKP substrate, and the direction of that dependency.

The constitution requires a universal platform that UCOS CONSUMES, and requires it not to be
developed as part of UCOS. The substrate is now extracted; these hold the binding back to it
to the property that makes the extraction worth anything — that the substrate never learns
about UCOS.
"""

from __future__ import annotations

import ast
import json
import pathlib
import runpy
import sys

import pytest

# THE GUARD MUST PRECEDE THE IMPORT IT GUARDS. `engine.substrate` imports `uakp` at module
# scope, so importing it first raises ModuleNotFoundError before `importorskip` can convert
# that absence into a skip. The substrate is an EXTERNAL project by constitutional design —
# it is installed here as an editable checkout and is present in no clone and on no runner —
# so this module is unimportable exactly where the suite matters most. A collection error
# aborts the ENTIRE pytest run rather than this one module, which is why an absence the
# author had already declared lawful still failed `./verify.sh --full` in CI.
uakp = pytest.importorskip("uakp", reason="the substrate is not installed in this environment")

from engine.substrate import adapter, gate  # noqa: E402 — guarded by the skip above

REPO = pathlib.Path(__file__).resolve().parents[3]
DECLARATION = REPO / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json"
CONSUMER = REPO / "engine" / "substrate"


def _declaration() -> dict:
    return json.loads(DECLARATION.read_text(encoding="utf-8"))


def test_the_substrate_never_learns_about_ucos() -> None:
    """The one property the extraction exists to create.

    An adapter placed in the substrate would undo it in a single commit, so this is asserted
    over the substrate's own installed source rather than trusted.
    """
    root = pathlib.Path(uakp.__file__).resolve().parent
    forbidden = ("00-BOOK", "00-MASTER", "00-CMG", "99-FREEZE", "UCOS")
    for module in sorted(root.rglob("*.py")):
        for node in ast.walk(ast.parse(module.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for token in forbidden:
                    assert token not in node.value, (
                        f"{module.name} names {token!r}. The substrate has learned about its "
                        f"consumer, which is the extraction undone."
                    )


def test_every_ucos_specific_fact_lives_on_the_consumer_side() -> None:
    """The mirror: the adapter is where UCOS knowledge is allowed to be."""
    source = (CONSUMER / "adapter.py").read_text(encoding="utf-8")
    assert "00-BOOK" in source, (
        "the consumer-side adapter names no UCOS register, so either it reads nothing or the "
        "knowledge moved somewhere worse"
    )


def test_consumption_is_not_a_runtime_dependency() -> None:
    """pyproject declares dependencies = [] on constitutional grounds, ISD-L-09 refuses a
    pinned runtime dependency, and test_infinite_scope asserts the list is empty. Consumption
    happens in the governance plane; the runtime core is untouched."""
    manifest = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    assert "dependencies = []" in manifest
    assert "uakp" not in manifest.split("[project.optional-dependencies]")[0]


def test_an_absent_substrate_is_a_fault_and_never_a_pass(monkeypatch, capsys) -> None:
    """A gate that reported OPEN because it could not import its subject would be the exact
    false green this apparatus exists to refuse.

    The substrate IS installed here, so its absence is forged rather than arranged: blocking
    the import is the only way to reach the branch that matters, and a branch nothing reaches
    is a branch nobody has shown can fire.
    """
    monkeypatch.setitem(sys.modules, "uakp", None)
    monkeypatch.setitem(sys.modules, "uakp.rules", None)
    monkeypatch.chdir(REPO)
    assert gate.main() == gate.EXIT_FAULT
    assert "FAULT" in capsys.readouterr().err


def test_the_ratchet_is_declared_with_a_reason() -> None:
    ratchet = _declaration()["ratchet"]
    assert isinstance(ratchet["contradictions"], int)
    reason = ratchet["$contradictions"]
    prose = "\n".join(reason) if isinstance(reason, list) else reason
    assert prose.strip(), (
        "a ceiling with no reason is a number somebody chose, and nobody can tell whether "
        "reaching zero is work or redesign"
    )
    assert str(ratchet["contradictions"]) in prose, (
        "the reason does not mention the number it explains, so the two can drift apart "
        "without either looking wrong"
    )


def test_the_gate_holds_at_its_declared_ceiling() -> None:
    from uakp import rules
    from uakp.core.contradiction import detect
    from uakp.core.graph import Graph

    graph = Graph.of(
        artifacts=adapter.artifacts(str(REPO)), authorities=adapter.authorities(str(REPO))
    )
    measured = len(list(detect(graph, rules.SHIPPED)))
    assert measured == _declaration()["ratchet"]["contradictions"], (
        f"measured {measured}; the ratchet refuses in both directions, so this is either new "
        f"debt or debt repaid without tightening the ceiling"
    )


def test_an_append_only_ledger_records_identity_and_does_not_claim_presence() -> None:
    """UCKP-ART-05 makes an identity permanent, so a retired path keeps its ledger entry
    forever. Treating history as a present claim reported thirteen contradictions that were
    all genuinely absent paths and none of them defects — one was the deliberate retirement
    of ledger_authority.py, which is the system working."""
    authorities = {a.identity: a for a in adapter.authorities(str(REPO))}
    ledger = authorities["UCOS-IDENTITY-LEDGER"]
    for claimed in ledger.governs:
        assert (REPO / claimed).exists(), f"the ledger authority claims {claimed}, which is gone"


# --- the refusal witnesses (UEC-L-14) -----------------------------------------------------
#
# UEC-L-05 measures that a test NAMES this gate. That is necessary and nowhere near
# sufficient: every test above names it and none of them had forged a condition it must
# refuse, so the gate was counted as governed while nobody had shown it could refuse
# anything. A verifier nothing has shown can refuse certifies nothing, and its green tick is
# worse than no tick because it licenses the belief that the property was checked.
#
# Each witness below builds a whole root whose truth is known, points the gate at it, and
# asserts the CLOSED exit code as a literal — the shape UEC-000001 declares under
# refusal_witness.accepted_shapes.


def _forged_root(tmp_path, contradictions: int) -> pathlib.Path:
    """A minimal repository whose only declared truth is a contradiction ceiling.

    No `00-BOOK/DATA/artifacts.json`, no exclusion register and no identity ledger, so every
    artifact the walk finds is owned by nobody. The count is therefore knowable in advance
    and the ceiling can be set above it and below it on purpose.
    """
    declaration = tmp_path / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json"
    declaration.parent.mkdir(parents=True)
    declaration.write_text(
        json.dumps(
            {
                "artifact_id": "UCOS-SUB-001",
                "requires": "uakp>=0.0.1",
                "ratchet": {"contradictions": contradictions},
                "discovery": {"ungoverned_directories": [".git", "__pycache__"]},
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_the_gate_refuses_new_debt_above_the_ceiling(tmp_path, monkeypatch, capsys) -> None:
    """The upper side of the ratchet: an artifact no authority claims must fail the gate."""
    monkeypatch.chdir(_forged_root(tmp_path, contradictions=0))
    assert gate.main() == 1, "a ratchet that admits new debt is not a ratchet"
    assert "CLOSED" in capsys.readouterr().err


def test_the_gate_refuses_slack_below_the_ceiling(tmp_path, monkeypatch, capsys) -> None:
    """The lower side, which is the half a one-directional ceiling gets wrong.

    Debt repaid without tightening the ceiling leaves room a future regression can occupy in
    silence, so measuring under the ceiling is refused exactly as measuring over it is.
    """
    monkeypatch.chdir(_forged_root(tmp_path, contradictions=10_000))
    assert gate.main() == 1, "slack under the ceiling is a regression nobody would see"
    assert "slack" in capsys.readouterr().err


def test_an_unusable_declaration_is_a_fault_and_never_a_pass(tmp_path, monkeypatch) -> None:
    """A gate whose own declaration will not parse has measured nothing and must say so."""
    broken = tmp_path / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json"
    broken.parent.mkdir(parents=True)
    broken.write_text("{not json", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert gate.main() == 2, "an unreadable declaration must yield no verdict"


def test_an_absent_ungoverned_directory_list_is_a_fault_rather_than_a_default(tmp_path) -> None:
    """The list moved from a frozenset literal into the declaration so that admitting a name
    is a data change (UCKP-ART-17). A default would silently walk `.git` and `.ec1-venv` and
    report thousands of artifacts nothing governs, so its absence raises."""
    declaration = tmp_path / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json"
    declaration.parent.mkdir(parents=True)
    declaration.write_text(json.dumps({"discovery": {"ungoverned_directories": []}}), "utf-8")
    with pytest.raises(ValueError, match="empty"):
        adapter.ungoverned_directories(str(tmp_path))


def test_the_ungoverned_directory_list_is_read_from_data_and_not_frozen_in_code() -> None:
    """ISD-L-01 and UCON-L-15 both counted the literal, and both were right: a set whose
    membership can only change by editing a module is a closed enumeration."""
    source = (CONSUMER / "adapter.py").read_text(encoding="utf-8")
    assert "frozenset(\n" not in source, "the closed enumeration is back in the module"
    declared = _declaration()["discovery"]["ungoverned_directories"]
    assert adapter.ungoverned_directories(str(REPO)) == frozenset(declared)


def test_every_semantic_edit_moves_the_declaration_digest() -> None:
    """UEC-L-08 asks whether a certification identity exists; this asks the harder question.

    A digest over a projection — the ratchet alone, or a curated subset — certifies two
    different declarations with one value, which is the defect engine/construct was measured
    carrying. Every field participates here, so no edit can change what the gate enforces
    while leaving its identity where it was.
    """
    declaration = _declaration()
    before = gate.declaration_digest(declaration)
    assert before == gate.declaration_digest(_declaration()), "the digest is not deterministic"
    mutated = dict(declaration)
    mutated["ratchet"] = dict(declaration["ratchet"])
    mutated["ratchet"]["contradictions"] = declaration["ratchet"]["contradictions"] + 1
    assert gate.declaration_digest(mutated) != before, (
        "moving the ceiling left the certification identity unchanged, so one digest "
        "certifies two different declarations"
    )


def test_the_gate_is_reachable_from_two_independent_invocation_planes() -> None:
    """UEC-L-06: two planes mean deleting one leaves a signal. The Makefile target named
    `$(PYTHON)`, which this repository does not define, so `make -n` printed
    `m engine.substrate` and the only plane there was could never have executed."""
    planes = {
        "Makefile": (REPO / "Makefile").read_text(encoding="utf-8"),
        "sub-gate.yml": (REPO / ".github" / "workflows" / "sub-gate.yml").read_text("utf-8"),
    }
    for name, text in planes.items():
        assert "engine.substrate.gate" in text, f"{name} does not invoke the gate by name"
    assert set(_declaration()["gate"]["invoked_from"]), "the declaration records no plane"


# --- the readers underneath the measurement -----------------------------------------------
#
# The forged roots above carry a declaration and nothing else, so the artifact register is
# absent and the authorities generator stops at its first read — which left every register
# BELOW it unmeasured. The real repository has all of them, present and well formed, so the
# arms that answer for a register that is absent, unparseable or shaped differently had no
# case in either direction.


def _adapter_root(tmp_path, **documents) -> str:
    """A root carrying the artifact register, plus whatever else the case declares.

    The register is always written because the authorities generator RETURNS when it cannot
    be read: without it nothing below is reached, which is exactly why the forged gate roots
    left the rest of this module unmeasured.
    """
    (tmp_path / "00-BOOK" / "DATA").mkdir(parents=True, exist_ok=True)
    declaration = tmp_path / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json"
    declaration.parent.mkdir(parents=True, exist_ok=True)
    declaration.write_text(
        json.dumps({"discovery": {"ungoverned_directories": [".git", "__pycache__"]}}),
        encoding="utf-8",
    )
    (tmp_path / "governed.txt").write_text("", encoding="utf-8")
    # The register claims every path this root contains, INCLUDING itself and the
    # declaration: an artifact no authority claims is a contradiction, so a root meant to
    # measure zero of them cannot leave its own governing documents unclaimed.
    (tmp_path / "00-BOOK" / "DATA" / "artifacts.json").write_text(
        json.dumps(
            {
                "artifacts": [
                    {"path": "governed.txt"},
                    {"path": "00-BOOK/DATA/artifacts.json"},
                    {"path": "00-MASTER/UCOS-SUB-001/sub-declaration.json"},
                ]
            }
        ),
        encoding="utf-8",
    )
    for relative, body in documents.items():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return str(tmp_path)


def _named(root: str) -> dict[str, frozenset[str]]:
    return {a.identity: a.governs for a in adapter.authorities(root)}


def test_a_register_that_is_absent_contributes_no_authority(tmp_path) -> None:
    """AN ABSENT REGISTER IS AN ABSENT CLAIM, NOT A FAULT.

    Four registers are read and each is optional in exactly this sense: a repository that
    does not keep one has no authority of that kind, and the measurement proceeds over the
    ones it does keep. Raising instead would make the gate unable to measure any repository
    that keeps a subset — and this gate's whole argument is that it measures the repository
    rather than one register.
    """
    found = _named(_adapter_root(tmp_path))

    assert set(found) == {"UCOS-ARTIFACT-REGISTER"}
    assert "governed.txt" in found["UCOS-ARTIFACT-REGISTER"]


def test_a_register_that_cannot_be_parsed_contributes_no_authority(tmp_path) -> None:
    """A TRUNCATED REGISTER MUST NOT BECOME AN EMPTY ONE SILENTLY — and it does not: it
    contributes nothing, exactly as an absent one does, because a register that cannot be
    read has made no claim this consumer can apply. The alternative is a partial parse, which
    would absolve whatever happened to be readable and report the rest as ungoverned.
    """
    root = _adapter_root(
        tmp_path,
        **{
            "00-BOOK/DATA/id-ledger.json": "{ truncated",
            "00-BOOK/DATA/exclusion-register.json": "{ truncated",
            "00-MASTER/UEC-000001/uec-declaration.json": "{ truncated",
        },
    )

    assert set(_named(root)) == {"UCOS-ARTIFACT-REGISTER"}


def test_the_identity_ledger_claims_only_what_it_minted_and_is_still_here(tmp_path) -> None:
    """AN APPEND-ONLY LEDGER RECORDS IDENTITY, IT DOES NOT CLAIM PRESENCE.

    Three arms, none of which had run. A section that is not a mapping is skipped rather than
    iterated — the ledger's two sections are read by name and a future one of another shape
    must not raise inside a reader whose job is to report. A ledger whose entries are all
    RETIRED paths yields no authority at all rather than an authority governing nothing,
    because an authority with an empty claim set reads as a register that exists and has said
    nothing, which is a different fact from history. And the present intersection is what
    keeps a retired identity from being reported as a claim over a path that is gone.
    """
    all_retired = _adapter_root(
        tmp_path / "retired",
        **{
            "00-BOOK/DATA/id-ledger.json": json.dumps(
                {"by_path": {"deleted-long-ago.txt": {}}, "by_object": ["not a mapping"]}
            )
        },
    )
    assert "UCOS-IDENTITY-LEDGER" not in _named(all_retired)

    still_here = _adapter_root(
        tmp_path / "present",
        **{
            "00-BOOK/DATA/id-ledger.json": json.dumps(
                {"by_path": {"governed.txt": {}, "deleted-long-ago.txt": {}}, "by_object": None}
            )
        },
    )
    assert _named(still_here)["UCOS-IDENTITY-LEDGER"] == frozenset({"governed.txt"})


def test_the_enforcement_register_claims_only_identities_that_are_paths(tmp_path) -> None:
    """IDENTITIES THAT ARE NOT PATHS ARE NOT CLAIMS OVER PATHS.

    The register names Make targets and verify.sh stages beside files — real governed things
    that are not artifacts — so the claim is filtered to what exists on disk. A register whose
    governed list is not a list at all is skipped rather than iterated, and one whose entries
    all name non-paths yields no authority rather than one governing nothing.
    """
    wrong_shape = _adapter_root(
        tmp_path / "shape",
        **{"00-MASTER/UEC-000001/uec-declaration.json": json.dumps({"governed_enforcement": {}})},
    )
    assert "UCOS-ENFORCEMENT-REGISTER" not in _named(wrong_shape)

    only_targets = _adapter_root(
        tmp_path / "targets",
        **{
            "00-MASTER/UEC-000001/uec-declaration.json": json.dumps(
                {"governed_enforcement": [{"identity": "make: verify"}, "not a mapping"]}
            )
        },
    )
    assert "UCOS-ENFORCEMENT-REGISTER" not in _named(only_targets)

    real_files = _adapter_root(
        tmp_path / "files",
        **{
            "00-MASTER/UEC-000001/uec-declaration.json": json.dumps(
                {"governed_enforcement": [{"identity": "governed.txt"}, {"identity": "make: x"}]}
            )
        },
    )
    assert _named(real_files)["UCOS-ENFORCEMENT-REGISTER"] == frozenset({"governed.txt"})


def test_an_exclusion_register_declaring_no_rule_absolves_nothing(tmp_path) -> None:
    """A REGISTER WITH NO RULES IS NOT A REGISTER THAT ABSOLVES EVERYTHING.

    The rules are collected first and the walk is only made when there is something to match
    against — so a register present but empty yields no authority, rather than an authority
    over the empty set or, worse, a walk whose ``any()`` over no rules would have to be
    decided one way or the other. And a repository with no ``.gitignore`` has no carve-outs,
    which must not stop the exclusions being read: the dependency runs one way only, so a
    missing ignore file can never grant an absolution and must never withhold one either.
    """
    no_rules = _adapter_root(
        tmp_path / "empty",
        **{"00-BOOK/DATA/exclusion-register.json": json.dumps({"entries": [{"class": "CACHE"}]})},
    )
    assert "UCOS-EXCLUSION-REGISTER" not in _named(no_rules)

    with_rules = _adapter_root(
        tmp_path / "rules",
        **{
            "00-BOOK/DATA/exclusion-register.json": json.dumps(
                {"entries": [{"rule": "governed.txt", "class": "CACHE"}]}
            )
        },
    )
    assert "governed.txt" in _named(with_rules)["UCOS-EXCLUSION-REGISTER"]


def test_a_rule_that_is_blank_or_a_comment_matches_nothing(tmp_path) -> None:
    """WHAT THE COMPILER CANNOT INTERPRET IT DOES NOT ABSOLVE.

    Every rule in the register is a real pattern, so the two arms that reject a line before
    compilation had no case. A comment and a blank line are ordinary gitignore content, and
    compiling either would produce a pattern matching the empty string — which every relative
    path starts with. Over-matching here silently absolves paths the register never claimed,
    and that is the direction that hides a finding.
    """
    assert adapter._pattern("") is None
    assert adapter._pattern("   ") is None
    assert adapter._pattern("# a comment about the next rule") is None
    assert adapter._pattern("*") is None
    assert adapter._pattern("00-BOOK/DATA/") is not None


def test_the_segment_grammar_covers_the_single_character_and_broken_class_forms() -> None:
    """THE SEGMENT GRAMMAR IS GIT'S, AND THREE OF ITS FORMS HAD NEVER BEEN COMPILED.

    ``?`` is one character and not any run of them, so it must not become ``[^/]*`` — a rule
    like ``log?.txt`` would then claim ``log-archive.txt``. A ``[`` with no closing bracket is
    not a character class: git takes it literally, and treating the rest of the segment as a
    class body would swallow the pattern that follows it. The class form itself is why the
    escape is not applied wholesale — the register uses ``[0-9][0-9]-*.md`` to claim
    43 generated files, and escaping the brackets left every one unaccounted for.
    """
    single = adapter._pattern("log?.txt")
    assert single is not None
    assert adapter._matches("log1.txt", "log?.txt") is True
    assert adapter._matches("log-archive.txt", "log?.txt") is False

    assert adapter._matches("a[b.txt", "a[b.txt") is True
    assert adapter._matches("ab.txt", "a[b.txt") is False

    assert adapter._matches("01-a.md", "[0-9][0-9]-*.md") is True
    assert adapter._matches("0a-a.md", "[0-9][0-9]-*.md") is False


def test_an_ungoverned_directory_list_that_is_not_a_list_of_names_is_a_fault(tmp_path) -> None:
    """THE LIST IS DATA, AND DATA OF THE WRONG SHAPE IS A FAULT AND NEVER A DEFAULT.

    The empty case was tested; the malformed one was not. A string, a mapping, or a list
    holding anything that is not a non-empty name cannot be used as a skip set — and falling
    back to a default would silently walk ``.git`` and ``.ec1-venv`` and report thousands of
    artifacts nothing governs, a measurement that lies in the direction of alarm.
    """
    for malformed in ("not-a-list", {"a": 1}, ["", ".git"], [".git", 7]):
        declaration = tmp_path / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json"
        declaration.parent.mkdir(parents=True, exist_ok=True)
        declaration.write_text(
            json.dumps({"discovery": {"ungoverned_directories": malformed}}), encoding="utf-8"
        )
        with pytest.raises(ValueError, match="is not a list of names"):
            adapter.ungoverned_directories(str(tmp_path))


def test_the_gate_opens_and_names_each_authority_when_the_ratchet_holds(
    tmp_path, monkeypatch, capsys
) -> None:
    """THE GATE'S ONLY PASSING VERDICT HAD NEVER BEEN PRODUCED BY A TEST.

    Both refusal witnesses forge a root with no register at all, so every artifact is owned
    by nobody, the count is above or below the ceiling on purpose, and the gate always
    CLOSED. That left two things unmeasured: the OPEN verdict itself — the answer this gate
    gives on every healthy run — and the per-authority line of its report, which is what
    tells a reader WHICH register absolved what. A gate whose passing output nobody has seen
    can print anything.
    """
    root = _adapter_root(tmp_path)
    (tmp_path / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json").write_text(
        json.dumps(
            {
                "artifact_id": "UCOS-SUB-001",
                "requires": "uakp>=0.0.1",
                "ratchet": {"contradictions": 0},
                "discovery": {"ungoverned_directories": [".git", "__pycache__"]},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(root)

    assert gate.main() == 0

    out = capsys.readouterr().out
    assert "OPEN — the ratchet holds." in out
    assert "UCOS-ARTIFACT-REGISTER" in out
    assert "contradictions  : 0 (ceiling 0)" in out


def test_a_measurement_that_does_not_complete_is_a_fault_and_never_a_verdict(
    tmp_path, monkeypatch, capsys
) -> None:
    """FAULT AND CLOSED ARE DIFFERENT ANSWERS, and only the declaration's fault arm had run.

    An unreadable declaration was tested. This is the other one: the declaration parses, the
    substrate imports, and the MEASUREMENT itself fails. Reporting that as CLOSED would say
    the repository has new contradictions when the truth is that nothing was counted, and
    reporting it as OPEN would be a false green over a subject that was never loaded. The
    handler is deliberately broad because any failure here means nothing was measured.
    """
    root = _adapter_root(tmp_path)
    (tmp_path / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json").write_text(
        json.dumps(
            {
                "ratchet": {"contradictions": 0},
                "discovery": {"ungoverned_directories": [".git"]},
            }
        ),
        encoding="utf-8",
    )

    def _refuse(_root: str):
        raise RuntimeError("the walk could not complete")

    monkeypatch.setattr(adapter, "artifacts", _refuse)
    monkeypatch.chdir(root)

    assert gate.main() == 2

    err = capsys.readouterr().err
    assert "FAULT — the measurement did not complete" in err
    assert "RuntimeError" in err


def test_the_module_entry_point_runs_the_gate_and_exits_with_its_code(
    tmp_path, monkeypatch
) -> None:
    """``python -m engine.substrate`` IS ONE OF THE TWO DECLARED INVOCATION PLANES.

    UEC-L-06 requires two, and a test already asserts that both the Makefile and the workflow
    NAME the gate — which is a claim about text. This is the claim about behaviour: the
    module runs the gate and exits with its code. The module body carries no ``__main__``
    guard, so it is executed by running it as a module rather than by importing it, which is
    also the only way the declared invocation is actually exercised.
    """
    root = _adapter_root(tmp_path)
    (tmp_path / "00-MASTER" / "UCOS-SUB-001" / "sub-declaration.json").write_text(
        json.dumps(
            {
                "ratchet": {"contradictions": 0},
                "discovery": {"ungoverned_directories": [".git", "__pycache__"]},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(root)

    with pytest.raises(SystemExit) as raised:
        runpy.run_module("engine.substrate", run_name="__main__")

    assert raised.value.code == 0

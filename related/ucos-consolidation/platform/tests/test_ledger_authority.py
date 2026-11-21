"""UCOS-LEDGER-AUTHORITY-001 — the one identity-ledger write chokepoint.

The defect these tests exist for (D0.1): `uga_engine.py run` printed
``identity ledger updated: 0 minted`` while permanently allocating ``UCOS-OBS-000007``
and advancing the shared ``category_seq``. Nothing miscounted. The run reported from
``epoch1_identity``, which counts ``by_object`` only, while the SAME write persisted the
``by_observation`` identities minted elsewhere. Allocation scope and reporting scope were
different scopes, so a caller-side counter could only ever measure the allocations that
caller happened to know about.

``ledger_authority.commit`` derives the report from the difference between the on-disk
pre-image and the ledger about to be written, so the report is a property of the bytes
rather than of the caller's bookkeeping. These tests hold that property:

* :func:`test_the_authority_is_the_only_ledger_writer` — structural. No tracked source
  outside the authority may name the ledger in a write call.
* :func:`test_an_allocation_can_never_be_reported_as_nothing` — the D0.1 shape itself,
  replayed: a write that allocates only ``by_observation``.
* the append-only refusals — a permanent identifier may not be forgotten, reissued, or
  have its counter rewound.

Every test writes to ``tmp_path``. Nothing here can touch the real ledger.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "00-BOOK" / "tools"

#: The authority's own path, named once. It is an ordinary importable package now — it was
#: `00-BOOK/tools/ledger_authority.py`, where no coverage source could name it, no authority
#: claimed it and Ω-3 measured the one allocation chokepoint as unreachable code.
AUTHORITY_REL = "engine/ledger_authority/__init__.py"
AUTHORITY_SOURCE = REPO / AUTHORITY_REL

import importlib.util  # noqa: E402

from engine import ledger_authority as LA  # noqa: E402
from engine.omega_infinite import git_provider  # noqa: E402


def _write(tmp_path: Path, obj: dict) -> str:
    path = tmp_path / "id-ledger.json"
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return str(path)


def _writer(path, ledger):
    """A minimal stand-in for each caller's own serializer."""

    Path(path).write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def _issue(path, ledger, actor="test", **overrides):
    """Issue a permit for exactly what ``plan()`` measures — the real operator workflow.

    Deliberately derived from ``plan()`` rather than hand-built: a test that constructed
    a digest independently would be asserting that two implementations agree, which is the
    very thing the design removes.
    """

    manifest = LA.plan(path, ledger, actor=actor)
    permit = {
        "permit_id": "P-TEST",
        "actor": actor,
        "manifest_digest": manifest["digest"],
        "preimage_digest": manifest["preimage_digest"],
        "head": manifest["head"],
        "scope": {
            "maps": sorted(manifest["allocated"]),
            "max_allocations": manifest["total_allocations"],
        },
        "expires_at": None,
        "single_use": True,
    }
    permit.update(overrides)
    Path(LA.permit_register_path(path)).write_text(
        json.dumps({"permits": [permit]}), encoding="utf-8"
    )
    return permit["permit_id"]


# ---------------------------------------------------------------------------------------
# structural: the chokepoint is the ONLY writer


# The invariant's vocabulary, kept identical to LEDGER-INV-01 in uga_engine.py. The
# `(?<![A-Z_])` guard is load-bearing: without it CHANGE_LEDGER_PATH (a derived view,
# not the identity ledger) matches on the substring and the guard fails on the wrong file.
_LEDGER_REF = r"(?:(?<![A-Z_])LEDGER_PATH\b|id-ledger\.json)"
_PY_WRITE = re.compile(
    r"(?:_dump_json|_dump|_write_text|_atomic_write|json\.dump|write_text|os\.replace)"
    r"\s*\(\s*[^\n]{0,120}?" + _LEDGER_REF
)
_PY_OPEN = re.compile(r"open\s*\(\s*[^\n]{0,120}?" + _LEDGER_REF + r"[^\n]{0,60}?['\"][wax]")
_SH_WRITE = re.compile(r"(?:>>?|\btee\b)\s*[^\n|;&]{0,80}?id-ledger\.json")


def _tracked_sources() -> list[str]:
    raw = subprocess.run(  # noqa: S603
        ["git", "ls-files", "-z"],  # noqa: S607 - resolved from PATH, as CI does
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return [f for f in raw.split("\0") if f.endswith((".py", ".sh"))]


def test_the_authority_is_the_only_ledger_writer() -> None:
    """Structural. A fifth writer is a test failure, not a discovery made afterwards.

    Lexical rather than import-based on purpose: the failure being prevented is a NEW
    direct write, and a new direct write is visible in the source text before it is ever
    executed. A file naming the ledger inside a write primitive is a second write path
    regardless of how it is reached at run time.
    """
    sources = _tracked_sources()
    assert len(sources) > 500, "the tracked-source scan collapsed; the guard would be vacuous"

    violations: list[str] = []
    for rel in sources:
        if rel == AUTHORITY_REL:
            continue  # the authority is the sanctioned write path
        try:
            lines = (REPO / rel).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        patterns = (_SH_WRITE,) if rel.endswith(".sh") else (_PY_WRITE, _PY_OPEN)
        for number, line in enumerate(lines, 1):
            if any(p.search(line) for p in patterns):
                violations.append(f"{rel}:{number}: {line.strip()[:100]}")

    assert not violations, (
        "identity-ledger write outside UCOS-LEDGER-AUTHORITY-001:\n  "
        + "\n  ".join(violations)
        + f"\nRoute it through {AUTHORITY_REL}::commit so the allocation is measured "
        "against the on-disk pre-image."
    )


# The probe strings below are ASSEMBLED FROM FRAGMENTS, and that is load-bearing rather
# than fussy. Written literally, each one is itself a direct-write match, so once this
# file is tracked the guard above would report three violations against its own source —
# the certifier failing the repository it certifies. Splitting the two ledger tokens keeps
# every RUNTIME string byte-identical while no LINE of this file matches. The alternative,
# exempting test files from LEDGER-INV-01, would carve a hole exactly where a future
# direct write is most likely to be introduced and least likely to be noticed.
_LEDGER_CONST = "LEDGER" + "_PATH"
_LEDGER_FILE = "id-" + "ledger.json"


@pytest.mark.parametrize(
    "line",
    [
        f"_dump_json({_LEDGER_CONST}, ledger)",
        f'_dump({_LEDGER_CONST}, st["ledger"])',
        f'json.dump(ledger, open("00-BOOK/DATA/{_LEDGER_FILE}", "w"))',
    ],
)
def test_the_structural_guard_actually_matches_a_direct_write(line: str) -> None:
    """Non-vacuity. A guard that matches nothing would pass on a repository full of writes."""
    assert _PY_WRITE.search(line) or _PY_OPEN.search(line), f"guard blind to: {line}"


def test_the_guard_does_not_confuse_the_change_ledger_for_the_identity_ledger() -> None:
    """`change-ledger.json` is a DERIVED view; writing it is not an allocation."""
    assert not _PY_WRITE.search("_dump_json(CHANGE_LEDGER_PATH, change_ledger)")


# ---------------------------------------------------------------------------------------
# the D0.1 defect itself


def test_an_allocation_can_never_be_reported_as_nothing(tmp_path: Path) -> None:
    """The exact D0.1 shape: allocate an OBSERVATION while the caller counts OBJECTS.

    The old report was a caller-side `by_object` count, which is 0 here — and the run
    printed `0 minted` while `UCOS-OBS-000007` became permanent. The report must be
    derived from the pre-image instead, so this cannot be summarised as nothing.
    """
    before = {"category_seq": {"OBS": 6}, "by_object": {"a.py": {"universal_id": "UCOS-OBJ-1"}}}
    path = _write(tmp_path, before)
    after = {
        "category_seq": {"OBS": 7},
        "by_object": {"a.py": {"universal_id": "UCOS-OBJ-1"}},  # unchanged: caller counts 0
        "by_observation": {"k": {"observation_id": "UCOS-OBS-000007"}},
    }

    report = LA.commit(path, after, actor="test", writer=_writer, permit=_issue(path, after))

    assert report["allocating"] is True
    assert report["total_allocations"] == 1
    assert report["allocated"]["by_observation"] == ["UCOS-OBS-000007"]
    assert report["counter_advances"] == {"OBS": [6, 7]}
    assert report["bytes_changed"] is True

    line = LA.format_report(report)
    assert "no allocation" not in line, "the D0.1 message is representable again"
    assert "UCOS-OBS" not in line or "ALLOCATED 1" in line
    assert "ALLOCATED 1" in line and "category_seq(OBS:6->7)" in line


def test_a_genuine_no_op_is_still_reported_as_no_allocation(tmp_path: Path) -> None:
    """The converse. The report must not cry allocation when the bytes did not move."""
    state = {"category_seq": {"OBS": 6}, "by_object": {"a.py": {"universal_id": "UCOS-OBJ-1"}}}
    path = _write(tmp_path, state)
    report = LA.commit(path, dict(state), actor="test", writer=_writer, permit=LA.NO_ALLOCATION)
    assert report["allocating"] is False
    assert report["total_allocations"] == 0
    assert "no allocation" in LA.format_report(report)


@pytest.mark.parametrize(
    ("map_name", "field", "identifier"),
    [
        ("by_path", "universal_id", "UCOS-DOC-000009"),
        ("by_object", "universal_id", "UCOS-OBJ-000009"),
        ("by_execution", "execution_id", "UCOS-EXE-000009"),
        ("by_observation", "observation_id", "UCOS-OBS-000009"),
    ],
)
def test_every_identity_map_is_measured(
    tmp_path: Path, map_name: str, field: str, identifier: str
) -> None:
    """Each of the four maps a writer can touch is counted, not just the caller's own."""
    path = _write(tmp_path, {})
    proposed = {map_name: {"k": {field: identifier}}}
    report = LA.commit(path, proposed, actor="test", writer=_writer, permit=_issue(path, proposed))
    assert report["allocated"] == {map_name: [identifier]}
    assert report["total_allocations"] == 1


def test_an_unknown_identity_map_is_surfaced_rather_than_counted_as_zero(
    tmp_path: Path,
) -> None:
    """A fifth kind of allocation must not inherit the no-op message.

    This is the property that makes the fix survive the next writer: an allocation this
    module cannot yet count is reported as an unknown, never summarised as nothing.
    """
    path = _write(tmp_path, {})
    proposed = {"by_covenant": {"k": {"covenant_id": "X-1"}}}
    report = LA.commit(path, proposed, actor="test", writer=_writer, permit=_issue(path, proposed))
    assert report["total_allocations"] == 0
    assert report["allocating"] is True, "an unmeasured map was summarised as no allocation"
    assert report["unmeasured_maps"] == ["by_covenant"]
    assert "UNMEASURED_MAPS" in LA.format_report(report)
    assert "no allocation" not in LA.format_report(report)


# ---------------------------------------------------------------------------------------
# append-only refusals


@pytest.mark.parametrize(
    ("before", "after", "expected"),
    [
        (
            {"by_object": {"a": {"universal_id": "U-1"}}},
            {"by_object": {}},
            "REMOVED",
        ),
        (
            {"by_object": {"a": {"universal_id": "U-1"}}},
            {"by_object": {"a": {"universal_id": "U-2"}}},
            "REISSUED",
        ),
        (
            {"category_seq": {"OBS": 7}},
            {"category_seq": {"OBS": 6}},
            "REGRESS",
        ),
        (
            {"page_cursor": 12507},
            {"page_cursor": 12000},
            "REGRESS",
        ),
    ],
)
def test_append_only_violations_are_refused(
    tmp_path: Path, before: dict, after: dict, expected: str
) -> None:
    path = _write(tmp_path, before)
    with pytest.raises(LA.LedgerWriteRefused, match=expected):
        LA.commit(path, after, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)


def test_a_refused_write_never_reaches_the_writer(tmp_path: Path) -> None:
    """Fail-closed ordering: the pre-image is checked BEFORE the file can be touched.

    If the refusal happened after the write, a rejected transaction would still have
    made the damage permanent — which is the whole property being bought here.
    """
    path = _write(tmp_path, {"by_object": {"a": {"universal_id": "U-1"}}})
    original = Path(path).read_bytes()
    calls: list[object] = []

    def spy(p, ledger):
        calls.append(p)
        _writer(p, ledger)

    with pytest.raises(LA.LedgerWriteRefused):
        LA.commit(path, {"by_object": {}}, actor="test", writer=spy, permit=LA.NO_ALLOCATION)

    assert calls == [], "the writer ran despite the refusal"
    assert Path(path).read_bytes() == original, "a refused write still changed the ledger"


def test_an_unreadable_ledger_is_refused_not_treated_as_empty(tmp_path: Path) -> None:
    """Treating corruption as {} would report every existing identity as freshly minted."""
    path = tmp_path / "id-ledger.json"
    path.write_text("{ this is not json", encoding="utf-8")
    with pytest.raises(LA.LedgerWriteRefused, match="cannot be read"):
        LA.commit(str(path), {}, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)


def test_a_missing_ledger_is_a_legitimate_first_mint(tmp_path: Path) -> None:
    """A first-ever allocation has no pre-image; that is not corruption."""
    path = str(tmp_path / "id-ledger.json")
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    report = LA.commit(path, proposed, actor="test", writer=_writer, permit=_issue(path, proposed))
    assert report["allocated"] == {"by_object": ["U-1"]}
    assert report["bytes_changed"] is True


# ---------------------------------------------------------------------------------------
# AUTHORIZATION — permit enforcement at the chokepoint (Phase 2C)
#
# The property under test: an allocation cannot occur through any path unless a permit
# survives verification INSIDE commit(). Every test writes to tmp_path; none can reach
# the real ledger.


def test_omitting_the_permit_is_a_type_error(tmp_path: Path) -> None:
    """The loudest possible failure, and the reason `permit` has no default.

    A default of None would turn this TypeError — raised at the call site before any
    measurement runs — into a silent bypass. That is the single likeliest way this
    control could be lost, so it is pinned here.
    """
    path = _write(tmp_path, {})
    with pytest.raises(TypeError, match="permit"):
        LA.commit(path, {}, actor="test", writer=_writer)  # type: ignore[call-arg]


@pytest.mark.parametrize("bad", [None, "", 0, [], {}, True])
def test_a_non_permit_is_refused(tmp_path: Path, bad: object) -> None:
    """None is not a pass. Neither is any other falsy or wrong-typed value."""
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    with pytest.raises(LA.PermitRefused):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=bad)


def test_an_allocation_without_a_permit_never_reaches_the_writer(tmp_path: Path) -> None:
    """Fail-closed ordering, now for authorization as well as append-only."""
    path = _write(tmp_path, {"by_object": {"a": {"universal_id": "U-1"}}})
    original = Path(path).read_bytes()
    calls: list[object] = []

    def spy(p, ledger):
        calls.append(p)
        _writer(p, ledger)

    proposed = {"by_object": {"a": {"universal_id": "U-1"}, "b": {"universal_id": "U-2"}}}
    with pytest.raises(LA.PermitRefused):
        LA.commit(path, proposed, actor="test", writer=spy, permit="does-not-exist")

    assert calls == [], "the writer ran despite an unauthorized allocation"
    assert Path(path).read_bytes() == original


def test_a_false_no_allocation_claim_is_refused(tmp_path: Path) -> None:
    """NO_ALLOCATION is a CLAIM, checked against the measurement — never a bypass."""
    path = _write(tmp_path, {"category_seq": {"OBS": 6}})
    proposed = {
        "category_seq": {"OBS": 7},
        "by_observation": {"k": {"observation_id": "UCOS-OBS-000007"}},
    }
    with pytest.raises(LA.PermitRefused, match="ALLOCATES"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)
    assert "by_observation" not in json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_permit_is_self_invalidating(tmp_path: Path) -> None:
    """Replay control with no spent-permit registry.

    Performing the allocation moves the pre-image, so recomputing the binding no longer
    matches. Spent-ness is DERIVED from the ledger and the register, both already
    committed — there is no third artifact and no second mutable authority.
    """
    path = _write(tmp_path, {"category_seq": {"OBS": 6}})
    proposed = {
        "category_seq": {"OBS": 7},
        "by_observation": {"k": {"observation_id": "UCOS-OBS-000007"}},
    }
    permit_id = _issue(path, proposed)

    first = LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)
    assert first["total_allocations"] == 1
    assert first["authorization"] == "PERMIT"

    with pytest.raises(LA.PermitRefused, match="preimage_digest"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)


def test_a_permit_does_not_authorize_a_different_actor(tmp_path: Path) -> None:
    """A permit for UGA objects must not be spendable on a corpus mint."""
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, actor="UCOS-UGA-001")
    with pytest.raises(LA.PermitRefused, match="actor"):
        LA.commit(path, proposed, actor="UMB-IMP-001", writer=_writer, permit=permit_id)


def test_a_permit_does_not_authorize_a_larger_allocation(tmp_path: Path) -> None:
    """THE D0.1 control: authorized scope and executed scope must be the same object.

    A permit is obtained for one identity, then two are allocated. The recomputed digest
    differs, so the write is refused — an allocation can never exceed the one disclosed.
    """
    path = _write(tmp_path, {})
    small = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, small)

    larger = {"by_object": {"a": {"universal_id": "U-1"}, "b": {"universal_id": "U-2"}}}
    with pytest.raises(LA.PermitRefused, match="manifest_digest"):
        LA.commit(path, larger, actor="test", writer=_writer, permit=permit_id)
    assert json.loads(Path(path).read_text(encoding="utf-8")) == {}


def test_a_permit_bound_to_another_head_is_refused(tmp_path: Path) -> None:
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, head="0" * 40)
    with pytest.raises(LA.PermitRefused, match="head"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)


def test_an_expired_permit_is_refused(tmp_path: Path) -> None:
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, expires_at="2000-01-01T00:00:00Z")
    with pytest.raises(LA.PermitRefused, match="expired"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)


def test_a_permit_whose_scope_omits_the_touched_map_is_refused(tmp_path: Path) -> None:
    """`scope` is verified independently of the digest.

    The digest already binds exactly; scope exists because a human cannot read a digest.
    A permit whose stated scope disagrees with what it approves is malformed, and saying
    so by name is what makes the refusal reviewable.
    """
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, scope={"maps": ["by_execution"], "max_allocations": 9})
    with pytest.raises(LA.PermitRefused, match="scope"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)


def test_an_unreadable_permit_register_is_refused_not_ignored(tmp_path: Path) -> None:
    """A register that cannot be parsed cannot be shown to contain the claimed permit."""
    path = _write(tmp_path, {})
    Path(LA.permit_register_path(path)).write_text("{ not json", encoding="utf-8")
    with pytest.raises(LA.PermitRefused, match="cannot be read"):
        LA.commit(
            path,
            {"by_object": {"a": {"universal_id": "U-1"}}},
            actor="test",
            writer=_writer,
            permit="P-TEST",
        )


def test_a_missing_permit_register_is_empty_not_open(tmp_path: Path) -> None:
    path = _write(tmp_path, {})
    assert LA.load_permit_register(path) == []
    with pytest.raises(LA.PermitRefused, match="not in"):
        LA.commit(
            path,
            {"by_object": {"a": {"universal_id": "U-1"}}},
            actor="test",
            writer=_writer,
            permit="P-TEST",
        )


def test_a_duplicated_permit_id_is_refused(tmp_path: Path) -> None:
    """An ambiguous authorization is no authorization."""
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed)
    register = json.loads(Path(LA.permit_register_path(path)).read_text(encoding="utf-8"))
    register["permits"].append(dict(register["permits"][0]))
    Path(LA.permit_register_path(path)).write_text(json.dumps(register), encoding="utf-8")
    with pytest.raises(LA.PermitRefused, match="ambiguous"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)


# ---------------------------------------------------------------------------------------
# preview: one measurement shared by preview, authorization and execution


def test_plan_writes_nothing(tmp_path: Path) -> None:
    before = {"category_seq": {"OBS": 6}}
    path = _write(tmp_path, before)
    original = Path(path).read_bytes()
    LA.plan(
        path,
        {"category_seq": {"OBS": 7}, "by_observation": {"k": {"observation_id": "X"}}},
        actor="test",
    )
    assert Path(path).read_bytes() == original
    assert not Path(LA.permit_register_path(path)).exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["id-ledger.json"]


def test_plan_and_commit_measure_the_same_allocation(tmp_path: Path) -> None:
    """D0.1 closure: preview scope, authorized scope and executed scope are one object.

    Both call ``build_manifest`` → ``allocation_report`` with the same arguments, so a
    divergence would require them to stop sharing that function — which this detects.
    """
    path = _write(tmp_path, {"category_seq": {"OBS": 6}})
    proposed = {
        "category_seq": {"OBS": 7},
        "by_observation": {"k": {"observation_id": "UCOS-OBS-000007"}},
    }
    previewed = LA.plan(path, proposed, actor="test")
    executed = LA.commit(
        path, proposed, actor="test", writer=_writer, permit=_issue(path, proposed)
    )
    for field in (
        "allocated",
        "counter_advances",
        "cursor_advances",
        "unmeasured_maps",
        "total_allocations",
        "allocating",
    ):
        assert previewed[field] == executed[field], f"preview and execution differ on {field}"
    assert previewed["digest"] == executed["digest"]


def test_the_measurement_has_exactly_one_implementation() -> None:
    """Structural: no second allocation-report implementation may exist.

    A duplicate measurement is a duplicate SCOPE, and divergent scopes ARE D0.1.
    """
    source = AUTHORITY_SOURCE.read_text(encoding="utf-8")
    assert source.count("def allocation_report(") == 1
    assert source.count("def build_manifest(") == 1
    # plan() and commit() must each reach the measurement through build_manifest, and
    # neither may call allocation_report directly.
    tree = ast.parse(source)
    for name in ("plan", "commit"):
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        called = {ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)}
        assert "build_manifest" in called, f"{name}() no longer routes through build_manifest"
        assert (
            "allocation_report" not in called
        ), f"{name}() calls allocation_report directly, bypassing the shared manifest"


# =======================================================================================
# PHASE 1 — governance-independent remediation (R-1 … R-11).
#
# Specified by PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md §E. Every test below is
# either a REPRODUCTION (asserts the fixed behaviour, so it fails before its unit lands)
# or a REGRESSION (asserts behaviour correct before AND after, so it must never go red).
#
# Each defect ID names a finding in PHASE0-E1-ATOMICITY-REPORT.md /
# PHASE0-E2-CORRESPONDENCE-REPORT.md. No test below asserts anything about who may
# authorize a write, what a permit means, or when one expires: every predicate is a
# function of (pre-image, proposed document, persisted bytes).
# =======================================================================================

_HIST = {"UCOS-OBJ-000001": [{"seq": 1, "at": "t0", "content_hash": "h0"}]}


def _base(history: bool = True) -> dict:
    """A minimal ledger of the shape the production ledger actually has.

    `history` is a PARAMETER, not a constant, because E1-F5 MASKS the
    NO_ALLOCATION-path reproductions of E1-F4 and E2-F4 on any ledger carrying it:
    an unclassified top-level map makes `allocating` true, so the write is refused
    for UNMEASURED_MAPS before the defect under test is ever evaluated. Phase 0.5
    §D.4 records this as a fixture constraint rather than a dependency edge.
    """
    doc = {
        "version": 1,
        "category_seq": {"OBJ": 1},
        "by_object": {
            "a.py": {
                "universal_id": "UCOS-OBJ-000001",
                "object_class": "TOOLING_OBJECT",
                "first_seen": "commit:aaaa",
            }
        },
    }
    if history:
        doc["history"] = json.loads(json.dumps(_HIST))
    return doc


def _plus_one(base: dict) -> dict:
    """The same ledger with ONE further object identity allocated."""
    after = json.loads(json.dumps(base))
    after["category_seq"]["OBJ"] = 2
    after["by_object"]["b.py"] = {
        "universal_id": "UCOS-OBJ-000002",
        "object_class": "TOOLING_OBJECT",
        "first_seen": "commit:bbbb",
    }
    return after


# ---------------------------------------------------------------------------------------
# R-1 / E1-F7 — the pre-image is ONE read, shared by verification and measurement


def test_the_parsed_and_raw_preimages_come_from_one_read(tmp_path: Path) -> None:
    """REPRODUCTION. Two unreconciled reads of one file ARE the window (E1-F1)."""
    path = _write(tmp_path, _base())
    raw, doc = LA.read_preimage_bytes(path)
    assert raw is not None
    assert json.loads(raw.decode("utf-8")) == doc, "the two views disagree"


def test_a_missing_ledger_still_reads_as_an_empty_preimage(tmp_path: Path) -> None:
    """REGRESSION. E1-S4: a missing ledger is a legitimate first mint, not an error."""
    raw, doc = LA.read_preimage_bytes(str(tmp_path / "absent.json"))
    assert raw is None
    assert doc == {}


def test_commit_reaches_the_preimage_through_exactly_one_reader() -> None:
    """REPRODUCTION, structural. `commit()` must not read the ledger twice.

    Asserted by AST rather than by counting `open` calls, because R-2 deliberately
    adds a THIRD read — the pre-write re-check — and a bare count cannot distinguish
    "one pre-image read plus one re-check" from "two unreconciled pre-image reads".
    The property R-1 establishes is that verification and the change measurement
    share ONE observation, and that is what is asserted here.
    """
    source = AUTHORITY_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "commit")
    called = [ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)]
    assert called.count("read_preimage_bytes") == 1, (
        "commit() must obtain the pre-image exactly once; got "
        f"{called.count('read_preimage_bytes')} calls"
    )
    assert "load_preimage" not in called, (
        "commit() calls load_preimage, which is a SECOND read of the same file that "
        "nothing reconciles with the raw pre-image — this is E1-F7"
    )


# ---------------------------------------------------------------------------------------
# R-2 / E1-F1 — a write that lands inside the verification window is refused


def test_a_concurrent_write_inside_the_verification_window_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """REPRODUCTION. The E1-F1 probe: inject the rival at the git_head subprocess.

    `git_head` is where commit() yields the CPU (a 15 s-timeout fork inside the
    window), so it is the realistic injection point rather than a contrived one.
    """
    base = _base()
    path = _write(tmp_path, base)
    after = _plus_one(base)
    permit_id = _issue(path, after)
    real_git_head, fired = LA.git_head, []

    def hijack(near):
        if not fired:  # the concurrent actor, inside MW-1
            fired.append(1)
            rival = json.loads(json.dumps(base))
            rival["category_seq"]["OBJ"] = 2
            rival["by_object"]["z.py"] = {
                "universal_id": "UCOS-OBJ-000002",
                "object_class": "TOOLING_OBJECT",
                "first_seen": "commit:zzzz",
            }
            _writer(path, rival)
        return real_git_head(near)

    monkeypatch.setattr(LA, "git_head", hijack)
    with pytest.raises(LA.LedgerWriteRefused, match="changed between verification and write"):
        LA.commit(path, after, actor="test", writer=_writer, permit=permit_id)

    on_disk = json.loads(Path(path).read_text(encoding="utf-8"))
    assert (
        "z.py" in on_disk["by_object"]
    ), "a permanent identifier already persisted by another writer was destroyed"


def test_a_single_writer_is_unaffected_by_the_recheck(tmp_path: Path) -> None:
    """REGRESSION. The re-read must not refuse when nothing else touched the file."""
    base = _base()
    path = _write(tmp_path, base)
    after = _plus_one(base)
    report = LA.commit(path, after, actor="test", writer=_writer, permit=_issue(path, after))
    assert report["total_allocations"] == 1
    assert report["bytes_changed"] is True
    assert sorted(json.loads(Path(path).read_text(encoding="utf-8"))["by_object"]) == [
        "a.py",
        "b.py",
    ]


# ---------------------------------------------------------------------------------------
# R-3 / E1-F2 — two commits cannot interleave


def test_two_commits_cannot_interleave(tmp_path: Path) -> None:
    """REPRODUCTION. Real mutual exclusion, measured across processes.

    `history` is omitted so this test verifies R-3 independently of R-5 (Phase 0.5
    §D.3: R-3 has no predecessor and must be verifiable alone).
    """
    path = _write(tmp_path, _base(history=False))
    marker = tmp_path / "order.log"
    script = textwrap.dedent(
        f"""
        import sys, json, time, pathlib
        sys.path.insert(0, {str(REPO)!r})
        from engine import ledger_authority as LA
        path, marker, tag = {str(path)!r}, {str(marker)!r}, sys.argv[1]
        def writer(p, o):
            with open(marker, "a") as fh:
                fh.write(tag + "-enter\\n")
            time.sleep(0.5)
            pathlib.Path(p).write_text(json.dumps(o, indent=2) + "\\n", encoding="utf-8")
            with open(marker, "a") as fh:
                fh.write(tag + "-exit\\n")
        with open(path) as fh:
            doc = json.load(fh)
        LA.commit(path, doc, actor="test", writer=writer, permit=LA.NO_ALLOCATION)
        """
    )
    procs = [
        subprocess.Popen(  # noqa: S603
            [sys.executable, "-c", script, tag], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        for tag in ("A", "B")
    ]
    for proc in procs:
        out, err = proc.communicate(timeout=120)
        assert proc.returncode == 0, err.decode()

    order = marker.read_text(encoding="utf-8").split()
    assert order in (
        ["A-enter", "A-exit", "B-enter", "B-exit"],
        ["B-enter", "B-exit", "A-enter", "A-exit"],
    ), f"the two commits interleaved: {order}"


def test_a_lock_timeout_refuses_rather_than_proceeding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """REGRESSION. Contention must fail closed, never wait forever and never proceed."""
    fcntl = pytest.importorskip("fcntl")
    path = _write(tmp_path, _base(history=False))
    original = Path(path).read_bytes()
    monkeypatch.setattr(LA, "LEDGER_LOCK_TIMEOUT_SECONDS", 0.2)

    held = os.open(str(tmp_path), os.O_RDONLY)
    try:
        fcntl.flock(held, fcntl.LOCK_EX)
        with pytest.raises(LA.LedgerWriteRefused, match="lock"):
            LA.commit(
                path,
                json.loads(original.decode("utf-8")),
                actor="test",
                writer=_writer,
                permit=LA.NO_ALLOCATION,
            )
    finally:
        fcntl.flock(held, fcntl.LOCK_UN)
        os.close(held)
    assert Path(path).read_bytes() == original


# ---------------------------------------------------------------------------------------
# R-4 / E1-F4 — the record body of an existing identity is append-only in full


def test_a_record_body_rewrite_is_refused(tmp_path: Path) -> None:
    """REPRODUCTION. `object_class` and `first_seen` rewritten, identifier held constant."""
    base = _base(history=False)  # §D.4 — E1-F5 masks this on the production shape
    path = _write(tmp_path, base)
    forged = json.loads(json.dumps(base))
    forged["by_object"]["a.py"]["object_class"] = "GOVERNANCE_OBJECT"
    forged["by_object"]["a.py"]["first_seen"] = "commit:FORGED"

    with pytest.raises(LA.LedgerWriteRefused, match="REWRITTEN"):
        LA.commit(path, forged, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)

    landed = json.loads(Path(path).read_text(encoding="utf-8"))
    assert landed["by_object"]["a.py"]["object_class"] == "TOOLING_OBJECT"
    assert landed["by_object"]["a.py"]["first_seen"] == "commit:aaaa"


def test_a_new_records_body_is_unconstrained(tmp_path: Path) -> None:
    """REGRESSION. Only EXISTING records are frozen; a fresh allocation is not."""
    base = _base(history=False)
    path = _write(tmp_path, base)
    after = _plus_one(base)
    after["by_object"]["b.py"]["object_class"] = "GOVERNANCE_OBJECT"  # a new key
    report = LA.commit(path, after, actor="test", writer=_writer, permit=_issue(path, after))
    assert report["allocated"] == {"by_object": ["UCOS-OBJ-000002"]}


# ---------------------------------------------------------------------------------------
# R-5 / E1-F5 — `history` is classified, and its declared append-only property enforced


def test_a_byte_identical_write_allocates_nothing_on_a_ledger_with_history(
    tmp_path: Path,
) -> None:
    """REPRODUCTION (a). The production shape: today this reports allocating=True.

    `history` is in neither IDENTITY_MAPS nor NON_ALLOCATION_KEYS, so a byte-identical
    no-op measures as an allocation and NO_ALLOCATION is unconditionally refused
    against the real ledger — which is what makes ukb.py's idempotent exec-declare
    branch dead code.
    """
    base = _base()  # carries `history`
    path = _write(tmp_path, base)
    report = LA.commit(
        path,
        json.loads(json.dumps(base)),
        actor="test",
        writer=_writer,
        permit=LA.NO_ALLOCATION,
    )
    assert report["unmeasured_maps"] == []
    assert report["allocating"] is False
    assert report["bytes_changed"] is False


def test_history_erasure_is_refused(tmp_path: Path) -> None:
    """REPRODUCTION (b). The append-only property ukb.record_snapshots claims.

    Uses the PERMIT path deliberately: the refusal must fire regardless of
    authorization mode, not only under the no-allocation claim.
    """
    base = _base()
    path = _write(tmp_path, base)
    erased = json.loads(json.dumps(base))
    erased["history"] = {}

    with pytest.raises(LA.LedgerWriteRefused, match="history"):
        LA.commit(path, erased, actor="test", writer=_writer, permit=_issue(path, erased))

    assert json.loads(Path(path).read_text(encoding="utf-8"))["history"] == _HIST


def test_a_shortened_history_list_is_refused(tmp_path: Path) -> None:
    """REPRODUCTION (b). A snapshot list may only ever be extended."""
    base = _base()
    base["history"]["UCOS-OBJ-000001"].append({"seq": 2, "at": "t1", "content_hash": "h1"})
    path = _write(tmp_path, base)
    truncated = json.loads(json.dumps(base))
    truncated["history"]["UCOS-OBJ-000001"] = truncated["history"]["UCOS-OBJ-000001"][:1]

    with pytest.raises(LA.LedgerWriteRefused, match="not an extension"):
        LA.commit(path, truncated, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)


def test_a_history_append_is_accepted_under_a_permit(tmp_path: Path) -> None:
    """REGRESSION. The real `ukb build --mint` shape: history grows, nothing else moves.

    This is the case that must NOT become unauthorizable. Before R-5 it required a
    permit (allocating=True for UNMEASURED_MAPS); after R-5 it still requires one
    (the document differs from the pre-image, so NO_ALLOCATION is false). Nothing
    that needed a permit stops needing one.
    """
    base = _base()
    path = _write(tmp_path, base)
    grown = json.loads(json.dumps(base))
    grown["history"]["UCOS-OBJ-000001"].append({"seq": 2, "at": "t1", "content_hash": "h1"})

    report = LA.commit(path, grown, actor="test", writer=_writer, permit=_issue(path, grown))
    assert report["allocating"] is False
    assert report["total_allocations"] == 0
    assert report["bytes_changed"] is True
    landed = json.loads(Path(path).read_text(encoding="utf-8"))
    assert len(landed["history"]["UCOS-OBJ-000001"]) == 2


def test_history_is_classified_exactly_once() -> None:
    """REGRESSION, structural. `history` must be in exactly one classification set."""
    assert "history" in LA.NON_ALLOCATION_KEYS
    assert "history" not in LA.IDENTITY_MAPS


# ---------------------------------------------------------------------------------------
# R-6 / E1-F6 — a permanent identifier names at most one thing


@pytest.mark.parametrize("second_map", ["by_object", "by_observation"])
def test_a_duplicate_identifier_is_refused(tmp_path: Path, second_map: str) -> None:
    """REPRODUCTION. Within a map and ACROSS maps — the four share one category_seq."""
    base = _base(history=False)
    path = _write(tmp_path, base)
    collide = json.loads(json.dumps(base))
    if second_map == "by_object":
        collide["by_object"]["c.py"] = {
            "universal_id": "UCOS-OBJ-000001",
            "object_class": "TOOLING_OBJECT",
            "first_seen": "commit:ccc",
        }
    else:
        collide["by_observation"] = {
            "k": {
                "observation_id": "UCOS-OBJ-000001",
                "observer": "o",
                "subject": "s",
                "kind": "K",
                "first_seen": "t",
            }
        }

    with pytest.raises(LA.LedgerWriteRefused, match="bound to BOTH"):
        LA.commit(path, collide, actor="test", writer=_writer, permit=_issue(path, collide))


def test_the_mw3_interleaving_is_refused_by_two_independent_legs(tmp_path: Path) -> None:
    """REPRODUCTION. E1-F6's UNVERIFIABLE window, made verifiable by naming the leg.

    Leg 1 — key removal: the late proposal is missing the rival's key.
    Leg 2 — duplicate identifier: one identifier bound to two keys.
    Today only leg 1 fires, so the property rests on a single check; asserting both
    is the point of the test.
    """
    base = _base(history=False)
    path = _write(tmp_path, base)
    late = _plus_one(base)  # computed against base: b.py -> …002
    rival = _plus_one(base)
    rival["by_object"]["z.py"] = rival["by_object"].pop("b.py")  # rival took …002
    _writer(path, rival)  # the rival's bytes land first

    with pytest.raises(LA.LedgerWriteRefused) as exc:
        LA.commit(path, late, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)
    assert "REMOVED" in str(exc.value), "leg 1 (key removal) no longer fires"

    merged = json.loads(json.dumps(rival))  # a proposal that PRESERVES the rival's key
    merged["by_object"]["b.py"] = {
        "universal_id": "UCOS-OBJ-000002",
        "object_class": "TOOLING_OBJECT",
        "first_seen": "commit:bbbb",
    }
    with pytest.raises(LA.LedgerWriteRefused, match="bound to BOTH"):
        LA.commit(path, merged, actor="test", writer=_writer, permit=_issue(path, merged))


def test_the_live_ledger_has_no_duplicate_identifiers() -> None:
    """REGRESSION, backward compatibility. Read-only against the production ledger."""
    ledger = json.loads((REPO / "00-BOOK" / "DATA" / "id-ledger.json").read_text(encoding="utf-8"))
    seen: dict[object, str] = {}
    for map_name, field in LA.IDENTITY_MAPS.items():
        for key, record in (ledger.get(map_name) or {}).items():
            ident = record.get(field) if isinstance(record, dict) else record
            assert ident not in seen, f"{ident!r} in both {seen.get(ident)} and {map_name}[{key!r}]"
            seen[ident] = f"{map_name}[{key!r}]"
    assert len(seen) > 5000, "the uniqueness scan collapsed; the guard would be vacuous"


# ---------------------------------------------------------------------------------------
# R-7 / E2-F1, E2-F2 — the persisted document must equal the authorized document


def test_a_divergent_writer_is_refused(tmp_path: Path) -> None:
    """REPRODUCTION (E2-F1). A writer that persists a different document.

    Today this returns authorization=PERMIT with no error while three permanent
    identifiers land on disk, only one of which any manifest measured.
    """
    base = _base()
    path = _write(tmp_path, base)
    after = _plus_one(base)
    permit_id = _issue(path, after)
    original = Path(path).read_bytes()

    def divergent(p, obj):
        forged = json.loads(json.dumps(obj))
        forged["by_object"]["b.py"]["universal_id"] = "UCOS-OBJ-999999"
        forged["by_object"]["EXTRA.py"] = {
            "universal_id": "UCOS-OBJ-000003",
            "object_class": "TOOLING_OBJECT",
            "first_seen": "commit:xxx",
        }
        forged["category_seq"]["OBJ"] = 3
        _writer(p, forged)

    with pytest.raises(LA.LedgerWriteRefused, match="not the authorized document"):
        LA.commit(path, after, actor="test", writer=divergent, permit=permit_id)

    assert Path(path).read_bytes() == original, "the pre-image was not restored"


def test_a_silent_writer_is_refused(tmp_path: Path) -> None:
    """REPRODUCTION (E2-F2). Reports ALLOCATED 1 while the disk is unchanged."""
    base = _base()
    path = _write(tmp_path, base)
    after = _plus_one(base)
    permit_id = _issue(path, after)
    original = Path(path).read_bytes()

    with pytest.raises(LA.LedgerWriteRefused):
        LA.commit(path, after, actor="test", writer=lambda p, o: None, permit=permit_id)

    assert Path(path).read_bytes() == original


def test_a_writer_that_removes_the_file_is_refused(tmp_path: Path) -> None:
    """REPRODUCTION (E2-F2). An absent file after the write is not a success."""
    base = _base()
    path = _write(tmp_path, base)
    after = _plus_one(base)
    permit_id = _issue(path, after)

    with pytest.raises(LA.LedgerWriteRefused, match="persisted nothing"):
        LA.commit(path, after, actor="test", writer=lambda p, o: os.remove(p), permit=permit_id)

    assert Path(path).exists(), "the pre-image was not restored"


def test_a_writer_that_persists_unparseable_content_is_refused(tmp_path: Path) -> None:
    """REPRODUCTION (E2-F1). Bytes that are not a document cannot be the document."""
    base = _base()
    path = _write(tmp_path, base)
    after = _plus_one(base)
    permit_id = _issue(path, after)
    original = Path(path).read_bytes()

    def garbage(p, o):
        Path(p).write_text("{ not json", encoding="utf-8")

    with pytest.raises(LA.LedgerWriteRefused, match="unparseable"):
        LA.commit(path, after, actor="test", writer=garbage, permit=permit_id)

    assert Path(path).read_bytes() == original


def test_a_first_mint_that_the_writer_drops_leaves_no_file(tmp_path: Path) -> None:
    """REGRESSION. The restore of an absent pre-image is removal, not an empty file."""
    path = str(tmp_path / "id-ledger.json")
    proposed = {"by_object": {"a.py": {"universal_id": "UCOS-OBJ-000001"}}}
    permit_id = _issue(path, proposed)

    with pytest.raises(LA.LedgerWriteRefused):
        LA.commit(path, proposed, actor="test", writer=lambda p, o: None, permit=permit_id)

    assert not Path(path).exists(), "a first mint that failed left a phantom ledger"


def test_both_production_writers_satisfy_the_post_write_check(tmp_path: Path) -> None:
    """REGRESSION. The guard that R-7 did not break production.

    Exercises the REAL serializers — ukb._dump_json and uga_engine._dump — rather
    than a restatement of their arguments.
    """
    for writer in _production_writers():
        base = _base()
        path = _write(tmp_path, base)
        after = _plus_one(base)
        report = LA.commit(path, after, actor="test", writer=writer, permit=_issue(path, after))
        assert report["total_allocations"] == 1, writer
        assert report["bytes_changed"] is True, writer
        assert json.loads(Path(path).read_text(encoding="utf-8")) == after, writer
        Path(path).unlink()
        Path(LA.permit_register_path(path)).unlink()


# ---------------------------------------------------------------------------------------
# R-8 / E2-F3 — bytes_changed is rendered, and the contradiction is refused


def test_the_operator_line_shows_whether_the_file_moved(tmp_path: Path) -> None:
    """REPRODUCTION. A measurement that exists is either enforced or shown."""
    base = _base()
    path = _write(tmp_path, base)
    after = _plus_one(base)
    report = LA.commit(path, after, actor="test", writer=_writer, permit=_issue(path, after))
    assert "bytes_changed=True" in LA.format_report(report)

    noop = LA.commit(
        path,
        json.loads(json.dumps(after)),
        actor="test",
        writer=_writer,
        permit=LA.NO_ALLOCATION,
    )
    assert "bytes_changed=False" in LA.format_report(noop)


def test_plan_output_still_renders_without_a_bytes_changed_field(tmp_path: Path) -> None:
    """REGRESSION. format_report is also called on plan() output and in a refusal.

    Two production sites pass a manifest with no `bytes_changed` key —
    ukb.py:1293 and uga_engine.py:1982 — plus _verify_permit's own refusal message.
    A bare subscript would turn all three into KeyError.
    """
    base = _base()
    path = _write(tmp_path, base)
    after = _plus_one(base)
    manifest = LA.plan(path, after, actor="test")
    assert "bytes_changed" not in manifest
    line = LA.format_report(manifest)  # must not raise
    assert "ALLOCATED 1" in line
    assert "bytes_changed" not in line


def test_an_allocation_that_did_not_move_the_file_is_refused() -> None:
    """REPRODUCTION, unit-level. `allocating` and `bytes_changed` cannot contradict.

    Called directly rather than through commit(), because after R-7 the state is
    UNREACHABLE through commit() (Phase 0.5 §D.5: persisted == ledger and
    raw_after == raw_before together imply before == ledger, hence allocating is
    false). A test that tried to reach it through commit() would be asserting
    against R-7's refusal instead, and would prove nothing about this check.
    """
    contradiction = {
        "actor": "test",
        "total_allocations": 1,
        "allocating": True,
        "allocated": {"by_object": ["UCOS-OBJ-000002"]},
        "counter_advances": {},
        "cursor_advances": {},
        "unmeasured_maps": [],
        "bytes_changed": False,
    }
    with pytest.raises(LA.LedgerWriteRefused, match="did not move"):
        LA._refuse_unmoved_allocation(contradiction)

    consistent = dict(contradiction, bytes_changed=True)
    LA._refuse_unmoved_allocation(consistent)  # must not raise


# ---------------------------------------------------------------------------------------
# R-9 / E2-F4 — NO_ALLOCATION permits nothing, not merely no allocation


@pytest.mark.parametrize(
    ("key", "value"), [("version", 99), ("discovered_volumes", {"VOL-666": 1})]
)
def test_no_allocation_does_not_authorize_a_non_allocating_mutation(
    tmp_path: Path, key: str, value: object
) -> None:
    """REPRODUCTION. The sentinel's docstring already claims it 'can only ever permit less'."""
    base = _base(history=False)  # §D.4
    path = _write(tmp_path, base)
    mutated = json.loads(json.dumps(base))
    mutated[key] = value

    with pytest.raises(LA.PermitRefused, match="MUTATES"):
        LA.commit(path, mutated, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)

    assert json.loads(Path(path).read_text(encoding="utf-8")).get(key) != value


def test_an_idempotent_no_op_is_still_accepted_under_no_allocation(tmp_path: Path) -> None:
    """REGRESSION. The one real production case: ukb.py:2380-2384's idempotent re-declare.

    `allocate_execution` early-returns on an existing key (ukb.py:2249-2251) and
    `_exec_declare` mutates the ledger nowhere else, so `ledger` equals the pre-image.
    """
    base = _base(history=False)
    base["by_execution"] = {"k": {"execution_id": "UCOS-EXE-000001", "first_seen": "t"}}
    path = _write(tmp_path, base)

    report = LA.commit(
        path,
        json.loads(json.dumps(base)),
        actor="test",
        writer=_writer,
        permit=LA.NO_ALLOCATION,
    )
    assert report["allocating"] is False
    assert report["authorization"] == "NO_ALLOCATION"
    assert report["bytes_changed"] is False


# ---------------------------------------------------------------------------------------
# R-10 / E2-F5 — LEDGER-INV-01 sees a write reached through a path PARAMETER


def _uga():
    """The engine that owns LEDGER-INV-01. Imported lazily; module import is ~0 s."""
    master = REPO / "00-MASTER" / "UCOS-UGA-001"
    if str(master) not in sys.path:
        sys.path.insert(0, str(master))
    import uga_engine  # noqa: PLC0415

    return uga_engine


def _production_writers():
    """The two real ledger serializers, for R-7's and R-11's regression coverage."""
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    import ukb  # noqa: PLC0415

    return (ukb._dump_json, _uga()._dump)


def test_the_guard_catches_an_indirect_ledger_write() -> None:
    """REPRODUCTION. Non-vacuity: the lexical patterns are blind to this shape."""
    source = textwrap.dedent(
        """
        LEDGER_PATH = "00-BOOK/DATA/id-ledger.json"
        def helper(p, obj):
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(obj)
        def go():
            helper(LEDGER_PATH, "{}")
        """
    )
    found = _uga().indirect_ledger_writes("probe.py", source)
    assert found, "the AST guard is blind to parameter indirection"
    assert any("helper" in v for v in found)

    uga = _uga()
    assert not any(
        uga._PY_LEDGER_WRITE.search(line) or uga._PY_LEDGER_OPEN.search(line)
        for line in source.splitlines()
    ), "the lexical guard already covered this, so the AST leg would be redundant"


def test_the_guard_reports_no_indirect_write_in_current_source() -> None:
    """REGRESSION, backward compatibility. Measured: 0 indirect writes at HEAD.

    Scans tracked source directly rather than through build(mint=False), which
    performs the full ~60 s discovery pass.
    """
    uga = _uga()
    violations: list[str] = []
    for rel in _tracked_sources():
        if rel == AUTHORITY_REL or not rel.endswith(".py"):
            continue
        try:
            source = (REPO / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        violations.extend(uga.indirect_ledger_writes(rel, source))
    assert violations == [], f"new indirection violations: {violations}"


def test_the_indirection_guard_is_wired_into_the_invariant() -> None:
    """REGRESSION, structural. The measurement must be REACHED, not merely defined."""
    source = (REPO / "00-MASTER" / "UCOS-UGA-001" / "uga_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    fn = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "_direct_ledger_writes"
    )
    called = {ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)}
    assert "indirect_ledger_writes" in called, (
        "_direct_ledger_writes does not call the indirection measurement, so "
        "LEDGER-INV-01 still cannot see a write through a path parameter"
    )


# ---------------------------------------------------------------------------------------
# R-11 / E2-F6 — serializer round-trip equivalence (R-7's premise)


def _full_shape_fixture() -> dict:
    """Every top-level key the production ledger carries, in miniature."""
    return {
        "version": 1,
        "by_path": {
            "d.md": {
                "universal_id": "UCOS-DOC-000001",
                "category": "DOC",
                "page_start": 1,
                "page_count": 2,
                "first_seen": "t",
            }
        },
        "by_object": {
            "a.py": {
                "universal_id": "UCOS-OBJ-000001",
                "category": "OBJ",
                "object_class": "TOOLING_OBJECT",
                "first_seen": "t",
            }
        },
        "by_execution": {"k": {"execution_id": "UCOS-EXE-000001", "first_seen": "t"}},
        "by_observation": {
            "o::s::K": {
                "observation_id": "UCOS-OBS-000001",
                "observer": "o",
                "subject": "s",
                "kind": "K",
                "first_seen": "t",
            }
        },
        "history": {
            "UCOS-DOC-000001": [
                {
                    "seq": 1,
                    "at": "t",
                    "content_hash": "h",
                    "version": "1.0.0",
                    "status": "ACTIVE",
                    "path": "d.md",
                    "name": "Doc — ünïcode",
                }
            ]
        },
        "page_cursor": 2,
        "category_seq": {"DOC": 1, "OBJ": 1, "EXE": 1, "OBS": 1},
        "discovered_volumes": {"VOL-1": 1},
        "volume_seq": 1,
    }


@pytest.mark.parametrize("doc_name", ["empty", "synthetic", "production"])
def test_the_three_serializers_round_trip_to_the_same_document(
    tmp_path: Path, doc_name: str
) -> None:
    """R-7's PREMISE. R-7 compares DOCUMENTS; that is only sound if every serializer
    round-trips faithfully. If this test ever fails, R-7 will begin refusing
    production writes, and this is the test that says why.
    """
    doc = {
        "empty": {},
        "synthetic": _full_shape_fixture(),
        "production": json.loads(
            (REPO / "00-BOOK" / "DATA" / "id-ledger.json").read_text(encoding="utf-8")
        ),
    }[doc_name]

    assert json.loads(LA._canonical(doc)) == doc, "_canonical does not round-trip"

    ukb_dump, uga_dump = _production_writers()
    ukb_path, uga_path = tmp_path / "u.json", tmp_path / "g.json"
    ukb_dump(str(ukb_path), doc)
    uga_dump(str(uga_path), doc)
    ukb_bytes, uga_bytes = ukb_path.read_bytes(), uga_path.read_bytes()

    assert json.loads(ukb_bytes) == doc, "ukb._dump_json does not round-trip"
    assert json.loads(uga_bytes) == doc, "uga_engine._dump does not round-trip"
    assert ukb_bytes == uga_bytes, "the two production writers diverged at byte level"
    if doc:
        assert LA._canonical(doc).encode("utf-8") != ukb_bytes, (
            "_canonical is expected to differ at BYTE level, which is why R-7 compares "
            "documents rather than bytes"
        )


def test_a_first_mint_into_a_nonexistent_tree_still_works(tmp_path: Path) -> None:
    """REGRESSION for R-3. Exclusion must not turn a legitimate first mint into a refusal.

    E1-S4 — "a missing ledger is a legitimate first mint, not an error" — is a property
    the lock could silently have taken away: the lock is held on the ledger's DIRECTORY,
    and on a first mint into a fresh tree that directory does not exist yet. Every writer
    already creates it (`ukb._dump_json` calls os.makedirs), so the lock creates it too.
    """
    data_dir = tmp_path / "DATA"
    path = str(data_dir / "id-ledger.json")
    proposed = {"by_object": {"a.py": {"universal_id": "UCOS-OBJ-000001"}}}

    def writer(p, obj):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        Path(p).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    manifest = LA.plan(path, proposed, actor="test")
    data_dir.mkdir(parents=True, exist_ok=True)
    Path(LA.permit_register_path(path)).write_text(
        json.dumps(
            {
                "permits": [
                    {
                        "permit_id": "P-FIRST",
                        "actor": "test",
                        "manifest_digest": manifest["digest"],
                        "preimage_digest": manifest["preimage_digest"],
                        "head": manifest["head"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = LA.commit(path, proposed, actor="test", writer=writer, permit="P-FIRST")
    assert report["allocated"] == {"by_object": ["UCOS-OBJ-000001"]}
    assert report["bytes_changed"] is True


# --------------------------------------------------------- RC-0012: the registration deadlock


def _ukb_authorization():
    """``ukb.py``'s permit resolver, loaded without executing the script's CLI."""

    spec = importlib.util.spec_from_file_location("_ukb_under_test", TOOLS / "ukb.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module._authorization


def test_a_missing_permit_is_a_verified_no_allocation_claim_not_an_omission() -> None:
    """RC-0012. `None` reached `commit()` and deadlocked every registration transaction.

    `ledger_authority.commit` requires `permit` with no default, deliberately — a default
    "would convert the loudest possible failure into a silent bypass". But `ukb.py` passed
    `getattr(args, "permit", None)`, and None is not an authorization, so EVERY
    `ukb.py build --mint` died with `permit must be a permit_id string or NO_ALLOCATION; got
    None` — including the idempotent re-runs that allocate nothing. `register.sh` could not
    complete its own transaction, which is why tracked artifacts stayed unregistered.
    """
    authorization = _ukb_authorization()

    class _Args:
        permit = None

    assert (
        authorization(_Args()) is LA.NO_ALLOCATION
    ), "a missing permit must become the VERIFIED no-allocation claim, never None"

    class _WithPermit:
        permit = "P-EXPLICIT"

    assert authorization(_WithPermit()) == "P-EXPLICIT", "an explicit permit must win"
    assert authorization(object()) is LA.NO_ALLOCATION, "an absent attribute behaves as absent"


def test_the_no_allocation_claim_still_refuses_a_real_allocation(tmp_path: Path) -> None:
    """The fix must not weaken the control: the sentinel is CHECKED, not trusted.

    Without this, RC-0012's remediation would be the bypass the permit register exists to
    prevent — an unauthorized mint would simply succeed.
    """
    authorization = _ukb_authorization()

    class _Args:
        permit = None

    path = _write(tmp_path, {"by_path": {}, "version": 1})
    proposed = {"by_path": {"a.md": "UCOS-KA-000001"}, "version": 1}

    with pytest.raises(LA.PermitRefused) as refusal:
        LA.commit(path, proposed, actor="test", writer=_writer, permit=authorization(_Args()))

    message = str(refusal.value)
    assert "NO_ALLOCATION was asserted, but this write ALLOCATES" in message
    assert "Obtain a permit" in message, "the refusal must say what to do, not what type it wanted"
    # Refused BEFORE the writer ran: the ledger is exactly as it was.
    assert json.loads(Path(path).read_text(encoding="utf-8")) == {"by_path": {}, "version": 1}


def test_a_no_op_transaction_completes_without_a_permit(tmp_path: Path) -> None:
    """The other half: registration is idempotent in steady state and must not need a permit.

    A transaction that allocates nothing is the common case. Requiring an authorization for it
    made the whole transaction unreachable, and an unreachable transaction registers nothing.
    """
    authorization = _ukb_authorization()

    class _Args:
        permit = None

    ledger = {"by_path": {"a.md": "UCOS-KA-000001"}, "version": 1}
    path = _write(tmp_path, ledger)
    report = LA.commit(
        path, dict(ledger), actor="test", writer=_writer, permit=authorization(_Args())
    )
    assert report["allocating"] is False
    assert report["bytes_changed"] is False, "a no-op must not move the file"
    assert report["authorization"] == "NO_ALLOCATION"


# ------------------------------------------- RC-0005: registration parity is enforced somewhere

REGISTER_SH = TOOLS / "register.sh"


def test_the_pre_gate_does_not_claim_a_parity_it_does_not_measure() -> None:
    """RC-0005. PRE printed "no unregistered ... artifact can silently enter the corpus".

    It measures no such thing, and correctly so: in PRE mode an artifact is a violation only if
    it is unregistered AND invalid/unclassified/unreconciled. A gate that refused every
    unregistered artifact would refuse exactly the ones the registration transaction exists to
    register — Phase 0 runs before Phase 1 mints. The defect was the CLAIM, not the gate.
    """
    source = (TOOLS / "ukb.py").read_text(encoding="utf-8")
    # Executable lines only. The old sentence survives in a comment that explains why it was
    # wrong, and a test that could not tell those apart would forbid recording the history.
    code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
    assert "can silently enter the corpus" not in code, (
        "the parity claim must not be PRINTED by either branch; PRE does not measure parity, "
        "and POST states the stronger fact in its own words"
    )
    # Matched on one line: the message is built from adjacent literals, so the rendered
    # sentence is not contiguous in the source.
    assert "PARITY is asserted by the" in code, "it must say where parity IS asserted"
    assert "every eligible artifact is registered" in code, "the POST branch keeps the strong claim"


def test_the_observation_plane_invokes_the_post_parity_gate() -> None:
    """Parity must be asserted by something that runs on its own.

    Before this, POST ran in exactly one place — Phase 9 of the WRITE transaction. `verify.sh`,
    `ucos-registration-gate.yml` and `register.sh --observe` all ran `enforce --pre`, so
    "every tracked artifact is registered" was checked by no verification plane at all. Nine
    artifacts reached the committed tree unregistered while every gate reported PASS.
    """
    script = REGISTER_SH.read_text(encoding="utf-8")
    # The observation block ends at its own `exit "$RC"`; anything after it is the WRITE
    # transaction, whose PRE/POST calls are a different plane and must not be counted here.
    observe = script.split('if [ "$OBSERVE" = "1" ]', 1)[1].split('exit "$RC"', 1)[0]
    post_calls = [
        line
        for line in observe.splitlines()
        if "ukb.py" in line and "enforce" in line and "--pre" not in line
    ]
    assert post_calls, (
        "the read-only observation plane must invoke the POST parity gate; without it no "
        "automated plane asserts that every tracked artifact is registered"
    )
    # It must remain read-only: the observation plane may never mint.
    assert "--mint" not in observe, "the observation plane must never allocate identity"


def test_the_registration_transaction_forwards_an_operator_permit() -> None:
    """RC-0012's other half: a real allocation must be authorizable without editing a ledger."""
    script = REGISTER_SH.read_text(encoding="utf-8")
    assert "--permit=*)" in script, "register.sh must accept an operator-supplied permit"
    assert "build --mint $PERMIT_FLAG" in script, "Phase 1 must forward it to the mint"


# ---------------------------------------------------------------------------------------
# the readers' own refusals, and the branches a well-formed ledger never reaches


def test_the_preimage_reader_refuses_a_ledger_it_cannot_parse(tmp_path: Path) -> None:
    """`commit` reads bytes and parses them itself; `load_preimage` is the other reader.

    Both refuse for the same reason and neither may stand in for the other's coverage: a
    caller that used this one and got `{}` back from a corrupt file would report every
    existing identity as freshly minted.
    """
    path = tmp_path / "id-ledger.json"
    path.write_text("{ this is not json", encoding="utf-8")
    with pytest.raises(LA.LedgerWriteRefused, match="cannot be read"):
        LA.load_preimage(str(path))


def test_the_byte_reader_refuses_a_ledger_it_cannot_open(tmp_path: Path) -> None:
    """Unparseable and unopenable are different failures on different readers."""
    path = tmp_path / "id-ledger.json"
    path.write_text("{}", encoding="utf-8")
    path.chmod(0o000)
    with pytest.raises(LA.LedgerWriteRefused, match="cannot be read"):
        LA._read_bytes_or_none(str(path))


def test_a_lock_that_cannot_be_taken_refuses_rather_than_writing_unserialized(
    tmp_path: Path,
) -> None:
    """The lock is on the ledger's DIRECTORY, and a directory that cannot exist is a refusal.

    Not a hypothetical: a first-ever mint may target a tree nobody has created, so the lock
    creates it. Creating it under a path component that is a regular file cannot succeed, and
    proceeding without the lock would be a write two writers cannot be shown not to interleave.
    """
    (tmp_path / "not-a-directory").write_text("", encoding="utf-8")
    path = str(tmp_path / "not-a-directory" / "id-ledger.json")
    with pytest.raises(LA.LedgerWriteRefused, match="to take the ledger lock"):
        LA.commit(path, {}, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)


def test_a_record_that_is_not_an_object_is_still_append_only(tmp_path: Path) -> None:
    """The record body check names the fields that changed, and needs a body to name them.

    A ledger whose record is a bare identifier string carries no fields, so the refusal says
    `<record>` rather than inventing a field list. The identifier held still in both shapes,
    which is exactly why the identifier projection cannot see this rewrite.
    """
    path = _write(tmp_path, {"by_object": {"a": "U-1"}})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    with pytest.raises(LA.LedgerWriteRefused, match=r"\['<record>'\]"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)


def test_a_record_carrying_no_identifier_binds_nothing(tmp_path: Path) -> None:
    """One identifier names at most one thing; a record naming NO identifier names nothing.

    Without the skip, two records that both omit their identifier field would collide on
    `None` and be reported as the same permanent identifier bound twice.
    """
    path = _write(tmp_path, {})
    proposed = {
        "by_object": {"a": {"first_seen": "x"}, "b": {"first_seen": "y"}},
    }
    LA.commit(path, proposed, actor="test", writer=_writer, permit=_issue(path, proposed))
    assert set(json.loads(Path(path).read_text(encoding="utf-8"))["by_object"]) == {"a", "b"}


def test_removing_a_category_from_the_counter_is_refused(tmp_path: Path) -> None:
    """Its allocated identifiers would become reissuable, which is the one thing identity is not."""
    path = _write(tmp_path, {"category_seq": {"OBS": 7}})
    with pytest.raises(LA.LedgerWriteRefused, match="would be REMOVED"):
        LA.commit(path, {"category_seq": {}}, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)


def test_a_history_entry_that_is_not_a_list_is_refused_when_it_changes(tmp_path: Path) -> None:
    """Append-only over a list is a prefix check; over anything else it is an equality check.

    A history that arrives in some other shape cannot be shown to have kept its prefix, so the
    only safe reading is that any change to it is a replacement.
    """
    path = _write(tmp_path, {"history": {"UID-1": "a string where a list belongs"}})
    proposed = {"history": {"UID-1": "a different string"}}
    with pytest.raises(LA.LedgerWriteRefused, match="different shape"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)


def test_the_report_line_names_a_cursor_that_advanced(tmp_path: Path) -> None:
    """`page_cursor` and `volume_seq` move without any identifier being allocated.

    A line that omitted them would describe a mutating write as though nothing had moved,
    which is the D0.1 shape one level down.
    """
    path = _write(tmp_path, {"page_cursor": 1})
    proposed = {"page_cursor": 2}
    report = LA.plan(path, proposed, actor="test")
    assert "page_cursor:1->2" in LA.format_report(report)


def test_a_head_that_cannot_be_determined_is_none_rather_than_a_failure(
    tmp_path: Path, monkeypatch
) -> None:
    """Every failure of the provider is "no head", and none of them is an exception.

    `git_head` feeds `manifest["head"]`, which every permit is bound to. A provider that
    raised here would turn an unreadable repository into a crash inside the chokepoint.
    """

    def refusing(*args, **kwargs):
        raise RuntimeError("the provider cannot answer here")

    monkeypatch.setattr(git_provider, "GitDiscoveryProvider", refusing)
    assert LA.git_head(str(tmp_path / "id-ledger.json")) is None


def test_a_permit_register_that_is_not_a_list_is_refused_rather_than_guessed(
    tmp_path: Path,
) -> None:
    path = _write(tmp_path, {})
    Path(LA.permit_register_path(path)).write_text(
        json.dumps({"permits": {"P-TEST": {}}}), encoding="utf-8"
    )
    with pytest.raises(LA.PermitRefused, match="refusing to guess its shape"):
        LA.load_permit_register(path)


def test_a_permit_binding_a_head_is_refused_where_the_head_disagrees(
    tmp_path: Path, monkeypatch
) -> None:
    """The other side of the head binding: determinable, and not the one the permit names.

    The `head cannot be determined` refusal is what a temporary directory produces. This is
    the refusal a real repository produces when the permit was issued against a different
    commit, and the two must not be spelled the same way.
    """
    monkeypatch.setattr(LA, "git_head", lambda near_path: "a" * 40)
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed)
    monkeypatch.setattr(LA, "git_head", lambda near_path: "b" * 40)
    with pytest.raises(LA.PermitRefused, match="permit binds"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)


def test_a_scope_whose_maps_are_not_a_list_constrain_nothing(tmp_path: Path) -> None:
    """`max_allocations` still binds. A malformed `maps` must not silently authorize
    everything OR refuse everything: the digest is what binds exactly, and scope is the
    reviewable half of it."""
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, scope={"maps": "by_object", "max_allocations": 1})
    report = LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)
    assert report["total_allocations"] == 1


def test_a_naive_expiry_is_read_as_utc_rather_than_refused(tmp_path: Path) -> None:
    """An instant with no offset is the commonest spelling an operator writes by hand.

    Reading it as UTC is a decision; the alternative — comparing a naive datetime against an
    aware one — raises TypeError inside the chokepoint, which is a crash rather than a verdict.
    """
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, expires_at="2000-01-01T00:00:00")
    with pytest.raises(LA.PermitRefused, match="expired"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)


def test_an_unparseable_expiry_is_refused_rather_than_ignored(tmp_path: Path) -> None:
    """An expiry nobody can read is not an absent expiry: it is a permit nobody can bound."""
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, expires_at="whenever")
    with pytest.raises(LA.PermitRefused, match="not an ISO-8601 instant"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)


def test_a_permit_inside_its_expiry_still_authorizes(tmp_path: Path) -> None:
    """Expiry is measured in both directions, or `expired` is a branch that always fires."""
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, expires_at="2999-01-01T00:00:00Z")
    report = LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)
    assert report["total_allocations"] == 1


def test_an_unmoved_allocation_found_after_the_write_restores_the_ledger(
    tmp_path: Path, monkeypatch
) -> None:
    """Defence in depth, and the depth is what is measured here.

    Once the persisted document is compared against the authorized one this state is
    unreachable through `commit()` — which is why the guard's own refusal path had never run.
    A guard whose failure path has never executed cannot be relied on to restore the file the
    day the comparison above it is weakened.
    """
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed, permit_id="P-TEST")

    def refusing(report: dict) -> None:
        raise LA.LedgerWriteRefused("the report claims an allocation but the file did not move")

    monkeypatch.setattr(LA, "_refuse_unmoved_allocation", refusing)
    with pytest.raises(LA.LedgerWriteRefused, match="did not move"):
        LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)
    assert json.loads(Path(path).read_text(encoding="utf-8")) == {}


def test_a_history_entry_of_another_shape_that_did_not_change_is_not_a_replacement(
    tmp_path: Path,
) -> None:
    """The shape check refuses a CHANGE, not a shape. A ledger carrying a history entry this
    module cannot read as a list still commits, as long as the entry is left alone — otherwise
    one unreadable entry would freeze every later write to the whole ledger."""
    before = {"history": {"UID-1": "a string where a list belongs"}, "page_cursor": 1}
    path = _write(tmp_path, before)
    proposed = {"history": {"UID-1": "a string where a list belongs"}, "page_cursor": 2}
    report = LA.commit(path, proposed, actor="test", writer=_writer, permit=_issue(path, proposed))
    assert report["cursor_advances"] == {"page_cursor": [1, 2]}


def test_a_permit_bound_to_the_head_the_repository_is_at_authorizes(
    tmp_path: Path, monkeypatch
) -> None:
    """The third of the three head outcomes. Undeterminable and disagreeing are both refusals;
    agreeing has to be a pass, or binding a head would make every permit unusable."""
    monkeypatch.setattr(LA, "git_head", lambda near_path: "a" * 40)
    path = _write(tmp_path, {})
    proposed = {"by_object": {"a": {"universal_id": "U-1"}}}
    permit_id = _issue(path, proposed)
    report = LA.commit(path, proposed, actor="test", writer=_writer, permit=permit_id)
    assert report["total_allocations"] == 1

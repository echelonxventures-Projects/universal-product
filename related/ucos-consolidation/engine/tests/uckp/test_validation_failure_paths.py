"""Every reachable FAIL state of the seventeen probes.

:mod:`engine.tests.uckp.test_universe_and_validation` measures the lawful universe and
drives the invariants that a *whole-universe* mutation can break. This module finishes
the job at the level of the individual finding: for each degenerate condition a probe
claims to detect, there is a test that produces that condition and asserts the probe
says so.

The reason this matters is UCCEP-F-001 inverted. A probe branch that has never executed
is a claim, not a check — the finding could be misspelled, unreachable, or measuring the
wrong object, and a universe that only ever passes would never tell us. So the universe
is not mutated in place (it is frozen and shared); instead each test hands the validator
a *proxy* that answers exactly like the real universe except for the one thing under
test. That keeps every other measurement real, which is what makes the single reported
finding attributable.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.tests.uckp.doubles import Proxy as _Proxy
from engine.uckp.errors import LawViolation
from engine.uckp.identity import urn_for
from engine.uckp.law import ROOT_LAW
from engine.uckp.ucko import UCKO
from engine.uckp.validation import (
    FUTURE_PROBE_TERM,
    REFUSED,
    SATISFIED,
    VIOLATED,
    ConstitutionalValidator,
)
from engine.uckp.values import (
    AuditEntry,
    DiscoveryDescriptor,
    ProvenanceStep,
)
from engine.uckp.vocabulary import Term

# --- the one tool this module needs ---------------------------------------------


def _measure(universe: object, invariant_id: str, **overrides: object):
    """Measure one invariant against ``universe`` with ``overrides`` applied."""
    return ConstitutionalValidator(_Proxy(universe, **overrides)).validate_invariant(invariant_id)


def _findings(result) -> str:
    return "\n".join(result.findings)


def _evidence(result) -> dict[str, str]:
    return dict(result.evidence)


@pytest.fixture
def sample(universe) -> UCKO:
    """One real object from the universe, to be degraded one facet at a time."""
    return universe.registry.require(universe.root_id())


# --- the report surface ---------------------------------------------------------


def test_the_summary_truncates_an_invariant_that_reports_more_than_four_findings(universe):
    """A terminal summary that printed 900 findings would be read by nobody."""

    class Noisy(ConstitutionalValidator):
        def probes(self):
            return {
                **super().probes(),
                "UCKP-INV-01": lambda: (tuple(f"finding {n}" for n in range(6)), ()),
            }

    report = Noisy(universe).validate()
    text = report.summary()
    assert "             - finding 3" in text
    assert "- ... 2 more" in text
    assert report.verdict == REFUSED


# --- INV-02: single authority ---------------------------------------------------


def test_inv_02_detects_an_object_that_names_no_parent_authority(universe, sample):
    orphaned = dataclasses.replace(sample, authority=_Proxy(sample.authority, derives_from=""))
    result = _measure(universe, "UCKP-INV-02", objects=lambda: (orphaned,))
    assert result.verdict == VIOLATED
    assert "names no parent authority" in _findings(result)


def test_inv_02_detects_an_object_deriving_from_an_authority_that_does_not_exist(universe, sample):
    ghost = urn_for("test", "GHOST-AUTHORITY")
    detached = dataclasses.replace(sample, authority=_Proxy(sample.authority, derives_from=ghost))
    result = _measure(universe, "UCKP-INV-02", objects=lambda: (detached,))
    assert result.verdict == VIOLATED
    assert f"derives from {ghost}, which does not exist" in _findings(result)


def test_inv_02_detects_an_authority_chain_that_does_not_reach_the_root_law(universe, mint_object):
    """The parent exists, so the cheap check passes; the chain is what fails."""
    stray = mint_object("UNGROUNDED", derives_from=universe.root_id())
    result = _measure(universe, "UCKP-INV-02", objects=lambda: (stray,))
    assert result.verdict == VIOLATED
    assert "does not ground in the root law" in _findings(result)


def test_inv_02_detects_a_universe_that_declares_more_than_one_self_grounding_root(universe):
    root_id = universe.root_id()
    two_roots = _Proxy(universe.registry, root_ids=lambda: (root_id, urn_for("test", "SECOND")))
    result = _measure(universe, "UCKP-INV-02", registry=two_roots)
    assert result.verdict == VIOLATED
    assert "declares 2 self-grounding roots" in _findings(result)


# --- INV-03: zero duplication ---------------------------------------------------


def test_inv_03_detects_the_same_identity_and_content_admitted_twice(universe, sample):
    """One object counted twice is both a uuid collision and a content collision."""
    result = _measure(universe, "UCKP-INV-03", objects=lambda: (sample, sample))
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert f"uuid {sample.identity.uuid} claimed by 2" in findings
    assert f"content digest {sample.content_sha256[:16]} shared by 2" in findings
    assert _evidence(result)["distinct_uuids"] == "1"


def test_inv_03_skips_a_source_file_it_cannot_parse_and_then_reports_it_measured_nothing(
    universe, tmp_path
):
    """An unparseable file is not a violation; a tree of them is an unmeasured clause."""
    package = tmp_path / "engine"
    package.mkdir()
    (package / "truncated.py").write_text("def content_hash(payload:\n", encoding="utf-8")
    result = ConstitutionalValidator(universe, source_root=tmp_path).validate_invariant(
        "UCKP-INV-03"
    )
    assert result.verdict == VIOLATED
    assert "single-primitive clause is unmeasured" in _findings(result)
    assert _evidence(result)["source_files_scanned"] == "0"


def test_inv_03_does_not_flag_a_primitive_that_delegates_to_a_collaborator(universe, tmp_path):
    """``_delegate.compute(...)`` is a call, not an implementation of the digest."""
    package = tmp_path / "engine"
    package.mkdir()
    (package / "delegating.py").write_text(
        "from engine.uckp import canonical as _delegate\n"
        "def content_hash(payload):\n"
        "    return _delegate.content_hash(payload)\n",
        encoding="utf-8",
    )
    result = ConstitutionalValidator(universe, source_root=tmp_path).validate_invariant(
        "UCKP-INV-03"
    )
    assert result.verdict == SATISFIED
    assert _evidence(result)["source_files_scanned"] == "1"
    assert _evidence(result)["primitive_redefinitions"] == "0"


# --- INV-04: zero ambiguity -----------------------------------------------------


def test_inv_04_detects_an_object_that_leaves_a_facet_unanswered(universe, sample):
    silent = dataclasses.replace(sample, lifecycle="")
    result = _measure(universe, "UCKP-INV-04", objects=lambda: (silent,))
    assert result.verdict == VIOLATED
    assert "leaves 1 facet(s) absent: lifecycle" in _findings(result)
    assert _evidence(result)["incomplete_objects"] == "1"


# --- INV-06: zero circular authority --------------------------------------------


def test_inv_06_reports_a_refusal_from_the_graph_rather_than_swallowing_it(universe):
    """The probe asks the graph to refuse; a refusal it hid would be a silent pass."""

    def refuse() -> None:
        raise LawViolation("authority relation contains a cycle")

    graph = _Proxy(universe.graph(), require_acyclic_authority=refuse)
    result = _measure(universe, "UCKP-INV-06", graph=lambda: graph)
    assert result.verdict == VIOLATED
    assert "authority acyclicity refused" in _findings(result)


# --- INV-07: zero hardcoded knowledge -------------------------------------------


def test_inv_07_detects_an_object_carrying_no_provenance(universe, sample):
    undeclared = dataclasses.replace(sample, provenance=())
    result = _measure(universe, "UCKP-INV-07", objects=lambda: (undeclared,))
    assert result.verdict == VIOLATED
    assert "carries no provenance" in _findings(result)


def test_inv_07_detects_a_provenance_step_that_names_no_source(universe, sample):
    """A step with no source is knowledge asserted by nobody — hardcoding with a label."""
    unsourced = dataclasses.replace(
        sample,
        provenance=(ProvenanceStep(actor="someone", action="declared", source="   "),),
    )
    result = _measure(universe, "UCKP-INV-07", objects=lambda: (unsourced,))
    assert result.verdict == VIOLATED
    assert "1 provenance step(s) naming no source" in _findings(result)
    assert _evidence(result)["objects_with_sourced_provenance"] == "0"


# --- INV-10: zero repository lock-in --------------------------------------------


def test_inv_10_detects_an_object_categorised_as_something_that_may_only_be_a_view(
    universe, sample
):
    projected = dataclasses.replace(sample, taxonomy=_Proxy(sample.taxonomy, category="document"))
    result = _measure(universe, "UCKP-INV-10", objects=lambda: (projected,))
    assert result.verdict == VIOLATED
    assert "which Article 4" in _findings(result)


def test_inv_10_refuses_a_universe_in_which_nothing_binds_the_repository_at_all(universe):
    """Unbound is not the same as unlocked: with no binding the claim is untested."""
    result = _measure(universe, "UCKP-INV-10", objects=lambda: ())
    assert result.verdict == VIOLATED
    assert "no object binds the repository at all" in _findings(result)


def test_inv_10_detects_a_law_that_stopped_declaring_the_repository_non_authoritative(
    universe,
):
    forgetful = _Proxy(
        universe.law, is_non_authoritative=lambda name: False, non_authoritative_categories=()
    )
    result = _measure(universe, "UCKP-INV-10", law=forgetful, objects=lambda: ())
    assert result.verdict == VIOLATED
    findings = _findings(result)
    for name in ("repository", "file", "folder", "source-code", "document"):
        assert f"{name!r} is not declared non-authoritative" in findings


# --- INV-12: zero runtime lock-in -----------------------------------------------


def test_inv_12_detects_an_object_that_binds_no_runtime_and_a_universe_of_one_technology(
    universe, sample
):
    stranded = dataclasses.replace(sample, runtime_bindings=())
    result = _measure(universe, "UCKP-INV-12", objects=lambda: (stranded,))
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert "binds no runtime at all" in findings
    assert "reaches only 0 runtime technolog" in findings
    assert _evidence(result)["objects_bound_to_none"] == "1"


# --- INV-13: infinite evolvability ----------------------------------------------


def test_inv_13_detects_a_terminal_stage_in_the_evolution_cycle(universe, monkeypatch):
    monkeypatch.setattr("engine.uckp.validation.is_terminal", lambda stage: True)
    result = _measure(universe, "UCKP-INV-13")
    assert result.verdict == VIOLATED
    assert "is terminal, so evolution can stop" in _findings(result)


def test_inv_13_detects_a_stage_whose_successor_leaves_the_cycle(universe, monkeypatch):
    monkeypatch.setattr("engine.uckp.validation.next_stage", lambda stage: "somewhere-else")
    result = _measure(universe, "UCKP-INV-13")
    assert result.verdict == VIOLATED
    assert "has no successor inside the cycle" in _findings(result)


def test_inv_13_detects_an_empty_ledger_that_has_never_wrapped(universe):
    barren = _Proxy(
        universe.evolution,
        records=lambda: (),
        cycles=lambda: 0,
        completed_cycles=lambda: 0,
        is_terminated=lambda: False,
    )
    result = _measure(universe, "UCKP-INV-13", evolution=barren)
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert "ledger is empty, so append-only is untested" in findings
    assert "has not yet wrapped past the final stage" in findings


def test_inv_13_detects_a_ledger_that_exposes_a_destructive_operation(universe):
    class Rewritable:
        """A ledger with a delete method is not an append-only ledger."""

        def __init__(self, base: object) -> None:
            self._base = base

        def __getattr__(self, name: str) -> object:
            return getattr(self._base, name)

        def delete(self, record: object) -> None:  # pragma: no cover - existence is the finding
            raise AssertionError("never called")

    result = _measure(universe, "UCKP-INV-13", evolution=Rewritable(universe.evolution))
    assert result.verdict == VIOLATED
    assert "exposes 'delete', which is not append-only" in _findings(result)


# --- INV-14: infinite extensibility ---------------------------------------------


class _VocabularyStub:
    """A vocabulary registry holding exactly one vocabulary, which the test controls."""

    def __init__(self, vocabulary: object, *, extensible: bool = True) -> None:
        self._vocabulary = vocabulary
        self._extensible = extensible

    def is_extensible(self) -> bool:
        return self._extensible

    def vocabulary_ids(self) -> tuple[str, ...]:
        return ("uckp.stub-vocabulary",)

    def require(self, vocabulary_id: str) -> object:
        return self._vocabulary


def _one_vocabulary(universe) -> object:
    registry = universe.vocabularies()
    return registry.require(registry.vocabulary_ids()[0])


def test_inv_14_detects_a_vocabulary_registry_that_reports_itself_closed(universe):
    stub = _VocabularyStub(_one_vocabulary(universe), extensible=False)
    result = _measure(universe, "UCKP-INV-14", vocabularies=lambda: stub)
    assert result.verdict == VIOLATED
    assert "vocabulary registry reports itself closed" in _findings(result)


def test_inv_14_detects_a_vocabulary_that_refuses_an_unknown_future_term(universe):
    def refuse(term: object) -> object:
        raise LawViolation("this vocabulary is closed")

    closed = _Proxy(_one_vocabulary(universe), extended_with=refuse)
    result = _measure(universe, "UCKP-INV-14", vocabularies=lambda: _VocabularyStub(closed))
    assert result.verdict == VIOLATED
    assert "refused an unknown future term" in _findings(result)
    assert _evidence(result)["vocabularies_extended"] == "0"


def test_inv_14_detects_a_vocabulary_that_accepts_an_extension_without_admitting_it(universe):
    """Silent acceptance is worse than refusal: it looks open and is not."""
    declared = _one_vocabulary(universe)
    pretending = _Proxy(declared, extended_with=lambda term: declared)
    result = _measure(universe, "UCKP-INV-14", vocabularies=lambda: _VocabularyStub(pretending))
    assert result.verdict == VIOLATED
    assert "did not admit the term" in _findings(result)


def test_inv_14_detects_a_probe_that_would_have_mutated_the_vocabulary_it_measured(universe):
    """Extension must derive a new vocabulary; widening the original manufactures a pass."""
    widened = _one_vocabulary(universe).extended_with(
        Term(term_id=FUTURE_PROBE_TERM, definition="already admitted before the probe ran")
    )
    # Extension "succeeds" by handing back the same widened vocabulary — which is what
    # in-place widening would look like from the probe's side.
    mutating = _Proxy(widened, extended_with=lambda term: widened)
    result = _measure(universe, "UCKP-INV-14", vocabularies=lambda: _VocabularyStub(mutating))
    assert result.verdict == VIOLATED
    assert "was mutated by the probe" in _findings(result)


def test_inv_14_detects_a_projection_engine_that_cannot_reason_about_an_unknown_kind(universe):
    def explode(kinds: object) -> object:
        raise KeyError("holo-deck")

    engine = _Proxy(universe.projections, unimplemented=explode)
    result = _measure(universe, "UCKP-INV-14", projections=engine)
    assert result.verdict == VIOLATED
    assert "cannot reason about unknown kinds" in _findings(result)


def test_inv_14_detects_an_adapter_set_that_names_no_future_member(universe):
    class _Kind:
        def __init__(self, kind: str) -> None:
            self._kind = kind

        def describe(self) -> dict[str, str]:
            return {"kind": self._kind}

    result = _measure(
        universe,
        "UCKP-INV-14",
        persistence=(_Kind("memory"),),
        execution=(_Kind("python"),),
    )
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert "the persistence adapter set names no future member" in findings
    assert "the execution adapter set names no future member" in findings


# --- INV-15: infinite replayability ---------------------------------------------


def test_inv_15_detects_a_timeline_that_cannot_prove_or_replay_itself(universe):
    crippled = _Proxy(
        universe.timeline,
        proofs_complete=lambda: False,
        replays_identically=lambda: False,
        verify=lambda: False,
    )
    result = _measure(universe, "UCKP-INV-15", timeline=crippled)
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert "carries an incomplete proof set" in findings
    assert "does not reproduce it" in findings
    assert "refuses its own verification" in findings


def test_inv_15_detects_a_state_altered_after_sealing_or_carrying_a_broken_proof(universe):
    head = universe.timeline.head()
    tampered = _Proxy(head, verify_integrity=lambda: False, proofs_hold=lambda: False)
    timeline = _Proxy(universe.timeline, states=lambda: (tampered,))
    result = _measure(universe, "UCKP-INV-15", timeline=timeline)
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert "was altered after sealing" in findings
    assert "carries a proof that does not hold" in findings


def test_inv_15_detects_governance_and_projections_that_do_not_re_derive(universe):
    result = _measure(
        universe,
        "UCKP-INV-15",
        governance=_Proxy(universe.governance, replays_identically=lambda: False),
        projections=_Proxy(universe.projections, replays_identically=lambda objects: False),
    )
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert "governance decision does not re-derive itself" in findings
    assert "projection does not regenerate byte-identically" in findings


# --- INV-16: infinite discoverability -------------------------------------------


@pytest.mark.parametrize(
    ("descriptor", "expected"),
    [
        (DiscoveryDescriptor(discoverable=False, provider="p"), "declares itself undiscoverable"),
        (DiscoveryDescriptor(self_describing=False, provider="p"), "does not self-describe"),
        (DiscoveryDescriptor(provider="   "), "names no provider"),
    ],
)
def test_inv_16_detects_an_object_that_cannot_be_found(universe, sample, descriptor, expected):
    hidden = dataclasses.replace(sample, discovery=descriptor)
    result = _measure(universe, "UCKP-INV-16", objects=lambda: (hidden,))
    assert result.verdict == VIOLATED
    assert expected in _findings(result)
    assert _evidence(result)["undiscoverable"] == "1"


class _AnonymousObject(UCKO):
    """An object whose self-description omits the identity it is a description of."""

    def describe(self) -> dict[str, object]:
        described = dict(super().describe())
        described["ucko_id"] = ""
        return described


def test_inv_16_detects_a_self_description_that_carries_no_identity(universe, sample):
    anonymous = _AnonymousObject(
        **{field.name: getattr(sample, field.name) for field in dataclasses.fields(sample)}
    )
    result = _measure(universe, "UCKP-INV-16", objects=lambda: (anonymous,))
    assert result.verdict == VIOLATED
    assert "produces a self-description with no identity" in _findings(result)


# --- INV-17: infinite auditability ----------------------------------------------


def test_inv_17_detects_an_object_carrying_no_audit_entry(universe, sample):
    unaudited = dataclasses.replace(sample, audit=())
    result = _measure(universe, "UCKP-INV-17", objects=lambda: (unaudited,))
    assert result.verdict == VIOLATED
    assert "carries no audit entry" in _findings(result)


def test_inv_17_detects_an_audit_entry_missing_an_actor_action_or_subject(universe, sample):
    nameless = dataclasses.replace(
        sample, audit=(AuditEntry(actor="  ", action="mint", subject=sample.ucko_id),)
    )
    result = _measure(universe, "UCKP-INV-17", objects=lambda: (nameless,))
    assert result.verdict == VIOLATED
    assert "audit entr(y/ies) missing an actor, action or subject" in _findings(result)
    assert _evidence(result)["unaudited_objects"] == "1"


def test_inv_17_detects_a_state_and_a_timeline_with_no_audit_trail(universe):
    head = universe.timeline.head()
    silent_state = _Proxy(head, audit_trail=())
    timeline = _Proxy(
        universe.timeline, audit_complete=lambda: False, states=lambda: (silent_state,)
    )
    result = _measure(universe, "UCKP-INV-17", timeline=timeline)
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert "carries no audit trail" in findings
    assert "records no audit entry" in findings


def test_inv_17_detects_a_governance_runtime_and_a_ledger_that_recorded_nothing(universe):
    result = _measure(
        universe,
        "UCKP-INV-17",
        governance=_Proxy(universe.governance, audit=lambda: ()),
        evolution=_Proxy(universe.evolution, records=lambda: ()),
    )
    assert result.verdict == VIOLATED
    findings = _findings(result)
    assert "governance runtime has recorded no audit entry" in findings
    assert "evolution ledger records nothing" in findings


# --- the whole law, on a universe broken in one place ----------------------------


def test_a_single_broken_facet_refuses_the_whole_report(universe, sample):
    """Every invariant blocks, so one detected violation is a refusal of the universe."""
    broken = dataclasses.replace(sample, audit=())
    validator = ConstitutionalValidator(_Proxy(universe, objects=lambda: (broken,)))
    report = validator.validate()
    assert report.verdict == REFUSED
    assert report.satisfied_count() < len(ROOT_LAW.invariants)
    assert not report.all_stop_conditions_met()

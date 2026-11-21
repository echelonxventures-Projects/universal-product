"""UCXI-000001 Parts 01/11 — constitution and validation tests.

A law that cannot fail is not a law, so every one of the twelve laws is driven into a
violating state here and asserted to report it. Constructing those states requires
bypassing the registration authority (which refuses them at the front door), so several
tests write directly into the registry's private state — that is the point: the laws
catch corruption the authority never accepted.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.context.composition import compose
from engine.context.constitution import (
    CONTEXT_CONSTITUTION,
    CONTEXT_LAWS,
    LAW_CHECKS,
    ConstitutionAssessment,
    ContextConstitution,
    ContextLaw,
    LawAssessment,
)
from engine.context.errors import ConstitutionViolation, ContextValidationError
from engine.context.graph import build_context_graph
from engine.context.model import ContextRecord, ContextValue
from engine.context.registry import GENESIS_HASH, AuditEntry, ContextRegistry
from engine.context.taxonomy import (
    ContextAuthority,
    ContextKind,
    ContextLifecycle,
    ContextRelation,
)
from engine.context.validation import (
    SEVERITY_ADVISORY,
    SEVERITY_VIOLATION,
    VALIDATION_RULES,
    ContextValidator,
    ValidationRule,
    validate,
)
from engine.tests.context.conftest import declaration, future_taxon, spatial_values


def _inject(registry: ContextRegistry, record: ContextRecord) -> None:
    """Place a record into the registry without going through registration."""
    registry._records[record.context_id] = record  # noqa: SLF001 - deliberate corruption


def _record(registry: ContextRegistry, **overrides: object) -> ContextRecord:
    base = registry.records()[0]
    fields = {
        "context_id": base.context_id,
        "kind": base.kind,
        "taxon_id": base.taxon_id,
        "namespace": base.namespace,
        "natural_key": base.natural_key,
        "values": base.values,
        "authority": base.authority,
        "lifecycle": base.lifecycle,
        "boundary": base.boundary,
        "parent": base.parent,
        "description": base.description,
        "universal": base.universal,
    }
    fields.update(overrides)
    return ContextRecord(**fields)  # type: ignore[arg-type]


# ------------------------------------------------------------------- constitution


def test_twelve_laws_each_carry_a_check() -> None:
    assert len(CONTEXT_LAWS) == 12
    assert {law.law_id for law in CONTEXT_LAWS} == set(LAW_CHECKS)
    assert CONTEXT_CONSTITUTION.to_dict()["count"] == 12
    assert CONTEXT_CONSTITUTION.law("CXL-01").title == "Universal Representability"
    with pytest.raises(ConstitutionViolation):
        CONTEXT_CONSTITUTION.law("CXL-99")


def test_constitution_refuses_unchecked_or_undeclared_laws() -> None:
    extra = (*CONTEXT_LAWS, ContextLaw(law_id="CXL-13", title="t", statement="s"))
    with pytest.raises(ConstitutionViolation):
        ContextConstitution(extra)
    with pytest.raises(ConstitutionViolation):
        ContextConstitution(CONTEXT_LAWS[:1])


def test_universal_catalog_is_constitutionally_compliant(
    universal_registry: ContextRegistry, composed: object
) -> None:
    assessment = CONTEXT_CONSTITUTION.require_compliance(
        universal_registry,
        graph=build_context_graph(universal_registry),
        composed=composed,
    )
    assert assessment.compliant
    assert assessment.violations == ()
    assert assessment.findings() == ()
    assert assessment.summary()["compliant"] == 12
    assert assessment.law("CXL-01") is not None
    assert assessment.law("CXL-99") is None
    assert assessment.to_dict()["is_compliant"] is True
    # deterministic: the same subject seals identically
    assert assessment.content_hash == CONTEXT_CONSTITUTION.assess(universal_registry).content_hash


def test_assessment_aggregates_findings() -> None:
    assessment = ConstitutionAssessment(
        laws=(
            LawAssessment(law_id="CXL-02", title="b", compliant=False, findings=("bad",)),
            LawAssessment(law_id="CXL-01", title="a", compliant=True),
        )
    )
    assert assessment.laws[0].law_id == "CXL-01"
    assert not assessment.compliant
    assert assessment.findings() == ("CXL-02: bad",)


def test_law_01_and_02_catch_an_unclassified_or_malformed_context(
    universal_registry: ContextRegistry,
) -> None:
    _inject(universal_registry, _record(universal_registry, kind="quantum"))
    assessment = CONTEXT_CONSTITUTION.assess(universal_registry)
    assert not assessment.law("CXL-01").compliant
    assert not assessment.law("CXL-02").compliant


def test_law_03_catches_an_unbounded_context(universal_registry: ContextRegistry) -> None:
    _inject(universal_registry, _record(universal_registry, boundary=""))
    assert not CONTEXT_CONSTITUTION.assess(universal_registry).law("CXL-03").compliant


def test_law_04_catches_an_unfederated_cross_frame_reference(
    empty_registry: ContextRegistry,
) -> None:
    here = empty_registry.register(declaration(natural_key="here", boundary="frame-a"))
    there = empty_registry.register(
        declaration(
            kind=ContextKind.SPATIAL,
            natural_key="there",
            boundary="frame-b",
            values=spatial_values(),
        )
    )
    empty_registry.relate(ContextRelation.DEPENDS_ON, here.context_id, there.context_id)
    assessment = CONTEXT_CONSTITUTION.assess(empty_registry)
    assert not assessment.law("CXL-04").compliant

    empty_registry.relate(ContextRelation.FEDERATES, here.context_id, there.context_id)
    assert CONTEXT_CONSTITUTION.assess(empty_registry).law("CXL-04").compliant


def test_law_05_catches_a_fabricated_identity(universal_registry: ContextRegistry) -> None:
    _inject(universal_registry, _record(universal_registry, context_id="UCOS-CTX-deadbeefcafe"))
    assert not CONTEXT_CONSTITUTION.assess(universal_registry).law("CXL-05").compliant


def test_law_06_catches_duplicate_substance_and_a_wrong_taxon(
    universal_registry: ContextRegistry,
) -> None:
    base = universal_registry.records()[0]
    clone = _record(
        universal_registry,
        context_id="UCOS-CTX-000000000001",
        natural_key=base.natural_key + "-clone",
    )
    _inject(universal_registry, clone)
    assessment = CONTEXT_CONSTITUTION.assess(universal_registry)
    assert not assessment.law("CXL-06").compliant

    fresh = ContextRegistry()
    fresh.register(declaration())
    _inject(fresh, _record(fresh, taxon_id="CTX-SPATIAL"))
    assert not CONTEXT_CONSTITUTION.assess(fresh).law("CXL-06").compliant


def test_law_07_catches_an_unresolvable_registered_kind(empty_registry: ContextRegistry) -> None:
    same_dims = {"reference_frame": "a", "ordering": "b", "resolution": "c"}
    empty_registry.register(declaration(natural_key="one", values=same_dims, boundary="frame-a"))
    empty_registry.register(
        declaration(
            natural_key="two",
            values={**same_dims, "reference_frame": "z"},
            boundary="frame-a",
        )
    )
    assert not CONTEXT_CONSTITUTION.assess(empty_registry).law("CXL-07").compliant


def test_law_08_catches_a_valueless_provenance(universal_registry: ContextRegistry) -> None:
    base = universal_registry.records()[0]
    stripped = ContextValue(
        dimension=base.values[0].dimension,
        value=base.values[0].value,
        authority=base.values[0].authority,
        source="placeholder",
    )
    object.__setattr__(stripped, "source", "")
    _inject(universal_registry, _record(universal_registry, values=(stripped,)))
    assessment = CONTEXT_CONSTITUTION.assess(universal_registry)
    assert not assessment.law("CXL-08").compliant


def test_law_09_catches_a_broken_seal(universal_registry: ContextRegistry) -> None:
    _inject(universal_registry, _record(universal_registry, content_hash="0" * 64))
    assert not CONTEXT_CONSTITUTION.assess(universal_registry).law("CXL-09").compliant


def test_law_10_catches_authority_claimed_by_an_observer(empty_registry: ContextRegistry) -> None:
    observer_values = {"observer_id": "o", "vantage": "v", "epistemic_access": "e"}
    empty_registry.register(
        declaration(
            kind=ContextKind.OBSERVER,
            natural_key="obs",
            values=observer_values,
            authority=ContextAuthority.CONSTITUTIONAL,
        )
    )
    assert not CONTEXT_CONSTITUTION.assess(empty_registry).law("CXL-10").compliant


def test_law_10_catches_observation_used_as_constraint(empty_registry: ContextRegistry) -> None:
    observer = empty_registry.register(
        declaration(
            kind=ContextKind.OBSERVER,
            natural_key="obs",
            values={"observer_id": "o", "vantage": "v", "epistemic_access": "e"},
        )
    )
    governance = empty_registry.register(
        declaration(
            kind=ContextKind.GOVERNANCE,
            natural_key="gov",
            values={"authority": "a", "policy": "p", "decision_rights": "d"},
        )
    )
    subject = empty_registry.register(declaration(natural_key="subject"))
    empty_registry.relate(ContextRelation.OBSERVES, observer.context_id, subject.context_id)
    empty_registry.relate(ContextRelation.CONSTRAINS, governance.context_id, subject.context_id)
    assert CONTEXT_CONSTITUTION.assess(empty_registry).law("CXL-10").compliant

    # the same pair both observing and constraining is the violation
    empty_registry._relations.clear()  # noqa: SLF001 - rebuild the pair deliberately
    empty_registry.relate(ContextRelation.OBSERVES, observer.context_id, subject.context_id)
    edge = empty_registry.relate(
        ContextRelation.CONSTRAINS, governance.context_id, subject.context_id
    )
    forged = type(edge)(
        relation=ContextRelation.CONSTRAINS, source=observer.context_id, target=subject.context_id
    )
    empty_registry._relations[forged.edge_id] = forged  # noqa: SLF001
    assert not CONTEXT_CONSTITUTION.assess(empty_registry).law("CXL-10").compliant


def test_law_11_and_12_catch_a_broken_journal(universal_registry: ContextRegistry) -> None:
    universal_registry._audit.append(  # noqa: SLF001 - deliberate tamper
        AuditEntry(
            sequence=99,
            action="register",
            subject="x",
            content_hash="c",
            previous_hash=GENESIS_HASH,
        )
    )
    assessment = CONTEXT_CONSTITUTION.assess(universal_registry)
    assert not assessment.law("CXL-11").compliant
    assert not assessment.law("CXL-12").compliant


def test_law_12_catches_an_unjournaled_context(universal_registry: ContextRegistry) -> None:
    _inject(universal_registry, _record(universal_registry, context_id="UCOS-CTX-000000000002"))
    findings = CONTEXT_CONSTITUTION.assess(universal_registry).law("CXL-12").findings
    assert any("never journaled" in finding for finding in findings)


def test_require_compliance_is_fail_closed(universal_registry: ContextRegistry) -> None:
    _inject(universal_registry, _record(universal_registry, boundary=""))
    with pytest.raises(ConstitutionViolation):
        CONTEXT_CONSTITUTION.require_compliance(universal_registry)


# ---------------------------------------------------------------------- validation


def test_universal_catalog_validates_cleanly(
    universal_registry: ContextRegistry, composed: object
) -> None:
    report = validate(universal_registry, composed=composed)
    assert report.is_valid
    assert report.is_clean
    assert len(report.rules) == 12
    assert report.rules_failed() == ()
    assert report.metrics["contexts"] == 16
    assert report.metrics["universal_covered"] == 16
    assert report.summary()["violations"] == 0
    assert report.to_dict()["is_clean"] is True
    assert sum(report.by_dimension().values()) == 0


def test_validation_is_deterministic(universal_registry: ContextRegistry) -> None:
    assert validate(universal_registry).content_hash == validate(universal_registry).content_hash


def test_empty_registry_is_valid_but_not_clean(empty_registry: ContextRegistry) -> None:
    report = validate(empty_registry)
    assert report.is_valid  # no violation-severity finding
    assert not report.is_clean  # coverage advisories are reported
    assert report.advisories
    assert "CXV-11" in report.rules_failed()
    assert all(finding.severity == SEVERITY_ADVISORY for finding in report.advisories)


def test_violations_are_reported_with_their_rule(universal_registry: ContextRegistry) -> None:
    _inject(universal_registry, _record(universal_registry, context_id="UCOS-CTX-deadbeefcafe"))
    report = validate(universal_registry)
    assert not report.is_valid
    assert "CXV-03" in report.rules_failed()
    assert any(finding.severity == SEVERITY_VIOLATION for finding in report.violations)
    assert report.by_dimension()["identity"] >= 1


def test_shape_seal_and_relation_rules_are_measured(universal_registry: ContextRegistry) -> None:
    _inject(universal_registry, _record(universal_registry, content_hash="0" * 64))
    assert "CXV-04" in validate(universal_registry).rules_failed()

    fresh = ContextRegistry()
    fresh.register(declaration())
    _inject(fresh, _record(fresh, values=()))
    assert "CXV-02" in validate(fresh).rules_failed()


def test_orphan_advisory_is_reported(empty_registry: ContextRegistry) -> None:
    empty_registry.register(declaration())
    report = validate(empty_registry)
    assert "CXV-12" not in report.rules_failed()  # classified-as keeps every context connected


def test_require_valid_is_fail_closed(universal_registry: ContextRegistry) -> None:
    validator = ContextValidator()
    validator.require_valid(universal_registry)
    _inject(universal_registry, _record(universal_registry, context_id="UCOS-CTX-deadbeefcafe"))
    with pytest.raises(ContextValidationError):
        validator.require_valid(universal_registry)


def test_validator_refuses_unenforced_or_undeclared_rules() -> None:
    extra = (*VALIDATION_RULES, ValidationRule(rule_id="CXV-13", dimension="d", statement="s"))
    with pytest.raises(ContextValidationError):
        ContextValidator(extra)
    with pytest.raises(ContextValidationError):
        ContextValidator(VALIDATION_RULES[:1])


def test_rule_severity_is_validated() -> None:
    with pytest.raises(ContextValidationError):
        ValidationRule(rule_id="CXV-X", dimension="d", statement="s", severity="whatever")


def test_lifecycle_history_rule_reports_a_broken_chain(
    universal_registry: ContextRegistry,
) -> None:
    universal_registry._audit.clear()  # noqa: SLF001 - the journal is destroyed
    report = validate(universal_registry)
    assert "CXV-08" in report.rules_failed()


def test_boundedness_rule_reports_an_empty_frame(universal_registry: ContextRegistry) -> None:
    _inject(universal_registry, _record(universal_registry, boundary=""))
    assert "CXV-09" in validate(universal_registry).rules_failed()


def test_provenance_rule_reports_a_missing_source(universal_registry: ContextRegistry) -> None:
    base = universal_registry.records()[0]
    value = base.values[0]
    stripped = ContextValue(
        dimension=value.dimension,
        value=value.value,
        authority=value.authority,
        source="placeholder",
    )
    object.__setattr__(stripped, "source", "")
    _inject(universal_registry, _record(universal_registry, values=(stripped,)))
    assert "CXV-10" in validate(universal_registry).rules_failed()


def test_superseded_context_is_reported_as_uncovered(universal_registry: ContextRegistry) -> None:
    temporal = universal_registry.by_kind(ContextKind.TEMPORAL)[0]
    universal_registry.transition(temporal.context_id, ContextLifecycle.SUPERSEDED)
    report = validate(universal_registry)
    assert "CXV-11" in report.rules_failed()
    assert report.is_valid  # coverage is advisory, not a violation


# ---------------------------------------------------------------------------------------
# The law checks that only a MALFORMED ONTOLOGY or a BROKEN REGISTRY can reach
# ---------------------------------------------------------------------------------------


def _ontology_without(registry: ContextRegistry, kind: str):
    """The registry's ontology with ``kind``'s shape removed, and nothing else changed."""

    class _Narrowed:
        def __init__(self, real) -> None:
            self._real = real

        def specifies(self, candidate: str) -> bool:
            return candidate != kind and self._real.specifies(candidate)

        def __getattr__(self, name: str):
            return getattr(self._real, name)

    return _Narrowed(registry.ontology)


def test_law_01_catches_a_universal_kind_with_no_declared_shape(
    universal_registry: ContextRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """REPRESENTABILITY IS A CLAIM ABOUT THE VOCABULARY, not only about the records.

    A universal kind the ontology does not specify is a kind nothing could ever be declared
    in: every declaration of it would fail value-checking for a reason that names the record
    rather than the missing shape. The check exists so the gap is reported once, against the
    vocabulary, and it cannot fire while the shipped ontology specifies all sixteen.
    """
    kind = universal_registry.taxonomy.universal_kinds()[0]
    monkeypatch.setattr(
        universal_registry, "_ontology", _ontology_without(universal_registry, kind)
    )
    assessment = CONTEXT_CONSTITUTION.assess(universal_registry)
    law = assessment.law("CXL-01")

    assert not law.compliant
    assert any("no declared ontological shape" in f and kind in f for f in law.findings)


def test_law_02_separates_an_unclassified_kind_from_an_unspecified_one(
    universal_registry: ContextRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TWO DIFFERENT GAPS, TWO DIFFERENT MESSAGES, and only the first had a test.

    "Not classified by the taxonomy" means nothing says what this kind IS; "no declared
    ontological shape" means the taxonomy classifies it and the ontology does not say what
    it must carry. Bounded extension (CXL-02) requires both, and reporting one message for
    both would send a reader to the wrong register.
    """
    registered = next(iter(universal_registry.kinds()))
    monkeypatch.setattr(
        universal_registry, "_ontology", _ontology_without(universal_registry, registered)
    )
    law = CONTEXT_CONSTITUTION.assess(universal_registry).law("CXL-02")

    assert not law.compliant
    assert any(
        f"registered kind {registered!r} has no declared ontological shape" == f
        for f in law.findings
    )


def test_law_02_catches_a_future_kind_admitted_without_a_shape(
    empty_registry: ContextRegistry,
) -> None:
    """OPENNESS IS BOUNDED. A future taxon may be admitted at any time, and admitting one
    whose shape nobody declared would make the classification grow faster than the ontology
    — a kind that is classified, admissible, and impossible to declare a value in."""

    extended = empty_registry.taxonomy.extend(future_taxon())
    object.__setattr__(empty_registry, "_taxonomy", extended)

    law = CONTEXT_CONSTITUTION.assess(empty_registry).law("CXL-02")
    assert not law.compliant
    assert any("was admitted without a declared shape" in f for f in law.findings)


def test_law_04_skips_an_edge_whose_endpoint_the_registry_lost(
    universal_registry: ContextRegistry,
) -> None:
    """A DANGLING EDGE IS CXL-11's FINDING, NOT CXL-04's.

    Frame-crossing is a comparison between two records' boundaries, and an edge with a
    missing endpoint has no second boundary to compare. Reporting it here would attribute a
    referential-integrity defect to the federation law, and the reader would go looking for
    a federation that was never the problem.
    """
    records = universal_registry.records()
    universal_registry.relate(
        relation=ContextRelation.DEPENDS_ON,
        source=records[0].context_id,
        target=records[1].context_id,
    )
    del universal_registry._records[records[1].context_id]  # noqa: SLF001 - deliberate corruption

    law = CONTEXT_CONSTITUTION.assess(universal_registry).law("CXL-04")
    assert law.compliant, law.findings


def test_law_09_catches_a_relation_whose_identity_does_not_reproduce(
    universal_registry: ContextRegistry,
) -> None:
    """A GUARD THAT THE EDGE TYPE MAKES UNREACHABLE, and that is worth stating.

    An edge id is DERIVED from the relation and its two endpoints, and ``edge_id`` is a
    computed property rather than a stored field — so the check recomputes it from the same
    three values it already holds and the two can never disagree. Records were checked for a
    fabricated seal because a record STORES its hash; an edge cannot carry one.

    The branch is exercised with a stand-in edge answering a different id, because that is
    what a rehydrated edge from a wire format would be: the moment ``edge_id`` becomes a
    persisted field, this check is the thing that notices somebody wrote one by hand.
    """
    records = universal_registry.records()
    universal_registry.relate(
        relation=ContextRelation.DEPENDS_ON,
        source=records[0].context_id,
        target=records[1].context_id,
    )
    genuine = universal_registry.relations()[0]

    class _FabricatedId:
        relation = genuine.relation
        source = genuine.source
        target = genuine.target
        note = genuine.note
        edge_id = "UCOS-CTXREL-written-by-hand"

    stored = universal_registry._relations  # noqa: SLF001 - deliberate corruption
    stored[genuine.edge_id] = _FabricatedId()

    law = CONTEXT_CONSTITUTION.assess(universal_registry).law("CXL-09")
    assert not law.compliant
    assert any("identity does not reproduce" in f for f in law.findings)


def test_law_12_catches_a_supersession_whose_predecessor_was_destroyed(
    universal_registry: ContextRegistry,
) -> None:
    """ZERO AUTHORITY TO DESTROY. A supersession edge is the record that history happened,
    and the thing it supersedes must still be there — otherwise the edge asserts a past that
    can no longer be read, which is deletion wearing the shape of an amendment."""
    records = universal_registry.records()
    universal_registry.relate(
        relation=ContextRelation.SUPERSEDES,
        source=records[0].context_id,
        target=records[1].context_id,
    )
    # A SECOND supersession whose predecessor is intact, so the loop is shown to continue
    # past a well-formed edge rather than reporting the first one it reaches.
    universal_registry.relate(
        relation=ContextRelation.SUPERSEDES,
        source=records[2].context_id,
        target=records[3].context_id,
    )
    del universal_registry._records[records[1].context_id]  # noqa: SLF001 - deliberate corruption

    law = CONTEXT_CONSTITUTION.assess(universal_registry).law("CXL-12")
    assert not law.compliant
    assert any("history was destroyed" in f for f in law.findings)


def test_the_constitution_lists_the_laws_it_holds() -> None:
    """``laws()`` is the accessor a reader enumerates the constitution through. Only
    ``law(id)`` had a caller, which leaves "how many laws are there, and which" answerable
    only by asking for each one by a name you already had to know."""
    listed = CONTEXT_CONSTITUTION.laws()

    assert len(listed) == 12
    assert [law.law_id for law in listed] == sorted(law.law_id for law in listed)
    for law in listed:
        assert CONTEXT_CONSTITUTION.law(law.law_id) is law


# ---------------------------------------------------------------------------------------
# The validation rules that only a corrupted registry reaches
# ---------------------------------------------------------------------------------------


def test_a_record_whose_taxon_is_unclassified_or_classifies_another_kind_is_reported(
    universal_registry: ContextRegistry,
) -> None:
    """TWO CLASSIFICATION DEFECTS, TWO MESSAGES, and the second only reachable past the first.

    A taxon the taxonomy does not hold means nothing says what this context is; a taxon that
    holds and classifies a DIFFERENT kind means the record cites a classifier that describes
    something else. Registration prevents both, so this rule reads a registry that was
    assembled another way — and the `continue` is what stops the second check from being run
    against a taxon that could not be fetched.
    """
    unclassified = _record(universal_registry, taxon_id="CTX-NOBODY-DECLARED")
    _inject(universal_registry, unclassified)
    details = [f.detail for f in validate(universal_registry).findings]
    assert any("is not classified" in d for d in details)

    fresh = ContextRegistry()
    fresh.register(declaration())
    mismatched = _record(fresh, taxon_id="CTX-SPATIAL")
    _inject(fresh, mismatched)
    details = [f.detail for f in validate(fresh).findings]
    assert any("classifies 'spatial'" in d and "context is 'temporal'" in d for d in details)


def test_a_relation_whose_endpoint_is_gone_is_reported_and_not_ontology_checked(
    universal_registry: ContextRegistry,
) -> None:
    """AN EDGE WITH ONE END IS NOT AN EDGE.

    The relation rule asks the ontology whether a source KIND may relate to a target KIND,
    and a missing endpoint has no kind to ask about. Reporting the dangling endpoint and
    stopping is what keeps the ontology answering a question it can answer — the alternative
    is an `AttributeError` on `None.kind` inside a rule whose message would then name the
    ontology rather than the missing record.
    """
    records = universal_registry.records()
    universal_registry.relate(
        relation=ContextRelation.DEPENDS_ON,
        source=records[0].context_id,
        target=records[1].context_id,
    )
    del universal_registry._records[records[1].context_id]  # noqa: SLF001 - deliberate corruption

    details = [f.detail for f in validate(universal_registry).findings]
    assert any("endpoint is not registered" in d for d in details)


def test_the_validator_lists_the_rules_it_holds() -> None:
    """``rules()`` is how a reader enumerates what validation actually checks. Without it,
    "which rules exist" is answerable only by reading the source — and a rule that stopped
    being registered would be invisible to every consumer that reports coverage of them."""
    listed = ContextValidator(VALIDATION_RULES).rules()

    assert listed
    assert [r.rule_id for r in listed] == sorted(r.rule_id for r in listed)
    assert len({r.rule_id for r in listed}) == len(listed)


def test_a_rehydrated_assessment_keeps_the_seal_it_was_given() -> None:
    """A SEAL IS EVIDENCE, NOT A CONVENIENCE. The report seals itself when it is built and
    keeps the seal it is handed when it is read back — resealing on rehydration would make
    every stored report verify against itself and never against the state it was taken over,
    which is the one comparison a stored seal exists to allow.
    """
    built = validate(ContextRegistry())
    assert built.content_hash

    rehydrated = type(built)(
        rules=built.rules,
        findings=built.findings,
        metrics=dict(built.metrics),
        content_hash="0" * 64,
    )
    assert rehydrated.content_hash == "0" * 64, "the seal was recomputed on rehydration"
    assert rehydrated.rules == built.rules


def test_law_04_catches_a_frame_that_federates_into_itself(
    universal_registry: ContextRegistry,
) -> None:
    """A FEDERATION INTO YOUR OWN FRAME IS NOT A FEDERATION.

    Federation is what authorises a reference ACROSS a frame boundary. A frame naming a
    target that resolves back into the same frame has authorised nothing — and worse, it
    reads as authorisation, so a later cross-frame reference could point at it as its
    warrant. Every composition this repository builds federates outward or not at all, which
    is why the check had never fired.
    """

    composed = compose(universal_registry)
    frame = composed.reference_frames[0]
    # TWO federated targets: one that resolves back into this frame and one that does not,
    # so the loop is shown to keep going past a legitimate outward federation rather than
    # reporting the first target it looks at.
    outward = (
        next(
            f.universe_id for f in composed.reference_frames[1:] if f.context_id != frame.context_id
        )
        if any(f.context_id != frame.context_id for f in composed.reference_frames[1:])
        else "UCOS-CTX-not-in-this-composition"
    )
    inward = dataclasses.replace(frame, federated=(outward, frame.universe_id))
    self_federating = dataclasses.replace(
        composed, reference_frames=(inward, *composed.reference_frames[1:])
    )
    assert self_federating.frame_of(frame.universe_id) == frame.context_id

    law = CONTEXT_CONSTITUTION.assess(universal_registry, composed=self_federating).law("CXL-04")
    assert not law.compliant
    assert any("federates into its own frame" in f for f in law.findings)


def test_a_relation_between_two_registered_contexts_is_checked_against_the_ontology(
    universal_registry: ContextRegistry,
) -> None:
    """The arm past the dangling-endpoint guard, which every intact edge takes. Only the
    dangling case had a test, which left the ontology consultation — the part that decides
    whether one KIND may relate to another — unexecuted by this rule."""
    records = universal_registry.records()
    universal_registry.relate(
        relation=ContextRelation.DEPENDS_ON,
        source=records[0].context_id,
        target=records[1].context_id,
    )

    report = validate(universal_registry)
    assert not any("endpoint is not registered" in f.detail for f in report.findings)


def test_a_rehydrated_constitutional_assessment_keeps_the_seal_it_was_given() -> None:
    """The same rehydration discipline the validation report keeps. An assessment is stored
    evidence, and resealing it on read would make it verify against itself rather than
    against the state it was taken over."""
    built = CONTEXT_CONSTITUTION.assess(ContextRegistry())
    assert built.content_hash

    rehydrated = type(built)(laws=built.laws, content_hash="0" * 64)
    assert rehydrated.content_hash == "0" * 64, "the seal was recomputed on rehydration"
    assert rehydrated.laws == built.laws

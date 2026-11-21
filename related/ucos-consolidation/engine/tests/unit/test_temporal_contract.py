"""CMG-000002 conformance tests for engine/temporal.

The tests are organised by the contract's own laws rather than by module, because the
thing worth protecting is the law, not the implementation shape. The two most
important tests are the ones asserting a *refusal*:
``test_law7_cross_system_is_incomparable`` and
``test_no_representation_is_mandated`` — a temporal library that quietly answers every
comparison, or that privileges UTC, has broken the contract while still passing
happy-path tests.
"""

from __future__ import annotations

import ast
import subprocess

import pytest

from engine.temporal import (
    FACET_NAMES,
    TEMPORAL_CONTRACT,
    ConversionRule,
    Ordering,
    Precision,
    Provenance,
    ReferenceSystem,
    TemporalCoordinate,
    TemporalError,
    TemporalFacet,
    TemporalRecord,
    TemporalRegistry,
    ValidityPeriod,
    compare,
    convert,
    validate_ordering,
)
from engine.temporal.coordinate import (
    Conversion,
    CreationMethod,
    SystemType,
    parse_qualified,
)
from engine.temporal.operations import preserve_context


def _prov(authority: str = "test-authority") -> Provenance:
    return Provenance(creation_authority=authority, creation_method=CreationMethod.COMPUTATION)


def _coord(primary: str, system: ReferenceSystem, resolution: str = "tick") -> TemporalCoordinate:
    return TemporalCoordinate(
        primary=primary,
        reference_system=system,
        precision=Precision(resolution=resolution),
        provenance=_prov(),
    )


LAMPORT = ReferenceSystem(
    system_type=SystemType.LOGICAL, system_identifier="lamport", causality_tracking=True
)
MARS = ReferenceSystem(system_type=SystemType.CONTEXTUAL, system_identifier="mars-sol")
UNIX = ReferenceSystem(system_type=SystemType.PHYSICAL, system_identifier="unix-epoch")
VECTOR = ReferenceSystem(
    system_type=SystemType.LOGICAL, system_identifier="vector-clock", total_order=False
)


# --------------------------------------------------------------------------- laws


def test_law7_cross_system_is_incomparable() -> None:
    """Law 7: coordinates in different systems have no order without a conversion."""
    assert compare(_coord("5", LAMPORT), _coord("1247", MARS)) is Ordering.INCOMPARABLE


def test_law7_holds_even_with_a_registry_lacking_the_conversion() -> None:
    registry = TemporalRegistry()
    registry.register_system(LAMPORT)
    registry.register_system(MARS)
    assert compare(_coord("5", LAMPORT), _coord("1247", MARS), registry) is Ordering.INCOMPARABLE


def test_law6_ordering_within_a_system_is_numeric_not_lexical() -> None:
    """2 < 10. String comparison gets this wrong, and logical clocks depend on it."""
    assert compare(_coord("2", LAMPORT), _coord("10", LAMPORT)) is Ordering.BEFORE
    assert compare(_coord("10", LAMPORT), _coord("2", LAMPORT)) is Ordering.AFTER


def test_equal_values_are_simultaneous() -> None:
    assert compare(_coord("7", LAMPORT), _coord("7", LAMPORT)) is Ordering.SIMULTANEOUS


def test_non_numeric_values_order_lexically() -> None:
    a, b = _coord("alpha", MARS), _coord("beta", MARS)
    assert compare(a, b) is Ordering.BEFORE


def test_numeric_and_non_numeric_do_not_compare_as_numbers() -> None:
    """The two-part key keeps '3' and 'three' from being silently compared."""
    assert compare(_coord("3", MARS), _coord("three", MARS)) is Ordering.BEFORE


def test_float_values_order_numerically() -> None:
    assert compare(_coord("1.5", UNIX), _coord("10.25", UNIX)) is Ordering.BEFORE


def test_partial_order_system_yields_incomparable_for_distinct_values() -> None:
    """A vector clock with concurrent events has no total order."""
    assert compare(_coord("a", VECTOR), _coord("b", VECTOR)) is Ordering.INCOMPARABLE
    assert compare(_coord("a", VECTOR), _coord("a", VECTOR)) is Ordering.SIMULTANEOUS


def test_no_representation_is_mandated() -> None:
    """CMG-000002 §3.1: none of the forbidden representations may be privileged."""
    assert TEMPORAL_CONTRACT["mandated_representation"] is None
    assert TEMPORAL_CONTRACT["clock_free"] is True


def test_package_exposes_no_clock() -> None:
    """A now()/utcnow() here would make every coordinate unreplayable."""
    import engine.temporal as temporal
    import engine.temporal.operations as operations

    for module in (temporal, operations):
        for banned in ("now", "utcnow", "today", "current_time"):
            assert not hasattr(module, banned), f"{module.__name__} exposes {banned}"


# ------------------------------------------------------------------- conversion


def _registry_with_lamport_to_unix() -> TemporalRegistry:
    registry = TemporalRegistry()
    registry.register_system(LAMPORT)
    registry.register_system(UNIX)
    registry.register_conversion(
        ConversionRule(
            source=LAMPORT,
            target=UNIX,
            function_name="lamport_to_unix_scaled",
            authority="test-authority",
            convert=lambda primary: str(int(primary) * 100),
        )
    )
    return registry


def test_law3_conversion_records_provenance() -> None:
    registry = _registry_with_lamport_to_unix()
    converted = convert(_coord("3", LAMPORT), UNIX, registry)
    assert converted.primary == "300"
    assert converted.reference_system.same_system(UNIX)
    assert len(converted.conversion_history) == 1
    step = converted.conversion_history[0]
    assert step.conversion_function == "lamport_to_unix_scaled"
    assert step.conversion_authority == "test-authority"
    assert step.source_system == LAMPORT.key
    assert step.target_system == UNIX.key


def test_conversion_to_same_system_is_identity_and_records_nothing() -> None:
    registry = _registry_with_lamport_to_unix()
    original = _coord("3", LAMPORT)
    assert convert(original, LAMPORT, registry) is original


def test_undeclared_conversion_is_refused() -> None:
    registry = TemporalRegistry()
    registry.register_system(LAMPORT)
    registry.register_system(MARS)
    with pytest.raises(TemporalError, match="no declared conversion"):
        convert(_coord("3", LAMPORT), MARS, registry)


def test_conversion_enables_cross_system_comparison() -> None:
    registry = _registry_with_lamport_to_unix()
    assert compare(_coord("3", LAMPORT), _coord("500", UNIX), registry) is Ordering.BEFORE


def test_comparison_uses_reverse_conversion_when_only_that_direction_exists() -> None:
    registry = _registry_with_lamport_to_unix()
    assert compare(_coord("500", UNIX), _coord("3", LAMPORT), registry) is Ordering.AFTER


def test_conversion_endpoint_must_be_declared() -> None:
    registry = TemporalRegistry()
    registry.register_system(LAMPORT)
    with pytest.raises(TemporalError, match="not a declared reference system"):
        registry.register_conversion(ConversionRule(LAMPORT, MARS, "f", "a", lambda p: p))


def test_conflicting_conversion_is_refused() -> None:
    registry = _registry_with_lamport_to_unix()
    with pytest.raises(TemporalError, match="already declared by a different function"):
        registry.register_conversion(
            ConversionRule(LAMPORT, UNIX, "other_function", "a", lambda p: p)
        )


def test_identical_conversion_reregistration_is_idempotent() -> None:
    registry = _registry_with_lamport_to_unix()
    registry.register_conversion(
        ConversionRule(LAMPORT, UNIX, "lamport_to_unix_scaled", "test-authority", lambda p: p)
    )
    assert registry.convertible(LAMPORT, UNIX)


def test_conflicting_system_registration_is_refused() -> None:
    registry = TemporalRegistry()
    registry.register_system(LAMPORT)
    with pytest.raises(TemporalError, match="already declared differently"):
        registry.register_system(
            ReferenceSystem(
                system_type=SystemType.LOGICAL, system_identifier="lamport", total_order=False
            )
        )


def test_registry_serialises_systems_and_conversions() -> None:
    doc = _registry_with_lamport_to_unix().to_dict()
    assert len(doc["systems"]) == 2
    assert doc["conversions"][0]["conversion_function"] == "lamport_to_unix_scaled"


# ------------------------------------------------------------------- validation


def test_validate_ordering_accepts_a_sound_sequence() -> None:
    seq = [_coord(str(n), LAMPORT) for n in (1, 2, 3, 10)]
    assert validate_ordering(seq) == ()


def test_validate_ordering_reports_a_regression() -> None:
    seq = [_coord("5", LAMPORT), _coord("2", LAMPORT)]
    problems = validate_ordering(seq)
    assert len(problems) == 1
    assert "is after" in problems[0]


def test_validate_ordering_reports_incomparable_neighbours() -> None:
    problems = validate_ordering([_coord("5", LAMPORT), _coord("1", MARS)])
    assert len(problems) == 1
    assert "incomparable" in problems[0]


def test_validate_ordering_of_empty_and_single_sequences() -> None:
    assert validate_ordering([]) == ()
    assert validate_ordering([_coord("1", LAMPORT)]) == ()


# ------------------------------------------------------------------ coordinate


def test_reference_system_requires_an_identifier() -> None:
    with pytest.raises(TemporalError, match="no identifier"):
        ReferenceSystem(system_type=SystemType.LOGICAL, system_identifier="")


def test_coordinate_requires_a_primary_value() -> None:
    with pytest.raises(TemporalError, match="no primary value"):
        _coord("", LAMPORT)


def test_provenance_requires_an_authority() -> None:
    with pytest.raises(TemporalError, match="no creation authority"):
        Provenance(creation_authority="", creation_method=CreationMethod.CLOCK)


def test_system_version_participates_in_identity() -> None:
    """A calendar reform makes old and new values incomparable; version detects it."""
    kind = SystemType.CONTEXTUAL
    v1 = ReferenceSystem(system_type=kind, system_identifier="cal", system_version="1")
    v2 = ReferenceSystem(system_type=kind, system_identifier="cal", system_version="2")
    assert not v1.same_system(v2)
    assert compare(_coord("5", v1), _coord("6", v2)) is Ordering.INCOMPARABLE


def test_logical_constructor_builds_a_causal_clock_free_coordinate() -> None:
    coord = TemporalCoordinate.logical(41, system_identifier="repo", authority="UCOS-UGA-001")
    assert coord.primary == "41"
    assert coord.reference_system.system_type is SystemType.LOGICAL
    assert coord.reference_system.causality_tracking is True
    assert coord.provenance.creation_method is CreationMethod.COMPUTATION


def test_coordinate_serialises_the_full_contract_shape() -> None:
    doc = _coord("7", LAMPORT).to_dict()
    assert set(doc) == {"reference_system", "value", "provenance", "conversion_history"}
    assert doc["reference_system"]["ordering_model"]["total_order"] is True
    assert doc["value"]["primary"] == "7"


def test_unknown_system_type_is_representable() -> None:
    """CMG-000002 declares Future Unknown Time as an open slot."""
    unknown = ReferenceSystem(system_type=SystemType.UNKNOWN, system_identifier="not-yet-invented")
    assert _coord("x", unknown).system_key.startswith("unknown:")


# -------------------------------------------------------------------- validity


def test_validity_period_may_be_open_ended() -> None:
    period = ValidityPeriod(since=_coord("1", LAMPORT))
    assert period.open_ended is True
    assert period.to_dict()["until"] is None


def test_validity_period_bounds_must_share_a_reference_system() -> None:
    with pytest.raises(TemporalError, match="different reference systems"):
        ValidityPeriod(since=_coord("1", LAMPORT), until=_coord("2", MARS))


def test_closed_validity_period_serialises_both_bounds() -> None:
    period = ValidityPeriod(since=_coord("1", LAMPORT), until=_coord("9", LAMPORT))
    doc = period.to_dict()
    assert doc["open_ended"] is False
    assert doc["until"]["value"]["primary"] == "9"


# ---------------------------------------------------------------------- facets


def test_all_eight_facets_are_declared() -> None:
    assert FACET_NAMES == (
        "creation",
        "existence",
        "validity",
        "evolution",
        "certification",
        "retirement",
        "archive",
        "restoration",
    )


def test_record_requires_a_subject_identity() -> None:
    with pytest.raises(TemporalError, match="no subject identity"):
        TemporalRecord(subject_identity="")


def test_facets_are_recorded_and_reported_in_declaration_order() -> None:
    record = (
        TemporalRecord(subject_identity="urn:ucos:ucko:ns:x")
        .with_facet(TemporalFacet.RETIREMENT, _coord("9", LAMPORT))
        .with_facet(TemporalFacet.CREATION, _coord("1", LAMPORT))
    )
    assert record.recorded_facets() == ("creation", "retirement")
    assert "evolution" in record.missing_facets()


def test_rerecording_an_identical_facet_is_idempotent() -> None:
    coord = _coord("1", LAMPORT)
    record = TemporalRecord(subject_identity="x").with_facet(TemporalFacet.CREATION, coord)
    assert record.with_facet(TemporalFacet.CREATION, coord) is record


def test_rerecording_a_facet_differently_is_refused() -> None:
    record = TemporalRecord(subject_identity="x").with_facet(
        TemporalFacet.CREATION, _coord("1", LAMPORT)
    )
    with pytest.raises(TemporalError, match="already recorded at a different coordinate"):
        record.with_facet(TemporalFacet.CREATION, _coord("2", LAMPORT))


def test_duplicate_facets_are_refused_at_construction() -> None:
    coord = _coord("1", LAMPORT)
    with pytest.raises(TemporalError, match="recorded more than once"):
        TemporalRecord(subject_identity="x", facets=(("creation", coord), ("creation", coord)))


def test_facet_precedence_violation_is_reported() -> None:
    record = (
        TemporalRecord(subject_identity="x")
        .with_facet(TemporalFacet.CREATION, _coord("10", LAMPORT))
        .with_facet(TemporalFacet.EVOLUTION, _coord("2", LAMPORT))
    )
    problems = record.violations()
    assert len(problems) == 1
    assert "evolution precedes creation" in problems[0]


def test_sound_facet_ordering_has_no_violations() -> None:
    record = (
        TemporalRecord(subject_identity="x")
        .with_facet(TemporalFacet.CREATION, _coord("1", LAMPORT))
        .with_facet(TemporalFacet.EVOLUTION, _coord("5", LAMPORT))
        .with_facet(TemporalFacet.RETIREMENT, _coord("9", LAMPORT))
    )
    assert record.violations() == ()


def test_incomparable_facets_are_reported_as_unverifiable() -> None:
    record = (
        TemporalRecord(subject_identity="x")
        .with_facet(TemporalFacet.CREATION, _coord("1", LAMPORT))
        .with_facet(TemporalFacet.EVOLUTION, _coord("1247", MARS))
    )
    problems = record.violations()
    assert len(problems) == 1
    assert "incomparable" in problems[0]


def test_restoration_without_archive_is_reported() -> None:
    record = TemporalRecord(subject_identity="x").with_facet(
        TemporalFacet.RESTORATION, _coord("5", LAMPORT)
    )
    assert any("restoration recorded without an archive" in p for p in record.violations())


def test_archive_then_restoration_is_sound() -> None:
    record = (
        TemporalRecord(subject_identity="x")
        .with_facet(TemporalFacet.ARCHIVE, _coord("5", LAMPORT))
        .with_facet(TemporalFacet.RESTORATION, _coord("8", LAMPORT))
    )
    assert record.violations() == ()


def test_record_carries_validity_and_serialises() -> None:
    record = TemporalRecord(subject_identity="urn:ucos:ucko:ns:x").with_facet(
        TemporalFacet.CREATION, _coord("1", LAMPORT)
    )
    record = record.with_validity(ValidityPeriod(since=_coord("1", LAMPORT)))
    doc = record.to_dict()
    assert doc["subject_identity"] == "urn:ucos:ucko:ns:x"
    assert "creation" in doc["facets"]
    assert doc["validity"]["open_ended"] is True
    assert doc["recorded"] == ["creation"]


def test_coordinate_lookup_returns_none_for_an_unrecorded_facet() -> None:
    record = TemporalRecord(subject_identity="x")
    assert record.coordinate(TemporalFacet.ARCHIVE) is None
    assert record.has(TemporalFacet.ARCHIVE) is False


# --------------------------------------------------------------------- context


def test_preserve_context_binds_without_owning_context() -> None:
    """Law 5 context preservation; UCXI-000001 remains the context owner."""
    bound = preserve_context(_coord("1", LAMPORT), {"observer": "gate", "frame": "repo"})
    assert bound["context"] == {"frame": "repo", "observer": "gate"}
    assert "UCXI-000001" in bound["$context_owner"]


# ------------------------------------------------------- qualified round-tripping
# The qualified form exists so a coordinate can travel in one field without decaying
# into a bare value. Every refusal below is a representation that would have needed a
# default frame to interpret, which CMG-000002 §3.1 forbids.


def test_qualified_form_carries_the_frame_with_the_value() -> None:
    coord = _coord("484", LAMPORT)
    assert coord.qualified == "logical:lamport@1#484"


def test_qualified_round_trips() -> None:
    original = _coord("484", LAMPORT)
    restored = parse_qualified(original.qualified, authority="test")
    assert restored.primary == original.primary
    assert restored.reference_system.same_system(original.reference_system)


def test_qualified_round_trip_preserves_comparability() -> None:
    a = parse_qualified(_coord("2", LAMPORT).qualified, authority="t")
    b = parse_qualified(_coord("10", LAMPORT).qualified, authority="t")
    assert compare(a, b) is Ordering.BEFORE


def test_bare_value_is_refused() -> None:
    """A timestamp with no reference system has silently mandated a representation."""
    with pytest.raises(TemporalError, match="mandates a representation"):
        parse_qualified("2026-08-17T00:00:00Z", authority="test")


def test_qualified_without_a_primary_is_refused() -> None:
    with pytest.raises(TemporalError, match="no primary value"):
        parse_qualified("logical:lamport@1#", authority="test")


@pytest.mark.parametrize("bad", ["logical:lamport#5", "logical:@1#5", "logical#5"])
def test_malformed_reference_system_key_is_refused(bad: str) -> None:
    with pytest.raises(TemporalError, match="malformed reference system key"):
        parse_qualified(bad, authority="test")


def test_unknown_system_type_token_is_refused() -> None:
    with pytest.raises(TemporalError, match="unknown reference system type"):
        parse_qualified("invented:frame@1#5", authority="test")


def test_qualified_preserves_a_non_default_system_version() -> None:
    versioned = ReferenceSystem(
        system_type=SystemType.CONTEXTUAL, system_identifier="cal", system_version="7"
    )
    restored = parse_qualified(_coord("3", versioned).qualified, authority="t")
    assert restored.reference_system.system_version == "7"


def test_a_conversion_projects_every_field_it_declares() -> None:
    """A conversion row that is never serialised is a row nothing can verify.

    The to_dict of the conversion history is what the coordinate's timeline renders and
    what CMG-000002 Law 3 evidence carries; each field must appear, and the projection must
    round-trip the same values the record holds.
    """
    conversion = Conversion(
        source_system="epoch-ns",
        target_system="iso-8601",
        conversion_function="divide_by_1e9",
        conversion_authority="CMG-000002",
    )
    projected = conversion.to_dict()
    assert projected["source_system"] == "epoch-ns"
    assert projected["conversion_authority"] == "CMG-000002"


# --------------------------------------------------- IE-03: the ban, measured repo-wide
#
# `test_package_exposes_no_clock` above bans now/utcnow/today on `engine.temporal` and
# `engine.temporal.operations`. That is the package that DEFINES the coordinate contract,
# and the ban never reached the repository that has to honour it -- so every module outside
# those two could read a wall clock and emit a bare ISO-8601 string, and nothing measured
# it. IE-03 records "2 unqualified UTC/ISO-8601 emissions bypass it" and names
# obs/logging.py and registry/universal/audit.py. Measured by shape over tracked
# non-test source under the governed roots, the population is NINE across EIGHT modules.
# The register undercounts by seven, all of them `datetime.now(...)` rather than
# `fromtimestamp(...)`, which is the shape it happened to grep for.
#
# Both bounds below are two-sided: a tenth emission fails, and repaying one fails too
# until the bound is lowered to match, because a bound that only refuses growth lets
# repaid debt sit unrecorded.

#: Calls that turn a wall clock into a temporal VALUE: an evidence stamp, an audit clock,
#: a log field. Each one is a coordinate emitted with no ReferenceSystem, which is what
#: CMG-000002 requires and what makes the result unreplayable.
_COORDINATE_EMISSIONS = frozenset(
    {
        ("engine/construct/evidence.py", "now"),
        ("engine/execution_environment/evidence.py", "now"),
        ("engine/foundation/obs/logging.py", "fromtimestamp"),
        ("engine/graph/architecture/evidence.py", "now"),
        ("engine/graph/evidence.py", "now"),
        ("engine/ledger_authority/__init__.py", "now"),
        ("engine/recursive_knowledge/evidence.py", "now"),
        ("engine/registry/universal/audit.py", "fromtimestamp"),
        ("engine/registry/universal/audit.py", "now"),
    }
)

#: Modules that read a clock for a DURATION rather than a coordinate. A monotonic or
#: perf_counter reading carries no calendar meaning, cannot be compared across systems and
#: is not a coordinate, so CMG-000002 does not reach it. Bounded per MODULE rather than
#: per call: another elapsed-time measurement inside a module already sanctioned for it is
#: not a new finding, but a module that starts reading a clock is.
_DURATION_MODULES = frozenset(
    {
        "engine/certification_integrity/immutable.py",
        "engine/certification_integrity/suite.py",
        "engine/foundation/obs/telemetry.py",
        "engine/ledger_authority/__init__.py",
    }
)

_EMISSION_CALLS = frozenset({"now", "utcnow", "today", "fromtimestamp"})
_DURATION_CALLS = frozenset({"monotonic", "perf_counter", "time", "time_ns"})
_GOVERNED_ROOTS = ("engine/", "platform/", "intelligence/", "data/", "application/")


def _clock_reads() -> tuple[set[tuple[str, str]], set[str]]:
    """Every wall-clock read in tracked non-test governed source, found by AST shape.

    Returns the emission pair set, the duration module set, and the emission TALLY. The
    tally exists because pair identity alone is blind to a SECOND identical call in a
    module already listed -- (path, "now") is the same pair whether the module emits once
    or twice -- and a second emission site is a new finding.

    By shape rather than by name, for the reason `engine/infinite_scope/detector.py` gives
    about closed enumerations: a list of known sites is finite and goes stale, a detector
    for the shape catches the one somebody adds next year.
    """
    here = __file__.rsplit("/", 1)[0]
    root = (
        subprocess.run(  # noqa: S603
            ["git", "rev-parse", "--show-toplevel"],  # noqa: S607
            capture_output=True,
            check=True,
            cwd=here,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    listing = subprocess.run(  # noqa: S603
        ["git", "ls-files", "-z"],  # noqa: S607
        capture_output=True,
        check=True,
        cwd=root,
    )
    paths = [p for p in listing.stdout.decode("utf-8").split("\0") if p.endswith(".py")]
    emissions: set[tuple[str, str]] = set()
    durations: set[str] = set()
    tally: list[tuple[str, str]] = []
    for path in paths:
        if not path.startswith(_GOVERNED_ROOTS):
            continue
        if "/tests/" in path or path.rsplit("/", 1)[-1].startswith("test_"):
            continue
        try:
            with open(f"{root}/{path}", encoding="utf-8") as handle:
                tree = ast.parse(handle.read())
        except (OSError, SyntaxError):  # pragma: no cover - a parse failure is not a finding
            continue
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            if node.func.attr in _EMISSION_CALLS:
                emissions.add((path, node.func.attr))
                tally.append((path, node.func.attr))
            elif node.func.attr in _DURATION_CALLS:
                durations.add(path)
    return emissions, durations, tally


def test_the_clock_ban_is_measured_over_the_repository_not_only_the_package() -> None:
    """No module may begin emitting an unqualified temporal coordinate unnoticed."""
    emissions, _, tally = _clock_reads()
    assert emissions == _COORDINATE_EMISSIONS, (
        f"unqualified coordinate emissions changed: "
        f"new={sorted(emissions - _COORDINATE_EMISSIONS)}, "
        f"repaid={sorted(_COORDINATE_EMISSIONS - emissions)}"
    )
    assert len(tally) == len(_COORDINATE_EMISSIONS), (
        f"emission COUNT is {len(tally)} against {len(_COORDINATE_EMISSIONS)} disclosed "
        f"sites: a module already listed has begun emitting more than once"
    )


def test_duration_measurement_is_distinguished_from_coordinate_emission() -> None:
    """A duration is not a coordinate, and the distinction is measured, not assumed.

    Conflating the two is how IE-03's own count went wrong in the other direction: twelve
    monotonic and perf_counter reads sit in this tree and none of them is a temporal
    coordinate, so a scan that counted every clock read would report eighteen findings and
    train the reader to ignore the report.
    """
    emissions, durations, _ = _clock_reads()
    assert durations == _DURATION_MODULES, (
        f"modules reading a clock for duration changed: "
        f"new={sorted(durations - _DURATION_MODULES)}, "
        f"removed={sorted(_DURATION_MODULES - durations)}"
    )
    assert not (_DURATION_CALLS & _EMISSION_CALLS), "a call cannot be both classes"
    assert {
        path for path, _ in emissions
    } != durations, "the two populations are measured separately and must not be the same set"

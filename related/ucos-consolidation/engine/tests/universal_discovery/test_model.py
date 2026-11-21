"""UCOS-OMEGA-001 Part 1 — the vocabulary, exercised rather than merely imported.

WHY THIS MODULE WAS AT 24%. ``model.py`` is where Ω's terms are DEFINED, so every other suite
imports it and almost none of it runs: the dataclasses are constructed by ``surface.build`` from a
real repository, and their record renderings, their refusal predicates and their emptiness guards
are reached only on paths a whole-suite run happens to take. A vocabulary nothing exercises is a
vocabulary whose guards can rot into no-ops while every import of it keeps succeeding.

THE GUARD THAT MATTERS MOST IS ``Population.__post_init__``. Every Ω invariant is vacuously true
over an empty world, so an empty population must FAULT rather than report a pass — the single most
dangerous defect this programme could have, because it converts "this repository is ungoverned"
into "this repository is fully governed". It is asserted here directly, in both of its forms.
"""

from __future__ import annotations

import pytest

from engine.universal_discovery.model import (
    ARCHIVED,
    AUTHORITY_REQUIRED,
    CONVERGENT,
    DENSITY,
    DISPOSITIONS,
    ENTROPY,
    EXEMPTED,
    GENERATED,
    HELD,
    IMPROVED,
    JUSTIFIED,
    LOWER_IS_BETTER,
    MEASURED,
    MONOTONIC,
    RATCHET_KINDS,
    REGRESSED,
    SEEDED,
    STALLED,
    SURFACE_DISPOSITIONS,
    TRANSIENT,
    Artifact,
    Observation,
    OmegaError,
    Population,
)


def _artifact(**overrides: object) -> Artifact:
    fields: dict[str, object] = {
        "path": "engine/thing.py",
        "root": "engine",
        "module": "engine.thing",
        "disposition": MEASURED,
        "disposition_rule": "Ω-C-04",
        "disposition_reason": "coverage names its package",
        "authority": "engine.thing",
        "authority_rule": "Ω-A-04",
        "reachable": True,
        "reached_by": ("test", "python"),
        "statements": 12,
        "callables": 3,
        "imports": 4,
    }
    fields.update(overrides)
    return Artifact(**fields)  # type: ignore[arg-type]


def _population(**overrides: object) -> Population:
    fields: dict[str, object] = {
        "paths": ("engine/thing.py",),
        "roots": ("engine",),
        "importable_roots": ("engine",),
        "test_roots": ("engine/tests",),
        "measurable_packages": ("engine.thing",),
    }
    fields.update(overrides)
    return Population(**fields)  # type: ignore[arg-type]


# ------------------------------------------------------------------------ the vocabulary


def test_the_five_dispositions_are_the_whole_vocabulary() -> None:
    assert DISPOSITIONS == (MEASURED, EXEMPTED, GENERATED, ARCHIVED, TRANSIENT)
    assert len(set(DISPOSITIONS)) == 5


def test_transient_is_the_only_disposition_that_may_lack_an_authority() -> None:
    """Ω-2 admits ``authority = ""`` for exactly one disposition, and the reason is that
    transience is the only self-justifying claim: an artifact declared not to persist cannot
    acquire a durable owner."""
    assert AUTHORITY_REQUIRED == frozenset({MEASURED, EXEMPTED, GENERATED, ARCHIVED})
    assert TRANSIENT not in AUTHORITY_REQUIRED
    assert AUTHORITY_REQUIRED < set(DISPOSITIONS)


def test_only_measured_and_exempted_enter_the_surface_denominator() -> None:
    """GENERATED and ARCHIVED are excluded because their bytes are owned elsewhere, TRANSIENT
    because it does not persist. That is what stops the ratio being flattered by reclassification
    alone — a move out of the denominator has to be justified by a measured property."""
    assert SURFACE_DISPOSITIONS == frozenset({MEASURED, EXEMPTED})
    assert SURFACE_DISPOSITIONS < set(DISPOSITIONS)


def test_every_ratchet_kind_falls_toward_better() -> None:
    """One comparison serves every kind. A metric whose better direction is up is expressed as its
    complement, so no per-metric sign convention exists to get wrong."""
    assert RATCHET_KINDS == (MONOTONIC, CONVERGENT, DENSITY, ENTROPY)
    assert LOWER_IS_BETTER == frozenset(RATCHET_KINDS)


def test_the_six_verdicts_are_distinct() -> None:
    verdicts = (IMPROVED, HELD, STALLED, REGRESSED, JUSTIFIED, SEEDED)
    assert len(set(verdicts)) == 6


# --------------------------------------------------------------------------- the artifact


def test_an_artifact_renders_every_verdict_it_carries() -> None:
    """The record is what a reader checks the claims against, so a field missing from it is a
    verdict nobody can audit."""
    record = _artifact().as_record()
    assert set(record) == {
        "path",
        "root",
        "module",
        "disposition",
        "disposition_rule",
        "disposition_reason",
        "authority",
        "authority_rule",
        "reachable",
        "reached_by",
        "statements",
        "callables",
        "imports",
    }
    assert record["reached_by"] == ["test", "python"]
    assert isinstance(record["reached_by"], list), "the record must be JSON-shaped"


def test_an_artifact_is_frozen_so_three_verdicts_cannot_drift_apart() -> None:
    """Disposition, authority and reachability are functions of one population. Mutating one after
    construction would produce a record computed over three worlds."""
    artifact = _artifact()
    with pytest.raises((AttributeError, TypeError)):
        artifact.disposition = EXEMPTED  # type: ignore[misc]


def test_an_unimportable_artifact_carries_an_empty_module_name() -> None:
    assert _artifact(module="", root="00-MASTER").as_record()["module"] == ""


# ------------------------------------------------------------------------ the observation


def test_an_observation_refuses_only_on_a_regression_or_a_stall() -> None:
    """The refusal predicate IS the gate's verdict, so the set it tests has to be exact."""
    for verdict in (REGRESSED, STALLED):
        assert Observation("m", CONVERGENT, 1.0, 0.0, verdict, "s").refused
    for verdict in (IMPROVED, HELD, JUSTIFIED, SEEDED):
        assert not Observation("m", CONVERGENT, 1.0, 0.0, verdict, "s").refused


def test_an_observation_record_omits_a_justification_it_does_not_have() -> None:
    """An empty justification key would read as "justified with no reason", which is the one thing
    a justified regression may never be."""
    assert "justification" not in Observation("m", MONOTONIC, 1.0, 1.0, HELD, "s").as_record()
    justified = Observation("m", MONOTONIC, 2.0, 1.0, JUSTIFIED, "s", justification="a reason")
    assert justified.as_record()["justification"] == "a reason"


def test_a_ratio_metric_renders_its_numerator_and_denominator() -> None:
    """A density printed without its terms cannot be re-derived, and a figure nobody can re-derive
    is a claim rather than a measurement."""
    plain = Observation("m", CONVERGENT, 3.0, 3.0, HELD, "s")
    assert "ratio" not in plain.as_record()

    ratio = Observation("d", DENSITY, 0.25, 0.25, HELD, "s", ratio=(1, 4))
    assert ratio.as_record()["ratio"] == {"numerator": 1, "denominator": 4}


def test_a_seeded_observation_has_no_best_ever_value_and_does_not_refuse() -> None:
    """The first measurement of a metric cannot regress against a bound that does not exist."""
    seeded = Observation("new", CONVERGENT, 9.0, None, SEEDED, "s")
    assert seeded.best is None
    assert not seeded.refused
    assert seeded.as_record()["best"] is None


# -------------------------------------------------------------------------- the population


def test_an_empty_population_faults_rather_than_reporting_a_pass() -> None:
    """THE MOST DANGEROUS DEFECT THIS PROGRAMME COULD HAVE. Every Ω invariant is vacuously true
    over an empty world, so an empty answer would convert "this repository is ungoverned" into
    "this repository is fully governed"."""
    with pytest.raises(OmegaError) as refusal:
        _population(paths=())
    assert "vacuously true" in str(refusal.value)


def test_a_population_with_paths_but_no_roots_faults() -> None:
    """The second emptiness, and it is a different fault: tracked Python exists and the root
    derivation returned nothing, which means the derivation is broken rather than the world."""
    with pytest.raises(OmegaError):
        _population(roots=())


def test_a_population_admits_declarations_and_defaults_them_to_empty() -> None:
    """Exemptions and transient declarations are the only human-authored inputs, and both are
    OPTIONAL — a repository that declares neither is a complete world, not a broken one."""
    bare = _population()
    assert bare.declared_exemptions == {}
    assert bare.declared_transient == {}

    declared = _population(
        declared_exemptions={"engine.dead": "no test files"},
        declared_transient={"scratch.py": "not persisted"},
    )
    assert declared.declared_exemptions == {"engine.dead": "no test files"}
    assert declared.declared_transient == {"scratch.py": "not persisted"}


def test_a_population_is_frozen() -> None:
    population = _population()
    with pytest.raises((AttributeError, TypeError)):
        population.paths = ()  # type: ignore[misc]


def test_omega_error_is_an_ordinary_runtime_error() -> None:
    """So a caller that catches RuntimeError does not silently swallow a fault it cannot handle
    while believing it caught something narrower."""
    assert issubclass(OmegaError, RuntimeError)

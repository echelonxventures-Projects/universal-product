"""Fixtures for the UCKP (Universal Constitutional Knowledge Universe) suite.

The assembled universe is expensive to build — discovery walks the package, ten
persistence adapters are constructed, and the assimilated variant reads and maps 1201
artifacts — so both are session-scoped. They are immutable values, which is what makes
sharing them across tests safe: :class:`ConstitutionalUniverse` is frozen and its
registry, timeline and ledger are append-only, so no test can hand a mutated universe to
the next one.

Tests that need to *break* something build their own small universe from the
``minimal_*`` factories instead.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.uckp.assimilation import load_artifact_registry
from engine.uckp.identity import urn_for
from engine.uckp.registry import UniversalKnowledgeRegistry
from engine.uckp.ucko import UCKO
from engine.uckp.universe import ConstitutionalUniverse, build_universe
from engine.uckp.validation import validate_universe
from engine.uckp.values import Relationship
from engine.uckp.vocabulary import VocabularyRegistry, build_vocabulary_registry

#: The namespace the fixtures mint test objects in.
TEST_NAMESPACE = "test"


@pytest.fixture
def vocabularies() -> VocabularyRegistry:
    """A fresh vocabulary registry — never the universe's own, which tests must not widen."""
    return build_vocabulary_registry()


@pytest.fixture
def root_urn() -> str:
    return urn_for(TEST_NAMESPACE, "ROOT")


@pytest.fixture
def minimal_root(root_urn: str) -> UCKO:
    """A self-grounding root object: the only kind whose authority is its own."""
    return UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="ROOT",
        concept="test root law",
        definition="the self-grounding root of a test universe",
        kind="law",
        category="law",
        authority_tier="constitutional",
        derives_from=root_urn,
        owner="test-authority",
        instrument="engine.tests.uckp",
    )


@pytest.fixture
def minimal_child(minimal_root: UCKO) -> UCKO:
    """A child deriving its authority from the root."""
    return UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="CHILD",
        concept="test principle",
        definition="a principle deriving from the test root",
        kind="principle",
        category="principle",
        authority_tier="constitutional",
        derives_from=minimal_root.ucko_id,
        owner="test-authority",
        instrument="engine.tests.uckp",
        relationships=(Relationship("derived-from", minimal_root.ucko_id, "authority"),),
    )


@pytest.fixture
def minimal_registry(
    minimal_root: UCKO, minimal_child: UCKO, vocabularies: VocabularyRegistry
) -> UniversalKnowledgeRegistry:
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies)
    registry.register_all((minimal_root, minimal_child))
    return registry


@pytest.fixture
def mint_object():
    """A factory for lawful test objects, so negative tests vary one thing at a time."""

    def _mint(local_name: str, *, derives_from: str, **overrides) -> UCKO:
        fields = {
            "namespace": TEST_NAMESPACE,
            "local_name": local_name,
            "concept": f"concept {local_name}",
            "definition": f"the meaning of {local_name}, unique to it",
            "kind": "fact",
            "category": "knowledge",
            "authority_tier": "engineering",
            "derives_from": derives_from,
            "owner": "test-authority",
            "instrument": "engine.tests.uckp",
        }
        fields.update(overrides)
        return UCKO.mint(**fields)

    return _mint


@pytest.fixture(scope="session")
def persistence_base(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("uckp-persistence")


@pytest.fixture(scope="session")
def universe(persistence_base: Path) -> ConstitutionalUniverse:
    """The constitutional universe: discovered, coherent, no assimilated corpus."""
    return build_universe(persistence_base=persistence_base)


@pytest.fixture(scope="session")
def validated_universe(universe: ConstitutionalUniverse):
    """The validation report for the lawful universe, measured once for the session.

    WHY CACHING THIS IS NOT A WEAKENING, AND WHAT LICENSES IT. `validate_universe` is a pure
    function of an immutable universe, and the suite does not take that on trust:
    `test_the_report_is_deterministic_and_content_addressed` calls it TWICE and asserts the two
    reports share a digest and serialize identically. That test is the licence for this fixture
    and must keep calling the function directly — the moment it consumes the cache instead, the
    property that makes the cache sound stops being measured.

    WHAT IT COST TO NOT HAVE THIS. Measured across a full sharded run: this one call was the
    largest single cost in the suite, roughly 70s per invocation against a session-scoped
    universe that had already been built. `test_each_invariant_reports_the_measurements_its_
    verdict_rests_on` is parametrized over all seventeen invariants, so it alone paid that
    seventeen times to ask seventeen questions of one immutable report.

    The report is consumed through read-only accessors (`result`, `to_dict`, `summary`,
    `digest`), so sharing one instance changes what is measured in no way.
    """
    return validate_universe(universe)


@pytest.fixture(scope="session")
def assimilated(tmp_path_factory):
    """The universe with every existing UCOS artifact assimilated into it.

    Skips rather than fails when the artifact registry is absent: the universe is
    repository-independent by construction (Article 4), so a checkout without the
    corpus is a legitimate state in which this particular measurement cannot be taken.
    """
    from engine.uckp.assimilation import ARTIFACT_REGISTRY_PATH, build_assimilated_universe

    source_root = Path(__file__).resolve().parents[3]
    if not (source_root / ARTIFACT_REGISTRY_PATH).is_file():
        pytest.skip(f"{ARTIFACT_REGISTRY_PATH} is not present in this checkout")
    base = tmp_path_factory.mktemp("uckp-assimilated")
    return build_assimilated_universe(source_root=source_root, persistence_base=base)


@pytest.fixture(scope="session")
def assimilated_universe(assimilated) -> ConstitutionalUniverse:
    return assimilated[0]


@pytest.fixture(scope="session")
def assimilation_report(assimilated):
    return assimilated[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


#: P0-BLOCKER-ERADICATION-001 — the corpus population is MEASURED, never asserted as a
#: literal. Snapshot literals made this suite fail on every legitimate corpus growth: the
#: same assertion has broken at 1206, at 1220, at 1227 and again at 1231, each time reported
#: as a test failure when nothing was wrong except that the repository had grown. The
#: invariants these tests actually name — "every artifact becomes exactly one object", "every
#: object reconstructs its source record exactly" — are relations between the register and the
#: assimilation of it, and a relation is proven by comparing the two sides, not by comparing
#: one side to a number a human transcribed on a particular day. Deriving the expectation from
#: the register under measurement keeps the invariant exact and retires the recurrence class.
@pytest.fixture(scope="session")
def corpus_size(repo_root: Path) -> int:
    """How many artifacts the registry under measurement actually holds."""
    _, records = load_artifact_registry(repo_root)
    return len(records)


@pytest.fixture(scope="session")
def uga_projection_size() -> int:
    """How many objects engine.uckp.uga_projection contributes right now.

    Measured live from the same UGA registry file the provider itself reads
    (`00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json`), for the identical
    reason `corpus_size` above is measured rather than transcribed: this population
    grows with the repository, not with a constitutional amendment, so a literal here
    would join the exact recurrence class P0-BLOCKER-ERADICATION-001 already retired
    for the corpus count.
    """
    from engine.uckp.uga_projection import _load_entries

    return len(_load_entries())


@pytest.fixture(scope="session")
def constitution_object_count() -> int:
    """Objects the constitution mints for itself, independent of the corpus.

    This one IS a literal, and legitimately so: it counts the authored constitutional
    objects, which change only when the constitution is amended — never when a repository
    artifact is added. Keeping it separate from :func:`corpus_size` is what makes a change
    in the total attributable to one cause or the other.

    175 constitution + capability objects, plus the 18 UCOS-CAA-001 alignment objects
    (the binding, the identity derivation, 8 authority roles and 8 alignment rules — role
    ORTHOGONAL and rule CAA-INV-08 added by the CMG/UCKP reconciliation) that
    :mod:`engine.uckp.alignment` contributes as the third declarative provider.
    """
    return 193

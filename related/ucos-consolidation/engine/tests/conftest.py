"""Shared pytest fixtures for the EC-1 engine test suite.

Provides small, self-contained registry substrates written to ``tmp_path`` so the
Registry Adapter (EPIC-002) can be exercised without touching the read-only
certified corpus (DP-03). A separate fixture points at the real ``00-BOOK/DATA``
for read-only integration checks (present only when the corpus is available).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.registry.source import (
    ARTIFACTS_FILE,
    RELATIONSHIPS_FILE,
    VOLUMES_FILE,
    RegistrySource,
    default_data_dir,
)

_TRACE_EMPTY = {
    "requirement": [],
    "architecture": [],
    "design": [],
    "implementation": [],
    "source_code": [],
    "unit_test": [],
    "integration_test": [],
    "functional_test": [],
    "security_test": [],
    "certification": [],
    "deployment": [],
    "production": [],
    "operations": [],
}


def _artifact(uid, **overrides):
    base = {
        "universal_id": uid,
        "native_id": None,
        "name": f"Artifact {uid}",
        "description": "",
        "category": "REG",
        "volume": "VOL-000",
        "page_start": 1,
        "page_end": 1,
        "status": "ACTIVE",
        "version": "1.0.0",
        "parent": None,
        "dependencies": [],
        "program": "UKB",
        "owner": "UCOS-PROGRAM-CUSTODIAN",
        "tags": ["UKB", "REG"],
        "path": f"00-BOOK/{uid}.md",
        "return_link": "00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md",
        "content_hash": None,
        "traceability": dict(_TRACE_EMPTY),
    }
    base.update(overrides)
    return base


def _edge(edge_id, src, dst, edge_type, inverse_of=None, note="structural:chain"):
    return {
        "edge_id": edge_id,
        "from": src,
        "to": dst,
        "type": edge_type,
        "inverse_of": inverse_of,
        "note": note,
    }


def _volume(vid, serial, name, category, artifact_count, page_start=1, page_end=10):
    return {
        "volume_id": vid,
        "serial": serial,
        "name": name,
        "description": f"Volume {name}.",
        "category": category,
        "status": "ACTIVE",
        "artifact_count": artifact_count,
        "page_range_start": page_start,
        "page_range_end": page_end,
        "index_path": f"00-BOOK/REGISTRIES/VOLUME-REGISTRY.md#{vid.lower()}",
    }


@pytest.fixture
def sample_artifacts():
    """A small, internally-consistent set of artifact records."""
    return [
        _artifact("UCOS-BOOK-000000", name="Root Book", category="BOOK", volume="VOL-000"),
        _artifact(
            "UCOS-REG-000001",
            native_id="REG-001",
            name="Alpha",
            category="REG",
            volume="VOL-000",
            parent="UCOS-BOOK-000000",
            program="UKB",
            status="ACTIVE",
        ),
        _artifact(
            "UCOS-ENG-000001",
            native_id="ENG-001",
            name="Beta",
            category="ENG",
            volume="VOL-003",
            parent="UCOS-BOOK-000000",
            program="ENG",
            status="FROZEN",
            dependencies=["UCOS-REG-000001"],
        ),
    ]


@pytest.fixture
def sample_relationships():
    """Edges over the sample artifacts (Parent/Child + Depends-On)."""
    return [
        _edge("UEDGE-000000001", "UCOS-REG-000001", "UCOS-BOOK-000000", "Parent"),
        _edge("UEDGE-000000002", "UCOS-BOOK-000000", "UCOS-REG-000001", "Child"),
        _edge("UEDGE-000000003", "UCOS-ENG-000001", "UCOS-REG-000001", "Depends-On"),
        _edge("UEDGE-000000004", "UCOS-ENG-000001", "UCOS-BOOK-000000", "Parent"),
    ]


@pytest.fixture
def sample_volumes():
    """Volumes matching the sample artifact placement counts."""
    return [
        _volume("VOL-000", 0, "MASTER INDEX", "IDX", artifact_count=2),
        _volume("VOL-003", 3, "ARCHITECTURE", "ARCH", artifact_count=1),
    ]


@pytest.fixture
def data_dir(tmp_path, sample_artifacts, sample_relationships, sample_volumes) -> Path:
    """Write a complete sample substrate to a temp dir and return its path."""
    (tmp_path / ARTIFACTS_FILE).write_text(
        json.dumps(
            {
                "generated_at": "2026-07-16T00:00:00+00:00",
                "count": len(sample_artifacts),
                "artifacts": sample_artifacts,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / RELATIONSHIPS_FILE).write_text(
        json.dumps({"count": len(sample_relationships), "relationships": sample_relationships}),
        encoding="utf-8",
    )
    (tmp_path / VOLUMES_FILE).write_text(
        json.dumps({"count": len(sample_volumes), "volumes": sample_volumes}),
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def source(data_dir) -> RegistrySource:
    """A RegistrySource over the sample substrate."""
    return RegistrySource(data_dir)


@pytest.fixture
def real_data_dir() -> Path:
    """The real, read-only 00-BOOK/DATA directory (skips if unavailable)."""
    path = default_data_dir()
    if not path.is_dir():
        pytest.skip("00-BOOK/DATA registry substrate not present")
    return path


# --------------------------------------------------------------------------- #
# EPIC-003 (Compiler Core) fixtures — a certified provenance substrate plus    #
# ready-made BP-DATA blueprint documents. Everything lives under tmp_path so    #
# the compiler never touches the read-only corpus (DP-03).                      #
# --------------------------------------------------------------------------- #

from engine.registry.adapter import RegistryAdapter  # noqa: E402

# The six provenance-chain sources a BP-DATA blueprint references (IMP-007 §1).
# These mirror the real, certified 00-BOOK data-family artifacts.
_PROVENANCE_SOURCES = {
    "canonical_source": "UCOS-DAT-000007",
    "reference_architecture": "UCOS-REF-000003",
    "runtime_catalog": "UCOS-CAT-000003",
    "architecture_constitution": "UCOS-DAT-000002",
    "ontology_root": "UCOS-DAT-000004",
    "generation_framework": "UCOS-GEN-000003",
}


@pytest.fixture
def compiler_artifacts():
    """Registered, certified (ACTIVE) provenance sources for BP-DATA compilation.

    Includes one deliberately non-certified artifact (``UCOS-DAT-000099`` in
    IN_PROGRESS) so tests can exercise the 'reject uncertified source' path.
    """
    records = [_artifact("UCOS-BOOK-000000", name="Root Book", category="BOOK", volume="VOL-000")]
    for uid in _PROVENANCE_SOURCES.values():
        records.append(
            _artifact(
                uid,
                name=f"Certified source {uid}",
                category=uid.split("-")[1],
                volume="VOL-006",
                parent="UCOS-BOOK-000000",
                status="ACTIVE",
            )
        )
    records.append(
        _artifact(
            "UCOS-DAT-000099",
            name="Uncertified data source",
            category="DAT",
            volume="VOL-006",
            parent="UCOS-BOOK-000000",
            status="IN_PROGRESS",
        )
    )
    return records


@pytest.fixture
def compiler_data_dir(tmp_path, compiler_artifacts):
    """A registry substrate (artifacts only) sufficient for the compiler."""
    (tmp_path / ARTIFACTS_FILE).write_text(
        json.dumps({"count": len(compiler_artifacts), "artifacts": compiler_artifacts}),
        encoding="utf-8",
    )
    (tmp_path / RELATIONSHIPS_FILE).write_text(
        json.dumps({"count": 0, "relationships": []}), encoding="utf-8"
    )
    (tmp_path / VOLUMES_FILE).write_text(json.dumps({"count": 0, "volumes": []}), encoding="utf-8")
    return tmp_path


@pytest.fixture
def compiler_registry(compiler_data_dir) -> RegistryAdapter:
    """A Registry Adapter over the certified compiler substrate."""
    return RegistryAdapter.open(compiler_data_dir)


@pytest.fixture
def data_blueprint() -> dict:
    """A valid, certified BP-DATA blueprint document (the BP-DATA success case)."""
    return {
        "ir_version": "1.0.0",
        "blueprint_id": "BP-DATA-0001",
        "family": "BP-DATA",
        "name": "Customer",
        "version": "1.0.0",
        "description": "Customer master-data entity.",
        "certification": {"status": "CERTIFIED", "evidence": "UCOS-DAT-000018"},
        "provenance": dict(_PROVENANCE_SOURCES),
        "dependencies": [],
        "entity": {
            "name": "Customer",
            "table": "customer",
            "attributes": [
                {"name": "id", "data_type": "uuid", "nullable": False, "primary_key": True},
                {
                    "name": "email",
                    "data_type": "string",
                    "nullable": False,
                    "unique": True,
                    "max_length": 320,
                },
                {"name": "created_at", "data_type": "timestamp", "nullable": False},
            ],
            "indexes": [{"name": "ix_customer_email", "columns": ["email"], "unique": True}],
            "relationships": [{"name": "orders", "target": "BP-DATA-0002", "kind": "one_to_many"}],
        },
    }


@pytest.fixture
def dependency_blueprint() -> dict:
    """A second BP-DATA blueprint that BP-DATA-0001 can depend on."""
    return {
        "ir_version": "1.0.0",
        "blueprint_id": "BP-DATA-0002",
        "family": "BP-DATA",
        "name": "Order",
        "version": "1.0.0",
        "certification": {"status": "CERTIFIED", "evidence": "UCOS-DAT-000018"},
        "provenance": dict(_PROVENANCE_SOURCES),
        "dependencies": [],
        "entity": {
            "name": "Order",
            "table": "order_line",
            "attributes": [
                {"name": "id", "data_type": "uuid", "nullable": False, "primary_key": True},
                {"name": "total", "data_type": "decimal", "nullable": False},
            ],
        },
    }


# --------------------------------------------------------------------------- #
# EPIC-005 (Runtime Assembly) fixtures — a real published compiler package on   #
# disk plus the signer that produced it, so the runtime engine can be exercised #
# end to end against a genuine EPIC-003 artifact (never the certified corpus).  #
# --------------------------------------------------------------------------- #

from engine.compiler.pipeline import CompilerPipeline  # noqa: E402
from engine.compiler.signing import Signer  # noqa: E402

#: A non-secret, fixed runtime-assembly signing key (a test fixture, never a
#: production credential — production keys remain by-reference via env://).
RUNTIME_SIGNING_KEY = b"ec1-runtime-assembly-test-key"


@pytest.fixture
def runtime_signer() -> Signer:
    """The signer that both signs and verifies the published test package."""
    return Signer(key=RUNTIME_SIGNING_KEY)


@pytest.fixture
def published_package(tmp_path, compiler_registry, data_blueprint, runtime_signer):
    """Compile BP-DATA-0001 through the real pipeline and publish it to disk.

    Returns the :class:`PublishedArtifact` (its ``output_dir`` holds
    ``manifest.json``, ``sbom.json``, ``signature.json``, ``artifact-record.json``
    and ``artifacts/**``) — a genuine EPIC-003 published compiler package.
    """
    output_dir = tmp_path / "published"
    pipeline = CompilerPipeline(compiler_registry, signer=runtime_signer, output_dir=output_dir)
    result = pipeline.compile_one(data_blueprint)
    assert result.success and result.published is not None
    return result.published


@pytest.fixture
def dependency_published_package(tmp_path, compiler_registry, dependency_blueprint, runtime_signer):
    """A second published package (BP-DATA-0002) usable as a dependency closure member."""
    output_dir = tmp_path / "published-dep"
    pipeline = CompilerPipeline(compiler_registry, signer=runtime_signer, output_dir=output_dir)
    result = pipeline.compile_one(dependency_blueprint)
    assert result.success and result.published is not None
    return result.published


# --------------------------------------------------------------------------- #
# EPIC-006 (Universal Runtime Composition) fixtures — a synthetic RuntimeUnit   #
# factory so the composition graph/context/planner/composition/orchestration    #
# layers can be exercised without re-compiling a package for every universe.     #
# (The integration suite still composes *real* assembled units end to end.)      #
# --------------------------------------------------------------------------- #

import hashlib as _hashlib  # noqa: E402

from engine.runtime.assembly import RuntimeUnit  # noqa: E402
from engine.runtime.disclosure import build_disclosure  # noqa: E402


@pytest.fixture
def make_runtime_unit():
    """Return a factory building a minimal, disclosed :class:`RuntimeUnit`.

    The ``package_sha256`` is derived deterministically from the blueprint id, so
    two units with the same id share a hash and two different ids never collide.
    Pass ``disclosure=False`` to build a unit missing the EC-1 disclosure.
    """

    def _make(blueprint_id, *, disclosure=True):
        sha = _hashlib.sha256(blueprint_id.encode()).hexdigest()
        return RuntimeUnit(
            runtime_id=f"UCOS-RUN-{blueprint_id}",
            blueprint_id=blueprint_id,
            artifact_id=f"UCOS-CMP-{blueprint_id}",
            name=blueprint_id,
            version="1.0.0",
            package_sha256=sha,
            provenance_chain=(blueprint_id,),
            signature={"algorithm": "HMAC-SHA256"},
            sbom={"sbom_format": "ucos-sbom/1.0.0", "components": [{"name": "x"}]},
            dependency_closure=(),
            secrets=(),
            resources={},
            descriptor={},
            environment="runtime",
            disclosure=build_disclosure() if disclosure else None,
        )

    return _make


# --------------------------------------------------------------------------- #
# EPIC-RTE-002 (Runtime Execution Platform) fixtures — deterministic           #
# compositions built from synthetic, disclosed RuntimeUnits so the execution   #
# scheduler/coordinator/lifecycle/observability layers can be exercised without #
# re-compiling a package. Executes nothing — a recorded structure only.         #
# --------------------------------------------------------------------------- #

from engine.runtime.composition import Universe, compose  # noqa: E402
from engine.runtime.context import Federation  # noqa: E402


@pytest.fixture
def make_composition(make_runtime_unit):
    """Return a factory for a diamond composition A→{B,C}→D in one context.

    ``coordination`` selects the recorded coordination class. The graph is a
    diamond so concurrent scheduling yields multiple stages and >1 parallelism.
    """

    def _make(coordination="concurrent"):
        a = Universe.of(make_runtime_unit("A"), context_id="ctx1")
        b = Universe.of(make_runtime_unit("B"), context_id="ctx1", depends_on=["A"])
        c = Universe.of(make_runtime_unit("C"), context_id="ctx1", depends_on=["A"])
        d = Universe.of(make_runtime_unit("D"), context_id="ctx1", depends_on=["B", "C"])
        return compose([a, b, c, d], coordination=coordination)

    return _make


@pytest.fixture
def composition(make_composition):
    """A ready-made concurrent diamond composition."""
    return make_composition("concurrent")


@pytest.fixture
def federated_composition(make_runtime_unit):
    """A two-context composition with an explicit cross-context federation.

    ``A`` lives in ``ctx1``; ``B`` lives in ``ctx2`` and depends on ``A`` — a
    cross-context dependency authorised by an explicit federation reference.
    """
    a = Universe.of(make_runtime_unit("A"), context_id="ctx1")
    b = Universe.of(make_runtime_unit("B"), context_id="ctx2", depends_on=["A"])
    return compose([a, b], coordination="sequential", federations=[Federation("B", "A")])


# --------------------------------------------------------------------------------
# Governance engines: one loader, not twenty-one.
#
# The 39 engines under 00-MASTER/ are executable scripts in directories whose names are
# not Python identifiers ("00-MASTER", "UCI-000001"), so no import statement and no
# coverage source can name them. Ω-4 measures the consequence as `unnameable_exemptions`
# and states what closes it: "making those engines importable under test rather than only
# executable as scripts".
#
# Twenty-one test modules had already solved that privately, each with its own copy of the
# same eight lines of importlib. Twenty-one authorings of one mechanism is what UCKP-ART-03
# voids, and it had a practical cost as well as a constitutional one: a new engine test
# started by copying the boilerplate, so the cheapest thing to write was another copy and
# the most expensive was the first shared one.
#
# This is that shared one. It does not make the engines importable by NAME — nothing can,
# short of moving them — but it makes loading one a single call, so the marginal cost of
# testing the 25 engines no test currently reaches is a test rather than a test plus a
# loader.
# --------------------------------------------------------------------------------
import importlib.util as _importlib_util  # noqa: E402
from types import ModuleType as _ModuleType  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GOVERNANCE_ROOT = _REPO_ROOT / "00-MASTER"


def load_governance_engine(program: str, engine: str | None = None) -> _ModuleType:
    """Load ``00-MASTER/<program>/<engine>.py`` as a module, executed in-process.

    ``engine`` defaults to the single ``*_engine.py`` in the program directory, because
    naming it at every call site would be one more thing to keep in step with the tree.

    The module name is suffixed rather than bare: an engine loaded as ``aee_engine`` would
    collide in ``sys.modules`` with any other engine of that stem, and two programs already
    ship a ``closure_engine``. It is deliberately NOT registered in ``sys.modules`` — a test
    that mutates a loaded engine must not leak that into the next test's import.
    """
    directory = _GOVERNANCE_ROOT / program
    if not directory.is_dir():
        raise AssertionError(f"no governance program at 00-MASTER/{program}")
    if engine is None:
        candidates = sorted(directory.glob("*_engine.py"))
        if len(candidates) != 1:
            raise AssertionError(
                f"00-MASTER/{program} holds {len(candidates)} *_engine.py files; name one "
                f"explicitly: {[c.name for c in candidates]}"
            )
        path = candidates[0]
    else:
        path = directory / (engine if engine.endswith(".py") else f"{engine}.py")
    if not path.is_file():
        raise AssertionError(f"no engine at {path.relative_to(_REPO_ROOT)}")
    spec = _importlib_util.spec_from_file_location(f"{program}.{path.stem}_under_test", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"{path.relative_to(_REPO_ROOT)} is not loadable as a module")
    module = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def governance_engine():
    """``governance_engine("UCOS-AEE-001")`` -> the loaded module, cached per session."""
    cache: dict[tuple[str, str | None], _ModuleType] = {}

    def load(program: str, engine: str | None = None) -> _ModuleType:
        key = (program, engine)
        if key not in cache:
            cache[key] = load_governance_engine(program, engine)
        return cache[key]

    return load

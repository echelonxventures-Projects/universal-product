"""UCKP Layer Zero — UGA Existence Projection (Article 8, `existence_resolution`).

Implements the provider `existence_resolution.declared_projections` names: UGA's
already-computed `owner`, `object_class` and `lifecycle` fields, projected into the
`OWNERSHIP`, `IDENTITY` and `LIFECYCLE` facets of a :class:`~engine.uckp.ucko.UCKO`,
one per entry in `00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json`.

No fact is computed here that UGA did not already compute. This module reads UGA's
generated, canonical output — never `uga_engine.py`'s classification functions directly
— because the registry file is the artifact `identity_authority_resolution` and
`existence_resolution` already recognize as UGA's authoritative output, and reading it
is Reuse Before Create; re-deriving classification a second time would not be.

Identity is minted through the namespace `identity_authority_resolution.derivation`
already declares (`ucos-repository`), with the UGA `universal_id` carried through
verbatim as the local name — the exact, already-bound `repository_local_urn` shape
(`engine/uckp/alignment.py`), not a new derivation invented here.

This is a PROJECTION, not a second existence authority: it neither creates a UGA
identifier nor overrides one. If UGA's registry lacks an entry, this provider has
nothing to offer for it; if UGA retires an entry, this provider stops offering it. UGA
remains sole authority over which objects exist; this module only makes what UGA
already knows visible to UCKP's completeness model (Article 6).
"""

from __future__ import annotations

import json
from pathlib import Path

from engine.uckp.alignment import REPOSITORY_NAMESPACE
from engine.uckp.constitution import UNIVERSAL_RUNTIMES, root_law_urn
from engine.uckp.ucko import UCKO

#: The one artifact this provider reads. Never uga_engine.py's classification
#: functions directly — see module docstring.
_UGA_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "00-MASTER"
    / "UCOS-UGA-001"
    / "02-UNIVERSAL-OBJECT-REGISTRY.json"
)

#: What every projected object derives from, in the relationship graph. A bare article
#: id (e.g. "UCKP-ART-08") is text, not a node: engine/uckp/graph.py:80-82 turns
#: `authority.derives_from` into a `-derived-from->` edge against whatever string is
#: given, and engine/uckp/universe.py's require_coherent() then refuses any edge whose
#: target is not itself a minted UCKO — exactly what a bare article id is not. Every
#: existing provider (capabilities.py, constitution.py, alignment.py) derives from a
#: real node's URN, never a law-text citation; root_law_urn() is engine.uckp.constitution's
#: own public function for exactly this, already used the same way by
#: engine/tests/uckp/test_alignment.py. constitution.py mints the Root Law's own UCKO at
#: this URN, and is always among the discovered providers alongside this one, so the
#: edge this creates always resolves.
_DERIVES_FROM = root_law_urn()

#: UGA's two observed lifecycle values (engine/uckp/../uga_engine.py::classify_object)
#: mapped onto the registered uckp.lifecycle-stage vocabulary. Deterministic, total over
#: the two values UGA emits; an unrecognised third value fails closed rather than
#: guessing.
_LIFECYCLE_MAP: dict[str, str] = {
    "AUTHORED": "draft",
    "GENERATED": "implemented",
}

#: UGA's seven object classes (classify_object's closed set) mapped onto the registered
#: uckp.governed-category vocabulary. Deliberately avoids every category the three
#: native providers (alignment.py, capabilities.py, constitution.py) already occupy —
#: confirmed empirically (native population's category histogram: artifact=10,
#: authority=17, capability=10, constraint=17, governance=20, identity=1, law=1,
#: metadata=33, observation=13, principle=20, runtime=10, taxonomy=13, transition=15,
#: validation=13). 'metadata' in particular is a closed, one-per-facet category (33
#: native objects, one per Facet member) — a first attempt at this map used 'metadata'
#: for CONFIGURATION_OBJECT and 'runtime'/'artifact' for others, and
#: test_every_facet_and_every_capability_has_a_canonical_object (which asserts
#: by_category('metadata') == 33 exactly) caught the resulting contamination before
#: this module was ever committed. Every category below is confirmed absent from the
#: native histogram.
_CATEGORY_MAP: dict[str, str] = {
    "CONFIGURATION_OBJECT": "policy",
    "EXECUTABLE_OBJECT": "engine",
    "TEST_OBJECT": "verification",
    "TOOLING_OBJECT": "workflow",
    "DATA_OBJECT": "state",
    "DOCUMENT_ARTIFACT": "knowledge",
    "EXCLUDED_DOCUMENT": "concept",
}

#: Authority tier per object class, same closed set. Advisory for document classes
#: (informative only); engineering for everything else (binding on an implementation).
#: Never 'constitutional' or 'architectural' — this provider makes no such claim.
_TIER_MAP: dict[str, str] = {
    "CONFIGURATION_OBJECT": "engineering",
    "EXECUTABLE_OBJECT": "engineering",
    "TEST_OBJECT": "engineering",
    "TOOLING_OBJECT": "engineering",
    "DATA_OBJECT": "engineering",
    "DOCUMENT_ARTIFACT": "advisory",
    "EXCLUDED_DOCUMENT": "advisory",
}

#: The one knowledge-kind used for every projected object: each is a pointer into an
#: existence fact UGA already holds, not authored institutional knowledge in its own
#: right (contrast engine/knowledge/seed.py's PRINCIPLE/DECISION/RULE entries).
_KIND = "reference"


class UnrecognisedUGAValueError(ValueError):
    """A UGA entry carries a lifecycle or object_class this projection does not map.

    Fails closed rather than guessing: an unmapped value would otherwise either crash
    obscurely inside UCKO.mint's vocabulary checks or, worse, silently coerce to a
    wrong answer.
    """


def _load_entries() -> tuple[dict, ...]:
    """The UGA registry's entries, exactly as UGA wrote them. Read-only."""
    with _UGA_REGISTRY_PATH.open(encoding="utf-8") as handle:
        document = json.load(handle)
    return tuple(document["entries"])


def _project_one(entry: dict) -> UCKO:
    """One UGA entry, projected into a UCKO. Pure: same entry, same object, always."""
    object_class = entry["object_class"]
    lifecycle = entry["lifecycle"]
    if lifecycle not in _LIFECYCLE_MAP:
        raise UnrecognisedUGAValueError(f"{entry['path']}: unmapped UGA lifecycle {lifecycle!r}")
    if object_class not in _CATEGORY_MAP:
        raise UnrecognisedUGAValueError(
            f"{entry['path']}: unmapped UGA object_class {object_class!r}"
        )
    return UCKO.mint(
        namespace=REPOSITORY_NAMESPACE,
        local_name=entry["universal_id"],
        concept=entry["path"],
        definition=(
            f"Repository object at {entry['path']} (class {object_class}), "
            f"tracked by UCOS-UGA-001 as {entry['universal_id']}."
        ),
        kind=_KIND,
        category=_CATEGORY_MAP[object_class],
        authority_tier=_TIER_MAP[object_class],
        derives_from=_DERIVES_FROM,
        owner=entry["owner"],
        lifecycle=_LIFECYCLE_MAP[lifecycle],
        provider="engine.uckp.uga_projection",
        tags=(object_class.lower(),),
        # UCKP-INV-12 (zero-runtime-lock-in) requires every object to bind at least one
        # runtime; mint()'s own default (empty tuple) is facet-present but invariant-
        # violating. Reused verbatim from engine.uckp.constitution, the same universal
        # triple every native UCKP object already binds — not a new runtime declared
        # here.
        runtime_bindings=UNIVERSAL_RUNTIMES,
    )


def ucko_objects() -> tuple[UCKO, ...]:
    """Provider hook (Article 8): the registry discovers these without enumeration.

    Deterministic and total over the UGA registry's own entries at call time: the same
    file always yields the same tuple, in the same order (UGA's own entry order,
    unmodified), with no wall-clock and no randomness anywhere in the path.
    """
    return tuple(_project_one(entry) for entry in _load_entries())


__all__ = ["UnrecognisedUGAValueError", "ucko_objects"]

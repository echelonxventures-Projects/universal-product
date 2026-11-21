"""UCPA-000001 — Universal Constitutional Primitive Alignment.

The root ontology was correct and unenforced. ``ONT-02``, ``ONT-03`` and ``ONT-04``
appeared in no ``.py`` and no ``.json`` file anywhere in the repository: the
constitutional primitives existed only as markdown prose, so no gate measured them, and
the canonical register's own reduction obligation was asserted and never computed. This
package supplies the missing measurement and the missing mapping, and nothing else.

It holds **no authority**. The root ontology is owned by
``01-WORKING/ONTOLOGY-REGISTER.md`` and was ratified by ``UCOS-RAT-001``; this package
reads both and refuses any primitive the register does not already declare. The facet
side of the mapping is imported from :mod:`engine.uckp.facets` rather than restated, so
the mapping cannot drift from the model it maps — it can only fail.

Three parts, in dependency order:

* :mod:`engine.root_ontology.model` — the declaration, rehydrated and refused when
  unusable.
* :mod:`engine.root_ontology.contract` — the measurements, one per declared law.
* :mod:`engine.root_ontology.gate` — the fail-closed gate, OBSERVE MODE, read-only.
"""

from __future__ import annotations

from engine.root_ontology.model import (
    AXIOM,
    LAYER,
    ROLE_AUTHORITY,
    ROLE_SUPERSEDED,
    AlignmentContract,
    AlignmentError,
    Law,
    OntologySource,
    Openness,
    Primitive,
    Projection,
    RatifiedStanding,
    Reduction,
    SelfApplication,
)

__all__ = [
    "AXIOM",
    "LAYER",
    "ROLE_AUTHORITY",
    "ROLE_SUPERSEDED",
    "AlignmentContract",
    "AlignmentError",
    "Law",
    "Openness",
    "OntologySource",
    "Primitive",
    "Projection",
    "RatifiedStanding",
    "Reduction",
    "SelfApplication",
]

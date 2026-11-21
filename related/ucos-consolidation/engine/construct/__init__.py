"""UCON-000001 — the Universal Construct Foundation.

**What this capability adds that no existing owner supplied: a total, traceable disposition for
every presented construct, and a governed home for the unknown, the contradictory and the
undecidable.**

The gap it closes was measurable before it existed. A construct whose classifying kind was
unregistered raised ``MetaTypeUnknownError`` (``engine/kernel/errors.py``) and left no record, so
"we governed a refusal" and "we never saw it" were the same observable state. A contradiction was
a three-string finding recomputed on each run with no identity and no lifecycle
(``engine/knowledge/intelligence.py::ConflictFinding``). An unknown was a coercion-failure
message. A non-closed measurement cell had identity but, by its own docstring, deliberately no
status (``engine/uicm/gap.py::Gap``). The foundational principle — that any presented construct
can be represented, governed, traced, researched and disposed without constitutional redesign —
was therefore true of the DECLARATIONS and false of the RUNTIME.

Eleven parts, in dependency order:

    01  model         the construct entity, and the records that dispose it
    02  declaration   every vocabulary, rehydrated and refused when unusable
    03  reality       reality status, and the conjunction that keeps it honest
    04  disposition   the disposition engine — a total function, or it is not an engine
    05  registry      the append-only store, which has no refusal path
    06  views         the unknown, contradiction, research and discovery registries
    07  extension     self-extension: nine subjects, one mechanism
    08  audit         the extensibility audit — measure first, migrate nothing
    09  contract      the sixteen laws, computed
    10  evidence      a record of a measurement, never Repository Truth
    11  gate          fail-closed, read-only, three-valued

Four design decisions carry the whole thing, and each is enforced structurally rather than by
convention:

**The registry has no refusal path.** Disposition decides what a construct may *do*, never
whether it *exists in the record*. A REJECT is a record naming the rule and rationale that
produced it, so a governed refusal is distinguishable from a silent drop — and law UCON-L-05
compares the presentation count to the population, so a registry that could lose a construct
fails its own arithmetic.

**The catch-all is ESCALATE.** A catch-all of REJECT would discard precisely the constructs the
rule set failed to anticipate — the unforeseen, the future-originated, the currently
unrepresentable — while reporting a clean, fully-covered run. Law UCON-L-03 measures both that the
catch-all assigns the declared disposition and that the disposition forecloses nothing.

**Admission and reality cannot see each other.** ``reality`` does not import ``disposition``,
``disposition`` does not import ``reality``, and law UCON-L-11 parses both to confirm neither ever
will. They meet only as a conjunction — an act is permitted iff the active disposition permits it
AND the active reality state permits it — which is the operational form of *admission does not
imply truth*: ADMIT permits ``certify``, HYPOTHETICAL does not, and no amount of admission changes
that.

**Nine kinds of self-extension take one path.** An ontology, a governance rule, a verifier, a
location axis, a temporal system and an identity namespace are all *constructs*, so there is one
extension mechanism to verify rather than nine. Law UCON-L-09 walks the declared extension points
and performs every admission in memory on every run.

What this capability does NOT claim: the declaration's ``principle.refused_claims`` names each
refused claim explicitly, and this docstring deliberately does not restate them — one list, one
owner. Law UCON-L-13 scans this package's own source for the vocabulary such a guarantee would
need and refuses any undeclared occurrence, so the absence of the claim is a ratchet rather than a
promise. The claims are refused because they are unverifiable, not because they are undesirable.

It is also not a second authority. UMK-000001 owns open-by-registration classification;
UCOS-CEU-001 owns the existence and epistemic vocabularies every reality state binds to;
UCKP-ART-05 owns identity; UCXI-000001 owns context and location axes; CMG-000002 owns temporal
coordinates. Law UCON-L-14 imports the CEU seeds and refuses a binding CEU does not carry, so this
declaration cannot drift into a private copy of somebody else's vocabulary.

AUTHORITY = NONE (DERIVED TRUTH). Stdlib only. No clock is read anywhere except one field of the
evidence payload, which no verdict depends on.
"""

from __future__ import annotations

from engine.construct.declaration import (
    DECLARATION_PATH,
    Declaration,
    DeclarationError,
    load_declaration,
    repo_root,
)
from engine.construct.model import (
    NAMESPACE,
    Construct,
    ConstructError,
    DispositionRecord,
    Evidence,
    Lineage,
    Presentation,
    RealityAssessment,
    construct_id,
)
from engine.construct.registry import ConstructRegistry, JournalEntry, RegistryError

__all__ = [
    "DECLARATION_PATH",
    "NAMESPACE",
    "Construct",
    "ConstructError",
    "ConstructRegistry",
    "Declaration",
    "DeclarationError",
    "DispositionRecord",
    "Evidence",
    "JournalEntry",
    "Lineage",
    "Presentation",
    "RealityAssessment",
    "RegistryError",
    "construct_id",
    "load_declaration",
    "repo_root",
]

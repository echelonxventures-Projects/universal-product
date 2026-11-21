"""UCOS Ω∞ Phase 2 — Universal Governance and Contradiction Architecture.

AUTHORITY = NONE (DERIVED TRUTH). This package issues no certification, seals no governance
artifact, writes no file and modifies no production governance decision. It is an architecture and
its executable proofs.

PHASE 1 REMOVED ARCHITECTURAL ASSUMPTIONS. PHASE 2 REMOVES GOVERNANCE AMBIGUITY. The distinction
is exact: Phase 1 made "what is discoverable" a question rather than a hard-coded answer, and left
every discovered artifact with a governance record that could still be silent. A silent governance
state is one that is neither asserted nor refused — it simply is not there, and nothing can count
it, argue with it or drive it to zero.

    Ω-1 disposition   MEASURED | EXEMPTED | GENERATED | ARCHIVED | TRANSIENT
    Ω-1 authority     "" is legal for TRANSIENT
    UCI verdict       OPEN | CLOSED | FAULT
    certification     certified | not-certified
    governance        governed | not-governed
    compliance        conformant | non-conformant
    freeze            FREEZE | DO-NOT-FREEZE

SEVEN VOCABULARIES, NO TWO OF WHICH SHARE A TYPE, and none of which has a word for "we do not
know". Phase 2's subject is exactly that missing word, and the six axes below are what replace it.

READ IN THIS ORDER — and this index is MEASURED, which it had to become.

    reference/        the open-world core: capabilities, encodings, the fourteen domains and the
                      declared transformations between them. Imports nothing from ``temporal``,
                      which is what makes Time a registered domain rather than the root.
    temporal/         TIME as one of those domains: frames, scales, orderings, the coordinate,
                      clocks as providers and calendars as presentation-only providers.
    state.py          Ω-2.1 + Ω-2.4 + Ω-2.5 — six axes, twenty states, a checkable transition graph
    authority.py      Ω-2.2 — seven tiers, resolution that cannot terminate with NONE

WHAT IS NOT HERE, NAMED SO THE GAP IS COUNTABLE. This index used to list eleven modules and the
tree held two of them: ``clock.py``, ``contradiction.py`` (Ω-2.3), ``certification.py`` (Ω-2.6),
``registry.py`` (Ω-2.7), ``selfverify.py`` (Ω-2.8), ``invariants.py`` (Ω-2.9), ``adapters.py``
(Ω-2.10), ``evidence.py`` and ``__main__.py`` were never written. A reader following the order
reached for files that did not exist, and nothing reported it, because a docstring is prose and
prose is not measured.

The deliverables above remain undelivered and are stated here as an absence rather than removed:
Ω-2.3, Ω-2.6, Ω-2.7, Ω-2.8, Ω-2.9 and Ω-2.10 have no implementation in this package. What changed
is that the claim is now checked — ``engine/tests/omega_governance/test_package_architecture.py``
compares this index against the tree, so the next module to be written must be added here and a
module named here must exist.

THE ONE-SENTENCE THESIS. A governance state is not a scalar; forcing it to be one is what made
MEASURED and GOVERNED the same word, and a system in which those are the same word cannot report
an artifact that is governed and unmeasured, which is the most common artifact there is.
"""

from __future__ import annotations

#: The standing this package holds, as a VALUE rather than only as a sentence in the docstring
#: above. The literal is the token UCOS-UCAF-001 classifies (UCAF-TC-02, "the derived-truth tier
#: records and asserts nothing"): it was `"NONE"`, which said the same thing in a spelling no
#: classification carried, so the authority-realization gate reported a token minted in the
#: executable plane and classified nowhere. Two spellings of one standing is how a vocabulary
#: acquires an unclassifiable member.
AUTHORITY = "NONE (DERIVED TRUTH)"

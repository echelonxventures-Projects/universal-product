"""UCOS Ω∞ Universal Reference Architecture — the open-world core (Deliverables 1 to 4).

AUTHORITY = NONE (DERIVED TRUTH). Registers vocabularies. Certifies nothing, seals nothing, writes
nothing.

THE STARTING ASSUMPTION IS THAT WE FAILED. Ω∞ Rule 8 requires "we removed the hardcoded assumptions"
to be treated as false until measured. Applied to this package's own first draft, it found five:

    json.dumps / hashlib.sha256   Representation and Identity, hardcoded as requirements
    tuple[int, ...]               measurement assumed numeric
    dict[int, str] rule table     keyed 1..7, so an eighth authority tier raised KeyError
    AXES quantified over          a closed list inside a domain model
    default_ordering = TOTAL      a default that privileged one ordering discipline

None of them looked like an enum. That is why Rule 4 says every closed list must be CHALLENGED
rather than every list somebody noticed — the dangerous ones are the ones spelled as ordinary code.

READ IN THIS ORDER.

    capability.py      what a provider or domain may be ASKED. Resolution by capability, never name
    encoding.py        Representation and Identity as provider slots. Two codecs, two digests
    domain.py          ReferenceDomain, Schema, Invariant, Provenance, Value. The fourteen minimums
    transformation.py  declared relationships between domains, and the honest absence of arithmetic

THE DEPENDENCY DIRECTION IS THE NON-PRIVILEGE CLAIM. Nothing in this package imports
``engine.omega_governance.temporal``, so Time is not the root of the architecture; ``temporal``
imports ``reference`` and is one registered domain among fourteen.

THAT IS CHECKABLE RATHER THAN ASSERTED, and for a while it was only asserted. This paragraph used
to name ``openworld.no_domain_is_privileged`` as the check; no ``openworld`` module was ever
written, so the architecture's central claim was carried by a sentence pointing at nothing. It is
measured over the parsed imports of every module in this package by
``engine/tests/omega_governance/test_package_architecture.py``, in both directions — that
``reference`` imports no ``temporal`` module, and that ``temporal`` does import ``reference``, so
two packages that merely never spoke to each other could not pass.
"""

from __future__ import annotations

#: The standing this package holds, as a VALUE rather than only as a sentence in the docstring
#: above. The literal is the token UCOS-UCAF-001 classifies (UCAF-TC-02, "the derived-truth tier
#: records and asserts nothing"): it was `"NONE"`, which said the same thing in a spelling no
#: classification carried, so the authority-realization gate reported a token minted in the
#: executable plane and classified nowhere. Two spellings of one standing is how a vocabulary
#: acquires an unclassifiable member.
AUTHORITY = "NONE (DERIVED TRUTH)"

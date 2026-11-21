"""UCOS Ω∞ — Universal Research Intelligence · UCOS-URI-001.

The additive subsystem that OWNS research intelligence for this repository:

    Research Assimilation → Research Registry → Standards Analysis → Research Validation

It assimilates the repository's own canonical knowledge, decision record, concept
closure and generated corpus measurements into a research corpus of **claims,
findings, contributions and standards records** — and every one of those records
stores a *reference* to canonical content, never a copy of it. The corpus is the
single upstream input from which Publication Intelligence (``intelligence.publication``,
UCOS-UPI-001) generates every publication format.

Constitutional constraints honoured by construction:
  * derive, never fabricate      — every record resolves to a declared substrate
    surface; an unavailable surface yields INDETERMINATE, never an invented value
  * reference, never duplicate   — records carry refs; prose materialises only at
    render time through the Canonical Knowledge Resolver (UCKO-PRIN-0001)
  * deterministic & reproducible — identical repository state ⇒ byte-identical output
  * append-only registration     — Knowledge-Once + tamper-evident hash chain
  * AUTHORITY = NONE (derived truth) — canonical knowledge remains the only authority

Standard library only (TP-04). Writes nothing outside ``intelligence/UCOS-URI-001/``.
"""

from __future__ import annotations

__version__ = "1.0.0"

#: The programme identifier every emitted artifact declares.
PROGRAMME = "UCOS-URI-001"

#: Authority classification of every emitted artifact.
AUTHORITY = "NONE (derived truth)"

__all__ = ["AUTHORITY", "PROGRAMME", "__version__"]

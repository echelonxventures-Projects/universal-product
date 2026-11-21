"""UCOS Ω∞ — shared intelligence kernel for derived-truth subsystems.

The kernel is the **single** home of the primitives that every additive
intelligence subsystem needs and that must never be re-implemented:

  * :mod:`intelligence.kernel.canonical`  — deterministic serialization + sealing
    (re-exported from the existing owner, ``intelligence.rie.canonical``)
  * :mod:`intelligence.kernel.config`     — repository/storage-agnostic config +
    output sinks (re-exported from ``intelligence.rie.config``, plus a nested sink)
  * :mod:`intelligence.kernel.ids`        — deterministic, content-derived identity
    (layered on the registered owner, ``engine.registry.universal.identity``)
  * :mod:`intelligence.kernel.substrate`  — declaration-driven, read-only access to
    Repository Truth, with availability + content fingerprints
  * :mod:`intelligence.kernel.knowledge`  — the Canonical Knowledge Resolver: the
    ONLY route by which canonical content may enter a derived artifact
  * :mod:`intelligence.kernel.ledger`     — an append-only, content-addressed,
    Knowledge-Once, hash-chained registry ledger

Reuse-before-create is enforced by construction: where a primitive already has a
canonical owner in this repository the kernel *re-exports* it rather than writing
a second copy (the Knowledge Once Principle, UCKO-PRIN-0001; the duplication
anti-pattern, UCKO-ANTI-0001).

AUTHORITY = NONE (derived truth). Standard library only (TP-04).
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = ["__version__"]

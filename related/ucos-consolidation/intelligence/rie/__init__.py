"""UCOS Ω∞ — Repository Intelligence Engine (RIE) · UCOS-RIE-001.

An ADDITIVE, AI-agnostic, repository-agnostic, storage-agnostic intelligence
subsystem that continuously DERIVES repository knowledge from repository
evidence. It is the authoritative *producer* of the repository intelligence
outputs (the Repository Implementation Baseline / UCOS-IMP-BASELINE-001 is one
of its generated outputs), but it holds **no authority of its own**:

    Repository evidence remains the only authority. AUTHORITY = NONE (derived truth).

Constitutional constraints honored by construction:
  * derive, never hardcode      — every metric is read/computed from evidence
  * compose, never duplicate    — reads existing generated evidence (00-BOOK/DATA,
                                  coverage.xml, git); creates no second source of truth
  * AI/repository/storage-agnostic — no vendor API; repo root auto-resolved; output
                                  emitted through a pluggable sink
  * deterministic & reproducible — identical repository state ⇒ byte-identical output
  * autonomous                  — runnable head-less via CLI or hook
  * never modifies engine/**, platform/**, 99-FREEZE/**, 00-SOURCE/**, or 00-BOOK/**

Runtime code is Python standard library only (TP-04 vendor-neutral core).
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = ["__version__"]

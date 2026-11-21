"""ZG-P-02 — Coverage bootstrap (Universe→Code Coverage Instrument).

Composes the coverage instrument over the **real repository** evidence source and
returns a ready :class:`~platform.coverage.service.CoverageService`. This is the default
production wiring used to recompute Universe→Code coverage on demand (e.g. after each
commit, mirroring the REG-AUTO-001 / TRACK-001 recompute discipline). It creates no
authority and no alternate registry; it reads authoritative repository evidence only.
"""

from __future__ import annotations

from pathlib import Path
from platform.coverage.repository import RepositoryEvidenceSource
from platform.coverage.service import CoverageService, build_coverage_service


def bootstrap_coverage(repo_root: Path | str | None = None) -> CoverageService:
    """Build the coverage service over the repository evidence source (default wiring)."""
    return build_coverage_service(RepositoryEvidenceSource(repo_root))


__all__ = ["bootstrap_coverage"]

"""EPIC-PLAT-003 — Coverage report ingestion (Terminal T5).

Coverage Reports are produced by the **canonical coverage tool** (``verify.sh`` runs
``pytest --cov ... --cov-report=xml`` and ``coverage report``). This module does not
re-measure coverage — it *reuses* the Cobertura ``coverage.xml`` the canonical tool
already emitted, projecting it into an immutable, deterministic
:class:`~platform.repository_operations.contracts.CoverageSummary`.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET  # noqa: S405 - trusted, locally-produced coverage.xml
from pathlib import Path
from platform.repository_operations.contracts import CoverageSummary
from platform.repository_operations.errors import CoverageReportError


def parse_coverage_xml(text: str) -> CoverageSummary:
    """Parse a Cobertura coverage XML document into a :class:`CoverageSummary`.

    Raises:
        CoverageReportError: if the document is not well-formed or is not a Cobertura
            ``<coverage>`` report.
    """
    try:
        root = ET.fromstring(text)  # noqa: S314 - trusted, locally-produced coverage.xml
    except ET.ParseError as exc:
        raise CoverageReportError(
            "coverage report is not well-formed XML", detail=str(exc)
        ) from exc

    if root.tag != "coverage":
        raise CoverageReportError("not a Cobertura coverage report", root=root.tag)

    def _float(attr: str) -> float:
        try:
            return float(root.get(attr, "0") or "0")
        except ValueError as exc:
            raise CoverageReportError(
                "coverage attribute is not numeric", attribute=attr, value=root.get(attr)
            ) from exc

    def _int(attr: str) -> int:
        try:
            return int(root.get(attr, "0") or "0")
        except ValueError as exc:
            raise CoverageReportError(
                "coverage attribute is not an integer", attribute=attr, value=root.get(attr)
            ) from exc

    return CoverageSummary(
        line_rate=_float("line-rate"),
        branch_rate=_float("branch-rate"),
        lines_covered=_int("lines-covered"),
        lines_valid=_int("lines-valid"),
        branches_covered=_int("branches-covered"),
        branches_valid=_int("branches-valid"),
    )


def load_coverage_summary(path: str | Path) -> CoverageSummary:
    """Load and parse a coverage report from ``path``.

    Raises:
        CoverageReportError: if the file cannot be read (a *missing* file is a caller
            concern, checked before invoking this) or cannot be parsed.
    """
    report_path = Path(path)
    try:
        text = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CoverageReportError(
            "coverage report could not be read", path=str(report_path), detail=str(exc)
        ) from exc
    return parse_coverage_xml(text)


__all__ = ["parse_coverage_xml", "load_coverage_summary"]

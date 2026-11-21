"""EPIC-PLAT-003 — Coverage report ingestion tests (Terminal T5)."""

from __future__ import annotations

from platform.repository_operations.coverage import load_coverage_summary, parse_coverage_xml
from platform.repository_operations.errors import CoverageReportError
from platform.tests.repository_operations_helpers import COVERAGE_XML_FULL

import pytest


def test_parse_coverage_xml_full():
    summary = parse_coverage_xml(COVERAGE_XML_FULL)
    assert summary.line_percent == 100.0
    assert summary.branch_percent == 100.0
    assert summary.lines_covered == 10
    assert summary.branches_valid == 4


def test_parse_coverage_xml_not_well_formed():
    with pytest.raises(CoverageReportError):
        parse_coverage_xml("<coverage ")


def test_parse_coverage_xml_wrong_root():
    with pytest.raises(CoverageReportError):
        parse_coverage_xml("<report line-rate='1.0'></report>")


def test_parse_coverage_xml_non_numeric_float():
    with pytest.raises(CoverageReportError):
        parse_coverage_xml('<coverage line-rate="abc"></coverage>')


def test_parse_coverage_xml_non_integer():
    with pytest.raises(CoverageReportError):
        parse_coverage_xml('<coverage line-rate="1.0" lines-covered="x"></coverage>')


def test_load_coverage_summary_reads_file(tmp_path):
    path = tmp_path / "coverage.xml"
    path.write_text(COVERAGE_XML_FULL, encoding="utf-8")
    summary = load_coverage_summary(path)
    assert summary.line_percent == 100.0


def test_load_coverage_summary_read_error(tmp_path):
    # A directory cannot be read as a file → OSError → CoverageReportError.
    with pytest.raises(CoverageReportError):
        load_coverage_summary(tmp_path)

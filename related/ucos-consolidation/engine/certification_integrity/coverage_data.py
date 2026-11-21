"""UCI-000001 Part 2 — reading a coverage measurement without trusting its summary.

WHY THIS READS LINES AND NOT PERCENTAGES.

``coverage.xml`` carries a ``line-rate`` attribute on every element, and using it would make
this package's figures a restatement of coverage.py's arithmetic rather than an independent
computation over the same evidence. The distinction is what makes Rules 10 and 11 provable:
"combined shards == single full execution" is NOT provable from two percentages, because two
different covered-line SETS routinely produce the same ratio. Only the sets can be compared, so
only the sets are read.

The parser therefore takes exactly one thing from the XML — per file, which line numbers were
hit and which were not — and derives every total itself.
"""

from __future__ import annotations

import hashlib
import json
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from engine.certification_integrity.model import IntegrityError

#: Prefix for a file whose identity the coverage document does not determine. Marked rather than
#: guessed; see ``_relative``.
AMBIGUOUS_PREFIX = "?ambiguous:"


@dataclass(frozen=True)
class FileCoverage:
    """The measured line status of one file. ``hit``/``missed`` are disjoint by construction."""

    path: str
    hit: frozenset[int]
    missed: frozenset[int]

    @property
    def statements(self) -> int:
        return len(self.hit) + len(self.missed)

    @property
    def percent(self) -> float:
        total = self.statements
        return 100.0 if total == 0 else round(len(self.hit) * 100.0 / total, 4)


@dataclass(frozen=True)
class CoverageReport:
    """A whole coverage measurement, keyed by repository-relative path."""

    files: dict[str, FileCoverage]
    #: Branch totals are carried through for provenance and compared by Rule 11. They are not
    #: used in the line-equality proof: a line-set comparison already detects every difference a
    #: branch comparison would, and reporting both keeps the stronger claim checkable.
    branches_valid: int
    branches_covered: int
    #: The totals the document DECLARES in its root element, as distinct from the totals its body
    #: contains. Kept separately and compared, because they can disagree — see
    #: ``body_is_incomplete``.
    declared_statements: int = 0
    declared_covered: int = 0

    @property
    def statements(self) -> int:
        return sum(f.statements for f in self.files.values())

    @property
    def covered(self) -> int:
        return sum(len(f.hit) for f in self.files.values())

    @property
    def missing(self) -> int:
        return sum(len(f.missed) for f in self.files.values())

    @property
    def percent(self) -> float:
        return 100.0 if self.statements == 0 else round(self.covered * 100.0 / self.statements, 4)

    @property
    def body_is_incomplete(self) -> bool:
        """True when the document's root totals exceed the totals its own body contains.

        THIS IS A REAL, MEASURED DEFECT IN ``coverage xml``, not a defensive check.

        Measured on this repository's own certification artifact at 78b62b30:

            coverage report (terminal)  1,259 files   125,217 statements   96%
            coverage.xml root element                 125,217 statements
            coverage.xml body             644 files    67,279 statements

        57,938 statements — 46% of the measurement — are absent from the body while the header
        continues to claim them. The cause is ``source`` naming 78 roots while sibling layers
        share module basenames: ``coverage xml`` emits one ``<class filename=...>`` per distinct
        RELATIVE name, so ``data/governance.py`` and ``application/governance.py`` reduce to one
        ``governance.py`` and the loser is dropped from the body entirely.

        The percentage is unaffected, which is exactly what makes it dangerous: every summary
        agrees, and only a consumer that reads per-file data sees 644 files where there are 1,259.
        ``.github/workflows/ec1-ci.yml`` uploads this file as the ``coverage-xml`` artifact, so any
        dashboard, IDE gutter or external quality gate reading it is reading half the repository
        with no indication that the other half exists. Absence renders as nothing, not as zero.
        """
        return self.declared_statements > self.statements

    @property
    def missing_from_body(self) -> int:
        return max(0, self.declared_statements - self.statements)

    @property
    def ambiguous_files(self) -> tuple[str, ...]:
        """Files the document could not identify. A non-empty tuple is a defect in the PRODUCER.

        Reported rather than raised, because the totals are still correct and refusing the whole
        measurement over a rendering defect would discard good data. The gate surfaces the count.
        """
        return tuple(sorted(p for p in self.files if p.startswith(AMBIGUOUS_PREFIX)))

    @property
    def branch_percent(self) -> float | None:
        if not self.branches_valid:
            return None
        return round(self.branches_covered * 100.0 / self.branches_valid, 4)

    def line_signature(self) -> dict[str, tuple[int, ...]]:
        """The exact covered-line set per file, which is what Rules 8, 10 and 11 compare.

        Sorted tuples rather than sets so the structure is directly comparable and directly
        serialisable; a set's iteration order would make an equal signature print differently on
        two runs and invite a false drift finding.
        """
        return {path: tuple(sorted(f.hit)) for path, f in sorted(self.files.items())}

    def digest(self) -> str:
        """A content hash of the whole measurement, for the provenance record.

        Includes the MISSED lines as well as the hit ones, so that a run which stopped measuring
        a file entirely produces a different digest from one that measured it and found it
        uncovered. Those are the two failures Rule 11 separates, and a hit-only digest would
        make them identical.
        """
        payload = {
            path: {"hit": sorted(f.hit), "missed": sorted(f.missed)}
            for path, f in sorted(self.files.items())
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


def parse(xml_path: str, *, repository: str | None = None) -> CoverageReport:
    """Read ``coverage.xml`` into per-file line sets.

    Paths are normalised to repository-relative POSIX form. coverage.py writes ``filename``
    relative to a ``<sources>`` root and that root is an absolute machine path, so leaving it
    unresolved would make two runs in two directories produce incomparable reports — and the
    immutable-extraction run of Rule 7 runs in a temporary directory by construction, so every
    comparison it feeds would report drift that is really only a working directory.
    """
    if not os.path.exists(xml_path):
        raise IntegrityError(
            f"no coverage measurement at {xml_path} — refusing to report a coverage figure over "
            "a measurement that was never taken"
        )
    try:
        # noqa justification: the input is this repository's own coverage.xml, written by
        # coverage.py in the same run. defusedxml is not a declared dependency and adding one to
        # parse a file we produced ourselves would widen the dependency surface, not narrow risk.
        root = ET.parse(xml_path).getroot()  # noqa: S314
    except ET.ParseError as exc:
        raise IntegrityError(f"{xml_path} is not parseable coverage XML: {exc}") from exc

    repo = os.path.realpath(repository or os.getcwd())
    sources = [s.text for s in root.findall("./sources/source") if s.text]

    files: dict[str, FileCoverage] = {}
    # Iterate packages rather than classes directly, because the enclosing <package name="...">
    # is what disambiguates a filename. With more than one <source> root -- which is the normal
    # case after `coverage combine`, since the config names 74 -- a bare `governance.py` exists
    # under several roots and resolving it by "first root where the file exists" silently picks
    # the wrong one.
    #
    # Measured: this reader's own Rule 10 check caught it. combine(4 shards) compared against one
    # whole run reported 19 files present in one and absent in the other, while statements
    # (7,536), covered (7,347), branch totals and every per-file line set were identical. The
    # coverage data agreed exactly; 19 files had been filed under `application/` instead of
    # `data/`. A percentage comparison would have passed, and a file-set comparison reported a
    # shard-combination defect that did not exist.
    for package in root.findall(".//package"):
        hint = (package.get("name") or "").replace(".", "/")
        for element in package.findall(".//class"):
            filename = element.get("filename")
            if not filename:
                continue
            relative = _relative(filename, sources, repo, hint=hint)
            hit: set[int] = set()
            missed: set[int] = set()
            for line in element.findall("./lines/line"):
                number = line.get("number")
                if number is None:
                    continue
                (hit if line.get("hits") not in (None, "0") else missed).add(int(number))
            # A path can appear more than once when it is measured under two source roots.
            # Merging by union rather than overwriting keeps a re-measured file from LOSING hits,
            # which would understate coverage and manufacture a drift finding.
            if relative in files:
                previous = files[relative]
                hit |= previous.hit
                missed |= previous.missed
            files[relative] = FileCoverage(relative, frozenset(hit), frozenset(missed - hit))

    if not files:
        raise IntegrityError(
            f"{xml_path} names no measured file — a coverage report over nothing would report "
            "100% forever, so it is refused rather than summarised"
        )

    return CoverageReport(
        files=files,
        branches_valid=int(root.get("branches-valid") or 0),
        branches_covered=int(root.get("branches-covered") or 0),
        declared_statements=int(root.get("lines-valid") or 0),
        declared_covered=int(root.get("lines-covered") or 0),
    )


def _relative(filename: str, sources: list[str], repo: str, *, hint: str = "") -> str:
    """Resolve a coverage ``filename`` to a repository-relative POSIX path.

    REFUSES TO GUESS WHEN THE DOCUMENT IS AMBIGUOUS, and that refusal is a measured finding
    rather than caution.

    ``coverage xml`` writes ``filename`` with the longest matching ``<source>`` prefix stripped.
    With one source root that is unambiguous. With 78 -- which is what this repository's declared
    scope produces -- a bare ``governance.py`` exists under four roots, and coverage.py has
    discarded the information needed to say which. Measured on a two-layer run: the ``.coverage``
    data holds 140 distinct measured files and the rendered XML holds 121 ``<class>`` entries. The
    totals agree exactly (15,178 statements both ways), so no percentage reveals it; 19 files'
    line data is filed under another file's name.

    Guessing "the first root where a file of this name exists" is what this function did first,
    and it produced a false Rule 10 finding: combine(4 shards) versus one whole run reported 19
    files present in one and absent in the other, with every per-file line set identical. The
    coverage was right and the reader was wrong.

    So an ambiguous name resolves to a STABLE, MARKED key. Stable, so two runs of one state still
    compare equal and no false drift is manufactured; marked, so the ambiguity is visible in the
    report instead of being silently attributed to one of the candidates.
    """
    if os.path.isabs(filename):
        resolved = os.path.realpath(filename)
        if resolved.startswith(repo + os.sep):
            return os.path.relpath(resolved, repo).replace(os.sep, "/")
        return filename.replace(os.sep, "/")

    matches = []
    for source in sources:
        candidate = os.path.realpath(os.path.join(source, filename))
        if candidate.startswith(repo + os.sep) and os.path.exists(candidate):
            matches.append(os.path.relpath(candidate, repo).replace(os.sep, "/"))
    unique = sorted(set(matches))

    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        if hint:
            preferred = [m for m in unique if m == f"{hint}/{filename}" or m.startswith(hint + "/")]
            if len(preferred) == 1:
                return preferred[0]
        return f"{AMBIGUOUS_PREFIX}{filename}"  # caller de-duplicates; see parse()

    direct = os.path.realpath(os.path.join(repo, filename))
    if direct.startswith(repo + os.sep) and os.path.exists(direct):
        return os.path.relpath(direct, repo).replace(os.sep, "/")
    # Unresolvable: keep the declared name rather than inventing one. A wrong-but-stable key is
    # comparable across runs; a synthesised key is not.
    return filename.replace(os.sep, "/")


def compare(left: CoverageReport, right: CoverageReport) -> dict[str, object]:
    """Diff two measurements at line-set granularity.

    Returns a structure that is empty exactly when the two measurements are identical. This is
    the primitive behind Rule 8 (A == B == C), Rule 10 (shards versus whole) and Rule 11 (two
    independent runs), and it is deliberately the SAME primitive: those rules ask one question
    about three pairs of inputs, and implementing it three times would let the answers diverge.
    """
    left_sig, right_sig = left.line_signature(), right.line_signature()
    only_left = sorted(set(left_sig) - set(right_sig))
    only_right = sorted(set(right_sig) - set(left_sig))
    differing: dict[str, dict[str, list[int]]] = {}
    for path in sorted(set(left_sig) & set(right_sig)):
        a, b = set(left_sig[path]), set(right_sig[path])
        if a != b:
            differing[path] = {
                "covered_only_in_first": sorted(a - b),
                "covered_only_in_second": sorted(b - a),
            }
    return {
        "identical": not (only_left or only_right or differing),
        "files_only_in_first": only_left,
        "files_only_in_second": only_right,
        "files_with_differing_lines": differing,
        "statement_delta": right.statements - left.statements,
        "branch_delta": right.branches_valid - left.branches_valid,
        "first": {
            "statements": left.statements,
            "covered": left.covered,
            "percent": left.percent,
            "branches_valid": left.branches_valid,
            "digest": left.digest(),
        },
        "second": {
            "statements": right.statements,
            "covered": right.covered,
            "percent": right.percent,
            "branches_valid": right.branches_valid,
            "digest": right.digest(),
        },
    }

"""Evidence readers — the only inputs the engine trusts.

Every fact the engine reports is read here from repository evidence that other
certified/authoritative producers already emit:

  * ``00-BOOK/DATA/*.json``   — ukb.py / ukbx.py generated corpus intelligence
  * ``git``                   — the version-control eligibility boundary + HEAD

``coverage.xml`` is read too, but is deliberately NOT in that list: it is
TEST_EXECUTION_STATE, not repository evidence. Nothing reachable from
:func:`intelligence.rie.engine.build_model` may consume it (UCOS-CL-005), and it
is parsed through the repository's canonical Cobertura reader rather than here
(UCOS-CL-007). See :meth:`EvidenceReader.coverage`.

The reader NEVER writes any of these; it composes them (compose-never-duplicate).
Absent evidence is reported as ``available=False`` and degrades gracefully to a
fail-closed ``INDETERMINATE`` rather than an invented value.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from platform.repository_operations.coverage import load_coverage_summary
from platform.repository_operations.errors import CoverageReportError
from typing import Any

from . import __version__
from .canonical import canonical_json, sha256_file, sha256_text
from .config import RepoConfig

_DATA_FILES = (
    "control-tower.json",
    "artifacts.json",
    "certification.json",
    "twin.json",
    "volumes.json",
)


@dataclass(frozen=True)
class Coverage:
    available: bool
    line_pct: float
    branch_pct: float
    lines_covered: int
    lines_valid: int


class EvidenceReader:
    """Reads (never writes) the repository evidence surfaces."""

    def __init__(self, config: RepoConfig) -> None:
        self.config = config
        self._cache: dict[str, Any] = {}

    # -- corpus DATA -----------------------------------------------------
    def data(self, name: str) -> dict[str, Any]:
        if name not in self._cache:
            path = self.config.data_file(name)
            self._cache[name] = (
                json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
            )
        return self._cache[name]

    def control_tower(self) -> dict[str, Any]:
        return self.data("control-tower.json")

    def artifacts(self) -> dict[str, Any]:
        return self.data("artifacts.json")

    def certification(self) -> dict[str, Any]:
        return self.data("certification.json")

    def twin(self) -> dict[str, Any]:
        return self.data("twin.json")

    # -- coverage --------------------------------------------------------
    def coverage(self) -> Coverage:
        """Coverage measurement for NON-canonical surfaces only.

        UCOS-CL-005 — nothing reachable from :func:`intelligence.rie.engine.build_model`
        may call this. ``coverage.xml`` is TEST_EXECUTION_STATE: gitignored, produced by
        the test runner, and absent from every pristine clone, so a canonical artifact
        that reads it cannot reproduce itself from the same commit. The remaining callers
        (portal, knowledge store, research corpus) all emit to ignored or untracked paths
        where an environmental measurement is legitimate and expected.

        UCOS-CL-007 — the Cobertura document is parsed by the repository's canonical
        reader, ``platform.repository_operations.coverage``, rather than by a private
        ``ElementTree`` walk here. That module already exists to reuse "the coverage.xml
        the canonical tool already emitted"; re-implementing it was a second answer to a
        question the repository had answered once.
        """
        path = self.config.coverage_xml
        if not path.exists():
            return Coverage(False, 0.0, 0.0, 0, 0)
        try:
            summary = load_coverage_summary(path)
        except CoverageReportError:
            # Fail closed to "unavailable" rather than propagating: an unreadable
            # environmental artifact must degrade an observational surface, never abort
            # a caller that is not asking about coverage.
            return Coverage(False, 0.0, 0.0, 0, 0)
        return Coverage(
            True,
            round(summary.line_rate * 100, 2),
            round(summary.branch_rate * 100, 2),
            summary.lines_covered,
            summary.lines_valid,
        )

    # -- git -------------------------------------------------------------
    def head(self) -> str:
        return self._git("rev-parse", "--short", "HEAD") or "UNKNOWN"

    def head_commit(self) -> str:
        """The full source commit the outputs are derived at."""
        return self._git("rev-parse", "HEAD") or "UNKNOWN"

    def head_committed_at(self) -> str:
        """HEAD's committer date, strict ISO-8601.

        Generation time is taken from the source commit, never from the wall
        clock: the mandated generation timestamp must not make a regeneration of
        an unchanged repository produce different bytes.
        """
        return self._git("show", "-s", "--format=%cI", "HEAD") or "UNKNOWN"

    def branch(self) -> str:
        return self._git("rev-parse", "--abbrev-ref", "HEAD") or "UNKNOWN"

    def tracked(self, pattern: str) -> list[str]:
        """Tracked paths matching *pattern*, NUL-delimited so non-ASCII names survive.

        Without ``-z``, git renders any path containing a non-ASCII byte in
        double-quoted, octal-escaped form (``"…/UCOS-\\316\\251\\342\\210\\236-…"``).
        That literal string does not resolve on disk, so such a path is silently
        unreadable — the eligibility boundary would omit tracked artifacts that
        demonstrably exist. ``-z`` is what ``00-BOOK/tools/ukb.py::_git_ls`` already
        uses, so discovery measures the same boundary registration does.
        """
        out = self._git("ls-files", "-z", pattern)
        return sorted(entry for entry in out.split("\0") if entry) if out else []

    def _git(self, *args: str) -> str:
        try:
            res = subprocess.run(  # noqa: S603
                ["git", *args],  # noqa: S607 - fixed argv, no shell
                cwd=self.config.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return ""
        return res.stdout.strip() if res.returncode == 0 else ""

    # -- determinism fingerprint ----------------------------------------
    def state_fingerprint(self) -> dict[str, Any]:
        """A content fingerprint of all evidence inputs that determine canonical output identity.

        Identical repository state ⇒ identical fingerprint ⇒ identical outputs.

        Repository Fixed-Point Closure (UCOS-RFP-001 RFP-2) — the commit identity
        and branch are excluded (they made every output non-convergent by construction).

        Constitutional classification of inputs (UCOS-UCL-LIFECYCLE):

        ``evidence_files`` (00-BOOK/DATA/*.json) — TRACKED_SOURCE: git-versioned artifacts
        produced by the canonical generation chain (ukb/ukbx). These are the canonical
        identity-determining inputs.

        ``coverage.xml`` — TEST_EXECUTION_STATE / QUALITY_MEASUREMENT: a generated artifact
        produced by the test runner outside the canonical RIB→AEE→RIE chain. It is
        environmental state, not repository truth. Including it in the identity fingerprint
        violates the universal input closure contract: a pristine clone lacks coverage.xml
        because the bootstrap does not run the test suite, so every clone regeneration
        produces a different ``input_hash`` and therefore a different catalog SHA256, causing
        irreproducible ``registry_variance``, ``ordering_variance`` and ``certification_variance``
        in Phase-9 pristine-clone certification.

        Fix, in two parts. UCOS-P0-FCL-002-FIX-001 removed coverage from this fingerprint,
        which made ``input_hash`` deterministic. UCOS-CL-005 completed it: coverage was still
        reaching canonical bytes through ``analysis.py`` (``coverage_line_pct``,
        ``coverage_branch_pct``, ``coverage_full``, and a progress reconciliation branch), so
        the model digest still moved with ``coverage.xml`` while the fingerprint did not. Both
        routes are now closed, and the whole class is held shut by a boundary test asserting
        the serialized model is byte-identical with and without ``coverage.xml``.
        """
        files = {
            self.config.rel(self.config.data_file(n)): sha256_file(self.config.data_file(n))
            for n in _DATA_FILES
        }
        return {
            "evidence_files": files,
            # coverage_measurement is intentionally absent from this fingerprint.
            # See docstring — it is TEST_EXECUTION_STATE and must not influence canonical
            # artifact identity, and under UCOS-CL-005 no canonical surface reads it at all.
        }

    # UCOS-CL-007: coverage_enrichment() removed. It was added at be46a300 to hold the
    # coverage measurement that state_fingerprint() had just given up, but nothing ever
    # consumed it — its only caller was its own test. It also duplicated a capability the
    # repository already owns: platform/repository_operations/coverage.py parses Cobertura
    # into a CoverageSummary and documents itself as reusing "the canonical coverage.xml",
    # and platform/measurement/contracts.py owns the Measurement abstraction. Adding a
    # third parser here would have violated Knowledge Once for a value no producer read.

    # -- generation provenance ------------------------------------------
    def generation_state(self) -> dict[str, Any]:
        """The provenance block every generated artefact carries.

        Records the generator, the input hash and where the output hash lives.
        Every field is derived from tracked repository content, so regenerating
        over an unchanged tree reproduces the same bytes — provenance that cannot
        be reproduced is not provenance.

        The source commit, the repository head and the generation timestamp taken
        from the commit's committer date are deliberately ABSENT (UCOS-RFP-001
        RFP-2). Version control already records which commit contains these
        artifacts; restating it inside them duplicated that state and made the
        artifacts unable to reproduce themselves, which is the defect class
        UCOS-RFP-001 abolishes.
        """
        if "generation_state" not in self._cache:
            fingerprint = self.state_fingerprint()
            self._cache["generation_state"] = {
                "generator": "UCOS-RIE-001 Repository Intelligence Engine",
                "generator_version": __version__,
                "anchor": (
                    "the containing commit — owned by version control, never restated here "
                    "(UCOS-RFP-001 RFP-2)"
                ),
                "input_hash": sha256_text(canonical_json(fingerprint)),
                "input_hash_basis": (
                    "sha256 over the canonical evidence fingerprint — every 00-BOOK/DATA evidence "
                    "file hash, which together pin the tracked state these outputs derive from. "
                    "Coverage measurement (TEST_EXECUTION_STATE) is excluded per "
                    "UCOS-P0-FCL-002-FIX-001 — it is not canonical identity input."
                ),
                "output_hash_field": "content_hash",
            }
        return dict(self._cache["generation_state"])

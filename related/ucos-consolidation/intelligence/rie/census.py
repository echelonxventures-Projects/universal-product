"""Code census — derive source/test metrics from the code substrate.

Uses the version-control eligibility boundary (``git ls-files``) to match the
repository doctrine that git-tracked files define the corpus, with a filesystem
fallback so the engine remains usable in a non-git checkout (repository-agnostic).
All results are sorted/deterministic.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .evidence import EvidenceReader

_TEST_DEF = re.compile(r"^\s*def test_", re.MULTILINE)


@dataclass(frozen=True)
class RootCensus:
    root: str
    source_files: int
    loc: int
    test_files: int
    test_functions: int

    def as_dict(self) -> dict[str, int | str]:
        return asdict(self)


def _iter_py(reader: EvidenceReader, root: str) -> list[Path]:
    """Tracked *.py files under ``root`` (git), else filesystem walk."""
    tracked = reader.tracked(f"{root}/*.py")
    base = reader.config.repo_root
    if tracked:
        return [base / p for p in tracked]
    # Fallback: deterministic filesystem walk.
    return sorted(p for p in (base / root).rglob("*.py") if "__pycache__" not in p.parts)


def census_for(reader: EvidenceReader, root: str) -> RootCensus:
    files = _iter_py(reader, root)
    src = [p for p in files if "tests" not in p.relative_to(reader.config.repo_root).parts]
    tests = [p for p in files if "tests" in p.relative_to(reader.config.repo_root).parts]
    loc = 0
    for p in src:
        try:
            loc += sum(1 for _ in p.read_text(encoding="utf-8", errors="ignore").splitlines())
        except OSError:
            continue
    test_fns = 0
    for p in tests:
        try:
            test_fns += len(_TEST_DEF.findall(p.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return RootCensus(
        root=root,
        source_files=len(src),
        loc=loc,
        test_files=len(tests),
        test_functions=test_fns,
    )


def full_census(reader: EvidenceReader) -> dict[str, RootCensus]:
    return {root: census_for(reader, root) for root in reader.config.code_roots}

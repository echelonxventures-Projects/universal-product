"""Capability discovery — enumerate realized capabilities from the substrate.

Discovery is genuine, not hardcoded. The unit universe is derived from the
version-control eligibility boundary (``git ls-files``), which is the same
Repository Truth the Repository Integration Blueprint discovers over:

  * every tracked ``<root>/__init__.py``   — a code root
  * every tracked ``<root>/<pkg>/__init__.py`` — a package inside a code root

The first line of each package docstring is read as its description and metrics
are derived from the census. Discovery also records the automation tools,
operational memory (MCS), corpus, and the orchestration specifications
(CIOA/CCE) whose presence-without-code marks them PLANNED.

Nothing is filtered out on aesthetic grounds. A test package is a tracked
implementation unit and is catalogued as one; excluding it created a permanent,
uncloseable capability-coverage gap against the repository's own inventory.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path

from .evidence import EvidenceReader
from .knowledge import policy_for


@dataclass(frozen=True)
class Capability:
    unique_id: str
    canonical_name: str
    canonical_location: str
    category: str
    authority: str
    reuse: str
    replacement_prohibited: bool
    implementation_status: str
    description: str
    evidence_present: bool
    summary: str = ""
    symbols: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


#: Characters of leading docstring prose retained as a capability's ``summary``.
#: Bounded so the catalogue stays a catalogue, but long enough to carry the domain
#: vocabulary that identifies *what the capability is for* — which is what makes the
#: catalogue answerable to "does this already exist?" rather than merely enumerable.
_SUMMARY_CHARS = 2500

#: Maximum public symbol names recorded per capability, sorted for determinism.
_SYMBOL_LIMIT = 400


def _docstring(init_py: Path) -> str:
    """The module docstring of ``init_py``, or ``""`` if unreadable."""
    try:
        mod = ast.parse(init_py.read_text(encoding="utf-8", errors="ignore"))
        return (ast.get_docstring(mod) or "").strip()
    except (OSError, SyntaxError):
        return ""


def _docline(init_py: Path) -> str:
    doc = _docstring(init_py)
    first = doc.splitlines()[0] if doc else ""
    return first[:160]


def _docsummary(init_py: Path) -> str:
    """The leading prose of the module docstring, whitespace-normalised and bounded.

    ``description`` keeps only the docstring's first line, which is a *title*: it names
    the capability but does not say what it does. Reuse determination is a question
    about purpose ("is there already something that classifies knowledge?"), and a
    title carries almost none of the vocabulary needed to answer it. The leading
    paragraphs do, so they are captured here as well — additively, leaving
    ``description`` byte-identical for its existing consumers.
    """
    doc = _docstring(init_py)
    if not doc:
        return ""
    return " ".join(doc.split())[:_SUMMARY_CHARS]


def _symbols(reader: EvidenceReader, location: str) -> tuple[str, ...]:
    """Public top-level class/function names and module stems of one capability.

    The *structural* half of a capability's identity. Prose describes a capability's
    architecture in vocabulary shared with every other capability ("deterministic",
    "canonical", "constitutional"), which makes prose alone a weak discriminator. Its
    public symbol surface does not: a package containing ``provenance.py`` and
    ``ProvenanceLedger`` is identifiable as the provenance owner by structure rather
    than by adjectives. Recording both lets a reuse question be answered on whichever
    signal is present.

    Derived from tracked files only, so the symbol surface obeys the same
    version-control eligibility boundary as capability discovery itself.
    """
    root = reader.config.repo_root
    names: set[str] = set()
    for relative in reader.tracked(f":(glob){location}/*.py"):
        path = root / relative
        stem = Path(relative).stem
        if stem != "__init__":
            names.add(stem)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except (OSError, SyntaxError):
            continue
        for node in tree.body:
            if isinstance(
                node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
            ) and not node.name.startswith("_"):
                names.add(node.name)
    return tuple(sorted(names)[:_SYMBOL_LIMIT])


def _package_locations(reader: EvidenceReader, root: str) -> list[str]:
    """Every tracked package inside *root*, at ANY depth, repository-relative and sorted.

    Derived from ``git ls-files``; falls back to a deterministic filesystem walk
    so the engine remains usable in a non-git checkout.

    Depth is deliberately unbounded. A fixed ``<root>/*/__init__.py`` glob is the
    same class of defect as a hardcoded root list (see
    :func:`intelligence.rie.config.discover_code_roots`): it silently truncates the
    capability universe at one level, so a nested package could never be
    catalogued and capability coverage fell behind the repository. Sub-packages are
    capabilities in their own right — ``engine/knowledge/ukip`` is an entire
    knowledge-intelligence platform — and a catalogue that cannot see them cannot
    answer "does this already exist?", which is the question the catalogue exists
    to answer.

    The root's own ``__init__.py`` is excluded because :func:`discover` records the
    code root itself separately; including it here would emit a duplicate record.
    """
    base = reader.config.repo_root / root
    tracked = reader.tracked(f":(glob){root}/**/__init__.py")
    if tracked:
        locations = {rel.rsplit("/", 1)[0] for rel in tracked}
        return sorted(locations - {root})
    if not base.exists():
        return []
    return sorted(
        reader.config.rel(init_py.parent)
        for init_py in base.rglob("__init__.py")
        if init_py.parent != base
        and not any(part.startswith(".") for part in init_py.relative_to(base).parts)
    )


def _code_capability(reader: EvidenceReader, seq: int, root: str, location: str) -> Capability:
    """One catalogue record for one tracked Python package."""
    policy = policy_for(root)
    init_py = reader.config.repo_root / location / "__init__.py"
    name = location.replace("/", ".")
    return Capability(
        unique_id=f"RC-{seq:02d}",
        canonical_name=name,
        canonical_location=location,
        category=root,
        authority=str(policy["authority"]),
        reuse=str(policy["reuse"]),
        replacement_prohibited=bool(policy["replacement_prohibited"]),
        implementation_status=str(policy["status"]),
        description=_docline(init_py),
        evidence_present=init_py.exists(),
        summary=_docsummary(init_py),
        symbols=_symbols(reader, location),
    )


def discover(reader: EvidenceReader) -> list[Capability]:
    cfg = reader.config
    caps: list[Capability] = []
    seq = 0

    # 1. Every tracked Python code root, and every tracked package inside it.
    for root in cfg.code_roots:
        seq += 1
        caps.append(_code_capability(reader, seq, root, root))
        for location in _package_locations(reader, root):
            seq += 1
            caps.append(_code_capability(reader, seq, root, location))

    # 2. Automation tools (presence-derived).
    tool_dir = cfg.repo_root / cfg.tool_dir
    for tool in ("ukb.py", "ukbx.py", "register.sh"):
        if (tool_dir / tool).exists():
            seq += 1
            pol = policy_for("automation")
            caps.append(
                Capability(
                    unique_id=f"RC-{seq:02d}",
                    canonical_name=f"automation/{tool}",
                    canonical_location=cfg.rel(tool_dir / tool),
                    category="automation",
                    authority=str(pol["authority"]),
                    reuse=str(pol["reuse"]),
                    replacement_prohibited=bool(pol["replacement_prohibited"]),
                    implementation_status=str(pol["status"]),
                    description=f"Repository automation tool {tool}",
                    evidence_present=True,
                )
            )

    # 3. Operational memory (MCS).
    if (cfg.repo_root / cfg.mcs_dir).exists():
        seq += 1
        pol = policy_for("operational_memory")
        caps.append(
            Capability(
                unique_id=f"RC-{seq:02d}",
                canonical_name="master-context-system",
                canonical_location=cfg.mcs_dir,
                category="operational_memory",
                authority=str(pol["authority"]),
                reuse=str(pol["reuse"]),
                replacement_prohibited=bool(pol["replacement_prohibited"]),
                implementation_status=str(pol["status"]),
                description="Master Context System (state-driven operational memory)",
                evidence_present=True,
            )
        )

    # 4. Orchestration specifications (present without code ⇒ PLANNED).
    for spec in cfg.orchestration_specs:
        spec_path = cfg.repo_root / spec
        seq += 1
        pol = policy_for("orchestration_spec")
        name = "CIOA" if "000000" in spec else "CCE"
        caps.append(
            Capability(
                unique_id=f"SPEC-{name}",
                canonical_name=name,
                canonical_location=spec,
                category="orchestration_spec",
                authority=str(pol["authority"]),
                reuse=str(pol["reuse"]),
                replacement_prohibited=bool(pol["replacement_prohibited"]),
                implementation_status=str(pol["status"]),
                description="Orchestration authority — specification only (no executable code)",
                evidence_present=spec_path.exists(),
            )
        )

    return caps

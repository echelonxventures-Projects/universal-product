"""UCOS-EVIDENCE-UNIVERSE-001 — the five classes of evidence, and what each may touch.

Why a universe rather than a list
---------------------------------
The repository has always held evidence. What it lacked was a statement of what evidence
IS — so each surface was governed by whichever list happened to mention it. ``.gitignore``
decided the version-control boundary, ``00-BOOK/DATA/exclusion-register.json`` decided the
cleanliness class, and nothing at all decided whether a producer could read a surface while
rendering a canonical artifact. UAKOS-CLOSURE-008 is what that gap looks like when it fires:
an execution transcript became a component of two canonical artifacts' identity, and the
question "was that allowed?" had no owner to answer it.

The five classes
----------------
    AUDIT         who did what, recorded so an act can be reviewed after the fact
    DEBUG         a trace kept to diagnose a specific failure
    IMPROVEMENT   a measurement kept to decide what to change next
    EXECUTION     what a command emitted when it ran — stdout, stderr, timings, counts
    VALIDATION    the deterministic derived result of checking something

The four constitutional rules
-----------------------------
    R-EV-1  Evidence may SUPPORT truth.
            Every surface is owned, produced by a named producer, and may be read, cited and
            published. Nothing here restricts the KEEPING of evidence.

    R-EV-2  Evidence may never SILENTLY become identity.
            Every surface declares ``canonical_identity_role: NON_CANONICAL`` and the input
            classification a consumer is obliged to use. A canonical artifact that consumes a
            surface is therefore a declared, visible fact rather than an accident.

    R-EV-3  Execution observations cannot influence canonical hashes.
            AUDIT, DEBUG, IMPROVEMENT and EXECUTION surfaces map to input classifications
            that ``generated_artifacts.CANONICAL_ARTIFACT_INPUT_CLASSIFICATION`` refuses.
            VALIDATION is the one class that may be TRACKED_DETERMINISTIC — a derived result
            is repository truth when it is derived from repository truth.

    R-EV-4  Debug and improvement artifacts cannot affect certification.
            ``may_affect_certification`` is false for both classes by construction, and a
            certification artifact that names such a surface as an input is a finding.

The DEBUG and IMPROVEMENT classes are declared with no surface present. That is deliberate
and is the point of a universe: the first debug trace someone keeps lands in a class that
already exists, with a rule that already applies, instead of arriving unclassified and being
discovered later by a phase gate.
"""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

REGISTRY_PATH = "00-BOOK/DATA/evidence-universe.json"

SCHEMA = "ucos-evidence-universe"

#: The five classes. Closed set: an evidence surface outside it is unclassified, which fails.
EVIDENCE_CLASSES: frozenset[str] = frozenset(
    {"AUDIT", "DEBUG", "IMPROVEMENT", "EXECUTION", "VALIDATION"}
)

#: R-EV-4. These classes may never influence a certification outcome.
CERTIFICATION_FORBIDDEN_CLASSES: frozenset[str] = frozenset({"DEBUG", "IMPROVEMENT"})

#: R-EV-3. The only class whose members may be TRACKED_DETERMINISTIC: a derived result is
#: repository truth exactly when it is derived from repository truth.
DETERMINISTIC_ELIGIBLE_CLASSES: frozenset[str] = frozenset({"VALIDATION"})

#: The identity role every evidence surface carries. Evidence is kept; it makes no claim.
REQUIRED_IDENTITY_ROLE = "NON_CANONICAL"


@dataclass(frozen=True)
class EvidenceSurface:
    """One declared surface of the evidence universe."""

    surface_id: str
    path_pattern: str
    evidence_class: str
    owner: str
    producer: str
    retention: str
    input_classification: str
    canonical_identity_role: str
    may_affect_certification: bool
    present: bool
    note: str

    def matches(self, path: str) -> bool:
        """Whether a repository-relative path falls inside this surface."""
        return fnmatch.fnmatch(path, self.path_pattern) or path.startswith(
            self.path_pattern.rstrip("*")
        )


def _surface(raw: dict) -> EvidenceSurface:
    return EvidenceSurface(
        surface_id=str(raw.get("surface_id", "")),
        path_pattern=str(raw.get("path_pattern", "")),
        evidence_class=str(raw.get("evidence_class", "")),
        owner=str(raw.get("owner", "")),
        producer=str(raw.get("producer", "")),
        retention=str(raw.get("retention", "")),
        input_classification=str(raw.get("input_classification", "")),
        canonical_identity_role=str(raw.get("canonical_identity_role", "")),
        may_affect_certification=bool(raw.get("may_affect_certification", False)),
        present=bool(raw.get("present", False)),
        note=str(raw.get("note", "")),
    )


@lru_cache(maxsize=8)
def load(repo: Path) -> tuple[EvidenceSurface, ...]:
    doc = json.loads((Path(repo) / REGISTRY_PATH).read_text(encoding="utf-8"))
    return tuple(_surface(raw) for raw in doc.get("surfaces", []))


def document(repo: Path) -> dict:
    return json.loads((Path(repo) / REGISTRY_PATH).read_text(encoding="utf-8"))


# --- derived views ------------------------------------------------------------------------


def surface_for(repo: Path, path: str) -> EvidenceSurface | None:
    """The declared surface a path belongs to, or None if the path is not evidence.

    Longest pattern wins, so a specific member (``…/evidence/verify.log``) resolves to its
    own declaration rather than to the directory that contains it.
    """
    candidates = [s for s in load(Path(repo)) if s.matches(path)]
    if not candidates:
        return None
    return max(candidates, key=lambda s: len(s.path_pattern))


def classes_present(repo: Path) -> dict[str, int]:
    counts = dict.fromkeys(sorted(EVIDENCE_CLASSES), 0)
    for surface in load(Path(repo)):
        counts[surface.evidence_class] = counts.get(surface.evidence_class, 0) + 1
    return counts


# --- invariants ---------------------------------------------------------------------------


def validate(repo: Path) -> list[str]:
    """Every rule of the universe, as findings. Empty means the universe holds."""
    repo = Path(repo)
    doc = document(repo)
    findings: list[str] = []

    if doc.get("schema") != SCHEMA:
        findings.append(f"schema is {doc.get('schema')!r}, expected {SCHEMA!r}")

    declared_classes = set(doc.get("evidence_classes", {}))
    if declared_classes != set(EVIDENCE_CLASSES):
        findings.append(
            f"declared classes {sorted(declared_classes)} do not match the universe "
            f"{sorted(EVIDENCE_CLASSES)}"
        )

    seen: set[str] = set()
    for s in load(repo):
        where = s.surface_id or s.path_pattern or "<anonymous>"
        if not s.surface_id:
            findings.append(f"{where}: no surface_id")
        elif s.surface_id in seen:
            findings.append(f"{s.surface_id}: declared twice")
        seen.add(s.surface_id)

        if not s.path_pattern:
            findings.append(f"{where}: no path_pattern")
        if s.evidence_class not in EVIDENCE_CLASSES:
            findings.append(f"{where}: class {s.evidence_class!r} is outside the universe")

        # R-EV-1 — evidence is kept, and kept BY someone.
        for field, value in (
            ("owner", s.owner),
            ("producer", s.producer),
            ("retention", s.retention),
        ):
            if not value:
                findings.append(f"{where}: no {field} — R-EV-1 requires evidence be accountable")

        # R-EV-2 — no surface claims identity.
        if s.canonical_identity_role != REQUIRED_IDENTITY_ROLE:
            findings.append(
                f"{where}: canonical_identity_role is {s.canonical_identity_role!r}; every "
                f"evidence surface is {REQUIRED_IDENTITY_ROLE} — R-EV-2"
            )
        if not s.input_classification:
            findings.append(
                f"{where}: no input_classification — a consumer would have to guess how to "
                f"classify it, which is how evidence becomes identity silently (R-EV-2)"
            )

        # R-EV-3 — only a derived result may be deterministic.
        if (
            s.input_classification in {"TRACKED_DETERMINISTIC", "GENERATED_DETERMINISTIC"}
            and s.evidence_class not in DETERMINISTIC_ELIGIBLE_CLASSES
        ):
            findings.append(
                f"{where}: class {s.evidence_class} declared "
                f"{s.input_classification}; only {sorted(DETERMINISTIC_ELIGIBLE_CLASSES)} may "
                f"carry a deterministic classification — R-EV-3"
            )

        # R-EV-4 — debug and improvement never reach certification.
        if s.evidence_class in CERTIFICATION_FORBIDDEN_CLASSES and s.may_affect_certification:
            findings.append(
                f"{where}: class {s.evidence_class} declares may_affect_certification — R-EV-4"
            )
    return findings

"""EX-016 — the executable classifier for the mutation governance boundary.

``00-BOOK/DATA/mutation-governance-boundary.json`` declares nine ordered classification
rules and a fail-closed terminal. EX-015 made those rules *declarative*; this module makes
them *decidable*. Until a rule is evaluated it is prose, and prose is what let
``uisd-declaration.json`` be authored, owned, engine-consumed and unclassified while six of
its mutations were certified.

THE RULES ARE DATA, NOT CODE. This module contains no rule text, no class name ordering and
no predicate the register does not declare. It loads ``classification_rules.rules``, and
:func:`validate_rule_coverage` refuses **three** ways — a declared rule with no
implemented predicate cannot be evaluated, an implemented predicate no rule declares is
dead code wearing the appearance of enforcement, and a rule that is both and still cannot
be reached classifies nothing at all. The first two are the two-sided construction
``engine.infinite_scope.contract.LAW_CHECKS`` and ``ADMISSION_FORMS`` already use. The third
exists because two-sidedness was not enough: R-09 was declared, implemented and covered
while ``GOVERNED_ANALYSIS`` claimed 0 of 6751 tracked paths, because its criteria were a
strict superset of R-08's and R-08 was evaluated first. See
:func:`validate_rule_reachability`, which refuses that shape statically, and
:func:`validate_rule_population`, which measures whether a reachable rule is actually
reached.

UNRESOLVED IS NOT A CLASS. It is the declared terminal, it confers no authority, and it must
never be read as a permissive default — a default would silently grant an authority no owner
claimed, which is exactly how CORPUS_REGISTRATION and GOVERNED_DECLARATION each came to be
missing. Consumers that gate on classification MUST treat it as failure.

DETERMINISM. Every predicate is a pure function of ``(subject, Repository)``. The repository
view is built once, from ``git ls-files`` and the registers, and is then immutable: no clock,
no environment, no filesystem traversal order and no dependence on the order in which
subjects are presented.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from platform.repository_intelligence import generated_artifacts

from engine.omega_infinite.git_provider import GitDiscoveryProvider

#: A Python string literal. Used to index what the corpus names, never to parse code.
_LITERAL = re.compile(r"""["']([^"'\n]{1,300})["']""")

BOUNDARY_PATH = "00-BOOK/DATA/mutation-governance-boundary.json"

#: Statuses a classification may carry. UNRESOLVED and ERROR are diagnostic; only
#: CLASSIFIED carries a mutation class.
CLASSIFIED = "CLASSIFIED"
UNRESOLVED = "UNRESOLVED"
ERROR = "ERROR"

#: Subject kinds. Most mutation subjects are paths; CONSTITUTIONAL_TRUTH's are not — its
#: subjects are Population and ConstitutionalMetadata objects reached through the gateway.
#: The register states this in ``$subject_domain``; the classifier honours it rather than
#: assuming every subject is a file.
PATH = "PATH"
OBJECT = "OBJECT"

_EXCLUSION_INSTRUMENTS = frozenset({".gitignore", "00-BOOK/DATA/exclusion-register.json"})
_CORPUS_REGISTERS = frozenset({"00-BOOK/DATA/id-ledger.json", "00-BOOK/DATA/artifacts.json"})
_CONSTITUTIONAL_OBJECT_TYPES = frozenset({"Population", "ConstitutionalMetadata"})
_EXECUTABLE_SUFFIXES = frozenset({".py", ".sh"})
_BUILD_MANIFESTS = frozenset({"pyproject.toml"})
_DECLARATION_KEYS = frozenset(
    {"programme", "manifest", "authority", "laws", "expansion_axes", "determination"}
)
_MARKDOWN_SUFFIX = ".md"

#: The labels an authored governance document uses to self-declare its owning authority,
#: checked in this priority order. Both conventions are real and observed: ADRs (adr/*.md)
#: declare "Deciders"; constitutions and determination/assessment reports declare
#: "Authority". Neither is guessed — a document naming neither is not classified.
_OWNER_LABELS = ("authority", "deciders")

#: A document's own self-declared lifecycle stage, when it states one. Open vocabulary —
#: whatever the document says ("Accepted", "RATIFIED ... LIVING-UNTIL-FROZEN"), never
#: coerced into a closed set, matching CXL-style "state what's known, don't invent."
_LIFECYCLE_LABEL = "status"

#: ``**Label:** value`` — the bold-label metadata convention (assessment/determination reports).
_BOLD_LABEL = re.compile(r"^\*\*\s*([A-Za-z][A-Za-z ]*?)\s*:\*\*\s*(.+)$")

#: ``| Label | value |`` — the two-column metadata table convention (ADRs, constitutions).
#: A row is excluded when the label is the header word itself or either cell is a separator
#: (``---``), so the table's own header/rule lines are never read as a declared field.
_TABLE_ROW = re.compile(r"^\|\s*([A-Za-z][A-Za-z ]*?)\s*\|\s*(.+?)\s*\|\s*$")


class ClassificationError(RuntimeError):
    """The boundary register could not be read or is unusable. A FAULT, never a verdict."""


@dataclass(frozen=True, slots=True)
class Subject:
    """One mutation subject: a repository path, or a constitutional object."""

    identity: str
    kind: str = PATH
    object_type: str = ""

    @classmethod
    def of_path(cls, path: str) -> Subject:
        return cls(identity=str(path).replace("\\", "/"), kind=PATH)

    @classmethod
    def of_object(cls, identity: str, object_type: str) -> Subject:
        return cls(identity=identity, kind=OBJECT, object_type=object_type)


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    """Exactly one outcome per subject. ``mutation_class`` is empty unless CLASSIFIED."""

    artifact: str
    mutation_class: str
    rule_id: str
    authority: str
    status: str
    reason: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "artifact": self.artifact,
            "mutation_class": self.mutation_class,
            "rule_id": self.rule_id,
            "authority": self.authority,
            "status": self.status,
            "reason": self.reason,
        }


@dataclass
class Repository:
    """An immutable view of one repository state. Built once, reused for every subject."""

    root: Path
    _overrides: dict[str, object] = field(default_factory=dict, repr=False)

    @cached_property
    def tracked(self) -> frozenset[str]:
        """Every version-controlled path, read NUL-separated so no path is escaped.

        ``-z`` is not an optimisation, it is the correctness condition. Without it git
        C-quotes and octal-escapes any path holding a non-ASCII byte, so a tracked
        ``…UCOS-Ω∞-…`` artifact arrives as the literal string
        ``"…UCOS-\\316\\251\\342\\210\\236-…"`` and never equals its own path. Such a path
        then tests as *untracked*, and because ``_r01_repository_state`` claims any existing
        path absent from this set, the artifact is silently absorbed into REPOSITORY_STATE
        before the rule that actually owns it is ever evaluated — a wrong authority, which
        is strictly worse than the fail-closed terminal. ``-z`` disables quoting outright,
        so this does not depend on ``core.quotePath`` being configured any particular way.

        Decoding is byte-safe for the same reason: a path git carries need not be valid
        UTF-8, and ``surrogateescape`` round-trips those bytes instead of raising or
        substituting. Same construction as ``ukb._git_ls``, the repository's other
        version-control boundary query.
        """
        if "tracked" in self._overrides:
            return frozenset(self._overrides["tracked"])  # type: ignore[arg-type]
        # THE PROVIDER, AND IT NOW FAILS CLOSED — which is what the paragraph above argues for
        # and what this call previously did not do. `check=False` meant a non-git tree yielded an
        # EMPTY tracked set, and `_r01_repository_state` claims any existing path absent from
        # that set: every subject in the repository would be absorbed into REPOSITORY_STATE
        # before the rule that owns it was ever evaluated. That is the "wrong authority, strictly
        # worse than the fail-closed terminal" this docstring names, produced by the tolerance
        # rather than prevented by it.
        #
        # Byte-safety is preserved rather than re-argued: the provider's one subprocess call site
        # decodes with `errors="surrogateescape"` exactly as this call did, so a path git carries
        # that is not valid UTF-8 still round-trips instead of raising or substituting.
        return frozenset(
            artifact.location.locator
            for artifact in GitDiscoveryProvider(root=str(self.root)).enumerate()
        )

    @cached_property
    def generated(self) -> frozenset[str]:
        if "generated" in self._overrides:
            return frozenset(self._overrides["generated"])  # type: ignore[arg-type]
        return frozenset(generated_artifacts.canonical_paths(self.root))

    @cached_property
    def producer_homes(self) -> frozenset[str]:
        """The declared producer module homes. A producer is not a declaration."""
        if "producer_homes" in self._overrides:
            return frozenset(self._overrides["producer_homes"])  # type: ignore[arg-type]
        return frozenset(h.home for h in generated_artifacts.producer_homes(self.root) if h.home)

    @cached_property
    def _consumed_literals(self) -> frozenset[str]:
        """Every string literal appearing in tracked Python source, indexed once.

        A set, not a concatenated blob: the predicate is asked once per tracked subject, and
        substring-scanning the whole corpus per subject is quadratic in repository size — a
        classifier the corpus gate cannot afford to run is a classifier that will not be run.
        """
        if "python_corpus" in self._overrides:
            blob = str(self._overrides["python_corpus"])
            return frozenset(_LITERAL.findall(blob))
        literals: set[str] = set()
        for rel in sorted(p for p in self.tracked if p.endswith(".py")):
            try:
                text = (self.root / rel).read_text(encoding="utf-8", errors="replace")
            except OSError:  # pragma: no cover - a file vanishing mid-scan
                continue
            literals.update(_LITERAL.findall(text))
        return frozenset(literals)

    def is_consumed_by_an_engine(self, path: str) -> bool:
        """True iff some tracked Python source names this artifact as a literal.

        Full path or basename: a consumer may assemble the path from segments, which is what
        ``engine/constitution/stages.py`` does for the UCL manifest, so the basename is the
        only literal present. Both forms are decidable and deterministic.
        """
        basename = path.rsplit("/", 1)[-1]
        return path in self._consumed_literals or basename in self._consumed_literals

    def declaration_document(self, path: str) -> dict | None:
        """The artifact parsed as a JSON object, or None when it is not one."""
        if not path.endswith(".json"):
            return None
        try:
            loaded = json.loads((self.root / path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return loaded if isinstance(loaded, dict) else None

    def text_of(self, path: str) -> str | None:
        """The artifact's own text, or None when it cannot be read as one."""
        overrides = self._overrides.get("markdown_texts")
        if isinstance(overrides, dict) and path in overrides:
            return str(overrides[path])
        try:
            return (self.root / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None


def load_boundary(repo: Path) -> dict:
    """Load the boundary register, or fail closed."""
    try:
        doc = json.loads((repo / BOUNDARY_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ClassificationError(f"{BOUNDARY_PATH} is absent or unreadable") from exc
    if not isinstance(doc, dict) or "classification_rules" not in doc:
        raise ClassificationError(f"{BOUNDARY_PATH} declares no classification_rules")
    return doc


def authority_for(boundary: dict, mutation_class: str) -> str:
    """The governing authority chain the register names for a class."""
    for entry in boundary.get("mutation_classes", []):
        if entry.get("class") == mutation_class:
            return str(entry.get("governed_by", ""))
    return ""


# --------------------------------------------------------------------- rule predicates
# Each returns True when its rule claims the subject. Signature is uniform so the evaluator
# never branches on rule identity.


def _r01_repository_state(subject: Subject, repo: Repository, boundary: dict) -> bool:
    if subject.kind is not PATH and subject.kind != PATH:
        return False
    path = subject.identity
    if path.startswith(".git/"):
        return True
    if path in _EXCLUSION_INSTRUMENTS or path in repo.tracked:
        return False
    return (repo.root / path).exists()


def _r02_exclusion(subject: Subject, repo: Repository, boundary: dict) -> bool:
    return subject.kind == PATH and subject.identity in _EXCLUSION_INSTRUMENTS


def _r03_corpus_registration(subject: Subject, repo: Repository, boundary: dict) -> bool:
    return subject.kind == PATH and subject.identity in _CORPUS_REGISTERS


def _r04_generated_artifact(subject: Subject, repo: Repository, boundary: dict) -> bool:
    return subject.kind == PATH and subject.identity in repo.generated


def _r05_constitutional_truth(subject: Subject, repo: Repository, boundary: dict) -> bool:
    """An OBJECT predicate. A path subject never satisfies it — the register says so."""
    return subject.kind == OBJECT and subject.object_type in _CONSTITUTIONAL_OBJECT_TYPES


def _r06_governed_declaration(subject: Subject, repo: Repository, boundary: dict) -> bool:
    """All seven declared membership criteria, evaluated. Examples are never consulted."""
    if subject.kind != PATH:
        return False
    path = subject.identity
    document = repo.declaration_document(path)
    checks = governed_declaration_checks(path, document, repo)
    return all(checks.values())


def governed_declaration_checks(
    path: str, document: dict | None, repo: Repository
) -> dict[str, bool]:
    """Each criterion, individually, so a refusal can name which one failed."""
    suffix = "." + path.rsplit(".", 1)[-1] if "." in path else ""
    return {
        "authored": path not in repo.producer_homes and not (document or {}).get("generated_at"),
        "repository-controlled": path in repo.tracked,
        "declaration-bearing": bool(document) and bool(_DECLARATION_KEYS & set(document or {})),
        "programme-owned": _owning_programme(path, document) != "",
        "engine-consumed": repo.is_consumed_by_an_engine(path),
        "non-generated": path not in repo.generated,
        "non-executable": suffix not in _EXECUTABLE_SUFFIXES,
    }


def _owning_programme(path: str, document: dict | None) -> str:
    """Exactly one owning programme, or the empty string. CEP-009 I.3 keeps it single."""
    doc = document or {}
    programme = doc.get("programme")
    if isinstance(programme, dict) and programme.get("id"):
        return str(programme["id"])
    for key in ("artifact_id", "id"):
        if isinstance(doc.get(key), str) and doc[key]:
            return str(doc[key])
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "00-MASTER":
        return parts[1]
    return ""


def _r07_source(subject: Subject, repo: Repository, boundary: dict) -> bool:
    if subject.kind != PATH:
        return False
    path = subject.identity
    suffix = "." + path.rsplit(".", 1)[-1] if "." in path else ""
    return suffix in _EXECUTABLE_SUFFIXES or path.rsplit("/", 1)[-1] in _BUILD_MANIFESTS


def _markdown_declared_fields(text: str, *, limit: int = 40) -> dict[str, str]:
    """The document's own opening metadata fields, first match per label wins.

    Scans only the first ``limit`` lines — a self-declaration lives at the top of every
    observed convention (immediately after the title), so this stays bounded rather than
    scanning arbitrarily long prose looking for a label that was never declared.
    """
    fields: dict[str, str] = {}
    for line in text.splitlines()[:limit]:
        stripped = line.strip()
        bold = _BOLD_LABEL.match(stripped)
        if bold:
            label, value = bold.group(1).strip().lower(), bold.group(2).strip()
            fields.setdefault(label, value)
            continue
        row = _TABLE_ROW.match(stripped)
        if row:
            label, value = row.group(1).strip().lower(), row.group(2).strip()
            if label == "field" or set(label) == {"-"} or set(value) <= {"-"}:
                continue  # the table's own header row or separator row, not a declared field
            fields.setdefault(label, value)
    return fields


def authored_document_owner(path: str, repo: Repository) -> str:
    """The authority the document declares of itself, or ``""`` if it declares none.

    Checked in :data:`_OWNER_LABELS` priority order: "Authority" (constitutions,
    determination/assessment reports) before "Deciders" (ADRs) — both are real,
    observed self-declaration conventions, read from the artifact rather than assumed.
    """
    text = repo.text_of(path)
    if text is None:
        return ""
    fields = _markdown_declared_fields(text)
    for label in _OWNER_LABELS:
        if fields.get(label):
            return fields[label]
    return ""


def authored_document_lifecycle(path: str, repo: Repository) -> str:
    """The document's own self-declared lifecycle stage, or ``""`` if it declares none.

    Open vocabulary — whatever the document states ("Accepted", "RATIFIED ...
    LIVING-UNTIL-FROZEN") — never coerced into a closed set the class does not declare.
    """
    text = repo.text_of(path)
    if text is None:
        return ""
    return _markdown_declared_fields(text).get(_LIFECYCLE_LABEL, "")


def authored_document_checks(path: str, repo: Repository) -> dict[str, bool]:
    """Each of Class 7's five membership criteria, individually, mirroring Class 6's shape."""
    return {
        "markdown": path.endswith(_MARKDOWN_SUFFIX),
        "authored": path not in repo.producer_homes,
        "repository-controlled": path in repo.tracked,
        "non-generated": path not in repo.generated,
        "self-declared-authority": bool(authored_document_owner(path, repo)),
    }


def _r08_authored_document(subject: Subject, repo: Repository, boundary: dict) -> bool:
    if subject.kind != PATH:
        return False
    return all(authored_document_checks(subject.identity, repo).values())


#: Rule id to predicate. Two-sided, exactly like LAW_CHECKS: a declared rule with no
#: predicate cannot be evaluated, and a predicate no rule declares is dead code.
#: Matches the alternation R-09 states in its own predicate text, e.g.
#: "(determination|analysis|assessment|...)". Deriving the markers is what keeps them from
#: becoming a second vocabulary: a hardcoded tuple beside a declared alternation is two lists
#: that nobody reconciles, and an unreconciled second list is how R-09 came to be declared with
#: no predicate at all.
_ALTERNATION = re.compile(r"\(([a-z]+(?:\|[a-z]+)+)\)")


def _analysis_markers(boundary: dict) -> tuple[str, ...]:
    """The filename markers Class 8's `analysis-artifact` criterion names, read from the register.

    Read from R-09's declared predicate rather than restated here, so the code cannot drift from
    the rule it implements — the markers can only change by changing the declaration. A register
    that states no alternation is a fault, not an empty vocabulary: an empty marker set would
    make the criterion unsatisfiable and Class 8 would silently claim nothing while every report
    stayed green, which is the vacuity this classifier exists to refuse.
    """
    for rule in boundary["classification_rules"]["rules"]:
        if str(rule.get("id")) != "R-09":
            continue
        match = _ALTERNATION.search(str(rule.get("predicate", "")))
        if not match:
            raise ClassificationError(
                "R-09 states no filename-marker alternation in its predicate, so its "
                "`analysis-artifact` criterion could never be satisfied and Class 8 would claim "
                "nothing while reporting no error"
            )
        return tuple(match.group(1).split("|"))
    raise ClassificationError("the register declares no rule R-09")


def governed_analysis_checks(path: str, repo: Repository, boundary: dict) -> dict[str, bool]:
    """Each of Class 8's six membership criteria, individually, mirroring Class 6 and 7.

    Five of the six are Class 7's, evaluated through the same helpers rather than restated:
    a second copy of `authored`, `repository-controlled` or `self-declared-authority` would be
    a second definition of one criterion, and the two would drift. The sixth — `analysis-artifact`
    — is what separates an analytical work product from general governance prose.
    """
    name = path.rsplit("/", 1)[-1].lower()
    return {
        **authored_document_checks(path, repo),
        "analysis-artifact": any(marker in name for marker in _analysis_markers(boundary)),
    }


def _r09_governed_analysis(subject: Subject, repo: Repository, boundary: dict) -> bool:
    """R-09 — Class 8, GOVERNED_ANALYSIS.

    THIS PREDICATE DID NOT EXIST, AND ITS ABSENCE DISABLED THE WHOLE CLASSIFIER. The register
    declared R-01..R-09 and this module implemented R-01..R-08, so `validate_rule_coverage`
    reported "rule 'R-09' is declared but no predicate implements it" and `classify()` returned
    ERROR for EVERY subject — not just for an analysis artifact. Twenty-eight tests in this
    suite failed at HEAD for that one reason, and the failure is the exact shape this suite's
    own docstring warns about: "a rule nobody evaluates is prose, and prose is what let
    uisd-declaration.json be authored, owned, engine-consumed and unclassified while six of its
    mutations were certified."

    PRECEDENCE IS TAKEN FROM THE REGISTER, NOT FROM THE PROSE. R-09 is declared at precedence 9,
    which places it AFTER R-08 — so a markdown artifact that satisfies both is an
    AUTHORED_DOCUMENT, and Class 8 takes what R-08 leaves. The class body's
    `$distinction_from_authored_document` note asserted the opposite ("R-09 evaluates before
    R-08"); the machine-readable `precedence` field is what `classify()` reads and is therefore
    the authority, and the prose has been corrected to match rather than the ordering silently
    changed to match the prose.
    """
    if subject.kind != PATH:
        return False
    return all(governed_analysis_checks(subject.identity, repo, boundary).values())


RULE_PREDICATES: dict[str, Callable[[Subject, Repository, dict], bool]] = {
    "R-01": _r01_repository_state,
    "R-02": _r02_exclusion,
    "R-03": _r03_corpus_registration,
    "R-04": _r04_generated_artifact,
    "R-05": _r05_constitutional_truth,
    "R-06": _r06_governed_declaration,
    "R-07": _r07_source,
    "R-08": _r08_authored_document,
    "R-09": _r09_governed_analysis,
}


#: How a class's declared membership criteria are NAMED: ``markdown — the path ends .md``
#: states the criterion ``markdown``. The register is the authority on what a class's criteria
#: are, exactly as it is the authority on the rules themselves, so shadowing is decided from
#: the declaration and not from a table in this module. A ``{rule: criteria-function}`` table
#: here would be a second vocabulary nobody reconciles — the shape that let R-09 be declared
#: with no predicate at all. That the module's ``*_checks`` functions return exactly these
#: keys is pinned by ``platform/tests/test_mutation_classification.py``, which binds the two
#: sides without either one having to restate the other.
_CRITERION_SEPARATOR = " — "


def declared_criteria(boundary: dict) -> dict[str, frozenset[str]]:
    """Each class's declared membership-criteria NAMES, for the classes that declare any.

    A class stating no ``membership_criteria`` is not absent from governance; it simply
    states its membership as prose the register does not decompose, and shadowing between
    such a class and another cannot be decided from the declaration. Those classes are
    omitted rather than assumed disjoint, which is why :func:`validate_rule_population`
    exists to catch by census what this cannot catch by structure.
    """
    criteria: dict[str, frozenset[str]] = {}
    for entry in boundary.get("mutation_classes", ()):
        declared = entry.get("membership_criteria") or ()
        if not declared:
            continue
        criteria[str(entry.get("class", ""))] = frozenset(
            str(item).split(_CRITERION_SEPARATOR, 1)[0].strip() for item in declared
        )
    return criteria


def rule_precedence(boundary: dict) -> tuple[dict[str, int], tuple[str, ...]]:
    """Every rule's declared precedence, and the problems that make the order undefined."""
    order: dict[str, int] = {}
    claimed: dict[int, str] = {}
    problems: list[str] = []
    for rule in boundary["classification_rules"]["rules"]:
        rule_id = str(rule.get("id", ""))
        raw = rule.get("precedence")
        try:
            precedence = int(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            problems.append(
                f"rule {rule_id!r} declares no usable precedence ({raw!r}), so the order in "
                f"which it is evaluated is undefined"
            )
            continue
        if precedence in claimed:
            problems.append(
                f"rules {claimed[precedence]!r} and {rule_id!r} both declare precedence "
                f"{precedence}, so their relative order is undefined"
            )
        claimed[precedence] = rule_id
        order[rule_id] = precedence
    return order, tuple(problems)


def ordered_rules(boundary: dict) -> tuple[dict, ...]:
    """The declared rules in EVALUATION order, which is declared precedence and nothing else.

    ``classify`` used to iterate the JSON array directly, so ``precedence`` was authoritative
    only for as long as somebody kept the array sorted by hand. Two orderings that agree by
    convention are one edit away from disagreeing silently, and the one that would have won is
    the one no reader checks. Sorting here makes the declared field the only order there is.
    """
    return tuple(
        sorted(
            boundary["classification_rules"]["rules"],
            key=lambda rule: (int(rule["precedence"]), str(rule.get("id", ""))),
        )
    )


def validate_rule_reachability(boundary: dict) -> tuple[str, ...]:
    """Refuse a rule that is declared, implemented — and can never fire.

    THE THIRD SIDE. :func:`validate_rule_coverage` refuses a declared rule with no predicate
    and a predicate no rule declares. Neither can see the case that actually occurred: R-09 was
    declared, implemented, covered and UNREACHABLE. Its six criteria are R-08's five plus one,
    so R-09 strictly implies R-08 — and R-08 was evaluated first. ``GOVERNED_ANALYSIS`` claimed
    0 of 6751 tracked paths while every report stayed green. That is the vacuity this module
    exists to refuse, wearing the appearance of coverage.

    Both conditions below are STATIC. They hold whatever the corpus happens to contain today,
    which is what separates them from :func:`validate_rule_population`:

    * **Precedence is a total order.** A rule with no usable precedence, or two rules sharing
      one, leaves evaluation order undefined — and an undefined order over overlapping
      predicates makes a subject's class depend on file layout.
    * **No rule is shadowed.** If rule X's criteria are a strict superset of an earlier rule
      Y's, then X ⟹ Y, Y is reached first, and X can never claim a subject in any repository
      state whatsoever.
    """
    order, problems = rule_precedence(boundary)
    problems = list(problems)
    criteria = declared_criteria(boundary)
    # Rules are compared by the CLASS each claims, because criteria are declared on classes.
    ruled = tuple(
        (str(rule.get("id", "")), str(rule.get("class", "")))
        for rule in boundary["classification_rules"]["rules"]
        if str(rule.get("class", "")) in criteria and str(rule.get("id", "")) in order
    )
    for later_id, later_class in ruled:
        later = criteria[later_class]
        for earlier_id, earlier_class in ruled:
            if earlier_id == later_id or order[earlier_id] >= order[later_id]:
                continue
            earlier = criteria[earlier_class]
            if earlier < later:
                problems.append(
                    f"rule {later_id!r} ({later_class}, precedence {order[later_id]}) can never "
                    f"match: its criteria are those of {earlier_id!r} ({earlier_class}, "
                    f"precedence {order[earlier_id]}) plus {sorted(later - earlier)}, so every "
                    f"subject it would claim is claimed by {earlier_id!r} first"
                )
    return tuple(problems)


def validate_rule_population(
    results: tuple[ClassificationResult, ...], boundary: dict
) -> tuple[str, ...]:
    """Refuse a rule that claims nothing over the live corpus and has not declared why.

    :func:`validate_rule_reachability` proves a rule CAN fire. This measures whether it DOES.
    The two are different questions and a rule can pass the first while failing the second —
    a criterion narrowed until nothing satisfies it is reachable in principle and vacuous in
    fact, and the register would still read as a complete classification.

    Zero is not automatically a fault. R-01 claims untracked paths, so it claims none of a
    tracked corpus by construction; R-05's subjects are constitutional objects rather than
    paths. Those are legitimate and the register names them in
    ``$rules_expected_to_claim_no_tracked_path``, each with its reason. Anything else claiming
    nothing is reported — an expectation stated in the register can be argued with, whereas a
    silent zero cannot.
    """
    excused = boundary["classification_rules"].get("$rules_expected_to_claim_no_tracked_path")
    excused = excused if isinstance(excused, dict) else {}
    claimed = {r.rule_id for r in results if r.status == CLASSIFIED}
    problems: list[str] = []
    for rule in ordered_rules(boundary):
        rule_id = str(rule.get("id", ""))
        if rule_id in claimed or rule_id in excused:
            continue
        problems.append(
            f"rule {rule_id!r} ({rule.get('class', '')}) claimed no subject over the corpus "
            f"and is not named in $rules_expected_to_claim_no_tracked_path with a reason"
        )
    for rule_id in sorted(set(excused) & claimed):
        problems.append(
            f"rule {rule_id!r} is excused from claiming subjects but claimed some; the "
            f"excuse is stale and must be withdrawn"
        )
    return tuple(problems)


def validate_rule_coverage(boundary: dict) -> tuple[str, ...]:
    """Refuse in every direction. Empty means the register and this module agree.

    Three sides, not two: a declared rule no predicate implements, a predicate no rule
    declares, and a rule that is both and still cannot be reached.
    """
    declared = [str(r.get("id", "")) for r in boundary["classification_rules"]["rules"]]
    problems: list[str] = []
    for rule_id in declared:
        if rule_id not in RULE_PREDICATES:
            problems.append(f"rule {rule_id!r} is declared but no predicate implements it")
    for orphan in sorted(set(RULE_PREDICATES) - set(declared)):
        problems.append(f"predicate {orphan!r} is implemented but no rule declares it")
    if problems:
        # Reachability reads the criteria functions of rules this module implements. With a
        # rule or a predicate missing, that reading is not yet meaningful — report the gap
        # that exists rather than a second one derived from it.
        return tuple(problems)
    return tuple(problems) + validate_rule_reachability(boundary)


def classify(
    subject: Subject | str, repo: Repository, boundary: dict | None = None
) -> ClassificationResult:
    """Resolve one subject to exactly one outcome, in declared precedence order."""
    if isinstance(subject, str):
        subject = Subject.of_path(subject)
    try:
        doc = boundary if boundary is not None else load_boundary(repo.root)
    except ClassificationError as exc:
        return ClassificationResult(subject.identity, "", "", "", ERROR, str(exc))

    problems = validate_rule_coverage(doc)
    if problems:
        return ClassificationResult(subject.identity, "", "", "", ERROR, "; ".join(problems))

    for rule in ordered_rules(doc):
        rule_id = str(rule.get("id", ""))
        try:
            matched = RULE_PREDICATES[rule_id](subject, repo, doc)
        except Exception as exc:  # noqa: BLE001 - an unevaluable predicate is a FAULT
            return ClassificationResult(
                subject.identity, "", rule_id, "", ERROR, f"{type(exc).__name__}: {exc}"
            )
        if matched:
            mutation_class = str(rule.get("class", ""))
            return ClassificationResult(
                artifact=subject.identity,
                mutation_class=mutation_class,
                rule_id=rule_id,
                authority=authority_for(doc, mutation_class),
                status=CLASSIFIED,
            )

    terminal = doc["classification_rules"].get("terminal", {})
    return ClassificationResult(
        artifact=subject.identity,
        mutation_class="",
        rule_id="",
        authority="",
        status=UNRESOLVED,
        reason=str(terminal.get("effect", "FAILS CLOSED"))
        + " — no mutation classification rule matched",
    )


def classify_all(
    paths: list[str] | tuple[str, ...], repo: Repository
) -> tuple[ClassificationResult, ...]:
    """Classify many subjects deterministically: sorted input, one shared boundary read."""
    doc = load_boundary(repo.root)
    return tuple(classify(Subject.of_path(p), repo, doc) for p in sorted(paths))


def unresolved(results: tuple[ClassificationResult, ...]) -> tuple[str, ...]:
    """The subjects that reached the terminal. Ordered, for a fail-closed consumer."""
    return tuple(r.artifact for r in results if r.status == UNRESOLVED)


__all__ = [
    "BOUNDARY_PATH",
    "CLASSIFIED",
    "ERROR",
    "OBJECT",
    "PATH",
    "RULE_PREDICATES",
    "UNRESOLVED",
    "ClassificationError",
    "ClassificationResult",
    "Repository",
    "Subject",
    "authored_document_checks",
    "authored_document_lifecycle",
    "authored_document_owner",
    "authority_for",
    "classify",
    "classify_all",
    "declared_criteria",
    "governed_analysis_checks",
    "governed_declaration_checks",
    "load_boundary",
    "ordered_rules",
    "rule_precedence",
    "unresolved",
    "validate_rule_coverage",
    "validate_rule_population",
    "validate_rule_reachability",
]

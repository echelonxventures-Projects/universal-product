"""UCOS Ω∞ Phase 1, Deliverable 4 — classification as a pipeline, with extension LAST.

AUTHORITY = NONE (DERIVED TRUTH).

THE ASSUMPTION THIS REMOVES. Discovery today asks git for ``'*.py'`` and every artifact it returns
is Python by construction. Type is not decided, it is presupposed by the query — so there is no
classifier to improve, no artifact that could be typed wrongly, and no way to discover a Python
file that is not named ``.py`` or to notice that a ``.py`` file is actually generated data.

THE DIRECTIVE'S CONSTRAINT, TAKEN LITERALLY: "classification must be independent from file
extension". Independence is not achieved by deleting extension logic — a suffix is real evidence
and discarding it would make the layer worse. It is achieved by making the suffix the WEAKEST and
LAST source of evidence, so that no classification DEPENDS on it:

  1. PROVIDER-DECLARED   the storage system already knows. An object store with a content type, a
                         registry with a schema field, a graph with a node label. Strongest,
                         because it is a fact from the system of record rather than an inference.
  2. CONTENT-BASED       the artifact's own bytes. A shebang names its interpreter; a document
                         opens with structure. Evidence, and it travels with the bytes.
  3. EXTENSION-BASED     the locator's suffix. Weakest: a name is a claim by whoever typed it, and
                         renaming a file must not be able to change what it IS.
  4. UNKNOWN             unconditional. Total by construction, and a NAMED population rather than
                         an absence, so it can be counted, reported and driven down.

Every artifact receives exactly one type, and step 4 takes no condition — the same totality
construction as Ω-5's dispositions, and for the same reason: an unclassified artifact is a
governance hole that no measurement can see.

NO GIANT RULE TABLE, AND NO HARD-CODED LANGUAGE LIST. This module contains no mapping from
suffixes to languages. ``SuffixClassifier`` holds a vocabulary it is GIVEN; ``TypeVocabulary`` is
the injected data; and ``seed_vocabulary()`` builds a deliberately minimal starting set which a
caller may replace wholesale. Adding Rust does not touch this file — it registers a type and a
suffix. That is the difference between a rule engine and a rule list.

ONE VOCABULARY, TWO ACCESS PATHS. The suffix classifier and the interpreter probe read the SAME
``TypeVocabulary``. A hard-coded "shebang mentions python -> PYTHON" branch would be a second
language list, disagreeing with the first the moment either changed.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from engine.omega_infinite.artifact import (
    CONFIGURATION,
    DATASET,
    DOCUMENT,
    PYTHON,
    UNKNOWN,
    Artifact,
    ArtifactType,
)

#: The metadata key through which a provider declares a type it already knows. Read by
#: ``ProviderDeclaredClassifier``; a provider that knows nothing simply omits it.
DECLARED_TYPE_KEY = "declared_type"

RULE_PROVIDER_DECLARED = "Ω∞-T-01"
RULE_CONTENT_INTERPRETER = "Ω∞-T-02"
RULE_CONTENT_STRUCTURE = "Ω∞-T-03"
RULE_SUFFIX = "Ω∞-T-04"
RULE_UNCLASSIFIED = "Ω∞-T-05"


class ClassificationError(RuntimeError):
    """A classifier was configured in a way that could produce an unauditable type."""


@dataclass(frozen=True)
class Classification:
    """One classifier's answer: the type, and the rule that produced it.

    THE RULE IS NOT OPTIONAL. A type with no rule cannot be argued with, and "why is this a
    DATASET" is the first question a reader of the evidence document asks.
    """

    artifact_type: ArtifactType
    rule: str

    def __post_init__(self) -> None:
        if not self.rule.strip():
            raise ClassificationError(
                f"a classification to {self.artifact_type.name} must name the rule that produced "
                "it, or the type is an assertion rather than a measurement"
            )


@runtime_checkable
class Classifier(Protocol):
    """One source of typing evidence.

    ABSTAINING IS A FIRST-CLASS ANSWER. ``classify`` returns ``None`` for "I have no evidence",
    which is different from "this is UNKNOWN". Only the terminal rule may say UNKNOWN; a
    classifier that guessed instead of abstaining would prevent every weaker classifier from ever
    being consulted.
    """

    def identifier(self) -> str:
        """A stable name, so evidence can say which classifier answered."""

    def classify(self, artifact: Artifact, content: str | None) -> Classification | None:
        """The type this classifier can evidence, or ``None`` to abstain."""


# --------------------------------------------------------------------------------- vocabulary


@dataclass(frozen=True)
class TypeVocabulary:
    """Injected evidence tables. THE DATA, kept out of the classifiers that read it.

    ``suffixes``      locator suffix -> type. Lower-cased on lookup.
    ``interpreters``  interpreter basename -> type, for shebang evidence.

    Both are supplied by the caller. This class holds no default and knows no language, so the
    "no hard-coded language list" constraint is satisfied structurally rather than by restraint.
    """

    suffixes: dict[str, ArtifactType] = field(default_factory=dict)
    interpreters: dict[str, ArtifactType] = field(default_factory=dict)

    def for_suffix(self, locator: str) -> ArtifactType | None:
        """The longest registered suffix that matches, so ``.tar.gz`` can beat ``.gz`` later."""
        lowered = locator.lower()
        matches = [s for s in self.suffixes if lowered.endswith(s.lower())]
        if not matches:
            return None
        return self.suffixes[max(matches, key=len)]

    def for_interpreter(self, token: str) -> ArtifactType | None:
        """Match an interpreter basename, ignoring a trailing version — ``python3.12`` is python."""
        name = token.rsplit("/", 1)[-1].strip()
        for candidate, artifact_type in sorted(self.interpreters.items()):
            if name == candidate or name.startswith(candidate):
                return artifact_type
        return None

    def with_suffix(self, suffix: str, artifact_type: ArtifactType) -> TypeVocabulary:
        return TypeVocabulary({**self.suffixes, suffix: artifact_type}, dict(self.interpreters))

    def with_interpreter(self, token: str, artifact_type: ArtifactType) -> TypeVocabulary:
        return TypeVocabulary(dict(self.suffixes), {**self.interpreters, token: artifact_type})


def seed_vocabulary() -> TypeVocabulary:
    """A MINIMAL starting vocabulary — enough to reproduce today's behaviour, and no more.

    DELIBERATELY SMALL, and the smallness is the deliverable. A hundred-entry table would be the
    "giant rule table" the directive forbids, and would encode a language list that goes stale
    exactly the way ``SOURCE_TREES = ("engine", "platform")`` did. Callers extend this; providers
    override it entirely; nothing in the pipeline assumes any particular entry is present.
    """
    return TypeVocabulary(
        suffixes={
            ".py": PYTHON,
            ".md": DOCUMENT,
            ".rst": DOCUMENT,
            ".txt": DOCUMENT,
            ".toml": CONFIGURATION,
            ".cfg": CONFIGURATION,
            ".ini": CONFIGURATION,
            ".json": DATASET,
            ".csv": DATASET,
        },
        interpreters={"python": PYTHON},
    )


# -------------------------------------------------------------------------------- classifiers


@dataclass(frozen=True)
class ProviderDeclaredClassifier:
    """STRONGEST. The provider already knew, so nothing here needs to infer.

    This is the classifier that makes remote knowledge spaces possible without reading bytes: an
    object store returns a content type in its listing, and one network round-trip per artifact is
    avoided for every artifact the store can already describe.
    """

    resolve: Callable[[str], ArtifactType]

    def identifier(self) -> str:
        return "provider-declared"

    def classify(self, artifact: Artifact, content: str | None) -> Classification | None:
        del content  # a declaration needs no bytes, which is the point of consulting it first
        declared = artifact.metadata.get(DECLARED_TYPE_KEY, "")
        if not declared:
            return None
        return Classification(self.resolve(declared), RULE_PROVIDER_DECLARED)


#: How many leading characters of an artifact the content classifier may read. A BOUND, declared
#: here rather than left to callers, for the reason ``classification.MARKER_WINDOW`` records in
#: UCOS-OMEGA-001: a limit enforced by the caller is a limit some other caller will not enforce.
CONTENT_WINDOW = 4096


@dataclass(frozen=True)
class InterpreterClassifier:
    """CONTENT-BASED. Reads the shebang and resolves the interpreter through the vocabulary.

    WHY THIS IS THE HEADLINE OF DELIVERABLE 4. An executable script with no suffix at all —
    ``bin/ucos-report`` with ``#!/usr/bin/env python3`` — is typed PYTHON here, by its bytes, with
    the extension classifier never consulted. That is "independent from file extension" discharged
    by demonstration rather than claimed in a docstring.
    """

    vocabulary: TypeVocabulary

    def identifier(self) -> str:
        return "content-interpreter"

    def classify(self, artifact: Artifact, content: str | None) -> Classification | None:
        del artifact
        if not content:
            return None
        first = content[:CONTENT_WINDOW].splitlines()[:1]
        if not first or not first[0].startswith("#!"):
            return None
        resolved = self._resolve(first[0][2:])
        if resolved is None:
            return None
        return Classification(resolved, RULE_CONTENT_INTERPRETER)

    def _resolve(self, shebang: str) -> ArtifactType | None:
        """``/usr/bin/env python3`` and ``/usr/bin/python3.12`` resolve the same way."""
        for token in shebang.split():
            if token.endswith("env"):
                continue
            found = self.vocabulary.for_interpreter(token)
            if found is not None:
                return found
        return None


#: A content probe: bytes in, a type or ``None`` out. The extension point for magic numbers, XML
#: prologues, parquet footers and anything else a future artifact kind needs.
ContentProbe = Callable[[str], ArtifactType | None]


def structured_data_probe(head: str) -> ArtifactType | None:
    """Serialised structured data, recognised by shape rather than by name.

    GENERIC ON PURPOSE. It tests for a document that opens as a JSON object or array, which is a
    property of the bytes and not of any format's file naming. A ``.json`` suffix is not consulted
    and is not required.
    """
    stripped = head.lstrip()
    if stripped[:1] in ("{", "[") and stripped[-1:] in ("}", "]", ""):
        return DATASET
    return None


def prose_probe(head: str) -> ArtifactType | None:
    """A document that opens with a markup heading. Structure, not suffix."""
    stripped = head.lstrip()
    if stripped.startswith(("# ", "## ", "===", "---\ntitle")):
        return DOCUMENT
    return None


@dataclass(frozen=True)
class ContentProbeClassifier:
    """CONTENT-BASED. Runs injected probes in order; the first that answers wins.

    The probe list is data, so recognising a new format is a registration. There is no branch in
    this class that names a format, which is what keeps it from becoming the rule table.
    """

    probes: tuple[ContentProbe, ...]

    def identifier(self) -> str:
        return "content-structure"

    def classify(self, artifact: Artifact, content: str | None) -> Classification | None:
        del artifact
        if not content:
            return None
        head = content[:CONTENT_WINDOW]
        for probe in self.probes:
            found = probe(head)
            if found is not None:
                return Classification(found, RULE_CONTENT_STRUCTURE)
        return None


@dataclass(frozen=True)
class SuffixClassifier:
    """WEAKEST, AND LAST. The locator's suffix, consulted only when the bytes said nothing.

    Ordered last so that no classification DEPENDS on a name. Renaming an artifact can only change
    its type when nothing stronger had an opinion — which is the honest amount of authority a
    filename deserves.
    """

    vocabulary: TypeVocabulary

    def identifier(self) -> str:
        return "suffix"

    def classify(self, artifact: Artifact, content: str | None) -> Classification | None:
        del content
        found = self.vocabulary.for_suffix(artifact.location.locator)
        if found is None:
            return None
        return Classification(found, RULE_SUFFIX)


# ----------------------------------------------------------------------------------- pipeline


@dataclass(frozen=True)
class ClassificationPipeline:
    """Ordered classifiers plus an unconditional terminal rule. TOTAL by construction.

    ``classify`` never returns ``None`` and never raises for an unrecognised artifact: it returns
    UNKNOWN with ``RULE_UNCLASSIFIED``. That makes "we could not type this" a countable population
    instead of a silence, which is the only form in which it can be driven to zero.
    """

    classifiers: tuple[Classifier, ...]

    def identifiers(self) -> tuple[str, ...]:
        return tuple(c.identifier() for c in self.classifiers)

    def classify(self, artifact: Artifact, content: str | None = None) -> Classification:
        for classifier in self.classifiers:
            answer = classifier.classify(artifact, content)
            if answer is not None:
                return answer
        return Classification(UNKNOWN, RULE_UNCLASSIFIED)

    def apply(self, artifact: Artifact, content: str | None = None) -> Artifact:
        """The artifact, typed. One call site, so a type is never attached without its rule."""
        answer = self.classify(artifact, content)
        return artifact.with_type(answer.artifact_type, answer.rule)

    def apply_all(
        self,
        artifacts: Iterable[Artifact],
        read: Callable[[Artifact], str | None] | None = None,
    ) -> tuple[Artifact, ...]:
        """Type a population. ``read`` is injected so a REMOTE provider can decline to fetch bytes.

        A pipeline that read content itself would make classification impossible to run against a
        knowledge space whose bytes cost a network call each — so who reads, and whether reading
        happens at all, is the caller's decision.
        """
        return tuple(self.apply(a, read(a) if read is not None else None) for a in artifacts)


def default_pipeline(vocabulary: TypeVocabulary | None = None) -> ClassificationPipeline:
    """The Phase 1 pipeline: declared, then content, then suffix, then UNKNOWN.

    ORDER IS THE ARCHITECTURE. Reversing these four lines would restore extension-primary
    classification exactly, which is why the order is stated here once and nowhere else.
    """
    resolved = vocabulary or seed_vocabulary()
    return ClassificationPipeline(
        (
            ProviderDeclaredClassifier(_resolve_declared),
            InterpreterClassifier(resolved),
            ContentProbeClassifier((structured_data_probe, prose_probe)),
            SuffixClassifier(resolved),
        )
    )


def _resolve_declared(name: str) -> ArtifactType:
    """Resolve a provider-declared type name through the process-wide registry.

    A NAME THE REGISTRY DOES NOT KNOW IS A FAULT, not a new type. A provider inventing types by
    spelling is how a vocabulary stops being one; ``ArtifactTypeRegistry.declare`` is the way in.
    """
    from engine.omega_infinite.artifact import TYPES

    return TYPES.resolve(name)


def unknown_population(artifacts: Sequence[Artifact]) -> tuple[Artifact, ...]:
    """Every artifact the pipeline could not type. The number Phase 2 is measured against."""
    return tuple(a for a in artifacts if a.artifact_type == UNKNOWN)

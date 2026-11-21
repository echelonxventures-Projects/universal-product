"""UCOS Ω∞ Phase 1, Deliverable 2b — discovery with no version control of any kind.

AUTHORITY = NONE (DERIVED TRUTH).

THE DELIVERABLE, STATED AS THE TEST THAT PROVES IT. This provider must work without git, hg, svn or
p4. ``engine/tests/omega_infinite/test_filesystem_provider.py`` enumerates a directory that has
never been a repository — no ``.git``, no VCS binary consulted, no index — and gets a population.
That is the demonstration that git is no longer a dependency of UCOS: the system can discover
artifacts from storage directly.

WHAT THIS PROVIDER HONESTLY CANNOT DO, and declaring it is the whole value of Deliverable 6:

  NOT TRACKED_CONTENT     it enumerates whatever is on disk, so local debris IS in the population.
                          This is the exact defect ``platform/tests/test_coverage_scope.py``
                          documents — a control that decides differently on a developer's machine.
                          The provider is not forbidden from existing because of it; it is required
                          to SAY so, and a measurement that needs the eligibility boundary calls
                          ``require(TRACKED_CONTENT)`` and gets a refusal naming this provider.
  NOT VERSIONED_CONTENT   a filesystem has no revision. ``revision`` stays empty rather than being
                          filled with an mtime, which would make an unreproducible enumeration look
                          reproducible.
  NOT AUTHORITY_METADATA  a POSIX owner is not an authority. ``uid 501`` answers "which account
                          wrote this", never "which programme owns it", and offering it as
                          ownership would fabricate a governance fact.

WHY EXCLUSIONS ARE INJECTED AND NOT HARD-CODED. A walk of a working tree meets ``.git``,
``__pycache__``, virtualenvs and caches, and enumerating them would drown the population. But a
fixed list of noise directories inside this file would be the same class of defect as
``SOURCE_TREES``: correct on the day it was written, silently wrong afterwards, with no term for
what it omits. So ``DEFAULT_EXCLUSIONS`` is a constructor DEFAULT that any caller may replace
wholesale, and ``metadata()`` reports the exclusions actually in force — so a population is always
explainable without reading this module.
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterable

from engine.omega_infinite.artifact import Artifact, Location
from engine.omega_infinite.capability import (
    CONTENT_HASHING,
    LOCAL_STORAGE,
    CapabilitySet,
)
from engine.omega_infinite.provider import (
    BaseProvider,
    ProviderError,
    ProviderMetadata,
    Selector,
)

IDENTIFIER = "filesystem"

#: Exactly two capabilities, and the SHORTNESS of this tuple is the point. Compare it against
#: ``git_provider.CAPABILITIES``: the difference between the two is machine-readable, so "what do I
#: lose by discovering without version control" is a question with a computable answer.
CAPABILITIES = CapabilitySet.of(LOCAL_STORAGE, CONTENT_HASHING)

#: A DEFAULT, not a policy. Replaceable per instance; always reported in ``metadata()``.
DEFAULT_EXCLUSIONS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
    }
)

#: Bounds the walk so a symlink cycle or an absurd tree terminates instead of hanging a gate.
MAX_DEPTH = 64


class FilesystemDiscoveryProvider(BaseProvider):
    """Enumerates artifacts directly from storage. No index, no VCS, no network."""

    #: Below git: this provider offers strictly fewer guarantees, and resolution should prefer the
    #: stronger one when both are available. It is still the provider that makes the system work
    #: where no version control exists at all.
    priority = 10

    def __init__(
        self,
        root: str,
        *,
        exclusions: frozenset[str] = DEFAULT_EXCLUSIONS,
        follow_symlinks: bool = False,
    ) -> None:
        self.root = root
        self.exclusions = exclusions
        #: Off by default. A followed symlink can leave the knowledge space entirely, which would
        #: make the population depend on filesystem topology outside the space being measured.
        self.follow_symlinks = follow_symlinks

    # ------------------------------------------------------------------------- the contract

    def identifier(self) -> str:
        return IDENTIFIER

    def capabilities(self) -> CapabilitySet:
        return CAPABILITIES

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            identifier=IDENTIFIER,
            binding=self.root,
            mechanism="direct storage walk; no version control consulted",
            revision="",
            details={
                "exclusions": ", ".join(sorted(self.exclusions)) or "<none>",
                "follow_symlinks": str(self.follow_symlinks).lower(),
                "max_depth": str(MAX_DEPTH),
                "eligibility_boundary": "NONE — every readable entry is in the population, "
                "including untracked local debris, which is why TRACKED_CONTENT is not declared",
            },
        )

    def collect(self, selector: Selector) -> Iterable[Artifact]:
        """Walk storage and emit universal Artifacts. No suffix filter, no language assumption."""
        del selector  # narrowing is BaseProvider.enumerate's job, uniformly for every provider
        for locator in self._walk():
            yield Artifact(
                identifier=f"{IDENTIFIER}:{locator}",
                location=Location(IDENTIFIER, locator),
                metadata={"tracked": "false"},
            )

    # ------------------------------------------------------------------- filesystem specifics

    def _walk(self) -> tuple[str, ...]:
        """Repo-relative POSIX locators, sorted. Depth-bounded, exclusion-pruned.

        SORTED EXPLICITLY. ``os.walk`` order is filesystem-dependent, and a population whose order
        varies by machine would make two evidence documents differ for no governed reason.
        """
        if not os.path.isdir(self.root):
            raise ProviderError(
                f"{self.root!r} is not a readable directory, so this provider has no storage to "
                "enumerate; an empty population would be reported as a clean one"
            )
        found: list[str] = []
        for current, directories, files in os.walk(self.root, followlinks=self.follow_symlinks):
            relative = os.path.relpath(current, self.root)
            if self._prune(relative, directories):
                continue
            found.extend(self._locators(relative, files))
        return tuple(sorted(found))

    def _prune(self, relative: str, directories: list[str]) -> bool:
        """Mutate ``directories`` in place to stop the walk descending. Returns True to skip.

        In-place mutation is how ``os.walk`` pruning works; doing it here keeps the single
        responsibility of "which subtrees are out of scope" in one method.
        """
        if relative != "." and self._depth(relative) >= MAX_DEPTH:
            directories.clear()
            return True
        directories[:] = sorted(d for d in directories if d not in self.exclusions)
        return False

    def _locators(self, relative: str, files: Iterable[str]) -> tuple[str, ...]:
        prefix = "" if relative == "." else relative.replace(os.sep, "/") + "/"
        return tuple(f"{prefix}{name}" for name in sorted(files) if name not in self.exclusions)

    @staticmethod
    def _depth(relative: str) -> int:
        return len(relative.replace(os.sep, "/").split("/"))

    def read(self, locator: str) -> str:
        """Artifact bytes as text. Used by content-based classification.

        ``surrogateescape`` rather than a failure, matching ``graph.read_text``: an artifact whose
        bytes are not valid UTF-8 is still a real artifact, and refusing to enumerate it would
        shrink the population for an encoding reason.
        """
        absolute = os.path.join(self.root, locator)
        try:
            with open(absolute, encoding="utf-8", errors="surrogateescape") as handle:
                return handle.read()
        except OSError as exc:
            raise ProviderError(f"{locator!r} could not be read from storage: {exc}") from exc

    def content_hash(self, locator: str) -> str:
        """A sha256 of the bytes. Requires ``CONTENT_HASHING``, and asks first.

        NOT COMPARABLE WITH GIT'S HASH, and that is why ``Location`` carries the provider. Git
        reports a blob id over a prefixed payload; this is a plain digest. Two providers hashing the
        same bytes to different values is expected — treating the digest as globally comparable is
        the defect, and including the provider in the location is what prevents it.
        """
        self.require(CONTENT_HASHING)
        absolute = os.path.join(self.root, locator)
        try:
            with open(absolute, "rb") as handle:
                return hashlib.sha256(handle.read()).hexdigest()
        except OSError as exc:
            raise ProviderError(f"{locator!r} could not be hashed: {exc}") from exc


def available(root: str) -> bool:
    """Whether storage is readable. The FALLBACK PROBE, and it needs no external binary.

    A directory that exists is enough. This is the provider that answers when every version control
    probe has said no, which is what makes "discovery without git" a real capability of the system
    rather than a documented aspiration.
    """
    return os.path.isdir(root)

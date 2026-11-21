"""UCOS Ω∞ Phase 1, Deliverable 2a — Git, demoted from architecture to provider.

AUTHORITY = NONE (DERIVED TRUTH).

WHAT CHANGED, AND IT IS ONLY THIS: git is still how this repository is discovered, and it is no
longer how UCOS discovers. The mechanism moved from the middle of the system to behind a contract,
so the sentence "UCOS requires git" became "this provider requires git, and says so".

WHY GIT REMAINS THE PREFERRED PROVIDER HERE, stated so the demotion is not mistaken for a
downgrade. ``platform/tests/test_coverage_scope.py`` records the measurement: a control that
enumerates the working copy decides differently on a developer's machine than on a clean checkout,
and a control whose verdict depends on local debris gets suppressed. Version control is an
ELIGIBILITY BOUNDARY, and that boundary is a real governance property — which is why this provider
declares ``TRACKED_CONTENT`` and carries ``priority = 100``. Resolution by capability then prefers
it automatically, with no call site naming it.

THE ONE BEHAVIOURAL DIFFERENCE FROM Ω-1, AND IT IS DELIBERATE. ``discovery.tracked_python`` asks
git for ``'*.py'``. This provider asks for EVERYTHING and lets the caller narrow with a
``Selector``. The filter was the hard-coded assumption; moving it to the caller is the deliverable.
``compat.py`` demonstrates that passing ``Selector(patterns=("*.py",))`` reproduces the Ω-1
population exactly, so nothing is lost by widening the default.

WHAT THIS PROVIDER DOES NOT DO. It does not classify (Deliverable 4 does), it does not derive
authority (it merely declares that git CAN supply ownership facts, and exposes them on request),
and it does not decide what a knowledge space is (Deliverable 5 does). One question only.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Iterable

from engine.omega_infinite.artifact import Artifact, Location
from engine.omega_infinite.capability import (
    AUTHORITY_METADATA,
    CHANGE_SET,
    CONTENT_HASHING,
    LOCAL_STORAGE,
    REVISION_HISTORY,
    REVISION_IDENTITY,
    REVISION_METADATA,
    TRACKED_CONTENT,
    VERSIONED_CONTENT,
    WORKING_TREE_STATE,
    CapabilitySet,
)
from engine.omega_infinite.provider import (
    BaseProvider,
    ProviderError,
    ProviderMetadata,
    Selector,
)

IDENTIFIER = "git"

#: What git genuinely offers. Declared once, here, by the component that can actually deliver it —
#: which is the Deliverable 6 rule: providers self-describe, and nobody describes them.
CAPABILITIES = CapabilitySet.of(
    TRACKED_CONTENT,
    CHANGE_SET,
    REVISION_IDENTITY,
    REVISION_HISTORY,
    REVISION_METADATA,
    WORKING_TREE_STATE,
    VERSIONED_CONTENT,
    LOCAL_STORAGE,
    CONTENT_HASHING,
    AUTHORITY_METADATA,
)

#: Fixed argv prefix. No shell, ever, and no interpolation of caller data into a command string.
_LS_FILES = ("git", "ls-files", "-z", "--cached", "--exclude-standard")


def _run(root: str, *arguments: str) -> str:
    """One subprocess call site, so quoting and failure handling exist in exactly one place."""
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell, caller data never spliced
            ["git", *arguments],  # noqa: S607 - git resolved from PATH by design, as in Ω-1
            cwd=root,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ProviderError(f"git failed in {root!r} running {arguments}: {exc}") from exc
    return completed.stdout.decode("utf-8", errors="surrogateescape")


class GitDiscoveryProvider(BaseProvider):
    """Enumerates content a git index admits. ONE implementation of ``DiscoveryProvider``."""

    #: Above the filesystem provider, because tracked content is a stronger guarantee than
    #: whatever happens to be on disk. Expressed as a NUMBER rather than as a branch in the
    #: registry, so a future provider with better guarantees outranks this one without an edit.
    priority = 100

    def __init__(self, root: str) -> None:
        self.root = root

    # ------------------------------------------------------------------------- the contract

    def identifier(self) -> str:
        return IDENTIFIER

    def capabilities(self) -> CapabilitySet:
        return CAPABILITIES

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            identifier=IDENTIFIER,
            binding=self.root,
            mechanism="git ls-files --cached --exclude-standard",
            revision=self.revision(),
            details={
                "eligibility_boundary": "the git index, so untracked working-copy debris cannot "
                "change a verdict",
                "selector_default": "everything the index admits; Ω-1's '*.py' is now a caller "
                "supplied Selector rather than a hard-coded query",
            },
        )

    def collect(self, selector: Selector) -> Iterable[Artifact]:
        """Every tracked locator, as a universal Artifact. Ordering is ``BaseProvider``'s job."""
        revision = self.revision()
        for locator in self._tracked(selector):
            yield Artifact(
                identifier=f"{IDENTIFIER}:{locator}",
                location=Location(IDENTIFIER, locator, revision),
                metadata={"tracked": "true"},
            )

    # -------------------------------------------------------------------------- git specifics

    def _tracked(self, selector: Selector) -> tuple[str, ...]:
        """``git ls-files``, narrowed BY THE CALLER rather than by this module.

        The pattern is passed to git when the selector supplies one, so a narrow enumeration stays
        cheap; the result is filtered again by ``BaseProvider.enumerate`` because git's pathspec
        matching and ``fnmatch`` are not identical and the caller's selector is the authority.
        """
        arguments = [*_LS_FILES[1:], *selector.patterns]
        raw = _run(self.root, *arguments)
        return tuple(sorted(entry for entry in raw.split("\0") if entry))

    # ------------------------------------------------------------------- capability delivery
    #
    # ONE METHOD PER DECLARED CAPABILITY. Before these existed the provider declared five
    # capabilities and delivered one, so every caller needing a content hash, an owner or the
    # working tree went to git directly — and was then counted as bypassing an abstraction that
    # did not answer its question. `verify_capabilities` now refuses a declaration without a
    # delivery, which is what makes the count meaningful.

    def supply_working_tree_state(self, selector: Selector) -> dict[str, tuple[str, ...]]:
        """What the working copy holds that the recorded population does not.

        A DIFFERENT QUESTION from `--cached`, not a wider filter on it: a verdict that must not
        depend on local debris asks for tracked content, and a tool reporting what an operator has
        yet to commit asks for this.

        THE TWO HALVES ARE RETURNED SEPARATELY, AND THE FIRST DRAFT RETURNED ONLY ONE. This
        capability's declared description promises "additions not yet indexed, and modifications
        not yet recorded"; the first implementation ran `--others` alone and reported no
        modifications at all. A capability whose description claims more than its method delivers
        is the ENVELOPE_ONLY shape this package exists to measure, committed inside the package
        that measures it. Both halves are supplied now, KEYED RATHER THAN MERGED, because a caller
        needing the union can take it while one needing to know which half a path came from could
        not recover that from a merged set.
        """
        untracked = _run(
            self.root, "ls-files", "-z", "--others", "--exclude-standard", *selector.patterns
        )
        modified = _run(self.root, "ls-files", "-z", "-m", *selector.patterns)
        return {
            "untracked": tuple(sorted(e for e in untracked.split("\0") if e)),
            "modified": tuple(sorted(e for e in modified.split("\0") if e)),
        }

    def supply_revision_identity(
        self,
        selector: Selector,
        *,
        ref: str = "",
        diverged_from: str = "",
    ) -> dict[str, str | bool]:
        """Where this working copy stands, and how it names itself.

        The default answer carries the position facts a caller normally wants together, because
        four modules asked for two or three of them each and every one paid a separate process to
        get them. `ref` verifies that a named reference resolves; `diverged_from` reports where
        two references parted.

        EVERY FIELD IS ANSWERED OR EMPTY, NEVER ABSENT. A repository with no commits has no
        revision and no branch, and a caller must be able to tell "no revision" from "the provider
        declined to say" — which is the same reason `revision()` returns "" rather than raising.
        """
        if ref:
            try:
                _run(self.root, "rev-parse", "--verify", "--quiet", ref)
            except ProviderError:
                return {"ref": ref, "resolves": False}
            return {"ref": ref, "resolves": True}
        if diverged_from:
            try:
                base = _run(self.root, "merge-base", diverged_from, "HEAD").strip()
            except ProviderError:
                base = ""
            return {"diverged_from": diverged_from, "merge_base": base}

        def _ask(*arguments: str) -> str:
            try:
                return _run(self.root, *arguments).strip()
            except ProviderError:
                return ""

        return {
            "revision": self.revision(),
            "short": _ask("rev-parse", "--short", "HEAD"),
            "branch": _ask("rev-parse", "--abbrev-ref", "HEAD"),
            "upstream": _ask("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"),
            "is_work_tree": _ask("rev-parse", "--is-inside-work-tree") == "true",
        }

    def supply_change_set(
        self,
        selector: Selector,
        *,
        against: str = "HEAD",
        staged: bool = False,
        merge_base: bool = False,
    ) -> tuple[str, ...]:
        """Artifacts that DIFFER between a recorded point and the working copy or index.

        `against` names the point, `staged` asks the index rather than the working copy, and
        `merge_base` compares from where the branches diverged rather than from the tip — the
        three shapes the impact selector and the freeze stage between them actually ask for.

        `-z` throughout, so a path carrying a byte that is not valid UTF-8 arrives as itself
        rather than as an escaped rendering of itself. That is the same defect the change-set
        parser was corrected for once already: a quoted path matches no repository path at all.
        """
        target = f"{against}...HEAD" if merge_base else against
        arguments = ["diff", "--name-only", "-z"]
        if staged:
            arguments.append("--cached")
        arguments.append(target)
        raw = _run(self.root, *arguments, *selector.patterns)
        return tuple(sorted(entry for entry in raw.split("\0") if entry))

    def supply_revision_history(
        self, selector: Selector, *, limit: int = 0, refs: bool = False
    ) -> tuple[tuple[str, str], ...]:
        """The recorded revisions, or the named lines of development that reach them.

        Returned as (identifier, subject) pairs so a caller never parses a format string of its
        own; the separator stays inside this method, which is the point of asking a provider.
        """
        if refs:
            raw = _run(self.root, "for-each-ref", "--format=%(refname:short)")
            return tuple(sorted((name.strip(), "") for name in raw.splitlines() if name.strip()))
        arguments = ["log", "--format=%H%x1f%s"]
        if limit:
            arguments.insert(1, f"-{int(limit)}")
        raw = _run(self.root, *arguments)
        out = []
        for line in raw.splitlines():
            identifier, _, subject = line.partition("\x1f")
            if identifier:
                out.append((identifier, subject))
        return tuple(out)

    def supply_revision_metadata(
        self, selector: Selector, *, revision: str = "HEAD"
    ) -> dict[str, str]:
        """What a recorded revision carries: when it was made, and what it was called."""
        try:
            raw = _run(self.root, "show", "-s", "--format=%cI%x1f%s", revision).strip()
        except ProviderError:
            return {}
        committed, _, subject = raw.partition("\x1f")
        return {"revision": revision, "committed_at": committed, "subject": subject}

    def supply_content_hashing(self, selector: Selector) -> dict[str, str]:
        """Each tracked path mapped to the blob hash the index records for it.

        Read from `ls-files -s`, which is what the index already holds, rather than by reading and
        hashing the bytes: the index's answer is the one every other git-derived verdict rests on,
        and computing a second one would be a rival answer to a question already settled.
        """
        raw = _run(self.root, "ls-files", "-s", "-z", *selector.patterns)
        out: dict[str, str] = {}
        for entry in raw.split("\0"):
            if not entry:
                continue
            meta, _, path = entry.partition("\t")
            parts = meta.split()
            if len(parts) >= 2 and path:
                out[path] = parts[1]
        return out

    def supply_authority_metadata(self, selector: Selector) -> dict[str, str]:
        """The last committer of each selected path — the ownership fact git actually carries.

        The module docstring says this provider "declares that git CAN supply ownership facts, and
        exposes them on request". Until now there was no request to make. This is that request,
        and it stays a FACT rather than a derivation: who last touched a path is not who owns it,
        and the authority derivation consults this instead of inferring from structure.
        """
        owners: dict[str, str] = {}
        for path in self._tracked(selector):
            try:
                owners[path] = _run(self.root, "log", "-1", "--format=%an", "--", path).strip()
            except ProviderError:  # pragma: no cover - a path with no history
                owners[path] = ""
        return owners

    def supply_versioned_content(self, selector: Selector) -> str:
        """The revision the enumeration is reproducible against."""
        return self.revision()

    def supply_local_storage(self, selector: Selector) -> str:
        """Where the bytes are, on this machine, with no network call."""
        return str(self.root)

    def revision(self) -> str:
        """The committed revision, or "" in a repository with no commits yet.

        EMPTY IS HONEST. A fresh ``git init`` has no HEAD, and inventing an identifier for it would
        make an unreproducible enumeration look reproducible — the same defect as reporting 100%
        coverage over an empty denominator.
        """
        try:
            return _run(self.root, "rev-parse", "HEAD").strip()
        except ProviderError:
            return ""

    def content_hash(self, locator: str) -> str:
        """The index's own object id for a locator. Requires ``CONTENT_HASHING``, and asks first.

        ``require`` is called even though this class declares the capability unconditionally, and
        that is not ceremony: it is the pattern every provider method that depends on a capability
        must follow, and a method that skipped it would be the template someone copies.
        """
        self.require(CONTENT_HASHING)
        raw = _run(self.root, "rev-parse", f"HEAD:{locator}").strip()
        if not raw:
            raise ProviderError(f"git resolved no object for {locator!r} at HEAD")
        return raw

    def authority_metadata(self, locator: str) -> dict[str, str]:
        """Ownership facts git already holds. Requires ``AUTHORITY_METADATA``.

        ON DEMAND, NEVER DURING ENUMERATION. One ``git log`` per artifact would make enumerating a
        large repository cost thousands of subprocesses — so the capability declares that these
        facts are AVAILABLE, not that they are eagerly collected. A capability is a promise about
        what can be asked, not about what has already been paid for.
        """
        self.require(AUTHORITY_METADATA)
        raw = _run(self.root, "log", "-1", "--format=%an%x00%ae", "--", locator)
        parts = raw.strip().split("\0")
        if len(parts) != 2 or not parts[0]:
            return {}
        return {"last_author_name": parts[0], "last_author_email": parts[1]}


def available(root: str) -> bool:
    """Whether this provider can serve ``root`` at all.

    THE QUESTION Ω-1 CANNOT ASK. ``discovery.tracked_python`` raises when git is absent, because it
    has no notion of a provider being unavailable — there is nothing else it could do. A registry
    that must choose between providers needs a probe that answers rather than raises, and this is
    it: a directory with no git available, or no repository, is not an error here. It is a fact that
    makes the filesystem provider the resolution.
    """
    if not os.path.isdir(root):
        return False
    try:
        return _run(root, "rev-parse", "--is-inside-work-tree").strip() == "true"
    except ProviderError:
        return False

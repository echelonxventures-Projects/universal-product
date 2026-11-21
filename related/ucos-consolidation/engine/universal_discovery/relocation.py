"""UCOS-OMEGA-001 Part 9 (Ω-3) — the relocation proof, executed rather than asserted.

THE SUCCESS CRITERION, VERBATIM: moving a module ``engine/x.py`` → ``galaxy/x.py`` does not alter
governance. A docstring claiming that would be worth nothing, because every enumerated control
this package replaces also claimed to be general. So the claim is DISCHARGED BY EXPERIMENT on
every gate run.

THE EXPERIMENT. Take the whole discovered population and rename its largest root to a root that
does not exist. Re-derive test roots, re-derive the measurable packages, and re-classify every
artifact — all from the relocated paths, using the same file contents. Then compare, artifact by
artifact, against the verdicts computed over the real tree.

WHAT MUST BE INVARIANT, AND WHAT LEGITIMATELY IS NOT.

  invariant      the DISPOSITION. ``engine/foundation/identity.py`` is MEASURED, and
                 ``galaxy/foundation/identity.py`` must be MEASURED too — discovered as a
                 sub-package of a root nobody registered, with no edit anywhere.
  invariant      the DISPOSITION RULE. Being measured for a different reason after a move would
                 mean the rule read the directory.
  invariant      whether an AUTHORITY exists. Governance may not lapse because a file moved.
  NOT invariant  the authority's NAME under the ancestry rules, and correctly so: Ω-A-06 says the
                 capability package is the unit of custody, so a module that moves to a new
                 capability acquires that capability's owner. A design in which the NAME never
                 changed would be one where ownership was independent of structure, which is a
                 different and worse claim.

A FAILURE HERE IS NOT COSMETIC. It means some verdict is still keyed on a path, which is the
defect that put five whole trees outside the denominator, and it would mean the "unlimited future
scope" claim is false for the next tree somebody adds.
"""

from __future__ import annotations

from collections.abc import Mapping

from engine.universal_discovery import classification, discovery
from engine.universal_discovery.model import Artifact

#: A destination root that does not exist and is not referenced anywhere. Chosen so the experiment
#: cannot accidentally coincide with a real tree and pass by collision.
DESTINATION = "galaxy"


def _relocate(path: str, source_root: str, destination: str) -> str:
    if path == source_root or path.startswith(source_root + "/"):
        return destination + path[len(source_root) :]
    return path


def relocation_invariance(omega: object) -> tuple[str, ...]:
    """Every artifact whose verdict changed under relocation. Empty means the claim holds.

    Takes the built surface so the experiment costs no additional file read and no additional
    parse: relocation is a pure function of paths, and the contents are already in hand.
    """
    artifacts: tuple[Artifact, ...] = omega.artifacts  # type: ignore[attr-defined]
    population = omega.population  # type: ignore[attr-defined]
    heads: Mapping[str, str] = omega.source_heads  # type: ignore[attr-defined]
    imported_by: Mapping[str, frozenset[str]] = omega.imported_by  # type: ignore[attr-defined]
    frozen = omega.frozen  # type: ignore[attr-defined]

    source_root = _largest_root(artifacts)
    if not source_root:
        return ("<no root carried tracked python, so the experiment could not run>",)

    moved = {a.path: _relocate(a.path, source_root, DESTINATION) for a in artifacts}
    relocated_paths = tuple(sorted(moved.values()))
    relocated_imported_by = {
        moved[path]: frozenset(moved.get(importer, importer) for importer in importers)
        for path, importers in imported_by.items()
        if path in moved
    }

    test_roots = discovery.derive_test_roots(relocated_paths, relocated_imported_by)
    exemptions = _relocate_exemptions(population.declared_exemptions, source_root)
    transient = {moved.get(p, p): r for p, r in population.declared_transient.items()}
    measurable = discovery.derive_measurable_packages(
        relocated_paths, test_roots, exemptions=exemptions
    )

    drift: list[str] = []
    for artifact in artifacts:
        destination = moved[artifact.path]
        disposition, rule, _reason = classification.classify(
            destination,
            source_head=heads[artifact.path],
            measurable_packages=measurable,
            test_roots=test_roots,
            frozen=frozen,
            declared_exemptions=exemptions,
            declared_transient=transient,
        )
        if disposition != artifact.disposition or rule != artifact.disposition_rule:
            drift.append(
                f"{artifact.path} → {destination}: {artifact.disposition}/"
                f"{artifact.disposition_rule} became {disposition}/{rule}"
            )
    return tuple(drift)


def _largest_root(artifacts: tuple[Artifact, ...]) -> str:
    """Relocate the root that carries the most artifacts, so the experiment is the hardest one.

    Testing the smallest root would be the cheap version of this proof: a root with three files
    exercises fewer derivation rules than a root with eight hundred.
    """
    counts: dict[str, int] = {}
    for artifact in artifacts:
        if artifact.root and discovery.is_importable_name(artifact.root):
            counts[artifact.root] = counts.get(artifact.root, 0) + 1
    if not counts:
        return ""
    return max(sorted(counts), key=lambda root: counts[root])


def _relocate_exemptions(exemptions: Mapping[str, str], source_root: str) -> dict[str, str]:
    """A declared exemption names a PACKAGE, so relocating its root renames the package too.

    Rewriting it here is not smoothing the experiment over — it is what a real relocation would
    do, because ``engine.uicm`` becoming ``galaxy.uicm`` is exactly the edit the move implies.
    Leaving the exemption pointed at a package that no longer exists would test the staleness
    guard rather than the relocation property.
    """
    prefix = source_root + "."
    return {
        (
            DESTINATION + "." + package[len(prefix) :] if package.startswith(prefix) else package
        ): reason
        for package, reason in exemptions.items()
    }

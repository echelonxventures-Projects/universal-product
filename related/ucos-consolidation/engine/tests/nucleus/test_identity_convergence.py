"""UCOS-NUC-001 — identity inside this layer is minted by one authority, and it is measured.

Identity convergence is *not* the claim that one identifier format exists. Several formats
legitimately coexist, because several distinct populations exist: meta-types are minted by
:mod:`engine.kernel.identity`, knowledge objects by :mod:`engine.uckp.identity`, registered
artifacts by :mod:`engine.registry.universal.identity`, and the engineering pipeline mints
``ENGINEERING-EXECUTION-ONLY`` runtime, execution and compilation ids that are explicitly
non-authoritative. Formatting, rendering, hashing and UUID derivation are implementation
details, not authority.

Duplication is narrower and is what this file measures: a generator minting an identifier
**inside a population another authority owns, without delegating to it**. Two such
violations existed in this layer and were removed —
:attr:`~engine.nucleus.model.OwnershipAssignment.assignment_id` (``RELATIONSHIP``) and
:attr:`~engine.nucleus.certification.Certificate.certificate_id` (``CERTIFICATION``). Both
assembled a ``UCOS-`` identifier inline, producing ids the registration authority *accepts*
as its own — ``is_well_formed`` returned true and ``parse_kind_name`` named the kind — that
it had nevertheless never minted. The registry CLI mints genuine ids into both spaces, so
the populations overlapped and disagreement was possible.

The decisive test is :func:`test_no_module_mints_into_the_registry_namespace_inline`, which
walks the AST of :mod:`engine.nucleus` and fails if any module builds a ``UCOS-`` prefixed
identifier by concatenation or interpolation instead of calling ``deterministic_id``.
"""

from __future__ import annotations

import ast
from pathlib import Path

from engine.nucleus.certification import CERTIFICATE_NAMESPACE, certify
from engine.nucleus.law import StructuralRole
from engine.nucleus.model import ASSIGNMENT_NAMESPACE, OwnershipAssignment
from engine.nucleus.registry import build_seed_registry
from engine.registry.universal.identity import (
    ID_PREFIX,
    RegistryKind,
    deterministic_id,
    is_well_formed,
    parse_kind_name,
)
from engine.uckp.canonical import content_hash

NUCLEUS_PACKAGE = Path(__file__).resolve().parents[2] / "nucleus"

#: The prefix owned by the registration authority. Carrying it is *not* by itself a
#: violation — ownership is per population, and a population is identified by the kind
#: code, not by the prefix.
OWNED_PREFIX = f"{ID_PREFIX}-"


def _owns_population(literal: str) -> bool:
    """True iff the authority owns the population the literal's kind code names.

    This is the decision-ownership test, and it is why ``"UCOS-EVO-"`` is not flagged
    while ``"UCOS-REL-"`` is: ``REL`` is a registered kind code, so the authority owns
    that population and an inline mint there can disagree with it. ``EVO`` is registered
    nowhere, so the authority owns nothing to disagree with, and ``evolution_id`` is a
    distinct population rather than an intrusion into this one. Classifying by prefix
    alone would wrongly condemn it.
    """
    if not literal.startswith(OWNED_PREFIX):
        return False
    code = literal[len(OWNED_PREFIX) :].split("-", 1)[0]
    try:
        parse_kind_name(f"{ID_PREFIX}-{code}-0123456789ab")
    except Exception:
        return False
    return True


def _inline_owned_identifier_sites(tree: ast.AST) -> list[int]:
    """Line numbers where an identifier is assembled inside an owned population.

    Two shapes are matched, because both were used in the removed violations: string
    concatenation (``"UCOS-REL-" + digest``) and f-string interpolation
    (``f"UCOS-CERT-{digest}"``). A bare literal that is not combined with anything is left
    alone — that is a constant or prose, not a mint.
    """
    found: list[int] = []
    for node in ast.walk(tree):
        # "UCOS-<OWNED>-…" + something
        if (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Add)
            and isinstance(node.left, ast.Constant)
            and isinstance(node.left.value, str)
            and _owns_population(node.left.value)
        ):
            found.append(node.lineno)
        # f"UCOS-<OWNED>-…{…}"
        elif isinstance(node, ast.JoinedStr):
            head = node.values[0] if node.values else None
            if (
                isinstance(head, ast.Constant)
                and isinstance(head.value, str)
                and _owns_population(head.value)
                and any(isinstance(v, ast.FormattedValue) for v in node.values)
            ):
                found.append(node.lineno)
    return found


def test_the_detector_catches_both_removed_violations():
    """Calibration: the two retired inline mints are still detected, verbatim in shape."""
    retired_relationship = '"UCOS-REL-" + content_digest([a, b])[:12]'
    retired_certification = '"UCOS-CERT-" + content_hash([a, b])[:12]'
    interpolated = 'f"UCOS-CERT-{blueprint_id}-{digest}"'
    for source in (retired_relationship, retired_certification, interpolated):
        assert _inline_owned_identifier_sites(ast.parse(source)), source


def test_the_detector_ignores_constants_and_prose():
    """A prefix constant or a docstring mention is not a mint and must not be flagged."""
    assert _inline_owned_identifier_sites(ast.parse('CERT_ID_PREFIX = "UCOS-CERT-"')) == []
    assert _inline_owned_identifier_sites(ast.parse('x = "UCOS-REL- is owned elsewhere"')) == []


def test_the_detector_ignores_populations_the_authority_does_not_own():
    """``evolution_id`` mints under an unregistered code, so there is no owner to defy."""
    assert _inline_owned_identifier_sites(ast.parse('"UCOS-EVO-" + content_hash([a])[:12]')) == []
    assert not _owns_population("UCOS-EVO-")
    assert _owns_population("UCOS-REL-")
    assert _owns_population("UCOS-CERT-")


def test_the_evolution_population_stays_unclaimed_by_the_authority():
    """A guard, not a preference: this is what keeps ``evolution_id`` lawful.

    ``engine.nucleus.evolution`` mints ``UCOS-EVO-<12hex>`` itself. That is a separate
    population today only because no kind is registered under the code ``EVO``. If one ever
    were, those identifiers would retroactively parse as registered ids of a population
    they do not own — the exact retroactive reinterpretation the authority's own
    ``register_kind`` refuses for codes. Should this test fail, the fix is to make
    ``evolution_id`` delegate, not to relax the assertion.
    """
    assert not is_well_formed("UCOS-EVO-088bd1337123")
    assert not _owns_population("UCOS-EVO-")


def test_no_module_mints_into_the_registry_namespace_inline():
    """The decisive test: every identifier in this layer is minted by the authority."""
    offenders: dict[str, list[int]] = {}
    for path in sorted(NUCLEUS_PACKAGE.glob("*.py")):
        lines = _inline_owned_identifier_sites(ast.parse(path.read_text(encoding="utf-8")))
        if lines:
            offenders[path.name] = lines
    assert offenders == {}, f"identifier minted without delegating to the authority: {offenders}"


def test_the_relationship_identity_is_minted_by_the_authority():
    """``assignment_id`` reproduces exactly what the authority mints for its natural key."""
    assignment = OwnershipAssignment(
        capability_id="UCOS-CAP-000000000001",
        capability_key="payment.authorize",
        owner_id="UCOS-NUC-000000000001",
        owner_key="payment",
        owner_role=StructuralRole.NUCLEUS,
        authority="SEED",
    )
    expected = deterministic_id(
        RegistryKind.RELATIONSHIP,
        ASSIGNMENT_NAMESPACE,
        content_hash(["UCOS-CAP-000000000001", "UCOS-NUC-000000000001", "SEED", ""]),
    )
    assert assignment.assignment_id == expected
    assert is_well_formed(assignment.assignment_id)
    assert parse_kind_name(assignment.assignment_id) == RegistryKind.RELATIONSHIP.value


def test_the_certification_identity_is_minted_by_the_authority():
    """``certificate_id`` is an id the authority both accepts and could have minted."""
    certificate = certify(build_seed_registry())
    expected = deterministic_id(
        RegistryKind.CERTIFICATION,
        CERTIFICATE_NAMESPACE,
        content_hash(
            [
                certificate.subject,
                certificate.verdict.value,
                certificate.validation_digest,
                certificate.registry_digest,
                certificate.context_digest,
            ]
        ),
    )
    assert certificate.certificate_id == expected
    assert is_well_formed(certificate.certificate_id)
    assert parse_kind_name(certificate.certificate_id) == RegistryKind.CERTIFICATION.value


def test_delegated_identities_stay_deterministic_across_independent_derivations():
    """Delegation must not have cost determinism — replay depends on it."""
    first = certify(build_seed_registry())
    second = certify(build_seed_registry())
    assert first.certificate_id == second.certificate_id


def test_the_engineering_populations_stay_outside_the_registry_namespace():
    """Guard the separation that makes those populations specializations, not violations.

    ``ENGINEERING-EXECUTION-ONLY`` ids carry more segments than the authority's grammar
    admits, so they cannot be mistaken for registered identities. If a future change made
    one of these parse as a registry id, it would silently enter a population it does not
    own, and this test is what refuses that.
    """
    engineering_ids = (
        "UCOS-RUN-BP-DATA-0001-0123456789abcdef",
        "UCOS-CMP-BP-DATA-0001-5cdc24681ea75f46",
        "UCOS-EXEC-RUN-0123456789abcdef",
        "UCOS-ORCHESTRATION-0123456789abcdef",
        "UCOS-COMPOSITION-0123456789abcdef",
        "UCOS-CERT-BP-DATA-0001-0123456789abcdef",
    )
    for identifier in engineering_ids:
        assert not is_well_formed(identifier), identifier


def test_the_engineering_layers_cannot_reach_the_registration_authority():
    """Separation proven structurally: no import, so no possibility of an inline mint.

    Stronger than measuring today's identifier shapes — a layer that cannot import the
    authority cannot mint into its space by accident tomorrow either.
    """
    repo_root = NUCLEUS_PACKAGE.parent.parent
    for package in ("runtime", "compiler"):
        for path in (repo_root / "engine" / package).rglob("*.py"):
            if "test" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            assert "registry.universal.identity" not in source, path
            assert "deterministic_id" not in source, path

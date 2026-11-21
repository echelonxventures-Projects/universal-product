"""UCOS-NUC-001 — classification has exactly one authority, and it is measured.

Two authorities over one question is the failure the Single Authority Principle names.
Ownership-faculty convergence is proven in ``test_ownership_authority.py``; this file
proves the same property for *classification*: the rule that turns a subject's own
content into a structural role exists exactly once, string coercion has exactly one
path, and the legacy enum vocabulary never exceeds the registered CEU one.

All three are **measured** — over the package source, over the seeded registry, and over
the CEU catalogue — rather than asserted in prose. The decisive test is
:func:`test_the_classification_rule_has_exactly_one_implementation`: it walks the AST of
every module in :mod:`engine.nucleus` and fails if any module other than the canonical
one *produces* a :class:`StructuralRole` value from a conditional. Producing a role from a
branch is what classification is; merely testing a role, to pick a typed refusal or build
a lookup key, is reporting and is not flagged. Detecting the shape structurally rather
than by regex means reformatting cannot hide a reintroduced duplicate, and the detector
is itself calibrated against the exact rule that was removed to achieve convergence.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from engine.nucleus import authority
from engine.nucleus.errors import StructuralValidationError
from engine.nucleus.law import StructuralRole
from engine.nucleus.model import Classifiable, SubjectDeclaration, derive_role
from engine.nucleus.ownership import enforce
from engine.nucleus.registry import build_seed_registry

#: The package the classification rule is permitted to live in, and the one module in it
#: that may express the rule. Declared, so a classifier appearing anywhere else fails.
NUCLEUS_PACKAGE = Path(__file__).resolve().parents[2] / "nucleus"
CANONICAL_CLASSIFIER = "model.py"

ROLE_MEMBERS = {role.name for role in StructuralRole}


def _is_role_literal(node: ast.AST) -> bool:
    """True iff ``node`` is a ``StructuralRole.MEMBER`` expression."""
    return (
        isinstance(node, ast.Attribute)
        and node.attr in ROLE_MEMBERS
        and isinstance(node.value, ast.Name)
        and node.value.id == "StructuralRole"
    )


def _produces_role(node: ast.AST) -> bool:
    """True iff evaluating ``node`` yields a role, following nested conditionals.

    A conditional expression counts if either arm is a role or is itself role-producing,
    which is what makes the chained ``A if p else B if q else C`` form detectable.
    """
    if _is_role_literal(node):
        return True
    if isinstance(node, ast.IfExp):
        return _produces_role(node.body) or _produces_role(node.orelse)
    return False


def _role_valued_conditionals(tree: ast.AST) -> list[int]:
    """Line numbers of conditionals that *produce* a ``StructuralRole`` value.

    Producing a role from a branch is what classification *is*, whatever the surrounding
    code is named, so that is the shape matched here. Deliberately narrower than "mentions
    a role": a conditional that merely *tests* a role — to pick which typed refusal to
    raise, or to build a registry lookup key — has already had its decision made
    elsewhere and is reporting, not adjudicating. Matched on AST shape rather than by
    regex so neither reformatting nor renaming can conceal a second copy.
    """
    found: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.IfExp):
            if _produces_role(node):
                found.append(node.lineno)
        elif isinstance(node, ast.If):
            for branch in (*node.body, *node.orelse):
                returns = (
                    inner
                    for inner in ast.walk(branch)
                    if isinstance(inner, ast.Return | ast.Assign | ast.AnnAssign)
                )
                if any(r.value is not None and _produces_role(r.value) for r in returns):
                    found.append(node.lineno)
                    break
    return found


def test_the_nucleus_package_is_where_we_think_it_is():
    """Guard the path arithmetic, so the decisive test cannot pass by scanning nothing."""
    assert (NUCLEUS_PACKAGE / CANONICAL_CLASSIFIER).is_file()
    assert len(list(NUCLEUS_PACKAGE.glob("*.py"))) > 5


#: The duplicate classification rule that lived in ``ownership.py`` before convergence,
#: verbatim. Kept as the detector's own fixture: a duplication check that cannot detect
#: the duplication it was built to remove would pass forever while proving nothing.
RETIRED_DUPLICATE = """
derived = (
    StructuralRole.COMPOSITION
    if subject.composes
    else StructuralRole.NUCLEUS
    if subject.concept
    else StructuralRole.LAYER
)
"""

#: The two shapes that mention a role without classifying, taken from ``registry.py``.
#: They must NOT be flagged, or the check would force the typed refusals to be deleted.
LAWFUL_ROLE_MENTIONS = """
if (StructuralRole.COMPOSITION.value, domain) in self._subjects:
    raise OwnershipViolation("no capability may be specific to a composition")
if owner.role is StructuralRole.LAYER:
    raise LayerOwnershipViolation("layers own nothing")
"""


def test_the_detector_catches_the_duplicate_it_was_built_to_remove():
    """Calibration: the retired inline rule is still detected as a second authority."""
    assert _role_valued_conditionals(ast.parse(RETIRED_DUPLICATE))


def test_the_detector_catches_a_returning_duplicate():
    """The statement form of the rule is caught as well as the expression form."""
    disguised = (
        "def looks_innocent(x):\n"
        "    if x.composes:\n"
        "        return StructuralRole.COMPOSITION\n"
        "    return StructuralRole.LAYER\n"
    )
    assert _role_valued_conditionals(ast.parse(disguised))


def test_the_detector_does_not_flag_testing_a_role():
    """Reporting and lookup are not classification, so they must survive the check."""
    assert _role_valued_conditionals(ast.parse(LAWFUL_ROLE_MENTIONS)) == []


def test_the_canonical_classifier_is_itself_detected():
    """Proof the scan is pointed at real code: the one rule is found in the one module."""
    source = (NUCLEUS_PACKAGE / CANONICAL_CLASSIFIER).read_text(encoding="utf-8")
    assert _role_valued_conditionals(ast.parse(source))


def test_the_classification_rule_has_exactly_one_implementation():
    """The decisive test: no module but the canonical one may classify."""
    offenders: dict[str, list[int]] = {}
    for path in sorted(NUCLEUS_PACKAGE.glob("*.py")):
        if path.name == CANONICAL_CLASSIFIER:
            continue
        lines = _role_valued_conditionals(ast.parse(path.read_text(encoding="utf-8")))
        if lines:
            offenders[path.name] = lines
    assert offenders == {}, f"second classification authority found: {offenders}"


def test_the_canonical_classifier_is_total_and_has_no_default():
    """One rule, three reachable branches, every one derived from the subject's content."""
    assert (
        derive_role(SubjectDeclaration(key="commerce", title="Commerce", composes=("payment",)))
        is StructuralRole.COMPOSITION
    )
    assert (
        derive_role(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
        is StructuralRole.NUCLEUS
    )
    assert derive_role(SubjectDeclaration(key="platform", title="Platform")) is StructuralRole.LAYER


def test_both_declaration_and_record_satisfy_the_one_classifiable_surface():
    """The protocol is what lets one rule serve both holders of the classification facts."""
    registry = build_seed_registry()
    declaration = SubjectDeclaration(key="payment", title="Payment", concept="payment")
    assert isinstance(declaration, Classifiable)
    for subject in registry.subjects():
        assert isinstance(subject, Classifiable)


def test_the_ownership_gate_classifies_through_the_canonical_rule():
    """The gate measures agreement with the one rule, over records not declarations."""
    registry = build_seed_registry()
    for subject in registry.subjects():
        assert derive_role(subject) is subject.role
    report = enforce(registry)
    assert report.status == "PASS"
    assert report.measurements["NUC-INV-05"] == 0


@pytest.mark.parametrize("role", list(StructuralRole))
def test_the_projection_never_exceeds_the_registered_vocabulary(role: StructuralRole):
    """A projected role the CEU registry does not register would be invented in code."""
    assert role.value in authority.registered_roles()


@pytest.mark.parametrize("role", list(StructuralRole))
def test_the_projection_agrees_with_the_authority_on_both_faculties(role: StructuralRole):
    """The enum reports what the registry grants — the mark of a projection."""
    assert role.may_own_capability is authority.may_own_capability(role)
    assert role.may_select_nuclei is authority.may_select_units(role)


def test_string_coercion_has_one_authority_and_fails_closed():
    """``StructuralRole.coerce`` is the only string->role path, and invents nothing."""
    assert StructuralRole.coerce("nucleus") is StructuralRole.NUCLEUS
    assert StructuralRole.coerce(StructuralRole.LAYER) is StructuralRole.LAYER
    for value in ("dragon", "", "NUCLEUS", None, 7):
        with pytest.raises(StructuralValidationError):
            StructuralRole.coerce(value)


def test_coercion_round_trips_every_projected_role():
    """Totality of coercion over its own vocabulary, so no member is unreachable."""
    for role in StructuralRole:
        assert StructuralRole.coerce(role.value) is role
    assert set(StructuralRole.values()) == {r.value for r in StructuralRole}

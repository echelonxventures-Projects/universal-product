"""UCOS-EPIC-014 — Universal Assurance error-taxonomy tests.

The taxonomy makes four claims that the rest of the cluster relies on and that nothing
else checks: every error is **rooted** in the certified EC-1 foundation rather than
forking it, every error carries a **stable, unique, category-prefixed code**, the
``context`` is **structured and machine-consumable** rather than embedded in prose, and
the exported surface is **complete** — an error class that exists but is not exported
cannot be caught by name downstream.

Every property here is *derived by introspecting the module*, never restated from a
hard-coded list, so a thirteenth error class added tomorrow is measured by these tests
the moment it is authored instead of slipping in unexamined.
"""

from __future__ import annotations

import inspect
from platform.foundation.errors import PlatformError
from platform.universal_assurance import errors as errors_module
from platform.universal_assurance.errors import UniversalAssuranceError

import pytest

from engine.foundation.obs.errors import FoundationError

#: Every error class the module defines, discovered rather than enumerated.
DECLARED = tuple(
    sorted(
        (
            member
            for _, member in inspect.getmembers(errors_module, inspect.isclass)
            if issubclass(member, UniversalAssuranceError)
            and member.__module__ == errors_module.__name__
        ),
        key=lambda cls: cls.__name__,
    )
)

#: The subclasses only — the base carries the family code, not a category code.
CATEGORIES = tuple(cls for cls in DECLARED if cls is not UniversalAssuranceError)


def test_the_module_actually_declares_a_taxonomy():
    """A guard on the guards: if discovery finds nothing, every test below is vacuous."""
    assert len(CATEGORIES) >= 2


@pytest.mark.parametrize("error_cls", DECLARED, ids=lambda c: c.__name__)
def test_every_error_is_rooted_in_the_certified_foundation_not_a_fork(error_cls):
    assert issubclass(error_cls, UniversalAssuranceError)
    assert issubclass(error_cls, PlatformError)
    assert issubclass(error_cls, FoundationError)
    assert issubclass(error_cls, Exception)


@pytest.mark.parametrize("error_cls", CATEGORIES, ids=lambda c: c.__name__)
def test_every_category_derives_directly_from_the_family_base(error_cls):
    """A flat taxonomy: no category may be silently swallowed by catching a sibling."""
    assert error_cls.__bases__ == (UniversalAssuranceError,)


def test_the_family_base_derives_from_the_platform_base():
    assert UniversalAssuranceError.__bases__ == (PlatformError,)


@pytest.mark.parametrize("error_cls", DECLARED, ids=lambda c: c.__name__)
def test_every_error_declares_a_prefixed_non_inherited_code(error_cls):
    code = error_cls.__dict__.get("code")
    assert code is not None, f"{error_cls.__name__} inherits its code instead of owning one"
    assert isinstance(code, str) and code
    assert code.startswith("EC2-UASR-")


def test_every_code_is_unique_across_the_taxonomy():
    codes = [cls.code for cls in DECLARED]
    assert len(set(codes)) == len(codes), "two error categories share one code"


def test_the_family_base_carries_the_family_code_and_categories_do_not():
    assert UniversalAssuranceError.code == "EC2-UASR-000"
    for error_cls in CATEGORIES:
        assert error_cls.code != UniversalAssuranceError.code


@pytest.mark.parametrize("error_cls", DECLARED, ids=lambda c: c.__name__)
def test_every_error_is_documented(error_cls):
    """The docstring is what tells an operator which authoring fault they committed."""
    assert (error_cls.__doc__ or "").strip()


@pytest.mark.parametrize("error_cls", DECLARED, ids=lambda c: c.__name__)
def test_every_error_carries_structured_non_prose_context(error_cls):
    error = error_cls("something failed", section="policy", count=3, items=["a"])
    assert error.message == "something failed"
    assert error.context == {"section": "policy", "count": 3, "items": ["a"]}
    assert error.code == error_cls.code


@pytest.mark.parametrize("error_cls", DECLARED, ids=lambda c: c.__name__)
def test_every_error_renders_its_code_and_context_when_stringified(error_cls):
    rendered = str(error_cls("boom", subject="S-1"))
    assert error_cls.code in rendered
    assert "boom" in rendered
    assert "subject" in rendered


@pytest.mark.parametrize("error_cls", DECLARED, ids=lambda c: c.__name__)
def test_every_error_is_machine_consumable_as_a_dict(error_cls):
    payload = error_cls("boom", subject="S-1").to_dict()
    assert payload["code"] == error_cls.code
    assert payload["message"] == "boom"
    assert payload["context"] == {"subject": "S-1"}


@pytest.mark.parametrize("error_cls", DECLARED, ids=lambda c: c.__name__)
def test_an_error_with_no_context_is_still_well_formed(error_cls):
    error = error_cls("bare")
    assert error.context == {}
    assert error_cls.code in str(error)


@pytest.mark.parametrize("error_cls", CATEGORIES, ids=lambda c: c.__name__)
def test_catching_the_family_base_catches_every_category(error_cls):
    """One `except UniversalAssuranceError` must be a complete fail-closed boundary."""
    with pytest.raises(UniversalAssuranceError):
        raise error_cls("boom")


@pytest.mark.parametrize("error_cls", CATEGORIES, ids=lambda c: c.__name__)
def test_a_category_does_not_catch_its_siblings(error_cls):
    siblings = [cls for cls in CATEGORIES if cls is not error_cls]
    for sibling in siblings:
        assert not issubclass(sibling, error_cls)


# -- exported surface --------------------------------------------------------


def test_every_declared_error_is_exported():
    """An error class that is not exported cannot be caught by name downstream."""
    exported = set(errors_module.__all__)
    declared = {cls.__name__ for cls in DECLARED}
    assert declared - exported == set(), "declared but unexported error classes"


def test_nothing_is_exported_that_the_module_does_not_declare():
    for name in errors_module.__all__:
        assert hasattr(errors_module, name), f"__all__ names a missing attribute: {name}"


def test_the_export_list_has_no_duplicates():
    assert len(set(errors_module.__all__)) == len(errors_module.__all__)


def test_the_family_base_is_exported_first():
    """Readers meet the root of the taxonomy before its categories."""
    assert errors_module.__all__[0] == "UniversalAssuranceError"

"""Fixtures for the Validation Layer test suite.

Assembles a real runtime unit from a published compiler package (reusing the root
conftest ``published_package`` + ``runtime_signer`` fixtures) and projects it into
a validation subject, so the layer is exercised against a genuine generated
artifact — never a hand-built stand-in.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.runtime import assemble
from engine.validation.contracts import ValidationSubject


@pytest.fixture
def runtime_unit(published_package, runtime_signer):
    return assemble(published_package, verify_with=runtime_signer)


@pytest.fixture
def valid_subject(runtime_unit) -> ValidationSubject:
    return ValidationSubject.from_runtime_unit(runtime_unit, blueprint_class="BP-DATA")


def mutate(subject: ValidationSubject, **changes) -> ValidationSubject:
    """Return a copy of ``subject`` with fields replaced (for negative tests)."""
    return dataclasses.replace(subject, **changes)

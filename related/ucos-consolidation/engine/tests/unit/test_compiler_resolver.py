"""TASK-000021/000029 — Dependency Resolution Engine tests."""

from __future__ import annotations

import pytest

from engine.compiler.errors import CyclicDependencyError, DependencyError
from engine.compiler.parser import parse_document
from engine.compiler.resolver import DependencyResolver, ResolvedBuild


def test_resolve_single_blueprint(data_blueprint):
    ir = parse_document(data_blueprint)
    resolved = DependencyResolver().resolve([ir])
    assert isinstance(resolved, ResolvedBuild)
    assert resolved.order == ("BP-DATA-0001",)
    assert resolved.pinned_versions == {"BP-DATA-0001": "1.0.0"}
    assert len(resolved) == 1
    assert resolved.dependencies_of("BP-DATA-0001") == ()


def test_resolve_orders_dependencies_first(data_blueprint, dependency_blueprint):
    data_blueprint["dependencies"] = ["BP-DATA-0002"]
    a = parse_document(data_blueprint)
    b = parse_document(dependency_blueprint)
    resolved = DependencyResolver().resolve([a, b])
    assert resolved.order.index("BP-DATA-0002") < resolved.order.index("BP-DATA-0001")
    assert resolved.dependencies_of("BP-DATA-0001") == ("BP-DATA-0002",)


def test_resolve_rejects_duplicate_blueprint(data_blueprint):
    ir = parse_document(data_blueprint)
    with pytest.raises(DependencyError) as exc:
        DependencyResolver().resolve([ir, ir])
    assert "duplicate" in exc.value.message


def test_resolve_rejects_missing_dependency(data_blueprint):
    data_blueprint["dependencies"] = ["BP-DATA-9999"]
    ir = parse_document(data_blueprint)
    with pytest.raises(DependencyError) as exc:
        DependencyResolver().resolve([ir])
    assert exc.value.context["dependency"] == "BP-DATA-9999"


def test_resolve_fails_on_cycle(data_blueprint, dependency_blueprint):
    data_blueprint["dependencies"] = ["BP-DATA-0002"]
    dependency_blueprint["dependencies"] = ["BP-DATA-0001"]
    a = parse_document(data_blueprint)
    b = parse_document(dependency_blueprint)
    with pytest.raises(CyclicDependencyError):
        DependencyResolver().resolve([a, b])

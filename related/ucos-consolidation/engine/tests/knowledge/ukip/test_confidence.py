"""Tests for engine.knowledge.ukip.confidence (P4-F-003).

Coverage targets: confidence_declaration projects real source/provenance data,
bind_confidence registers through the real UCXI ContextRegistry, Context Once
refuses a silent overwrite, resupersede_confidence performs an explicit append-only
correction, and confidence_history reconstructs the full temporal series.
"""

from __future__ import annotations

import pytest

from engine.context.errors import DuplicateContextError
from engine.context.registry import ContextRegistry
from engine.knowledge.ukip.confidence import (
    CONFIDENCE_DIMENSION,
    bind_confidence,
    confidence_context_id,
    confidence_declaration,
    confidence_history,
    confidence_natural_key,
    confidence_of,
    resupersede_confidence,
)

from .conftest import make_unit, register


def _record(key: str = "conf-a", **overrides):
    unit = make_unit(key, **overrides)
    registry = register((unit,))
    return next(iter(registry.records()))


class TestConfidenceDeclaration:
    def test_projects_real_source_and_provenance(self) -> None:
        record = _record()
        declaration = confidence_declaration(record, confidence="high")
        values = declaration.value_mapping()
        ref = record.canonical_source
        assert values["source"] == f"{ref.provider_id}:{ref.locator}"
        assert values["provenance"] == record.provenance.seal
        assert values[CONFIDENCE_DIMENSION] == "high"

    def test_natural_key_binds_to_knowledge_id_and_version(self) -> None:
        record = _record()
        assert confidence_natural_key(record) == f"{record.knowledge_id}@{record.version}"

    def test_note_is_optional(self) -> None:
        record = _record()
        without_note = confidence_declaration(record, confidence="high")
        assert "note" not in without_note.value_mapping()
        with_note = confidence_declaration(record, confidence="high", note="reviewed")
        assert with_note.value_mapping()["note"] == "reviewed"


class TestBindConfidence:
    def test_binds_and_is_queryable(self) -> None:
        record = _record()
        registry = ContextRegistry()
        bind_confidence(registry, record, confidence="high")
        assert confidence_of(registry, record) == "high"

    def test_unbound_record_has_no_confidence(self) -> None:
        record = _record()
        registry = ContextRegistry()
        assert confidence_of(registry, record) is None

    def test_idempotent_reregistration_of_identical_confidence(self) -> None:
        record = _record()
        registry = ContextRegistry()
        first = bind_confidence(registry, record, confidence="high")
        second = bind_confidence(registry, record, confidence="high")
        assert first.context_id == second.context_id

    def test_different_confidence_for_same_version_is_refused(self) -> None:
        # Context Once (CXL-06): a correction must go through resupersede_confidence,
        # never a silent overwrite of the same (knowledge_id, version) identity.
        record = _record()
        registry = ContextRegistry()
        bind_confidence(registry, record, confidence="high")
        with pytest.raises(DuplicateContextError):
            bind_confidence(registry, record, confidence="low")

    def test_context_id_is_deterministic(self) -> None:
        record = _record()
        registry = ContextRegistry()
        bound = bind_confidence(registry, record, confidence="high")
        assert bound.context_id == confidence_context_id(record)


class TestResupersedeConfidence:
    def test_correction_retains_predecessor_and_activates_successor(self) -> None:
        record_v1 = _record("conf-b", version="1.0.0")
        registry = ContextRegistry()
        original = bind_confidence(registry, record_v1, confidence="low")

        record_v2 = _record("conf-b", version="2.0.0")
        corrected = resupersede_confidence(
            registry, original.context_id, record_v2, confidence="high"
        )

        assert confidence_of(registry, record_v2) == "high"
        # the predecessor is retained, not deleted (append-only)
        predecessor = registry.get(original.context_id)
        assert predecessor.lifecycle.value == "superseded"
        assert predecessor.dimension(CONFIDENCE_DIMENSION).value == "low"
        assert corrected.dimension(CONFIDENCE_DIMENSION).value == "high"

    def test_audit_chain_stays_intact_through_a_correction(self) -> None:
        record_v1 = _record("conf-c", version="1.0.0")
        registry = ContextRegistry()
        original = bind_confidence(registry, record_v1, confidence="low")
        record_v2 = _record("conf-c", version="2.0.0")
        resupersede_confidence(registry, original.context_id, record_v2, confidence="high")
        assert registry.verify_audit() == []


class TestConfidenceHistory:
    def test_reconstructs_the_full_series_in_registration_order(self) -> None:
        registry = ContextRegistry()
        v1 = _record("conf-d", version="1.0.0")
        first = bind_confidence(registry, v1, confidence="low")
        v2 = _record("conf-d", version="2.0.0")
        resupersede_confidence(registry, first.context_id, v2, confidence="medium")
        v3 = _record("conf-d", version="3.0.0")
        second = next(
            r for r in registry.by_kind("knowledge") if r.natural_key == confidence_natural_key(v2)
        )
        resupersede_confidence(registry, second.context_id, v3, confidence="high")

        history = confidence_history(registry, v1.knowledge_id)
        values = [h.dimension(CONFIDENCE_DIMENSION).value for h in history]
        assert values == ["low", "medium", "high"]

    def test_unrelated_subjects_do_not_leak_into_history(self) -> None:
        registry = ContextRegistry()
        a = _record("conf-e")
        bind_confidence(registry, a, confidence="high")
        b = _record("conf-eb")  # deliberately shares the "conf-e" prefix
        bind_confidence(registry, b, confidence="low")

        history = confidence_history(registry, a.knowledge_id)
        assert len(history) == 1
        assert history[0].dimension(CONFIDENCE_DIMENSION).value == "high"

    def test_empty_history_for_unknown_subject(self) -> None:
        registry = ContextRegistry()
        assert confidence_history(registry, "UKID-does-not-exist") == ()

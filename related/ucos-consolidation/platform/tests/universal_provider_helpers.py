"""Shared fixtures for the Universal Provider Architecture tests (Terminal-04).

The fixture providers here are deliberately *not* the Repository provider: the whole
claim of the architecture is that the framework is indifferent to which provider it
is handed, so the framework tests exercise an in-memory provider of an invented kind
that the framework has never heard of.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from platform.universal_provider.constitution import ProviderOperation
from platform.universal_provider.contracts import (
    ProviderCapability,
    ProviderDescriptor,
    ProviderQuery,
    ProviderResource,
)
from platform.universal_provider.sdk import (
    BaseProvider,
    declare_capability,
    declare_dependency,
    declare_provider,
)
from typing import Any

MEMO_PROVIDER_ID = "fixture.memo"
MEMO_KIND = "memo"
MEMO_RESOURCE_KIND = "memo.note"
MEMO_ENTRY_POINT = "platform.tests.universal_provider_helpers:build_memo"

#: The default in-memory substrate: id -> payload.
DEFAULT_NOTES: dict[str, dict[str, Any]] = {
    "note-a": {"title": "alpha", "tag": "red"},
    "note-b": {"title": "beta", "tag": "blue"},
    "note-c": {"title": "gamma", "tag": "red"},
}


def memo_capabilities() -> tuple[ProviderCapability, ...]:
    return (
        declare_capability(
            "memo.notes",
            ProviderOperation.QUERY,
            resource_kind=MEMO_RESOURCE_KIND,
            description="Enumerate notes.",
            selector_keys=("tag", "id_prefix"),
            deterministic=True,
            effects=("mem:read",),
        ),
        declare_capability(
            "memo.note",
            ProviderOperation.FETCH,
            resource_kind=MEMO_RESOURCE_KIND,
            description="Resolve one note.",
            deterministic=True,
            effects=("mem:read",),
        ),
        declare_capability(
            "memo.attestation",
            ProviderOperation.VERIFY,
            resource_kind=MEMO_RESOURCE_KIND,
            description="Attest one note.",
            deterministic=True,
            effects=("mem:read",),
        ),
    )


def memo_descriptor(
    *,
    provider_id: str = MEMO_PROVIDER_ID,
    version: str = "1.0.0",
    entry_point: str = MEMO_ENTRY_POINT,
    capabilities: tuple[ProviderCapability, ...] | None = None,
    dependencies: tuple[Any, ...] = (),
    kind: str = MEMO_KIND,
    source_of_record: str = "in-memory fixture substrate",
    authority: str = "TEST",
    name: str = "Memo Fixture Provider",
    metadata: Mapping[str, Any] | None = None,
) -> ProviderDescriptor:
    return declare_provider(
        provider_id,
        kind,
        version,
        name=name,
        authority=authority,
        description="An in-memory fixture provider of an invented kind.",
        source_of_record=source_of_record,
        entry_point=entry_point,
        capabilities=capabilities if capabilities is not None else memo_capabilities(),
        dependencies=dependencies,
        metadata=metadata,
    )


class MemoProvider(BaseProvider):
    """An in-memory provider. Everything constitutional comes from the SDK."""

    def __init__(
        self, descriptor: ProviderDescriptor, config: Mapping[str, Any] | None = None
    ) -> None:
        super().__init__(descriptor, config)
        notes = dict(config or {}).get("notes")
        self._notes: dict[str, dict[str, Any]] = (
            {str(k): dict(v) for k, v in notes.items()}
            if isinstance(notes, Mapping)
            else {k: dict(v) for k, v in DEFAULT_NOTES.items()}
        )

    def probe(self) -> dict[str, bool]:
        return {"substrate_loaded": bool(self._notes)}

    def resolve_query(
        self, capability: ProviderCapability, request: ProviderQuery
    ) -> Iterable[ProviderResource]:
        del capability
        tag = request.selector.get("tag")
        prefix = str(request.selector.get("id_prefix") or "")
        for note_id in reversed(sorted(self._notes)):  # unordered on purpose
            payload = self._notes[note_id]
            if tag is not None and payload.get("tag") != tag:
                continue
            if prefix and not note_id.startswith(prefix):
                continue
            yield self._note(note_id, payload)

    def resolve_resource(self, resource_id: str) -> ProviderResource | None:
        payload = self._notes.get(resource_id)
        return None if payload is None else self._note(resource_id, payload)

    def _note(self, note_id: str, payload: Mapping[str, Any]) -> ProviderResource:
        return self.resource(note_id, MEMO_RESOURCE_KIND, dict(payload))


class FaultyProvider(MemoProvider):
    """A provider whose substrate raises, to exercise PC-09 fault isolation."""

    def probe(self) -> dict[str, bool]:
        raise RuntimeError("probe exploded")

    def resolve_query(
        self, capability: ProviderCapability, request: ProviderQuery
    ) -> Iterable[ProviderResource]:
        raise RuntimeError("substrate exploded")


class DegradedProvider(MemoProvider):
    """A provider reporting a partially failing substrate."""

    def probe(self) -> dict[str, bool]:
        return {"substrate_loaded": True, "index_fresh": False}


def build_memo(
    descriptor: ProviderDescriptor, config: Mapping[str, Any] | None = None
) -> MemoProvider:
    """The fixture entry point resolved by discovery."""
    return MemoProvider(descriptor, config)


def build_faulty(
    descriptor: ProviderDescriptor, config: Mapping[str, Any] | None = None
) -> FaultyProvider:
    return FaultyProvider(descriptor, config)


def exploding_factory(
    descriptor: ProviderDescriptor, config: Mapping[str, Any] | None = None
) -> MemoProvider:
    """An entry point that raises during construction."""
    raise RuntimeError("construction exploded")


NOT_CALLABLE = "this is not callable"


def write_manifest(directory: Path, filename: str, payload: Any) -> Path:
    """Write a provider manifest into ``directory`` and return its path."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def memo_manifest(**overrides: Any) -> dict[str, Any]:
    """Return the fixture descriptor as a plain manifest mapping."""
    payload = memo_descriptor().to_dict()
    payload.update(overrides)
    return payload


__all__ = [
    "DEFAULT_NOTES",
    "MEMO_ENTRY_POINT",
    "MEMO_KIND",
    "MEMO_PROVIDER_ID",
    "MEMO_RESOURCE_KIND",
    "NOT_CALLABLE",
    "DegradedProvider",
    "FaultyProvider",
    "MemoProvider",
    "build_faulty",
    "build_memo",
    "declare_dependency",
    "exploding_factory",
    "memo_capabilities",
    "memo_descriptor",
    "memo_manifest",
    "write_manifest",
]

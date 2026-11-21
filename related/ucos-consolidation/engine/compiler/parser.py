"""TASK-000019 — Parse Engine (EPIC-003, IMP-007 §3 Parsing).

The parser is the compiler front-end: it admits a declarative blueprint document
(a mapping, or JSON text/bytes) into the intermediate representation
(:class:`BlueprintIR`, TASK-000017). Parsing is purely structural — it produces a
well-formed IR or fails with a :class:`ParseError`; **certification and registry
conformance are enforced downstream by the Validation Engine** (TASK-000020), per
the staged pipeline (IMP-007 §3).

The document shape is the canonical IR shape (TASK-000018), so the parser reuses
the serialization reconstruction and re-frames any failure as a parse-stage error,
keeping the stage boundary clean and the errors auditable.

Parsing invents nothing (TP-01): every field of the resulting IR is derived
directly from the document.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from engine.compiler.errors import ParseError, SerializationError
from engine.compiler.ir import BlueprintFamily, BlueprintIR
from engine.compiler.serialization import from_dict

#: Families the EPIC-003 compiler front-end admits for compilation.
#: The IR models every family, but EPIC-003 delivers BP-DATA end-to-end.
SUPPORTED_FAMILIES: frozenset[BlueprintFamily] = frozenset({BlueprintFamily.DATA})


def parse_document(document: Mapping[str, Any]) -> BlueprintIR:
    """Admit a blueprint mapping into a validated IR (structure only)."""
    if not isinstance(document, Mapping):
        raise ParseError("blueprint document must be an object", got=type(document).__name__)
    try:
        ir = from_dict(document)
    except SerializationError as exc:
        raise ParseError(
            "blueprint document could not be admitted into the IR",
            detail=exc.message,
            context=exc.context,
        ) from exc
    return ir


def parse_text(text: str) -> BlueprintIR:
    """Parse a JSON blueprint document from text into a validated IR."""
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParseError("blueprint document is not valid JSON", detail=str(exc)) from exc
    return parse_document(document)


def parse_bytes(data: bytes) -> BlueprintIR:
    """Parse a JSON blueprint document from UTF-8 bytes into a validated IR."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ParseError("blueprint document is not valid UTF-8", detail=str(exc)) from exc
    return parse_text(text)


def parse(source: Mapping[str, Any] | str | bytes) -> BlueprintIR:
    """Parse a blueprint from a mapping, JSON text, or UTF-8 bytes."""
    if isinstance(source, Mapping):
        return parse_document(source)
    if isinstance(source, bytes):
        return parse_bytes(source)
    if isinstance(source, str):
        return parse_text(source)
    raise ParseError("unsupported blueprint source type", got=type(source).__name__)


def is_supported(ir: BlueprintIR) -> bool:
    """True iff the parsed blueprint belongs to a family EPIC-003 compiles."""
    return ir.family in SUPPORTED_FAMILIES


def ensure_supported(ir: BlueprintIR) -> BlueprintIR:
    """Return ``ir`` if its family is compilable in EPIC-003, else raise.

    IMP-007 §2 — the compiler compiles only the registered families. EPIC-003
    scope is BP-DATA; other families parse into the IR but are not compilable here
    (no redesign; later epics add them).
    """
    if not is_supported(ir):
        raise ParseError(
            "blueprint family is not compilable in EPIC-003 (BP-DATA only)",
            blueprint_id=ir.blueprint_id,
            family=ir.family.value,
            supported=[f.value for f in sorted(SUPPORTED_FAMILIES, key=lambda x: x.value)],
        )
    return ir


__all__ = [
    "SUPPORTED_FAMILIES",
    "parse",
    "parse_document",
    "parse_text",
    "parse_bytes",
    "is_supported",
    "ensure_supported",
]

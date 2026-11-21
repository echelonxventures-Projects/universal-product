"""TASK-000017 — Universal Compiler data type system (EPIC-003).

A closed, deterministic mapping from the abstract attribute types declared by a
BP-DATA blueprint to concrete target representations (ANSI SQL column types and
Python type hints). The type set is *closed*: an attribute whose declared type is
not a member is rejected by the parser/validator (TP-01 — no invented behaviour).

The mapping is pure and stdlib-only (TP-04/TP-05); it invents no types and adds
no target semantics beyond the declared blueprint type.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.compiler.errors import CompilationError


class DataType(str, Enum):
    """The closed set of abstract attribute types a BP-DATA blueprint may declare."""

    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    BIGINT = "bigint"
    DECIMAL = "decimal"
    FLOAT = "float"
    BOOLEAN = "boolean"
    UUID = "uuid"
    DATE = "date"
    TIMESTAMP = "timestamp"
    JSON = "json"
    BYTES = "bytes"

    @classmethod
    def coerce(cls, value: object, *, context: str) -> DataType:
        """Return the enum member for ``value`` or raise (fail loud, no invention)."""
        try:
            return cls(str(value))
        except ValueError as exc:
            raise CompilationError(
                "unknown attribute data type",
                value=value,
                at=context,
                allowed=[member.value for member in cls],
            ) from exc


@dataclass(frozen=True, slots=True)
class TypeBinding:
    """The concrete target bindings for one abstract :class:`DataType`."""

    sql: str
    python: str


# The single source of truth for type lowering. Deterministic and closed.
_BINDINGS: dict[DataType, TypeBinding] = {
    DataType.STRING: TypeBinding(sql="VARCHAR", python="str"),
    DataType.TEXT: TypeBinding(sql="TEXT", python="str"),
    DataType.INTEGER: TypeBinding(sql="INTEGER", python="int"),
    DataType.BIGINT: TypeBinding(sql="BIGINT", python="int"),
    DataType.DECIMAL: TypeBinding(sql="DECIMAL", python="decimal.Decimal"),
    DataType.FLOAT: TypeBinding(sql="DOUBLE PRECISION", python="float"),
    DataType.BOOLEAN: TypeBinding(sql="BOOLEAN", python="bool"),
    DataType.UUID: TypeBinding(sql="UUID", python="uuid.UUID"),
    DataType.DATE: TypeBinding(sql="DATE", python="datetime.date"),
    DataType.TIMESTAMP: TypeBinding(sql="TIMESTAMP", python="datetime.datetime"),
    DataType.JSON: TypeBinding(sql="JSONB", python="dict"),
    DataType.BYTES: TypeBinding(sql="BYTEA", python="bytes"),
}

#: Types that accept an optional length parameter (rendered as ``TYPE(n)``).
_LENGTH_BEARING: frozenset[DataType] = frozenset({DataType.STRING})


def sql_type(data_type: DataType, *, max_length: int | None = None) -> str:
    """Return the ANSI SQL column type for ``data_type``.

    ``max_length`` is honoured only for length-bearing types (``string`` →
    ``VARCHAR(n)``); it is ignored for all others (deterministic lowering).
    """
    binding = _BINDINGS[data_type]
    if max_length is not None and data_type in _LENGTH_BEARING:
        return f"{binding.sql}({max_length})"
    return binding.sql


def python_type(data_type: DataType) -> str:
    """Return the Python type-hint string for ``data_type``."""
    return _BINDINGS[data_type].python


__all__ = ["DataType", "TypeBinding", "sql_type", "python_type"]

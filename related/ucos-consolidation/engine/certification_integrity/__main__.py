"""Dispatch ``python -m engine.certification_integrity`` to the gate."""

from __future__ import annotations

from engine.certification_integrity.gate import main

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

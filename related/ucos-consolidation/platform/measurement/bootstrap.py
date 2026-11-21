"""UCOS-EPIC-004 — Measurement bootstrap (UCOS-UMA-001).

Composes the Universal Measurement Engine over the **real Registry** Truth source and
returns a ready :class:`~platform.measurement.service.MeasurementService`. This is the
default production wiring used to measure the corpus on demand (e.g. after each Registry
mutation, mirroring the TRACK-001 recompute discipline). It creates no authority and no
Truth; it reads the authoritative ``00-BOOK`` substrate through the certified read-only
:class:`~engine.registry.adapter.RegistryAdapter` only.
"""

from __future__ import annotations

from pathlib import Path
from platform.measurement.service import MeasurementService, build_measurement_service
from platform.measurement.source import RegistryTruthSource

from engine.registry.adapter import RegistryAdapter


def bootstrap_measurement(data_dir: Path | str | None = None) -> MeasurementService:
    """Build the measurement service over the Registry Truth source (default wiring)."""
    adapter = RegistryAdapter.open(data_dir) if data_dir is not None else RegistryAdapter.open()
    return build_measurement_service(RegistryTruthSource(adapter))


__all__ = ["bootstrap_measurement"]

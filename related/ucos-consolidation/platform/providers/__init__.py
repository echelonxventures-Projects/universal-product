"""UCOS Ω∞ — Provider implementations and the provider catalog (Terminal-04).

This package sits **outside** the Universal Provider Architecture
(:mod:`platform.universal_provider`) by design. The framework must not know that any
particular provider exists, so provider implementations live here and reach the
framework only as **data**:

    * ``catalog/`` — JSON provider manifests. Discovery reads this directory; the
      framework has no compiled knowledge of its contents.
    * ``repository/`` — the Repository provider, the reference implementation. It is
      built on :class:`~platform.universal_provider.sdk.BaseProvider` and is reached
      exclusively through the ``entry_point`` string declared in its manifest.
    * ``TEMPLATE.provider.json`` — the copy-me manifest for a new provider. It is
      deliberately *not* inside ``catalog/`` so it is never discovered.

Onboarding a provider is therefore two acts, neither of which touches the framework:

    1. add a manifest to ``catalog/`` declaring identity, capabilities, and entry point;
    2. add a module exposing that entry point.

The framework's own gate ``PV-02-KIND-OPEN`` scans
:mod:`platform.universal_provider` for the provider under validation and fails if it
finds it — so this separation is enforced, not merely intended.
"""

from __future__ import annotations

from pathlib import Path

#: The provider catalog directory read by discovery.
CATALOG_DIR = Path(__file__).resolve().parent / "catalog"

#: The copy-me manifest for onboarding a new provider (outside the catalog).
TEMPLATE_MANIFEST = Path(__file__).resolve().parent / "TEMPLATE.provider.json"

__all__ = ["CATALOG_DIR", "TEMPLATE_MANIFEST"]

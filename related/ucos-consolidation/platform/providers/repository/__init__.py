"""UCOS Ω∞ — Repository Provider package (Terminal-04, Repository First).

The first provider realized against the Universal Provider Architecture, and the
reference every subsequent provider is written against. See
:mod:`platform.providers.repository.provider`.
"""

from __future__ import annotations

from platform.providers.repository.provider import (
    ARTIFACT_KIND,
    REPOSITORY_PROVIDER_ID,
    REPOSITORY_PROVIDER_KIND,
    REPOSITORY_PROVIDER_VERSION,
    RepositoryProvider,
    build,
    repository_capabilities,
    repository_descriptor,
    repository_root,
)

__all__ = [
    "ARTIFACT_KIND",
    "REPOSITORY_PROVIDER_ID",
    "REPOSITORY_PROVIDER_KIND",
    "REPOSITORY_PROVIDER_VERSION",
    "RepositoryProvider",
    "build",
    "repository_capabilities",
    "repository_descriptor",
    "repository_root",
]

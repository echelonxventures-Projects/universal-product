"""Fixtures for the UCOS Ω∞ Phase 2 governance suite.

EVERY FIXTURE HERE IS A FRESH REGISTRY, AND THAT IS THE POINT. The package ships module-level
vocabularies (``INITIAL_STATES``, ``INITIAL_TIERS``, ``WELL_KNOWN``, ``MINIMUM_DOMAINS``) which
registries SEED FROM rather than mutate, so a test that declares a new state or a sixth relation
must not be able to leak that declaration into the next test. Sharing one registry across the suite
would make the extension tests order-dependent, and an order-dependent proof that a system is
open for extension proves nothing at all.

``encoding`` is a fixture rather than a default argument for the reason the package itself gives:
representation and identity are provider slots, so every call site that needs bytes must NAME the
pair it used. A test module reaching for a global default would be asserting the assumption these
modules exist to remove.
"""

from __future__ import annotations

import pytest

from engine.omega_governance.reference.encoding import Encoding, default_encoding
from engine.omega_governance.state import (
    StateRegistry,
    TransitionGraph,
    default_graph,
    default_states,
)
from engine.omega_governance.temporal.frames import (
    FrameRegistry,
    ScaleRegistry,
    default_frames,
    default_scales,
)
from engine.omega_governance.temporal.ordering import (
    OrderingRegistry,
)
from engine.omega_governance.temporal.ordering import (
    default_registry as default_orderings,
)


@pytest.fixture
def encoding() -> Encoding:
    """The shipped codec/identity pair, named explicitly at every call site that needs bytes."""
    return default_encoding()


@pytest.fixture
def frames() -> FrameRegistry:
    """The seven shipped frames, with NO relations declared — comparability must be earned."""
    return default_frames()


@pytest.fixture
def scales() -> ScaleRegistry:
    return default_scales()


@pytest.fixture
def orderings() -> OrderingRegistry:
    """The four shipped strategies and the five shipped relations."""
    return default_orderings()


@pytest.fixture
def states() -> StateRegistry:
    return default_states()


@pytest.fixture
def graph() -> TransitionGraph:
    return default_graph()

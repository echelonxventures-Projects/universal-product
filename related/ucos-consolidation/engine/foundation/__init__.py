"""EC-1 Foundation layer (IMP-001).

Public API surface for configuration, observability (errors, logging, telemetry),
versioned contracts, and the frozen-path guard.
"""

from __future__ import annotations

from engine.foundation.config.config import Config, Environment, SecretRef, load_config
from engine.foundation.contracts.contract import Contract, ContractRegistry, Version
from engine.foundation.guards.frozen_paths import (
    FROZEN_PREFIXES,
    assert_no_frozen_write,
    find_frozen_writes,
)
from engine.foundation.obs.errors import (
    ConfigurationError,
    ContractViolation,
    FoundationError,
    ObservabilityError,
    SecurityViolation,
    ValidationError,
)
from engine.foundation.obs.logging import StructuredLogger, configure_logging, get_logger
from engine.foundation.obs.telemetry import (
    correlation_id,
    metric_counter,
    metric_gauge,
    metric_histogram,
    metrics_snapshot,
    new_correlation_id,
    set_correlation_id,
    trace,
)

__all__ = [
    # config
    "Config",
    "Environment",
    "SecretRef",
    "load_config",
    # contracts
    "Contract",
    "ContractRegistry",
    "Version",
    # guards
    "FROZEN_PREFIXES",
    "assert_no_frozen_write",
    "find_frozen_writes",
    # errors
    "FoundationError",
    "ConfigurationError",
    "SecurityViolation",
    "ContractViolation",
    "ObservabilityError",
    "ValidationError",
    # logging
    "StructuredLogger",
    "configure_logging",
    "get_logger",
    # telemetry
    "correlation_id",
    "set_correlation_id",
    "new_correlation_id",
    "metric_counter",
    "metric_gauge",
    "metric_histogram",
    "metrics_snapshot",
    "trace",
]

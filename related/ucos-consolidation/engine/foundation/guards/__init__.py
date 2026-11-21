"""Guards subpackage (TASK-000003)."""

from engine.foundation.guards.frozen_paths import (
    FROZEN_PREFIXES,
    assert_no_frozen_write,
    find_frozen_writes,
    main,
)

__all__ = ["FROZEN_PREFIXES", "assert_no_frozen_write", "find_frozen_writes", "main"]

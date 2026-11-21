"""UCI-000001 Part 7 — randomized execution order (mandate Rule 9).

WHY THIS IS A PLUGIN AND NOT A DEPENDENCY.

``pytest-randomly`` is the obvious answer and it is the wrong one here, for a reason specific to
this repository. UVI-L-08 measures that the shard assignment is DETERMINISTIC — longest-processing
-time with ties broken by path — so that two planners produce identical shards, and
``00-MASTER/UVI-000001/uvi-declaration.json`` declares certain files ``isolated`` because they
assert properties of the whole tree. A plugin that reseeds collection on every run by default
would make that contract unmeasurable and would change the meaning of every existing green run.
Adding a dependency to obtain a behaviour that must be off by default is a poor trade, so the
behaviour is implemented here in 40 lines that are themselves inside the coverage denominator.

OPT-IN, TWICE OVER. Nothing happens unless the plugin is loaded with ``-p`` AND
``UCI_SHUFFLE_SEED`` is set to an integer. Absent either, ``pytest_collection_modifyitems`` returns
without touching the order, so loading the plugin in a normal run is a no-op rather than a silent
reordering.

THE SEED IS REPORTED, WHICH IS THE ONLY THING THAT MAKES A FAILURE USEFUL. An order-dependent
failure that cannot be replayed is an anecdote. The seed is echoed into the terminal header, so a
failing randomized run names the exact permutation that produced it and
``UCI_SHUFFLE_SEED=<n>`` reproduces it.

WHAT IS SHUFFLED. Test items, wholesale. Shuffling within a module only would hide the most
common real order dependency, which is one module leaving global state another module reads —
class- and module-scoped fixtures still behave correctly because pytest re-runs setup and
teardown when the active scope changes, at the cost of extra setup calls. That cost is the price
of the measurement and is why this is not the default.
"""

from __future__ import annotations

import os
import random
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    pass

SEED_VARIABLE = "UCI_SHUFFLE_SEED"


def seed_from_environment(environ: dict[str, str] | None = None) -> int | None:
    """Read the seed. A non-integer value is ignored rather than guessed at.

    Returning ``None`` for a malformed value is deliberate: the alternative is to invent a seed,
    which would produce a randomized run that reports a seed nobody chose and cannot be replayed
    from the environment that produced it.
    """
    source = os.environ if environ is None else environ
    raw = source.get(SEED_VARIABLE)
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def shuffled(items: list[Any], seed: int) -> list[Any]:
    """Permute ``items`` reproducibly under ``seed``.

    Uses a private ``random.Random`` rather than the module-level functions so that seeding here
    cannot perturb any test that itself uses ``random`` — which would turn this measurement into
    a cause of the instability it is trying to detect.
    """
    generator = random.Random(seed)  # noqa: S311 - order permutation, not a security decision
    order = list(items)
    generator.shuffle(order)
    return order


def pytest_collection_modifyitems(items: list[Any]) -> None:
    """Reorder collected items when a seed is present. A no-op otherwise."""
    seed = seed_from_environment()
    if seed is None:
        return
    items[:] = shuffled(items, seed)


def pytest_report_header() -> str | None:
    """Name the permutation in the run's own output, so a failure is replayable."""
    seed = seed_from_environment()
    if seed is None:
        return f"uci-shuffle: inactive ({SEED_VARIABLE} unset)"
    return f"uci-shuffle: active, seed={seed} (replay with {SEED_VARIABLE}={seed})"

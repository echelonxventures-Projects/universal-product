"""UCOS Ω∞ — Data Layer (EC-3 Band 10) realization surface.

Additive engineering code that realizes the frozen UCOS Data architecture
(``10-DATA/`` DATA-001…DATA-018) **above**, and by reference to, the CERTIFIED
EC-1 engineering foundation (``engine/**``). It is the executable Data-layer
surface authorized by ``EC3-B10-DATA-REALIZATION-PACKAGE-001``:

    Data = representation-over-composition (DATA-001 §4).

The first realized unit is **EC3-B10-U01 — the Universal Datum Foundation**
(``data.datum``): the executable realization of the meta-model root concept
**DMC-01 Datum** (DATA-005 §2) — a typed (ENG-004) value (ENG-003) borne by an
identified (ENG-001) object (ENG-002).

Constitutional posture (invariant across this package):

* **Additive-only** — this package lives outside ``engine/**`` and ``platform/**``
  and mutates neither; the EC-2 freeze is preserved.
* **Reuse by reference (UDL-02 / DMI-05)** — every foundation primitive
  (Identity, Object, Value, Type, deterministic hashing, provisional-state
  disclosure, validation, certification, ledger) is imported from the CERTIFIED
  EC-1 engine and **never redefined**.
* **Storage-independent (UDL-11)** — no database, schema instance, file format,
  query language, engine, or vendor is selected here.
* **Non-constitutive (UDL-15)** — nothing here confers authority, embeds a
  secret, or asserts constitutional finality; authority is
  ``ENGINEERING-EXECUTION-ONLY``.
"""

from __future__ import annotations

__version__ = "0.1.0"

#: The realization unit this package first realizes (EC-3 Band 10, Unit 01).
REALIZATION_UNIT = "EC3-B10-U01"

#: The Data meta-class realized by the Datum Foundation (DATA-005 §2).
META_CLASS = "DMC-01"

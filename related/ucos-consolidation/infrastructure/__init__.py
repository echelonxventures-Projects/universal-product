"""UCOS Ω∞ — Infrastructure Layer (EC-3 Band 13) realization surface.

Additive engineering code that realizes the frozen UCOS Infrastructure architecture
(``13-INFRASTRUCTURE/`` INFRASTRUCTURE-001…018) **above**, and by reference to, the
CERTIFIED EC-1 engineering foundation (``engine/**``), the FROZEN EC-2 platform
(``platform/**``), the CERTIFIED-COMPLETE Band-10 Data realization (``data/**``), the
FROZEN Band-11 Service realization (``service/**``), and the FROZEN Band-12 Application
realization (``application/**``). It is the executable Infrastructure-layer surface
admitted by ``EC-3-AP-5-BAND-13-ADMISSION-DETERMINATION`` (Band 13 ADMITTED · MEP-04
OPEN) and planned by ``EC-3-B13-P01`` (Band-13 Master Program Charter):

    Infrastructure = realization-environment-over-experience (INFRASTRUCTURE-001 §4).

The first realized unit is **EC3-B13-U01 — the Universal Infrastructure Capability**
(``infrastructure.capability``): the executable realization of the meta-model leaf
concept **InfrastructureCapability** (INFRASTRUCTURE-005 §2; INFRASTRUCTURE-006) —
*the implementation-independent hosting/delivery ability an infrastructure realizes*:
a typed (ENG-004) ability borne by an identified (ENG-001) object (ENG-002) that reuses
the PLATFORM-006 / SF-2 capability construct **by reference** (ICAP-01 / UIL-06) and
enables a frozen lower-layer construct **by reference** (ICAP-03).

Constitutional posture (invariant across this package):

* **Additive-only** — this package lives outside ``engine/**``, ``platform/**``,
  ``data/**``, ``service/**`` and ``application/**`` and mutates none of them; the EC-2
  freeze and the CERTIFIED/FROZEN Band-10/11/12 surfaces are preserved.
* **Reuse by reference (UIP-02 / UIL-02)** — every foundation primitive (Identity,
  Object, Value, Type, Relationship&Reference; runtime behavior; platform composition;
  represented data; hosted operation; hosted experience; deterministic hashing;
  validation; certification; ledger; provisional-state disclosure) is imported from the
  CERTIFIED EC-1 engine (and referenced frozen lower layers) and **never redefined**.
* **Technology-independent (UIL-12 / UIL-15)** — no cloud provider, orchestrator, IaC
  tool, region/zone, hardware, transport, protocol, framework, or vendor is selected.
* **Non-constitutive (UIL-15)** — nothing here confers authority, embeds a secret, or
  asserts constitutional finality; authority is ``ENGINEERING-EXECUTION-ONLY``.
"""

from __future__ import annotations

__version__ = "0.1.0"

#: The realization unit this package first realizes (EC-3 Band 13, Unit 01).
REALIZATION_UNIT = "EC3-B13-U01"

#: The Infrastructure leaf meta-class realized by the Universal Infrastructure
#: Capability (INFRASTRUCTURE-005 §2).
META_CLASS = "InfrastructureCapability"

# ADR-0003: Universal Meta-Kernel — an open, self-describing meta-type system

> **Home note.** This architecture decision is homed inside the PROGRAM-002 operational-
> memory directory (`00-MASTER/UMK-000001/`, registration-excluded) rather than the corpus
> `adr/` family. The programme is AUTHORITY = NONE (derived truth); homing the record here
> keeps the certification commit self-contained and introduces no corpus-registration
> drift. It may be promoted into the corpus `adr/` family later through the normal
> registration transaction (`register.sh --guard`).

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-07-28 |
| Deciders | UCOS Ω∞ Kernel Foundation (PROGRAM-002, WAVE-2) |
| Technology Constitution refs | TP-04 (Vendor Neutrality of Core), TP-05 (Least Sufficient Technology), DP-03 (frozen corpus read-only), AR-03 (versioned contracts) |
| Supersedes | none |

## Context

PROGRAM-002 requires the smallest possible Universal Meta-Kernel capable of representing,
governing, composing, validating, certifying, discovering, tracing, and evolving the
largest possible universe of present and future concepts without kernel redesign. The
constitution forbids finite enumerations, architecturally closed domains, and any
hard-coded domain / provider / technology / Earth assumption in the kernel.

Repository Truth revealed a concrete architectural gap. The existing single registration
authority (`engine/registry/universal/`) keys every artifact by a **closed** enumeration,
`RegistryKind` (`engine/registry/universal/identity.py`). That enum's own history records
the problem: admitting the `CONTEXT` category (for UCXI-000001) required editing the enum
and its code map — a kernel edit for a new concept-category. Any future category (a new
value-exchange system, taxation model, civilization, execution model) would likewise
require editing kernel code, violating Engineering Rule 7 ("unknown future concepts shall
require registration, not kernel redesign") and the "no finite enumerations" requirement.

This ADR does not modify or deprecate the existing registry; it realizes the frozen
requirement for an open substrate beneath and beside it.

## Decision

We will implement the Universal Meta-Kernel (`engine/kernel/`) as the smallest possible
**open, self-describing meta-type system**:

1. A single universal thing — `MetaObject` — carries identity, an open attribute map, open
   relationships, and provenance. Anything the platform ever represents is a `MetaObject`.
2. A single reflective root — `MetaType` — closes the open world without a finite base:
   a meta-type is a `MetaObject` classified by `MetaType`, and the root `MetaType` is
   classified by itself.
3. Concept-categories are **registered meta-types (DATA)**, never enum members. The
   registry (`engine/kernel/registry.py`) admits any meta-type; the universe of categories
   is derived from what has been registered, with no closed set anywhere in the kernel.
4. Every admission is governed (`engine/kernel/governance.py`), possesses a deterministic
   identity (`engine/kernel/identity.py`), is append-only, versioned, Knowledge-Once, and
   recorded in a tamper-evident hash-chained audit journal.
5. The 22 founding universal abstractions ship as a seed DATA table
   (`engine/kernel/seed.py`), treated exactly as any category the kernel has never seen.

Compliance is proven by executed probes (`engine/kernel/compliance.py`) and bound by the
derived-truth programme UMK-000001; the kernel reuses the canonical `Version`/`Contract`
primitive (`engine/foundation/contracts/contract.py`) rather than creating a new one.

## Consequences

- Positive: a previously unknown category is admitted by registration alone; the kernel
  source is provably unchanged (fingerprint before/after the mandatory architectural proof
  is identical). No finite enumeration exists in the kernel (no `enum.Enum` subclass).
  Stdlib-only, deterministic, byte-identical across runs.
- Negative / neutral: the kernel intentionally overlaps in spirit with the closed-enum
  registry. They are not merged here. Migration path (reversible): providers may register
  the existing `RegistryKind` values as meta-types; the closed registry can later delegate
  its kind vocabulary to the meta-kernel without changing this ADR.
- Exit path (TP-04): the kernel depends on nothing beyond the Python standard library and
  the in-repo `Version` primitive, so it carries no vendor lock-in.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — additive;
      the frozen corpus (00-BOOK, 00-SOURCE, 99-FREEZE) is untouched (DP-03).
- [x] Rollback / migration path recorded (CC-04) — see Consequences.
- [x] Traceability links to affected artifacts recorded (CC-05) — `00-MASTER/UMK-000001/`
      (`umk-kernel.json`, `05-TRACEABILITY.md`) binds every abstraction to its home.
- [x] No secret material embedded (SEC-04).

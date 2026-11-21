# 06 — IMPLEMENTATION ROADMAP · DEPENDENCY SEQUENCING

> **Mission:** UCOS-NUCLEUS-001 · Deliverables **3 (roadmap)** and **7 (dependency sequencing)**.
> **Method:** sequencing is a topological order over the dependency graph, consistent with the engine-derived closure model (`05-DEPENDENCY-CLOSURE.md`, `engine/runtime/graph.py` acyclic). No step may precede its dependencies.

---

## 1. Governing gate (Wave 0 — before any authoring)

| Step | Action | Owner/tool | Exit criterion |
|---|---|---|---|
| W0.1 | Clean/stash in-flight `programme/evo-usis-005` work OR branch clean | git | working tree clean for this mission |
| W0.2 | CEP-009 amendment authorization for Nucleus Constitution | governance | write-authorized mission approved |
| W0.3 | Reuse-First Step-0 adjudication ratified (Nucleus=EXTEND; Commission NEW?) | `01-…` §1 | adjudication signed off |

Nothing downstream proceeds until W0 passes (Governance precedes generation — `MCP-001`).

---

## 2. Dependency-ordered waves

Edges: `A → B` means A depends on B (B first). Derived from Nucleus dependencies in the catalogs.

```
Wave 1  Nucleus primitive + Constitution        (EXTEND S2-03 + CEP-009)      [G-N1]
Wave 2  Nucleus completeness contract + NUC-META profile over registry        [depends W1]
Wave 3  Zero-Finite substrate fixes ZF-1..ZF-5   (schema de-hard-coding)       [depends W2]
Wave 4  Configuration-First invariant CFG-1 + config schemas (PLATFORM-010)    [depends W2]
Wave 5  Foundational Nuclei realization (EXTEND): Identity, Space, Time, Scale,
        Observer, Value/Currency, Language/Communication                        [depends W2]
Wave 6  Time/Calendar deep scope ([N] items: TRS, sync, precision, kinematics,
        non-Earth frames/calendars)                                             [depends W5:Time]
Wave 7  Commerce-domain Nuclei realization (EXTEND): Product, Catalog, Pricing,
        Offer, Inventory, Order, Payment, Tax, Party, Supplier, Logistics,
        Contract                                                                [depends W5]
Wave 8  Commission Nucleus (NEW, if Reuse-First=distinct)                       [depends W7:Pricing,Party]
Wave 9  Universe-as-composition catalog + Platform blueprints/config profiles   [depends W5,W7]
Wave 10 Registry regeneration + closure re-run + invariants=0                   [after each wave]
```

**Dependency rationale (evidence):**
- Time depends on Existence/Transformation (`UNI-006` deps `UNI-002, UNI-004`); Calendar depends on Time (`DOM-0021` dep `DOM-0020`) — so Calendar after Time.
- Pricing depends on Currency+Product+Time (`BUC-002`: `UNI-065` deps `UNI-067,UNI-064,UNI-006`) — so Pricing after those.
- Commission depends on Pricing+Party+Currency — so last among commerce.
- Universe compositions depend on their member Nuclei — so after Wave 7.

---

## 3. ZF-1…ZF-5 (Zero-Finite substrate scope — from architecture audit)

| ID | Fix | Target | Blocks true Zero-Finite? |
|---|---|---|---|
| ZF-1 | Unbounded `universal_id` (lift 10⁶ ceiling) | `00-BOOK/SCHEMAS/artifact.schema.json` | YES |
| ZF-2 | Unbounded `volume` id (lift 1000 ceiling) | schema | YES |
| ZF-3 | Registry-sourced `LifecycleStatus` (open vocabulary) | `engine/registry/models.py` + `status.schema.json` | YES |
| ZF-4 | Registry-sourced `TRACE_STAGES` + relax `additionalProperties` | schema + `models.py` | YES |
| ZF-5 | Registry-sourced `DiscoveryKind` (self-extending discovery) | `engine/discovery/contracts.py` | YES |

These are **engine/schema** changes and therefore the highest-risk items (touch frozen-adjacent core). They are the only items that genuinely require code change; all Nucleus *content* is registration/config.

---

## 4. Per-wave definition of done

Each wave unit is DONE when: owner EXTENDED/authored → registered (`register.sh`) → validated (`engine/validation`) → certified (`engine/certification` + CERTIFICATION-REGISTRY) → closure regenerated with `gap_total=0` and invariants 0 → traceability edge recorded (`07-…`). Mirrors the existing EC3 unit pattern (`CKPT-*` checkpoints).

---
*End of 06-IMPLEMENTATION-ROADMAP-AND-SEQUENCING.md*

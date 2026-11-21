# 06 — Identifier Registry Model

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define the **Identifier Registry** — the governed catalog of every *identifier family* (the format by which members of a namespace are named), replacing the 26 hard-coded regexes in `closure_engine.py:FAMILIES`. Satisfies **MA-1**. Works with the Namespace Registry (doc 05): a namespace *is a domain*; an identifier family *is how members of that domain are minted and matched*.

## 1. Defect being corrected (CLOSURE-007 report 03)

- Closed, hand-curated set of 26 families; new families require source edits.
- Rigid widths (`UCOS-COMP` exactly 6 digits; `MCS`/`CEP` exactly 3) silently drop `MCS-1`, `PHASE-11.0`, `AD-0016`.
- Case bug: `Phase-\d{3}` misses uppercase `PHASE-`.
- Sentinel exclusion `…-99/999/U99` embedded in code, undocumented as governance.
- Dozens of real families (`WP-R`, `PCAMG-RUNTIME`, `PI`, `AD`, `UMB`, `UCOS-RIE`, …) unrepresentable.

UMA makes every one of these a **registered, versioned, rationale-bearing data record**.

## 2. Identifier Family Descriptor Schema

| Field | Meaning | Fail-closed rule |
|---|---|---|
| `family_id` | Stable family key. | unique |
| `namespace_id` | Owning namespace (doc 05). | must resolve |
| `match_rule` | Declarative pattern spec (see §3) — NOT free-form regex. | required, validated |
| `width_policy` | Fixed / variable / range of the numeric part. | required (fixes rigid-width bug) |
| `case_policy` | case-sensitive / insensitive (fixes `PHASE` bug). | required |
| `issuing_authority` | Who mints IDs in this family. | required |
| `sentinel_policy` | Declared example/sentinel exclusions + rationale. | required (fixes hidden `_SENTINEL`) |
| `examples[]` / `counter_examples[]` | Positive/negative test vectors. | required (drives determinism tests) |
| `status` | Active / Reserved / Historical / Deprecated / Excluded. | required |
| `evidence[]` | Where the family occurs. | required |

## 3. Declarative Match Rule (no raw regex authority)

Discovery is **registry-driven, never regex-driven** (mission mandate). The registry stores a *declarative* match spec that the platform compiles deterministically; authors do not hand-write engine regexes:

```
MatchRule {
  prefix          # e.g. "UCOS-COMP"
  segment_shape   # ordered segments: [ALPHA], [ALNUM], [NUM]
  num_width       # fixed:N | range:[min,max] | variable   (replaces rigid \d{3})
  separators      # "-" etc.
  case            # sensitive | insensitive
  boundary        # word-boundary rules
}
```

- **Determinism:** the compiler is a pure function `MatchRule → matcher`; the same rule always compiles identically (replayable).
- **Governance over patterns:** because rules are declarative and validated (examples must match, counter-examples must not), a malformed family is rejected at registration — impossible with hand-edited regexes.
- **Width/case correctness:** `num_width=range:[1,4]` would capture `MCS-1`…`MCS-9999`; `case=insensitive` captures `PHASE-` and `Phase-` alike — both CLOSURE-007 defects closed by data, not code.

## 4. Family Lifecycle & Self-Registration

- Issuing authorities register their own families (self-registration, MA-1).
- Discovery, on seeing an ID-shaped token with no matching family, emits `UNCOVERED-IDENTIFIER` + a Registration Proposal (never auto-added; fail-closed).
- Sentinels/examples are explicit `sentinel_policy` records, not buried code — every exclusion enumerated (MA-7).

## 5. Relationship to Namespace Registry

```
Namespace (doc 05)  1 ────< N  Identifier Family (doc 06)
   e.g. UCOS-COMP        │        UCOS-COMP-######  (num_width fixed:6)
   e.g. PHASE            │        Phase-### & PHASE-### (case insensitive)
   e.g. UMB (prose)      └──────  (0 families → measured via Semantic Service, MA-6)
```

A namespace with zero identifier families is legal (prose namespaces); its members are found by the Semantic Service (doc 07/08), satisfying **MA-6** (ID-less concepts have a declared measurement path).

## 6. Registry Invariants

1. Single Identifier Registry per repository (Single Authority).
2. Declarative rules only; raw engine regex is an implementation detail, never the authority.
3. Every family versioned; measurements pin `registry_version` (replayability).
4. No family without evidence and test vectors (Evidence Before Conclusion + determinism).
5. Unknown token ⇒ UNCOVERED + proposal (fail-closed).

## 7. Dependency Determination

- `closure_engine.py:FAMILIES` (26 regexes) → **content seeds** the Identifier Registry, then its **authority is retired**. Discovery authority **TRANSFERS** to UMA. The engine, if retained by Closure, becomes a *consumer* of the registry snapshot (doc 20).

*END — 06 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*

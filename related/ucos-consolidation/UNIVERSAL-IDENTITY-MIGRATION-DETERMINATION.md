# UNIVERSAL IDENTITY MIGRATION DETERMINATION (G11)

> **Mission:** UCOS Ω∞ Universal Identity Capability Completion — Workstream 6 (gap G11)
> **Baseline:** `5eb1a704` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-17
> **Mode:** Determination. Prerequisite to any registration of the affected population. **Nothing is registered by this document.**
> **Authority:** NONE (DERIVED TRUTH). Determines disposition; performs no migration.

---

## 1. Executive determination

**The population is not anonymous, and "silently register" was correctly forbidden.** Measured against the gate's own eligibility function (`ukb._iter_files`), the population is:

| Measure | Value |
|---|---|
| Eligible artifacts | 1 371 |
| Registered in `artifacts.json` | 1 233 |
| **Unregistered eligible** | **138** |
| Hold a Universal ID (`by_object`, UGA) | **138 — all of them** |
| Hold a corpus ID (`by_path`, UMB-IMP-001) | **0** |
| Anonymous (no identity anywhere) | **0** |
| Zero-byte / invalid | **0** |
| Zone | **repository root — 138 of 138** |
| Extension | **`.md` — 138 of 138** |

The count was 135 before this cycle; the three determinations added here take it to 138. **Every one already holds identity** under `UCOS-UGA-001` as `EXCLUDED_DOCUMENT`/`EXDOC`. The gap is not identity — it is *corpus registration*, i.e. a `by_path` allocation plus an `artifacts.json` entry.

So the accurate statement of G11 is: **138 root-level markdown determinations hold UGA identity but are absent from the corpus register**, and `enforce --pre` does not block because in pre-mode `unregistered` is the scope selector, not a violation (`ukb.py:1959-1966`).

---

## 2. Why this is a real defect and not a filing preference

`REG-AUTO-001` states the rule the repository has already adopted:

- **P1 §3: "Creation is registration."** An artifact is not created until all seven registers reflect it; physical existence alone is "a draft on disk".
- **L2: "Created" ≡ "Registered".**
- **L1:** creation without registration is prohibited, and a commit adding an in-scope artifact without its register state "is invalid and must be blocked".

138 artifacts are therefore, by the standard's own definition, **drafts on disk** that have been treated as authoritative determinations for many cycles. Several are cited as governing authority by other documents. That is the substance of the defect: not that they lack identity, but that the corpus register does not carry what the corpus relies on.

---

## 3. Per-artifact disposition, determined by measurement

The population is homogeneous, which makes a class determination sound rather than lazy. Every one of the 138 resolves identically on every dimension the workstream requires:

| Dimension | Determination | Evidence |
|---|---|---|
| **Existing identity validity** | **VALID, retained.** All 138 hold `by_object` identity minted by `UCOS-UGA-001`. Registration **must not** retire or reissue them — `ids_preserved: ALL` | `id-ledger.json` `by_object` |
| **Owner** | `UCOS-REPOSITORY-ROOT` — `derive_owner()` returns this for root-level paths | `uga_engine.py:218-229` |
| **Namespace** | `ucos.determination` (declared in `uobc-birth-contract.json`) for the birth plane; corpus category is path-derived per §4 | UOBC-000001 |
| **Registry destination** | `00-BOOK/DATA/artifacts.json` plus the six synchronized registers of the `REG-AUTO-001` §7 atomic transaction `T` | REG-AUTO-001 §7 |
| **Evidence availability** | Each is its own evidence: a determination records the analysis that produced it. `evidence_class: VALIDATION` already assigned | UGA registry |
| **Temporal origin** | `first_seen` in `by_object`, expressed as `commit:<sha12>` — a commit-derived coordinate, not a wall clock. Admissible under CMG-000002 as a **contextual** reference system | `id-ledger.json` |
| **Certification requirement** | **NONE at migration.** These are `DERIVED TRUTH` determinations; they assert analysis, not law. Registration is not certification (CEP-005 is a separate channel) | CEP-005 |

**Classification is total and needs no configuration edit.** Running `ukb.classify()` over all 138 resolves every one to a derived category with volume `VOL-000` (17 × `PHASEU`, 13 × `H06IMP`, 10 × `H06TAS`, 8 × `H06OWN`, 8 × `H06R4G`, and a long tail). **Zero** resolve to `OTHER/MISC`, so `REG-AUTO-001` L4 (new family declaration) is **not triggered** — exactly the conclusion §21.2 reached for `00-CMG/`.

---

## 4. Determined migration path

Migration runs through the **existing** governed transaction. No new tool, no new register, no bypass.

| Step | Action | Owner | Refusal condition |
|---|---|---|---|
| 1 | `ukb.py enforce --pre` — confirm all 138 are valid and classifiable *before* the transaction | UMB-IMP-001 | any invalid or unclassified artifact aborts |
| 2 | `ukb.py build` — allocate `by_path` identity and page ranges; **`by_object` identity untouched** | UMB-IMP-001 | a reused or renumbered identifier aborts |
| 3 | `register.sh` phases 1-6 — the §7 atomic transaction `T` across all seven registers | REG-AUTO-001 | any component failing ⇒ transaction INCOMPLETE |
| 4 | `ukb.py validate` + `ukbx.py validate` — schema and referential integrity | UMB-IMP-001 | drift aborts |
| 5 | `ukb.py enforce` (post) — parity: eligible == registered | UMB-IMP-001 | non-zero unregistered aborts |
| 6 | `uga_engine.py run` — reclassify the 138 from `EXCLUDED_DOCUMENT` to `DOCUMENT_ARTIFACT` | UCOS-UGA-001 | anonymous object aborts |
| 7 | Birth records under UOBC-000001 for the 138, namespace `ucos.determination` | UOBC-000001 | missing mandatory field aborts |

**Identity preservation is the binding constraint.** Step 2 allocates a *corpus* identifier in a different plane; it does not replace the UCKP identity. A migration that reissued any of the 138 existing identifiers would violate `AIF` pinned-parameter law and the ledger's own "never reissued, never renumbered".

---

## 5. Why this determination does not itself migrate

Three reasons, each sufficient:

1. **Step 6 flips 138 objects from `EXCLUDED_DOCUMENT` to `DOCUMENT_ARTIFACT`.** That changes `object_class` for 138 entries, which changes `evidence_class` and `certification_status` assignment and re-renders every UGA surface. Combined with the register regeneration in step 3, this is a several-thousand-line diff across generated registers — a distinct commit from the capability work, and one whose review needs to be about the migration alone.

2. **`enforce --pre` becoming blocking is a gate inversion.** Making `unregistered` a hard failure (`ukb.py:1959-1966`) would fail the gate for the current tree *until* migration completes. Landing the gate change and the migration in one commit means the gate is never observed failing for the right reason — the evidence that it works is lost.

3. **`register.sh` mutates `00-BOOK/DATA`, `REGISTRIES`, `CONTROL-TOWER` and `PORTAL`**, which is why `verify.sh` keeps it behind opt-in `--full`. Running it inside a capability commit would mix a registration transaction into a code change.

**Determined sequence:** capability commit (this cycle) → migration commit (steps 1-7) → gate-inversion commit (make `unregistered` blocking, and anonymous objects fail `uga_engine.py gate`). In that order, each commit's evidence is legible.

---

## 6. Target and acceptance

| Criterion | Target | Current |
|---|---|---|
| Anonymous objects (no identity anywhere) | 0 | **0 — already met** |
| Unregistered eligible artifacts | 0 | 138 |
| Reissued or renumbered identifiers | 0 | 0 |
| Registry drift after migration | 0 | n/a |
| Birth records for migrated artifacts | 138 | 8 (this cycle's objects) |
| `enforce --pre` blocks on unregistered | yes | **no — deliberate, inverted in commit 3** |

---

## 7. Determination summary

| Item | Determination |
|---|---|
| Silently register the 138 | **REFUSED** — forbidden by instruction and by reviewability |
| Population is anonymous | **FALSE** — all 138 hold UGA identity; 0 anonymous |
| Nature of the gap | corpus registration (`by_path` + `artifacts.json`), not identity |
| Existing identities | **RETAINED** — never reissued, never renumbered |
| New family declaration (`REG-AUTO-001` L4) | **NOT TRIGGERED** — classification is total, 0 resolve to `OTHER/MISC` |
| Certification required at migration | **NO** — registration ≠ certification |
| Migration mechanism | the existing `register.sh` §7 atomic transaction; no new tool |
| Migration performed here | **NO** — determined, sequenced, and left to its own commit |

---

**END UNIVERSAL IDENTITY MIGRATION DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Identity Authority:** UCKP-ART-05 — unchanged; no identifier issued, retired or renumbered by this determination
**Governed Evolution:** ENABLED — CEP-009 · Article-14

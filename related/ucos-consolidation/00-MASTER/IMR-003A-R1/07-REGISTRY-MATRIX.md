# IMR-003A-R1 · OUTPUT 7 — REGISTRY MATRIX

| Field | Value |
|---|---|
| MISSION | `IMR-003A-R1` |
| ARTIFACT | Output 7 — Registry Matrix · supplies the **Registry Contracts** the recovery instruction requires |
| SCOPE | The registry **contract** per located registry: access mode, obligation, prohibition, enforcement. The integration model is owned by `IMR-003A/13-CIOS-REPOSITORY-INTEGRATION-MODEL.md` and is **bound here by pointer, not restated**. |
| CHECKPOINT | CP-006 |
| CENTRAL CLAIM | **CIOS owns no registry, creates no registry, writes to no registry, and adds no entry to any registry.** |
| DISCLOSURE | PROVISIONAL; Tier T1 VACANT |
| VERDICT | **14 REGISTRY CONTRACTS, ALL READ-ONLY. 0 WRITES. 0 ENTRIES ADDED.** |

---

## 1. THE REGISTRY CONTRACT FORM

`CIOS-INV-12` states CIOS holds *"no concern, no gate, no registry and no identifier space of its own."* A registry contract therefore has an unusual shape: it grants CIOS a **read right** and imposes a **write prohibition**, rather than describing a read/write relationship.

| Field | Meaning |
|---|---|
| **Access** | `R` read-only · `A` append-only via a located mechanism · `⊘` no access |
| **Reads for** | the specific CIOS determination the registry feeds |
| **Prohibition** | what CIOS may never do to this registry |
| **Enforcement** | the located clause or machine check that holds CIOS to it |

---

## 2. THE 14 REGISTRY CONTRACTS

### `RC-01` — `CMG-REGISTRY.json` (CMG)

| | |
|---|---|
| Access | **R** |
| Reads for | artifact kinds `CMG-K-01…24` → `CIOS-ID-10`; tiers; states; concerns; `VAC-01` occupancy |
| Prohibition | no concern claimed; no kind, tier, state, namespace or artifact entry added; `CIOS-G-02` remains the gate that would admit a concern |
| Enforcement | `CIOS-INV-12`; `GOV-001` Part 10; `V-63` (`cios_concerns_owned = 0`) |

### `RC-02` — `id-ledger` (`REG-AUTO-001`, `00-BOOK/tools/`)

| | |
|---|---|
| Access | **R** |
| Reads for | duplicate-identifier detection at `CIOS-S-08` (`E-06`) |
| Prohibition | no identifier allocated; no ledger entry created; no `CIOS-*` identifier ever presented to it |
| Enforcement | `CIOS-L-12`, `CIOS-L-14`; `NS-3`; `V-73` (`id_ledger_entries_created = 0`) |

### `RC-03` — `artifacts.json` (`REG-AUTO-001`)

| | |
|---|---|
| Access | **R** |
| Reads for | registered-artifact population; the FROZEN population (27) so CIOS never touches it |
| Prohibition | no entry added; the 27 FROZEN entries unchanged |
| Enforcement | `GD-10` acceptance criterion 1; `V-73` |

### `RC-04` — `UAKOS-CLOSURE-002/closure.json` (Repository Truth)

| | |
|---|---|
| Access | **R** + **A** (append via `CIOS-P-40`, `CIOS-PL-C` only) |
| Reads for | `determination=CLOSED`, `concept_total=434`, `gap_total=0`, seven zero gap classes; canonical homes |
| Prohibition | never read-modify-write; never regenerate (`IEC-001` `07` / C10 / RG-3 owns regeneration); never edit; never delete |
| Enforcement | `AIF-L17`; `WS-4`; `E-20` EXCLUDES; `V-84` … `V-88` (values verified unchanged) |

### `RC-05` — UAKOS canonical-home register

| | |
|---|---|
| Access | **R** |
| Reads for | `CIOS-ID-11` home and `CIOS-ID-12` owner resolution at `CIOS-S-05`/`S-06` |
| Prohibition | no home created, reassigned or removed; a pre-existing duplicate is a **finding**, never repaired by CIOS |
| Enforcement | `CEP-001` LAW-4; `CIOS-INV-06`; `E-04` EXCLUDES |

### `RC-06` — `uccep-bindings.json` / `uccep.json` (UCCEP)

| | |
|---|---|
| Access | **R** |
| Reads for | gates `G-01…G-14`; checks `CK-*`; findings `UCCEP-F-001…008` |
| Prohibition | no gate added; no check added; no finding discharged; no programme entry added |
| Enforcement | `CIOS-01` I.6, IX.4; `AC-4`; `V-63`, `V-79` |

### `RC-07` — `ucda-decisions.json` (UCDA)

| | |
|---|---|
| Access | **R** |
| Reads for | disposition obligation and evidence gate at `CIOS-S-18` |
| Prohibition | no decision added; no disposition altered |
| Enforcement | `CEP-002` Art 28; `CK-DECISION-EVIDENCE`; `UCCEP-F-008` bound |

### `RC-08` — `CEP-009` evolution registry

| | |
|---|---|
| Access | **R** |
| Reads for | change classes (`CEP-009` IV.1) → `CIOS-ID-17`; lineage |
| Prohibition | no evolution entry created; CIOS owns **no** evolution model |
| Enforcement | `CIOS-01` VIII.1; `CIOS-12` §1 |

### `RC-09` — `CEP-007` freeze registry (Art XVI)

| | |
|---|---|
| Access | **R** |
| Reads for | the declared frozen surface, **so CIOS never touches it** |
| Prohibition | **no entry added, ever.** No freeze declared, implied or recorded. No frozen artifact mutated — such an act is void and places the Program in **HALTED** |
| Enforcement | `CEP-007` II.4, IV.4, IX.5; `GD-10-C1`, `GD-10-C2`; `V-69` … `V-72` |

### `RC-10` — `IMG-001` backlog / graph / waves / order / critical path

| | |
|---|---|
| Access | **R** |
| Reads for | `CIOS-K-01…K-06` inputs; family→owner map → `CIOS-ID-13` |
| Prohibition | wave partition W1–W5 not altered; located order not reordered; counts (20·15·32·11·12; 77 effective) preserved exactly |
| Enforcement | `CIOS-01` VII.2; `V-47`, `V-51` … `V-54` |

### `RC-11` — `IEC-001` queues / states / gates / batch boundary

| | |
|---|---|
| Access | **R** + **handoff** (`CIOS-P-30`) |
| Reads for | Execution Queue admission conditions; batch-cut boundary (`CIOS-P-27`); terminal-state events (`CIOS-P-37`) |
| Prohibition | no located queue reordered; no predicate re-evaluated; no gate re-implemented; no dispatch performed; CIOS relinquishes control at handoff |
| Enforcement | `CIOS-01` I.4, VII.1; `E-15` EXCLUDES; `V-36`, `V-38` |

### `RC-12` — AIF ledger

| | |
|---|---|
| Access | **R** |
| Reads for | minted identity fields `CIOS-ID-01…ID-08` |
| Prohibition | **CIOS mints nothing.** No field allocated, altered or substituted; no default or placeholder supplied for a missing minted field |
| Enforcement | `CIOS-L-12`, `L-13`, `L-14`; `IDR-3`, `IDR-6`; `V-43` |

### `RC-13` — `MCP-001 … MCP-007`, `MCS-000` (master context)

| | |
|---|---|
| Access | **R** |
| Reads for | master context, state, execution, decisions, dashboard, traceability, recovery |
| Prohibition | no master record mutated |
| Enforcement | `AC-9`; `V-73` |

### `RC-14` — `UCIC-001` (capability implementation contract)

| | |
|---|---|
| Access | **R** |
| Reads for | capability implementation contract at `CIOS-S-09`/`S-10` |
| Prohibition | no contract altered. **Note:** `UCIC-001` is absent from `CMG-REGISTRY.json`, so capability staging has no citable owner — `GG-6` / `CIOS-GAP-11`, undischarged |
| Enforcement | `GG-6`; `CMG-L-01` |

---

## 3. AGGREGATE REGISTRY POSTURE

| Property | Value | Machine check |
|---|---|---|
| Registry contracts | **14** | §2 |
| Read-only contracts | **14 / 14** | §2 |
| Contracts with an append right | **1** (`RC-04`, via `CIOS-PL-C` only, append-only) | `V-88` |
| Registries **written** by CIOS | **0** | `V-73` |
| Registries **created** by CIOS | **0** | `V-63`, `V-73` |
| Registry **entries added** by CIOS | **0** | `V-73` |
| Freeze registry entries added | **0** | `V-72` |
| `id-ledger` entries created | **0** | `V-73` |
| Corpus identifiers consumed | **0** | `V-68`, `V-73` |
| Registration drift introduced | **0** | `V-73` |
| Frozen surfaces accessed | **0** | `V-73` |
| `closure.json` writes | **0** | `V-73`, `V-88` |
| Registries owned by CIOS | **0** | `CIOS-INV-12` |

---

## 4. THE `CIOS-*` IDENTIFIER FAMILIES ARE NOT REGISTRY ENTRIES

A necessary clarification, since CIOS declares thirteen identifier families.

| Property | `CIOS-*` families | Corpus identifiers |
|---|---|---|
| Allocated by | `IMR-003A` OUTPUT 0.4 (programme scope) | `REG-AUTO-001` |
| Present in `id-ledger` | **NO** | yes |
| Present in `artifacts.json` | **NO** | yes |
| Present in `CMG-REGISTRY.json` | **NO** | yes |
| Consume corpus identity | **NO** | yes |
| Zone | `00-MASTER/` — **registration-excluded** | registered zones |
| May be presented to `REG-AUTO-001` | **NEVER** (`NS-3`) | yes |

Basis: `00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES → "00-MASTER/"`. A `CIOS-E-07` or `CIOS-S-14` identifier denotes a **slot in a programme-scoped declaration**, not an allocated corpus identity. Machine-verified `V-65`, `V-75`.

---

## 5. WHY A READ-ONLY REGISTRY POSTURE IS THE CORRECT OUTCOME

Not an incapacity but the required result:

| If CIOS wrote a registry | Breach |
|---|---|
| added a `CMG-REGISTRY.json` concern | self-conferred authority — `CEP-009` I.5; requires `CIOS-G-02` |
| allocated an `id-ledger` identifier | parallel identifier system — `GOV-001` Part 10; `CIOS-L-14` |
| added a freeze registry entry | void freeze act — `CEP-007` II.4, IV.4; `GD-10-C1` |
| regenerated `closure.json` | second owner of Repository Truth — `CEP-001` LAW-4; `IEC-001` `07` owns it |
| created its own registry | `CIOS-INV-12`; `AC-4` |
| edited any registry in place | `AIF-L17` forward-only compensation |

Every write CIOS might plausibly want is a breach of a located instrument. **The read-only posture is therefore compelled, not chosen.**

---

## AUTHORITY BOUNDARY (MANDATORY)

This matrix records registry contracts. **CIOS owns no registry, creates none, writes to none, and adds no entry to any.** The freeze registry and the FROZEN population are unchanged. No `CIOS-*` identifier is a corpus identifier. This matrix confers no authority and authorizes no execution. Where it and a located canonical instrument disagree, **the located instrument governs and this matrix SHALL be corrected**.

**END OF ARTIFACT — `IMR-003A-R1` OUTPUT 7 · PROVISIONAL · ADDITIVE · AUTHORITY-NEUTRAL**

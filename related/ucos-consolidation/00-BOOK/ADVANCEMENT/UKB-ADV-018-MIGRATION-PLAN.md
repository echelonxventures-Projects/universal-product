# UCOS Ω∞ — UKB ADVANCEMENT MIGRATION PLAN

| Field | Value |
|-------|-------|
| ARTIFACT ID | UKB-ADV-018 |
| ARTIFACT | Migration Plan (Deliverable 19) |
| PROGRAM | UCOS Ω∞ UKB Advancement Program (ADV) |
| STATUS | ACTIVE |
| PARENT | UKB-ADV-017 |
| DEPENDS-ON | UKB-ADV-017 |
| VOLUME | VOL-021 (DIGITAL TWIN) |

*Append-only extension overlay on UCOS-BOOK-000000. This is a zero-downtime, non-destructive migration: the existing UKB keeps working unchanged throughout.*

---

## 1. MIGRATION PRINCIPLE

The advancement layer is **additive**. There is no data migration of existing records — every existing Universal ID, UPN, edge, and registry entry stays exactly as-is. "Migration" here means **standing up the overlay** and **flipping status sources from MANUAL to authoritative** incrementally, with reversibility at every step.

## 2. STEPS

| Step | Action | Reversible? | Integrity check |
|------|--------|-------------|-----------------|
| M0 | Snapshot ledger + registries (baseline) | n/a | record page_cursor + all Universal IDs |
| M1 | Append config (VOL-021, ADV rules/chain) | yes (revert append) | `import config` OK; existing rules unchanged |
| M2 | Add advancement schemas + docs | yes (delete new files) | `ukb.py validate` passes; existing IDs unchanged |
| M3 | Run `ukb.py build` | yes (ledger append-only; new IDs only) | diff ledger: only NEW paths added; page_cursor grew, prior ranges identical |
| M4 | Stand up `ukbx` + offline connectors; ingest fixtures | yes (delete signals) | `ukbx twin` computes snapshot; `control-tower.schema.json` valid |
| M5 | Connect live connectors one source at a time | yes (disable connector) | each dimension flips MANUAL→source; cursors advance |
| M6 | Enable control-tower automation | yes (revert to manual snapshot) | 0 ungoverned MANUAL dimensions |
| M7 | Enable portal/search/publication/AI | yes (feature-flag off) | certification C-08/10/11 pass |
| M8 | Continuous certification on | yes | C-01…C-13 pass |

## 3. STATUS-SOURCE CUTOVER (MANUAL → AUTHORITATIVE)

Per dimension, cutover is a **shadow-then-flip**:
1. **Shadow:** connector emits signals; rollup computes a *shadow* status alongside the MANUAL baseline.
2. **Compare:** operator reviews shadow vs baseline for one cadence.
3. **Flip:** dimension `signal_source` set to the authoritative source; MANUAL retained only as a historical signal (append-only).
Any anomaly → revert flip (the MANUAL baseline signal is still the latest until re-flipped). No data loss because everything is append-only.

## 4. ROLLBACK

Because the overlay writes only new files (`ADVANCEMENT/`, new `SCHEMAS/*.json`, `tools/ukbx.py`, `tools/connectors/`, `DATA/signals.json`, `DATA/twin.json`, `PORTAL/`) and appends only to `config.py`, full rollback = delete the new paths + revert the `config.py` appends + re-run `ukb.py build`. The foundation returns bit-for-bit to baseline (M0). No existing artifact was ever touched, so rollback carries zero risk to canon.

## 5. VALIDATION GATES

- After M3: ledger diff must show **only additions**; `page_cursor` strictly increased; every pre-existing `(path → universal_id, page range)` byte-identical to M0 snapshot.
- After M6: control tower schema-valid; portfolio still computed; no dimension lost.
- After M8: certification CERTIFIED.

*Return: [UKB-ADV-000](UKB-ADV-000-ADVANCEMENT-PROGRAM-MASTER-INDEX.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*

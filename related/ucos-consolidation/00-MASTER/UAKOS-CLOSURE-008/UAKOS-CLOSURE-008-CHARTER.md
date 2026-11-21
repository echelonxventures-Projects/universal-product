# UAKOS-CLOSURE-008 — CHARTER

**Constitutional Assimilation & Repository Completion (Final Closure)**

> AUTHORITY = NONE (DERIVED TRUTH). This programme legislates nothing, ratifies nothing and
> certifies no authority. It reconciles, homes, traces and reports. Fail-closed (TRACK-001).

---

## 1 — Mandate

Verification is complete. Knowledge assimilation is complete. Knowledge verification is
complete. This programme therefore performs **no discovery and no re-verification**. It
consumes those findings as frozen inputs and drives every verified knowledge object into
exactly one of six terminal constitutional states, so that no verified knowledge item
remains unclassified:

| # | Terminal state | Meaning |
|---|---|---|
| 1 | `ALREADY-REPRESENTED` | the repository already carries the object (measured presence) |
| 2 | `SEMANTICALLY-REPRESENTED` | an existing artifact satisfies the intent under another identifier |
| 3 | `ASSIMILATED` | homed in this programme's canonical register with a permanent destination |
| 4 | `HISTORICAL-EVIDENCE-ONLY` | project execution history: retained as evidence, never promoted |
| 5 | `SUPERSEDED` | replaced by a later ratified form |
| 6 | `REJECTED` | explicitly rejected; retained so the rejection is never silently reversed |

## 2 — Boundary

| Boundary | Rule |
|---|---|
| Canonical project | `~/Desktop/UCOS-CONSOLIDATION` — the ONLY implementation authority |
| Programme home | `00-MASTER/UAKOS-CLOSURE-008/` — the ONLY path this ENGINE writes |
| Integration surface | `Makefile` (targets `assimilate`, `assimilate-replay`, `assimilate-gate`) and `.github/workflows/assimilation-gate.yml` are committed WITH this programme so it is runnable and gated. The engine writes neither; both are declared in register 04 rather than left as an undeclared out-of-home footprint |
| External evidence | `~/Desktop/KNOWLEDGE-ASSIMILATION` — READ-ONLY. Never written, never treated as an implementation repository, used only for traceability, evidence lookup and constitutional justification |
| Ratified artifacts | never amended, never duplicated, never re-authored by this programme |
| Registration | `00-MASTER/` is an `EXCLUDE_DIR_PREFIX` in `00-BOOK/tools/config.py`, so these artifacts mint no identities and introduce no registration drift |

## 3 — Inputs (frozen, hashed)

| Input | Role |
|---|---|
| `output/knowledge/knowledge_base.json` | the 23,859 verified knowledge objects |
| `output/knowledge/gaps.json` | measured gap classes (516 / 319 / 40) |
| `output/knowledge/knowledge_base_summary.json` | published aggregate measures (cross-check) |
| `output/knowledge/FINAL_DETERMINATION.md` | promotion intent (§4 artifacts … §9 historical) |
| `output/knowledge/reports/GAP_REPORT.md` | gap classes and in-repo structural defects |
| `evidence/TRI-SOURCE-VERIFICATION-DETERMINATION.md` | the verification determination — the authority for every curated mapping |
| the repository at HEAD, via `git ls-files` | the semantic-equivalence universe |

Every input file is hashed into `EVIDENCE-MANIFEST.json`. The engine fails closed if an
input is absent, and `--render` replays every register from `assimilation.json` alone, so
the repository is self-contained and reproducible with the evidence tree detached.

## 4 — Prohibitions (STOP conditions, enforced by construction)

- No discovery reports, no repository search for further corpora, no speculative
  architectural analysis, no new philosophical documents, no re-verification.
- **Identifier matching alone is prohibited.** Equivalence must be semantic, structural or
  behavioural, and every mapping must resolve to an artifact that exists at HEAD.
- No duplicate concepts, no parallel authorities. Where an implementation already satisfies
  an intent, the mapping is recorded instead of a new artifact being created.
- No fabricated commitment: knowledge whose evidence carries no human decision
  (`IDEA` / `PROPOSAL`) is registered as a governed FUTURE entry, never scheduled as work.
- No fabricated certainty: registration is a constitutional home, not an implementation, and
  the reports say so explicitly.

## 5 — Method

1. **Reconcile** — for every object: already implemented? already documented? semantically
   equivalent? implemented under another identifier? missing? destination? dependencies?
   canonical owner? priority?
2. **Assimilate** — every approved missing item is homed with exactly one destination, one
   owner, one constitutional authority, one wave and one dependency chain.
3. **Validate** — the programme's own fail-closed gates, then the canonical repository gate
   `./verify.sh`.
4. **Iterate** until remaining approved promotion candidates = 0.

## 6 — Success criteria

| Criterion | Gate |
|---|---|
| Repository remains the sole implementation authority | change register 04 (0 files outside the programme home) |
| Every verified knowledge object classified | gate: unclassified = 0 |
| Every approved item assimilated or explicitly dispositioned | gate: remaining approved promotion candidates = 0 |
| No duplicate authorities | gate: no assimilated item is also present or semantically represented |
| No unresolved semantic mappings | gate: every anchor + proof token resolves at HEAD |
| `verify.sh` completes successfully | report 06, captured verbatim |
| Repository passes constitutional validation | `ukb.py enforce --pre` + `ukb.py validate` inside `verify.sh` |

Only when every gate passes may the determination
**REPOSITORY CONSTITUTIONALLY COMPLETE** be issued — and it is issued over
*constitutional disposition*, never over *implementation*, which remains with the
destination owners under their own constitutions.

## 7 — Artifacts

| Artifact | Contents |
|---|---|
| `01-REPOSITORY-RECONCILIATION-REGISTER.md` | the reconciliation determination and rule precedence |
| `02-SEMANTIC-EQUIVALENCE-REGISTER.md` | curated, propositional and computed equivalences |
| `03-ASSIMILATION-REGISTER.md` | the canonical home of every approved missing item |
| `04-REPOSITORY-CHANGE-REGISTER.md` | every change, hashed, with its registration status |
| `05-TRACEABILITY-REGISTER.md` | artifact ← evidence ← authority ← dependency chain |
| `06-VALIDATION-REPORT.md` | programme gates + `verify.sh` evidence |
| `07-CERTIFICATION-REPORT.md` | what is certified and what is explicitly withheld |
| `08-REPOSITORY-COMPLETION-REPORT.md` | the final determination |
| `assimilation.json` | the machine-readable register: all 23,859 objects, columnar |
| `EVIDENCE-MANIFEST.json` | sha256 of every external evidence file consumed |
| `assimilation_engine.py` | the deterministic engine that produces all of the above |

## 8 — Reproduction

```bash
python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py            # reconcile + assimilate
python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py --render   # replay, no evidence tree
python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py --gate     # exit 1 unless COMPLETE
./verify.sh                                                           # canonical repository gate
```

The engine emits no timestamps and derives its universe from `git ls-files` at HEAD, so
repeated runs at the same HEAD are byte-identical. `--render` replays the recorded
`head_commit` from `assimilation.json` instead of re-reading git, so the committed registers
remain the exact replay of their own machine-readable source across commits — which is what
the CI drift gate compares.

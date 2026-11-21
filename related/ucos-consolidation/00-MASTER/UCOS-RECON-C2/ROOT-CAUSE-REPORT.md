# UCOS-RECON-C2 — ROOT CAUSE REPORT · CK-REG-DRIFT

| Field | Value |
|-------|-------|
| MISSION | UCOS-RECON-C2 — eliminate the root cause of registration drift |
| CLASSIFICATION | RECONCILIATION CORRECTION — eligibility declaration + append-only ledger retirement |
| STATUS | **COMPLETE · RECON-C2 CLOSED** |
| AUTHORITY | **NONE — DERIVED TRUTH.** This report legislates nothing and ratifies nothing. |
| BRANCH | `integration/recovery-001` |
| BASELINE | `a6ccdc0` (PROGRAM-003 Universal Provider Framework) |
| REPAIR | `214c1a9` · programme regen `39819ad` · catalogue regen `4141647` · seal `4c6623f` |
| FORBIDDEN-WRITE CHECK | 0 writes to `engine/**`, `platform/**`, `00-SOURCE/**`, `99-FREEZE/**` |
| **RESULT** | CK-REG-DRIFT **PASS** · G-07 **PASS** · `blocking_failures = []` · 1204 → **1193** registered artifacts |

---

## 1. The single root cause

> **`00-BOOK/tools/config.py::EXCLUDE_DIR_PREFIXES` — the sole registration
> admission rule — enumerated the generator's GENERATED outputs only where they
> live under `00-BOOK/`. The UCOS-RIE-001 output family is emitted to
> `intelligence/`, so it was admitted into the Repository Corpus and given eleven
> permanent corpus identities. Because every one of those files embeds the commit
> that contains it and the hash of the registry that records it, the registration
> relation over them has no fixpoint. CK-REG-DRIFT was therefore not merely
> failing — it was UNSATISFIABLE.**

Everything else observed is a consequence of that one fact.

## 2. Why this is the root cause and not a symptom

The registration boundary is a pure function, evaluated in exactly one place
(`ukb.py::_iter_files`):

```
eligible = (git ls-files --cached --exclude-standard)
           ∩ INCLUDE_EXTENSIONS
           ∖ { p : p.startswith(EXCLUDE_DIR_PREFIXES) }
```

`INCLUDE_EXTENSIONS` contains `.json`. The eleven RIE outputs are tracked `.json`
files. No prefix matched them. So they were eligible, and REG-AUTO-001 correctly
registered them — recording a `content_hash` for each in
`00-BOOK/DATA/artifacts.json` and a version snapshot in `id-ledger.json`.

Now observe what those files contain. From `intelligence/rie/evidence.py` and the
`generation` envelope of every output:

| Embedded field | Source |
|---|---|
| `generation.repository_head.commit`, `generation.source_commit`, `evidence_state.head` | `git rev-parse HEAD` |
| `generation.generation_timestamp` | `git show -s --format=%cI HEAD` |
| `evidence_state.evidence_files["00-BOOK/DATA/*.json"]` | sha256 of the registry projections |
| `generation.input_hash` | sha256 over all of the above |
| `code.coverage_line_pct`, `evidence_state.coverage_measurement.fingerprint` | `coverage.xml` |

So the bytes that registration must record are a function of:

1. **the commit that will contain them** — committing changes `HEAD`, which
   changes the required bytes; and
2. **the register that records them** — registration rewrites
   `00-BOOK/DATA/artifacts.json`, whose sha256 is embedded in the outputs.

A fixpoint would require a commit whose own hash appears inside its own tree.
That is not reachable. **No sequence of regenerate → register → commit can ever
satisfy the drift gate.** This is why the git history contains a run of commits
named "regenerate at the committed anchor" (`ad39f62`, `d57ab5c`, `088a853`,
`4712da5`, `b47f5b9`, `b7431ca`, `3862bae`) that never converged, and why the
UCCEP establishment record already noted the identical signature: *"modified
registry projections and intelligence outputs … register.sh --guard exits 3."*

A third, independent disqualification: RIE derives from `coverage.xml`, which the
ignore authority declares an ENVIRONMENT artifact. A registered artifact's content
was therefore not even a function of the repository.

## 3. Constitutional basis

`config.py` encodes GOV-005 §5.3 verbatim:

> A REPOSITORY ARTIFACT is a version-controlled … **human-authored** corpus file.
> A GENERATED ARTIFACT is a deterministically re-derivable output — **regenerated,
> never hand-registered**. … **Only REPOSITORY ARTIFACTS are eligible for
> registration.**

The RIE family is a GENERATED ARTIFACT by its own declaration: every envelope
carries `"authority": "NONE (derived truth)"`, and the baseline states it is
*"a GENERATED OUTPUT of UCOS-RIE-001"*. It was never eligible. Its registration
was a **category error**, not an accounting error.

The `EXCLUDE_DIR_PREFIXES` block names the three classes it exists to exclude:
(1) the generator's own machinery, (2) **its GENERATED outputs**, (3) Operational
Memory. Class (2) was implemented only for `00-BOOK/`-resident outputs.

## 4. This is UCOS-RECON-C1, one leg unclosed

`00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` states its own root
cause as:

> `EXCLUDE_DIR_PREFIXES` listed the generator's machinery and generated outputs
> … **but not `00-MASTER/`** — which did not exist when the list was authored.

Substitute `intelligence/` for `00-MASTER/` and the sentence is unchanged.
RECON-C1 declared the governing principle —

> Repository Corpus = knowledge state (registered). Operational Memory =
> execution state. **Generated Projections = derived state (regenerated, never
> authoritative).** The three are now never mixed.

— and closed the Operational Memory leg. The Generated Projections leg remained
open for any producer emitting outside `00-BOOK/`. `intelligence/` is the first
such producer the repository grew.

## 5. Proximate trigger (why it surfaced at PROGRAM-003 and not earlier)

The gate compares `git status --porcelain` over the four projection subtrees. It
does **not** regenerate RIE. So the failure stayed latent for as long as nobody
re-ran `rie build` after the last atomic registration commit.

| Commit | Position | Effect |
|---|---|---|
| `898ef8d` | older | last commit carrying `00-BOOK/DATA/id-ledger.json` |
| `b47f5b9` | **newer** | regenerated the 10 RIE outputs and committed them **without** the registration half |

From `b47f5b9` onward the committed registry described a *prior* content state of
files whose *later* content state was committed. Six commits later PROGRAM-002 and
PROGRAM-003 were sealed on top of the split. The measured delta was exactly:

- 10 `Modified` change events (`UCHG-000001364…UCHG-000001373`), `commit: null`
- 10 `content_hash` updates in `artifacts.json`
- `id-ledger` seq 8 → 9 for `UCOS-INTELLIGENCE-000002…000011`
- **zero** new identities

`from` hashes equal the registry's recorded values; `to` hashes equal the bytes
committed at HEAD. A textbook split of source from projections — REG-AUTO-001 §7.

## 6. Hypotheses tested and rejected

| Hypothesis | Verdict | Evidence |
|---|---|---|
| Registry engine has a defect / is non-deterministic | **REJECTED** | Two consecutive full transactions produced byte-identical projection subtrees (digest `8b483a13…`). The FAIL was a correct report. |
| Generated reports are wrong | **REJECTED** | The 10 change events are derivable from committed bytes vs committed registry. |
| New work package `00-MASTER/MIP-W1-P001/` was not registered | **REJECTED** | Untracked ⇒ outside the `--cached` eligibility boundary; also under the excluded `00-MASTER/` prefix. Minted 0 identities; appears nowhere in the delta; `awaiting VCS binding: 0`. Doubly ineligible. |
| Registration transaction was interrupted | **REJECTED** | All 10 phases exit 0; enforcement and validation PASS. |
| Registration metadata incomplete / registry index missing entries | **REJECTED** | `enforce`: 1204 eligible = 1204 registered, 0 unregistered, 0 unclassified, 0 invalid — before the repair. |
| Projections regenerated from stale metadata | **REJECTED** | Ledger is append-only and path-keyed; `from` values match the committed registry exactly. |
| Orphan canonical artifacts | **PARTIALLY CONFIRMED, not causal** | `intelligence/UCOS-IMP-BASELINE-001.evidence.json` was registered but has no live producer. Being byte-stable it never drifted. Retired with the family. |
| Canonical source changed without projection regeneration | **CONFIRMED as the trigger, not the cause** | `b47f5b9`. But any regeneration would have produced it — see §2. |

## 7. Why the obvious repair was refused

"Run `register.sh` and commit" clears the symptom. It was refused because §2
proves it is guaranteed to break on the next `rie build` — which is exactly what
had already happened three times (`1c6e750` "registration drift cleared",
`898ef8d` "reconcile the working tree into the commit", and this incident). A
repair known in advance to fail again is a make-the-status-green patch.

## 8. Repair, in one line of consequence

Two `startswith` family prefixes were appended to the designated declaration:

```python
"intelligence/UCOS-RIE-",
"intelligence/UCOS-IMP-BASELINE-001.",
```

No engine logic, no classifier, no generated output was hand-edited. The files
remain **tracked**, so every consumer and every declared substrate pointer keeps
resolving; only their *corpus registration* is withdrawn.

**Proof the cause is gone, not masked:** `python -m intelligence.rie build`
regenerates all ten outputs and then
`git status --porcelain -- 00-BOOK` is **empty**. Before `214c1a9` the same
command produced ten change events, ten hash rewrites and a ledger append.

---

*END — UCOS-RECON-C2 ROOT CAUSE REPORT · AUTHORITY = NONE (DERIVED TRUTH)*

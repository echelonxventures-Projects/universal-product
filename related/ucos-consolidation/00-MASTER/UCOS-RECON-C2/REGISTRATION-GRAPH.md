# UCOS-RECON-C2 — REGISTRATION GRAPH · WHERE THE DIVERGENCE OCCURRED

| Field | Value |
|-------|-------|
| AUTHORITY | **NONE — DERIVED TRUTH** |
| PURPOSE | Trace Canonical Source → Registration Engine → Registry → Projection → Certification and locate the divergence exactly |

---

## 1. The chain, as implemented

Every node below is a real file or entry point in this repository. Nothing is
illustrative.

```
CANONICAL SOURCE          eligibility boundary          REGISTRATION ENGINE
──────────────────        ────────────────────          ───────────────────
git ls-files --cached ──► ukb.py::_repo_artifact_paths ─► ukb.py::_iter_files
--exclude-standard        (GOV-005 §5.1 / ELIG-RC-1)     ∩ INCLUDE_EXTENSIONS
                                                         ∖ EXCLUDE_DIR_PREFIXES  ◄── THE SOLE
                                                                │                     ADMISSION
                                                                ▼                     RULE
                                             register.sh (REG-AUTO-001, 10 phases)
                                             0 enforce --pre
                                             1 ukb build ──────────────┐
                                             2 ukbx sync --due         │
                                             3 ukbx twin               │
                                             4 ukbx portal             │
                                             5 ukb validate            │
                                             6 ukbx validate           │
                                             7 ukbx twin --check       │
                                             8 ukbx certify            │
                                             9 enforce (post)          │
                                                                       ▼
REGISTRY (append-only)                                    PROJECTIONS (derived)
──────────────────────                                    ─────────────────────
00-BOOK/DATA/id-ledger.json      ──────────────►  00-BOOK/REGISTRIES/*.md
  by_path, history, page_cursor,                  00-BOOK/CONTROL-TOWER/*.md
  category_seq                                    00-BOOK/PORTAL/*.md
00-BOOK/DATA/artifacts.json                       00-BOOK/DATA/{relationships,
  content_hash per artifact                         change-ledger,control-tower,
                                                    twin,volumes,certification}.json
                                                                       │
                                                                       ▼
                                                          CERTIFICATION
                                                          ─────────────
                                        register.sh --guard  = CK-REG-DRIFT
                                        git status --porcelain -- \
                                          00-BOOK/{DATA,REGISTRIES,
                                                   CONTROL-TOWER,PORTAL}
                                        empty ⇒ exit 0 ; non-empty ⇒ exit 3
                                                                       │
                                        G-07 Registry Gate = {CK-REG-ENFORCE,
                                                              CK-REG-DRIFT}
                                                                       │
                                        UCCEP-000000 --tier full ⇒ certification
```

## 2. The defect: a cycle, not a break

The chain above is acyclic **only if** every registered artifact's content is
independent of the registry and of the commit. The RIE family violated both.

```
        ┌──────────────────────────────────────────────────────────┐
        │                                                          │
        ▼                                                          │
  intelligence/UCOS-RIE-*.json                                     │
  intelligence/UCOS-IMP-BASELINE-001.*.json                        │
        │                                                          │
        │ was ELIGIBLE (tracked .json, no prefix matched)           │
        ▼                                                          │
  ukb build records content_hash  ──►  00-BOOK/DATA/artifacts.json  │
        │                                    │                     │
        │                                    │ sha256 of this file  │
        │                                    │ is embedded in the   │
        │                                    │ RIE output ──────────┘  (cycle A)
        │
        ▼
  commit ──► HEAD changes ──► RIE output embeds new HEAD ──► content_hash
        │                     (evidence_state.head, generation.source_commit,
        │                      generation.generation_timestamp)
        └──────────────────────────────────────────────────────► (cycle B)

  coverage.xml (GITIGNORED — an ENVIRONMENT non-artifact)
        └──► code.coverage_*, evidence_state.coverage_measurement ──► (leak C)
```

- **Cycle A** — registry ⇄ intelligence. Registration rewrites `artifacts.json`;
  its hash is an input to the artifact being registered.
- **Cycle B** — commit ⇄ intelligence. Any commit changes `HEAD`; `HEAD` is an
  input to the artifact being committed. Closing it needs a commit whose hash is
  inside its own tree.
- **Leak C** — a registered artifact whose content depends on a file the ignore
  authority declares a non-artifact, so the commit cannot reproduce it.

Cycle B alone makes the fixpoint unreachable. Cycles A and B together make the
gate unsatisfiable in principle, independent of operator discipline.

## 3. Exact divergence point

| Stage | Sound? | Finding |
|---|---|---|
| Canonical source (`git ls-files --cached`) | ✔ | Identical in every environment at a commit (B-01c). |
| **Eligibility boundary (`EXCLUDE_DIR_PREFIXES`)** | ✘ | **DIVERGENCE ORIGINATES HERE.** Class-(2) generated outputs were covered only under `00-BOOK/`. |
| Registration engine (`register.sh`, 10 phases) | ✔ | All phases exit 0; idempotent; enforcement and validation PASS. |
| Registry (`id-ledger`, `artifacts.json`) | ✔ | Append-only, path-keyed, monotonic. Recorded the truth it was given. |
| Projections (REGISTRIES/CONTROL-TOWER/PORTAL/DATA) | ✔ | Deterministic; byte-stable modulo neutralized stamps. |
| Certification (`--guard`, G-07, UCCEP) | ✔ | Reported the divergence correctly, fail-closed. |

**The engine did not fail. It faithfully registered something that was never an
eligible artifact.** Every downstream stage then behaved correctly, which is why
the failure presented as an unfixable drift rather than as an error.

## 4. Blast radius of the one rule

All of the following are downstream of that single prefix list — none has an
independent admission rule:

- Generators: `ukb.py cmd_build`, `ukbx.py {sync,twin,portal,certify}`, `register.sh`
- Registries: UNIVERSAL-ARTIFACT, UNIVERSAL-PAGE, KNOWLEDGE-GRAPH,
  CHANGE-VERSION-LINEAGE, CERTIFICATION, VOLUME
- Portal: 1 page per artifact + `index.md` + `UCOS-BOOK-000000.md`
- Ledgers: `id-ledger.json`, `change-ledger.json`, `relationships.json`
- Twin / dashboard: `control-tower.json`, `PROGRAM-CONTROL-TOWER.md`
- Gates: CK-REG-ENFORCE, CK-REG-VALIDATE, CK-REG-DRIFT → G-06, G-07 → UCCEP

## 5. The chain after repair

```
  intelligence/UCOS-RIE-*  ──► matched by EXCLUDE_DIR_PREFIXES ──► NOT ELIGIBLE
        │                                                              │
        │ still TRACKED (committed repository content)                  │
        ▼                                                              ▼
  consumers keep resolving:                            registry no longer records
   · rib-blueprint SUB-RIE-{CAPS,BASELINE,               their content_hash
     DEPS,FRONTIER} (required + tracked)                      │
   · platform/repository_intelligence                          ▼
     (live producer first, artifact second)         cycles A and B are CUT
   · intelligence/tests (in-memory outputs())       leak C is outside the corpus
```

Cycle A is cut because the registry no longer reads their hashes. Cycle B is cut
because nothing the commit must contain depends on the commit's own identity.

**Measured:** `python -m intelligence.rie build` followed by `register.sh` leaves
`git status --porcelain -- 00-BOOK` empty, and the projection-subtree digest
unchanged at `8b483a1340b2c2d25544528439a3396d8fd8b10e809c1795b61019304c09b78c`.

## 6. Residual, declared

RIE outputs still embed `HEAD`, so they are inherently **one commit stale** after
any commit that contains them. This is anchor lag, not registration drift:

- It perturbs the registry by **zero bytes** (§5).
- It is bounded: regenerate once, commit once, stop.
- It does surface in `UCOS-RIB-001` GATE-12 (`dirty_entries_outside_generated`)
  until the regeneration is committed. GATE-12 is a working-tree cleanliness
  check evaluated on a clean checkout in CI, where it passes.

Anchoring derived truth to a commit is the design intent
(`input_hash_basis`: *"…and HEAD, which pins the whole tracked tree"*). The
constitutional error was never the anchor — it was registering the anchored
output as corpus.

---

*END — UCOS-RECON-C2 REGISTRATION GRAPH · AUTHORITY = NONE (DERIVED TRUTH)*

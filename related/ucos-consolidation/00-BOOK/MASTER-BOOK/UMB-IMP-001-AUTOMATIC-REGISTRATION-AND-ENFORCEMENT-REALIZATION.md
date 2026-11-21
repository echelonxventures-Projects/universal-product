# UCOS Ω∞ — UMB-IMP-001 · AUTOMATIC REGISTRATION AND ENFORCEMENT REALIZATION

> **STATUS DOMAIN:** IMPLEMENTATION (DOMAIN-C — code that exists and runs)
> **STATUS BASIS:** The realized machinery in `00-BOOK/tools/{config.py,ukb.py,register.sh}`, `.kiro/hooks/auto-register-artifact.json`, `.github/workflows/ucos-registration-gate.yml`, and the append-only audit `00-BOOK/DATA/enforcement-audit.json` — plus live execution this session (`ukb.py enforce --pre/post`, full `register.sh` transaction `CERTIFIED (hard checks 7/7)`, `ukb.py validate`, `ukbx.py validate`, and isolated positive/negative gate tests). Evidence only; no projection.

| Field | Value |
|-------|-------|
| ARTIFACT ID | UMB-IMP-001 |
| ARTIFACT | Automatic Registration and Enforcement Realization |
| PROGRAM | UCOS Ω∞ Universal Master Book Architecture Program (UMB) |
| CLASSIFICATION | Implementation Realization — the first operational capability of the UMB architecture: automatic participation (auto-registration) + the minimum unskippable enforcement gates |
| STATUS | ACTIVE · IMPLEMENTATION |
| PARENT | UMB-000 |
| DEPENDS-ON | UMB-READINESS-001 (gap source); UMB-005/006/007/012/016/017/020 (read-only targets); STATUS-001; REG-AUTO-001; UCI-001; AUTH-INF-001; UMB-000 |
| CONSUMES (read-only) | `00-BOOK/DATA/*.json`; `00-BOOK/REGISTRIES/*`; `00-BOOK/PORTAL/*`; UMB-000…020; UMB-READINESS-001 |
| PRODUCES (append-only, machinery — not registered artifacts) | `config.py` metadata/enforcement config; `ukb.py` `read_metadata()`/metadata-fallback `classify()`/discovered-volume registration/`cmd_enforce()`+audit; `register.sh` pre/post gates + re-entrancy lock + `--install-hooks`; broadened `.kiro/hooks/auto-register-artifact.json`; `.github/workflows/ucos-registration-gate.yml`; `00-BOOK/DATA/enforcement-audit.json` |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| VOLUME | VOL-022 (MASTER BOOK ARCHITECTURE) |
| BASELINE DATE | 2026-07-16 |

*This is an implementation artifact. It realizes — in reusable, standard-library machinery — the single capability UMB-READINESS-001 identified as the highest-leverage, lowest-dependency gap (P0): converting the existing operator-driven registration transaction into automatic participation guarded by unskippable enforcement gates. It creates no new architecture family, no new registry, no new identifier namespace, and no lifecycle; it reuses the existing engines (`ukb.py`, `ukbx.py`), the existing Atomic Registration Transaction (`register.sh`), the existing classification config (`config.py`), and the existing connector/signal framework exclusively. It is append-only and authority-neutral, subordinate to the frozen constitutional corpus, STATUS-001, REG-AUTO-001, UCI-001, and AUTH-INF-001; where any statement conflicts with a higher instrument, the higher instrument governs and the statement is void to the extent of the conflict.*

---

## SECTION 1 — IMPLEMENTATION SCOPE

**In scope (realized by this artifact).**
1. **Automatic participation.** Any newly created in-scope artifact automatically becomes eligible for, and — on the next transaction — acquires: Identity, Registration, Classification, Validation, Registry participation, Knowledge-Graph participation, Traceability participation, and Certification participation, without manual discovery.
2. **Enforcement gates.** The minimum set of gates that make "Artifact Creation = Artifact Registration" (REG-AUTO-001 §7) *unskippable*, so that no unregistered, unclassified, or invalid artifact can silently enter the corpus.
3. **Metadata-driven discovery.** New documents, programs, volumes, families, artifact types, domains, and future artifact classes are discovered from configuration and artifact metadata — never from hard-coded lists.
4. **Audit + recovery.** An append-only enforcement audit records every gate outcome; failure is fail-closed and recovery is forward-only and idempotent.

**Out of scope (explicitly not built here; unchanged).** Typed traceability edges (UMB-007), the Change engine (UMB-008), semantic search (UMB-013), binary publication formats (UMB-011), live connectors (UMB-012 data), predictive AI (UMB-014), and security-zone enforcement (UMB-015). These remain future work per UMB-READINESS-001 §6 and are neither claimed nor implied here (STATUS-001 §2 non-projection).

**Governing constraint.** Exactly **one** registered artifact is created by this mission (this document). All executable changes are made to the generator *machinery*, which is excluded from registration by design (`config.py::EXCLUDE_DIR_PREFIXES` includes `00-BOOK/tools/`), so the corpus gains one artifact, not an architecture family.

---

## SECTION 2 — CURRENT-STATE ANALYSIS

Direct inspection + live execution established the pre-implementation state (consistent with UMB-READINESS-001 §§3–5, §11):

| Capability | Pre-state | Evidence |
|-----------|-----------|----------|
| Identity / ID+page ledger | REAL, append-only | `id-ledger.json`; `ukb validate` append-only proof |
| Registration transaction `T` | REAL, deterministic, idempotent, **manual** | `register.sh` 6 phases; run by hand only |
| Classification | Config-rule driven; **46 artifacts fell to `OTHER/MISC/VOL-000`** | `artifacts.json` program histogram |
| Knowledge-graph / portal / certification | REAL over the corpus | `relationships.json`; `PORTAL/`; `twin --check` 7/7 |
| **Auto-registration (trigger)** | **NOT OPERATIONAL** | one `PostFileCreate` hook matching only `09-PLATFORM/PLATFORM-.*\.md$` |
| **Enforcement gates** | **INCOMPLETE** | commit gate absent (`.git/hooks` = samples); CI gate absent; classification fallback silent |

**Proof of the gap (observed live).** At session start, `ukb.py enforce --pre` reported **290 eligible / 289 registered** — the file `00-BOOK/MASTER-BOOK/UMB-READINESS-001-…md` existed on disk but was **absent from every register**: the exact "artifact exists but registry unaware" divergence REG-AUTO-001 forbids, occurring because no gate fires under `00-BOOK/MASTER-BOOK/`.

---

## SECTION 3 — REUSE ANALYSIS

Per the mission's "reuse existing implementation wherever possible; do not create replacement systems," every requirement maps to an existing mechanism; only thin, additive layers were written.

| Requirement | Reused existing mechanism | Net-new (additive) |
|-------------|---------------------------|--------------------|
| Discovery | `ukb.py::_iter_files` (full-repo scan), `config.py::INCLUDE_EXTENSIONS`/`EXCLUDE_DIR_PREFIXES` | none — reused verbatim |
| Classification | `ukb.py::classify` + `config.py::CLASSIFY_RULES` | metadata fallback + discovered volumes |
| Identity / pages | `ukb.py::allocate` + `id-ledger.json` | discovered-volume serials (append-only in the same ledger) |
| Registration / sync | `register.sh` Atomic Transaction `T` (build→twin→portal→validate×2→certify) | pre/post gate phases wrapping `T` |
| Validation | `ukb.py validate` (structural), `ukbx.py validate` (twin) | eligibility/validity/classification/parity gate |
| Certification | `ukbx.py twin --check` (hard checks 7/7) | reused verbatim as gate Phase 6 |
| Authoring trigger | existing `PostFileCreate` Kiro hook | broadened matcher (config-driven) |
| Commit / CI gate | existing `register.sh --guard` drift logic | `--install-hooks` + CI workflow that invoke it |
| Audit | append-only JSON convention used across `DATA/` | `enforcement-audit.json` with per-mode dedup |

No engine was replaced; no registry, identifier namespace, or lifecycle was created (UCI-001 INTEGRATION MODEL preserved).

---

## SECTION 4 — IMPLEMENTATION DESIGN

The realization is four thin layers over the existing engines.

**4.1 Metadata-driven classification (`ukb.py::read_metadata`, `classify`).**
`classify(relpath, abspath)` now resolves in strict, append-only order:
1. **Ordered `CLASSIFY_RULES`** — unchanged; existing families keep their exact classification (first match wins).
2. **Self-declared metadata** — `read_metadata()` parses the artifact's own front-matter table for `PROGRAM/CATEGORY/VOLUME/FAMILY/DOMAIN` (labels in `config.py::METADATA_CLASSIFY_KEYS`). Only **well-formed codes** are accepted (`program/category` match `^[A-Z][A-Z0-9]{1,19}$`; `volume` matches `^VOL-\d{3}$`); a legacy artifact that declares a long descriptive program *name* is therefore **not** reclassified (append-only safety).
3. **`DEFAULT_CLASS`** — last resort, surfaced (never hidden) by the classification gate.
Because metadata is consulted **only** when no rule matches (previously → `OTHER`), the change can only rescue a formerly-`OTHER` artifact; it can never alter a prior classification. Verified: **0** existing artifacts reclassified.

**4.2 Discovered volumes (`ukb.py::cmd_build`).** When a metadata-declared `VOLUME` is not one of the permanent `config.py::VOLUMES`, it is auto-registered append-only into `id-ledger.json` (`discovered_volumes`, `volume_seq`) with a stable serial and emitted into `volumes.json`. Unlimited future volumes thus require no config edit.

**4.3 Enforcement gate (`ukb.py::cmd_enforce`).** A pure read of disk (`_iter_files`) vs. the registers (`artifacts.json`) computing three sets — `invalid`, `unclassified` (program==`OTHER`), `unregistered` — under two modes (`--pre`, post). Fail-closed (`exit 1`) on blocking violations; every run appends a fingerprinted, de-duplicated record to the audit log.

**4.4 Automatic triggering (`register.sh`, hook, CI).** The transaction is bracketed by the gates and made automatic by three layered triggers (Section 9).

---

## SECTION 5 — ENFORCEMENT DESIGN

The **minimum** gate set is four checks, ordered fail-fast (`config.py::ENFORCEMENT_GATES`):

| Gate | Question | Blocks (fail-closed) |
|------|----------|----------------------|
| **eligibility** | Is the file in scope? | (filter, not a violation) |
| **validity** | Readable + non-empty + resolvable title? | invalid artifact |
| **classification** | Resolves to a real class (program ≠ `OTHER`)? | unclassified **new** artifact |
| **registration** | Present in every register (count parity)? | unregistered eligible artifact |

**Two enforcement points, both unskippable when wired (REG-AUTO-001 §16 three-gate model):**
- **Pre-registration** (`enforce --pre`, `register.sh` Phase 0): gates only *newly-created* (unregistered) files — an invalid or unclassifiable new artifact **blocks the transaction before it can enter** the corpus.
- **Post-registration** (`enforce`, `register.sh` Phase 7): asserts full count parity (every eligible file is now registered) and validity; records the outcome.

Legacy artifacts already in the `OTHER` fallback are reported as **advisory** (they are visible, not silent); `--strict` promotes them to blocking. This satisfies "unclassified artifacts cannot **silently** enter" without a disruptive mass-reclassification (append-only; consistent with REG-AUTO-001 §13 "misclassified → flagged, not silently reclassified").

**Verified negative test (isolated repo):** an empty file (`invalid`) and a rule-less/metadata-less file (`unclassified`) both caused `ENFORCEMENT FAILED … exit 1`, while a valid+classifiable book root passed — proving the gate blocks rather than trusts.

---

## SECTION 6 — DISCOVERY DESIGN (ZERO HARD CODING · INFINITE EXPANSION)

Discovery is entirely configuration- or metadata-driven; **no** program, artifact, volume, domain, or family list is hard-coded in the discovery path.

| Discovered thing | Mechanism | Config/metadata source |
|------------------|-----------|------------------------|
| New **documents** | full-repo `os.walk` scan | `INCLUDE_EXTENSIONS` / `EXCLUDE_DIR_PREFIXES` |
| New **programs / families / artifact types / domains** | `CLASSIFY_RULES` (existing families) **or** self-declared front-matter metadata (new families) | `CLASSIFY_RULES`, `METADATA_CLASSIFY_KEYS` |
| New **volumes** | discovered-volume auto-registration | artifact `VOLUME` metadata → `id-ledger.json` |
| New **future artifact classes** | same metadata path; a clean `PROGRAM/CATEGORY` code is enough | artifact metadata |

**Verified infinite-expansion proof (isolated repo, zero config edits):** a synthetic `INFRA-001.md` declaring `| PROGRAM | INFRA |` / `| VOLUME | VOL-099 |` was auto-classified `('INFRA','INFRA','VOL-099')`, allocated a brand-new append-only identity `UCOS-INFRA-000001`, and registered into a newly discovered volume `VOL-099 (INFRASTRUCTURE)` — with no change to `config.py`. This demonstrates unlimited future programs, categories, and volumes without redesign (AUTH-INF-001).

---

## SECTION 7 — VALIDATION DESIGN

Validation reuses the transaction's existing validators and adds the pre-registration checks:

| Stage | Check | Realized by |
|-------|-------|-------------|
| Pre-registration | eligibility · validity · classifiability of new files | `ukb.py enforce --pre` |
| Structural | append-only ledger, no dup IDs/pages, no page overlap, referential integrity | `ukb.py validate` (Phase 4) |
| Twin | signals append-only, subjects resolve, provenance present, secret-free | `ukbx.py validate` (Phase 5) |
| Certification | acyclic deps (C-07), navigation reachability (C-08), control-tower automation (C-09), export/search smoke, provenance (C-04/12) | `ukbx.py twin --check` (Phase 6) |
| Post-registration | count parity + validity + classification report | `ukb.py enforce` (Phase 7) |

**Verified live:** `VALIDATION PASSED — 290 artifacts, append-only page ledger intact, referential integrity OK`; `TWIN VALIDATION PASSED — 12 signals … no embedded secrets`; certification `CERTIFIED (hard checks 7/7)`.

---

## SECTION 8 — FAILURE & RECOVERY DESIGN

**Failure handling (fail-closed, no partial success).**

| Failure | Detection | Outcome / exit |
|---------|-----------|----------------|
| New artifact invalid/unclassified | Phase 0 `enforce --pre` | transaction blocked (exit 4); artifact never enters |
| Build/twin/portal error | Phases 1–3 | INCOMPLETE (exit 1) |
| Structural / twin defect | Phases 4–5 | INCOMPLETE (exit 2) |
| Certification hard-check fail | Phase 6 | NOT-CERTIFIED (exit 2) |
| Unregistered eligible file remains | Phase 7 `enforce` | INCOMPLETE (exit 4) |
| Uncommitted synchronized state | `--guard` | DRIFT (exit 3) |

**Recovery (forward-only, idempotent).** Diagnose via the enforce report + `git diff` of the register dirs; for a new family declare a clean metadata row (or add a `CLASSIFY_RULE`); re-run `register.sh`. The append-only ledger guarantees recovery never disturbs previously-allocated identities or pages. **Idempotence verified:** repeated transactions leave the audit log stable (per-mode fingerprint dedup) and re-certify identically.

---

## SECTION 9 — INTEGRATION DESIGN

The gates integrate as the existing transaction plus three layered automatic triggers — the REG-AUTO-001 §16 model, now fully realized:

```
register.sh (Atomic Transaction T, UMB-IMP-001 gated):
  Phase 0  ukb enforce --pre     ← pre-registration gate (blocks silent entry)
  Phase 1  ukb build             ← identity, registry, graph, deps, control-tower, pages
  Phase 2  ukbx twin             ← digital twin + control-tower dimensions
  Phase 3  ukbx portal           ← navigation (no dead ends)
  Phase 4  ukb validate          ← structural invariants
  Phase 5  ukbx validate         ← twin/signal integrity
  Phase 6  ukbx twin --check     ← digital-twin certification (7/7)
  Phase 7  ukb enforce           ← post-registration parity gate + audit
  Phase 8  seal
```

| Gate | Trigger | Wiring |
|------|---------|--------|
| Authoring (gate 1) | `PostFileCreate` Kiro hook, matcher `\.(md\|txt\|docx)$` | `.kiro/hooks/auto-register-artifact.json` → `register.sh` (eligibility decided by config, so every future family is covered; re-entrancy lock prevents self-trigger loops) |
| Commit (gate 2) | git `pre-commit` (opt-in) | `register.sh --install-hooks` writes a hook running `register.sh --guard` (git config unchanged) |
| CI (gate 3) | GitHub Actions on push/PR | `.github/workflows/ucos-registration-gate.yml` runs `enforce --pre` + `register.sh --guard`; non-zero exit blocks merge |

A bypass of gate 1 is caught by gate 2; a bypass of gate 2 is caught by gate 3 — enforcement by construction, not discipline (REG-AUTO-001 P7).

---

## SECTION 10 — TESTING DESIGN

| Test | Type | Result |
|------|------|--------|
| `enforce --pre` at session start | integration (real corpus) | detected 290 eligible / 289 registered — the live gap (PASS: classifiable) |
| `enforce` post before build | negative (parity) | `ENFORCEMENT FAILED` exit 1 (expected) |
| empty + rule-less file in isolated repo | negative (validity + classification) | `ENFORCEMENT FAILED` exit 1 (expected) |
| clean new family `INFRA`/`VOL-099` in isolated repo | positive (discovery + expansion) | classified + `UCOS-INFRA-000001` + discovered volume, zero config edits |
| legacy `12-APPLICATION` descriptive-name files | regression (append-only) | remain `OTHER` — 0 reclassified |
| full `register.sh` × repeated | idempotence | `CERTIFIED 7/7`; audit log stable; append-only intact |
| this artifact's own creation | end-to-end (Section 12) | auto-registered on the next transaction |

Isolated tests redirect the engine's paths to a temp repo so the permanent ledger/audit are never polluted.

---

## SECTION 11 — OPERATIONAL DESIGN

- **Normal operation:** authors create artifacts; the authoring hook (or a later commit/CI run) fires `register.sh`, which gates, registers, synchronizes all seven registers, re-certifies, and audits — no manual step.
- **Observability:** `00-BOOK/DATA/enforcement-audit.json` is the append-only operational log of gate outcomes (mode, result, eligible/registered counts, offending paths). Consecutive identical states per mode are de-duplicated so the log is drift-free under idempotent re-runs.
- **Safety:** the re-entrancy lock (`00-BOOK/tools/.register.lock`, git-ignored, outside the scan and guard sets) makes nested/concurrent invocations no-ops and protects the append-only ledger from races.
- **Manual override:** `register.sh --strict` escalates classification advisories to blocking; `--guard` adds the drift gate for CI/commit; `--install-hooks` installs the commit gate.

---

## SECTION 12 — IMPLEMENTATION ACCEPTANCE CRITERIA & SELF-REGISTRATION DEMONSTRATION

**Acceptance criteria.**

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| AC-1 | A newly created artifact automatically participates end-to-end | MET | this artifact's registration (below) |
| AC-2 | Unregistered artifacts cannot silently enter | MET | pre/post gates fail-closed; live 290/289 gap surfaced |
| AC-3 | Unclassified new artifacts cannot silently enter | MET | negative test blocks rule-less file |
| AC-4 | Invalid artifacts cannot silently enter | MET | negative test blocks empty file |
| AC-5 | Zero hard coding (config/metadata-driven discovery) | MET | `INFRA`/`VOL-099` expansion with no config edit |
| AC-6 | Infinite expansion (programs/volumes/families) | MET | discovered-volume + metadata classification |
| AC-7 | No architectural/registry/identity redesign | MET | reuse table (Section 3); 0 reclassified |
| AC-8 | Append-only; idempotent | MET | ledger intact; audit stable across re-runs |
| AC-9 | Compatible with STATUS-001/REG-AUTO-001/UCI-001/AUTH-INF-001 | MET | Section 13 |
| AC-10 | Exactly one artifact created | MET | only this `.md`; all else is excluded machinery |

**Self-registration demonstration (populated by the registration run at the end of this mission).**

Creating this file left it in state `GENERATED` (on disk, unregistered). Running the Atomic Registration Transaction moved it to `REGISTERED` with **no manual per-artifact wiring** — the `^00-BOOK/MASTER-BOOK/` rule classified it, the ledger allocated its identity/pages append-only, the graph parented it to the UMB program root, the portal generated its page, and certification passed:

| Property | Before | After |
|----------|--------|-------|
| Total registered artifacts | 290 | **291** |
| This artifact's Universal ID | — (unregistered) | **`UCOS-UMB-000023`** |
| Native ID (preserved verbatim) | — | **UMB-IMP-001** |
| Program / Category / Volume | — | **UMB / UMB / VOL-022** |
| Parent (Knowledge-Graph) | — | **`UCOS-UMB-000001`** (UMB-000 master index) |
| Portal page | — | **`00-BOOK/PORTAL/UCOS-UMB-000023.md`** (breadcrumbs + backlinks, no dead end) |
| Certification | — | **CERTIFIED (hard checks 7/7)** |
| Post-registration enforcement | 290 eligible / 290 registered | **291 / 291 — parity, no unregistered** |

Thus a newly created artifact automatically acquired Identity, Registry participation, Classification, Validation, Knowledge-Graph participation, Dependency/Navigation participation, Certification participation, and Audit participation — the mission's definition of a participating UCOS entity.

---

## SECTION 13 — COMPATIBILITY WITH GOVERNING STANDARDS

- **STATUS-001.** This artifact declares STATUS DOMAIN + STATUS BASIS (§3 mandatory); it is a DOMAIN-C (implementation) claim evidenced by code + live execution, and asserts nothing about roadmap/certification/operational completion (§2 non-projection). Registration records existence + declared status only.
- **REG-AUTO-001.** Realizes the create=register binding (§7 `T`), the seven-register synchronization (§8–§12), the failure/recovery model (§13–§14), and completes the three-gate compliance model (§16) that was previously one narrow hook.
- **UCI-001.** Introduces no registry, engine, identifier namespace, lifecycle, or state store; reuses `artifact`/`relationship`/`signal` structures and the existing transaction exclusively (INTEGRATION MODEL / CP-6 reuse-only). The enforcement audit is an operational log, not a change registry.
- **AUTH-INF-001.** Discovery is configuration/metadata-driven with no hard-coded program/volume/family/domain limits; unlimited future artifacts, programs, volumes, and families are supported without redesign.

---

## AUTHORITY BOUNDARY (MANDATORY)

UMB-IMP-001 holds no constituent, governance, ratification, or EC-series authority and cannot authorize EC-1. It is an implementation realization only, append-only, subordinate to the frozen constitutional corpus, the Technology Constitution, STATUS-001, REG-AUTO-001, UCI-001, AUTH-INF-001, UMB-000…020, and all prior determinations. It creates no new architecture family, registry, identifier namespace, or lifecycle; it renumbers nothing; it modifies no frozen or historical artifact; it treats `00-SOURCE/`/`99-FREEZE/` as read-only; and it embeds no secret (RR-07). Per STATUS-001 §2, realizing this implementation capability projects no completion of any other domain. Any conflicting statement is void to the extent of the conflict.

## CERTIFICATION

| Attribute | Value |
|-----------|-------|
| Artifact Status | ACTIVE · IMPLEMENTATION |
| Evidence basis | Realized machinery + live execution (`enforce`, `register.sh` CERTIFIED 7/7, `validate`×2, isolated gate tests) 2026-07-16 |
| Method | Reuse-first realization; reality-as-it-exists; no fabrication |
| Scope verdict | First operational capability (auto-registration + enforcement) — REALIZED |
| Append-only verdict | PASS — 0 existing artifacts reclassified; ledger intact |
| Zero-hard-coding / infinite-expansion verdict | PASS — INFRA/VOL-099 expansion with no config edit |
| Authority | IMPLEMENTATION ONLY — NONE |

*Return: [UMB-000 Master Index](UMB-000-MASTER-BOOK-ARCHITECTURE-MASTER-INDEX.md) · [UMB-READINESS-001](UMB-READINESS-001-MASTER-BOOK-IMPLEMENTATION-READINESS-DETERMINATION.md) · [UMB-020 Universal Participation](UMB-020-SUCCESS-CRITERIA-AND-UNIVERSAL-PARTICIPATION-DEMONSTRATION.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*

**END OF ARTIFACT — UMB-IMP-001 · ACTIVE · IMPLEMENTATION · APPEND-ONLY · AUTHORITY-NEUTRAL · AUTOMATIC REGISTRATION AND ENFORCEMENT REALIZATION**

# CAEM-001 · OUTPUT 03 — PHASE 1 · HARD-CODED ASSUMPTION REGISTER

> **AUTHORITY = NONE — DERIVED TRUTH.** · **`CERTIFIED-PROVISIONAL`; Tier T1 VACANT** (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`).
>
> **No new finding family is minted.** New findings continue the **existing** `UCOS-ACFV-000001` series (`AG` architectural · `RG` repository · `IG` implementation · `GG` governance), per `GOV-001-N1`.

Mission Phase 1 requires proof that the architecture assumes none of 20 named things. The repository has already answered this **twice, at two levels of rigour, and the two answers disagree** — this output reconciles them and adds seven independently verified findings.

| Prior instrument | Baseline | Verdict |
|---|---|---|
| `04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md` (23 axes) | `ab78f35` · 2026-07-23 | "NONE CERTIFIED (foundation), LOW residual risk" — **but self-flags an ASSUMPTION**: *"An exhaustive line-by-line proof of absence across all 431 concepts was not performed."* |
| `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md` (16 axes) | `ab78f35` · 2026-07-23 | "all 16 CERTIFIED UNBOUNDED" — citation table + keyword count only; **no code inspection** |
| `engine/kernel/compliance.py` (18 prohibited tokens + 11 unknown categories) | live, CI-enforced | **Executed proof** — but scoped to `engine/kernel/**` only |
| `UCOS-ACFV-000001` (adversarial, 6 tracks, commands executed) | `527485a` · 2026-07-25 | **Verdict C — ARCHITECTURE NOT YET CLOSED · CERTIFICATION DENIED**; explicitly falsifies the two certifications above (`GG-06`) |

**`527485a` is an ancestor of the current HEAD `df763bf`.** ACFV's findings are therefore the live state of record unless separately remediated.

---

## §1 — THE 20 FORBIDDEN ASSUMPTIONS vs. ACTUAL COVERAGE

**DOC** = the 23-axis certification (keyword scan + scope-exclusion argument). **EXEC** = an executed, CI-enforced probe.

| # | Forbidden assumption | Coverage | Evidence |
|---|---|---|---|
| 1 | Earth | **DOC + EXEC** | DOC axis 7 "Planet: NONE"; `PROHIBITED_TOKENS` `"earth"`; CI gate id `no-domain-provider-technology-earth-civilization-coupling` |
| 2 | Country | **EXEC only** | `PROHIBITED_TOKENS` `"country"`. No DOC axis. |
| 3 | Language | **EXEC only** | token `"language"`; `UNKNOWN_CATEGORIES` includes `LanguageFamily/Glyphic-Resonance`. **Leaks — see IG-06.** |
| 4 | Currency | **EXEC only** | token `"currency"`; `ValueExchangeSystem/Entropy-Credit` admissible. **Violated — see RG-10.** |
| 5 | Calendar | **EXEC only** | token `"calendar"`; `TemporalModel/Branching-Retrocausal`. DOC axis 12 covers time *dimensionality*, not calendar systems. **Leaks — see IG-07.** |
| 6 | Tax | **EXEC only** | token `"tax"`; `TaxationModel/Gradient-Levy` |
| 7 | Technology | **DOC + EXEC** | DOC axis 1 (`CEP-007` II.2 SHALL NOT legislate technology); ACFV S-1 verified 0 product names in 55 Technology-Constitution principles; `_TECH_MARKERS` denylists reject any record naming a product |
| 8 | Cloud | **DOC + EXEC** | DOC axis 4; token `"cloud"`; `PROHIBITED_VENDOR_TOKENS` aws/azure/gcp. **Partially violated — see IG-08.** |
| 9 | Database | **DOC + EXEC** | DOC axis 5; token `"database"`; vendor tokens postgresql/mongodb/redis |
| 10 | Programming language | **DOC only** | DOC axis 2. Not a prohibited token. Realization is Python-only and stdlib-only by declared choice (`dependencies = []`) |
| 11 | **Operating system** | **NOT COVERED** | Absent from all 23 DOC axes and from both token lists. Nearest proxies: DOC axis 3 Infrastructure, axis 6 Runtime |
| 12 | Business domain | **PARTIAL** | token `"industry"`; no DOC axis. Prose assertion in `engine/kernel/__init__.py` |
| 13 | **ERP** | **NOT COVERED** | Never named in any axis or token list. Proxies only: `company`/`product`/`customer`/`order` |
| 14 | **CRM** | **NOT COVERED** | Same; proxy `customer` only |
| 15 | **Commerce** | **NOT COVERED — and confirmed as a live gap** | ACFV `RG-05`; `GG-06` notes neither axis list contains a commercial axis, *so neither could have detected it* |
| 16 | **Healthcare** | **NOT COVERED** | No axis, no token, no scan |
| 17 | Government | **PARTIAL / equivocal** | DOC axis 15 + unboundedness axis 13 certify *governance-model* neutrality; **neither addresses government as a business domain** |
| 18 | Human civilization | **DOC + EXEC** | DOC axes 8 Species + 9 Civilization; tokens `"human"`,`"earth"`; `Civilization/Xophar-Collective` admissible |
| 19 | Reality | **DOC only** | DOC axis 11 "parametric"; unboundedness axis 10. **No executable probe.** |
| 20 | **Existence** | **NOT COVERED** | Not an axis in either list. Proxies: DOC axis 22 "Unknown constructs", unboundedness axis 16 |

**Score: 6 covered by both DOC and EXEC · 5 by EXEC only · 1 by DOC only · 2 partial · 6 not covered at all** (operating system, ERP, CRM, commerce, healthcare, existence).

### The decisive scope caveat on EXEC

`engine/kernel/compliance.py` computes `leaked = sorted(founding_keys & set(PROHIBITED_TOKENS))` — a **set intersection over the 18 founding meta-type keys only**. `_kernel_has_no_closed_enum()` globs `_KERNEL_DIR.glob("*.py")` — **`engine/kernel/` only**. `engine/provider/compliance.py` is likewise `_PROVIDER_DIR`-scoped.

Neither probe scans `platform/`, `data/`, `service/`, `application/`, `infrastructure/`, or `intelligence/`. It is a genuine executable proof of a genuinely **narrow** claim: *the meta-kernel contains none of these tokens and can register all of them.* It is **not** a repository-wide absence proof — and every finding in §2 below sits outside its scope.

---

## §2 — FINDINGS VERIFIED AT `df763bf` (this session, by direct command)

### RG-09-A — **The frozen schema's identifier ceiling has been breached: `ukb validate` FAILS with 539 problems** · HIGH · NEW

| Field | Determination |
|---|---|
| Finding | `00-BOOK/SCHEMAS/artifact.schema.json:20` hard-codes `"pattern": "^UCOS-[A-Z]{2,6}-[0-9]{6}$"`. **539 of 1,193 registered artifacts (45.2%) violate it.** Every one of the 539 problems is this single pattern. |
| Verified | `python3 00-BOOK/tools/ukb.py validate` → `VALIDATION FAILED — 539 problem(s)`, **exit 1** |
| Breakdown | structural problems **0** · schema problems **539** · execution-register problems **0**. Corpus *integrity* is intact; the **schema** is what is wrong. |
| Namespaces breaching the 6-character ceiling | `UCOS-SERVICE` 149 · `UCOS-INFRASTRUCTU` 132 · `UCOS-APPLICATION` 121 · `UCOS-IMPLEMENTATI` 12 · `UCOS-IAC001C` 9 · `UCOS-IAC001E` 9 · `UCOS-EVOUSIS014/015/016` 9 each · `UCOS-IAC001B` 8 · `UCOS-IAC001D` 8 · `UCOS-IAC001A` 7 · `UCOS-ARCHITECTURA` 3 · `UCOS-FINALCERTIFI` 2 · `UCOS-VALIDATIONRE` 2 · others 1 each |
| Root cause | A hard-coded finite assumption — namespace ≤ 6 characters — that the repository's own registration engine outgrew. `SERVICE` is 7. Companion ceilings in the same file: `^VOL-[0-9]{3}$` (1,000 volumes), `[0-9]{6}` (10⁶ artifacts), closed 17-value `status`, `additionalProperties: false`. |
| Why it went undetected | **`ukb validate` is wired into no gate.** `verify.sh:105` runs only `ukb.py enforce --pre`. `ucos-registration-gate.yml` runs `eligibility --unbound`, `enforce --pre`, and `register.sh --guard` — **never `validate`**. `enforce --pre` passes cleanly (1,193 = 1,193, zero drift), so every gate is green while validation is red. |
| Compounding | `jsonschema` install in CI is `pip install jsonschema \|\| true` (operator action **OA-3**), so in CI the schema check may silently not run at all. |
| Relation to prior art | This is the live materialization of ACFV **RG-09** (schema hard ceilings inside the frozen corpus) and it **falsifies** `04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION` §3's structural defence that finite choices are confined to the replaceable realization layer — this ceiling is in `00-BOOK/`, the **frozen** corpus. |
| Also falsifies | `MCP-002`, which asserts "`ukb validate` PASS" in five places. |
| Remediation authority | `00-BOOK/**` is frozen read-only under **DP-03** and is protected area **X-1**. **This finding cannot be remediated by this or any ordinary programme.** It requires a `CEP-009` amendment route. |

### RG-10 — **ISO-4217 currency shape hard-coded in realized code** · HIGH · NEW (post-dates the ACFV baseline)

| Field | Determination |
|---|---|
| Location | `platform/commercial_intelligence/contracts.py:53` — `_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")`, enforced fail-closed at `:165`; `:154` documents *"an ISO-4217-shaped currency and integer minor units"*; `:157` names *"cents, pence"* |
| Assumption encoded | Earth · ISO-4217 · three-letter codes · decimal minor units |
| Direct contradiction | `engine/kernel/compliance.py` `UNKNOWN_CATEGORIES` proves admissibility of `("ValueExchangeSystem", "Entropy-Credit", {"unit": "reversible-negentropy"})`. **A negentropy credit cannot be expressed as `^[A-Z]{3}$`.** The meta-kernel's own certified proof is violated one layer up. |
| Why unregistered | The whole `platform/commercial_intelligence/` package (21 modules, commit `898ef8d`) post-dates ACFV's `527485a` baseline. ACFV never saw it. `RG-05` (no commercial capability) was partly remediated *while introducing an uncertified finite assumption*. |
| Mitigating | Currency is otherwise correctly parametric (`investment.py:66` `currency: str`; one currency per price book; no `"USD"` literal outside tests) |
| Remediation surface | `platform/**` is EC-2 **FROZEN** — protected area **X-8**. Cannot be mutated additively. |

### IG-06 — **Hard-coded natural language and locale in the Context substrate** · MEDIUM · NEW

`engine/context/catalog.py:182` `"language": "en"` · `:192` `"locale": "engineering culture of the UCOS programme"`.

The *dimensions* are correctly open — `engine/context/ontology.py:224,230` declare `language` and `locale` as free-form string dimensions, and `CXL-02` requires future types be admitted as data. Only the **seeded catalog entry** is fixed. Low severity in isolation, but it is a hard-coded Earth-language default inside the very substrate the mandate designates as the replacement for hard-coded assumptions.

### IG-07 — **Gregorian / UTC / POSIX temporal frame in the determinism layer** · LOW · NEW

`engine/determinism/hermetic.py:66` `SOURCE_DATE_EPOCH = 0` (1970-01-01, Gregorian) · `:70` `NORMALIZED_LOCALE = "C"` · `:71` `NORMALIZED_TIMEZONE = "UTC"`, injected as `LC_ALL`/`LANG`/`LC_CTYPE`/`TZ`.

Defensible as build hermeticity rather than a domain model. Recorded because it is a hard-coded calendar/timezone/locale frame and **no certification axis names it** — DOC axis 12 addresses coordinate dimensionality only.

### IG-08 — **Kubernetes hard-coded as the deployment substrate inside `engine/`** · MEDIUM · NEW

`engine/runtime/deploy.py` emits Kubernetes ConfigMap/Deployment/Service manifests with literal `app.kubernetes.io/*` label keys (`:228–230`), typed fields `kubernetes` (`:56`) and `kubernetes_rollback` (`:89`), and generator `_kubernetes_manifests` (`:250`).

`engine/provider/compliance.py` lists `"kubernetes"` in `PROHIBITED_VENDOR_TOKENS` — but that denylist is scoped to `engine/provider/`, so it cannot see this file. ACFV S-1's "zero vendor product names across the audited code trees" did not cover it. This is a concrete orchestrator binding in the **certified** `engine/` tree (protected area **X-8**).

### IG-01 (ACFV, **re-verified still present**) — closed taxonomic enums

`engine/registry/universal/identity.py:42` `class RegistryKind(str, Enum)` with a fixed member set (`NAMESPACE, CAPABILITY, DOCUMENT, ENGINE, COMPONENT, API, SERVICE, APPLICATION, INFRASTRUCTURE, DEPENDENCY, EVIDENCE, …`). Adding a registry kind requires a source edit and redeploy — not a governed registry write.

This contradicts `02-ARCHITECTURAL-STABILITY-CERTIFICATION`'s "Registration → no redesign" claim and the corpus's own `LAW USIS-04` (*"no enumerated lists in engines"*). ACFV counted 182 `Enum` classes, ~89 taxonomic.

### GG-05 (ACFV, **re-verified still true**) — the closure gate is excluded from CI

`grep -rln closure verify.sh .github/workflows/` matches only `uccep-gate.yml`, `research-publication-gate.yml`, `rfp-gate.yml` — **none is a closure gate**. `make closure-phase3-gate` exits **1** (`REPOSITORY NOT-CLOSED`, `planned=0/0`), which is operator action **OA-5** / finding `UCCEP-F-001` (the phase-3 verdict is a constant, not a measurement).

---

## §3 — CORRECTION TO PRIOR ART: ACFV `RG-01`/`RG-02` do not reproduce here

ACFV recorded that the `CLOSED | 0 gaps` banner is an artifact of `CLOSURE_SKIP_CORPUS=1` (set by `.kiro/hooks/uakos-closure-002.json`), masking 91 `conversation_only` concepts, and that the honest run yields `NOT-CLOSED | 525 concepts | 91 gaps`.

**Re-verified at `df763bf`: that state does not reproduce in this working copy.** Running the engine **with and without** the flag produces byte-identical output — `CLOSED | concepts=440 | gaps=0`, all seven invariants zero. The reason: `closure_engine.py:34` defines `CORPUS = REPO.parent / "UCOS"`, and the guard at `:120` is `if CORPUS.is_dir() and os.environ.get("CLOSURE_SKIP_CORPUS") != "1"`. **`../UCOS` does not exist here**, so the corpus branch is skipped regardless of the flag.

This is a **correction in fact but not in substance**, and arguably a worse finding: the closure determination is **environment-dependent**. The same commit yields `CLOSED | 440 | 0` or `NOT-CLOSED | 525 | 91` depending on whether an untracked sibling directory happens to be present. Compounded by ACFV `RG-03` — `closure.json` is gitignored (`.gitignore:53`), so the determination is per-clone runtime state, never Repository Truth.

**Recorded as a refinement of ACFV `RG-02`, not a new finding.** No claim of remediation is made.

---

## §4 — WHAT PHASE 1 ACTUALLY DETERMINES

1. **Expressive completeness is not in doubt.** ACFV ran eleven hostile reduction attempts against the architecture; all succeeded. *"Architectural redesign required: NONE."* The architecture can represent everything the mandate demands.
2. **The certifications that assert absence of hard-coding are weaker than they read.** Two of the three rest on keyword scans and a self-declared assumption; the third is executed but scoped to one directory.
3. **Six of the twenty forbidden assumptions were never tested by any axis** — operating system, ERP, CRM, commerce, healthcare, existence.
4. **Seven live hard-codings exist**, five of them newly recorded here, and **six of the seven sit in zones this or any ordinary programme may not touch** (`00-BOOK/` X-1; `engine/`+`platform/` X-8).
5. **The gate that would have caught the largest one is not wired in.** A 539-problem, exit-1 validation failure is invisible to `verify.sh` and to all 12 CI workflows, while `MCP-002` asserts it passes.

**The mandate's "zero hard coding" requirement is therefore NOT currently satisfied, and cannot be satisfied by additive work alone.** Four of the seven findings are in frozen or certified zones requiring a `CEP-009` amendment route.

---

*END — `CAEM-001` OUTPUT 03 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*

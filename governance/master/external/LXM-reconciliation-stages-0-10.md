# LUXORA Ω∞ — Stage 0–10 requirement reconciliation (read-only analysis)

Prepared by amazon-44 (read-only), 2026-10-30. No source, repository or workspace was modified.

## Sources

| ID | Source | Path | Bytes | Logical lines | SHA-256 |
|---|---|---|---|---|---|
| SRC-0002 | 636-line execution prompt (original) | `~/Downloads/Pasted text(20261030-050311).txt` | 34,673 | 636 | `0cc5363179627ba96444d2ab41a08c8f107e18343a395060afe7e3d970097dd0` |
| SRC-0003 | Combined single-file edition | `~/Downloads/LUXORA-Complete-Master-Execution-Prompt.md` | 78,296 | 1,276 | `581d1f255f069cf92302563a16a142f5f3e21bfcf434a21607c608ce56ad7e4b` |
| SRC-0001 | Owner mandate = Appendix A of SRC-0003 | SRC-0003 lines 374–1276 | — | — | — |

Line references: **S** = SRC-0002 line; **L** = SRC-0003 procedure line (1–366); **A** = SRC-0003 Appendix A line (374–1276).

## Classification key

| Code | Meaning |
|---|---|
| **FP** | Fully preserved: the combined procedure keeps the operational detail (possibly reworded or relocated to another stage) |
| **MO** | Mandate-only: the procedure drops the detail, but Appendix A states the same operational detail |
| **PP** | Partially preserved: some detail survives; the rest is in neither the procedure nor Appendix A |
| **OM** | Omitted: the operational instruction is in neither the procedure nor Appendix A (a related objective may exist) |
| **ST** | Strengthened: the procedure is stricter or more detailed than the source |
| **CF** | Conflicting, or now superseded by later fact |

Proposed IDs are *proposed only* (format from the consolidation prompt §8.2) and have not been allocated anywhere.

The matching was hand-verified against the full text. A token-overlap script was used only to find candidate lines.

---

## Header and execution directive (S1–S39)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000001 | 4–7, 9–10 | Owner, repository, integration branch, register, explicit release authorization, initial NO-GO | 5–9 | 376–382 | Yes | FP |
| LXM-REQ-000002 | 8 | **Primary execution environment: the existing approved integration workspace *outside iCloud*** | 35, 261 (path only) | 601 (path only) | The path survives; the explicit "outside iCloud" constraint does not | **PP** |
| LXM-REQ-000003 | 16–18 | Implement the complete scope of the attached master mandate | 13 | — | Yes (now "Appendix A") | FP |
| LXM-REQ-000004 | 20 | An execution mandate, not a proposal, architecture document, gap report alone or list of future recommendations | 13 | 392 | Yes | FP |
| LXM-REQ-000005 | 22 | Inspect, preserve, reconcile, implement, run checks, update records, continue without routine interruptions | 13 | 390, 396 | Yes | FP |
| LXM-REQ-000006 | 24 | Expected result: working, tested, traceable platform; capabilities and blockers honestly represented | 365, 22 | 406 | Yes | FP |
| LXM-REQ-000007 | 28 | Rule 1: execute sequentially in the same authorized owner session | 17, 357 | — | Yes | FP |
| LXM-REQ-000008 | 29 | Rule 2: don't ask the owner to confirm routine technical choices, file edits, test commands, ordinary fixes or progress between stages | 18, 361 | — | The general rule survives; the examples were dropped | FP |
| LXM-REQ-000009 | 30 | Rule 3: don't stop after the gap analysis, architecture plan, documentation **or one successful test suite** | 79, 359 | — | Inventory and plan survive; the "one successful test suite" case doesn't (it's restated in SRC-0004 §4) | PP |
| LXM-REQ-000010 | 31 | Rule 4: don't wait for an external dependency before independent work | 18, 20 | — | Yes | FP |
| LXM-REQ-000011 | 32 | Rule 5: a blocked item gets a documented blocker, preparatory work, a disabled operation, and work continues | 20, 363 | 921 | Yes | FP |
| LXM-REQ-000012 | 33 | Rule 6: a durable checkpoint after every material stage; resumable after a tool, session, process **or CI job** terminates | 21 | — | Yes ("CI job" not named) | FP |
| LXM-REQ-000013 | 34 | Rule 7: don't claim completion when a required check **was not executed or failed** | 184, 251 (relocated) | 406 | Yes (Stages 12 and 14) | FP |
| LXM-REQ-000014 | 35 | Rule 8: no competing sessions, no second writable checkout, **no concurrent edits** | 17, 287 | — | Yes | FP |
| LXM-REQ-000015 | 36 | Rule 9: **no repetitive progress messages**; one consolidated report at the end | 314 (the report only) | — | The final report survives; the ban on progress messages doesn't | **OM** |
| LXM-REQ-000016 | 37 | Rule 10: **ask the owner only** when progress needs a consequential business decision, a secret or credential, external authorization or an owner-reserved decision | 20, 363 (record and continue) | 1082 (decision packet) | The procedure never says when asking is allowed; only how to record a blocker | **OM** |
| LXM-REQ-000017 | 39 | "Without interruption" ≠ inventing financial decisions, exposing credentials, destructive actions or deploying | 19, 23, 37, 119 | 404–408 | Yes (spread across the text) | FP |

## Stage 0 (S43–S82)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000018 | 45 | Establish the real state before any change | 27 | 580 | Yes | FP |
| LXM-REQ-000019 | 49 | Absolute working directory | 29 (`pwd -P`) | 582 | Yes, more precise | ST |
| LXM-REQ-000020 | 50–51 | Branch, exact HEAD, remote URL, remote branch head | 29 | 583 | Yes | FP |
| LXM-REQ-000021 | 52 | Staged and unstaged changes | 30 (separately, plus `git diff --check`, `--stat`, changed paths) | 583 | Yes, more detailed | ST |
| LXM-REQ-000022 | 53 | Untracked files **and existing preservation artifacts** (inspect) | 30 (untracked); 37 (preserve) | — | Preservation artifacts are preserved but not *inspected* in Stage 0 (Stage 15 inventories them) | PP |
| LXM-REQ-000023 | 54 | Active Git, test, build and background processes | 31 | — | Yes | FP |
| LXM-REQ-000024 | 55 | **Open pull requests** and current CI runs | 32 (PR #6 only) | 584 | Narrowed to PR #6; the appendix covers the "integration PR" | PP |
| LXM-REQ-000025 | 56 | Canonical `PRODUCTION_READINESS.md` | 33 | 585 | Yes | FP |
| LXM-REQ-000026 | 57 | Decision records, generated context artifacts, **feature registries, test procedures** | 33 (context, generated) | 586, 587, 592, 594 | Decision records and registries/tests are in the appendix §3 only | MO |
| LXM-REQ-000027 | 61–63, 66 | Historical: PR #6 draft; head `ed634ad…`; CI `40922556022`; reverify | 35 | 611 | Yes, but **stale**: superseded by `39ed4d6` / run `40990327443` | FP + CF(stale) |
| LXM-REQ-000028 | 64 | Historical: owner session `amazon-62` | 3 | — | Yes (header) | FP |
| LXM-REQ-000029 | 68 | Re-resolution: 35 development dependencies, **ten version changes**, **jsdom/dom-selector 9→10**; don't infer committed or pushed from another session's report | 57 | 597 | The 35 entries and "don't rely on a report" survive; "ten version changes / 9→10" were dropped. **Commit `39ed4d6` records an integrity-only re-resolution with 0 version changes**, superseding that historical fact | PP + **CF(superseded)** |
| LXM-REQ-000030 | 72 | No `reset --hard`, `clean`, force-push, unapproved rewrite, destructive cleanup | 37 | 619–628 | Yes (the appendix is more detailed) | FP |
| LXM-REQ-000031 | 73 | Never overwrite or discard unrelated or uncommitted work | 37 | 617, 627–628 | Yes | FP |
| LXM-REQ-000032 | 74 | Never delete an original or preservation workspace | 37, 277 | 407, 626 | Yes | FP |
| LXM-REQ-000033 | 75 | Never **modify** a production DB or protected data during testing | 23 ("mutate production data"), 37, 131 | 632, 638 | Yes | FP |
| LXM-REQ-000034 | 76 | No hand-editing of generated files | 37 | 636 | Yes | FP |
| LXM-REQ-000035 | 77 | Never commit secrets, credentials, **keyrings**, private environment artifacts | 119, 234 | 566, 923 | Yes (keyrings fall under "secrets") | FP |
| LXM-REQ-000036 | 78 | Never merge PR #6 or deploy without authorization | 23, 243 | 638 | Yes | FP |
| LXM-REQ-000037 | 80 | Unsafe or differing state: preserve, reconcile without destroying | 39 (plus don't silently switch branches or overwrite another session's work) | 613 | Yes, more detailed | ST |
| LXM-REQ-000038 | 82 | Record the verified initial state **in the canonical release record or a governed checkpoint** | 27 ("inspect and record") | 1070 ("report the baseline") | Recording survives; the **destination** (canonical record or checkpoint) doesn't | PP |
| LXM-REQ-000039 | — | *Added:* don't remove `.git/index.lock` until no Git process owns it and its cause is understood | 37 | 630 | New relative to SRC-0002 (taken from the appendix) | ST |
| LXM-REQ-000040 | — | *Added:* expected workspace path recorded as a historical fact | 35 | 601 | New relative to SRC-0002 | ST |

## Stage 1 (S84–S127)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000041 | 86 | Finish Universal Technology Governance before widening the work | 43 | — | Yes | FP |
| LXM-REQ-000042 | 88 | Review `docs/technology.md`, declaration, snapshots, registry lifecycle, adapters, scanner, lock, inventory, tests | 43 (+ CLI, workflow, Dockerfile, manifest) | — | Yes, wider scope | ST |
| LXM-REQ-000043 | 92–98, 100, 102–103 | Open categories; source and protocol registration; safe discovery with provenance and bounded retrieval; separated lifecycle phases; kernel lifecycle reuse; deterministic locks; pinned artifacts; CI/runtime/dependency/container consistency; exceptions and rollback; tests for unknown categories | 47–53 | — | Yes | FP |
| LXM-REQ-000044 | 99 | Detection of undeclared technology assumptions **and unjustified hardcoding** | 52 (assumptions only) | 704–729 (business-policy audit) | Hardcoding detection moved to the Stage 4 business-policy audit; it's no longer a technology-governance check | PP |
| LXM-REQ-000045 | 101 | **Independently approved**, auditable production-affecting changes | 50 ("distinct-person approval **where required**") | — | The qualifier "where required" weakens an unconditional requirement | **PP (weakened)** |
| LXM-REQ-000046 | 107 | Complete the authorized re-resolution if not already done | 57 | — | Yes. Now historical: completed in `39ed4d6` | FP |
| LXM-REQ-000047 | 109 | Lockfile resolved/integrity metadata correct; constraints respected; reproducible install; production dependencies and `package.json` unchanged | 57 (+ checked against registry data, exact lockfile diff; changes only through a documented scope decision) | — | Yes, more detailed | ST |
| LXM-REQ-000048 | 111 | Verify jsdom/dom-selector against constraints; **don't force incompatible versions**; don't suppress integrity findings | 57 ("don't suppress findings"; "no broad uncontrolled upgrades") | — | "Don't force incompatible versions" isn't stated | PP |
| LXM-REQ-000049 | 113 | Clean `npm ci`, affected tests, full suite, lock/inventory generation, governance gate, browser, PostgreSQL, Docker | 59 (+ freshness, Docker smoke) | — | Yes | ST |
| LXM-REQ-000050 | 115 | **Review each remaining technology-assumption finding individually and classify it: fixed / verified constraint / approved exception / unresolved gap** | 59 ("reconcile all findings") | 717–725 (a different 7-way taxonomy, business policy only) | The per-finding four-way classification is lost | **OM** |
| LXM-REQ-000051 | 119 | Update register and technology documentation with evidence | 61 | — | Yes | FP |
| LXM-REQ-000052 | 121 | Commit and push **only after required local checks pass** and the diff is inspected; two independent green CI runs on the exact post-change SHA; examine required jobs | 61 (diff inspection, two runs, required jobs); 239 (Stage 14 gates) | 1128 | The gate "commit only after local checks pass" isn't explicit in Stage 1; Stage 14 restores it for the final commit | PP |
| LXM-REQ-000053 | 123 | Don't count CI from an earlier commit | 59, 249 | 1226 | Yes | FP |
| LXM-REQ-000054 | 125 | **Don't begin unrelated concurrent work to accelerate the run**; keep the exclusive-session rule | 17 (session rule only) | — | The ban on concurrent work while CI runs is lost; it sits in tension with rule 4 / L18 (see conflict K4) | **OM** |
| LXM-REQ-000055 | 127 | Continue to Stage 2 after PR-053; a green gate ≠ mandate compliance | 63 | — | Yes | FP |

## Stage 2 (S129–S154)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000056 | 131, 135 | The mandate is the parent acceptance contract; if no canonical copy exists, record that and use the supplied one | 65–67 | 370 | Yes | FP |
| LXM-REQ-000057 | 133 | Locate the canonical copy; verify identity, version, **status and governance relationships**; don't weaken it | 67 ("identity, version and authority") | — | Status and governance relationships were dropped | PP |
| LXM-REQ-000058 | 137 | Inspect implementation, configuration, schemas, migrations, registries, UI, adapters, tests, CI, ops documentation, readiness records | 75 (relocated to Stage 3), 33 | 580–595 | Yes | FP |
| LXM-REQ-000059 | 139, 143–145, 147–149 | Conformance matrix, one entry per requirement: mandate reference, implementation, runtime/lifecycle enforcement, test, evidence and commit, five-value status | 71 | 941–962 (feature matrix) | Yes | FP |
| LXM-REQ-000060 | 146 | **Matrix field: configuration, schema and data dependencies** | — | 955 (*feature* matrix only) | Missing from the conformance matrix | **OM** |
| LXM-REQ-000061 | 150 | **Matrix field: remaining work, consequence** and closure condition | 71 (closure condition) | 962 (feature matrix: "remaining gaps") | "Remaining work" and "consequence" were dropped | PP |
| LXM-REQ-000062 | 152 | Reuse canonical records; no register competing with `PRODUCTION_READINESS.md` | 71 | 642–648 | Yes | FP |
| LXM-REQ-000063 | 154 | Architecture descriptions, seed placeholders, registry records and unrelated tests aren't proof | 22 (rule 6) | 406, 444 | Yes (relocated) | FP |
| LXM-REQ-000064 | — | *Added:* reconcile the five decisions; preserve IDs and history; verify meanings; an illustrative list isn't a closed taxonomy | 69 | 646, 1076–1080 | New relative to SRC-0002 | ST |

## Stage 3 (S156–S182)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000065 | 160–162, 164–169, 171 (migration) | Inventory scope: monetary policy, multi-business, business rules and configuration, payments, configuration registry and seeds, composition, arithmetic and persistence, feature-to-test, journeys/permissions/UI, DB migration | 75, 93 | 1088 | Yes | FP |
| LXM-REQ-000066 | 163 | Inventory scope: **financial exceptions and legacy data resolution** | — (Stage 5 L95 implements; it isn't inventoried) | 523–535, 1088 | Inventory scope: appendix only | MO |
| LXM-REQ-000067 | 170, 171 (recovery), 172–174 | Inventory scope: **security, tenancy, auditability; recovery; deployment infrastructure; monitoring, backups, disaster recovery, capacity; privacy, compliance, release authorization** | 75 ("production prerequisites", ops documentation) | 1088 (no security, operations or compliance inventory) | Only "production prerequisites" survives as a vague catch-all; Stages 10, 11 and 16 *verify* these but nothing *inventories* them as gaps | PP |
| LXM-REQ-000068 | 176 | Inventory from source; don't manufacture items or totals | 75 | 683 | Yes | FP |
| LXM-REQ-000069 | 178 | Identify duplicated policies, hidden rules, configuration gaps, missing seed options, stale artifacts, **conflicting authorities**, unimplemented capabilities, **tests that don't cover claimed behavior**, stale evidence | 77 (no "conflicting authorities" and no "tests not covering claimed behavior") | 1092 ("conflicting sources of truth", "insufficient tests") | Both missing items are in the appendix's Stage C | MO |
| LXM-REQ-000070 | 180 | **Classify each finding by impact, dependencies, priority and the work required to close it** | — | 838 (monetary only), 1013 (security only) | No general classification | **OM** |
| LXM-REQ-000071 | 182 | Don't stop after the inventory; a blocked item doesn't block unrelated work | 79 | 1084 | Yes | FP |
| LXM-REQ-000072 | — | *Added:* 8-way status (working / implemented not configured / configured not applied / missing / partial / untested / externally blocked / awaiting owner) | 77 | 1090 (5-way) | New relative to SRC-0002 | ST |

## Stage 4 (S184–S211)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000073 | 186 | Reuse the kernel, registry and configuration; extend if incomplete; no parallel engines **without justification** | 83 ("implement only missing mechanisms; avoid parallel engines, registries and schema sources") | 403, 658 | Stricter: the justification escape is removed | ST |
| LXM-REQ-000074 | 190–194, 196–200 | Identity, schema, ownership; typed options and validation; explicit defaults distinct from definitions; scope and inheritance; precedence and conflict detection; lifecycle, dates, versions; approval and activation; simulation and impact; audit and rollback; authorization and tenancy | 85, 87 | 660–679 | Yes (+ least privilege, secret protection) | FP/ST |
| LXM-REQ-000075 | 195 | Dependencies **and compatibility** | 85 (dependencies only) | 667 | Compatibility is in the appendix only | MO |
| LXM-REQ-000076 | 201 | **Links to implementations, consuming features and tests** | — | 671, 685–694 | Appendix only | MO |
| LXM-REQ-000077 | 203 | Authorized APIs and admin interfaces: discover, inspect, configure, validate, preview, simulate, approve, activate, compare, roll back | 85 | 677 | Yes | FP |
| LXM-REQ-000078 | 205 | **"A registry is not enough if authorized administrators can't use the functionality in the running platform"** | — | 422 (monetary rules only), 476 | Stated in general only for monetary rules (A422) and profiles (A476) | MO (scope narrower) |
| LXM-REQ-000079 | 207 | Seed from the implementation; preserve live configuration on re-apply; idempotent, deterministic, version-aware, **auditable** | 87 | 446, 698 | Yes ("auditable" is in A446) | FP |
| LXM-REQ-000080 | 209 | **Invalid configuration can't bypass monetary, security, authorization, ledger, payment, tenant or data-integrity invariants** | — | 405, 535, 1110, 1148, 1188 | Appendix only | MO |
| LXM-REQ-000081 | 211 | Test runtime behavior, not the existence of seed records | 87 | 444 | Yes | FP |
| LXM-REQ-000082 | — | *Added:* definition / template / approved / activated / historical distinction; 7-way hardcoding classification; don't turn every literal into configuration | 87, 89 | 673, 717–729 | New relative to SRC-0002 (taken from the appendix) | ST |

## Stage 5 (S213–S252)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000083 | 215 | Inspect the money model, **monetary migration history, canonical money inventory, policy records** and decisions | 93 (money model), 99 (decisions) | 588, 836 | The migration history and the money inventory are in the appendix only | MO |
| LXM-REQ-000084 | 217 | No second money library or competing monetary source of truth | 93 | 792 | Yes | FP |
| LXM-REQ-000085 | 221–223, 225–228, 232 | Exact representation; currency identity and currency-specific precision; rounding modes and boundaries; exact calculation and validation; versioned policy and traceability; legacy migration; quarantine; source-evidence preservation | 95, 97 | 794–811 | Yes (+ overflow; no binary floating point as the authority) | FP/ST |
| LXM-REQ-000086 | 224 | Conversion with **rate source, timestamps and fees** | 95 ("deterministic conversion and rates") | 435 | Rate source, timestamps and fees are in the appendix only | MO |
| LXM-REQ-000087 | 229 | Authorized exception resolution **with rationale** and audit history | 95 (no rationale) | 533 | Appendix only | MO |
| LXM-REQ-000088 | 230 | **Refund, tax, fee, discount and settlement allocation** | 93 (as paths to inventory, not as allocation) | 429–432, 847–848 | Appendix only | MO |
| LXM-REQ-000089 | 231 | **Reconciliation and discrepancy workflows** | 93 (as a path) | 436, 527, 533, 858 | Appendix only | MO |
| LXM-REQ-000090 | 234 | Audit every monetary read/write path and field; a fixed payment spine isn't proof | 93, 97 | 834 | Yes | FP |
| LXM-REQ-000091 | 236 | Inventory and seed every monetary rule; **configurable only when the running platform loads, validates and applies it** | 75, 87 (general) | 420, 442, 444 | The precise acceptance definition is in A444 only | MO |
| LXM-REQ-000092 | 238 | Preserve historical configuration; new transactions record the policy version | 97 | 446, 804 | Yes | FP |
| LXM-REQ-000093 | 242, 246–248, 250, 252 | MD-1…5: establish meanings and statuses; implement the mechanism and options; safe tests; keep activation blocked; continue; don't wait | 99 | 586, 866 | Yes | FP |
| LXM-REQ-000094 | 249 | Decision packet **with options, consequences and a recommendation** | 99 ("the exact decision packet") | 1082 (stronger: recommendation ≠ approval) | Appendix only | MO |

## Stage 6 (S254–S277)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000095 | 258–266 | Rule domains: catalog, pricing, offers, eligibility, promotions, orders, fulfilment, inventory, payments, refunds, disputes, approvals, access, notifications, workflows, risk | 103 | 499 | Yes | FP |
| LXM-REQ-000096 | 260 | Promotion **stacking** | 103 ("promotions") | 430 (coupon stacking, monetary) | Appendix only | MO |
| LXM-REQ-000097 | 266 | Risk controls **and exception handling** (as a business-rule domain) | 103 (risk only) | 436 (financial exceptions only) | Non-financial exception-handling rules are lost | PP |
| LXM-REQ-000098 | 267 | Business-specific **and future** domain behavior | 103 ("other supported domains") | 438, 515 | "Future" is in the appendix only | MO |
| LXM-REQ-000099 | 269, 273, 275, 277 | Canonical engine per function; new rules addable without source edits; new executable behavior through a reviewed, registered extension; no arbitrary code execution | 103, 105 | 450, 519, 521 | Yes | FP |
| LXM-REQ-000100 | 271 | Discoverable, configurable, testable; **composition**, precedence, scope, dependency validation, versioning, simulation, approval, activation, rollback, audit | 105 (no composition) | 508 | Composition is in the appendix only | MO |

## Stage 7 (S279–S315)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000101 | 281 | Reusable mechanism to define, discover, compose, validate, configure and test profiles | 109, 113 | 474 | Yes | FP |
| LXM-REQ-000102 | 283 | Reuse capability, domain, composition, **navigation, identity, authorization** and registry foundations | 109 ("reuse canonical capabilities") | 741, 749, 751, 757 | Appendix only | MO |
| LXM-REQ-000103 | 287–289, 291 (inheritance), 292–295 | Business-model definitions; shared primitives; dependencies and compatibility; configuration inheritance; workflow and rule selection; permissions, APIs, events, UI; schemas and migrations; connectors | 109 | 742–753 | Yes | FP |
| LXM-REQ-000104 | 287, 290, 291, 294, 296 | **Industry** definitions; profile **lifecycle**; **scope resolution**; **data ownership**; **observability** and **deployment profiles** | 109 (certification only) | 742, 745, 746, 752, 754–755 | Appendix only | MO |
| LXM-REQ-000105 | 298 | **Don't hardcode a closed list of business models**; no marketplace assumptions in shared primitives | 109 (marketplace half); 69 (general "not a closed taxonomy") | **472** ("must not become a hardcoded maximum enumeration"), 493, 759 | Explicit in A472. *This corrects my previous report, which said the prohibition was "only implicit".* | MO |
| LXM-REQ-000106 | 302–309, 311 | Six representative profiles through real mechanisms; build missing composition; per-profile maturity states | 111, 113 | 765–778 | Yes | FP |
| LXM-REQ-000107 | 313 | A template isn't proof; report missing implementations **and dependencies**; don't advertise | 113 | 478, 780 | Yes ("dependencies" in A780) | FP |
| LXM-REQ-000108 | 315 | Prioritize the first marketplace release; keep the foundation reusable | 113 (+ "without architecturally constraining later models") | 493, 784 | Yes | ST |

## Stage 8 (S317–S344)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000109 | 319 | **Preserve sound provider implementations; remove provider-specific coupling from common orchestration** | — | 874, 572 | Appendix only (almost word for word) | MO |
| LXM-REQ-000110 | 321, 325, 327–335, 337, 340, 342, 344 | Provider-neutral mechanism plus actual adapters; initiation, authorization, capture; credential references; currency and operation constraints; idempotency; signed webhooks; duplicate and out-of-order events; retries, timeouts, unknown outcomes; refunds; disputes; settlement and reconciliation; ledger and wallet integrity; a connector ≠ functional; external blockers; no secrets; mocks ≠ verification | 117, 119 | 539–572, 878–923 | Yes | FP |
| LXM-REQ-000111 | 326 | **Payment-method capability discovery** | 117 ("supported methods") | 549, 559 | Appendix only | MO |
| LXM-REQ-000112 | 336 | Provider **routing** and **operational controls** (health survives) | 117 (health/monitoring) | 561, 562 | Appendix only | MO |
| LXM-REQ-000113 | 338 | **Audit history** and conformance tests | 117 (conformance only) | 562, 933 | Appendix only | MO |

## Stage 9 (S346–S372)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000114 | 348 | Map features to acceptance criteria, APIs, data, screens, roles, permissions, configuration, integrations, tests | 123 (+ data/migrations, failure paths, SHA, evidence location) | 947–962 | Yes, more detailed | ST |
| LXM-REQ-000115 | 350, 355–363 | Journeys for buyers, sellers, admins, operators and other roles: tenancy and permissions, catalog, pricing, offers, checkout, payment recovery, orders, returns, refunds, wallet, configuration, approval and rollback, financial exceptions | 125 | 970–984 | Yes | FP |
| LXM-REQ-000116 | 354 | **Registration and session lifecycle** (authentication survives) | 125 (authentication only) | 974 | Appendix only | MO |
| LXM-REQ-000117 | 364 | **Notifications** journeys and operational failure paths | 125 (failure paths only) | — | The notification journey is lost (A499 lists notifications as a *rule* domain only) | PP |
| LXM-REQ-000118 | 366 | Test states, including **truthful user-facing status** | 125 | 988 ("absence of misleading success states") | Appendix only | MO |
| LXM-REQ-000119 | 368 | Responsive, accessible, **supported-browser operation** | 125 (responsive and accessibility) | 988, 990 | Appendix only | MO |
| LXM-REQ-000120 | 370, 372 | Page-load counts aren't proof; record SHA and result per test; untested journeys visible | 123, 125 | 966, 990 | Yes | FP |

## Stage 10 (S374–S398)

| Proposed ID | S | Source requirement | L | A | Detail survives? | Class |
|---|---|---|---|---|---|---|
| LXM-REQ-000121 | 376, 380–382, 388, 390–392 | Security, persistence, migrations, integrity and recovery per deployment profile: authentication and authorization; tenancy and least privilege; API validation and abuse; dependency and container checks; monetary source preservation; backup encryption and secret exclusion; restore | 127, 129 | 996–1011 | Yes | FP |
| LXM-REQ-000122 | 383 | Secret handling **and rotation procedures** | 129 (handling only) | 1001 | Appendix only | MO |
| LXM-REQ-000123 | 384 | Webhook verification, replay protection **and idempotency** | 129 | 1002–1003 | Appendix only | MO |
| LXM-REQ-000124 | 385 | Audit integrity **and configuration authorization** | 129 | 1007 | Appendix only | MO |
| LXM-REQ-000125 | 386 | **Sensitive-data protection** and safe logging | 129 (safe logs) | 1006, 1008 | Appendix only | MO |
| LXM-REQ-000126 | 387 | Rate limits **and resource exhaustion** | 129 | 1005 | Appendix only | MO |
| LXM-REQ-000127 | 389 | Migration, failed-migration safety **and upgrade compatibility** | 129 | 1027 | Appendix only | MO |
| LXM-REQ-000128 | 394, 396, 398 | Isolated databases for destructive tests; each DB profile tested independently; standard suites; findings recorded | 131 (+ preservation copies) | 1025, 1031, 1013 | Yes | ST |

## Stages 11–16 and the final report

| Section | Method | Result |
|---|---|---|
| Stages 11–15 (S400–555 vs L133–288) | `diff` of the raw lines | **Byte-identical** |
| Stage 16 + final report (S556–625 vs L289–354) | `diff` of the raw lines | Only differences: two `---` separator lines plus the blank line after each |
| Same | Normalized (drop `---`, collapse whitespace), SHA-256 | **Identical**: `92847556683c88f1…` both |
| Final execution rule (S626–636 vs L355–365) | Word diff | "Begin now by establishing … and confirming exclusive ownership. Then" → "Continue in the existing exclusive owner session. Establish … ownership, then". No change in meaning |

## Totals (Stages 0–10 plus header and directive, 128 proposed requirement rows)

| Class | Rows |
|---|---|
| FP (fully preserved), including 1 FP + CF(stale) | 57 |
| FP/ST | 2 |
| ST (strengthened or added in the combined procedure) | 15 |
| MO (mandate-only) | 33 |
| PP (partially preserved), including 1 PP + CF(superseded) | 15 |
| OM (omitted) | 6 |
| **Total** | **128** |

Counts were computed from the Class column. The classifications themselves are hand judgments.

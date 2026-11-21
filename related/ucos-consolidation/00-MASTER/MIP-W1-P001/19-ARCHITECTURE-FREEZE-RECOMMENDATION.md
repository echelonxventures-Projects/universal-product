# 19 — Architecture Freeze Recommendation

**Anchor** `c6c20fb` · **Freeze authority** `00-CEP/CEP-007` (Constitutional Freeze Constitution) —
this output **recommends**, it does not freeze.

---

## Recommendation

> ## FREEZE THE ARCHITECTURE · DO NOT FREEZE THE BASELINE
>
> **Freeze now:** the layered architecture, the capability disposition set, the constitutional
> function decomposition, and the derived-truth programme contract. These are stable, gate-verified,
> and safe to build on.
>
> **Do not freeze:** the repository baseline itself, until blocker **B-1** is cleared. The registry
> that would carry the freeze evidence is provably stale at this anchor; freezing over it would seal
> a false assertion into a constitutional record.

---

## 1 · What is fit to freeze — and why

### 1.1 The 11-layer architecture — FREEZE

| Evidence | Measure |
|---|---|
| Layers located and ordered | 11, bottom-up, no downward dependency |
| Typed `Depends-On` acyclicity | `depends_on_acyclic: true` over 4,774 edges |
| Cross-unit architectural cycles | **0** — RIB GATE-10 PASS |
| Orphan units | **0** — RIB GATE-11 PASS |
| Dangling / malformed / unresolved edges | **0 / 0 / 0** |
| Graph validity | `is_valid: true` over 1,229 nodes · 12,851 edges |

Three architectural cycles previously existed and were eliminated at `6dae436` **as data, by homing
one contract correctly** — not worked around in code. That is the behaviour of an architecture that
can absorb correction without deformation, which is precisely the property a freeze should preserve.

### 1.2 The capability disposition set — FREEZE

| Evidence | Measure |
|---|---|
| Capabilities dispositioned | 66/66, by an **ordered total rule set of 11 rules** — computed, never asserted |
| Replacement prohibited | 45/66 (68%) |
| REPLACE / REWRITE / FORK dispositions | **0** |
| Duplicate capability / interface / runtime | **0 / 0 / 0** |
| Capability↔unit resolution | 100% both directions — RIB GATE-07 PASS |
| Evidence present | 66/66 |

### 1.3 The constitutional function decomposition — FREEZE

`CEP-000`…`CEP-010`: eleven instruments, eleven constitutional functions (engineering, governance,
execution, validation, certification, ratification, freeze, evidence, amendment, audit), **exactly
one owner each**. No function unowned; no function double-owned. `DUP-CONSTITUTION` = 0.

Amendment discipline is demonstrated rather than asserted: `CEP-002` Article 28 was added **by
amending the located governance constitution** (`CEP-002-AMD-002`), not by creating a parallel
instrument.

### 1.4 The derived-truth programme contract — FREEZE

Eight programmes instantiate one identical contract: `AUTHORITY = NONE (DERIVED TRUTH)`, deterministic
regeneration, declared forbidden-write prefixes, fail-closed `--gate`, self-checks, sealed output.

| Self-check | Result |
|---|---|
| `CK-SELF-DECLARATION` — every reference resolves, no duplicate IDs | PASS |
| `CK-SELF-NO-ENUMERATION` — zero hardcoding / data-driven proof | PASS |
| `CK-SELF-WRITE-SCOPE` — writes only own operational memory | PASS |
| `CK-SELF-DETERMINISM` — identical seal across repeated runs | PASS |
| `CK-DETERMINISM-BUILD` — double-build, fail-on-divergence | PASS |
| `CK-RIE-DETERMINISM` — deterministic regeneration | PASS |

`UCCEP` demonstrated the contract's extensibility: it bound every located gate through
`uccep-bindings.json` and required **no change to any engine**. Adding a gate is a data entry.

Three facts are declared **non-derivable** (`ND-01` benefit, `ND-02` phase, `ND-03` supersession)
rather than fabricated. This practice should be frozen as a norm.

---

## 2 · Why the baseline must NOT be frozen yet

### 2.1 The freeze evidence is stale — B-1

`CEP-007` makes a freeze record constitutional. A freeze asserts *this exact content, at this exact
anchor*. At `c6c20fb`:

| Measure | Value |
|---|---|
| Registered artifacts whose `content_hash` matches committed bytes | **1,194 of 1,204** |
| Registered artifacts bound to content that does not exist | **10** |
| Of those, correct HEAD hashes | **0 of 10** |
| `register.sh --guard` from a pristine clean tree | **REGISTRATION DRIFT DETECTED** |

The ten include `UCOS-RIE-CAPABILITY-CATALOG.json` — the canonical owner of the capability catalogue
that §1.2 recommends freezing, and which RIB, UCCEP and this programme all bind by pointer.

Freezing here would make a permanent constitutional assertion about content that is not what the
registry says it is. Every downstream certification citing the freeze would inherit the error, and
`99-FREEZE/SOURCE-HASHES.txt` — the mechanism designed to make freezes verifiable — would be
recording the wrong hashes.

### 2.2 The aggregate gate does not pass — measured

`make uccep-full` at the anchor:

```
GATE: FAIL-CLOSED — blocking constitutional checks failed: CK-REG-DRIFT
UCCEP-000000: NOT-CERTIFIED | tier=full | gates=13/14 PASS | programmes=14/16 PASS
             | blocking=CK-REG-DRIFT | seal=12a33bff8c2d1778
```

`CEP-007` freeze presupposes a certified state. The repository's own aggregate constitutional gate
returns NOT-CERTIFIED. Freezing over a fail-closed gate would invert the gate's purpose.

### 2.3 Three further conditions the freeze record would misstate

| Condition | What a freeze taken now would imply | What is true |
|---|---|---|
| **B-2** | knowledge assimilation closed | NOT-CLOSED — 91 concepts unhomed at true scope |
| **B-3** | evidence and traceability bound | 2.2% mean; 8 of 10 chain links broken; 969 evidence artefacts unbound |
| **B-4** | the frozen code is verified | 43.1% of LOC and 47.5% of tests are outside the gate |

A freeze is an assertion about **what has been verified**. Under B-4 that assertion would be true of
56.9% of the code while reading as though it covered all of it.

### 2.4 The blueprint is not anchored here

`rib.json` records `head: bde5ffa`, `tracked_files: 4894`. The anchor is `c6c20fb` with 4,895 files.
The document whose determination is *"BLUEPRINT CERTIFIED — REPOSITORY MAY PROCEED"* describes a state
two commits behind. It must be regenerated at the freeze anchor before it can support a freeze
(`G-RIB-1`).

---

## 3 · What must NOT be frozen at all yet

| Surface | Reason |
|---|---|
| **Layer 5 — CIOA / CCE** | `PLANNED`, specification-only. Freezing an unimplemented control plane forecloses the composition choices `REALIZE_BY_COMPOSITION` requires. |
| **Layers 10–11 — AEOS spine, adapters, CLI** | absent; 12 declared gaps, 4 HIGH |
| **`14-SECURITY`** | truncated at `-004`; 14 instruments and the master registry absent. Freezing an incomplete band would require a superseding amendment (`CEP-009` Art IV.3) to finish it. |
| **`15-USIS`** | 36 instruments, 21 zones, 12 registries, **no code root** — specification only |
| **Runtime / deployment / production dimensions** | 4 BLOCKED on stale connectors; nothing measured to freeze |
| **Identity strategy** | `G-ID-1` / `R-05` — sequential category cursors are not merge-safe; freezing before the decision locks in a merge hazard across 95 category sequences |

---

## 4 · Freeze preconditions (ordered)

| # | Precondition | Verification | Blocks freeze |
|---|---|---|---|
| 1 | Clear B-1 — atomic re-registration commit | `register.sh --guard` exits 0 from a clean tree; all 1,204 hashes match | **YES** |
| 2 | Regenerate `UCOS-RIB-001` at the freeze anchor | `rib.json.repository.head` == freeze commit; 12/12 gates PASS | **YES** |
| 3 | Aggregate gate passes | `make uccep-full` → `CERTIFIED-PROVISIONAL`, `blocking=none` | **YES** |
| 4 | Correct the findings register | `UCCEP-F-003` → discharged; `UCCEP-F-007` → blocking | **YES** |
| 5 | State the freeze scope explicitly | freeze notice names what is frozen (architecture, dispositions, constitutional decomposition, programme contract) and what is not (layers 5, 10, 11; `14-SECURITY`; `15-USIS`; runtime) | **YES** |
| 6 | Extend verification scope (B-4) | gate green over all 8 code roots | recommended |
| 7 | Home the 91 concepts (B-2) | corpus-inclusive closure exits 0 | recommended |
| 8 | Bind the traceability spine (B-3) | `health --strict` exits 0 | recommended |

Preconditions 1–5 are the minimum for a **defensible** architecture freeze. 6–8 are required before a
**baseline** freeze.

---

## 5 · Freeze scope statement (proposed text)

> **FROZEN at `<commit>`:**
> the 11-layer architecture and its acyclicity invariant; the 66-capability disposition set and the
> 11-rule ordered disposition algorithm; the `CEP-000`…`CEP-010` constitutional function
> decomposition; the derived-truth programme contract (AUTHORITY=NONE · deterministic regeneration ·
> declared write scope · fail-closed gate · sealed output · non-derivable declaration); the
> `UCIC-001` capability implementation contract; the band instrument pattern (`-001`…`-018`); the
> EC-3 six-aspect module pattern.
>
> **NOT FROZEN:** layer 5 (CIOA/CCE, `PLANNED`); layers 10–11 (AEOS spine, adapters, CLI, absent);
> `14-SECURITY` (`-005`…`-018` absent); `15-USIS` (no code root); the runtime/deployment/production
> dimensions (unmeasured); the identity strategy (decision pending).
>
> **CERTIFICATION CEILING:** `CERTIFIED-PROVISIONAL`. Constitutional Tier T1 is VACANT
> (`UCCEP-F-004`); no located authority is competent to ratify. This freeze is **provisional** and
> asserts no final or ratified status.

---

## 6 · Recommendation, restated

**Freeze the architecture — it has earned it.** Eleven ordered layers, zero cycles, zero orphans,
zero duplicate capabilities, zero unowned units, verified determinism, and a computed rather than
asserted disposition set. Nothing found in Wave-1 argues for redesign.

**Withhold the baseline freeze until precondition 1 is met.** B-1 is hours of work. Taking the freeze
before it would trade a few hours for a permanent false assertion in the constitutional record — the
one trade a freeze constitution exists to prevent.

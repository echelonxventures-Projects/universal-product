# PHASE0 — GOVERNANCE-INDEPENDENT DETERMINATION

| Field | Value |
|---|---|
| Phase | 0 — Governance-Independent Blocker Elimination |
| Scope | E-1, E-2, E-3, E-4A only |
| Objective | Reduce the blocker set to the irreducible governance-dependent core |
| Method | Source reading + execution against the live repository; every finding reproduced |
| Repository | working tree at `77798202`; `00-BOOK/tools/ledger_authority.py` is `AM` (never committed); `ukb.py`, `uga_engine.py`, `register.sh` carry uncommitted modifications |
| Governance content | **NONE.** No governance root was answered, assumed, redesigned or ranked. No authority, permit rule, ratification rule, domain rule, threat model or temporal legitimacy decision appears in this report or in the four subordinate reports. |
| FD-1 / FD-2 / FD-3′ / FD-4 / FD-5 | **Not answered. Not approached.** Every governance root remains UNKNOWN. |

---

## 1. Constituent reports

| Report | Work item | Verdict |
|---|---|---|
| `PHASE0-E1-ATOMICITY-REPORT.md` | Verification → Write Atomicity | 6 UNSAFE · 1 UNVERIFIABLE · 8 SAFE |
| `PHASE0-E2-CORRESPONDENCE-REPORT.md` | Writer ↔ Authorization Correspondence | 7 UNSAFE · 1 UNPROVEN · 4 SAFE |
| `PHASE0-E3-CLAIM-INTEGRITY-REPORT.md` | `UGA-INV-10` Claim Integrity | **TAUTOLOGY** |
| `PHASE0-E4A-ISSUANCE-PATH-REPORT.md` | Permit Issuance Existence Path | 1 of 5 operations IMPLEMENTED; 4 MISSING |

All four exist. Every finding in each carries file-and-line source references.

---

## 2. Findings

### 2.1 The single structural cause

Four work items were investigated independently. Three of them converge on one architectural
fact:

> **`ledger_authority.commit()` authorizes a lossy projection of a document, and then hands
> an unconstrained callable the file path.**

`ledger_authority.py:316-336` binds the permit to six fields derived, via
`_identifier_index` (`:112-119`), from **one field per ledger record**. `ledger_authority.py:583`
then calls `writer(path, ledger)` and never looks at the result as an object. Between those
two lines sit the atomicity gap (E-1) and the correspondence gap (E-2). They are two views
of the same boundary.

E-3 is independent of that boundary and is a measurement defect. E-4A is an absence.

### 2.2 E-1 — Verification → Write Atomicity

**Answer: `commit()` can observe one state, validate it, and write a different state without
detection.** Demonstrated by execution, not by argument.

| ID | Finding | Class |
|---|---|---|
| E1-F1 | TOCTOU inside `commit()`'s own window (`:567` → `:583`, spanning a `subprocess.run(timeout=15)` at `:349-368`). A concurrently-persisted permanent identifier was **destroyed** while `commit()` reported success. | UNSAFE |
| E1-F2 | No mutual exclusion of any kind — no `fcntl`, `flock`, `O_EXCL`, `os.replace` or CAS in either writer. `register.sh:187-197` holds a non-atomic advisory lock that guards only itself. | UNSAFE |
| E1-F3 | Permit replay after ledger restore. `preimage_digest` (`:338-347`) derives spent-ness from mutable state; restoring the pre-image bytes re-validated the same permit. | UNSAFE |
| E1-F4 | Record bodies of permanent identities are outside every check. `object_class` and `first_seen` were rewritten with `assert_append_only` silent, `allocating=False`, and a `NO_ALLOCATION` claim **accepted**. | UNSAFE |
| E1-F5 | `history` (1628 live entries) is in neither `IDENTITY_MAPS` (`:71-77`) nor `NON_ALLOCATION_KEYS` (`:83-85`). Consequences: a byte-identical no-op measures `allocating=True`, so `NO_ALLOCATION` is unusable on the production ledger; and total erasure of `history` is not an append-only violation. | UNSAFE |
| E1-F6 | Minting arithmetic (`uga_engine.py:271-321`) computed against a read (`:1700`) separated from verification by the whole discovery pass. Observed behaviour fails closed via the key-removal check; the counter-collision leg is untested. | UNVERIFIABLE |
| E1-F7 | `raw_before` (`:577-581`) is read and never reconciled with `before` (`:567`). The one-line comparison that would collapse the window is available and not made. | UNSAFE |

Eight properties were **proven safe**, principally: refusals precede the writer so a refused
write leaves the file byte-identical (`:567-583`); unreadable ledger and unreadable register
both fail closed (`:100-110`, `:387-399`); the permit is verified against the recomputed
manifest, never a caller-supplied description (`:571-573`); `plan()` and `commit()` share one
measurement implementation (`:402-414`); `permit` has no default (`:546`).

### 2.3 E-2 — Writer ↔ Authorization Correspondence

**Answer: the bytes authorized are not guaranteed to equal the bytes persisted. No
guarantee, partial or otherwise, exists.**

Three independent reasons: nothing is compared after the write; no digest of *bytes* exists
anywhere to compare against; and the writer is outside the boundary by explicit design
(`:560-564`).

| ID | Finding | Class |
|---|---|---|
| E2-F1 | Divergent writer. A writer persisting a different document produced **three permanent identifiers on disk that no manifest measured and no permit named**, with `authorization=PERMIT` and no error. | UNSAFE |
| E2-F2 | Silent writer. `report` claimed `ALLOCATED 1 permanent identifier(s)`; disk was unchanged. This is the mirror of the D0.1 defect the module's own header documents — the fix addressed one direction only. `ukb._dump_json:139-140` is exactly this shape. | UNSAFE |
| E2-F3 | `bytes_changed` — **recorded correctly** (`:591`), **enforced nowhere**, and **absent from `format_report`** (`:223-249`), so all four call sites compute and discard it unseen. Its only production consumer (`uga_engine.py:2004`) uses it as a cache hint. The contradiction `allocating=True ∧ bytes_changed=False` is representable and unchecked. | UNSAFE |
| E2-F4 | `NO_ALLOCATION` permits less *allocation*, not less *mutation*. `version`, `discovered_volumes` and every non-identifier record field — including the full `by_execution` lifecycle body at `ukb.py:2388-2400` — are rewritable under it. | UNSAFE |
| E2-F5 | `LEDGER-INV-01` (`uga_engine.py:1079-1120`) requires the ledger to be named on the same line as a write primitive. Tested against the live patterns, **both production writers and both call sites are unmatched**; only a naïve direct write matches. The invariant cannot constrain writer behaviour. | UNSAFE |
| E2-F6 | Three non-equivalent serializers over one document (`:303-310`, `ukb.py:135-146`, `uga_engine.py:143-160`) with no round-trip test. No divergence demonstrated. | UNPROVEN |
| E2-F7 | E2-F1…F4 are currently **latent**: no production write reaches `writer`, because of E-4A. Removing E-4A activates all four simultaneously. | UNSAFE (higher-order) |

### 2.4 E-3 — `UGA-INV-10` Claim Integrity

**Outcome: TAUTOLOGY.**

`audited` is constructed unconditionally from `ledger["by_object"]`
(`uga_engine.py:1744-1760`) — the same map whose membership the check tests. Verified by
execution: `audited == set(by_object.keys())` is `True`, 5374 ≡ 5374. The *has-an-audit-event*
leg is therefore **unfalsifiable by construction**.

The leg that does discriminate reduces to *live non-document object absent from the ledger* —
which is `UGA-INV-01` verbatim. Executed on this repository:

```
UGA-INV-01  FAIL  measured=6804  violations=27
UGA-INV-10  FAIL  measured=5207  violations=27
violation sets identical ?  True
```

Not merely equal counts — **the same set**. Corroborated by six historical records
(`IMPLEMENTATION_BASELINE_ACCEPTED.md:124-125` 25/25; `UCOS-EXECUTION-GOVERNANCE-CERTIFICATION.md:256-257`
31/31; `OMEGA-CLOSURE-REPORT.md:234-235` 24/24; and three more), and stated outright at
`adr/0017-ucl-f-006-identity-minting-authorization.md:15`.

Ten classes of real mutation pass undetected, including every write to `by_path` (1628
documents), `by_execution`, `history`, every counter advance, every content change to an
already-registered object, and — materially — **every `ledger_authority.commit()` call**:
the chokepoint emits no audit event, and `UGA-INV-10` passes regardless.

Consequence: `UGA-INV-10` reaching PASS establishes only that discovered objects have ledger
entries. It establishes nothing about audit coverage. Every determination that cited
`UGA-INV-01` and `UGA-INV-10` as two independent signals double-counted one finding.

### 2.5 E-4A — Permit Issuance Existence Path

| Operation | Status |
|---|---|
| register creation | **MISSING** |
| register append | **MISSING** |
| register update | **MISSING** |
| register consumption | **IMPLEMENTED** (`:376-399`, `:432-543`, reached at `:573`) |
| register persistence | **MISSING** |

`00-BOOK/DATA/allocation-permits.json` does not exist. The only code that writes it is the
test fixture `platform/tests/test_ledger_authority.py:61-87`.

Because `permit` is mandatory with no default (`:546`), a complete enforcer with no issuer is
not a permissive gap — it is a **total block**. Measured against the live ledger, all three
possible values are refused:

```
permit=None            -> PermitRefused: permit must be a permit_id string or NO_ALLOCATION
permit='P-ANY'         -> PermitRefused: 'P-ANY' is not in 00-BOOK/DATA/allocation-permits.json
permit=NO_ALLOCATION   -> PermitRefused: NO_ALLOCATION was asserted, but this write
                          ALLOCATES … UNMEASURED_MAPS=['history']
```

`register.sh:216` — the repository's single sanctioned minting invocation, asserted as such
by `platform/tests/test_verification_purity.py:122-134` — passes **no** `--permit`. It is
refused at `:449-451`, so REG-AUTO-001 Phase 1 fails and the nine dependent phases never
run. Three `--permit` CLI flags exist (`ukb.py:2497`, `ukb.py:2555`,
`uga_engine.py:2079`) whose help text names a file the repository never produces.

---

## 3. Evidence

| # | Claim | How established | Mutating? |
|---|---|---|---|
| EV-1 | `commit()` step order and the three mutation windows | source read, `ledger_authority.py:546-593` | no |
| EV-2 | No locking or atomic-rename primitive in either writer | `grep` for `fcntl\|flock\|LOCK_EX\|O_EXCL\|threading.Lock\|filelock` and `os.replace\|os.rename\|fsync` over `00-BOOK/tools/` + `00-MASTER/UCOS-UGA-001/` — zero ledger matches | no |
| EV-3 | TOCTOU destroys a persisted identifier (E1-F1) | executed, temp-dir ledger, concurrent write injected at `git_head` | temp dir only |
| EV-4 | Permit replay succeeds after restore (E1-F3) | executed, temp-dir ledger | temp dir only |
| EV-5 | Record-body rewrite passes all checks (E1-F4) | executed, temp-dir ledger | temp dir only |
| EV-6 | `history` ⇒ `allocating=True` on a byte-identical no-op; `NO_ALLOCATION` refused | executed **against the live ledger** via `LA.plan` + `LA._verify_permit` — both read-only | **no** |
| EV-7 | Divergent writer undetected (E2-F1) | executed, temp-dir ledger | temp dir only |
| EV-8 | Silent writer reported as allocation (E2-F2) | executed, temp-dir ledger | temp dir only |
| EV-9 | `NO_ALLOCATION` permits file mutation (E2-F4) | executed, temp-dir ledger | temp dir only |
| EV-10 | `LEDGER-INV-01` does not match either production writer | executed against the live compiled patterns `U._PY_LEDGER_WRITE`, `U._PY_LEDGER_OPEN` | no |
| EV-11 | `audited == set(by_object.keys())`; INV-01 and INV-10 violation sets identical | executed, `uga_engine.build(mint=False)` — the `if not mint` branch (`:297-300`) allocates nothing and `build` never calls `LA.commit` | **no** |
| EV-12 | Register absent; no production writer | `grep` inventory + `os.path.exists` + `ls 00-BOOK/DATA/` | no |
| EV-13 | All three permit values refused on the live ledger | executed, `LA._verify_permit` (read-only) | **no** |
| EV-14 | `register.sh` passes no `--permit` | source read, `register.sh:211-216`. **`register.sh` was not executed** — running it would mutate the repository. | no |

`git status --porcelain 00-BOOK/DATA/id-ledger.json` is empty before and after all work. No
repository state was mutated by this phase. The probe harness was deleted; every probe is
reproduced inline in the subordinate reports.

---

## 4. Unresolved defects

**Nothing was closed by code change.** Each of the four work items specified a
*determination* deliverable — "Produce ⟨report⟩", "Classify", "Determine only", "Only
determine whether code exists" — and none authorized a code change. Stating this plainly:
the blocker set was **characterized and bounded**, not shrunk by remediation. That is the
honest reading of Phase 0's completion criteria, which list six reports and no code artifact.

The 14 defects below remain open. The **Remedy class** column is the load-bearing output of
this phase: it separates defects whose fix decides nothing about authority from those whose
fix cannot be written without a governance answer.

| ID | Defect | Status | Remedy class |
|---|---|---|---|
| E1-F1 | TOCTOU verification → write | REPRODUCED | **Governance-independent** — re-read and compare before writing |
| E1-F2 | No concurrency control | REPRODUCED | **Governance-independent** — exclusion or compare-and-swap |
| E1-F3 | Permit replay after restore | REPRODUCED | **Governance-dependent** — requires deciding single-use semantics (issuance) |
| E1-F4 | Record bodies unchecked | REPRODUCED | **Governance-independent** — widen the projection to the whole record |
| E1-F5 | `history` unclassified | REPRODUCED | **Governance-independent** — classify an existing key into one of two existing sets |
| E1-F6 | Minting arithmetic vs. verification read | REPRODUCED as window | **Governance-independent** — needs a test, not a decision |
| E1-F7 | `raw_before` unreconciled | REPRODUCED | **Governance-independent** — one comparison |
| E2-F1 | Divergent writer | REPRODUCED | **Governance-independent** — parse and compare after write |
| E2-F2 | Silent writer | REPRODUCED | **Governance-independent** — as above |
| E2-F3 | `bytes_changed` unenforced and unrendered | REPRODUCED | **Governance-independent** — assert it against `allocating`; render it |
| E2-F4 | `NO_ALLOCATION` permits mutation | REPRODUCED | **Governance-independent** — the sentinel's own docstring (`:293-296`) already claims this property; making the claim true adds no authority |
| E2-F5 | `LEDGER-INV-01` lexically blind | REPRODUCED | **Governance-independent** — measurement scope, not policy |
| E2-F6 | Serializer equivalence unproven | REPRODUCED as gap | **Governance-independent** — needs a round-trip test |
| E3 | `UGA-INV-10` tautology | REPRODUCED | **Governance-dependent** — replacing it requires defining *mutation* and *audit event* (domain rules) |
| E4A | No issuance path | REPRODUCED | **Governance-dependent** — requires issuance semantics, issuer identity, expiry |

**RESOLVED: 0. REPRODUCED: 15. NOT REPRODUCIBLE: 0.**

Every defect investigated was reproduced. Nothing in Section E's four items dissolved under
examination — which is itself the phase's substantive result: the governance-independent
blocker set did not shrink by discovering that some blockers were artifacts of misreading.

---

## 5. Residual governance dependencies

**Diagnosis: zero governance dependency.** Every finding above holds under every possible
answer to FD-1, FD-2, FD-3′, FD-4 and FD-5. Each concerns a property prior to, or orthogonal
to, any authority question:

- E1-F1/F2/F6/F7 and E2-F1/F2/F3/F5/F6 — *is the state that was verified the state that was
  written?* No authority defines this.
- E1-F4/F5 and E2-F4 — *is the mutation observed at all?* Prior to any question of
  permission.
- E-3 — *does the measurement measure what it names?* Arithmetic.
- E-4A — *does the code exist?* Existence.

**Remedy: three of fifteen are governance-dependent.**

| Defect | Governance root it touches | Why it cannot be closed in Phase 0 |
|---|---|---|
| E1-F3 | issuance semantics | Recording permit use requires deciding whether a permit is single-use, which is a permit rule — forbidden by Constraint 4. |
| E-3 | domain rules | Replacing the invariant requires defining what counts as a mutation and what an audit event must contain. |
| E-4A | issuance semantics, issuer identity, temporal legitimacy | Constraint 4 forbids introducing permits, ratification rules and temporal legitimacy decisions. Creating an issuance path requires all three. |

The remaining twelve are governance-independent in remedy as well as diagnosis. No remedy is
proposed, specified, sketched or ranked here; the classification above is a partition of the
existing defect set, not a design.

### 5.1 One dependency ordering, recorded as fact

E-4A currently blocks every write, which makes E2-F1…F4 and E1-F1…F2 latent rather than
active. Supplying any issuance path activates all of them at once. This is stated as a
measured consequence of `permit` being mandatory (`ledger_authority.py:546`) plus the
register's absence — not as sequencing advice.

---

## 6. Exact blocker count remaining

### 6.1 By work item

| Work item | Blockers | Class |
|---|---|---|
| E-1 | 7 | 6 UNSAFE + 1 UNVERIFIABLE |
| E-2 | 7 | 6 UNSAFE + 1 UNPROVEN (E2-F7 counted under E-4A's activation dependency, not double-counted) |
| E-3 | 1 | TAUTOLOGY |
| E-4A | 1 | MISSING (4 of 5 operations) |
| **Total** | **15** | — |

E2-F7 is a dependency statement about E-4A rather than a distinct defect; it is included in
E-2's seven for traceability and excluded from no total, since E-4A is counted once.

### 6.2 By remedy class — the phase's requested output

```
TOTAL BLOCKERS REMAINING IN SECTION E SCOPE ........... 15

  Governance-INDEPENDENT remedy (closable without any
  answer to FD-1 / FD-2 / FD-3′ / FD-4 / FD-5) ........ 12
      E1-F1, E1-F2, E1-F4, E1-F5, E1-F6, E1-F7,
      E2-F1, E2-F2, E2-F3, E2-F4, E2-F5, E2-F6

  Governance-DEPENDENT remedy — the irreducible core ...  3
      E1-F3   (single-use / permit-use recording)
      E-3     (definition of mutation + audit event)
      E-4A    (permit issuance path)

  RESOLVED this phase .................................  0
  NOT REPRODUCIBLE ....................................  0
```

### 6.3 The irreducible governance-dependent core

**3 blockers.** E1-F3, E-3, E-4A.

That is the reduction Phase 0 was run to obtain: of the fifteen defects reproduced across
Section E's four items, **twelve have remedies that decide nothing about authority**, and the
governance-dependent residue is three. The twelve are not closed — closing them was not
authorized by any of the four work items — but they are now separated from the three, with
source references and executed reproductions for each.

---

## 7. Phase 0 completion criteria

| # | Criterion | Status |
|---|---|---|
| 1 | All four reports exist | **MET** — `PHASE0-E1-ATOMICITY-REPORT.md`, `PHASE0-E2-CORRESPONDENCE-REPORT.md`, `PHASE0-E3-CLAIM-INTEGRITY-REPORT.md`, `PHASE0-E4A-ISSUANCE-PATH-REPORT.md` |
| 2 | Every finding backed by source references | **MET** — every finding cites file:line; 14 evidence items, 11 of them executed |
| 3 | Every finding classified SAFE / UNSAFE / UNPROVEN | **MET** — 12 SAFE, 12 UNSAFE, 2 UNPROVEN/UNVERIFIABLE across E-1 and E-2; E-3 carries its required four-way verdict; E-4A its required five-way per-operation verdict |
| 4 | Every governance statement excluded | **MET** — no authority, permit rule, ratification rule, domain rule, threat model or temporal decision is asserted. Where a remedy would require one, the requirement is named and left open (§5) |
| 5 | Every blocker categorized RESOLVED / REPRODUCED / NOT REPRODUCIBLE | **MET** — 0 / 15 / 0 |
| 6 | Final report exists with findings, evidence, unresolved defects, residual governance dependencies, exact blocker count | **MET** — this document, §2 / §3 / §4 / §5 / §6 |

### 7.1 Deviation, stated explicitly

The objective line reads *"close all governance-independent blockers."* No blocker was closed
by code change. Twelve are now **shown** to be closable without any governance answer, and
three are shown not to be. If code remediation of those twelve was intended within Phase 0,
it was not performed, and the reason is that each work item's deliverable was a report and
Constraint 4 bounded what may be introduced. Flagging rather than assuming: the twelve
governance-independent remedies await explicit authorization.

---

## 8. Stop condition

Phase 0 ends here.

- FD-1, FD-2, FD-3′, FD-4, FD-5 — **not answered**.
- Governance — **not redesigned**.
- New authorities — **none introduced**.
- Permits, ratification rules, domain rules, threat models, temporal legitimacy decisions —
  **none introduced**.
- Every governance root — **treated as UNKNOWN throughout**.
- Phase 1 artifacts — **none created**.
- Governance choices — **none recommended**.

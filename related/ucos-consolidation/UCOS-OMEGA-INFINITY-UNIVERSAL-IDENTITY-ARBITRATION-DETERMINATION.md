# UCOS Ω∞ — UNIVERSAL IDENTITY ARBITRATION DETERMINATION

**Which Universal ID is canonical when a subject holds two? — resolving `URS-2` before UGA synchronization is executed**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Mints no identity, retires no identity, renumbers nothing, declares no namespace, opens no registry, and arbitrates no live case. The model in §12–§15 is a proposal requiring the authority named in §14.5 before it may be applied to a single subject. |
| Mode | ANALYSIS ONLY · **NO IDENTITY CHANGE · NO REGISTRY CHANGE · NO CERTIFICATION CHANGE · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subject | `URS-2` — 217 subjects holding two Universal IDs each (25 at HEAD, 192 working-tree-only) |
| Law read | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` (AIF-L01…L24) · `00-MASTER/UIS-001/` (plane register, ledger measurement register, `uis_engine.py`) · `constitutional-authority-alignment.json` `identity_authority_resolution` / `identity_namespace_resolution` · `AUTH-INF-001` · `00-BOOK/tools/config.py` `EXCLUDE_DIR_PREFIXES` |
| Method | Direct measurement of the ledger's three maps at HEAD and in the working tree; per-subject mint-order reconstruction against git commit dates; source reading of the conformance metric that reports this condition as zero |
| Findings raised | **10** (`UIA-1`…`UIA-10`) · 2 CRITICAL · 3 HIGH · 4 MEDIUM · 1 LOW |
| Central result | The condition is a **direct violation of `AIF-L02`**, not a design gap; and **no fixed-authority or first-mint rule resolves it**, because the 217 split into two groups with **opposite mint orders** (§5). Arbitration must be **class-determined**, not time-determined or rank-determined. |

---

## 1. Objective, Method, and Standing Limitation

### 1.1 Objective

The UGA Reality Synchronization Determination found 217 subjects holding two Universal IDs
and blocked CAAR's first build on the condition rather than on a green gate (`URS-2`, §17.3
there). It named the defect and deliberately did not resolve it. This determination asks the
question that must be answered before step S-4 of that synchronization strategy:

> **When one subject holds more than one Universal ID, which one is canonical, by what rule,
> decided by whom, and what becomes of the other?**

### 1.2 Method

Three disciplines, each chosen because a prior artifact's absence of it produced a wrong
answer:

1. **Read the law before proposing a rule.** The repository has a ratified twenty-four-law
   identity constitution (`AIF-L01…L24`). Nine of its laws bear directly on this question.
   Six of them settle it. No arbitration rule is proposed below that is not derived from one.
2. **Measure the two sub-populations separately.** §5 shows that treating the 217 as one
   population is what makes the problem look unsolvable.
3. **Read the metric that says the problem does not exist.** `uis_engine.py` publishes
   `identities_multiple: 0`. §4.3 determines why.

### 1.3 Standing limitation

`classify()` still returns `ERROR`. Nothing below is a classification, an identity, or a
certification of record. **No identity was minted, retired, superseded, renumbered or
resolved in producing this determination**; `by_object` stands at 4,914 and `by_path` at
1,492 before and after (§19).

---

## 2. Analysis 1 — Existing Identity Authorities

**Finding: two planes, six located mechanisms, and one minting authority the located crosswalk does not list.**

### 2.1 What the alignment register declares

`constitutional-authority-alignment.json` `identity_authority_resolution` declares
`UCKP-ART-05` the one identity authority and names **two planes**:

| Plane | Home | Shape | Role |
|---|---|---|---|
| `CONSTITUTIONAL_OBJECT` | `engine/uckp/identity.py` | `urn:ucos:ucko:<namespace>:<local_name>` | **SUPREME — this IS `UCKP-ART-05`** |
| `REPOSITORY_OBJECT` | `00-BOOK/DATA/id-ledger.json` | `UCOS-<CATEGORY>-<NNNNNN>` | **PERSISTENCE — the ONE such binding in this repository** |

The second plane holds three maps: `by_path`, `by_object`, `by_observation`. **This is the
decisive structural fact of the entire determination:** the two identifiers a dual-identity
subject holds are not on two planes. They are two entries in **two maps of one plane**, in
one file, minted from one `category_seq` counter, under one grammar.

### 2.2 What actually mints, measured

| Authority | Map | Population | Minted at | Live count |
|---|---|---|---|---|
| `REG-AUTO-001` / `UMB-IMP-001` (`00-BOOK/tools/register.sh`, `ukb.py`) | `by_path` | corpus-eligible documents | ISO wall-clock timestamp | 1,492 |
| `UCOS-UGA-001` (`00-MASTER/UCOS-UGA-001/uga_engine.py`) | `by_object` | version-controlled non-corpus objects | `commit:<sha12>` | 4,914 |
| observing programmes (`UCOS-AEE-001`, `UCOS-RIB-001`, `UCCEP-000005`) | `by_observation` | observation subjects | `commit:<sha12>` | 7 |

All three write `UCOS-<CATEGORY>-<NNNNNN>` into one ledger, advancing one shared
`category_seq`. Uniqueness of *identifiers* is therefore guaranteed by construction and
holds under measurement (0 collisions, §4.1). Uniqueness of *identity per subject* is
guaranteed by nothing.

### 2.3 The located plane crosswalk does not list UGA

`00-MASTER/UIS-001/03-IDENTITY-PLANE-AND-GRAMMAR-REGISTER.md` enumerates the five `AIF-L03`
planes and the six mechanisms that realize them:

| Plane | Role | Realized by | Mechanism listed |
|---|---|---|---|
| P1 content | VERIFIES | MECH-UKIP | Knowledge Registry content identity |
| **P2 durable** | **IDENTIFIES** | **MECH-UKB** | **Universal ID Ledger allocator (`00-BOOK/tools/ukb.py`)** |
| P3 admission-ordinal | RENDERS | MECH-NOMENCLATURE | Universal Nomenclature crosswalk |
| P4 logical | NAMES | MECH-EPIC001, MECH-UCKP | Registry Platform identity · UCKP Layer Zero |
| P5 runtime | BINDS | MECH-UCXI | Universal Context identity |

`UCOS-UGA-001` appears nowhere. Its mint satisfies every property of P2 — same ledger, same
counter, same grammar `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$`, minted once, never reused — and
the register's section *"Why four schemes is the architecture and not a defect"* argues the
lawfulness of each listed mechanism **on the grounds that each occupies a different plane**.
That argument does not extend to a second mechanism on the same plane, and was never asked
to.

**`UIA-5` (HIGH):** `UCOS-UGA-001` mints durable (P2) identities into the one identity
ledger under the declared artifact-plane grammar, and is absent from the located
plane-and-mechanism crosswalk. The register's "one scheme per plane" justification therefore
does not cover the mechanism that produces half the ledger's entries (4,914 of 6,413).

### 2.4 The test that was written and never applied here

`identity_namespace_resolution` declares its own disqualifying test:

> **`second_authority_test`:** *"A second authority over the SAME namespace would be a rival
> mint or a rival admission registry for the same population. None was found…"*

It was applied to `UCKP-URN-IDENTITY` vs `KNOWLEDGE-OBJECT-IDENTITY` — two namespaces that
share no keyspace — and correctly returned "none found." It was never applied to `by_path`
vs `by_object`, which share the keyspace, the counter, the file and, for 217 subjects, the
population.

**`UIA-10` (LOW):** The alignment register's own `second_authority_test` returns a
different answer when applied to the two maps of the `REPOSITORY_OBJECT` plane than to the
two namespaces it was applied to; the test was never run against the pair that fails it.

---

## 3. Analysis 2 — Identity Precedence Rules

**Finding: no precedence rule exists anywhere, and the repository has a declared form for one it did not use here.**

### 3.1 Nothing declares precedence between the maps

Searched directly: `id-ledger.json` carries `version`, three maps, counters and `history` —
no precedence field. `uga-declaration.json` `one_identity_authority` declares *"This
programme mints from the SAME ledger and the SAME `category_seq` counter as the corpus. It
creates no second authority and no second sequence"* — a statement about the counter, not
about which id wins when both exist. `constitutional-authority-alignment.json` declares
plane roles (SUPREME, PERSISTENCE) but not map precedence within the persistence plane.
`mutation-governance-boundary.json` declares `ORDERED PRECEDENCE` for **classification
rules**, not for identity.

### 3.2 The repository does have a form for declaring precedence

`platform/universal_ownership/catalog/ucos-ownership-declarations.json` carries a top-level
`precedence` key alongside `provider_id`, `authority`, `description`, `schema` and
`assignments`. Ownership — a strictly less foundational concern than identity — has a
declared precedence field. **Identity has none.** The form exists; it was not applied to the
harder question.

### 3.3 Why a precedence rule alone would be the wrong instrument

A precedence rule ranks authorities: *"`REG-AUTO-001` outranks `UCOS-UGA-001`"*, or the
converse. §5 measures that such a rule gives the wrong answer for one of the two
sub-populations no matter which way it is oriented, because the two groups arose from
opposite orderings and opposite causes. **Precedence is the wrong shape of answer; §12
derives the right one from `AIF-L06`.**

---

## 4. Analysis 3 — Subject-to-Identity Relationship

**Finding: the law states the cardinality explicitly, and the repository's conformance engine measures a different thing under the right name.**

### 4.1 What the law requires

> **`AIF-L02` Opaque Durable Identity (P2).** *"**One** minted-once, immutable, opaque,
> authority-namespaced identity **per artifact**; never content/order/path-derived; never
> reused."*

> **`AIF-L06` Path-Independent Admission Key.** *"Identity is keyed by `(AuthorityID,
> local-key)`, decoupled from path."*

> **`AIF-L07` Authority-Namespaced Uniqueness.** *"Global uniqueness by construction; no
> global coordination required."*

`AIF-L02` settles the cardinality question in four words: **one per artifact**. The 217 are
not an ambiguity in the law to be resolved by interpretation; they are a measured
non-conformance with a ratified law.

`AIF-L06` settles the *shape* of the key, and is the load-bearing law for §12: the admission
key is the pair `(AuthorityID, local-key)`. Two authorities admitting the same subject
therefore produce two lawful keys — which is exactly why `AIF-L07`'s "uniqueness by
construction" holds for identifiers while `AIF-L02`'s "one per artifact" fails for subjects.
**The two laws are not in conflict; they describe different objects.** `AIF-L07` protects
the identifier space. `AIF-L02` protects the subject. Only the second is violated.

### 4.2 What is measured

| Property | Measured at this baseline | Law | Status |
|---|---|---|---|
| Identifier uniqueness | 0 collisions across all three maps | `AIF-L07` | **HOLDS** |
| Identifier never reused | 0 reused; 2 retired identities retained | `AIF-L02`, `AIF-L17` | **HOLDS** |
| Identifier never renumbered | 0 renumbered | `UIL-06` | **HOLDS** |
| Grammar conformance | 0 failures | `AIF-L02` | **HOLDS** |
| **One identity per artifact** | **217 subjects hold two** | **`AIF-L02`** | **VIOLATED** |

**`UIA-1` (CRITICAL):** 217 subjects hold two durable (P2) Universal IDs, in direct
non-conformance with `AIF-L02`'s "one … identity per artifact." Every other measured
property of the identity system holds. The defect is singular, precisely bounded, and
already illegal under a ratified law — it requires enforcement, not new legislation.

### 4.3 The conformance metric named for this condition reads zero, vacuously

`00-MASTER/UIS-001/04-IDENTITY-LEDGER-MEASUREMENT-REGISTER.md` publishes forty-two measures.
One is named **`identities_multiple`**. It reads **`0`**.

Its implementation, at `uis_engine.py:317-322`:

```python
# ---- derived plane
path_to_ids: dict[str, set[str]] = {}
for rec in records:                                   # records = artifacts.json artifacts
    path = str(rec.get(r_path) or "")
    if path:
        path_to_ids.setdefault(path, set()).add(str(rec.get(r_id) or ""))
multiple = sorted(p for p, ids in path_to_ids.items() if len(ids) > 1)
```

`records` is `artifacts.json`'s artifact collection (`uis_engine.py:252`). The measure asks
*"does one path appear twice **within the corpus registry**?"* — a condition that register's
own construction makes impossible. **It never reads `by_object`.** A subject holding one
corpus id and one object id is invisible to it by construction, and the zero is therefore
true and uninformative.

This is precisely the vacuity `mutation-governance-boundary.json` diagnosed in itself:

> *"the invariants quantified over classes rather than over artifacts, which made that
> silence vacuously lawful."*

Here the invariant quantifies over **one register** rather than over **the subject across
planes**, and the silence is vacuously lawful in the same way. Two independent instruments
in this repository have now been found failing by the identical mechanism.

**`UIA-2` (CRITICAL):** `identities_multiple` — the one published measure named for this
exact condition — quantifies over `artifacts.json` records only and reports `0` while 217
subjects hold two identities. The condition is unmeasured, not measured-and-clean, and no
gate anywhere fails on it.

---

## 5. Analysis 4 — Duplicate Identity Claims

**Finding: the 217 are two populations with opposite mint orders and opposite causes. This is the result that determines the arbitration model.**

### 5.1 The split

| | Group A | Group B |
|---|---|---|
| Count | **25** | **192** |
| Present at | **HEAD** and working tree | **working tree only** |
| Location | `00-MASTER/` (13) · `intelligence/` (11) · one root pointer (1) | repository-wide |
| Minted first | **corpus (`by_path`)** — 25 of 25 | **UGA (`by_object`)** — 192 of 192 |
| Second mint by | `UCOS-UGA-001` | `REG-AUTO-001` (uncommitted) |
| Cause | Corpus admitted the path **before** the exclusion boundary reached its present form; UGA then lawfully minted because the path is now corpus-excluded | UGA absorbed the document as `EXCLUDED_DOCUMENT` **before** the corpus registered it; the corpus then lawfully minted on registration |
| Governing UGA class | `EXCLUDED_DOCUMENT` (201 across both groups) · `DATA_OBJECT` (16) | same |

Mint order was reconstructed per subject by resolving each `by_object` `first_seen`
(`commit:<sha12>`) to its commit date and comparing against the `by_path` ISO timestamp:

```
MINT ORDER over 217:  {'corpus first': 25, 'uga first': 192}
```

The 192 accrued across **eight distinct commits** between 2026-08-12 and 2026-08-21, so this
is not one historical event but a standing process.

### 5.2 Group A is an already-registered finding, one step further on

The 25 are exactly the paths `00-BOOK/tools/config.py` `EXCLUDE_DIR_PREFIXES` excludes —
`00-MASTER/` (13), `intelligence/` (11), and the single root operational-memory redirect
(1). They are also, exactly, `UIS-001`'s `nonsource_identity_admissions = 25`, reported as
**`UIS-F-001`**:

> *"The identity ledger records permanent universal identities for paths that lie inside a
> currently excluded location … These are legacy admissions: they were minted before the
> exclusion authority reached its present form, and `AIF A/G7` grandfathers the imported
> corpus with frozen ordinals."*

`UIS-F-001` diagnosed the corpus identity as misplaced. It did not observe that each of
those 25 paths, being corpus-excluded, subsequently received a **second** identity from the
authority that governs corpus-excluded objects. **The dual identity is `UIS-F-001`'s
downstream consequence, unnoticed because the measuring engine could not see it (§4.3).**

**`UIA-4` (HIGH):** Group A's 25 dual identities are identically the 25 paths of
`UIS-F-001`, a finding already registered, bounded and referred — with the dual-identity
consequence unobserved by the register that raised it.

### 5.3 Why the split defeats every simple rule

| Candidate rule | Group A result | Group B result | Verdict |
|---|---|---|---|
| First mint wins | keeps the **corpus** id for a path the corpus now excludes | keeps the **UGA** id for a registered corpus document | **Wrong for both** |
| Last mint wins | keeps the UGA id — correct | keeps the corpus id — correct | Correct today, **by coincidence**: it encodes "whoever wrote last," which `AIF-L20` forbids as identity determinism derived from process order |
| `REG-AUTO-001` always outranks `UGA` | keeps a corpus id for an excluded path | correct | **Wrong for A** |
| `UGA` always outranks `REG-AUTO-001` | correct | keeps `UCOS-EXDOC-*` for a registered document | **Wrong for B** |
| **Governing-class-determined (§12)** | **correct** | **correct** | **Correct for both, by construction** |

**`UIA-3` (HIGH):** The 217 divide into two groups with opposite mint orders and opposite
causes, so no fixed-authority precedence rule and no time-ordered rule is correct for both.
Arbitration must be determined by which authority's admission predicate the subject
satisfies **now**.

### 5.4 The condition is growing

Group B grew from 0 to 192 in the standing uncommitted corpus registration, and grows by one
for every future registration of a document UGA had already absorbed. `URS-6`'s absorbing
terminal is the minting mechanism: absorption yields a class, a class yields an id category,
an id category yields a mint. **Arbitration declared after the next registration wave is
arbitration over a larger population, not a smaller one.**

---

## 6. Analysis 5 — Migration Strategy

**Finding: the law already names the transition, so migration is a recorded event, never a rewrite.**

### 6.1 The transition vocabulary exists

> **`AIF-L15` Declared-Intent Transitions.** *"version / copy / clone / fork / split / merge
> / **supersede** / replace / restore / new are author-declared and machine-validated."*

> **`AIF-L16` Deterministic Identity Decision.** *"A four-step algorithm decides
> version/new/transition; **ambiguity fails closed**."*

`supersede` is a ratified, machine-validated transition. `AIF-L16` further establishes that
the identity decision is *algorithmic and fail-closed* — which is the licence for §13's
selection rules to be an algorithm rather than a case-by-case adjudication, and the
requirement that an undecidable case must refuse rather than pick.

### 6.2 What migration therefore is, and is not

| Migration is | Migration is not |
|---|---|
| Appending a supersession record naming the surviving id | Deleting the superseded id |
| Marking one of two recorded identities `CURRENT` | Renumbering either id |
| Recording the transition as an event | Editing a `first_seen`, an ordinal, or a history entry |
| Re-pointing *publishers* (registries, projections) at the canonical id | Re-pointing the ledger, which keeps both |

### 6.3 Sequencing against the UGA synchronization strategy

`URS`'s S-4 and S-5 are the steps this determination feeds. Two ordering constraints are
measured rather than preferred:

1. **Arbitration must precede S-2 (`uga_engine.py run`), not follow it.** The projected next
   run flips 192 subjects from `EXCLUDED_DOCUMENT` to `DOCUMENT_ARTIFACT` and switches the
   published id from the `EXDOC` id to the corpus id — **performing an un-recorded, un-arbitrated
   supersession for 192 subjects as a side effect of a refresh.** Under the model in §12 that
   flip is the *correct outcome*; performed without a recorded supersession event it is
   `AIF-L15` non-compliance at scale, and it silently orphans 192 identities.
2. **Group A cannot be arbitrated by re-running anything.** Its 25 subjects are stable under
   any UGA run: they are corpus-excluded, so UGA will keep classifying them
   `EXCLUDED_DOCUMENT` and keep publishing the `EXDOC` id, while the corpus keeps its
   `by_path` entry. **Group A requires an explicit owner act; Group B requires an explicit
   record around an act that will otherwise happen implicitly.**

---

## 7. Analysis 6 — Historical Identity Preservation

**Finding: preservation is absolute, already enforced, and fully compatible with arbitration.**

### 7.1 What may never happen

> **`AIF-L17` Forward-Only Compensation.** *"No deletion or edit of Recorded Truth; correction
> is a new event; **retired identities are never reissued**."*

> **`AIF-L13` Prepare/Commit/Abort Atomicity.** *"Mints are provisional until seal; abort
> discards (**no orphan identity**); commit seals atomically."*

> **`IL-INF-07`** (`AUTH-INF-001`) — *"No reading … SHALL invalidate, renumber, mutate, or
> close any existing certification, freeze, registry, program, domain, artifact, **identity**,
> page, edge, or signal."*

> **`id_preservation`** (alignment register) — *"Every identifier that existed before this
> binding exists after it, unchanged … measured by `CAA-INV-04`, which recomputes the
> derivation over every ledger id and fails on any collision or **any id it cannot carry
> through verbatim**."*

And `UIS-001` states the operational consequence for a measurement that finds such a defect:

> *"erasing or editing a recorded identity is forbidden by the append-only law, so a
> measurement that 'fixed' one would be committing the defect it reports."*

### 7.2 Arbitration does not conflict with any of them

Selecting a canonical identity is **not** retiring the other. Both remain recorded, both
remain unique, both remain unreissued, both continue to carry through `CAA-INV-04`'s
derivation verbatim. What changes is a **published pointer** and a **recorded transition** —
neither of which is Recorded Truth being deleted or edited; both are new events, which is
exactly the form `AIF-L17` prescribes for a correction.

`AIF-L13` supplies the sharpest constraint on the model and is worth stating explicitly:
*"abort discards (no orphan identity)."* The 192 identities that the next UGA run would leave
unreferenced are **orphan identities** in precisely this sense — minted, sealed, and pointing
at nothing. `AIF-L13` forbids producing them. §13's rules are written to satisfy this.

**No finding is raised on this dimension.** Preservation law is clear, is enforced by a
live invariant, and constrains the model without obstructing it.

---

## 8. Analysis 7 — Universal Object Compatibility

**Finding: changing the published id changes the derived UCKO URN, so arbitration has a measurable downstream cost that must be sequenced.**

### 8.1 The derivation chain

`engine/uckp/uga_projection.py` projects each UGA registry entry into a constitutional
object:

```python
return UCKO.mint(namespace=REPOSITORY_NAMESPACE,
                 local_name=entry["universal_id"], ...)
```

and `identity_authority_resolution.derivation` declares the resulting shape:

```
UCOS-ENGINE-000496  →  urn:ucos:ucko:ucos-repository:UCOS-ENGINE-000496
```

The URN is a name-based UUID over `(namespace, local_name)`. **The local name is the
published Universal ID.** So for each of the 217, the constitutional-plane URN today is
derived from the *UGA* id (the registry publishes the `by_object` id for 217 of 217), and
selecting the corpus id as canonical would derive a different URN.

### 8.2 Why this is a cost and not a violation

`AIF-L03` declares the planes orthogonal and non-substitutable, and the P4 logical-plane
identity is *"pure, total, clock-free, storage-free"* — a pure function of its inputs. If
the input changes, the output changes, and that is correct behaviour for a pure function,
not a mutation of a recorded identity. The constitutional plane holds no ledger entry that
would be edited.

The cost is that **five digests move**: `07-CERTIFICATION.json`'s `existence_digest`,
`identity_digest`, `registry_digest`, `graph_digest` and `invariant_digest` are all computed
over surfaces that carry the published id. Arbitration therefore invalidates the current
UGA certification proof and requires it to be recomputed — which `CR-INF-011` already
permits (*"certification closes scope, never evolution"*) and `AIF-L21` already structures
(immutable historical attestation vs recomputed current status, in distinct stores).

**`UIA-9` (MEDIUM):** Selecting a canonical identity re-derives the constitutional-plane URN
for each arbitrated subject and invalidates all five UGA certification digests. Lawful under
`AIF-L03`/`AIF-L21`, and it makes arbitration a certification-affecting act that must be
sequenced with a recomputation rather than performed underneath a standing `CERTIFIED`
verdict.

### 8.3 A second, smaller incompatibility

`uga_projection.py`'s `_CATEGORY_MAP` maps UGA's object classes onto `uckp.governed-category`
and raises `UnrecognisedUGAValueError` on an unmapped class; `_LIFECYCLE_MAP` does the same
for lifecycle. Arbitration moves 192 subjects from `EXCLUDED_DOCUMENT` to
`DOCUMENT_ARTIFACT`. Both classes are mapped, so **no raise results** — verified by reading
the map. This dimension is compatible; it is recorded because the adjacent `RETIRED` case
(`URS-5`) is not, and a reader should not infer from that one that this one fails too.

---

## 9. Analysis 8 — Registry Impact

**Finding: four registers publish or consume an identity for these subjects; only one of them holds an identity that must not move.**

| Register | What it holds for a dual subject | Impact of arbitration |
|---|---|---|
| `id-ledger.json` `by_path` | The corpus identity + `history` + page range | **None.** Both entries stay, unedited (`AIF-L17`) |
| `id-ledger.json` `by_object` | The UGA identity | **None.** Both entries stay, unedited |
| `artifacts.json` | 1,461 corpus records keyed on `universal_id` | For Group A: the record exists for a path the exclusion boundary excludes — `UIS-F-001`'s standing question, unchanged by arbitration |
| UGA `02-UNIVERSAL-OBJECT-REGISTRY.json` | **The published id — the `by_object` one, for 217 of 217** | **This is where arbitration lands.** 192 entries change published id and class on the next run |
| UGA `03-AUDIT-UNIVERSE.json`, `04-RELATIONSHIP-GRAPH.json` | 34,872 relationships keyed on published ids | Re-derived; edges for 192 subjects re-key |
| `engine/uckp/uga_projection.py` consumers | Derived URNs | Re-derived (§8) |

### 9.1 The one thing that must not move

`id-ledger.json` `history` records 1,492 identity histories as contiguous append-only
sequences from one (`UIL-13`, measured `history_not_append_only: 0`). Arbitration must add no
entry to `history` for the superseded id and must renumber no `seq`. The supersession record
belongs in a **new** structure, not inside an existing identity's history — otherwise the
correction edits Recorded Truth, which is the defect it is correcting.

### 9.2 A grammar discrepancy surfaced while measuring

Two instruments declare the artifact-plane grammar, and they differ:

| Declared in | Grammar |
|---|---|
| `00-MASTER/UIS-001/03-IDENTITY-PLANE-AND-GRAMMAR-REGISTER.md` (from `artifact.schema.json`) | `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` |
| `constitutional-authority-alignment.json` `identity_authority_resolution.derivation.id_shape` | `^UCOS-[A-Z0-9]+-[0-9]{6}$` |

The second is strictly looser: it admits a leading digit and an unbounded category width.
Every live identity satisfies both (0 grammar failures measured), so nothing is currently
wrong — but two declarations of one grammar is a second definition of an existing primitive,
which `UCKP-ART-03` makes void, and the looser one is the one the URN derivation validates
against.

**`UIA-7` (MEDIUM):** Two instruments declare the artifact-plane identity grammar with
different patterns; the URN-derivation binding uses the looser. No live identity violates
either, so this is a latent divergence, not an active defect.

### 9.3 The surviving id's namespace may itself be ungoverned

Among the 217, the `by_path` side spans **78 distinct category namespaces** — `PHASEU` (17),
`MASTER` (13), `H06IMP` (13), `UNIVER` (11), `ADR` (11), `INTELLIGENCE` (11), and a long tail
of 72 more, most of them derived from the filename by the allocator's fallback. That is
`UIS-F-003`'s population: *"a majority of the live category namespaces hold minted identities
but match no declared rule."* The `by_object` side spans two (`EXDOC` 201, `DATAOBJ` 16),
both governed by UGA's `ID_CATEGORY`.

**`UIA-8` (MEDIUM):** For Group B, selecting the corpus id as canonical (the correct outcome
under §13) promotes an identity in a mostly-ungoverned namespace over one in a governed
namespace. Arbitration is still correct — governance of the namespace is `UIS-F-003`'s open
question, not a tiebreaker — but it makes `UIS-F-003` load-bearing for 192 more subjects.

---

## 10. Analysis 9 — Certification Impact

**Finding: arbitration is certification-affecting, and the law already separates the two things that must not be conflated.**

### 10.1 What is affected

| Surface | Claim today | Effect |
|---|---|---|
| UGA `07-CERTIFICATION.json` | `verdict: CERTIFIED`, five digests, scope 6,145 | **All five digests invalidated** (§8.2); already stale for other reasons (`URS-3`) |
| `certification.json` / `CERTIFICATION-REGISTRY.md` | scope 1,233 = HEAD corpus | Unaffected — the corpus identity set does not change; only which id is *published elsewhere* |
| `05-GOVERNANCE-INVARIANTS.json` | 29 of 29 PASS | Recomputed; gains one invariant if `AC-8` (§16) is adopted |

### 10.2 The law that governs how to do this without lying

> **`AIF-L21` Certification Duality.** *"Immutable Historical Attestation (RECORDED) vs
> recomputed Current Status (DERIVED), in distinct stores."*

> **`AIF-L01` Bifurcation of Truth.** *"Every datum is RECORDED or DERIVED, never both."*

The correct handling follows directly: the existing `CERTIFIED` verdict is a **historical
attestation** of what was true over the population it names, and remains a true statement
about that population at that commit. It is **not** amended, retracted or edited. A new
**current status** is recomputed after arbitration. Two records, two stores, no rewriting —
which is also `CR-INF-011`'s reading (*certification closes scope, never evolution*).

### 10.3 The ordering constraint this creates

Because arbitration invalidates the digests, and because `URS-3` already found the
certification surface asserting a verdict its own live gate contradicts, **arbitration must
not be performed underneath the standing verdict.** The sequence in §14.4 places the
recomputation explicitly rather than leaving it implied.

**No new finding is raised on this dimension**; the impact is fully covered by `UIA-9` and by
`URS-3`, which stands open.

---

## 11. Analysis 10 — Infinite Expansion Compatibility

**Finding: the arbitration model must admit an unknown future minting authority, and the two candidate models differ exactly on this point.**

### 11.1 The binding constraints

> **`UCKP-INV-14` infinite-extensibility.** *"Every vocabulary, adapter set and relationship
> class admits an unknown future member."*

> **`IL-INF-06` Expansion-always-available.** *"Every construct SHALL be read as admitting a
> next member without rewrite, renumber, or migration."*

> **`AIF-L24` Substrate Neutrality, Pinned Parameters.** *"CCF/algorithm/id-width/encoding are
> pinned parameters that widen append-only."*

A fourth ledger map, or a fifth minting authority, must be admissible without amending the
arbitration rule. This is not hypothetical: `by_observation` was itself added as a third map
after `by_path` and `by_object`, on the precedent `uga-declaration.json` records —
*"`EXEC-REG-001` established `by_execution` as an append-only map sharing the one identity
authority. `by_object` is the same construction for a second object class."* **The plane has
already grown three times.**

### 11.2 The test applied to the two candidate models

| Model | Admits a fourth authority without amendment? |
|---|---|
| **Authority-precedence table** (`REG-AUTO-001` > `UGA` > …) | **No.** A fourth authority requires a new row, ranked against every existing one — an amendment per addition, and an `O(n²)` question |
| **Governing-class determination** (§12) | **Yes.** A fourth authority declares its admission predicate; the rule *"the canonical id is the one whose authority's admission predicate the subject satisfies"* is unchanged |

This is an independent argument for §12's model, reaching the same conclusion as §5.3's
empirical one from a different direction. The empirical argument says a precedence table
gives wrong answers today; the constitutional argument says it cannot grow. **Both point at
the same replacement.**

**`UIA-6` (MEDIUM):** The two minting authorities record `first_seen` in two incomparable
grammars — ISO wall-clock (`2026-07-18T13:12:37+00:00`) for `by_path`, `commit:<sha12>` for
`by_object` and `by_observation`. Mint order across maps is not decidable from the ledger
alone; this determination reconstructed it only by resolving commits against git history
(§5.1). A future map admitted under `IL-INF-06` may introduce a third form. Separately, the
ISO form is a wall-clock reading inside a plane `AIF-L18` requires free of hidden state and
wall-clock.

---

## 12. Identity Arbitration Model

### 12.1 The model, in one statement

> **A subject holds exactly one canonical durable identity: the one minted by the authority
> whose admission predicate the subject satisfies under its currently governing class. Every
> other identity the subject holds is RECORDED, RETAINED, and marked SUPERSEDED-BY the
> canonical one. No identity is ever deleted, edited, renumbered, or reissued.**

### 12.2 Derivation from law, clause by clause

| Element | Law it derives from |
|---|---|
| "exactly one canonical durable identity" | `AIF-L02` — *one … identity per artifact* |
| "the authority whose admission predicate the subject satisfies" | `AIF-L06` — *identity is keyed by `(AuthorityID, local-key)`*: the authority is **part of the key**, so the key changes when the governing authority changes |
| "under its currently governing class" | `mutation-governance-boundary.json` `classification_rules` — one ordered, total, deterministic, fail-closed resolution over mutation subjects |
| "SUPERSEDED-BY" | `AIF-L15` — *supersede* is a declared, machine-validated transition |
| "RECORDED, RETAINED" | `AIF-L17`, `IL-INF-07`, `id_preservation` |
| "never … reissued" | `AIF-L02`, `AIF-L17`, `UIL-05` |
| "never renumbered" | `UIL-06` |
| decided algorithmically, ambiguity refuses | `AIF-L16` — *a four-step algorithm decides … ambiguity fails closed* |

**Not one element of this model is new law.** Every clause is a citation. This is the
outcome `UCKP-ART-18` requires — locate the canonical object and reuse it — applied to the
question of arbitration itself.

### 12.3 Why class determines identity, and not the reverse

The ordering `Identity → Class → Authority → Owner → …` that BC-6 Step 5 measured as
load-bearing appears to be contradicted here. It is not. Two different questions are being
ordered:

- **For a subject that already has one identity**, identity precedes class: you resolve the
  record, then read its class. That is the pipeline Step 5 measured.
- **For a subject with two identities**, class necessarily precedes selection, because the
  two identities differ precisely in *which authority admitted the subject*, and which
  authority may admit it is a class question by `AIF-L06`.

The dual-identity case is therefore not an exception to the pipeline; it is the case where
the pipeline's first node has two candidate values and the second node is the only thing that
discriminates them. **Arbitration is the repair of the first node using the second, performed
once, after which the normal ordering resumes.**

### 12.4 The model applied to the measured population

| Group | Governing class today | Authority whose predicate holds | Canonical id | Superseded id |
|---|---|---|---|---|
| **A** (25) — corpus-excluded operational memory and intelligence | Not corpus-eligible (`EXCLUDE_DIR_PREFIXES`) | `UCOS-UGA-001` | the **`by_object`** id (`UCOS-EXDOC-*`, `UCOS-DATAOBJ-*`) | the `by_path` corpus id |
| **B** (192) — registered corpus documents | Corpus-registered (`artifacts.json`) | `REG-AUTO-001` / `UMB-IMP-001` | the **`by_path`** corpus id | the `by_object` `UCOS-EXDOC-*` id |

The model selects a **different authority for each group**, which is the result §5.3
requires and no precedence table can produce.

### 12.5 One consequence that must be stated plainly

For Group A, the model marks 25 **corpus** identities superseded. Those 25 identities carry
page ranges in `by_path` and records in `artifacts.json`, and they are `UIS-F-001`'s
grandfathered admissions. Superseding them does not delete them, does not free their page
range, and does not remove their `artifacts.json` record — but it does mean the corpus
registry would hold 25 records whose subjects' canonical identity lives elsewhere.
**That is a corpus-authority decision, not an implementation detail**, and §14.5 routes it
accordingly. It is also exactly the disposition `UIS-F-001` referred to `UMB-003` and left
open; this determination does not close it, it shows what depends on it.

---

## 13. Canonical Identity Selection Rules

Ordered, total, deterministic, fail-closed — the properties
`mutation-governance-boundary.json` `classification_rules.properties` declares for its own
resolution, adopted here rather than re-derived.

```
Given a subject S holding identity set I(S) = { i₁ … iₙ }, n ≥ 1:

CIS-0  PRECONDITION.  Resolve S's governing class C(S) by the declared, ordered
       classification rules.  If C(S) = UNRESOLVED, STOP — no canonical identity is
       selected and none of I(S) is marked.  (AIF-L16: ambiguity fails closed.)

CIS-1  SINGLETON.     If n = 1, that identity is canonical.  No transition is recorded.
       (The 6,196 subjects not in the 217.)

CIS-2  ADMISSION.     Let A(C) be the authority whose declared admission predicate C(S)
       satisfies.  If exactly one iₖ ∈ I(S) was minted by A(C), iₖ is CANONICAL and every
       other member of I(S) is SUPERSEDED-BY iₖ.
       → resolves all 217 measured subjects.

CIS-3  NO-QUALIFIER.  If no iₖ was minted by A(C) — the subject's governing authority never
       minted for it — STOP.  Record UNARBITRATED.  Emit an admission request to A(C).
       Never promote a non-qualifying identity to fill the gap.
       (AIF-L13: mints are provisional until seal; no orphan identity.)

CIS-4  MULTI-QUALIFIER.  If two or more iₖ were minted by the same authority A(C), the
       condition is an intra-authority duplicate — a different and stricter defect than
       URS-2.  STOP.  Record CONTESTED.  Refer to A(C), which is the only party that may
       say which of its own mints was the admission.
       → measured population today: ZERO (0 collisions, 0 intra-map duplicates, §4.2).

CIS-5  IMMUTABILITY.  Once recorded, a CANONICAL selection may be changed only by a new
       recorded transition under AIF-L15, never by re-running CIS-2.  A re-run that would
       produce a different answer is a CONTESTED case, not a silent re-selection.
```

### 13.1 Properties, stated so they can be checked

| Property | How it is satisfied |
|---|---|
| **Deterministic** | `C(S)` is a pure function of the subject and the repository at one commit; `A(C)` is a declared mapping; no clock, no ordering, no caller |
| **Total** | Every subject reaches `CIS-1`, `CIS-2`, `CIS-3` or `CIS-4`. There is no fall-through |
| **Fail-closed** | Three of five outcomes (`CIS-0`, `CIS-3`, `CIS-4`) refuse rather than select |
| **Order-independent** | Nothing in `CIS-0…5` reads `first_seen`, mint order, or map order — which is why `UIA-6`'s incomparable timestamp grammars do not obstruct it |
| **Extensible** | A new authority declares an admission predicate; `A(C)` gains a mapping; `CIS-0…5` are unchanged (§11.2) |
| **Non-destructive** | No rule deletes, edits, renumbers or reissues any identity |

### 13.2 What `CIS-2` requires that does not exist yet

`A(C)` — the mapping from governing class to admitting authority — is **not declared
anywhere today**. It is derivable: `mutation-governance-boundary.json` maps classes to
governing authorities, `EXCLUDE_DIR_PREFIXES` defines corpus eligibility, and
`uga-declaration.json` defines the object boundary. But derivable is not declared, and
`CIS-2` may not depend on a derivation performed by whoever implements it.

**This is the single new declaration the model requires**, and it is the act §14.5 names
first.

---

## 14. Migration Rules

### 14.1 The supersession record

One record per superseded identity, appended to a **new** structure — never into an existing
identity's `history` (§9.1):

```jsonc
{
  "superseded_id":  "UCOS-EXDOC-001457",
  "canonical_id":   "UCOS-MASTER-000015",
  "subject":        "00-MASTER/MCP-001-MASTER-CONTEXT.md",
  "transition":     "supersede",                    // AIF-L15 declared intent
  "reason_class":   "<governing class at arbitration>",
  "reason_rule":    "CIS-2",
  "arbitrated_at_commit": "<sha>",
  "arbitrated_by":  "<the authority named in §14.5>",
  "reversible_by":  "a new AIF-L15 transition, never by re-running CIS-2"
}
```

### 14.2 The seven migration rules

```
MIG-1  APPEND ONLY.  Arbitration writes supersession records and writes nothing else into
       the ledger.  by_path, by_object, by_observation, category_seq, page_cursor and every
       history sequence are byte-unchanged.        (AIF-L17, id_preservation, UIL-06)

MIG-2  NO ORPHANS.  A superseded identity is never left merely unreferenced.  Every identity
       that ceases to be published acquires a supersession record in the same act.
                                                    (AIF-L13 — "abort discards (no orphan identity)")

MIG-3  PUBLISHERS FOLLOW, LEDGER DOES NOT.  Registries and projections re-point to the
       canonical id.  The ledger keeps both entries exactly as recorded.   (AIF-L01)

MIG-4  ARBITRATE BEFORE REFRESH.  No producer run that would change a published identity may
       execute before that subject is arbitrated.  Specifically: `uga_engine.py run` must not
       precede arbitration of Group B, because the run would otherwise perform 192
       unrecorded supersessions as a side effect.        (§6.3, AIF-L15)

MIG-5  ONE GROUP, ONE ACT.  Group A (25, corpus-superseding) and Group B (192,
       UGA-superseding) are arbitrated as two acts with two authorities (§14.5), never as one
       bulk operation, because they supersede identities held by different authorities.

MIG-6  CERTIFICATION IS RECOMPUTED, NEVER AMENDED.  The standing UGA verdict is retained as
       historical attestation; a new current status is computed after arbitration.
                                                    (AIF-L21, AIF-L01, CR-INF-011)

MIG-7  MEASURE BEFORE AND AFTER.  Identity counts per map, collision count, grammar-failure
       count and history-continuity count are recorded before and after and must be
       identical.  Arbitration that changes any of them has malfunctioned.   (CAA-INV-04)
```

### 14.3 What migration explicitly does not do

| Not done | Why |
|---|---|
| Delete a `by_object` or `by_path` entry | `AIF-L17`, `IL-INF-07` |
| Renumber any ordinal | `UIL-06`, `AIF-L04` (ordinals recorded at mint, never recomputed) |
| Free or reallocate a page range | Page allocation is corpus-owned; supersession is not deregistration |
| Remove an `artifacts.json` record | Corpus-authority act, out of scope (§12.5) |
| Merge the two identifiers | `AIF-L03` planes are crosswalked, never merged — and `UIS-001` applies the same rule to schemes |
| Retire the superseded identity | `RETIRED` means *path gone* (`uga-declaration.json`); a superseded identity's subject still exists |

The last row matters: **supersession and retirement are different states.** `URS-5` found
`RETIRED` structurally unemittable; arbitration must not be implemented by reusing it, or the
192 would be recorded as if their subjects had left version control.

### 14.4 Sequence

```
M-0  Declare A(C): the class → admitting-authority mapping (§13.2).        ← the only new declaration
M-1  Record the pre-arbitration measurement set (MIG-7).
M-2  Arbitrate Group B (192) — canonical = corpus id — and record 192 supersessions.
M-3  Run `uga_engine.py run`.  The 192 flip to DOCUMENT_ARTIFACT and publish the corpus id,
     now as the recorded consequence of M-2 rather than as an unrecorded side effect.
M-4  Arbitrate Group A (25) — canonical = object id — and record 25 supersessions.
     Requires the corpus-authority decision in §12.5.
M-5  Recompute UGA's certification (MIG-6); retain the prior attestation.
M-6  Re-measure (MIG-7); assert §16's criteria.
```

`M-2` precedes `M-3` by `MIG-4`. `M-4` is independent of `M-2`/`M-3` and may run in parallel
once its owner decision exists.

### 14.5 Authority required

| Act | Authority | Why this one |
|---|---|---|
| `M-0` declare `A(C)` | **Mutation governance owner** | `A(C)` maps governing class to admitting authority; the class vocabulary and its authority bindings are that owner's register |
| `M-2` supersede 192 UGA ids | **`UCOS-UGA-001`** | An authority may retire its own mint from publication; no other authority's record is touched |
| `M-4` supersede 25 corpus ids | **Corpus authority (`REG-AUTO-001` / `UMB-IMP-001`, via `UMB-003`)** | These are corpus identities with page ranges and `artifacts.json` records; `UIS-F-001` already referred exactly this population to `UMB-003` |
| `M-5` recompute certification | **Certification authority** | `AIF-L21` |

**No single authority can execute this migration.** That is a property of the defect: it was
produced by two authorities acting correctly in isolation, and it can only be closed by both
acting in coordination.

---

## 15. Conflict Resolution Rules

For cases `CIS-0`, `CIS-3` and `CIS-4` — the ones that refuse.

```
CR-1  UNRESOLVED CLASS (CIS-0).  The subject has no governing class, so it has no admitting
      authority, so no identity is canonical.  The subject is recorded UNARBITRATED with its
      full identity set intact and visible.  It is never resolved by picking the older, the
      newer, the more-referenced, or the more-convenient identity.

CR-2  NO QUALIFIER (CIS-3).  The subject's governing authority never minted for it.  Emit an
      admission request to that authority.  Until it is admitted, the subject's existing
      identities remain recorded and none is canonical.  A non-qualifying identity is never
      promoted to fill the gap — that would let a publication convention create an
      admission, which is the mechanism URS-2 was produced by.

CR-3  MULTI-QUALIFIER (CIS-4).  Two mints from one authority for one subject.  Referred to
      that authority alone.  No cross-authority rule applies, because no other authority can
      say which of another's mints was the admission.  (Measured population: zero.)

CR-4  CONTESTED CLASS.  If two classification rules would assign different classes — the
      AAR-1 condition, live for three prefixes — the subject is CONTESTED, not arbitrated.
      Identity arbitration inherits classification's contests; it never resolves one, because
      resolving it here would make identity arbitration a classification authority.

CR-5  NO SILENT RE-SELECTION.  A CIS-2 re-run producing a different canonical id than the
      recorded one is a CONTESTED case requiring a new AIF-L15 transition.  It is never
      applied silently.  (This is what makes arbitration idempotent under Phase 8.)

CR-6  CONFLICTS ARE COMPUTED, NEVER RECORDED AS DISPOSITIONS.  The arbitration record carries
      no exception list and no override field, and must never acquire one — adopting
      category_ownership_resolution's own rule R5 verbatim: "a ledger that described its own
      disagreement with reality would be one edit away from disposing of it."
```

### 15.1 The rule that is deliberately absent

There is **no tiebreaker**. No "if still ambiguous, prefer X." Every refusing path
(`CR-1`…`CR-4`) terminates in a referral to a named authority. This is `AIF-L16`'s *"ambiguity
fails closed"* taken literally, and it is the property that distinguishes this model from the
"last mint wins" rule that would coincidentally produce the right answer today (§5.3) while
encoding process order as identity truth — which `AIF-L20` forbids: *"Identity determinism
(recorded) is never derived from generated determinism."*

---

## 16. Validation Criteria

Arbitration is correctly specified and correctly executed when all of the following hold.
**None holds at this baseline.**

**Specification (before any subject is arbitrated):**

- [ ] `VC-1` · `A(C)` is declared — every governing class maps to exactly one admitting authority; the mapping is total over the class vocabulary and fails closed on `UNRESOLVED`
- [ ] `VC-2` · `CIS-0…5` are implemented as a pure function: same subject, same commit, same answer, no clock, no map order, no `first_seen` read
- [ ] `VC-3` · An invariant exists measuring **"exactly one canonical identity per subject, across all ledger maps"** — the condition `AIF-L07`, `CAA-INV-04` and `UGA-INV-01` jointly do not cover (§4.1–4.3)
- [ ] `VC-4` · `identities_multiple` is re-scoped to quantify over subjects across all maps, or is superseded by `VC-3`'s invariant and declared as measuring something narrower

**Execution (per arbitrated subject):**

- [ ] `VC-5` · Exactly one identity is `CANONICAL`; every other carries a supersession record naming it (`MIG-2` — no orphans)
- [ ] `VC-6` · Zero identities deleted, edited, renumbered or reissued; `by_path`, `by_object`, `by_observation`, `category_seq`, `page_cursor` and every `history` sequence byte-unchanged (`MIG-1`, `MIG-7`)
- [ ] `VC-7` · Identifier collisions, grammar failures and history discontinuities all still measure zero after arbitration (`CAA-INV-04`)
- [ ] `VC-8` · No supersession is recorded as a `RETIRED` lifecycle transition (§14.3)
- [ ] `VC-9` · No published identity changed without a supersession record recorded in the same act (`MIG-4` — specifically, `uga_engine.py run` did not precede `M-2`)

**Closure of the measured population:**

- [ ] `VC-10` · `by_path ∩ by_object` = ∅, **or** every element carries a supersession record naming the surviving id; count 217 → 0 unarbitrated
- [ ] `VC-11` · Group A's 25 arbitrated under a recorded corpus-authority decision (§12.5), not implicitly
- [ ] `VC-12` · A second arbitration pass over the same commit produces byte-identical output (`CR-5`, Phase 8 idempotence)

**Extensibility:**

- [ ] `VC-13` · A synthetic fourth minting authority is admitted with a declared predicate and `CIS-0…5` require no amendment — exercised, not asserted (`UCKP-INV-14`, `IL-INF-06`)

---

## 17. Closure Conditions

| # | Condition | Evidence |
|---|---|---|
| `CC-1` | **The law is enforced, not merely cited** — one subject, one canonical durable identity | `VC-3`, `VC-10` hold; `AIF-L02` measurable for the first time |
| `CC-2` | **The measure is not vacuous** — the condition is quantified over subjects across planes | `VC-4` holds; `identities_multiple` (or its successor) would rise above zero if the condition recurred |
| `CC-3` | **Nothing was destroyed** — every identifier that existed before exists after, unchanged | `VC-6`, `VC-7` hold; `CAA-INV-04` carries every id through verbatim |
| `CC-4` | **No orphans were produced** | `VC-5`, `VC-9` hold |
| `CC-5` | **It cannot silently recur** — a new dual identity fails a gate rather than accruing | `VC-3` is wired blocking; `URS-6`'s absorbing terminal is closed (the minting mechanism) |
| `CC-6` | **It grows** — a fourth authority costs a predicate declaration, not a rule amendment | `VC-13` holds, exercised |

**`CC-5` names the dependency that closes the loop:** arbitration resolves the standing 217,
and `URS-6`'s fail-closed terminal is what stops the 218th from being minted. Arbitration
without that terminal repair is a one-time cleanup of a condition that immediately begins
re-accruing (§5.4). **The two are one repair performed at two layers, and neither alone is
closure.**

### 17.1 Answer to the directive's question

| Question | Answer |
|---|---|
| What is the canonical resolution mechanism for a subject holding multiple Universal IDs? | **`CIS-0…5` (§13):** the canonical identity is the one minted by the authority whose admission predicate the subject's **currently governing class** satisfies. Not the first, not the last, not a ranked authority |
| Is it new law? | **No.** Every clause cites `AIF-L02`, `L06`, `L13`, `L15`, `L16`, `L17`, `L20`, `L21` or `AUTH-INF-001`. The model is enforcement of ratified law |
| What becomes of the other identity? | **Recorded, retained, marked `SUPERSEDED-BY`.** Never deleted, edited, renumbered, reissued, or recorded as `RETIRED` |
| Can it be executed now? | **No.** `A(C)` (§13.2) is underived-and-undeclared, and the act requires three authorities acting in coordination (§14.5) |
| Does it unblock UGA synchronization? | **It specifies `S-4` and `S-5`.** It also adds a constraint that did not exist before: **`S-2` (`uga_engine.py run`) must not precede `M-2`**, or 192 unrecorded supersessions occur as a side effect of a refresh (`MIG-4`) |

---

## 18. Findings Register

| ID | Finding | Severity | Status |
|---|---|---|---|
| `UIA-1` | 217 subjects hold two durable (P2) Universal IDs, in direct non-conformance with `AIF-L02` ("one … identity per artifact"); every other measured identity property holds | **CRITICAL** | **OPEN** |
| `UIA-2` | `identities_multiple` — the published measure named for this condition — quantifies over `artifacts.json` records only and reports `0`; the same vacuity mechanism `mutation-governance-boundary.json` diagnosed in itself | **CRITICAL** | **OPEN** |
| `UIA-3` | The 217 split into two groups with opposite mint orders (25 corpus-first, 192 UGA-first) and opposite causes; no fixed-authority or time-ordered rule is correct for both | **HIGH** | **OPEN** |
| `UIA-4` | Group A's 25 are identically `UIS-F-001`'s 25 `nonsource_identity_admissions` — a registered, bounded, referred finding whose dual-identity consequence was unobserved | **HIGH** | **OPEN** |
| `UIA-5` | `UCOS-UGA-001` mints P2 durable identities into the one ledger under the declared grammar and is absent from the located plane-and-mechanism crosswalk, whose "one scheme per plane" justification therefore does not cover 4,914 of 6,413 entries | **HIGH** | **OPEN** |
| `UIA-6` | The minting authorities record `first_seen` in two incomparable grammars (ISO wall-clock vs `commit:<sha12>`); mint order is not decidable from the ledger alone, and the ISO form is a wall-clock reading in a plane `AIF-L18` requires clock-free | **MEDIUM** | **OPEN** |
| `UIA-7` | Two instruments declare the artifact-plane identity grammar with different patterns; the URN-derivation binding uses the looser. Latent, not active — 0 live violations of either | **MEDIUM** | **OPEN** |
| `UIA-8` | For Group B, the correct canonical id sits in one of 78 mostly-ungoverned category namespaces (`UIS-F-003`), while the superseded id sits in a governed one; arbitration makes `UIS-F-003` load-bearing for 192 more subjects | **MEDIUM** | **OPEN** |
| `UIA-9` | Arbitration re-derives the constitutional-plane URN per subject and invalidates all five UGA certification digests; lawful under `AIF-L03`/`AIF-L21`, but it makes arbitration a certification-affecting act requiring sequenced recomputation | **MEDIUM** | **OPEN** |
| `UIA-10` | The alignment register's own `second_authority_test` was never applied to `by_path` vs `by_object` — the one pair in the repository that fails it | **LOW** | **OPEN** |

**10 raised · 0 resolved.**

### 18.1 Disposition of prior findings

| Prior | This determination |
|---|---|
| `URS-2` (217 dual identities) | **SPECIFIED, NOT RESOLVED.** Mechanism identified (`UIA-3`), law located (`UIA-1`), model derived (§12–§15). Zero subjects arbitrated |
| `URS-6` (absorbing terminal) | **CONFIRMED AS THE MINTING MECHANISM** and promoted to a closure dependency (`CC-5`): arbitration without it is cleanup of a re-accruing condition |
| `URS-3` (stale certification) | **EXTENDED**: arbitration invalidates the five digests independently of staleness (`UIA-9`) |
| `URS-5` (`RETIRED` unemittable) | **BOUNDED**: supersession must not be implemented by reusing `RETIRED` (§14.3), so `URS-5` is not on arbitration's critical path |
| `UIS-F-001` (25 nonsource admissions) | **EXTENDED**: identically Group A; its unresolved `UMB-003` referral is now a prerequisite of `M-4` (`UIA-4`) |
| `UIS-F-003` (74 ungoverned namespaces) | **EXTENDED**: load-bearing for 192 more subjects after arbitration (`UIA-8`) |
| `CIR-3` / `ACD-1` (CAAR's third identity authority) | **REINFORCED**: CAAR's identity rule `I-2` presumes one id per subject; §13 supplies the rule that makes `I-2` total |
| `AV-6` / `R-01` (absorption before resolution) | **THIRD OCCURRENCE** of the pattern — `R-01`, UGA's terminal, and now the vacuous quantification in `UIA-2` |

---

## 19. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-DETERMINATION.md` |
| Line count | ✅ **1036** |
| Required sections — the ten analyses | ✅ §2 authorities · §3 precedence · §4 subject-to-identity · §5 duplicate claims · §6 migration strategy · §7 historical preservation · §8 universal object compatibility · §9 registry impact · §10 certification impact · §11 infinite expansion |
| Required sections — identity arbitration model | ✅ §12 (statement, law derivation, applied to the measured population) |
| Required sections — canonical identity selection rules | ✅ §13 (`CIS-0`…`CIS-5`, properties, the one missing declaration) |
| Required sections — migration rules | ✅ §14 (`MIG-1`…`MIG-7`, sequence, authority routing) |
| Required sections — conflict resolution rules | ✅ §15 (`CR-1`…`CR-6`, and the deliberately absent tiebreaker) |
| Required sections — validation criteria | ✅ §16 (`VC-1`…`VC-13`) |
| Required sections — closure conditions | ✅ §17 (`CC-1`…`CC-6` + answer to the directive's question) |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Analysis only — arbitration performed | ✅ **0** subjects arbitrated |
| Identity changes | ✅ **0** — `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7, before and after; `category_seq` and `page_cursor` untouched |
| Identities minted / retired / superseded / renumbered | ✅ **0 / 0 / 0 / 0** |
| Code changes | ✅ **0** — `uis_engine.py`, `uga_engine.py`, `uga_projection.py`, `config.py` read, none written |
| Registry changes | ✅ **0** — ledger, `artifacts.json`, GAR, UGA surfaces, UIS surfaces read, none written |
| Certification changes | ✅ **0** |
| Commits | ✅ **0** |
| Tracked modifications unchanged | ✅ **38** — identical set to session start |
| Only one new artifact | ✅ the single delta is this file |
| Findings resolved | ✅ **0** — 10 raised |

### 19.1 Measurement provenance

```
id-ledger by_path / by_object / by_observation       1,492 / 4,914 / 7   (unchanged)
  at HEAD                                            1,264 / 4,914 / 7
by_path ∩ by_object   worktree / HEAD                217 / 25
  mint order: corpus first / UGA first               25 / 192
  UGA mint commits spanning the 217                  8   (2026-08-12 … 2026-08-21)
  by_path first_seen form                            ISO wall-clock, 217 of 217
  by_object first_seen form                          commit:<sha12>, 217 of 217
Group A (25) location                                00-MASTER/ 13 · intelligence/ 11 · root pointer 1
  == config.EXCLUDE_DIR_PREFIXES coverage            yes
  == UIS-001 nonsource_identity_admissions           25 = 25
by_path categories among the 217                     78 distinct (PHASEU 17, MASTER 13, H06IMP 13, …)
by_object categories among the 217                   2 distinct (EXDOC 201, DATAOBJ 16)
registry publishes by_object id for                  217 of 217
UIS-001 identities_multiple (published)              0        (scoped to artifacts.json records)
UIS-001 identity_collisions / renumbered / reused    0 / 0 / 0
UIS-001 identities_failing_declared_grammar          0
UIS-001 registry_identities_absent_from_ledger       0
AIF laws (AIF-L01…L24) / bearing on this question    24 / 9, of which 6 settle it
declared artifact-plane grammars                     2 (differing)
git status: modified / untracked / total             38 / 311 / 349
this artifact, lines                                 1036
```

---

*This determination minted no identity, retired none, superseded none, renumbered none, and
arbitrated no subject — `by_path` stands at 1,492, `by_object` at 4,914 and `by_observation`
at 7, before and after. It answers `URS-2`'s open question with a model that is entirely
citation: `AIF-L02` fixes the cardinality at one identity per artifact, `AIF-L06` makes the
admitting authority part of the key, `AIF-L15` supplies `supersede` as a ratified transition,
`AIF-L16` requires the decision be algorithmic and fail closed, and `AIF-L17` forbids
destroying what is superseded. The measured population divides into two groups with opposite
mint orders — 25 corpus-first paths that the exclusion boundary later excluded, and 192
documents UGA absorbed before the corpus registered them — which is why no precedence table
and no first-mint rule resolves both, and why the canonical identity must be the one whose
authority's admission predicate the subject satisfies **now**. The condition is not merely
unresolved but unmeasured: the one published metric named for it quantifies over a single
register and reports zero. Ten findings (`UIA-1`…`UIA-10`) are raised; none is resolved.
Execution requires one new declaration and three coordinating authorities, and one ordering
constraint is added to the UGA synchronization strategy: `uga_engine.py run` must not precede
arbitration of Group B, or 192 unrecorded supersessions occur as the side effect of a
refresh. The single repository mutation is the creation of this file.*

**END DETERMINATION — IDENTITY ARBITRATION MODEL SPECIFIED · NOT ADOPTED · ZERO SUBJECTS ARBITRATED · STOPPED AFTER ARTIFACT CREATION.**

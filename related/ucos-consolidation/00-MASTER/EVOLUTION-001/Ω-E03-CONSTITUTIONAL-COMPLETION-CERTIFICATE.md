# Ω-E03 — CONSTITUTIONAL COMPLETION CERTIFICATE

| Field | Value |
|---|---|
| WAVE | `Ω-E03` — Universal Constitutional Identity |
| AUTHORITY | **NONE — DERIVED TRUTH.** This certificate legislates nothing, ratifies nothing, certifies nothing and confers nothing. It records what the repository already measured and what an independent re-execution of that measurement observed. Where this certificate and a located instrument differ, **the located instrument governs**. |
| LOCATED EXIT RECORD | `02-CANONICAL-OWNERSHIP-MATRIX.md` §2 addendum (2026-08-02, `Ω-E03`) — the canonical, append-only wave exit record. This certificate **restates and independently verifies** it; it does not replace it and creates no second exit authority. |
| WAVE HOME | `00-MASTER/UIS-001/` |
| REPOSITORY ANCHOR | the commit carrying this record (RFP-2 — never restated here) |
| WORKING TREE AT CERTIFICATION | CLEAN (0 entries) |
| PROGRAMME SEAL | `a05f279d99b26e5d…` — moved from `cd753fa12a6b7ec8…` by the `OBL-E04-01` discharge, which a strengthened measurement must do |
| DETERMINATION | `IDENTITY-CONFORMANCE-BOUND` · gate `OPEN` |
| VERDICT | **Ω-E03 CONSTITUTIONALLY COMPLETE — `OBL-E04-01` DISCHARGED** |
| CERTIFICATE DATE | 2026-08-02 |

> **Provenance of this record.** A first issue of this certificate (unpublished) recorded
> `OBL-E04-01` as an **open** measurement defect and authorized Ω-E04 conditionally. Repository
> Truth then required the defect be discharged before Ω-E03 could close. It was. This issue is the
> permanent record, and §16 preserves the defect, its proof and its discharge rather than erasing
> them — a certificate that hid its own correction would be the defect it reports.

---

## 1. Repository Truth Determination

Ω-E03 was located before it was described. The determination rests on artifacts, not on the prompt
that produced them.

| Reading | Value | Located at |
|---|---|---|
| Wave commits | owned by version control, never restated here (RFP-2). The wave opens at `6ad60f6` "bind the identity architecture to its located owners" and closes at the last `Ω-E03` commit reachable from this record; `git log --grep='Ω-E03'` is the located enumeration. | `git log` |
| Wave home | `00-MASTER/UIS-001/` — 13 files: declaration, engine, model, 8 rendered registers | filesystem |
| Declaration | `uis-declaration.json` — 5 planes, 6 mechanisms, 20 laws, 19 bookkeeping obligations, 54 capabilities, 24 validations, 8 exit criteria, 6 findings. **Unchanged by the discharge.** | `00-MASTER/UIS-001/uis-declaration.json` |
| Engine | `uis_engine.py` — the only file the discharge amended | `00-MASTER/UIS-001/uis_engine.py` |
| Model | `uis.json` — derived, 42 counters (41 + `bookkeeping_fields_unresolved`) | `00-MASTER/UIS-001/uis.json` |
| Ownership rows added | 6 identity rows + 1 addendum; the matrix previously contained **zero** occurrences of the word *identity* | `02-CANONICAL-OWNERSHIP-MATRIX.md` |
| Aggregate gate | `G-24` "Identity Conformance Gate" → checks `CK-UIS`, `CK-UIS-SELF` | `00-MASTER/UCCEP-000000/uccep-bindings.json` |
| CI | `.github/workflows/uis-gate.yml` — 9 self-guards + gate + replay, exit 0/1/2 | `.github/workflows/uis-gate.yml` |
| Fixed-point stage | `STAGE-UIS`, `required: true`, `reentrant: true`, write zone `00-MASTER/UIS-001/` | `00-MASTER/UCOS-RFP-001/rfp-declaration.json` |
| Make targets | `uis`, `uis-gate`, `uis-self`, `uis-replay` | `Makefile` |
| New analyses registered | `UAR-UIS-01…07` (7) | `00-MASTER/UCOS-UAR-001/uar-analyses.json` |

**Determination.** Ω-E03 is a *measurement* wave over an identity architecture that already existed.
It introduced no identity authority and no corpus identity: the programme is classified SUBSTANTIVE,
is absent from `00-CMG/CMG-REGISTRY.json` by design under Art LXXVI.2(b), and consumes no permanent
corpus identity at all.

---

## 2. Constitutional Objective

To make the identity architecture the repository had already legislated **executable rather than
prose**, without creating a second identity authority.

The pre-wave condition, measured rather than asserted:

- `ENG-001` D5 declared **twenty Universal Identity Laws** as binding invariants whose violation it
  calls a failure condition — and **nothing checked one of them**.
- `AIF` Part III A/G-AUTH legislated **exactly one identity authority** — and nothing verified it.
- **Four identifier schemes** existed across the five declared identity planes — with no crosswalk.
- `AUTH-INF-001` asserted **unbounded lawful expansion** in seven directions — never probed.
- `02-CANONICAL-OWNERSHIP-MATRIX.md` held **zero identity rows** for seven identity authorities.

The objective was therefore not to build identity. It was to measure it, and to prove the
measurement cannot become what it measures.

---

## 3. Canonical Owners

Located, not created. None was moved, split, merged or restated — by the wave or by the discharge.

| Concern | Canonical owner | Ω-E03 disposition |
|---|---|---|
| Law of identity — planes, admission, federation, continuity | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` (`AIF`) — Part II AIF-L01…L24, AIF-L03 five planes, Part III A/G-AUTH | REUSE |
| Identity engineering architecture — theory, laws, ontology, meta-model | `07-ENGINEERING/UCOS-Ω∞-UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE.md` (`ENG-001`) — D3 UIS-P-01…24, D5 UIL-01…20, D10–D15, D30 | REUSE |
| Identity realization — allocator, ledger, facet set, addressability | `00-BOOK/MASTER-BOOK/UMB-003-IDENTITY-ARCHITECTURE.md` | REUSE |
| Nomenclature, namespace admission, native-ID crosswalk | `00-BOOK/MASTER-BOOK/UMB-004-NOMENCLATURE-ARCHITECTURE.md` | REUSE + EXTEND (measurement) |
| Registry, change, version, lineage realization | `UMB-005` / `UMB-008` / `UMB-009` / `UMB-010` | REUSE |
| Unbounded lawful expansion | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-AUTH-INF-001…CONSTITUTION.md` — `CR-INF-001…012`, `IL-INF-01…06` | REUSE + EXTEND (probe) |
| Closed facet set (33 members) | `engine/uckp/facets.py` | REUSE |
| Artifact grammar and bookkeeping schema | `00-BOOK/SCHEMAS/artifact.schema.json` | REUSE |
| Recorded identity plane | `00-BOOK/DATA/id-ledger.json` | REUSE (read-only) |
| Derived identity plane | `00-BOOK/DATA/artifacts.json` | REUSE (read-only) |
| Identity conformance **measurement** | `00-MASTER/UIS-001/` — `AUTHORITY = NONE — DERIVED TRUTH` | EXTEND (this wave) |

The single-authority obligation is **verified, not assumed**: 7/7 obligated architectures declare in
their own text that they realize the one identity authority (`realization_obligations_unmet = 0`).

---

## 4. Existing Capabilities Reused

**48 of 54** capabilities were dispositioned `REUSE`. The measurement reached them semantically — by
constitutional responsibility, not by identifier — across seven groups plus interoperability and
unboundedness. Every one resolved to a located owner, which made `CREATE` unavailable under
`00-CMG/CMG-000001` Art LXXVII.2(a) and LXXVII.4.

| Group | Reused capability → located owner (abridged) |
|---|---|
| IDENTITY | Universal Identifier → `AIF`; Canonical Identifier → `UMB-003`; Object Identifier → `engine/uckp/ucko.py`; Artifact Identifier → `artifact.schema.json`; Knowledge Identifier → `engine/knowledge/ukip/registry.py`; Runtime Identifier → `engine/context/registry.py` |
| DICTIONARY | Dictionary, Vocabulary → `engine/uckp/vocabulary.py`; Lexicon → `engine/context/ontology.py`; Symbol Table → `engine/registry/universal/identity.py`; Semantic Registry → `engine/uckp/registry.py`; Grammar → `artifact.schema.json`; Code Dictionary → `00-BOOK/tools/config.py` |
| REGISTRATION | Registry → `UMB-005`; Registration → `00-BOOK/tools/register.sh`; Catalog → `engine/context/catalog.py`; Directory, Inventory → `00-BOOK/REGISTRIES/…`; Ledger → `00-BOOK/DATA/id-ledger.json`; Manifest → `CHANGE-VERSION-LINEAGE-REGISTRY.md`; Bookkeeping → `artifact.schema.json` |
| RESOLUTION | Resolver → `engine/context/resolution.py`; Lookup, Allocation → `00-BOOK/tools/ukb.py`; Discovery → `engine/discovery/engine.py`; Addressability, Dereferencing → `UMB-003` |
| LINEAGE | Parent, Child, Ancestor, Descendant → `UMB-010`; Successor → `UMB-009`; Supersession, Evolution → `CEP-009`; Provenance → `engine/knowledge/ukip/provenance.py` |
| LIFECYCLE | Activation, Retirement, Archive → `UMB-003`; Certification → `CERTIFICATION-REGISTRY.md` |
| CONTEXT | Temporal, Spatial, Reality, Existence, Observer, Governance, Security → `engine/context/taxonomy.py` |
| UNBOUNDEDNESS | Unlimited lawful semantic evolution → `AUTH-INF-001`; unlimited lawful contextual dimensions → `engine/context/taxonomy.py` |

---

## 5. Existing Capabilities Extended

**6 of 54** capabilities were dispositioned `EXTEND` — in every case the extension is a *measurement
over the located owner*, in the operational-memory lane, holding no authority.

| Capability | Owner extended | What the extension is |
|---|---|---|
| Namespace Registry | `UMB-004` | measures which live category namespaces are governed by a declared classification rule |
| Identity plane crosswalk | `UMB-004` | crosswalks the located identifier schemes onto the 5 declared planes — mapped, never merged |
| Single identity authority | `AIF` | verifies the A/G-AUTH obligation against each obligated architecture's own text |
| Identity law conformance | `ENG-001` | binds 20/20 laws to their owner and measures the 19 the located data can decide |
| Unlimited lawful identity/family/namespace/object-class expansion | `AUTH-INF-001` | probes 9 declared directions against a located extension path |
| Constitutional self-description of identity | `UMB-003` | measures self-description **by resolution** rather than by parsing |

Total: **48 REUSE + 6 EXTEND + 0 CREATE = 54**, verified by re-execution after the discharge
(`capabilities = 54(0create)`, `capabilities_created = 0`, `capabilities_unowned = 0`).

---

## 6. Capabilities Refused

Nine self-challenges were run against standing up a new identity programme; all nine failed to
justify one. The refusals are recorded per-capability in
`08-ADMISSION-AND-DISPOSITION-DETERMINATION.md` (`Refusal recorded = YES` on all 54 rows).

| Refused | Grounds |
|---|---|
| A `UCID` (new universal constitutional identifier) | `AIF-L02`/`L03` and `UMB-003` §2 already own the identifier; a fifth scheme would amend four owners |
| A `UCIDD` (new constitutional identity dictionary) | `ENG-001` D11 already owns Dictionary; `engine/uckp/vocabulary.py` realizes it |
| A `UCIR` (new constitutional identity registry) | `ENG-001` D10 + `UMB-005` already own Registry; a sixth registry is forbidden |
| A new identity **authority** | the law declares **exactly one**, and 7/7 obligated architectures declare they realize it |
| A new identity **registry** | the located registry family already governs registration |
| A new identity **namespace** | `UMB-004` admits namespaces append-only from data; zero hard-coding |
| A new identity **lifecycle** | `UMB-003` already binds the lifecycle to its status field; `lifecycle_states_undeclared = 0` |
| A new identity **resolver** / address space | `UMB-003` §5 forecloses both **by name**: *"no new resolver or address space is created"* |
| A new **identifier family** | one grammar per declared plane already exists; planes are orthogonal and non-substitutable (`AIF-L03`) |
| A new **bookkeeping mechanism** | bookkeeping is already bound twice — `artifact.schema.json` and the closed 33-member facet set |

The refusals are held mechanically, not by intention: `--check-no-identity-minting` fails closed if
any emitted byte carries an identifier satisfying the located grammar that the ledger does not
already record, so this programme cannot silently become a fifth scheme. **The `OBL-E04-01`
discharge refused a new mechanism too:** the field binding was strengthened by *reading* the located
sources' own key space, not by declaring a schema, a field registry or a second bookkeeping model.

---

## 7. Measurable Gaps Found

**The single measurable gap was that none of the identity architecture was measured.** Decomposed:

| Gap | Evidence of absence | Class |
|---|---|---|
| `GAP-E03-1` | 20 identity laws declared binding invariants; 0 checked | UNMEASURED LAW |
| `GAP-E03-2` | "exactly one identity authority" legislated; 0 architectures verified | UNVERIFIED OBLIGATION |
| `GAP-E03-3` | 4 identifier schemes over 5 planes; no crosswalk read | UNREAD CROSSWALK |
| `GAP-E03-4` | 7 directions of unbounded expansion asserted; 0 probed | UNPROBED ASSERTION |
| `GAP-E03-5` | 19 bookkeeping obligations implied; no closed-facet binding measured | UNBOUND OBLIGATION |
| `GAP-E03-6` | `02-CANONICAL-OWNERSHIP-MATRIX.md` — 0 identity rows for 7 identity authorities | MISSING OWNERSHIP ROW |
| `GAP-E03-7` | no gate, no CI, no fixed-point stage for identity conformance | UNGATED CONCERN |
| `GAP-E03-8` | **found during exit certification** — `UIS-V-10` measured the containing owner, not the declared field, so `GAP-E03-5` was only half closed | UNMEASURED DIMENSION |

No gap was a *missing capability*. That is why the `CREATE` count is 0 and must be 0: every identity
capability already had a located owner.

---

## 8. Gaps Implemented

All eight, as measurement in the operational-memory lane.

| Gap | Closed by | Re-executed reading |
|---|---|---|
| `GAP-E03-1` | 20 laws bound to owner; 19 measured over recorded ledger + derived registry | `laws = 20/20 bound, 19 measured`; `laws_unbound = 0`; `laws_violated = 0` |
| `GAP-E03-2` | each obligated architecture's own text searched for the realization tokens | `authority = 7/7`; `realization_obligations_unmet = 0` |
| `GAP-E03-3` | 6 located mechanisms classified into exactly one of 5 planes, each plane realized | `planes = 5/5`; `mechanisms = 6`; `mechanisms_unclassified = 0`; `mechanisms_unresolved = 0` |
| `GAP-E03-4` | 9 directions probed against a located module **and** symbol | `unbounded = 9/9`; `extension_probes_unresolved = 0`; `unboundedness_violations = 0` |
| `GAP-E03-5` | 19 obligations bound to a located source, a **resolved field** and a member of the closed 33-facet set | `bookkeeping = 19/19`; `bookkeeping_unbound = 0`; `bookkeeping_facets_unknown = 0` |
| `GAP-E03-6` | 6 identity rows + `Ω-E03` addendum appended | `02-CANONICAL-OWNERSHIP-MATRIX.md` §2 |
| `GAP-E03-7` | `make uis-gate` · `G-24` (`CK-UIS`, `CK-UIS-SELF`) · CI workflow · `STAGE-UIS` | `G-24` **PASS**; `STAGE-UIS` required in the 33-stage pipeline |
| `GAP-E03-8` | `measure_bookkeeping` now requires the located source to **carry the declared field**; scope recorded; `bookkeeping_fields_unresolved` isolates the field half | `bookkeeping_fields_unresolved = 0`; 13 `ENTRY`, 1 `DOCUMENT`, 5 `MEMBER` |

### The `OBL-E04-01` discharge, precisely

The declared dimension read *"every bookkeeping obligation binds to a located **field** of a located
source"*, but `measure_bookkeeping` computed `bound` solely from `(REPO / owner).is_file()`. Both
branches of its `plane == "artifact"` conditional were byte-identical — an intended distinction never
implemented. The `field` was rendered into the register and never checked.

**Only the proof was corrected.** Identity, bookkeeping, canonical ownership and Repository Truth are
untouched; no declaration datum, law, plane, capability, disposition, bound or dimension count
changed. An obligation now binds only when the located source itself carries the declared field, at
the two depths the located sources actually use:

| Plane | Resolution | Obligations | Example |
|---|---|---|---|
| artifact | `ENTRY` — a key of a recorded entry | 13 | `universal_id`, `first_seen`, `content_hash` |
| artifact | `DOCUMENT` — a key of the record as a whole | 1 | `history` (1 225 entries, ledger top level) |
| code | `MEMBER` — a member of the located closed facet set | 5 | `authority`, `validation`, `verification`, `certification`, `context` |
| code | `SYMBOL` — a definition in the located module | 0 (available) | — |
| any | `FIELD-ABSENT` / `OWNER-ABSENT` | 0 | a failure of the binding, not a note |

Zero Enumeration is preserved: the key space is **read** from whatever the located source contains,
so no field name, path or namespace is hard-coded and adding a field or an obligation still requires
no change to the module. `--check-no-enumeration` PASS.

Additional measured position: 1 225 recorded identities, 1 225 recorded histories, 1 194 registered
identities, 94 live namespaces, 43 declared namespaces, namespace width 6, formatting capacity
1 000 000 per namespace, 24/24 blocking dimensions satisfied.

---

## 9. Gaps Intentionally Left to Canonical Owners

Six standing divergences are **bounded, disclosed and referred** — never repaired. Repairing any of
them would commit the defect the programme reports: `UIL-13` and `AIF-L17` forbid erasing or editing
a recorded identity, and `UIL-06` forbids renumbering one.

| Finding | Class | Measured | Bound | Referred to | Why not repaired |
|---|---|---|---|---|---|
| `UIS-F-001` | STANDING-LEDGER-DIVERGENCE | `nonsource_identity_admissions = 25` | `<= 25` (tight) | `UMB-003` | legacy admissions grandfathered by AIF A/G7 with frozen ordinals; deletion **is** the defect |
| `UIS-F-002` | STANDING-RESOLUTION-DIVERGENCE | `identities_unresolvable = 6` | declared | `UMB-003` | the RECORDED plane; an identity outlives its artifact by design |
| `UIS-F-003` | MEASURED-GOVERNANCE-GAP | `namespaces_ungoverned = 66` of 94 live | `<= 66` (tight) | `UMB-004` | namespaces minted by the allocator's filename fallback; only the nomenclature owner may declare a rule |
| `UIS-F-004` | DISCLOSED-PINNED-PARAMETER-DIVERGENCE | `namespace_partition_ambiguities = 17` | declared | pinned-parameter owner, `AIF-L24` | the derivation width narrowed below the width some records were minted under; renumbering is forbidden |
| `UIS-F-005` | MEASURED-COVERAGE-BOUNDARY | 1 law `DECLARED-NOT-MEASURABLE` (reflexivity, `UIL-11`) | governed | `ENG-001` | not decidable from artifact-plane data; reported as such rather than passing silently |
| `UIS-F-006` | DISCLOSED-CONSTITUTIONAL-READING | self-description measured by resolution | governed | `UMB-003` | a parseable identifier would contradict `AIF-L02` opacity and `ENG-001` UIS-P-06 |

None is blocking. Every bound is **tight**: `bounds_slack = 0`, so no disclosed divergence is
inflated to hide a regression inside its slack. The discharge strengthened `UIS-F-006`'s reading:
self-description by resolution now requires each obligation's field to resolve, not merely its
containing source.

---

## 10. Validation Evidence

Re-executed after the discharge on a clean tree. `make uis-gate` → **exit 0**.

```
UIS-001: IDENTITY-CONFORMANCE-BOUND | identities=1225rec/1194reg | planes=5/5 |
mechanisms=6 | authority=7/7 | laws=20/20bound,19measured | capabilities=54(0create) |
bookkeeping=19/19 | unbounded=9/9 | namespaces=94live/66ungoverned | criteria=24/24 |
immutable=true | gate=OPEN | seal=a05f279d99b26e5d
```

All **24 blocking dimensions PASS** (`UIS-V-01…24`), `blocking_failures = []`. Load-bearing counters:

| Counter | Value | Counter | Value |
|---|---|---|---|
| `capabilities_created` | 0 | `capabilities_unowned` | 0 |
| `capability_artifacts_unresolved` | 0 | `realization_obligations_unmet` | 0 |
| `mechanisms_unclassified` | 0 | `mechanisms_unresolved` | 0 |
| `planes_unrealized` | 0 | `laws_unbound` | 0 |
| `laws_violated` | 0 | `bookkeeping_unbound` | 0 |
| **`bookkeeping_fields_unresolved`** | **0** *(new — the field half, isolated)* | `bookkeeping_facets_unknown` | 0 |
| `registry_identities_absent_from_ledger` | 0 | `identity_collisions` | 0 |
| `identities_renumbered` | 0 | `identities_reused` | 0 |
| `identities_altered` | 0 | `identities_multiple` | 0 |
| `identities_absent` | 0 | `history_not_append_only` | 0 |
| `identities_failing_declared_grammar` | 0 | `identities_attribute_coupled` | 0 |
| `identity_records_with_secret_field` | 0 | `identity_records_claiming_authority` | 0 |
| `lifecycle_states_undeclared` | 0 | `namespaces_near_capacity` | 0 |
| `terminal_state_claims` | 0 | `unboundedness_violations` | 0 |
| `extension_probes_unresolved` | 0 | `bounds_slack` | 0 |
| `self_description_unbound` | 0 | `writes_outside_home` | 0 |
| `record_write_intersections` | 0 | `authority_claims` | 0 |
| `identity_minting_attempts` | 0 (literal — §16 `VER-02`) | | |

Record immutability: write set = 10 paths, located record set = 7 paths, intersection **0**, writes
outside home **0**, forbidden-prefix trespass **0**, `disjoint = YES`. All 7 protected records
(`REC-LEDGER`, `REC-REGISTRY`, `REC-CHANGE`, `REC-AIF`, `REC-ENG001`, `REC-UMB003`, `REC-UMB004`) are
located with their anchors still present in their owners' own text.

---

## 11. Verification Evidence

A gate that passes proves only one direction. Verification therefore required **negative controls**:
a blocking dimension that cannot be driven closed is not a measurement.

**Self-guards.** `make uis-self` → **9/9 PASS**: `check-declaration`, `check-no-enumeration`,
`check-write-scope`, `check-determinism`, `check-knowledge-once`, `check-record-immutability`,
`check-no-identity-minting`, `check-bounds-tight`, `check-no-authority`.

**Mutation matrix, post-discharge: 30 valid controls, 30 killed, 0 survived.** Each mutation was
applied to the declaration, the gate run, and the declaration restored byte-exact from an in-memory
backup (never from git, so the strengthening under test could not be silently reverted).

*`OBL-E04-01` discharge proof — `UIS-V-10` is now falsifiable at every resolution depth:*

| Control | Gate exit | Verdict |
|---|---|---|
| every declared field replaced by a nonexistent field | 1 | KILLED |
| ONE artifact `ENTRY` field made nonexistent | 1 | KILLED |
| ONE artifact `DOCUMENT` field made nonexistent | 1 | KILLED |
| ONE code-plane `MEMBER` field made nonexistent | 1 | KILLED |
| a field of the **other** located source substituted | 1 | KILLED |
| a code-plane member substituted for an artifact field | 1 | KILLED |
| a real field in the wrong case | 1 | KILLED |
| a proper prefix of a real field | 1 | KILLED |
| the containing owner itself no longer resolves | 2 | KILLED (fail-closed) |

*Non-regression — every control that killed the gate before the discharge still kills it:*

| Dimension | Controls | Result |
|---|---|---|
| `UIS-V-01`, `V-02`, `V-03` | owner unresolved · `CREATE` · artifact unresolved | 3/3 KILLED |
| `UIS-V-04`, `V-05` | unqualified architecture obliged · mechanism in undeclared plane | 2/2 KILLED |
| `UIS-V-06`, `V-07` | mechanism module · symbol · unrealized plane | 3/3 KILLED |
| `UIS-V-08`, `V-09` | law source unresolved · measurable law falsified | 2/2 KILLED |
| `UIS-V-11`, `V-12` | facet outside closed set · both plane sources | 3/3 KILLED |
| `UIS-V-13`, `V-14`, `V-18` | bounds tightened ×2 · bounds slackened ×2 | 4/4 KILLED |
| `UIS-V-16`, `V-17` | home declared forbidden · record inside write set | 2/2 KILLED |
| `UIS-V-22` | extension module · extension symbol | 2/2 KILLED |

Dimensions falsified by a killed control: **18 of 24** (`V-01`…`V-14`, `V-16`, `V-17`, `V-18`,
`V-22`). Not probed by this harness: **6** — `UIS-V-15`, `V-19`, `V-20`, `V-21`, `V-23`, `V-24`.
Their non-vacuity is **asserted by the wave record and not independently confirmed here**, and is
recorded as advisory rather than claimed.

The declaration was verified byte-exact and the working tree byte-clean after the harness.

---

## 12. Certification Evidence

| Instrument | Reading |
|---|---|
| `07-CERTIFICATION-REPORT.md` | determination `IDENTITY-CONFORMANCE-BOUND`, gate `OPEN`, seal `a05f279d…` |
| Exit criteria | `UIS-EX-01…08` declared. **`UIS-EX-06` is now measured** — "universal bookkeeping is a measured property: every obligation binds to a located field and a member of the closed facet set" is the statement the discharge made true of the proof as well as of the fact. The remaining criteria are carried collectively by the 24 blocking dimensions; `uis.json` records statements without a per-criterion satisfaction field. |
| Findings | 6 registered — 4 `REGISTERED`, 2 `GOVERNED`, **0 blocking**, 0 decided |
| Aggregate gate | `G-24` "Identity Conformance Gate" → `CK-UIS`, `CK-UIS-SELF` → **PASS** |
| Aggregate certification | `UCCEP-000000` at canonical tier `full`: `CERTIFIED-PROVISIONAL`, **gates 24/24 PASS**, **programmes 19/19 PASS**, `blocking=none`, `unproven=none`, seal `ca18947d4ee6a25a` |
| Repository blueprint | `UCOS-RIB-001` measured on a **clean** tree: `BLUEPRINT CERTIFIED — REPOSITORY MAY PROCEED`, units 238, gates 12/12, `dirty=0`, seal `d9825675ca382200` |
| Repository verification | `verify.sh` **PASSED** — ruff lint + format-check, pytest with `--cov-fail-under=90`, coverage report, governance enforce `--pre` (1 194/1 194 registered, 0 unregistered, 0 unclassified), registry validate (append-only page ledger intact, referential integrity OK) |
| New analyses | `UAR-UIS-01…07` registered at `00-MASTER/UCOS-UAR-001/uar-analyses.json` |
| Knowledge closure | `UAKOS-CLOSURE-002`: **CLOSED**, concepts 447, gaps 0 across all 7 gap classes |
| CI enforcement | `.github/workflows/uis-gate.yml` on every push and pull request, fail-closed (0/1/2) |
| Corpus identity consumed | **none** — operational memory, absent from `00-CMG/CMG-REGISTRY.json` by design |

Standing disclosure preserved: `CERTIFIED-PROVISIONAL`, Tier T1 VACANT (`VAC-01` / `CMG-OQ-02`).
This certificate does not upgrade that standing and cannot.

---

## 13. Replay Evidence

The registers are DERIVED TRUTH (`AIF AX-01`): they must be a pure function of the declaration and
the located sources, or the committed bytes are evidence of nothing.

```
$ make uis            # regenerate → wrote 10 artifacts to 00-MASTER/UIS-001
$ make uis-replay     # UIS-001 replay: no drift
$ git status --porcelain   # (empty)
```

- Full render followed by `git diff --exit-code -- 00-MASTER/UIS-001`: **no drift**.
- Seal reproduced identically across runs: `a05f279d99b26e5d…`.
- `--check-determinism` PASS: byte-identical rendering, no wall-clock, no commit identity in output.
- Replay is enforced in CI, not only locally.
- During the discharge, replay correctly reported **DRIFT** while the strengthened registers were
  uncommitted, and returned to **no drift** once the committed bytes matched the derivation. The
  guard was observed doing its job in both directions.

---

## 14. Fixed Point Evidence

`make rfp-gate` → **exit 0** on the committed tree after convergence.

```
UCOS-RFP-001: REPOSITORY IS A FIXED POINT | passes=3 | stages=33 | criteria=13/13 |
cycles=0 | gate=OPEN
```

| Criterion | Reading |
|---|---|
| `CLO-01` tree clean before assertion | `initial_dirty_entries = 0` |
| `CLO-02` every required stage exits successfully | `stage_failures = 0` |
| `CLO-03` no tracked file modified by any pass | `tracked_modifications = 0` |
| `CLO-04` no file staged by any pass | `staged_entries = 0` |
| `CLO-05` no untracked entry outside an excluded location | `untracked_outside_excluded = 0` |
| `CLO-06` byte-identical after every declared pass | `non_fixed_point_passes = 0` |
| `CLO-07` no self-reference cycle | `cycles_detected = 0` |
| `CLO-08` all residue attributable to a declared producer | `unattributed_paths = 0` |
| `CLO-09` every discovered producer is a declared stage | `undeclared_producers = 0` |
| `CLO-10` every producer write inside a declared zone | `producer_writes_outside_zones = 0` |
| `CLO-11` write zones pairwise disjoint | `overlapping_write_zones = 0` |
| `CLO-12` no producer candidate left unprobed | `unprobed_producer_candidates = 0` |
| `CLO-13` no stage writes into another stage's zone | `cross_zone_writes = 0` |

Passes 1/3, 2/3, 3/3: `modified=0 staged=0 untracked=0`.

### Convergence record

A strengthened measurement moves its seal, and derived consumers must catch up. Convergence was
driven with the **declared mechanism** — `rfp_engine.py --detect --keep-residue`, residue preserved
so it could be inspected rather than silently restored — and iterated until residue reached **zero**.

This certificate states the *properties* of that convergence, not a table of its rounds. A record
that enumerated its own convergence history would go stale the moment it was itself committed and
absorbed by the producers that inventory it, and updating it would require another round to record —
the self-reference `CLO-07` exists to forbid. The round-by-round history is owned by version control
(RFP-2) and is located at `git log --grep='Ω-E03 convergence'`.

The properties that hold at this record:

| Property | Evidence |
|---|---|
| Residue reached exactly zero | `rfp-gate` `tracked_modifications = 0`, `staged_entries = 0`, `untracked_outside_excluded = 0` over 3 passes |
| Every producer is byte-stable before its reading was committed | each producer re-run and digest-compared; no reading committed until two consecutive runs agreed |
| No intermediate dirty observation was committed as Repository Truth | the blueprint reads working-tree state **outside its own zone** (RFP-3), so its dirty-tree readings — recorded while upstream producers were still settling, at 10/12 gates — were **discarded, not committed**; the corpus consumers were committed ahead of it precisely so its reading could be taken at a clean tree, which is required for deterministic convergence rather than a convenience |
| The blueprint's committed reading was taken at a clean tree | `WORKING TREE CLEAN (0 entries…)`, `GATES 12/12`, `dirty=0`, `BLUEPRINT CERTIFIED — REPOSITORY MAY PROCEED` |
| A record describing the repository becomes part of it, lawfully | committing this certificate moved exactly one measurement — tracked files by one — and the producers that inventory and cite repository surfaces absorbed it without any determination changing; the fixed point absorbing that fact is the pipeline working, not a defect |

`STAGE-UIS` participates as a required, re-entrant stage in the **33-stage** pipeline: Ω-E03 extended
the pipeline, the discharge changed a stage's output, and the extended pipeline still converges.

---

## 15. Constitutional Invariants Preserved

| Invariant | Evidence |
|---|---|
| Exactly one identity authority | 7/7 obligated architectures declare it; `realization_obligations_unmet = 0` |
| No parallel authority created | `capabilities_created = 0`; `--check-no-authority` fails closed on any `CREATE` |
| Planes orthogonal, non-substitutable (`AIF-L03`) | 5/5 planes realized by exactly one located mechanism; schemes crosswalked, never merged |
| Recorded identities immutable (`UIL-13`, `AIF-L17`) | write ∩ record = 0, `disjoint = YES`; `identities_altered = 0`; `history_not_append_only = 0` |
| No renumbering (`UIL-06`) | `identities_renumbered = 0`; `identities_reused = 0` |
| Identifier opacity (`AIF-L02`, UIS-P-06) | `identities_attribute_coupled = 0`; self-description measured by resolution (`UIS-F-006`) |
| Knowledge Once | `--check-knowledge-once` PASS; `UAKOS-CLOSURE-002` CLOSED, gaps 0 |
| Reuse First | 48 REUSE + 6 EXTEND + 0 CREATE |
| Zero enumeration | `--check-no-enumeration` PASS — the discharge reads the key space rather than declaring it |
| Determinism | seal stable; `--check-determinism` PASS; replay no drift |
| Additive only / append-only | owner amendments only; `02-CANONICAL-OWNERSHIP-MATRIX.md` appended, never rewritten |
| Non-inheritance | this certificate carries no ratification, finality or authority forward |
| Ω∞ non-terminality (`CR-INF-001`) | `terminal_state_claims = 0` — no located instrument declares identity closed to evolution |
| Unbounded lawful expansion | 9/9 directions probed; `namespaces_near_capacity = 0` |
| Constitutional semantics unchanged by the discharge | declaration byte-identical in substance: 5 planes, 6 mechanisms, 20 laws, 19 obligations, 54 capabilities, 24 dimensions, 6 findings, all bounds — only the engine's measurement of a declared field changed |
| No prior capability weakened | Ω-E01's 22 authority dimensions and Ω-E02's 26 baseline dimensions remain blocking and satisfied; `UCCEP` 24/24 gates, 19/19 programmes, `blocking=none` |
| Repository remains a fixed point | 13/13 closure criteria over 33 stages, `cycles=0` |

---

## 16. Remaining Repository-Wide Architectural Gaps

### Findings raised by exit certification

| ID | Finding | Status |
|---|---|---|
| `VER-01` | **`UIS-V-10` did not measure what it declared.** `measure_bookkeeping` computed `bound` solely from `(REPO / owner).is_file()`; the declared `field` was rendered and never checked, and both branches of its plane conditional were byte-identical. Replacing all 19 fields with a nonexistent name left the gate OPEN, so `UIS-EX-06` was asserted rather than measured. The constitutional fact was true throughout — all 19 fields do resolve — but the proof did not prove it. | **DISCHARGED** (`OBL-E04-01`, commit `ba1a995`). The field is now measured at `ENTRY`, `DOCUMENT`, `MEMBER` or `SYMBOL` depth; 9/9 field-level controls drive the gate closed; 21/21 prior controls still die; `bookkeeping_fields_unresolved = 0`. |
| `VER-02` | **`UIS-V-15` is a restatement, not an independent measurement.** `identity_minting_attempts` is a literal `0`, so the dimension cannot fail. Its substance is carried by the `--check-no-identity-minting` self-guard, which does real work: it grammar-matches every emitted byte against the ledger's recorded identities and forbids writing any identity source. No fact is wrong; the dimension is redundant with a guard rather than independently falsifiable. | **OPEN — ADVISORY.** Referred to the measurement owner. Not blocking: the property is enforced, only not twice. |
| `VER-03` | **`programme.operational_home` is not the value the write-scope dimension binds to.** `OWN_PREFIX` derives from the engine's own location, so the declared home is documentation that could drift from the enforced home undetected. The dimension itself is sound — its trespass half is declaration-driven and kills cleanly. | **OPEN — ADVISORY.** Referred to the measurement owner. |
| `VER-04` | **The located exit record understates its own verification.** The `02-CANONICAL-OWNERSHIP-MATRIX.md` §2 `Ω-E03` addendum records "18 of 18 mutation scenarios drive the gate closed, so no dimension is vacuous". The count is now 30 of 30, and the "no dimension is vacuous" claim is confirmed for 18 of 24 dimensions and unprobed for 6. The addendum is append-only and belongs to the matrix owner; this certificate records the correction rather than editing it. | **OPEN — REFERRED** to the canonical ownership matrix owner. |

### Pre-existing repository-wide gaps (owned elsewhere, unchanged by Ω-E03)

From `00-MASTER/UCOS-RIB-001/06-GAP-ANALYSIS.md` over 238 discovered units, re-measured on a clean
tree at this certification:

| Gap | Class | Count |
|---|---|---|
| `GAP-EVIDENCE` | units with no located evidence surface | 230 |
| `GAP-VERIFICATION` | units with no located verification asset | 207 |
| `GAP-CERTIFICATION` | units carrying no recorded certification authority | 167 |
| `GAP-COVERAGE` | implementation units outside declared coverage scope | 26 |
| `GAP-DEPENDENCY` | implementation units with no measured dependency either way | 1 |
| `GAP-OWNER` · `GAP-RUNTIME` · `GAP-CAPABILITY` · `GAP-REGISTRY` · `GAP-DEAD-ENGINE` | — | 0 each |

Also standing: `CERTIFIED-PROVISIONAL` with **Tier T1 VACANT** (`VAC-01` / `CMG-OQ-02`) — no wave may
close this, since the vacancy is external to the repository; the Constitutional Reuse Gate remains
TO FORMALIZE as registered work package `WP-UCDA-005`; and the six `UIS-F-001…006` divergences of §9
remain open with their owners by constitutional necessity.

---

## 17. Authorization for Ω-E04

**AUTHORIZED — unconditionally. `OBL-E04-01` is discharged; no obligation is carried forward.**

Grounds:

1. Ω-E03's stated objective is met. The identity architecture is gate-verifiable rather than prose:
   54 capabilities owned, 0 created, 20/20 laws bound with 19 measured, 5/5 planes realized, 7/7
   architectures verifying the single authority, 9/9 expansion directions probed, 19/19 bookkeeping
   obligations bound to a **resolved field** and a closed-set facet, 24/24 blocking dimensions
   satisfied, `G-24` PASS.
2. The proof now proves the fact. The one dimension that was weaker than its stated text has been
   strengthened and is falsifiable at every resolution depth; 30 of 30 negative controls drive the
   gate closed.
3. Nothing was redesigned to achieve it. Identity, bookkeeping, canonical ownership and Repository
   Truth are unchanged; the declaration's substance is untouched; only the engine's measurement of an
   already-declared field changed.
4. No parallel authority was manufactured, and the measurement remains provably unable to become an
   identifier engine, registry, namespace, resolver or lifecycle.
5. The located records are provably unmodified: write ∩ record = ∅, all 7 anchors intact.
6. The result replays: no drift, stable seal, enforced in CI.
7. Repository Truth ends at a **committed deterministic fixed point**: working tree clean, zero
   residue, RIB measured on a clean tree at 12/12, RFP `OPEN`, 33 stages, 13/13 closure criteria,
   `cycles = 0`.
8. No previously certified capability was weakened: `UCCEP` at full tier reports 24/24 gates and
   19/19 programmes PASS with `blocking=none` and `unproven=none`; `verify.sh` is green; knowledge
   closure is CLOSED with 0 gaps.
9. Every divergence Ω-E03 could not lawfully repair is bounded with **zero slack**, disclosed, and
   referred to a named owner. `VER-02`, `VER-03` and `VER-04` are advisory or referred, and none is
   blocking.

**Ω-E03 is hereby constitutionally complete and closed.** Closure bounds scope, never evolution:
`terminal_state_claims = 0`, and `CR-INF-001` forbids reading this certificate as a terminal state.
Ω-E04 inherits no ratification, no finality and no authority from this record.

---

| Attestation | Value |
|---|---|
| CERTIFIED AT | the commit carrying this record · working tree CLEAN · zero residue |
| GATES RE-EXECUTED AFTER THE DISCHARGE | `make uis-self` 9/9 · `make uis-gate` OPEN · `make uis-replay` no drift · `./verify.sh` PASSED · `uccep_engine.py --tier full` 24/24 gates, 19/19 programmes · `make rib-gate` CERTIFIED, dirty=0, 12/12 · `make rfp-gate` FIXED POINT, 33 stages, 13/13, cycles=0 |
| NEGATIVE CONTROLS | 30 valid mutations · **30 killed** · 0 survived · declaration restored byte-exact · tree restored clean |
| SEAL LINEAGE | `cd753fa12a6b7ec8…` (asserted field binding) → `a05f279d99b26e5d…` (measured field binding) |
| AUTHORITY OF THIS CERTIFICATE | **NONE — DERIVED TRUTH.** It confers nothing, ratifies nothing and creates no exit authority. The canonical exit record is the `02-CANONICAL-OWNERSHIP-MATRIX.md` §2 `Ω-E03` addendum. |

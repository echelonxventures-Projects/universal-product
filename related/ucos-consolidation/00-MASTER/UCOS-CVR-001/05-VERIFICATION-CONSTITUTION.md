# UCOS-CVR-001 · 05 — THE VERIFICATION CONSTITUTION

> **Satisfies:** Task 7. **Status:** PROPOSED — awaiting constitutional approval.
> **Authority once ratified:** the permanent Verification Authority for UCOS. Every future
> implementation inherits it without amendment.
> **Anchor:** commit `898ef8d`. This instrument carries no wall-clock timestamp (Article VIII).

---

## ARTICLE I — VERIFICATION PRINCIPLES

| # | Principle | Statement |
|---|---|---|
| **VP-01** | **Derived Universe** | No verification scope is ever enumerated. Every universe is a pure function of Repository Truth. A path, package, module or directory naming a specific artifact must not appear in any executable verification file. |
| **VP-02** | **Totality** | Every tracked artifact holds exactly one verification class. There is no unclassified state, no `MISC`, no whitelist and no exception list. |
| **VP-03** | **Fail Closed** | An unknown, unmeasured, unresolvable or unowned condition is a failure. Silence is never success. |
| **VP-04** | **Declared Equals Measured** | Anything declared to be in a universe must appear in that universe's report. A declared-but-absent element fails the gate. |
| **VP-05** | **One Authority Per Subject** | Every verification subject has exactly one owner. Duplicated thresholds, duplicated scopes and duplicated verdicts are defects. |
| **VP-06** | **Reuse Before Create** | No verification capability may be created where a located owner exists. Binding is the default; authoring requires proven absence. |
| **VP-07** | **Evidence Or Absence** | Every claim resolves to evidence, or is declared absent with the evidence class that would be required. Fabrication and approximation are prohibited. |
| **VP-08** | **Determinism Of Judgement** | Identical inputs at an identical commit yield an identical verdict, in identical bytes, in every environment. |
| **VP-09** | **Provenance Without Entanglement** | Temporal and environmental provenance is preserved in a plane that no verification decision reads. |
| **VP-10** | **Verification Is Not Product** | Tests, tooling, evidence, certificates and generated output never contribute to the measurement of the product. |
| **VP-11** | **Monotonic Rigour** | Verification obligations and thresholds may only strengthen. Weakening requires an explicit constitutional amendment with recorded justification. |
| **VP-12** | **Inheritance** | Any artifact added after ratification acquires its obligations automatically, on the commit that adds it, with no configuration change. |
| **VP-13** | **Self-Verification** | The verification architecture is subject to its own rules and must carry guards proving it obeys them. |

---

## ARTICLE II — VERIFICATION TAXONOMY

Twenty-two verification types, in four bands. The set is **open**: a new type is an entry in the
declaration, never a code change (Article XI).

| Band | Types |
|---|---|
| **Static** | Lint · Static Analysis · Architecture Validation · Dependency Validation · Supply Chain Validation |
| **Behavioural** | Unit Test · Integration Test · System Test · Coverage · Mutation Testing · Performance Validation · Dynamic Analysis · Runtime Validation |
| **Structural** | Repository Validation · Registration Validation · Digital Twin Validation · Knowledge Validation · Context Validation · Temporal Validation |
| **Assertive** | Security Validation · Compliance Validation · Certification |

Each type carries exactly one authority, one default posture, and one reason
(`01` Part C). A type whose capability is absent is recorded `EXCLUDED — CAPABILITY ABSENT` with a
named owner-to-be; it is never recorded as Optional.

---

## ARTICLE III — VERIFICATION ONTOLOGY

| Term | Definition |
|---|---|
| **Artifact** | a version-controlled file; the atom of verification |
| **Class** | one of fifteen verification classes; a total, single-valued function of an artifact |
| **Unit** | the smallest thing a threshold may be applied to (a package, a module, an entry point) |
| **Type** | one of the twenty-two verification kinds |
| **Posture** | `MANDATORY` \| `OPTIONAL` \| `EXCLUDED` \| `EXCLUDED — CAPABILITY ABSENT` |
| **Obligation** | a `(class, type)` pair whose posture is MANDATORY |
| **Result** | the outcome of executing one obligation over one unit |
| **Evidence** | the content-addressed record of a result |
| **Verdict** | an aggregation of results by an authority |
| **Certificate** | a hash-chained, registered verdict |
| **Gate** | an executable that fails the build when an obligation is unsatisfied |
| **Universe** | a derived set of artifacts a gate is entitled to speak about |
| **Absence** | a declared, counted non-existence — a first-class result, never a blank |

---

## ARTICLE IV — COVERAGE ONTOLOGY

**IV.1** Coverage has exactly two dimensions, each with one authority, both bound to layer L4:

| Dimension | Measures | Authority |
|---|---|---|
| **Execution coverage** | statements and branches of production code executed by tests | `coverage` + `pytest-cov` |
| **Architectural coverage** | Universe → Phase → Program → Implementation → Epic → Module → CodeAsset → RuntimeAsset | `platform/coverage` |

Neither may be substituted for the other. A verdict quoting one dimension must name which.

**IV.2** `σ : class → {CONTRIBUTES, NEVER}` is total. `CONTRIBUTES` holds for exactly four
classes: Production Runtime, Production Library, Production CLI, Production Generator.

**IV.3** Tests never contribute to coverage. This rule is unamendable by ordinary process.

**IV.4** Coverage is governed by two floors — one aggregate, one per unit. An aggregate floor
without a per-unit floor is constitutionally insufficient, because it permits a fully unverified
unit inside a passing repository.

**IV.5** Coverage floors ratchet upward only (VP-11).

**IV.6** Every declared entry point is a unit.

**IV.7** Exclusion pragmas may remove only non-semantic lines. An exclusion that removes a
behavioural path is a violation of VP-07.

---

## ARTICLE V — CLASSIFICATION RULES

**V.1** The classification domain is the version-controlled corpus, and only that. Untracked files
are candidates: reported, never classified, never verified.

**V.2** Classification is an ordered rule chain over *evidence kinds* — self-declared metadata,
registration record, package ownership, capability ownership, structural position. The first match
wins. Ordering is the guarantee of single-valuedness.

**V.3** No rule may name a specific artifact. Rules name evidence, not paths.

**V.4** The chain terminates in `Unknown`, and `count(Unknown) > 0` fails the gate. The terminal
class exists so that failure is possible; it must never be used to absorb a tree.

**V.5** Classification is **append-only**. A new rule may introduce a class for previously
`Unknown` artifacts; it may not reclassify an already-classified artifact. Reclassification is an
amendment with recorded justification.

**V.6** The verification class is **orthogonal** to corpus identity (`program`/`category`/`volume`).
Neither axis may be overloaded to carry the other. Both derive from one boundary, so they can never
disagree about which artifacts exist.

---

## ARTICLE VI — DISCOVERY RULES

**VI.1** Discovery consumes six substrates only: Repository Truth, Registration, Classification,
Package Ownership, Capability Ownership, Artifact Metadata.

**VI.2** Discovery is a pure function of committed bytes. No wall-clock, no mtime, no environment
variable, no network, no working-tree state beyond the index.

**VI.3** Every universe publishes a digest. Two environments at one commit must produce identical
digests; inequality is a failure, not a warning.

**VI.4** The discovery engine must carry a **zero-enumeration guard** proving that no identifier
from its declaration is hard-coded in its own source. Task 4 is satisfied by that guard, not by
intent.

**VI.5** If the boundary cannot be established, the run **aborts**. An unknown universe may never
be replaced by a guess.

---

## ARTICLE VII — REGISTRATION RULES

**VII.1** Registration is the single identity authority. Unregistered means undiscoverable, and
undiscoverable means unverifiable.

**VII.2** Registration eligibility and verification classification share one boundary. Where
eligibility is narrower than the classification domain, the narrowing must be **declared, counted
and justified** — never implicit. *(Current state: eligibility = 1 204 of 4 862 tracked artifacts;
no source file is registrable. This is a declared narrowing, and it is why classification cannot be
delegated to registration.)*

**VII.3** Every verification unit resolves to an owner. An unowned unit is a finding.

**VII.4** Registration carries traceability; verification results attach to it. A result that
cannot attach to a registered subject is orphaned and fails.

**VII.5** Registration drift is a gate failure (already enforced by `register.sh --guard`).

---

## ARTICLE VIII — TEMPORAL RULES

**VIII.1** Every verification artifact has two planes: a deterministic plane containing no temporal
value, and a temporal plane containing the temporal record. The content hash covers the
deterministic plane only.

**VIII.2** The temporal plane is never an input to a verification decision.

**VIII.3** Every temporal value is produced through the Universal Temporal Framework, whose owners
are `UNI-006` (Time) and `DOM-0021` (Calendar). Verification **must not** implement its own clock,
calendar or conversion — that would create a duplicate authority (VP-05, VP-06).

**VIII.4** A temporal record carries: native instant and frame; universal reference instant and
standard; calendar; time standard; body; location; coordinates and coordinate system; bidirectional
conversion fidelity; formatting profile; precision; uncertainty; clock source.

**VIII.5** No Earth-specific default is permitted anywhere. `UTC`, `Z` and the Gregorian calendar
are ordinary registry entries, not defaults. Conformance is tested by substituting a non-Earth body
and a non-Gregorian calendar and requiring **no source change**.

**VIII.6** Formatting is rendering only. A rendered string is never compared, hashed or parsed back
as authority.

**VIII.7** A conversion that cannot be performed is declared `undefined`. Approximation without a
declared epsilon is prohibited (VP-07).

**VIII.8** Until the framework exists, `Temporal Validation` is satisfied only in its degenerate
form (`04` Part F) and **must be labelled interim** wherever asserted. An interim state presented
as conformance is a constitutional violation.

---

## ARTICLE IX — CERTIFICATION RULES

**IX.1** Certification consumes verification results; it never produces them. Hand-authored facts
entering a certification or acceptance gate are prohibited (this cuts the L5 → L3 edge).

**IX.2** A certificate names: subject, subject version, the obligations evaluated, every result,
the evidence digest, the policy digest, and the universe digest.

**IX.3** Certificates are append-only and hash-chained; the chain must be self-verifying.

**IX.4** An unsatisfied mandatory obligation makes certification impossible. There is no partial
certificate and no waiver without a recorded amendment.

**IX.5** Certification confers engineering readiness only, and must carry that disclosure verbatim.

**IX.6** A certificate whose evidence no longer resolves is **stale**, and stale is a failure.

---

## ARTICLE X — RUNTIME RULES

**X.1** One canonical command runs the whole verification architecture. Additional commands may
select subsets by declared tier; none may define its own scope.

**X.2** Tiers exist for latency, never for rigour: a tier may **defer** an obligation, never
**delete** one. Every mandatory obligation must be executed by at least one blocking gate.

**X.3** Local and CI execution run the identical gate over the identical universe. Divergence is a
defect of the gate, not of the environment.

**X.4** Verification is read-only with respect to the repository, except where a gate's declared
purpose is regeneration; those gates must carry a write-scope guard.

**X.5** Every gate is fail-closed: a gate that cannot determine its own verdict exits non-zero.

**X.6** Every gate reports what it executed, what it skipped, and why — a skipped obligation is
always visible.

**X.7** The environment is self-healing and pinned. A missing tool is a bootstrap failure, never a
skipped verification.

---

## ARTICLE XI — EXTENSION RULES

**XI.1** A new class, type, posture, threshold, unit kind, substrate or gate is an entry in the
verification declaration. **No engine change is permitted for extension.**

**XI.2** A new tree, package, band, capability or entry point acquires its obligations
automatically on the commit that introduces it (VP-12). If it does not, the discovery engine is
defective.

**XI.3** Admitting an absent capability (performance, mutation, dynamic analysis, supply chain)
requires: a pinned tool, a declared authority, a declared threshold, and a migration wave. Until
all four exist, the capability stays `EXCLUDED — CAPABILITY ABSENT`.

**XI.4** Extension may only add obligations or raise thresholds (VP-11).

---

## ARTICLE XII — MIGRATION RULES

**XII.1** Universe migration and threshold migration are **separate** acts and must never occur in
one commit. Widening a universe while holding a threshold constant is the only safe order.

**XII.2** Before a universe widens, its effect must be **measured and recorded** — the delta is
evidence, not a surprise. *(Measured for this mission: `U3` = 85.85 % branch-inclusive against a
declared floor of 90.)*

**XII.3** Where a widened universe would fail a ratified threshold, the authority chooses exactly
one, in writing: (a) raise coverage first, (b) admit with a per-unit exemption register that is
counted, dated and shrinking, or (c) reclassify the units honestly. **Lowering the threshold is
not among the options** (VP-11).

**XII.4** Every exemption is temporary, counted, attributed to an owner, and visible in every gate
run. An exemption without an owner is a violation.

**XII.5** No migration wave may leave the repository unable to run its canonical command.

**XII.6** Migration is reversible per wave: each wave declares its rollback before it executes.

---

## ARTICLE XIII — FUTURE EVOLUTION RULES

**XIII.1** The taxonomy is open. Verification types not yet conceived are admitted by declaration.

**XIII.2** The class set is open and append-only. Fifteen is the current cardinality, not a bound.

**XIII.3** The architecture must remain correct for artifact kinds that do not yet exist —
including non-textual, generated, model, data, hardware and non-Earth-frame artifacts. Any rule
that presumes "file of text in a git repository on Earth" is a defect to be corrected on discovery.

**XIII.4** No rule in this Constitution may be satisfied by a hand-maintained list. If satisfying a
rule requires enumeration, the rule is mis-specified and must be amended, not worked around.

**XIII.5** Amendment requires: the amended text, the reason, the authority, the measured impact,
and the migration wave. Amendments are append-only.

**XIII.6** This Constitution is subject to itself: it must be classified, registered, verified,
covered by its own guards, and certified like any other artifact (VP-13).

---

## RATIFICATION BLOCK

| Field | Value |
|---|---|
| Instrument | UCOS Verification Constitution |
| Programme | UCOS-CVR-001 |
| Status | **PROPOSED — NOT RATIFIED** |
| Authority asserted | NONE (DERIVED TRUTH) until ratified |
| Anchor | commit `898ef8d` |
| Temporal record | absent — see Article VIII.8 (framework unowned) |
| Blocking approval questions | `08-FINAL-READINESS-VERDICT.md` §3 |

*End of 05-VERIFICATION-CONSTITUTION.md*

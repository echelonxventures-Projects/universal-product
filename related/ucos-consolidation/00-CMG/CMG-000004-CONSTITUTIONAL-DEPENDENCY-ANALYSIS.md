# UCOS Ω∞ — CMG CONSTITUTIONAL DEPENDENCY ANALYSIS

| Field | Value |
|-------|-------|
| ARTIFACT ID | CMG-000004 |
| ARTIFACT | UCOS Ω∞ CMG Constitutional Dependency Analysis |
| CLASSIFICATION | Constitutional Meta Governance (CMG) — Dependency Analysis |
| PHASE | PHASE-000 |
| PROGRAM | CMG |
| CATEGORY | CMG |
| VOLUME | VOL-002 |
| STATUS | UNDER REVIEW · DERIVED · NON-NORMATIVE |
| VERSION | 1.0 |
| AUTHORITY | NONE (DERIVED TRUTH) |
| GOVERNED-BY | CMG-000001 |
| DEPENDS-ON | CMG-000001 |
| CANONICAL FORM | This Markdown file |

> Derived analysis under CMG-000001 Article XXXV (Dependency Model) and Article XVI (Authority Hierarchy). Every graph below is recomputable from `CMG-REGISTRY.json` by `00-CMG/tools/cmg_validate.py`.

---

## 1 — THE TWO GRAPHS

Two distinct directed acyclic graphs govern constitutional relationships, and conflating them is a common source of undecidability:

| Graph | Edge meaning | Cycle consequence | Verified by |
|---|---|---|---|
| **Dependency graph** | "cannot be evaluated without" | Undecidable validation | Kahn topological sort over `depends_on` |
| **Precedence lattice** | "governs on conflict" | Undecidable conflict resolution | Kahn topological sort over tier `subordinate_to` |

An artifact may depend on another without being subordinate to it, and may be subordinate without depending on it. Both graphs are verified acyclic independently (CMG-INV-05).

---

## 2 — PRECEDENCE LATTICE (TIER GRAPH)

```
                    T0  Constitutional Source Corpus
                     │        (frozen; informs, does not bind as law)
                     ▼
                    T1  Constitutional Authority  ── VACANT (VAC-01)
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      T1M           T2           T2I
   Meta-Const.   Program     Interpretive
   Authority     Authority    Authority
   (CMG-000001)  (CEP-000…)   (AUTH-INF-001)
        │            │            │
        └────────────┼────────────┘
                     ▼
                    T3  Domain Authority
                     ▼
                    T4  Execution Authority
                     ▼
                    T5  Derived-Truth Authority
```

**Declared orthogonalities** (no relative rank; conflicts resolve by jurisdiction, not by rank):
`T1M ⟂ T2`, `T2I ⟂ T2`, `T2I ⟂ T1M`.

**Why the tier identifiers are symbolic and non-consecutive.** `T1M` and `T2I` are inserted between numbered tiers precisely so that admitting a future tier never renumbers an existing one (CMG-000001 XVI.8). Consecutive numbering would be a hidden finite assumption.

**Topological sort result:** succeeds; 8 tiers, no cycle. Verified.

---

## 3 — INTRA-TIER REFINEMENTS PRESERVED

The lattice does not replace the located precedence statements; it contains them. Each located statement is a refinement **within** a tier:

| Tier | Located refinement, preserved verbatim in force |
|---|---|
| T2 | The four-tier Program authority order of the located charter (Constitutional → Program → Execution → Derived-Truth) |
| T2 | The governance conflict ladder: `CEP-000` over `CEP-001` over `CEP-002` over subordinate governance instruments; among equals, the earliest ratified definition prevails |
| T2 | The declared linear subordination chains in the front matter of `CEP-003` … `CEP-010`, each subordinate to all its predecessors in stated order |
| T3 | The located control-tower precedence chain ordering the frozen corpus, the technology constitution, architecture/engineering/runtime instruments, `STATUS-001`, `REG-AUTO-001`, and `UCI-001` |
| T3 | The closure-constitution ordering with `CONST-01` as the closure root and `CONST-02` … `CONST-11` as its refinements |

None of these is amended, restated, or overridden.

---

## 4 — DEPENDENCY CHAINS

### 4.1 The CEP spine (linear, depth 11)

```
CEP-000 → CEP-001 → CEP-002 → CEP-003 → CEP-004 → CEP-005
        → CEP-006 → CEP-007 → CEP-008 → CEP-009 → CEP-010
```
Each instrument declares subordination to all its predecessors. Depth 11, no branching, no cycle. This is the deepest chain in the corpus and the critical path for any change to `CEP-000`: an amendment there places all ten successors in the impact set.

### 4.2 The control-tower chain (linear, depth 4)

```
AUTH-INF-001 → STATUS-001 → REG-AUTO-001 → UCI-001 → GOV-INT-001
```
`UCI-001` is explicitly subordinate to both `STATUS-001` and `REG-AUTO-001`; `GOV-INT-001` is derived truth recording the chain.

### 4.3 The closure fan (depth 2, breadth 10)

```
CONST-01 → { CONST-02 … CONST-11 }
```
Wide and shallow: a change to `CONST-01` places ten artifacts in the impact set at depth 1, but no deeper.

### 4.4 The domain layer (depth 2, breadth 9)

```
TECH-CONST-001 → { DATA-001, RUNTIME-001, APPLICATION-001,
                   INFRASTRUCTURE-001, SERVICE-001, PLATFORM-001,
                   SECURITY-001, CAT-000, REF-000 }
```
The technology constitution is the shared superior of the domain constitutions. The domain constitutions do not depend on each other — this is why they coexist in T3 without a rank: their jurisdictions are disjoint, which the validator confirms by checking that their owned concern sets do not intersect.

### 4.5 CMG-000001

```
VAC-01 (vacant superior)
  ▲
CMG-000001 ──depends-on──▶ CEP-000 … CEP-010, AUTH-INF-001,
                           STATUS-001, REG-AUTO-001, UCI-001
```

**Topological sort result:** succeeds; 43 artifacts, no cycle. Verified.

---

## 5 — THE ACYCLICITY QUESTION FOR A META LAYER

A meta layer is the natural place for a constitutional dependency cycle to appear, because it plausibly needs the instruments that plausibly need it. CMG-000001 avoids the cycle by a deliberate asymmetry (CMG-000001 VII.6, XXXV.8):

| Direction | Present? | Reason |
|---|---|---|
| CMG-000001 **depends on** located instruments | Yes — 15 consumption dependencies | It delegates domains to them and consumes their models by reference |
| Located instruments **depend on** CMG-000001 for their standing | **No** | Their standing derives from their own declarations and from the located charter. Recognition adds no precondition to their validity |

Because the second direction is empty, no cycle can form through CMG-000001. This is verified: removing CMG-000001 from the graph changes no other artifact's dependency set.

---

## 6 — DEPENDENCY DEFECTS DETECTED

| Check | Result |
|---|---|
| Dependency cycles | 0 |
| Precedence lattice cycles | 0 |
| Unresolvable dependency targets | 0 |
| Unresolvable superior references | 0 (1 resolves to a recorded vacancy with a closure procedure, which is legal under CMG-INV-04) |
| Dependencies on POST-EFFECT artifacts | 0 |
| Incomparable, non-orthogonal artifact pairs | 0 |
| Same-tier pairs with overlapping jurisdiction and no declared rank | 0 |

---

## 7 — STANDING PROPAGATION

CMG-000001 XXXV.6 holds that standing cannot exceed the weakest dependency. Applied to the present corpus:

| Artifact set | Weakest dependency | Maximum standing |
|---|---|---|
| `CEP-000` | `VAC-01` (vacant T1) | PROVISIONAL |
| `CEP-001` … `CEP-010` | `CEP-000` (provisional) | PROVISIONAL |
| `AUTH-INF-001` | `VAC-01` | PROVISIONAL |
| `CMG-000001` | `VAC-01` | PROVISIONAL |
| Domain constitutions | `TECH-CONST-001` (provisional) | PROVISIONAL |
| `CONST-01` … `CONST-11` | `CEP-002` (provisional), frozen by their own baseline | FROZEN-PROVISIONAL |

**This is the single most consequential finding of the dependency analysis.** The vacancy at T1 propagates through the entire dependency graph. No artifact in the corpus can hold non-provisional constitutional standing until `VAC-01` closes. CMG-000001 does not create this condition; it makes it computable. Closing `CMG-OQ-01` and `CMG-OQ-02` is therefore the highest-leverage constitutional act available to the corpus — it is the one change that lifts standing everywhere at once.

The registry records `CONST-01` … `CONST-11` in state `FROZEN`, which is legal: freezing preserves standing without upgrading it (CMG-000001 XXVI.4, CMG-T-09).

# USIS-004 — Universal Capability Meta-Model

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-004 (Universal Capability Meta-Model) |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| STATUS | PROPOSED · AWAITING RATIFICATION · PRE-WAVE-0 |
| DEPENDS-ON | USIS-001 (LAW USIS-08) · USIS-002 · UCIC-001 · MIP per-part 24-field contract |
| BINDING | LAW USIS-08 — **every** present and future USIS capability SHALL conform to this meta-model end-to-end. |

> **Purpose.** Define the single constitutional realization model every capability follows, from a science down to certified, evidenced, governed implementation — so realization is uniform, deterministic, and machine-checkable, and no capability can exist partially.

---

## 1 — The canonical realization chain (24 tiers)

```
Science → Discipline → Domain → Sub-Domain → Capability → Theory → Ontology →
Taxonomy → Registry → Knowledge Object → Model → Algorithm → Pattern → Engine →
Runtime → Service → API → SDK → Implementation → Validation → Certification →
Evidence → Governance → Lifecycle
```

Each tier is a typed node with a canonical owner, a Universal ID, and edges to its parent tier and dependencies. The chain is **recursive** (a Sub-Domain may branch into Sub-Domains; LAW USIS-09) and **open** (new sciences/domains append without redesign).

## 2 — Tier contract

| Tier | Owner produces | Required edge (Parent) | Closure obligation (USIS-011) |
|------|----------------|------------------------|-------------------------------|
| Science | science registry row (USIS-SCI-*) | Universal Science Universe | registry closure |
| Discipline | discipline node | Science | taxonomy closure |
| Domain | domain home (06-DOMAINS/…) | Discipline | ownership closure |
| Sub-Domain | sub-domain node | Domain | taxonomy closure |
| Capability | capability spec (UCIC Output-2) | Sub-Domain/Domain | capability closure |
| Theory | theory artifact | Capability | — |
| Ontology | ontology entry | Theory | ontology closure |
| Taxonomy | taxonomy entry | Ontology | taxonomy closure |
| Registry | registry membership | Taxonomy | registry closure |
| Knowledge Object | UKO node | Registry | knowledge-once |
| Model | model row (agnostic) | Knowledge Object | model appended, versioned |
| Algorithm | algorithm row (agnostic) | Model/Capability | algorithm appended |
| Pattern | pattern artifact | Algorithm | — |
| Engine | engine spec (references registries) | Pattern | zero-hard-coding |
| Runtime | runtime binding | Engine | — |
| Service | service contract | Runtime | — |
| API | API surface | Service | — |
| SDK | SDK surface | API | — |
| Implementation | code artifact (Software stream) | SDK | UCIC Stages 4–8 |
| Validation | validation record | Implementation | validation closure |
| Certification | certification record | Validation | certification closure |
| Evidence | evidence bundle | Certification | TRACK-001 fail-closed |
| Governance | governing determination + gates | (spans all) | constitutional consistency |
| Lifecycle | lifecycle state (per stream) | (spans all) | dependency + traceability closure |

## 3 — Conformance rule (fail-closed)

A capability is **realized** only if every tier from Science → Lifecycle is present, owned, edged, and evidenced. A missing tier ⇒ the capability is NOT realized (partial realization is not a valid state). This is the meta-model instantiation of UCIC-001 Output-6 (Universal Completion Definition).

## 4 — Agnosticism boundary (LAW USIS-04)

- Tiers **Theory → Pattern** are *specification* tiers — technology-free.
- Tiers **Model / Algorithm** carry an optional `binding` field for present-day technology, which is *registered content*, swappable without changing any upper tier.
- Tiers **Engine → SDK** reference registries by contract and enumerate no member.
- Tier **Implementation** is the only tier that produces code, realized in the Software/Infrastructure stream and *referenced* by the capability (preserving intelligence-stream purity, USIS-008).

## 5 — Reuse-First selection (LAW USIS-02)

Before creating any tier node, the owner MUST search existing universes/registries for a canonical instance and **reuse** it (Knowledge-Once). A new node is admissible only if no canonical instance exists. This is the structural guarantee of Zero-Duplication / Zero-Overlap (verified in USIS-011).

## 6 — Recursion & infinite depth

The chain is self-similar: any Domain/Sub-Domain node can host a full child chain. There is no maximum depth or breadth. New tiers themselves (should a future science require one) register as meta-model extensions append-only (never a rewrite of an existing tier — CR-INF-007).

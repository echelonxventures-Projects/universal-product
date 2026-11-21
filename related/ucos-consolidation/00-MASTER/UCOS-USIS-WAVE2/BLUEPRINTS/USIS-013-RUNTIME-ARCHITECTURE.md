# USIS-013 — Runtime Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-013 (Runtime Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Runtime (USIS-004 tier 15) |
| CANONICAL HOME (on realization) | `15-…/14-RUNTIME/` |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-011 (Engine) |
| DEPENDS-ON | USIS-011 (Engine) · USIS-001 (LAW USIS-06) · `08-RUNTIME`/RIE (referenced) · Universe U26 (referenced) |
| CONSTITUTIONAL ANCHOR | LAW USIS-06 (governed autonomy & self-evolution); LAW P21-001/002/003; MIP Parts 21/22/32 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/011 + `08-RUNTIME` + U26/U28. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Runtime** — the tier that hosts engine execution, on-demand and continuous, under governed autonomy. This blueprint specifies the runtime node shape, the governed-autonomy and self-* bounds (LAW USIS-06), and the reference relationship to the platform runtime, without duplicating it.

---

## 1 — Purpose
The Runtime tier binds an Engine (USIS-011) to an execution mode — on-demand invocation or continuous operation — and enforces the governed-autonomy envelope. It is where self-* capabilities operate under a simulate-then-adopt, reversible-or-justified discipline (LAW USIS-06).

## 2 — Responsibilities
- Own the **runtime node shape**: execution mode (on-demand / continuous), governed-autonomy policy binding, and self-* gating contract.
- Enforce **governed autonomy** (LAW USIS-06): self-modification is simulate-then-adopt via a governance + simulation gate before effect; no unbounded self-modification.
- Provide the **hosting contract** consumed by Service (USIS-012).
- **Reference** the platform runtime (`08-RUNTIME`) and the RIE twin rather than re-homing execution machinery (LAW USIS-05).

## 3 — Boundaries
- **Owns:** runtime node shape, execution-mode binding, governed-autonomy/self-* gating for science-intelligence.
- **Does not own:** the platform runtime/scheduler (`08-RUNTIME`/RIE — referenced), the Simulation universe (U26 — referenced), the engine logic (USIS-011), or the service contract (USIS-012).
- Introduces no parallel runtime; specializes the universal runtime for the science-intelligence stream.

## 4 — Interfaces
Exposes: `register · describe · govern · secure · monitor · observe · meter · simulate · evolve · explain`. A runtime declares the engine it hosts, the execution mode, and the governance/simulation gate that fronts any self-* effect.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-011 (Engine). References `08-RUNTIME`/RIE (execution substrate) and Universe U26 (simulation gate). USIS-012 (Service) `Depends-On` this tier — Runtime founds Service (meta-model), though its catalog number is higher (numbering-index artifact; see Dependency Report).

## 6 — Registry model
Runtime bindings are recorded in the **Execution Registry** (target #5, under the Universal Science & Intelligence stream) and the Architecture Registry. Self-evolution actions register in the program **Self-Evolution Registry** (`04-REGISTRIES/`), append-only, each carrying its governance + simulation gate outcome.

## 7 — Relationship model
Parent edge → Engine (USIS-011). Child edge → Service (USIS-012). Reference edges → `08-RUNTIME`/RIE (host), U26 (simulation), U28 (evolution), Evidence (USIS-016). Governance and Lifecycle tiers span the node.

## 8 — Lifecycle
A runtime node follows **DEFINED → BOUND (engine + mode) → GOVERNED (autonomy envelope set) → REGISTERED → EVOLVING**, under UCIC-001. Any self-* transition passes the governance + simulation gate before effect (LAW USIS-06); effects are reversible-or-justified (LAW P21-003).

## 9 — Validation model
Referenced to USIS-014: a runtime is valid only if every self-* pathway is gated (no ungoverned autonomy), the governed-autonomy envelope is declared, and explanation coverage of runtime decisions is present (LAW USIS-07). Drift/hallucination/contradiction monitoring is declared (Part 20 models, referenced).

## 10 — Certification model
Referenced to USIS-015: certification confirms bounded autonomy (no unbounded self-modification), reversibility-or-justification of self-* effects, and canonical ownership. An ungated self-* pathway is non-certifiable (fail-closed).

## 11 — Evidence model
Referenced to USIS-016: execution traces, self-evolution gate outcomes (simulation result + governance decision), provenance and explanation traces (LAW USIS-07), and monitoring signals.

## 12 — Failure model
Per UCIC Output-4. An ungoverned self-* effect ⇒ LAW USIS-06 violation ⇒ non-certifiable/rolled back. A duplicated runtime/scheduler ⇒ Zero-Duplication violation. A self-* effect without a simulation gate ⇒ blocked before effect; rollback is reversal-or-justification.

## 13 — Reuse model
Reuse-First (LAW USIS-02): the platform runtime (`08-RUNTIME`), RIE twin, and Simulation universe (U26) are **referenced**, never re-homed. USIS runtime adds only the science-intelligence execution-mode and governed-autonomy specialization.

## 14 — Non-goals
- Not the platform runtime/scheduler (`08-RUNTIME`) nor the simulation engine (U26).
- Not a service surface (USIS-012) or API/SDK (USIS-017).
- Permits no unbounded self-modification; names no technology (LAW USIS-04/06).

*END — USIS-013 · RUNTIME ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*

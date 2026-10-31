# LUXORA Ω∞ — Architecture Constitution: final text (owner choices applied; awaiting the owner's confirmation as LXM-DEC-000015)

**Status: FINAL TEXT, NOT YET ADOPTED.** The owner's choices of 2026-10-31 (section 7) are applied. It becomes binding only when the owner confirms it as LXM-DEC-000015, and nothing is implemented before then. **Prepared by:** `amazon-44`, 2026-10-31. **Decides:** the owner.

**Basis:** the owner's text "Universal Autonomous Architecture" (pasted on 2026-10-30, preserved verbatim beside this file). The proposal keeps every intent of that text and changes three things:
- each rule becomes checkable;
- two absolute rules are bounded so that they help shipping rather than block it;
- the critical invariants and the order of work are made explicit.

Section 7 lists the choices the owner makes.

## 1. What this document is

A destination plus enforceable rules. Every rule below has an **invariant** (what must be true), a **check** (how a machine knows) and an **enforcement point** (where a violation is stopped). A rule without a check is a principle, not yet a rule.

## 2. Constitutional invariants (first-class, never traded off)

| # | Invariant | Check | Enforced at |
|---|---|---|---|
| I1 | **Money integrity.** One exact money model: integer minor units, explicit currency and scale. Every movement goes through a ledger, is reconciled and is never inferred. | Money audit: no float money in scope; ledger balances | CI + runtime guards |
| I2 | **Tenant isolation.** No data, configuration or action crosses a tenant boundary unless a contract allows it. | Isolation tests per surface | CI + runtime authorization |
| I3 | **Security and authorization.** Least privilege, audited actions, secrets never in code or images. | Security suite; secret scan | CI + runtime |
| I4 | **Knowledge Once.** Each fact has one canonical home; everything else is generated from it. | Regenerate-and-diff; duplicate detection | Gate + CI |
| I5 | **Zero unjustified hard-coding.** Business, market, provider, brand and technology facts are governed configuration. Each exception is declared with a reason. | Configuration and code adapters (ratchet to zero) | CI |
| I6 | **Technology agnosticism.** Technologies and providers sit behind contracts and adapters; the core names none. | Technology governance gate; core scan | CI |

**Privacy and compliance** is not a constitutional invariant (owner's choice, 2026-10-31). It remains governed requirements (consent, retention, data ownership and jurisdiction, all by configuration) and release gate 19, so it still blocks release until evidenced.

## 3. The seven rules, made enforceable

| Rule | Final wording | Check | Enforced at |
|---|---|---|---|
| R1 Connected architecture | Every domain declares what it provides and consumes. Cross-domain interaction goes only through declared contracts. | An undeclared cross-domain dependency fails | CI |
| R2 One source of truth | No parallel source of truth. **Transitional structures are allowed only if declared** (owner, reason, exit condition, date), are never authoritative, and are removed by their exit condition. | Transitional register: an undeclared or expired entry fails | CI + readiness |
| R3 Automatic propagation | A canonical change regenerates every dependent view, index, specification and test fixture. Nothing is synchronised by hand. | Committed generated files equal a fresh generation | CI |
| R4 Governed extensibility | New providers, markets, business models, capabilities and object types enter through **registered extension points** (contract + adapter + conformance tests). Generality is built when a registered need arrives, not ahead of it. | The core names no provider, market or business model; each extension passes its contract tests | CI |
| R5 No false completion | Each requirement and capability carries a computed state (§4). No state is declared by hand. | Readiness computes states from evidence | Readiness + release gate |
| R6 Automation by default | Every deterministic decision is automated. **Owner-reserved decisions** (financial policy, release, scope, irreversible data actions, security exceptions, architecture changes) are governed and never guessed. | Owner-reserved changes need a recorded decision with approval | Gate |
| R7 Enforcement at change time | Every change to knowledge, configuration or code passes the gate and CI before it lands. Independent assurance is periodic and never the maintenance mechanism. | Required checks protect the main branch | Repository settings + CI |

## 4. Lifecycle states (R5)

**Specified → Designed → Implemented → Configured → Enforced at runtime → Verified → Certified**

Each state requires its own evidence, and a state is never inferred from the one before it:

| State | Evidence required |
|---|---|
| Specified | A canonical requirement |
| Designed | A specification section |
| Implemented | Code traced to the requirement |
| Configured | A declared, governed configuration |
| Enforced at runtime | A runtime trace or an invariant check |
| Verified | Tests passing on the exact SHA |
| Certified | Release evidence and owner approval |

## 5. Layers (clarified)

1. **Foundation (kernel).** Identity, registry, configuration, rules, events, workflow, data, integration adapters, security. It names no business.
2. **Domains.** Commerce, Finance, Operations, Experience. Each domain owns its data and contracts, and invariants I1–I3 apply inside every one.
3. **Composition.** Business profiles assemble capabilities through configuration. A profile or template is never proof of a working solution.
4. **Intelligence (bounded).** Decision support and automation on governed data. It **proposes; it never acts** past an invariant or an owner decision. A change to production comes only through the gate.
5. **Execution and lifecycle.** Deployment, observability, resilience, recovery, automatic conformance.
6. **Knowledge and assimilation.** The Master and its gate govern every layer above.

## 6. Operating loop and order of work

**Loop:** Discover → Assimilate → Validate → Execute → Observe → Propose.
- "Learn" is defined as: measured outcomes produce proposals.
- Proposals enter through the gate like any other contribution.
- Nothing modifies itself in production.

**Order of work** (each step permanent, LXM-REQ-000230):
1. Invariants I1–I3 enforced for the launch scope.
2. The first-marketplace journeys reach **Verified** end to end.
3. Governance in CI: the Master in the repository, R7 active.
4. Generalisation through registered extension points as needs are registered.

## 7. The owner's choices (2026-10-31)

| # | Choice | Owner's answer |
|---|---|---|
| A | R2: transitional structures | **Allowed if declared**, with an owner, reason, exit condition and date; never authoritative |
| B | R4: generality | **On registered need** (marketplace first), through registered extension points |
| C | First-class constitutional invariants | **Money integrity, tenant isolation, security and authorization** (privacy and compliance not promoted) |
| D | Lifecycle states (§4) | **Adopted as written** |
| E | Intelligence proposes, never acts past invariants or owner decisions (§5.4) | **Adopted as written** |
| F | Order of work (§6) | **Adopted as written** |

The answers are recorded verbatim in `LXM-DEC-000015.answers.txt`, with their transcript provenance.

## 8. Once confirmed

1. The text is recorded as **LXM-DEC-000015** through the decision gate.
2. It is assimilated as a new source, SRC-0010. Its rules are matched against the existing requirements (LXM-REQ-000195 to 000230 already cover much of it) and added only where new.
3. Each check in §2 and §3 becomes a test in the tools already built.

# UCOS-RFP-001 — REPOSITORY CLOSURE LIFECYCLE

> GENERATED FROM `rfp-declaration.json` BY UCOS-RFP-001 — DO NOT EDIT BY HAND.
> Regenerate with `make rfp`. AUTHORITY = NONE (DERIVED TRUTH).
>
> This projection records the DECLARATION only. It carries no commit identity
> (RFP-2) and no observation of the working tree (RFP-3) — including the
> fixed-point verdict itself, which is carried by the gate's exit code and
> standard output. An artifact asserting "the repository is a fixed point"
> would falsify that sentence by being written.

## The canonical lifecycle

| # | Stage | Closure-relevant | Gate |
|---|---|---|---|
| 1 | Repository Discovery | — | — |
| 2 | Context Assimilation | — | — |
| 3 | Architecture Review | — | — |
| 4 | Implementation | — | — |
| 5 | Verification | yes | `G-10` |
| 6 | Validation | yes | `G-10` |
| 7 | Evidence Generation | yes | `G-12` |
| 8 | Registry Regeneration | yes | `G-07` |
| 9 | Certification | yes | `G-11` |
| 10 | Commit | yes | — |
| 11 | Fresh Repository Discovery | yes | `G-15` |
| 12 | Pipeline Re-execution | yes | `G-15` |
| 13 | Repository Fixed-Point Verification | yes | `G-15` |
| 14 | Programme Closure | yes | `G-15` |

## What this programme adds

Steps 1–10 were already the repository's practice. Steps 11–14 are new and are the whole substance of the mission: closure is no longer asserted at certification, it is asserted only after the repository has been shown to reproduce itself from the state that was committed. Certification says *the state is lawful*; fixed-point verification says *the state is real*.

## Inheritance

- **RFP-1 Fixed-Point Closure Condition** — No programme may close, and no repository may be certified, unless the repository is a Stable Repository State: executing the declared pipeline over the committed HEAD leaves the repository byte-identical, for each of the declared convergence passes.
- **RFP-7 Universal Inheritance, No Opt-Out** — RFP-1..RFP-6 bind every PROGRAM, EPIC, EIP, Universe, Framework, Capability and Module, present and future, with no opt-out and no per-programme exemption. Inheritance is structural: the condition is evaluated over the REPOSITORY, so anything the repository contains is bound without needing to declare itself bound.

Inheritance is structural, not registrational: the condition is evaluated over the REPOSITORY, so every programme the repository contains is bound without enrolling, and no programme can exempt itself by omission.

---

*Regenerate with `make rfp`.*

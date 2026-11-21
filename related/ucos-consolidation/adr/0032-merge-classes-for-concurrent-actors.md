# ADR-0032: Four merge classes: derived regenerates, ledgers union and refuse, declarations merge by hand

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-05`, `UCKP-ART-13`, `REG-AUTO-001` §7, `DEC-ADR-0020` |
| Supersedes | none |

## Context

Measured on this repository: `relationships.json` is 2.9 MB, `id-ledger.json` 2.3 MB and
`artifacts.json` 2.1 MB. Every actor that registers anything rewrites all three, so every
parallel branch collides — and a textual merge of a *derived* register is meaningless even
where git accepts it, because these files are a pure function of the tree.

The identity ledger is worse than meaningless: a text merge can resolve an identity collision
by picking a side, which `UCKP-ART-05` forbids outright.

## Decision

Four declared merge classes, held in `00-BOOK/DATA/workspace-coordination.json` and projected
by `.gitattributes`:

- **DERIVED** — regenerate. Correctness comes from the regeneration, and `register.sh --guard`
  already refuses a commit whose generated output is stale, so no second enforcement is created.
- **IRREVERSIBLE** — union by key, and **refuse** on a divergent value. Never regenerate:
  re-deriving would reissue identity.
- **APPEND_ONLY** — union. Two actors appending different lines have not disagreed.
- **AUTHORED** — merge by hand. A conflict is a real disagreement between two people.

## Alternatives rejected

**Rely on short branches and care.** Rejected: `P-UCOS-CORPUS-001` was lost to a moving head
and `P-UCOS-CORPUS-003` nearly was, both under care.

**Regenerate the identity ledger on conflict.** Rejected — it would reissue identity, which is
the one thing `ART-05` forbids without qualification.

**Shard the large registers into one file per record.** Not rejected, deferred: it is the
durable fix and a large migration, and the merge drivers make it unnecessary for now.

## Revisit conditions

- A conflict class appears that none of the four describes — most likely a register that is
  partly derived and partly authored, which would need splitting rather than a fifth class.

## Consequences

Two actors can register artifacts on separate branches and both merge with no manual conflict
resolution. An identity collision stops the merge loudly instead of being resolved silently.

A named driver is inert without `merge.<name>.driver` in each clone, so
`scripts/install-hooks.sh` configures both and `register.sh --observe` warns when a declared
driver is unconfigured.

## Compliance

`ART-05` (identity never reissued) is what makes the ledger union-and-refuse rather than
regenerate. `ART-13` (one canonical form) is what makes a derived register regenerate rather
than merge. `REG-AUTO-001` §7 (atomic creation) is unaffected: source and projection still move
in one commit.

## Validation evidence

Implemented and exercised at commit `c0c43f88`. The union driver was run against a real
two-branch git merge: disjoint allocations unioned with `page_cursor` reconciled to the maximum;
one key carrying two values was refused with exit 1. `make merge-drivers` re-runs that selftest.

#!/usr/bin/env bash
# UCOS Ω∞ — merge driver for DERIVED registers.  git calls: driver %O %A %B %P
#
# WHY THIS RESOLVES TO ONE SIDE AND DOES NOT MERGE. These files are a pure function of
# the tree: `ukb.py build` re-derives them. Any textual merge of two derivations is a
# third thing that neither producer would emit, and it would be committed as truth.
# So the driver takes one side to complete the merge, and correctness comes from the
# REGENERATION that follows, not from the choice.
#
# WHY NOTHING HERE RUNS THE PRODUCER. Mid-merge the tree is not in a state a producer
# can read. Instead this leans on a guard that already exists: `register.sh --guard`
# fails (exit 3) when generated output differs from what is committed. An unregenerated
# merge is therefore refused at the boundary that already asks that question, and no
# second enforcement mechanism is created.
set -euo pipefail
ours="$2"; path="${4:-<unknown>}"
printf '%s\n' "ucos-regenerate: resolved '$path' to the current side." >&2
printf '%s\n' "  This file is DERIVED. Run: bash 00-BOOK/tools/register.sh" >&2
printf '%s\n' "  register.sh --guard refuses the commit until it is regenerated." >&2
exit 0   # %A already holds our side; leaving it is the resolution

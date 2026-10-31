#!/usr/bin/env bash
# End-of-step check for the canonical writer (LXM-REQ-000237): a step is finished only when git status is clean.
# usage: step-check.sh <repository root>
# Exit 0 clean; 1 not clean (lists what remains); 2 not a git working tree. It only reads: it never commits, stashes,
# reverts or deletes anything (LXM-REQ-000030), and it never removes .git/index.lock.
set -uo pipefail
R="$1"
git -C "$R" --no-optional-locks rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git working tree: $R"; exit 2; }
st="$(git -C "$R" --no-optional-locks status --porcelain=v1 --untracked-files=all)"
head="$(git -C "$R" --no-optional-locks rev-parse HEAD)"
if [ -n "$st" ]; then
  echo "NOT CLEAN at $head: $(printf '%s\n' "$st" | grep -c .) path(s) modified, staged or untracked. Commit the step's work; never revert or discard it."
  printf '%s\n' "$st" | head -50
  exit 1
fi
echo "clean at $head"

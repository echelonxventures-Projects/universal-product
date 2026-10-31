#!/usr/bin/env bash
# Fixtures for step_commit.py against a throw-away local remote: a step is committed and pushed; a repeat changes nothing;
# a protected branch, a suspected secret, an index lock, a diverged remote, a receiving repository not confirmed private and a
# detached HEAD are refused with nothing changed.
# usage: test_step_commit.sh <scratch dir>
set -uo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; T="$1/step-commit-fixture"; rm -rf "$T"; mkdir -p "$T"; cd "$T"
# the fixture's own configuration: the real one, with the visibility check answered by a stand-in (private unless the file "public" exists)
python3 -I -c 'import json,sys; c=json.load(open(sys.argv[1])); c["visibility_check"]={"repo_pattern":"(remote)\\.git$","command":["sh","-c","[ -e \"$0\" ] && echo false || echo true",sys.argv[3]],"expect":"true"}; json.dump(c,open(sys.argv[2],"w"))' "$H/step-commit.json" "$T/cfg.json" "$T/public"
python3 -I -c 'import json,sys; c=json.load(open(sys.argv[1])); json.dump(c,open(sys.argv[2],"w"))' "$H/step-commit.json" "$T/real.json"
sc() { python3 -I "$H/step_commit.py" "$@" --config "$T/cfg.json" >/dev/null; echo $?; }
fails=0; want() { if [ "$2" = "$3" ]; then echo "PASS  $1"; else echo "FAIL  $1 (exit $2, wanted $3)"; fails=$((fails+1)); fi; }
git init -q --bare remote.git; git clone -q remote.git ws 2>/dev/null; cd ws; git config user.email f@f; git config user.name f
echo a > a.txt; git add a.txt; git commit -qm init; git push -q origin HEAD:refs/heads/master; git switch -qc step/one
echo b > b.txt; want "step committed and pushed" "$(sc . --message one)" 0
[ -z "$(git status --porcelain)" ] && [ "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/step/one | cut -f1)" ]; want "tree clean, remote equals local" $? 0
want "repeat changes nothing" "$(sc . --message two)" 0
git switch -q master; echo c > c.txt; want "protected branch refused" "$(sc . --message x)" 1; rm c.txt; git switch -q step/one
k=key; echo "api_$k = \"abcd1234efgh5678\"" > s.env; want "suspected secret refused" "$(sc . --message x)" 1; rm s.env
touch .git/index.lock; echo d > d.txt; want "index lock refused, lock kept" "$(sc . --message x)" 1; [ -e .git/index.lock ]; want "lock not deleted" $? 0; rm .git/index.lock d.txt
cd "$T"; git clone -q -b step/one remote.git other; cd other; git config user.email f@f; git config user.name f; echo z > z.txt; git add z.txt; git commit -qm other; git push -q; cd "$T/ws"
h="$(git rev-parse HEAD)"; echo e > e.txt; want "diverged remote refused (no force-push)" "$(sc . --message x)" 1
[ "$(git rev-parse HEAD)" = "$h" ] && [ -n "$(git status --porcelain)" ]; want "refusal changed nothing" $? 0; rm e.txt
touch "$T/public"; h="$(git rev-parse HEAD)"; echo f > f.txt; want "public receiving repository refused" "$(sc . --message x)" 1
[ "$(git rev-parse HEAD)" = "$h" ]; want "refusal before publishing changed nothing" $? 0; rm "$T/public"
want "unrecognised remote refused (real configuration)" "$(python3 -I "$H/step_commit.py" . --message x --config "$T/real.json" >/dev/null; echo $?)" 1; rm f.txt
git checkout -q --detach; want "detached HEAD refused" "$(sc . --message x)" 1
echo; echo "$fails failed"; exit $((fails > 0))

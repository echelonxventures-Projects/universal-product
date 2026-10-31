"""End-of-step commit and push for the canonical writer (LXM-REQ-000237): commit the step's work, push it to its own
branch, and finish only when the tree is clean and the remote head equals the local head.
Usage: python3 -I step_commit.py <workspace> --message <text> [--config step-commit.json] [--dry-run]

Refuses, changing nothing: a receiving repository not confirmed private, a present .git/index.lock (never deleted), a detached HEAD, a protected or frozen branch, a
push that is not a fast-forward (never force-pushes), and any changed file that looks like it holds a secret. It never
reverts, stashes or discards work (LXM-REQ-000030). Exit 0 clean and pushed (or nothing to do), 1 refused, 2 usage error."""
import json, os, re, subprocess, sys
sys.dont_write_bytecode = True


def git(ws, *a, check=True):
    r = subprocess.run(['git', '-C', ws, '--no-optional-locks'] + list(a), capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError('git %s: %s' % (' '.join(a), (r.stderr or r.stdout).strip()[-400:]))
    return r.stdout.strip()


def refuse(msg):
    print('REFUSED: ' + msg); sys.exit(1)


def main(argv):
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    if len(argv) < 2 or not opt('--message'):
        print(__doc__); return 2
    ws, msg, dry = os.path.abspath(argv[1]), opt('--message'), '--dry-run' in argv
    cfg = json.load(open(opt('--config') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'step-commit.json')))
    gitdir = git(ws, 'rev-parse', '--absolute-git-dir')
    if os.path.exists(os.path.join(gitdir, 'index.lock')):
        refuse('%s/index.lock exists; it is never deleted. Resolve the other git process first.' % gitdir)
    branch = git(ws, 'symbolic-ref', '--quiet', '--short', 'HEAD', check=False)
    if not branch:
        refuse('detached HEAD: a step is committed on its own branch')
    if branch in cfg['protected_branches'] or any(re.search(p, branch) for p in cfg['protected_patterns']):
        refuse('branch %s is protected or frozen; commit the step on its own branch' % branch)
    status = git(ws, 'status', '--porcelain=v1', '--untracked-files=all', '-z')
    paths = [e[3:] for e in status.split('\0') if len(e) > 3 and e[0] != 'D' and e[1] != 'D']
    hits = []
    for p in paths:
        f = os.path.join(ws, p)
        if p in cfg['secret_allow_files'] or not os.path.isfile(f) or os.path.getsize(f) > cfg['secret_scan_max_bytes']:
            continue
        t = open(f, 'rb').read().decode('utf-8', 'replace')
        hits += ['%s (pattern %d)' % (p, i) for i, pat in enumerate(cfg['secret_patterns']) if re.search(pat, t)]
    if hits:
        refuse('possible secret in %s; secrets never enter the repository. Remove it or move it to the secret store.' % ', '.join(hits))
    remote_head = (git(ws, 'ls-remote', cfg['remote'], 'refs/heads/' + branch).split() or [''])[0]
    local = git(ws, 'rev-parse', 'HEAD')
    if remote_head and remote_head != local and subprocess.run(['git', '-C', ws, 'merge-base', '--is-ancestor', remote_head, local], capture_output=True).returncode:
        refuse('the remote %s has commits this branch lacks; never force-push. Integrate them first.' % branch)  # checked before committing: a refusal changes nothing
    vc = cfg.get('visibility_check')  # the receiving repository must be private (LXM-REQ-000149); command and expected answer are configuration
    if vc:
        url = git(ws, 'remote', 'get-url', cfg['remote'])
        m = re.search(vc['repo_pattern'], url)
        if not m:
            refuse('cannot tell which repository %s is (%s); its visibility must be checked before a push' % (cfg['remote'], url))
        r = subprocess.run([a.replace('{repo}', m.group(1)) for a in vc['command']], capture_output=True, text=True)
        if r.returncode or r.stdout.strip() != vc['expect']:
            refuse('%s is not confirmed private (%s); a push would publish. Make it private first.' % (m.group(1), (r.stdout or r.stderr).strip()[:80] or 'no answer'))
    if dry:
        print('dry run: would commit %d path(s) on %s and push to %s' % (len(paths), branch, cfg['remote'])); return 0
    if paths or status:
        git(ws, 'add', '-A')
        body = msg + ('\n\n' + '\n'.join(cfg['trailers']) if cfg['trailers'] else '')
        git(ws, 'commit', '-q', '-m', body)
    head = git(ws, 'rev-parse', 'HEAD')
    if remote_head != head:
        git(ws, 'push', '-q', '-u', cfg['remote'], 'HEAD:refs/heads/' + branch)
        remote_head = (git(ws, 'ls-remote', cfg['remote'], 'refs/heads/' + branch).split() or [''])[0]
    left = git(ws, 'status', '--porcelain=v1', '--untracked-files=all')
    if left or remote_head != head:
        print('NOT FINISHED: tree clean %s; remote %s equals local %s: %s' % (not left, branch, head[:12], remote_head == head)); return 1
    print('clean and pushed at %s (%s, %s)' % (head, cfg['remote'], branch)); return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except RuntimeError as e:
        print('ERROR: %s' % e); sys.exit(1)

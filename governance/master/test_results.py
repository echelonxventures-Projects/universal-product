"""Summarise one test run into evidence that readiness.py reads (LXM-REQ-000140: every result names the exact SHA tested).
Usage: python3 -I test_results.py --log <run.log> --exit <code> --sha <tested sha> --runtime <runtime> --command <text>
                                  --started <time> --finished <time> --status-after <git status output file> [--config readiness.json] --out <file.json>

The pass and fail markers come from the configuration (readiness.json, "tests"). The summary never decides anything; readiness.py
applies the rule."""
import hashlib, json, os, sys

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)

HERE = os.path.dirname(os.path.abspath(__file__))


def summarise(log_text, exit_code, sha, runtime, command, started, finished, status_after, cfg, log_sha):
    t = cfg['tests']
    lines = log_text.split('\n')
    passed = sum(1 for l in lines if l.lstrip().startswith(t['pass_marker']))
    failed = [l.strip()[:200] for l in lines if l.lstrip().startswith(t['fail_marker'])]
    crashed = [l.strip()[:200] for l in lines if any(m in l for m in t['crash_markers'])]
    return {'sha': sha, 'runtime': runtime, 'command': command, 'started': started, 'finished': finished, 'exit': exit_code,
            'passed': passed, 'failed': len(failed), 'failures': failed[:50], 'crashes': crashed[:20],
            'tree_clean_after': status_after.strip() == '', 'changed_after': [l for l in status_after.split('\n') if l.strip()][:50],
            'log_sha256': log_sha}


def main(argv):
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    need = ('--log', '--exit', '--sha', '--runtime', '--command', '--started', '--finished', '--status-after', '--out')
    if any(not opt(k) for k in need):
        print(__doc__); return 2
    cfg = json.load(open(opt('--config') or os.path.join(HERE, 'readiness.json'), encoding='utf-8'))
    raw = open(opt('--log'), 'rb').read()
    r = summarise(raw.decode('utf-8', 'replace'), int(opt('--exit')), opt('--sha'), opt('--runtime'), opt('--command'), opt('--started'),
                  opt('--finished'), open(opt('--status-after'), encoding='utf-8').read(), cfg, hashlib.sha256(raw).hexdigest())
    json.dump(r, open(opt('--out'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('%s on %s: exit %d, %d passed, %d failed, %d crash lines, tree clean after: %s' % (
        r['command'], r['sha'][:12], r['exit'], r['passed'], r['failed'], len(r['crashes']), r['tree_clean_after']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

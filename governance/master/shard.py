"""Small files (design §1, Level 2): split each register into one file per record plus a generated index, and join them back.
The proof: joining reproduces every register byte for byte, so the Master generated from the shards is identical.
Usage: python3 -I shard.py split <root> <out dir>      python3 -I shard.py join <shard dir> <out dir>
       python3 -I shard.py prove <root>                (split, join, rebuild and compare, in a scratch directory)"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats come from ids.json (LXM-REQ-000240)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assimilate import gate_config  # the external sources resolve against the Master folder
REGISTERS = {'reqs.txt': X(r'@{req}'), 'decisions.txt': X(r'@{dec}'), 'evidence.txt': X(r'@{evd}'), 'trace.txt': X(r'@{req}')}
sha = lambda b: hashlib.sha256(b).hexdigest()


def split(root, out):
    for reg, head in REGISTERS.items():
        text = open(os.path.join(root, reg), encoding='utf-8').read()
        parts = re.split(r'(?m)^(?=%s\b)' % head, text)
        d = os.path.join(out, reg[:-4]); os.makedirs(d, exist_ok=True)
        index = {'register': reg, 'preamble': parts[0], 'records': []}
        for p in parts[1:]:
            rid = re.match(head, p).group(0)[1:]
            open(os.path.join(d, rid + '.txt'), 'w', encoding='utf-8').write(p)
            index['records'].append({'id': rid, 'file': rid + '.txt', 'bytes': len(p.encode()), 'sha256': sha(p.encode())})
        json.dump(index, open(os.path.join(d, X('{@shard_index_json}')), 'w', encoding='utf-8'), indent=1)


def join(shards, out):
    for reg in REGISTERS:
        d = os.path.join(shards, reg[:-4]); index = json.load(open(os.path.join(d, X('{@shard_index_json}')), encoding='utf-8'))
        body = []
        for r in index['records']:
            p = open(os.path.join(d, r['file']), encoding='utf-8').read()
            if sha(p.encode()) != r['sha256']:
                raise SystemExit('shard %s does not match its index' % r['file'])
            body.append(p)
        open(os.path.join(out, reg), 'w', encoding='utf-8').write(index['preamble'] + ''.join(body))


def prove(root):
    t = tempfile.mkdtemp(prefix='lxm-shard-'); sh, rb = os.path.join(t, 'registry'), os.path.join(t, 'rebuilt')
    shutil.copytree(root, rb, ignore=shutil.ignore_patterns('__pycache__', X('{@out_dir}')))
    for reg in REGISTERS:
        os.remove(os.path.join(rb, reg))
    split(root, sh); join(sh, rb)
    same = {reg: open(os.path.join(root, reg), 'rb').read() == open(os.path.join(rb, reg), 'rb').read() for reg in REGISTERS}
    g = gate_config(root)
    os.makedirs(os.path.join(rb, X('{@out_dir}')))
    subprocess.run([sys.executable, '-I', os.path.join(rb, X('{@build_py}')), g['src2'], g['src3'], os.path.join(rb, X('{@out_dir}'))], check=True, capture_output=True)
    master = open(os.path.join(root, X('{@out_dir}'), X('{@master_md}')), 'rb').read() == open(os.path.join(rb, X('{@out_dir}'), X('{@master_md}')), 'rb').read()
    sizes = [r['bytes'] for reg in REGISTERS for r in json.load(open(os.path.join(sh, reg[:-4], X('{@shard_index_json}'))))['records']]
    files = len(sizes)
    shutil.rmtree(t, ignore_errors=True)
    return same, master, files, max(sizes), sum(sizes) // files


if __name__ == '__main__':
    if sys.argv[1] == 'split':
        split(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'join':
        join(sys.argv[2], sys.argv[3])
    else:
        same, master, files, mx, avg = prove(sys.argv[2])
        print('%d record files (largest %d bytes, average %d); registers rejoined byte-identical: %s; Master rebuilt from shards identical: %s' % (
            files, mx, avg, ', '.join('%s %s' % (k, 'yes' if v else 'NO') for k, v in same.items()), master))
        sys.exit(0 if all(same.values()) and master else 1)

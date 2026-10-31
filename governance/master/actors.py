"""Roles, not names (LXM-REQ-000239): resolve {role:<id>} references against the actor registry (actors.json) and match a
remote to its host in the host registry (hosts.json). No agent, tool, person or host is named in this file."""
import json, os, re, sys
sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)

HERE = os.path.dirname(os.path.abspath(__file__))


def registry(name, root=HERE):
    return json.load(open(os.path.join(root, name), encoding='utf-8'))


def role(rid, root=HERE):
    a = registry('actors.json', root)
    r = a['roles'][rid]
    return '%s (%s)' % (a['actors'][r['actor']]['label'], r['describes'])


def actor(rid=None, root=HERE):
    """The actor holding a role: the one named, else the role in the configured environment variable, else the default role."""
    a = registry('actors.json', root)
    rid = rid or os.environ.get(a['actor_env']) or a['default_role']
    return a['actors'][a['roles'][rid]['actor']]


def resolve(obj, root=HERE):
    """Replace every {role:<id>} in strings, lists and objects; an unknown role fails loudly."""
    if isinstance(obj, str):
        return re.sub(r'\{role:([\w-]+)\}', lambda m: role(m.group(1), root), obj)
    if isinstance(obj, list):
        return [resolve(x, root) for x in obj]
    if isinstance(obj, dict):
        return {k: resolve(v, root) for k, v in obj.items()}
    return obj


def host_for(url, root=HERE):
    """(host id, host entry, repository) for a remote URL, or (None, None, None) when no registered host matches."""
    for hid, h in registry('hosts.json', root)['hosts'].items():
        m = re.search(h['url_pattern'], url)
        if m:
            return hid, h, m.group(1)
    return None, None, None

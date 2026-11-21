#!/usr/bin/env python3
"""UCOS-UGA-001 — Universal Governance Assimilation Engine.

Brings every version-controlled object that is NOT a corpus document under the
SAME constitutional control the corpus already has: identity, ownership,
lifecycle, dependency closure, evidence boundary, audit history, validation.

WHY THIS EXISTS
---------------
`00-BOOK/tools/config.py::INCLUDE_EXTENSIONS` is (.md, .txt, .docx, .json). The
registration boundary is document-only, so at the time of authoring 1936
version-controlled executable and configuration objects — including all 29
producers named by the generated-artifact registry — had no universal identity,
no owner and no lifecycle. The corpus governed its artifacts by naming engines
that were themselves anonymous.

The identity authority, audit universe, evidence universe and relationship graph
already existed and already worked. What was missing was a TERM for a thing that
executes rather than a thing that is read. This engine adds the object class, not
a parallel government.

ONE IDENTITY AUTHORITY
----------------------
Identities are minted from `00-BOOK/DATA/id-ledger.json` using the SAME
`category_seq` counter as the corpus, into an append-only `by_object` map. This
is the construction EXEC-REG-001 already established for `by_execution`. No page
range is consumed: pages are a BOOK concept, so `page_cursor` is never touched
and the corpus page layout is bit-for-bit unaffected. `ukb.py cmd_build` iterates
the document eligibility universe (never the ledger), and `load_ledger` preserves
unknown keys, so `by_object` is invisible to the corpus transaction by
construction rather than by convention.

DETERMINISM
-----------
No output contains a wall clock. Every timestamp emitted is a `first_seen` frozen
in the append-only ledger at mint time. A second run with no repository change is
a no-op on disk, which is what makes Phase-8 fixed point and Phase-9 pristine
clone checkable by plain byte comparison.

USAGE
    uga_engine.py gate    verify invariants; mutate nothing; exit 1 on violation
    uga_engine.py stats   print the current measured state
    uga_engine.py run     GOVERNED / IRREVERSIBLE. Allocates permanent identity into the
                          append-only 00-BOOK/DATA/id-ledger.json. This is a
                          CORPUS_REGISTRATION-class mutation reserved for REG-AUTO-001
                          authorization (00-BOOK/DATA/mutation-governance-boundary.json).
                          It is NOT an operator remediation: diagnose with `gate`, obtain
                          authorization, and let the authorized transaction allocate.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

# The identity-ledger write chokepoint (UCOS-LEDGER-AUTHORITY-001). It used to live under
# 00-BOOK/tools and be imported by explicit path, because that directory is a script
# directory rather than an importable package. `python_imports` resolved that edge, but Ω-3's
# import graph could not, and the chokepoint every irreversible allocation passes through was
# therefore measured as unreachable. It is now a named package; the import below is an
# ordinary one that every graph in the repository can resolve. Only the root needs adding to
# sys.path, because this engine is invoked as a script rather than as a module.
sys.path.insert(0, REPO)
from engine import ledger_authority as LA  # noqa: E402

DECLARATION = os.path.join(HERE, "uga-declaration.json")
LEDGER_PATH = os.path.join(REPO, "00-BOOK", "DATA", "id-ledger.json")
ARTIFACTS_PATH = os.path.join(REPO, "00-BOOK", "DATA", "artifacts.json")
GENREG_PATH = os.path.join(REPO, "00-BOOK", "DATA", "generated-artifact-registry.json")
EVIDENCE_PATH = os.path.join(REPO, "00-BOOK", "DATA", "evidence-universe.json")
OBSERVATION_PATH = os.path.join(REPO, "00-BOOK", "DATA", "observation-universe.json")
CAA_PATH = os.path.join(REPO, "00-BOOK", "DATA",
                        "constitutional-authority-alignment.json")

OUT = {
    "inventory":    os.path.join(HERE, "00-EXISTENCE-INVENTORY.json"),
    "executables":  os.path.join(HERE, "01-EXECUTABLE-OBJECT-REGISTRY.json"),
    "universal":    os.path.join(HERE, "02-UNIVERSAL-OBJECT-REGISTRY.json"),
    "audit":        os.path.join(HERE, "03-AUDIT-UNIVERSE.json"),
    "graph":        os.path.join(HERE, "04-RELATIONSHIP-GRAPH.json"),
    "invariants":   os.path.join(HERE, "05-GOVERNANCE-INVARIANTS.json"),
    "observation":  os.path.join(HERE, "06-SELF-OBSERVATION.json"),
    "certification": os.path.join(HERE, "07-CERTIFICATION.json"),
    "observations": os.path.join(HERE, "08-OBSERVATION-REGISTRY.json"),
    "dashboard":    os.path.join(HERE, "00-UGA-DASHBOARD.md"),
    "obs_audit":    os.path.join(REPO, "00-BOOK", "DATA",
                                 "canonical-observation-audit.json"),
}

#: PHASE 1 — the signatures by which a mutable observation is recognised inside a
#: canonical artifact. Distinct from `forbidden_canonical_keys`, which is the ENFORCED
#: scoped rule set: this is the wider DETECTION sweep that finds candidates the rules do
#: not yet name, so an unidentified leak is a measurement rather than a surprise.
OBSERVATION_SIGNATURES: dict[str, str] = {
    "residue": "EXECUTION_RESIDUE",
    "unattributed": "EXECUTION_RESIDUE",
    "residue_total": "EXECUTION_RESIDUE",
    "unattributed_residue": "EXECUTION_RESIDUE",
    "dirty_entries": "WORKING_TREE_STATE",
    "dirty_entries_outside_generated": "WORKING_TREE_STATE",
    "contamination_entries": "WORKING_TREE_STATE",
    "worktree_entries": "WORKING_TREE_STATE",
    "working_tree": "WORKING_TREE_STATE",
    "untracked": "WORKING_TREE_STATE",
    "modified": "WORKING_TREE_STATE",
    "deleted": "WORKING_TREE_STATE",
    "generated_at": "ENVIRONMENT_STATE",
    "timestamp": "ENVIRONMENT_STATE",
    "elapsed": "ENVIRONMENT_STATE",
    "duration": "ENVIRONMENT_STATE",
    "coverage": "ENVIRONMENT_STATE",
    "total_coverage": "ENVIRONMENT_STATE",
}

# Trees whose Python packages participate in intra-repository import resolution.
CODE_ROOTS = ("engine", "platform", "service", "data", "application",
              "infrastructure", "intelligence", "realization", "scripts")

CONFIG_EXT = (".yml", ".yaml", ".toml", ".cfg", ".ini", ".gitignore")
EXEC_EXT = (".py", ".sh")


# ---------------------------------------------------------------------------
# io helpers
# ---------------------------------------------------------------------------
def _load(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        if default is None:
            raise
        return default


def _dump(path, obj):
    """Write pretty deterministic JSON. Returns True when the bytes changed."""
    text = json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    return _write_text(path, text)


def _write_text(path, text):
    try:
        with open(path, encoding="utf-8") as fh:
            if fh.read() == text:
                return False
    except FileNotFoundError:
        pass
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return True


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(abspath: str) -> str | None:
    try:
        with open(abspath, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def _digest_of(obj) -> str:
    """Stable content digest of a JSON-able structure."""
    return _sha256_bytes(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode())


def _git_ls():
    """The repository artifact boundary, as version control declares it.

    `-z` is mandatory, not stylistic: without it git QUOTES any path containing a
    non-ASCII byte, and 116 paths in this repository carry Ω/∞ in their names. The
    quoted form is a different string, so those objects would be minted identities
    under a name no lookup could ever match — an anonymous object wearing a
    plausible label, which is the exact failure this programme exists to forbid.
    """
    out = subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
        ["git", "-C", REPO, "ls-files", "-z", "--cached",  # noqa: S607 — resolved from PATH, as CI does
         "--exclude-standard"],
        capture_output=True, text=True, check=False)
    if out.returncode != 0:
        raise SystemExit("UGA: not a git work tree — the repository artifact boundary "
                         "is undefined. Refusing to guess (fails closed).")
    return sorted(p for p in out.stdout.split("\0") if p)


# ---------------------------------------------------------------------------
# EPOCH 0 — Existence Discovery
# ---------------------------------------------------------------------------
def classify_object(rel: str, registered_docs: set, generated_paths: set) -> tuple[str, str]:
    """(object_class, lifecycle) — TOTAL over the version-controlled boundary.

    Every branch returns; the final branch is unconditional. 'UNKNOWN' is therefore
    structurally unreachable, which is what makes the Epoch-0 success condition
    (unknown_objects == 0) a property of the classifier rather than a lucky
    measurement of today's file set.
    """
    lifecycle = "GENERATED" if rel in generated_paths else "AUTHORED"

    if rel in registered_docs:
        return "DOCUMENT_ARTIFACT", lifecycle
    if rel.startswith(("00-BOOK/tools/", "00-BOOK/DATA/")):
        return "TOOLING_OBJECT", lifecycle
    if rel.endswith(".py") or rel.endswith(".sh"):
        base = os.path.basename(rel)
        is_test = ("/tests/" in f"/{rel}" or rel.startswith("tests/")
                   or base.startswith("test_") or base.endswith("_test.py"))
        return ("TEST_OBJECT" if is_test else "EXECUTABLE_OBJECT"), lifecycle
    if rel.endswith(CONFIG_EXT):
        return "CONFIGURATION_OBJECT", lifecycle
    if rel.endswith(".json"):
        return "DATA_OBJECT", lifecycle
    # Unconditional terminal branch: a readable document that the corpus registry
    # does NOT carry — Operational Memory under 00-MASTER/ and the generated
    # projections under 00-BOOK/CONTROL-TOWER, REGISTRIES, VOLUMES and PORTAL.
    # Excluded from CORPUS REGISTRATION by declared authority, which is a statement
    # about which register lists them — never a licence to exist anonymously.
    return "EXCLUDED_DOCUMENT", lifecycle


def derive_owner(rel: str) -> str:
    """TOTAL ownership function. The last rule is unconditional."""
    parts = rel.split("/")
    if rel.startswith("00-BOOK/tools/") or rel.startswith("00-BOOK/DATA/"):
        return "UCOS-UKB-TOOLING"
    if parts[0] == "00-MASTER" and len(parts) > 2:
        return parts[1]
    if len(parts) > 2:
        return f"{parts[0]}/{parts[1]}"
    if len(parts) == 2:
        return parts[0]
    return "UCOS-REPOSITORY-ROOT"


def epoch0_discovery(paths, registered_docs, generated_paths):
    objects = []
    for rel in paths:
        klass, lifecycle = classify_object(rel, registered_docs, generated_paths)
        objects.append({
            "path": rel,
            "object_class": klass,
            "lifecycle": lifecycle,
            "owner": derive_owner(rel),
        })
    return objects


# ---------------------------------------------------------------------------
# EPOCH 1 — Universal Identity Authority (shared ledger, append-only)
# ---------------------------------------------------------------------------
ID_CATEGORY = {
    "EXECUTABLE_OBJECT": "ENGINE",
    "TEST_OBJECT": "TESTOBJ",
    "CONFIGURATION_OBJECT": "CONFIG",
    "TOOLING_OBJECT": "TOOLING",
    "DATA_OBJECT": "DATAOBJ",
    "EXCLUDED_DOCUMENT": "EXDOC",
}


def epoch1_identity(objects, ledger, mint: bool, now: str):
    """Mint a universal identity for every object of a governed class.

    Shares the corpus `category_seq` counter. Consumes NO page range. Append-only:
    an existing entry is returned untouched, so an identity is permanent and is
    never reissued to a different path.
    """
    by_object = ledger.setdefault("by_object", {})
    seq = ledger.setdefault("category_seq", {})
    doc_ids = ledger.get("by_path", {})

    minted, anonymous = [], []
    for o in objects:
        rel = o["path"]
        if o["object_class"] == "DOCUMENT_ARTIFACT":
            # Governed by UMB-IMP-001. Read its identity; never mint one here.
            entry = doc_ids.get(rel)
            o["universal_id"] = entry["universal_id"] if entry else None
            o["identity_authority"] = "UMB-IMP-001"
            if not o["universal_id"]:
                anonymous.append(rel)
            continue

        o["identity_authority"] = "UCOS-UGA-001"
        existing = by_object.get(rel)
        if existing:
            o["universal_id"] = existing["universal_id"]
            o["first_seen"] = existing["first_seen"]
            continue
        if not mint:
            o["universal_id"] = None
            anonymous.append(rel)
            continue
        cat = ID_CATEGORY[o["object_class"]]
        n = seq.get(cat, 0) + 1
        seq[cat] = n
        uid = f"UCOS-{cat}-{n:06d}"
        by_object[rel] = {
            "universal_id": uid,
            "object_class": o["object_class"],
            "category": cat,
            "first_seen": now,
        }
        o["universal_id"] = uid
        o["first_seen"] = now
        minted.append(rel)

    # RETIRED: minted previously, no longer carried by version control. Identity is
    # retained and never reissued (append-only).
    live = {o["path"] for o in objects}
    retired = sorted(p for p in by_object if p not in live)
    return minted, anonymous, retired


# ---------------------------------------------------------------------------
# EPOCH 4 (computed early — the registry embeds dependencies)
# ---------------------------------------------------------------------------

def _module_name(rel: str) -> str | None:
    if not rel.endswith(".py"):
        return None
    mod = rel[:-3].replace("/", ".")
    if mod.endswith(".__init__"):
        mod = mod[: -len(".__init__")]
    return mod


def build_import_index(paths):
    index = {}
    for rel in paths:
        mod = _module_name(rel)
        if mod and rel.split("/")[0] in CODE_ROOTS:
            index[mod] = rel
    return index


#: WHICH SUFFIXES HAVE AN EDGE DERIVER, and how a language acquires one.
#:
#: This was `if rel.endswith(".py")` at the single call site, which meant a file in any other
#: language could never carry a dependency edge — not because its dependencies are unknowable,
#: but because nothing was ever asked. The consequence reached further than this engine: the
#: impact selector derives its bounded suffixes from which suffixes actually carry edges, so a
#: Rust file escalated every change to FULL forever, and no amount of Rust tooling could have
#: changed that while this line read `.py`.
#:
#: REGISTERING A DERIVER IS HOW A LANGUAGE BECOMES VISIBLE (UCKP-ART-08, UCKP-ART-17: admitted by
#: registration, never by amendment). A deriver takes the same four arguments and returns
#: repository-relative paths that RESOLVE to tracked files; edges to anything outside the
#: repository boundary are not repository dependencies and are not emitted.
EDGE_DERIVERS: dict[str, object] = {}


def register_edge_deriver(suffix: str, deriver) -> None:
    """Admit a language to dependency analysis. Idempotent; last registration wins."""
    EDGE_DERIVERS[suffix] = deriver


def artifact_type_of(rel: str, abspath: str) -> str:
    """What this artifact IS, asked of the entity rather than of its filename.

    THE SUFFIX IS THE LAST RESORT RULE, NOT THE FIRST. engine/omega_infinite/classification.py
    declares four rules in precedence order — Ω∞-T-01 provider-declared, Ω∞-T-02 content
    interpreter, Ω∞-T-03 content structure, Ω∞-T-04 suffix — and the first version of the deriver
    registry keyed on the fourth. A Python file with no `.py` extension and a
    `#!/usr/bin/env python3` line is typed PYTHON by rule Ω∞-T-02 and would have carried no
    dependency edges, because its NAME did not end the right way.

    Measured when this changed: no tracked file is currently reclassified by asking properly —
    zero non-`.py` files carry a Python shebang — so this moves no edge today. It is structural,
    and the structure is the point: a provider that declares its artifacts' types makes them
    derivable without anyone editing a table of suffixes.

    Falls back to the suffix when the classifier cannot be reached, because this engine must run
    in a checkout where the classification package is absent; a fallback that degrades to the
    previous behaviour is the honest failure mode.
    """
    try:
        from engine.omega_infinite.artifact import Artifact, Location
        from engine.omega_infinite.classification import default_pipeline
    except ImportError:  # pragma: no cover - classification package absent
        return os.path.splitext(rel)[1]
    try:
        with open(abspath, encoding="utf-8", errors="surrogateescape") as handle:
            content = handle.read(4096)
    except OSError:  # pragma: no cover - unreadable file
        content = None
    artifact = Artifact(identifier=rel, location=Location("uga", rel, ""))
    return default_pipeline().classify(artifact, content).artifact_type.name


def derive_edges(rel: str, abspath: str, index: dict, tracked: set) -> list:
    """Dependency edges for one object, from whichever deriver claims its TYPE.

    A type nobody claims yields no edges — the same answer the hardcoded branch gave, reached
    because nothing derives them rather than because the engine declined to ask.
    """
    deriver = EDGE_DERIVERS.get(artifact_type_of(rel, abspath))
    return list(deriver(abspath, rel, index, tracked)) if deriver else []


def python_imports(abspath: str, rel: str, index: dict, tracked: set) -> list[str]:
    """Intra-repository import edges, resolved to real paths.

    Only edges that RESOLVE to a version-controlled module are emitted. Stdlib and
    third-party imports are outside the repository boundary and are not repository
    dependencies.

    Two resolution modes, because this repository uses both. Package-qualified
    imports (`from engine.knowledge import seed`) resolve through the module index.
    SCRIPT-STYLE SIBLING imports (`import config as C`, how 00-BOOK/tools and the
    00-MASTER engines are written) resolve against the importing file's own
    directory — without this, the governance tooling's own dependency edges are
    invisible, and a dependency nobody can see is the hidden dependency Epoch 4
    exists to eliminate.
    """
    try:
        with open(abspath, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=rel)
    except (OSError, SyntaxError, ValueError):
        return []

    pkg = (_module_name(rel) or "").rsplit(".", 1)[0]
    here = os.path.dirname(rel)
    found = set()

    def resolve(mod: str):
        if not mod:
            return
        if mod in index:
            found.add(index[mod])
            return
        # `from pkg.mod import name` where name is itself a module
        parent = mod.rsplit(".", 1)[0]
        if parent in index:
            found.add(index[parent])
            return
        # script-style sibling module in the importing file's own directory
        top = mod.split(".")[0]
        for cand in (f"{top}.py", os.path.join(top, "__init__.py")):
            sib = os.path.join(here, cand) if here else cand
            sib = os.path.normpath(sib)
            if sib in tracked and sib != rel:
                found.add(sib)
                return
        # corpus tooling reached through an explicit sys.path insert. 00-BOOK/tools is a
        # script directory, not a CODE_ROOT package, so the module index cannot carry it
        # and the sibling rule above cannot see it from another directory. Checked LAST,
        # so a module of the same name in the importer's own directory still wins. Without
        # this, an engine routing its ledger write through `ledger_authority` would carry
        # an unresolved edge — the invisible dependency Epoch 4 exists to eliminate.
        for cand in (f"{top}.py", os.path.join(top, "__init__.py")):
            tool = os.path.normpath(os.path.join("00-BOOK", "tools", cand))
            if tool in tracked and tool != rel:
                found.add(tool)
                return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                resolve(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:                      # relative import
                base = pkg.split(".")
                up = node.level - 1
                base = base[: len(base) - up] if up else base
                target = ".".join([*base, node.module] if node.module else base)
            else:
                target = node.module or ""
            resolve(target)
            if node.module or node.level:
                for a in node.names:
                    resolve(f"{target}.{a.name}")
    return sorted(found)


# ---------------------------------------------------------------------------
# EPOCH 2/3 — Universal Object Registry + evidence boundary
# ---------------------------------------------------------------------------
EVIDENCE_FOR_CLASS = {
    # Which evidence class a governance record about this object belongs to.
    # Closed set from UCOS-EVIDENCE-UNIVERSE-001; no sixth class is created.
    "EXECUTABLE_OBJECT": "VALIDATION",
    "TEST_OBJECT": "VALIDATION",
    "CONFIGURATION_OBJECT": "VALIDATION",
    "TOOLING_OBJECT": "VALIDATION",
    "DATA_OBJECT": "VALIDATION",
    "DOCUMENT_ARTIFACT": "VALIDATION",
    "EXCLUDED_DOCUMENT": "VALIDATION",
}



#: Keyed by ARTIFACT TYPE, not suffix: the type is what the entity is, decided by the four
#: declared classification rules with the filename consulted last. A second language is a
#: second call to this, and a provider declaring its own types needs no call at all.
register_edge_deriver("PYTHON", python_imports)

def epoch2_registry(objects, index, producer_of, consumers_of, decl, tracked):
    # This engine's OWN emitted surfaces. Once they are version-controlled they are
    # objects like any other and MUST hold identity — but their content_hash is
    # deliberately null, because a file cannot contain its own hash: recording it
    # would change the bytes, which changes the hash, a self-reference with no
    # fixpoint. The repository already met this exact relation with the UCOS-RIE-001
    # outputs and resolved it by removing them from registration; identity is kept
    # here and only the unsatisfiable field is withheld, which is the narrower cut.
    own_surfaces = {os.path.relpath(p, REPO) for p in OUT.values()}

    entries = []
    for o in objects:
        rel = o["path"]
        abspath = os.path.join(REPO, rel)
        deps = derive_edges(rel, abspath, index, tracked)

        governed = o["object_class"] != "DOCUMENT_ARTIFACT"
        entries.append({
            "universal_id": o["universal_id"],
            "path": rel,
            "object_class": o["object_class"],
            "owner": o["owner"],
            "producer": producer_of.get(rel, "HUMAN_AUTHORED"),
            "identity_authority": o["identity_authority"],
            "lifecycle": o["lifecycle"],
            "dependencies": deps,
            "produces": sorted(consumers_of.get(rel, [])),
            "evidence_class": EVIDENCE_FOR_CLASS[o["object_class"]],
            "evidence_boundary": "NON_CANONICAL",
            "validation_contract": (
                "UCOS-UGA-001 §UGA-INV-01..10" if governed else "UMB-IMP-001 ENFORCEMENT_GATES"),
            "certification_status": "GOVERNED",
            "content_hash": None if rel in own_surfaces else _sha256_file(abspath),
            "content_hash_withheld": (
                "SELF_REFERENTIAL — this engine emits this surface; a file cannot "
                "contain its own hash." if rel in own_surfaces else None),
            "first_seen": o.get("first_seen"),
        })
    entries.sort(key=lambda e: e["path"])
    return entries


# ---------------------------------------------------------------------------
# Observation Universe — identity for what was SEEN, separate from what IS
# ---------------------------------------------------------------------------
def observation_key(observer: str, subject: str, kind: str) -> str:
    return f"{observer}::{subject}::{kind}"


def mint_observation(ledger, observer: str, subject: str, kind: str, mint: bool, now: str):
    """Return the stable Universal Identity of an observation.

    VALUE-INDEPENDENT BY CONSTRUCTION. The key is (observer, subject, kind) and the
    observed value is not an input, so the identity a canonical artifact carries never
    moves when the observation does. That is the whole mechanism: the canonical bytes
    hold still while the measurement stays free to change, and nothing is hidden —
    the value is preserved on an evidence surface addressed by this id.

    Minted from the ONE identity authority (shared category_seq, category OBS) into the
    append-only `by_observation` map, alongside `by_path` and `by_object`.
    """
    by_obs = ledger.setdefault("by_observation", {})
    key = observation_key(observer, subject, kind)
    existing = by_obs.get(key)
    if existing:
        return existing["observation_id"]
    if not mint:
        return None
    seq = ledger.setdefault("category_seq", {})
    n = seq.get("OBS", 0) + 1
    seq["OBS"] = n
    oid = f"UCOS-OBS-{n:06d}"
    by_obs[key] = {
        "observation_id": oid,
        "observer": observer,
        "subject": subject,
        "kind": kind,
        "first_seen": now,
    }
    return oid


#: The observations this repository's engines are KNOWN to take. Declaring them here
#: (rather than discovering them) is deliberate: an observation that no one declared is
#: an anonymous observation, and OBS-INV-01 forbids those. Each entry is minted an
#: identity, so a canonical artifact has a stable id to reference in place of a value.
DECLARED_OBSERVATIONS: tuple[tuple[str, str, str], ...] = (
    ("UCOS-AEE-001", "actuator-execution-residue", "EXECUTION_RESIDUE"),
    ("UCOS-AEE-001", "unattributed-residue", "EXECUTION_RESIDUE"),
    ("UCOS-RIB-001", "dirty-entries-outside-generated", "WORKING_TREE_STATE"),
    ("UCOS-RIB-001", "working-tree-cleanliness-verdict", "WORKING_TREE_STATE"),
    ("UCCEP-000005", "worktree-entries", "WORKING_TREE_STATE"),
    ("intelligence/realization", "materialization-action", "MATERIALIZATION_ACTION"),
    ("P0-FINAL-CLOSURE-002", "concurrent-writer-detection", "WORKING_TREE_STATE"),
)


def epoch_observation_universe(ledger, obs_decl, mint: bool, now: str):
    """Mint identity for every declared observation; return the registry rows."""
    kinds = set(obs_decl["observation_kinds"])
    rows, anonymous, undeclared_kind = [], [], []
    for observer, subject, kind in DECLARED_OBSERVATIONS:
        if kind not in kinds:
            undeclared_kind.append(f"{observer}::{subject}::{kind}")
            continue
        oid = mint_observation(ledger, observer, subject, kind, mint, now)
        if not oid:
            anonymous.append(observation_key(observer, subject, kind))
            continue
        spec = obs_decl["observation_kinds"][kind]
        rows.append({
            "observation_id": oid,
            "observer": observer,
            "subject": subject,
            "kind": kind,
            "canonical_admissibility": spec["canonical_admissibility"],
            "evidence_class": spec["evidence_class"],
            "evidence_surface": f"00-MASTER/{observer}/evidence/"
                                if observer.startswith(("UCOS-", "UCCEP", "P0-")) else observer,
            "value_recorded_here": False,
        })
    rows.sort(key=lambda r: r["observation_id"])
    return rows, anonymous, undeclared_kind


def scan_canonical_for_observation_values(obs_decl):
    """OBS-INV-02 — find observation VALUES embedded in canonical artifacts.

    Structural, deterministic, and declaration-driven: the key names come from the
    registry's `forbidden_canonical_keys`, so closing a newly-found leak is one appended
    entry in DATA and needs no code change.

    A key carrying a well-formed observation id is COMPLIANT — that is the migration
    target, not a violation. A key carrying anything else is the value itself.
    """
    id_shape = re.compile(obs_decl["observation_id_shape"])
    rules = obs_decl["forbidden_canonical_keys"]["rules"]
    findings = []

    def walk(node, path, rel, forbidden):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in forbidden:
                    if isinstance(v, str) and id_shape.match(v):
                        continue                      # a reference — compliant
                    if isinstance(v, list) and not v:
                        # An empty list still ENCODES the observation: it is the value
                        # "nothing was seen", and it becomes non-empty when something is.
                        findings.append(f"{rel}: {path}.{k} carries an observation value "
                                        f"(empty list — presence still encodes the reading)")
                    else:
                        findings.append(f"{rel}: {path}.{k} carries an observation value "
                                        f"({forbidden[k]})")
                walk(v, f"{path}.{k}", rel, forbidden)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]", rel, forbidden)

    for rel in obs_decl["canonical_scope"]["paths"]:
        abspath = os.path.join(REPO, rel)
        if not os.path.isfile(abspath):
            findings.append(f"{rel}: declared canonical artifact is absent (fails closed)")
            continue
        if not rel.endswith(".json"):
            continue                                  # markdown renderings follow their model
        forbidden = {r["key"]: r["kind"] for r in rules if r["artifact"] == rel}
        if not forbidden:
            continue
        try:
            with open(abspath, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError) as exc:
            findings.append(f"{rel}: unreadable, so it cannot be cleared ({exc})")
            continue
        walk(doc, "$", rel, forbidden)
    return findings


def canonical_observation_audit(obs_decl, genreg, ledger):
    """PHASE 1 — every canonical artifact that carries a mutable observation.

    Sweeps the WHOLE declared canonical set (every CANONICAL entry in the
    generated-artifact registry), not just the enforced scope, so nothing stays
    unidentified. A site already migrated to an observation id is reported as REMEDIATED
    rather than omitted — the audit records the state of the leak, not merely the ones
    still open.
    """
    id_shape = re.compile(obs_decl["observation_id_shape"])
    enforced = {(r["artifact"], r["key"]) for r in
                obs_decl["forbidden_canonical_keys"]["rules"]}
    by_key = {}
    for rec in (ledger.get("by_observation") or {}).values():
        by_key.setdefault(rec["observer"], []).append(rec["observation_id"])

    rows = []
    seq = 0
    for entry in genreg["entries"]:
        if entry.get("canonical_identity_role") != "CANONICAL":
            continue
        rel = entry["canonical_path"]
        if not rel.endswith(".json"):
            continue
        abspath = os.path.join(REPO, rel)
        try:
            with open(abspath, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError):
            continue

        hits: dict[str, tuple[str, bool]] = {}

        def walk(node, path):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k in OBSERVATION_SIGNATURES:
                        migrated = isinstance(v, str) and bool(id_shape.match(v))
                        prev = hits.get(k)
                        # A key is only REMEDIATED if EVERY occurrence is a reference.
                        hits[k] = (f"{path}.{k}",
                                   migrated if prev is None else (prev[1] and migrated))
                    walk(v, f"{path}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{path}[{i}]")

        walk(doc, "$")
        for key, (where, migrated) in sorted(hits.items()):
            seq += 1
            kind = OBSERVATION_SIGNATURES[key]
            owner = entry.get("owner") or "UNKNOWN"
            rows.append({
                "object_id": f"COA-{seq:06d}",
                "artifact": rel,
                "producer": entry.get("producer") or "UNDECLARED",
                "observation_type": kind,
                "current_location": where,
                "classification": (
                    "REMEDIATED — carries an observation identity, not a reading"
                    if migrated else
                    "MUTABLE OBSERVATION IN CANONICAL IDENTITY"
                    if (rel, key) in enforced else
                    "CANDIDATE — signature present, not yet under an enforced rule"),
                "enforced_by_rule": (rel, key) in enforced,
                "remediation": (
                    "none — already an observation reference" if migrated else
                    f"replace the reading with the {owner} observation identity and write "
                    f"the value to that programme's evidence surface"),
                "observation_identities_available": sorted(by_key.get(owner, [])),
            })
    return rows


# ---------------------------------------------------------------------------
# UNIVERSAL OBSERVATION LINEAGE BOUNDARY — UCOS-OBSERVATION-UNIVERSE-001
#
# "Observation influence must never enter canonical identity, directly or through
# derived values."
#
# The three guards that existed before this — OBS-INV-02 (declared keys), OBS-INV-07
# (signature sweep) and RIB's own strip (_WORKING_TREE_MEASURES) — are the SAME KIND of
# instrument: a vocabulary of leak NAMES. None of the six values that broke Phase 8 is
# spelled like a leak; `gates_passed` is a perfectly innocent name for a contaminated
# number. A name-based test can only find the leaks someone already thought of.
#
# So the boundary is measured two ways, neither of them lexical, and neither of them a
# new pipeline:
#
#   OBS-INV-11  DIFFERENTIAL. Hold the commit fixed, vary a declared observation source,
#               require the canonical projection to be byte-identical. It must EXECUTE a
#               producer's projection function, which this engine may not do — it is
#               stdlib-only so the constitutional gate workflows can run it, and running
#               producers from here would make it a second execution engine. It is
#               measured in the pytest stage of verify.sh, the same single pipeline.
#   OBS-INV-12  Every producer holding canonical output declares the observation sources
#               it actually reads. Measured HERE, by reading the producer's source with
#               docstrings and comments removed — because three producers carry the words
#               `coverage.xml` in prose describing a leak UCOS-CL-005 already closed, and
#               a guard that cannot tell prose from a call site cries wolf.
#   OBS-INV-13  Every canonical artifact proves its ancestry: the transitive closure of
#               its input_closure, with every ancestor classified.
# ---------------------------------------------------------------------------
def _code_only(source: str) -> str:
    """``source`` reduced to the string literals that could be a READ.

    Two positions are blanked, both on the same principle: a token a module DECLARES is
    not a token it reads.

      * a docstring — three producers carry `coverage` prose describing a leak
        UCOS-CL-005 already closed, and reading that as a call site is a false accusation;
      * a string used as a DICTIONARY-LITERAL KEY — `{"total_coverage": ...}` names a
        term; `data["total_coverage"]` reads one. The first is a declaration and is
        blanked, the second is a Subscript and survives, which is what lets this engine
        hold the detection vocabulary it is itself measured against.

    Everything else stays, because `"--porcelain"` inside an argv list IS the read this
    invariant exists to find. Blanking is span-precise and preserves line numbering, so a
    future line-number report stays truthful.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    spans: list[ast.Constant] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            spans.extend(
                key for key in node.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            )
            continue
        if not isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef
                          | ast.AsyncFunctionDef):
            continue
        body = getattr(node, "body", None)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            if isinstance(body[0].value.value, str):
                spans.append(body[0].value)

    lines = source.splitlines()
    for constant in spans:
        start, end = constant.lineno - 1, (constant.end_lineno or constant.lineno) - 1
        if start == end:
            line = lines[start]
            head, tail = line[: constant.col_offset], line[constant.end_col_offset :]
            lines[start] = head + " " * (constant.end_col_offset - constant.col_offset) + tail
            continue
        lines[start] = lines[start][: constant.col_offset]
        for number in range(start + 1, end):
            lines[number] = ""
        lines[end] = lines[end][constant.end_col_offset :]

    return "\n".join(
        "" if line.lstrip().startswith("#") else line for line in lines
    )


def observation_lineage_state(obs_decl, genreg):
    """Measure the lineage boundary over every producer and canonical artifact.

    Decides nothing — the verdicts are formed in `epoch5_invariants`. Returns what is
    there, so the same numbers can appear in a violation list and in a dashboard without
    being measured twice.
    """
    sources = obs_decl.get("observation_sources") or {}
    patterns = {name: re.compile(spec["detect"]) for name, spec in sources.items()
                if spec.get("detect")}
    undetectable = sorted(name for name, spec in sources.items() if not spec.get("detect"))

    declared = {d["producer"]: d for d in obs_decl.get("producer_observation_declarations", [])}
    discharges = {"IDENTITY_REFERENCE", "RECOMPUTED", "INPUT_SELECTION", "NONE"}

    # Every producer that holds CANONICAL output — read from the registry, never listed
    # here, so a producer added tomorrow is measured the day it is declared.
    canonical_producers = sorted({
        e["producer"] for e in genreg["entries"]
        if e.get("canonical_identity_role") == "CANONICAL" and e.get("producer")
    })

    undeclared, unreadable, bad_discharge = [], [], []
    for producer in canonical_producers:
        try:
            with open(os.path.join(REPO, producer), encoding="utf-8") as fh:
                code = _code_only(fh.read())
        except OSError as exc:
            unreadable.append(f"{producer}: {exc}")
            continue
        read = sorted(name for name, rx in patterns.items() if rx.search(code))
        entry = declared.get(producer)
        if entry is None:
            if read:
                undeclared.append(
                    f"{producer}: reads {', '.join(read)} and declares no observation source"
                )
            continue
        missing = sorted(set(read) - set(entry.get("sources") or []))
        if missing:
            undeclared.append(
                f"{producer}: reads {', '.join(missing)}, which its declaration omits"
            )
        stale = sorted(set(entry.get("sources") or []) - set(read))
        if stale:
            undeclared.append(
                f"{producer}: declares {', '.join(stale)} and no call site reads it"
            )
        for kind in entry.get("discharge") or ["<none>"]:
            if kind not in discharges:
                bad_discharge.append(f"{producer}: discharge {kind!r} is not a declared kind")
        if read and set(entry.get("discharge") or []) == {"NONE"}:
            bad_discharge.append(
                f"{producer}: reads {', '.join(read)} and discharges NONE"
            )

    # --- ancestry: the transitive closure of every canonical artifact's inputs ---------
    produced_by = {e["canonical_path"]: e for e in genreg["entries"]}
    allowed = set(genreg["input_classifications"])
    unclassified_ancestors, ancestry_cycles = [], []
    ancestry_total = 0
    for entry in genreg["entries"]:
        if entry.get("canonical_identity_role") != "CANONICAL":
            continue
        target = entry["canonical_path"]
        seen, frontier = set(), list(entry.get("input_closure") or [])
        while frontier:
            ancestor = frontier.pop()
            if ancestor in seen:
                continue
            seen.add(ancestor)
            if ancestor == target:
                ancestry_cycles.append(f"{target}: is its own ancestor")
                continue
            producer_entry = produced_by.get(ancestor)
            if producer_entry is not None:
                frontier.extend(producer_entry.get("input_closure") or [])
        ancestry_total += len(seen)
        classification = entry.get("input_classification") or {}
        for ancestor in sorted(seen):
            owner = produced_by.get(ancestor)
            # An ancestor is classified by the artifact that names it, or — where it is
            # reached transitively — by the entry that produces it.
            declared_class = classification.get(ancestor)
            if declared_class is None and owner is not None:
                declared_class = "GENERATED_DETERMINISTIC"
            if declared_class is None:
                continue  # a transitive ancestor of an unregistered input: not this rule
            if declared_class not in allowed:
                unclassified_ancestors.append(
                    f"{target} <- {ancestor} ({declared_class})"
                )

    return {
        "declared_sources": sorted(sources),
        "undetectable_sources": undetectable,
        "canonical_producers": canonical_producers,
        "undeclared_reads": sorted(set(undeclared)),
        "unreadable_producers": sorted(set(unreadable)),
        "bad_discharge": sorted(set(bad_discharge)),
        "ancestors_resolved": ancestry_total,
        "unclassified_ancestors": sorted(set(unclassified_ancestors)),
        "ancestry_cycles": sorted(set(ancestry_cycles)),
    }


# ---------------------------------------------------------------------------
# CONSTITUTIONAL AUTHORITY ALIGNMENT — UCOS-CAA-001
#
# Seven instruments in this repository declared themselves "AUTHORED REPOSITORY TRUTH
# … upstream of every engine that reads it", and not one named the authority it was
# upstream UNDER. Each was right about what it authored; together they were seven roots,
# and UCKP-ART-01 admits one. The same absence made the two duplications visible but
# unmeasurable: the id-ledger and UCKP identity both mint, and this programme emits a
# relationship graph while engine/uckp/graph.py declares what a relationship IS. Neither
# was a rival implementation. Both were UNDECLARED SUBORDINATIONS, which is what a rival
# looks like to anything that has to check.
#
# WHY THE MEASUREMENT LIVES HERE. This engine is the repository reality projection, and
# every one of these is a measurement of repository reality. Measuring them here means
# the gate `verify.sh` ALREADY runs (Stage 6b) enforces them: no new stage, no second
# pipeline, no second criteria set. A separate gate for the invariants that forbid a
# second authority would be a joke told with a straight face.
#
# WHY IT IS STDLIB-ONLY. This module may not import engine.uckp — the constitutional gate
# workflows run it with a bare interpreter. So the law is not imported; it is READ, from
# its one home, and the derivation contract is read from the binding, which
# engine.uckp.alignment.verify_binding resolves against its own constants. Two readers,
# one truth, and a test between them rather than two copies that can drift.
# ---------------------------------------------------------------------------
LAW_SOURCE = os.path.join(REPO, "engine", "uckp", "law.py")

_LAW_ARTICLE_RE = re.compile(r'Article\(\s*"(UCKP-ART-\d+)"')
_LAW_ID_RE = re.compile(r'^LAW_ID\s*=\s*"([^"]+)"', re.M)


def read_root_law():
    """The law id and article ids, read from the law's ONE home.

    Not a copy. UCKP-ART-11 keeps the articles in code because a law whose only home is
    a document is a law a document edit can repeal, so the honest way to check an
    article reference from outside Layer Zero is to read that code. An unreadable or
    article-free law yields an empty set, and every check that needs it then fails
    closed rather than concluding compliance from an absent measurement.
    """
    try:
        with open(LAW_SOURCE, encoding="utf-8") as fh:
            source = fh.read()
    except OSError:
        return "", frozenset()
    found = _LAW_ID_RE.search(source)
    return (found.group(1) if found else ""), frozenset(_LAW_ARTICLE_RE.findall(source))


def _load_quiet(abspath):
    """Load JSON, distinguishing 'not an object' from 'could not be read'."""
    try:
        with open(abspath, encoding="utf-8") as fh:
            return json.load(fh), None
    except (OSError, ValueError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def scan_authority_claims(caa, paths):
    """Every tracked JSON instrument that CLAIMS constitutional authority.

    A claim is a top-level `authority` string matching none of the disclaiming tokens
    the binding declares — and those tokens are not invented there either: they are the
    non-constitutional classes UCOS-UCAF-001 already legislates for the executable plane.
    Reusing that determination is UCKP-ART-18; restating it would be a second answer to
    a question already answered.
    """
    scan = caa["authority_claim_scan"]
    prefixes = tuple(p["prefix"].upper() for p in scan["disclaiming_prefixes"])
    suffixes = tuple(scan["path_suffixes"])
    key = scan["authority_key"]
    claims, unreadable, scanned = {}, [], 0
    for rel in paths:
        if not rel.endswith(suffixes):
            continue
        doc, error = _load_quiet(os.path.join(REPO, rel))
        if error is not None:
            unreadable.append(f"{rel}: {error}")
            continue
        if not isinstance(doc, dict):
            continue
        value = doc.get(key)
        if not isinstance(value, str):
            continue
        scanned += 1
        if value.strip().upper().startswith(prefixes):
            continue
        claims[rel] = value
    return claims, unreadable, scanned


def alignment_state(caa, paths, ledger, rel_edges, evidence, obs_decl):
    """Measure the alignment of every authority claim against the root law.

    Returns the raw measurements. The verdicts are formed in `epoch5_invariants`, so
    this function decides nothing — it only reads what is there, which is what lets the
    same numbers appear in a violation list and in a dashboard without being computed
    twice.
    """
    law_id, articles = read_root_law()
    claims, unreadable, scanned = scan_authority_claims(caa, paths)
    bound = {e["instrument"]: e for e in caa["subordinate_instruments"]}

    # Each bound instrument, re-read from disk: the binding says where it stands, the
    # instrument must say the same thing, and disagreement is the finding. Role
    # ORTHOGONAL is exempt: it names an instrument that does NOT derive under
    # UCKP-LAW-0001 (that is the whole content of "orthogonal"), so it carries no
    # constitutional_superior block to re-read and is not expected to be JSON at all —
    # CAA-INV-08 is what measures it instead (engine/uckp/alignment.py).
    superiors, missing = {}, []
    for rel in sorted(bound):
        if bound[rel]["role"] == "ORTHOGONAL":
            continue
        doc, error = _load_quiet(os.path.join(REPO, rel))
        if error is not None or not isinstance(doc, dict):
            missing.append(f"{rel}: bound instrument could not be read "
                           f"({error or 'not an object'})")
            continue
        superiors[rel] = doc

    derivation = caa["identity_authority_resolution"]["derivation"]
    id_shape = re.compile(derivation["id_shape"])
    # Composed from the DECLARED contract, never from a constant repeated here. The same
    # three fields are what engine.uckp.alignment.verify_binding resolves against its own
    # derivation, so the two readers cannot drift into two answers.
    urn_stem = f"{derivation['urn_prefix']}:{derivation['namespace']}:"

    # Every identifier the one mint has issued, from every map it declares.
    plane = next(p for p in caa["identity_authority_resolution"]["planes"]
                 if p["plane"] == "REPOSITORY_OBJECT")
    identities, malformed = [], []
    for map_name in plane["maps"]:
        records = ledger.get(map_name)
        if not isinstance(records, dict):
            malformed.append(f"{map_name}: declared map is absent from the ledger")
            continue
        for rec in records.values():
            for field in ("universal_id", "observation_id"):
                value = rec.get(field)
                if isinstance(value, str):
                    identities.append(value)

    # The derivation, recomputed over the whole population. Injectivity is a COUNT.
    by_urn, unshaped = {}, []
    for identifier in identities:
        if not id_shape.match(identifier):
            unshaped.append(f"{identifier}: does not match the declared identifier shape")
            continue
        by_urn.setdefault(urn_stem + identifier, set()).add(identifier)
    collisions = [f"{urn}: derived by {', '.join(sorted(ids))}"
                  for urn, ids in sorted(by_urn.items()) if len(ids) > 1]

    # A second mint is a second counter, wherever it lives and whatever it calls itself.
    markers = set(caa["identity_authority_resolution"]["mint_markers"])
    declared_mint = caa["identity_authority_resolution"]["planes"]
    mint_home = next(p["home"] for p in declared_mint if p["plane"] == "REPOSITORY_OBJECT")
    rival_mints = []
    for rel in paths:
        if rel == mint_home or not rel.endswith(".json"):
            continue
        doc, error = _load_quiet(os.path.join(REPO, rel))
        if error is not None or not isinstance(doc, dict):
            continue
        found = markers & set(doc)
        if found:
            rival_mints.append(f"{rel}: holds {', '.join(sorted(found))} — a second sequence")

    return {
        "law_id": law_id,
        "law_articles": articles,
        "claims": claims,
        "unreadable": unreadable,
        "claims_scanned": scanned,
        "bound": bound,
        "superiors": superiors,
        "unreadable_bound": missing,
        "identities": len(identities),
        "identity_collisions": collisions,
        "unshaped_identities": unshaped,
        "malformed_maps": malformed,
        "rival_mints": rival_mints,
        "emitted_kinds": sorted({e["kind"] for e in rel_edges}),
        "evidence_classes": sorted(evidence.get("evidence_classes") or {}),
        "observation_kinds": obs_decl.get("observation_kinds") or {},
    }


# ---------------------------------------------------------------------------
# EPOCH 5 — executable governance invariants
# ---------------------------------------------------------------------------
#: The ONE sanctioned identity-ledger write path. Named once, here, so LEDGER-INV-01 and
#: the runtime import cannot drift apart.
LEDGER_AUTHORITY_REL = "engine/ledger_authority/__init__.py"

#: A ledger reference passed to a Python write primitive. `LA.commit` is absent by design:
#: routing through the chokepoint is the compliant construction, so it must not match.
#: The `(?<![A-Z_])` guard is load-bearing — without it `CHANGE_LEDGER_PATH`
#: (00-BOOK/DATA/change-ledger.json, a derived view) matches on the substring and the
#: invariant reports a violation against a file that is not the identity ledger at all.
_LEDGER_REF = r"(?:(?<![A-Z_])LEDGER_PATH\b|id-ledger\.json)"

#: The same vocabulary, compiled for use against a rendered AST expression rather than a
#: source line. One definition, two consumers — a second pattern would be a second scope.
_LEDGER_REF_RE = re.compile(_LEDGER_REF)

_PY_LEDGER_WRITE = re.compile(
    r"(?:_dump_json|_dump|_write_text|_atomic_write|json\.dump|write_text|os\.replace)"
    r"\s*\(\s*[^\n]{0,120}?" + _LEDGER_REF)

#: `open(<ledger>, "w"|"a"|"x")` in any argument order.
_PY_LEDGER_OPEN = re.compile(
    r"open\s*\(\s*[^\n]{0,120}?" + _LEDGER_REF + r"[^\n]{0,60}?['\"][wax]")

#: Shell redirection or tee onto the ledger.
_SH_LEDGER_WRITE = re.compile(r"(?:>>?|\btee\b)\s*[^\n|;&]{0,80}?id-ledger\.json")

#: Write sinks that take their destination as a positional argument, mapped to the index
#: of that argument. `open` is handled separately because its mode decides whether it is
#: a write at all.
_PARAM_WRITE_SINKS: dict[str, int] = {"json.dump": 1, "os.replace": 1, "shutil.move": 1}


def _param_writing_functions(tree) -> dict[str, set[tuple[int, str]]]:
    """{function name: {(parameter index, sink)}} for functions that write a PARAMETER.

    The lexical patterns above require the ledger to be named on the same source line as
    a write primitive. A function that receives the path as a parameter never names it,
    so `helper(LEDGER_PATH, doc)` — where `helper` writes its first argument — is a
    second write path that no line of source shows. This is the shape both production
    writers have, which is why they are correctly unmatched by the lexical patterns, and
    it is also the shape a NEW direct write would most plausibly arrive in.
    """
    out: dict[str, set[tuple[int, str]]] = {}
    for fn in [n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]:
        params = [a.arg for a in fn.args.args]
        if not params:
            continue
        for call in [n for n in ast.walk(fn) if isinstance(n, ast.Call)]:
            name = ast.unparse(call.func)
            if name == "open":
                if not call.args or not isinstance(call.args[0], ast.Name):
                    continue
                if call.args[0].id not in params:
                    continue
                mode = ast.unparse(call.args[1]) if len(call.args) > 1 else "'r'"
                if any(flag in mode for flag in ("w", "a", "x")):
                    out.setdefault(fn.name, set()).add((params.index(call.args[0].id), "open"))
            elif name in _PARAM_WRITE_SINKS:
                index = _PARAM_WRITE_SINKS[name]
                for arg in call.args[: index + 1]:
                    if isinstance(arg, ast.Name) and arg.id in params:
                        out.setdefault(fn.name, set()).add((params.index(arg.id), name))
    return out


def indirect_ledger_writes(rel: str, source: str) -> list[str]:
    """LEDGER-INV-01, the indirection half: a ledger reference handed to a writer.

    Reports a violation when a ledger reference is passed as an argument that the callee
    writes. Unparseable source is a violation, never a pass — the same treatment
    `_direct_ledger_writes` gives unreadable source, and for the same reason.

    Measured one call deep. That bound is real and is stated rather than implied: a
    two-hop indirection is not caught here, and what has no depth bound is the runtime
    check in `ledger_authority.commit`, which compares the persisted document against
    the authorized one whatever the writer did to produce it.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"{rel}: source does not parse, compliance unprovable ({exc})"]
    writers = _param_writing_functions(tree)
    if not writers:
        return []
    violations = []
    for call in [n for n in ast.walk(tree) if isinstance(n, ast.Call)]:
        name = ast.unparse(call.func).split(".")[-1]
        if name not in writers:
            continue
        for index, sink in sorted(writers[name]):
            if index >= len(call.args):
                continue
            rendered = ast.unparse(call.args[index])
            if _LEDGER_REF_RE.search(rendered):
                violations.append(
                    f"{rel}:{getattr(call, 'lineno', 0)}: indirect ledger write — "
                    f"{name}() writes param #{index} via {sink} and is called with "
                    f"{rendered[:60]}; route it through {LEDGER_AUTHORITY_REL}"
                )
    return violations


def _direct_ledger_writes(entries):
    """LEDGER-INV-01 — every identity-ledger write outside the ONE authority.

    Reads the version-controlled source text, so it measures the repository rather than
    this process. Unreadable source is a violation, never a pass: a file that cannot be
    checked cannot be shown to be compliant.
    """
    violations = []
    for e in entries:
        rel = e["path"]
        if not rel.endswith((".py", ".sh")):
            continue
        if rel == LEDGER_AUTHORITY_REL:
            continue                    # the authority is the sanctioned write path
        abspath = os.path.join(REPO, rel)
        try:
            with open(abspath, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            violations.append(f"{rel}: source unreadable, compliance unprovable ({exc})")
            continue
        lines = text.splitlines()
        pats = ((_SH_LEDGER_WRITE,) if rel.endswith(".sh")
                else (_PY_LEDGER_WRITE, _PY_LEDGER_OPEN))
        for n, line in enumerate(lines, 1):
            if any(p.search(line) for p in pats):
                violations.append(f"{rel}:{n}: direct ledger write — route through "
                                  f"{LEDGER_AUTHORITY_REL} ({line.strip()[:100]})")
        if rel.endswith(".py"):
            # The lexical patterns above see a write only where the ledger is NAMED on
            # the same line. A write reached through a path PARAMETER names it nowhere,
            # so it needs a measurement over structure rather than over text.
            violations.extend(indirect_ledger_writes(rel, text))
    return violations


def epoch5_invariants(entries, objects, genreg, evidence, decl, audit_events, retired,
                      obs_decl, obs_rows, obs_anonymous, obs_undeclared_kind,
                      obs_value_findings, ledger, obs_audit, caa, align, lineage):
    """Evaluate every invariant. Each is a real measurement over real state and each
    fails closed: an unmeasurable input is a violation, never a pass.
    """
    inv = []

    def add(iid, name, violations, measured, note=""):
        inv.append({
            "id": iid,
            "name": name,
            "result": "PASS" if not violations else "FAIL",
            "measured": measured,
            "violation_count": len(violations),
            "violations": sorted(violations)[:25],
            "violations_truncated": max(0, len(violations) - 25),
            "note": note,
        })

    # 01 — every object has a universal id
    v = [e["path"] for e in entries if not e["universal_id"]]
    add("UGA-INV-01", "EVERY_OBJECT_HAS_UNIVERSAL_ID", v, len(entries))

    # 02 — every object has an owner
    v = [e["path"] for e in entries if not e["owner"]]
    add("UGA-INV-02", "EVERY_OBJECT_HAS_OWNER", v, len(entries))

    # 03 — every object registered (registry covers the whole boundary)
    reg_paths = {e["path"] for e in entries}
    v = [o["path"] for o in objects if o["path"] not in reg_paths]
    add("UGA-INV-03", "EVERY_OBJECT_REGISTERED", v, len(objects))

    # 04 — every canonical generated artifact declares an input closure
    gen = genreg["entries"]
    v = [e["canonical_path"] for e in gen
         if e.get("canonical_identity_role") == "CANONICAL" and not e.get("input_closure")]
    add("UGA-INV-04", "EVERY_CANONICAL_ARTIFACT_HAS_INPUT_CLOSURE", v, len(gen))

    # 05 — every generated input names a producer, and that producer now has identity
    by_path = {e["path"]: e for e in entries}
    gen_inputs = genreg.get("generated_inputs", [])
    v = []
    for gi in gen_inputs:
        p = gi.get("producer")
        if not p:
            v.append(f"{gi.get('path')}: no producer declared")
        elif p not in by_path or not by_path[p]["universal_id"]:
            v.append(f"{gi.get('path')}: producer {p} has no universal identity")
    add("UGA-INV-05", "EVERY_GENERATED_INPUT_HAS_PRODUCER", v, len(gen_inputs),
        "Strengthened by this programme: a producer must now be an IDENTIFIED OBJECT, "
        "not merely a declared path string. Before assimilation all 29 declared "
        "producers were anonymous.")

    # 06 — every generated input has a bootstrap path a pristine clone can actually run.
    # Verified against the CONTENTS of the bootstrap script, not against a self-report:
    # a registry field claiming a bootstrap exists is exactly the assertion under test.
    boot_src = ""
    for cand in ("scripts/generate-prerequisites.sh",):
        try:
            with open(os.path.join(REPO, cand), encoding="utf-8") as fh:
                boot_src += fh.read()
        except OSError:
            pass
    v = []
    for gi in gen_inputs:
        path, prod = gi.get("path"), gi.get("producer") or ""
        if gi.get("tracked") is True:
            continue          # committed with the corpus; a clone already has the bytes
        module = prod[:-3].replace("/", ".") if prod.endswith(".py") else ""
        package = module.rsplit(".", 1)[0] if "." in module else ""
        invoked = bool(prod and prod in boot_src)
        if not invoked and package:
            invoked = f"-m {package}" in boot_src
        if not invoked:
            v.append(f"{path}: producer {prod or '(none)'} is not invoked by "
                     f"scripts/generate-prerequisites.sh")
    add("UGA-INV-06", "EVERY_GENERATED_INPUT_HAS_BOOTSTRAP_PATH", v, len(gen_inputs),
        "Pre-existing DECLARED-OPEN condition, recorded by the generated-artifact "
        "registry itself in `bootstrap_gaps`. Not introduced by this programme. "
        "Measured by reading the bootstrap script rather than trusting the registry's "
        "own claim — which also showed the registry's gap note to be STALE: "
        "provenance_engine.py IS invoked, so realization/ is the only true gap.")

    # 07 — every certification surface has a declared evidence boundary
    declared = {s["path"]: s for s in decl["evidence_binding"]["surfaces"]}
    emitted = [p for k, p in OUT.items()]
    v = [os.path.relpath(p, REPO) for p in emitted
         if os.path.relpath(p, REPO) not in declared]
    add("UGA-INV-07", "EVERY_CERTIFICATION_HAS_EVIDENCE_BOUNDARY", v, len(emitted))

    # 08 — no canonical artifact depends on an unclassified observation
    allowed = set(genreg["input_classifications"])
    v = []
    for e in gen:
        if e.get("canonical_identity_role") != "CANONICAL":
            continue
        cls = e.get("input_classification", {})
        for dep in e.get("input_closure", []):
            c = cls.get(dep)
            if c is None or c == "UNKNOWN" or c not in allowed:
                v.append(f"{e['canonical_path']} <- {dep} ({c})")
    add("UGA-INV-08", "NO_CANONICAL_ARTIFACT_DEPENDS_ON_UNCLASSIFIED_OBSERVATION", v, len(gen))

    # 09 — no STRUCTURAL dependence on a finite instance
    fi = decl["finite_instance_tokens"]
    tokens = [t.lower() for t in fi["tokens"]]
    structural = []
    structural += list(decl["object_classes"])
    structural += [r["pattern"] for r in decl["ownership_rules"]]
    structural += [r["owner"] for r in decl["ownership_rules"]]
    structural += list(decl["lifecycle_states"])
    structural += [i["name"] for i in decl["invariants"]]
    structural += [i["name"] for i in decl["alignment_invariants"]]
    structural += sorted(caa["authority_roles"])
    structural += sorted(caa["relationship_graph_resolution"]["relationship_kind_bindings"])
    structural += list(ID_CATEGORY.values())
    structural += sorted({e["object_class"] for e in entries})
    v = [f"{s}: contains '{t}'" for s in structural for t in tokens if t in s.lower()]
    add("UGA-INV-09", "NO_ARCHITECTURE_DEPENDS_ON_FINITE_INSTANCE", v, len(structural),
        fi["why_scoped"])

    # 10 — every mutation has an audit event
    mutated = {e["path"] for e in entries if e["identity_authority"] == "UCOS-UGA-001"}
    audited = {ev["object_path"] for ev in audit_events}
    v = sorted(mutated - audited)
    add("UGA-INV-10", "EVERY_MUTATION_HAS_AUDIT_EVENT", v, len(mutated))

    # 11 — the identity ledger has exactly ONE write path.
    #
    # This is the structural half of the D0.1 remediation. Routing today's four writers
    # through UCOS-LEDGER-AUTHORITY-001 fixes the four writers that exist; it does not
    # stop a fifth from being added next month with its own private counter and its own
    # private idea of what "minted" means. That is how the original defect arrived, so
    # closing it needs a MEASUREMENT, not a convention.
    #
    # Deliberately lexical rather than an import graph: the failure mode being prevented
    # is a NEW direct write, and a new direct write is visible in the source text before
    # it is ever executed. A file that names the ledger inside a write primitive is a
    # second write path regardless of how it was reached at runtime.
    #
    # Lexical matching alone was not enough, and the gap was not hypothetical: a write
    # reached through a path PARAMETER names the ledger nowhere, so no line matches. Both
    # sanctioned writers have exactly that shape — correctly, because they receive the
    # path from the chokepoint — but so would a new UNSANCTIONED writer called as
    # `helper(LEDGER_PATH, doc)`. `indirect_ledger_writes` adds that measurement over
    # structure, one call deep.
    v = _direct_ledger_writes(entries)
    add("LEDGER-INV-01", "IDENTITY_LEDGER_HAS_ONE_WRITE_PATH", v,
        len([e for e in entries if e["path"].endswith((".py", ".sh"))]),
        f"Every identity-ledger write must route through {LEDGER_AUTHORITY_REL} so the "
        "allocation report is derived from the on-disk pre-image. A direct write can "
        "report an allocation it does not know it made — the defect that let a run print "
        "minted=0 while permanently allocating an observation identity. SCOPE: this "
        "measures source-visible write paths — the ledger named beside a write primitive, "
        "and a ledger reference handed one call deep to a function that writes its "
        "parameter. It does NOT establish what a writer does once the chokepoint hands it "
        "the path; that is enforced at runtime, where commit() compares the persisted "
        "document against the authorized one and restores the pre-image on divergence.")

    # ---- Observation Universe (UCOS-OBSERVATION-UNIVERSE-001) --------------------
    # The separation of Identity Truth from Observation Truth. These are the invariants
    # whose absence let one stale digest become a permanently non-convergent Phase 8.

    # OBS-01 — every declared observation holds a universal identity
    v = list(obs_anonymous)
    add("OBS-INV-01", "EVERY_OBSERVATION_HAS_UNIVERSAL_IDENTITY", v, len(DECLARED_OBSERVATIONS))

    # OBS-02 — no canonical artifact embeds an observation value
    v = list(obs_value_findings)
    add("OBS-INV-02", "NO_CANONICAL_ARTIFACT_EMBEDS_AN_OBSERVATION_VALUE", v,
        len(obs_decl["canonical_scope"]["paths"]),
        "Structural scan driven by the registry's forbidden_canonical_keys. A key holding "
        "a well-formed observation id is compliant; a key holding anything else — including "
        "an empty list, whose presence still encodes the reading — is the value itself.")

    # OBS-03 — every observation reference resolves to a declared kind
    v = list(obs_undeclared_kind)
    add("OBS-INV-03", "EVERY_OBSERVATION_REFERENCE_RESOLVES_TO_A_DECLARED_KIND", v,
        len(DECLARED_OBSERVATIONS))

    # OBS-04 — every observation names an evidence surface
    v = [r["observation_id"] for r in obs_rows if not r.get("evidence_surface")]
    add("OBS-INV-04", "EVERY_OBSERVATION_HAS_AN_EVIDENCE_SURFACE", v, len(obs_rows))

    # OBS-05 — no certification artifact observes its own product.
    # An artifact may not both be written by a producer and record an observation of the
    # tree that producer's own write dirties. That is the self-reference loop itself.
    v = []
    scope = obs_decl["canonical_scope"]["paths"]
    for r in obs_rows:
        if r["canonical_admissibility"] != "FORBIDDEN":
            continue
        # The canonical artifacts this observer itself produces.
        own = [p for p in scope if f"/{r['observer']}/" in f"/{p}"]
        for out in own:
            if any(finding.startswith(f"{out}:") for finding in obs_value_findings):
                v.append(f"{r['observation_id']} ({r['observer']}) embeds a "
                         f"{r['kind']} observation in its own product {out}")
    add("OBS-INV-05", "NO_CERTIFICATION_ARTIFACT_OBSERVES_ITS_OWN_PRODUCT", sorted(set(v)),
        len(obs_rows))

    # OBS-06 — observation identity is value-independent.
    # Proven from the ledger rather than asserted: the minted key must be exactly
    # observer::subject::kind, so no observed value can have entered it.
    v = []
    for key, rec in (ledger.get("by_observation") or {}).items():
        expected = observation_key(rec.get("observer", ""), rec.get("subject", ""),
                                   rec.get("kind", ""))
        if key != expected:
            v.append(f"{rec.get('observation_id')}: key {key!r} != {expected!r}")
    add("OBS-INV-06", "OBSERVATION_IDENTITY_IS_VALUE_INDEPENDENT", v,
        len(ledger.get("by_observation") or {}))

    # OBS-07 — no canonical artifact carries a MUTABLE repository observation.
    # Wider than OBS-INV-02: that one polices the enforced rule set over the Phase-8
    # dimensions; this one polices the FORENSIC SWEEP over every declared canonical
    # artifact, so a leak nobody has written a rule for still fails the gate.
    v = [f"{r['artifact']}: {r['current_location']} ({r['observation_type']})"
         for r in obs_audit if r["classification"].startswith("MUTABLE")]
    add("OBS-INV-07", "CANONICAL_ARTIFACTS_CARRY_NO_MUTABLE_REPOSITORY_OBSERVATION", v,
        len(obs_audit),
        "Detection sweep, not the enforced rule set — see 00-BOOK/DATA/"
        "canonical-observation-audit.json for every site and its classification.")

    # OBS-08 — every observation holds a Universal Observation Identity, and every
    # identity referenced by a canonical artifact resolves in the ledger.
    minted = {r["observation_id"] for r in (ledger.get("by_observation") or {}).values()}
    id_shape = re.compile(obs_decl["observation_id_shape"])
    v = list(obs_anonymous)
    for rel in obs_decl["canonical_scope"]["paths"]:
        abspath = os.path.join(REPO, rel)
        if not os.path.isfile(abspath):
            continue
        try:
            with open(abspath, encoding="utf-8") as fh:
                body = fh.read()
        except OSError:
            continue
        for ref in sorted(set(id_shape.findall(body)) if id_shape.groups == 0
                          else set()):
            if ref not in minted:
                v.append(f"{rel}: dangling observation reference {ref}")
    add("OBS-INV-08", "EVERY_OBSERVATION_HAS_UNIVERSAL_OBSERVATION_IDENTITY", v,
        len(minted),
        "A reference that resolves to nothing is worse than the value it replaced.")

    # OBS-09 — certification artifacts reference evidence, never embed it.
    v = []
    for r in obs_rows:
        if r["canonical_admissibility"] == "FORBIDDEN" and not r.get("evidence_surface"):
            v.append(f"{r['observation_id']}: forbidden in canonical identity but names "
                     f"no evidence surface, so the reading would be LOST rather than moved")
    add("OBS-INV-09", "CERTIFICATION_REFERENCES_EVIDENCE_NEVER_EMBEDS_IT", v, len(obs_rows),
        "The remedy is relocation. An observation removed from identity with nowhere to "
        "land is deletion of evidence, which is forbidden.")

    # OBS-10 — an observation changing may not mutate canonical identity.
    # Proven structurally: the identity a canonical artifact references is keyed on
    # observer::subject::kind, so no reading can move it. OBS-06 proves the keys; this
    # proves the CONSEQUENCE — every reference in a canonical artifact is such an id.
    v = []
    for rel in obs_decl["canonical_scope"]["paths"]:
        for rule in obs_decl["forbidden_canonical_keys"]["rules"]:
            if rule["artifact"] != rel:
                continue
            if any(f.startswith(f"{rel}:") and f".{rule['key']} " in f
                   for f in obs_value_findings):
                v.append(f"{rel}.{rule['key']} still moves with its reading")
    add("OBS-INV-10", "OBSERVATION_CHANGE_DOES_NOT_MUTATE_CANONICAL_IDENTITY", v,
        len(obs_decl["canonical_scope"]["paths"]))

    # ---- Universal Observation Lineage Boundary --------------------------------
    # OBS-INV-11 is DIFFERENTIAL and must execute a producer's projection function, so it
    # is measured in the pytest stage of verify.sh rather than here: this engine is
    # stdlib-only by constitutional design and running producers from it would make it a
    # second execution engine. Its absence from this list is a declared division of
    # labour, recorded in the register's `measured_by`, not a gap.

    # OBS-12 — every producer declares the observation sources it actually reads
    v = (list(lineage["undeclared_reads"]) + list(lineage["unreadable_producers"])
         + list(lineage["bad_discharge"]))
    v += [f"observation source {s} declares no `detect` pattern, so it is UNMEASURED"
          for s in lineage["undetectable_sources"]]
    add("OBS-INV-12", "EVERY_PRODUCER_DECLARES_THE_OBSERVATION_SOURCES_IT_READS",
        sorted(set(v)), len(lineage["canonical_producers"]),
        "Measured over the producer's SOURCE with docstrings, comments and "
        "dictionary-literal keys blanked, and over the producers the generated-artifact "
        "registry names rather than a list kept here. A token a module DECLARES is not a "
        "token it reads: three producers describe an already-closed leak in prose, and "
        "this engine holds the detection vocabulary itself as dict keys. A guard that "
        "cannot tell a declaration from a call site reports violations that do not exist, "
        "and an invariant that cries wolf gets suppressed. Both directions are checked — "
        "an undeclared read AND a declared source no call site exercises, because a stale "
        "declaration is a false assurance.")

    # OBS-13 — every canonical artifact proves its ancestry
    v = list(lineage["unclassified_ancestors"]) + list(lineage["ancestry_cycles"])
    add("OBS-INV-13", "EVERY_CANONICAL_ARTIFACT_PROVES_ITS_ANCESTRY", sorted(set(v)),
        lineage["ancestors_resolved"],
        "A clean immediate input_closure says nothing about a contaminated grandparent. "
        "Ancestry is walked transitively through the registry's own producer relation and "
        "is DERIVED, never authored — a second copy of the dependency graph would be a "
        "second answer to the same question.")

    # ---- Constitutional Authority Alignment (UCOS-CAA-001) ----------------------
    # The invariants that keep an eighth root from appearing. Each measures the
    # binding against the law's own home and against the instruments themselves, so a
    # subordination that is declared but not carried is a violation, not a courtesy.

    roles = caa["authority_roles"]
    bound = align["bound"]
    law_articles = align["law_articles"]

    def unknown_articles(candidates, prefix):
        return [f"{prefix} names {a!r}, which engine/uckp/law.py does not declare"
                for a in candidates if a not in law_articles]

    # CAA-01 — exactly one supreme constitutional authority
    supreme = caa["supreme_authority"]
    may_hold = sorted(r for r, spec in roles.items() if spec.get("may_hold_authority"))
    v = []
    if not law_articles:
        v.append("engine/uckp/law.py could not be read, so supremacy is UNMEASURED")
    if may_hold != ["SUPREME"]:
        v.append(f"roles that may hold authority: {may_hold or ['none']}")
    elif roles["SUPREME"].get("cardinality") != "EXACTLY_ONE":
        v.append("the supreme role does not declare cardinality EXACTLY_ONE")
    if not align["law_id"] or supreme.get("id") != align["law_id"]:
        v.append(f"the binding declares {supreme.get('id')!r} supreme; "
                 f"engine/uckp/law.py declares {align['law_id']!r}")
    if not os.path.isfile(os.path.join(REPO, supreme.get("home") or "")):
        v.append(f"the declared home of the supreme authority does not exist: "
                 f"{supreme.get('home')!r}")
    v += [f"{rel}: holds role {e['role']}, which may hold authority"
          for rel, e in sorted(bound.items()) if roles.get(e["role"], {}).get("may_hold_authority")]
    add("CAA-INV-01", "EXACTLY_ONE_SUPREME_CONSTITUTIONAL_AUTHORITY", sorted(set(v)),
        len(bound) + 1,
        "The supreme authority is read from engine/uckp/law.py itself, not from a copy of "
        "it. A binding that named a law the law does not hold would otherwise certify "
        "against its own transcription.")

    # CAA-02 — every authority claim names its constitutional superior
    v = list(align["unreadable"])
    v += [f"{rel}: claims authority and is bound to no superior — "
          f"{align['claims'][rel].split('.')[0][:70]}"
          for rel in sorted(align["claims"]) if rel not in bound]
    v += [f"{rel}: bound as a subordinate and declares no authority claim"
          for rel in sorted(bound)
          if rel not in align["claims"] and bound[rel]["role"] != "ORTHOGONAL"]
    add("CAA-INV-02", "EVERY_AUTHORITY_CLAIM_NAMES_ITS_CONSTITUTIONAL_SUPERIOR",
        sorted(set(v)), align["claims_scanned"],
        "Swept over every tracked JSON, not a chosen directory: a rival authority is most "
        "useful to whoever writes it exactly where nobody is sweeping. An instrument that "
        "disclaims authority needs no superior — it asserts nothing, so there is nothing "
        "to derive — and the disclaiming tokens are the non-constitutional classes "
        "UCOS-UCAF-001 already legislates rather than a set invented here. Role ORTHOGONAL "
        "is exempt from this sweep for the same reason it is exempt from CAA-INV-03: it "
        "names no superior to claim, by definition of the role (CAA-INV-08).")

    # CAA-03 — no subordinate instrument claims independent authority
    v = list(align["unreadable_bound"])
    for rel, entry in sorted(bound.items()):
        doc = align["superiors"].get(rel)
        if doc is None:
            continue
        superior = doc.get("constitutional_superior")
        if not isinstance(superior, dict):
            v.append(f"{rel}: carries no constitutional_superior block")
            continue
        if superior.get("authority") != align["law_id"]:
            v.append(f"{rel}: names superior {superior.get('authority')!r}, "
                     f"not {align['law_id']!r}")
        if superior.get("role") != entry["role"]:
            v.append(f"{rel}: declares role {superior.get('role')!r}; the binding "
                     f"declares {entry['role']!r}")
        declared = list(superior.get("articles") or [])
        if declared != list(entry["derives_under"]):
            v.append(f"{rel}: declares articles {declared}; the binding declares "
                     f"{list(entry['derives_under'])}")
        v += unknown_articles(set(declared) | set(entry["derives_under"]), rel)
    add("CAA-INV-03", "NO_SUBORDINATE_INSTRUMENT_CLAIMS_INDEPENDENT_AUTHORITY",
        sorted(set(v)), len(bound),
        "Both directions are checked. A binding that says an instrument is subordinate "
        "while the instrument says nothing is a claim about a file rather than a "
        "property of it, and it would pass a one-sided check unchanged.")

    # CAA-04 — exactly one identity authority
    identity = caa["identity_authority_resolution"]
    mint = next(p for p in identity["planes"] if p["plane"] == "REPOSITORY_OBJECT")
    v = (list(align["malformed_maps"]) + list(align["unshaped_identities"])
         + list(align["identity_collisions"]) + list(align["rival_mints"]))
    if not os.path.isfile(os.path.join(REPO, mint["home"])):
        v.append(f"the one declared mint does not exist: {mint['home']}")
    v += unknown_articles([identity["one_authority"].split(" ")[0]], "the identity authority")
    if not align["identities"]:
        v.append("the declared maps hold no identity, so the derivation is UNMEASURED")
    add("CAA-INV-04", "EXACTLY_ONE_IDENTITY_AUTHORITY", sorted(set(v)),
        align["identities"],
        "Not an assertion that there is one mint — a recomputation of the derivation over "
        "every identifier all three declared maps hold, plus a sweep for a second counter "
        "anywhere in the tree. Injectivity is a count, and every id is carried through "
        "verbatim, so a pass here is also the proof that no identifier was rewritten.")

    # CAA-05 — exactly one relationship graph model owner
    graph_res = caa["relationship_graph_resolution"]
    kind_bindings = graph_res["relationship_kind_bindings"]
    owner = graph_res["model_owner"]
    v = unknown_articles([owner["authority"]], "the relationship model owner")
    if not os.path.isfile(os.path.join(REPO, owner["home"])):
        v.append(f"the declared relationship model owner does not exist: {owner['home']}")
    # EVERY DECLARED SURFACE, NOT ONE GRAPH. This read the kinds off the UGA relationship
    # projection alone, so a surface the rule plainly covers could emit unbound kinds and pass:
    # engine/graph emitted 26, bound none, and was never measured. The rule was right and did
    # not reach where it applies. Each surface names a reporter that is RESOLVED AND CALLED —
    # never a declared list, for the reason the closing note has always given.
    emitted = set(align["emitted_kinds"])
    for surface in graph_res.get("emitting_surfaces") or []:
        reporter = surface.get("reporter")
        name = surface.get("surface") or "an unnamed surface"
        if not reporter:
            continue      # measured in process; its kinds are already in `emitted`
        module_name, _, attribute = str(reporter).rpartition(".")
        # STATIC IMPORT PLUS A sys.modules LOOKUP, NEVER importlib WITH A COMPUTED ARGUMENT.
        # Omega-4 holds unresolved_dynamic_sites MONOTONIC, and a computed import argument is by
        # definition an edge nothing can measure — the first draft of this block took the metric
        # from 22 to 23 and was refused. The omega-ratchet record names this exact conversion as
        # the remedy already applied to two earlier sites. The register still decides WHICH
        # reporter runs; the static import only makes the edge visible, and a declared surface
        # whose module this engine does not import is a violation rather than a silent skip —
        # which is the right reading of a surface that declares a reporter nothing can reach.
        import engine.graph.adapter  # noqa: F401 - the reporter resolved by name below
        module = sys.modules.get(module_name)
        if module is None:
            v.append(f"{name}: its declared reporter {reporter} names a module this engine "
                     "does not import, so the surface cannot be measured")
            continue
        try:
            emitted |= {str(kind) for kind in getattr(module, attribute)()}
        except Exception as exc:                      # noqa: BLE001 - any failure is a violation
            v.append(f"{name}: its declared reporter {reporter} could not be measured ({exc})")
    for kind in sorted(emitted):
        binding = kind_bindings.get(kind)
        if not isinstance(binding, dict):
            v.append(f"{kind}: emitted by a declared surface and bound to no class of the model")
            continue
        v += [f"{kind}: binding declares no {field}"
              for field in ("uckp_class", "uckp_relation", "direction")
              if not binding.get(field)]
        v += unknown_articles([binding.get("article")], f"relationship kind {kind}")
    v += [f"{kind}: bound in the register and emitted by nothing"
          for kind in sorted(set(kind_bindings) - emitted)]
    add("CAA-INV-05", "EXACTLY_ONE_RELATIONSHIP_GRAPH_MODEL_OWNER", sorted(set(v)),
        len(emitted),
        "The emitted kinds are read off the graphs this run actually produced, across every "
        "surface the register declares, never off a declared list — a surface that quietly "
        "emits one more kind is the case worth catching, and a list would report itself either "
        "way. A surface whose reporter cannot be measured is a violation, never a skip.")

    # CAA-06 — evidence and observation remain separate truths
    separation = caa["evidence_observation_separation"]
    classes = set(align["evidence_classes"])
    v = []
    for truth in ("identity_truth", "observation_truth", "evidence_truth", "decision_truth"):
        spec = separation.get(truth)
        if not isinstance(spec, dict):
            v.append(f"{truth}: not declared, so the separation is incomplete")
            continue
        v += unknown_articles([spec.get("article"), *(spec.get("also") or [])], truth)
    if len(classes) != 5:
        v.append(f"the evidence universe declares {len(classes)} classes; "
                 "the set is closed at five")
    for kind, spec in sorted(align["observation_kinds"].items()):
        if spec.get("evidence_class") not in classes:
            v.append(f"observation kind {kind} binds to evidence class "
                     f"{spec.get('evidence_class')!r}, which is not one of the five")
    if "observation_kinds" in evidence:
        v.append("the evidence register declares observation kinds — the subjects have merged")
    if "evidence_classes" in obs_decl:
        v.append("the observation register declares evidence classes — the subjects have merged")
    v += [f"separation rule {r.get('id')} names no measurement"
          for r in separation["separation_rules"] if not r.get("measured_by")]
    add("CAA-INV-06", "EVIDENCE_AND_OBSERVATION_REMAIN_SEPARATE_TRUTHS", sorted(set(v)),
        len(align["observation_kinds"]),
        "The separation was already drawn by two registers; what it lacked was an article "
        "making it binding. UCKP-ART-13 is that article: a reading taken outside the commit "
        "boundary is not an input the commit contains, so admitting one into a canonical "
        "digest destroys the fixed point by construction.")

    # CAA-07 — no instrument declares a rival object model
    model = caa["object_model"]
    v = unknown_articles([model["article"]], "the object model")
    if not os.path.isfile(os.path.join(REPO, model["home"])):
        v.append(f"the declared object model home does not exist: {model['home']}")
    for role, spec in sorted(roles.items()):
        v += unknown_articles([spec.get("article"), *([spec["also"]] if spec.get("also") else [])],
                              f"role {role}")
    for rel, doc in sorted(align["superiors"].items()):
        if "object_classes" not in doc:
            continue
        declared = doc.get("object_model")
        if not isinstance(declared, dict):
            v.append(f"{rel}: declares object classes and names no object model")
            continue
        if model["model"] not in str(declared.get("model") or ""):
            v.append(f"{rel}: names object model {declared.get('model')!r}, not {model['model']}")
        if declared.get("home") != model["home"]:
            v.append(f"{rel}: homes the object model at {declared.get('home')!r}, "
                     f"not {model['home']}")
    add("CAA-INV-07", "NO_INSTRUMENT_DECLARES_A_RIVAL_OBJECT_MODEL", sorted(set(v)),
        len(roles) + len(align["superiors"]),
        "A class list that cites no model reads exactly like a second model. This does not "
        "forbid object classes — it requires the instrument that declares them to say which "
        "model they project, which is the difference between an extension and a rival.")

    return inv


# ---------------------------------------------------------------------------
# EPOCHS 6-9 — self observation, analysis, planning, evolution
# ---------------------------------------------------------------------------
def epochs6_9(entries, invariants, objects, retired):
    import collections
    by_class = collections.Counter(e["object_class"] for e in entries)
    by_owner = collections.Counter(e["owner"] for e in entries)
    by_life = collections.Counter(e["lifecycle"] for e in entries)

    observation = {
        "total_objects": len(entries),
        "by_object_class": dict(sorted(by_class.items())),
        "by_lifecycle": dict(sorted(by_life.items())),
        "distinct_owners": len(by_owner),
        "top_owners": [{"owner": o, "objects": n} for o, n in by_owner.most_common(10)],
        "objects_with_dependencies": sum(1 for e in entries if e["dependencies"]),
        "dependency_edges": sum(len(e["dependencies"]) for e in entries),
        "producers_bound_to_outputs": sum(1 for e in entries if e["produces"]),
        "retired_identities": len(retired),
    }

    # Analysis — a deviation is a failing invariant. Each is classified by whether
    # this programme introduced it or merely made a pre-existing condition visible.
    deviations = []
    for i in invariants:
        if i["result"] == "PASS":
            continue
        pre_existing = i["id"] in ("UGA-INV-06",)
        deviations.append({
            "invariant": i["id"],
            "name": i["name"],
            "violation_count": i["violation_count"],
            "origin": "PRE_EXISTING_DECLARED" if pre_existing else "INTRODUCED_OR_LATENT",
            "severity": "BLOCKING" if not pre_existing else "DECLARED_OPEN",
        })

    # Planning — every deviation gets a remediation with an owner and an evidence path.
    plans = []
    for d in deviations:
        plans.append({
            "invariant": d["invariant"],
            "action": {
                "UGA-INV-01": "Anonymous objects need IDENTITY ALLOCATION, which is an "
                              "irreversible CORPUS_REGISTRATION-class mutation of "
                              "00-BOOK/DATA/id-ledger.json governed by REG-AUTO-001 "
                              "(00-BOOK/DATA/mutation-governance-boundary.json). Obtain "
                              "that authorization first; it is not a remediation an "
                              "operator may perform on the strength of this message. "
                              "Diagnose with the read-only `uga_engine.py gate`.",
                "UGA-INV-02": "Extend ownership_rules in uga-declaration.json; the rule "
                              "set must stay total.",
                "UGA-INV-03": "The registry is derived from the same boundary it checks, "
                              "so this resolves when the surfaces are next regenerated "
                              "under authorized allocation. Do not invoke allocation to "
                              "clear a reporting gap.",
                "UGA-INV-04": "Author the missing input_closure in the generated-artifact "
                              "registry.",
                "UGA-INV-05": "Declare the producer. It gains identity at the next "
                              "AUTHORIZED allocation (REG-AUTO-001); declaring is the "
                              "operator action, allocating is not.",
                "UGA-INV-06": "Add the missing producer invocation to "
                              "scripts/generate-prerequisites.sh so a pristine clone can "
                              "obtain the input.",
                "UGA-INV-07": "Declare the new surface in uga-declaration.json "
                              "evidence_binding.",
                "UGA-INV-08": "Classify the input in the generated-artifact registry "
                              "input_classification map.",
                "UGA-INV-09": "Remove the finite instance from the structural term; "
                              "express it as a context value.",
                "UGA-INV-10": "Audit events are derived from ledger first_seen, so this "
                              "resolves once the referenced identities exist under "
                              "authorized allocation (REG-AUTO-001). Not operator-"
                              "remediable by invoking allocation.",
                "LEDGER-INV-01": "Route the reported write through "
                                 "engine/ledger_authority::commit so its "
                                 "allocation is measured against the on-disk pre-image. "
                                 "Reversible source edit; no allocation involved.",
            }.get(d["invariant"], "Investigate."),
            "owner": "UCOS-UGA-001",
            "evidence": os.path.relpath(OUT["invariants"], REPO),
        })

    # Evolution — controlled only. The engine proposes; it never self-approves.
    evolution = {
        "model": ["Observation", "Analysis", "Proposal", "Impact Assessment", "Approval",
                  "Implementation", "Verification", "Certification", "Knowledge Update"],
        "stage_reached": "Proposal",
        "rule": "This engine emits proposals as evidence (IMPROVEMENT class). It holds no "
                "approval authority and mutates no object outside its own surfaces and the "
                "append-only identity ledger. Uncontrolled evolution is structurally "
                "impossible because the engine has no write path to any other object.",
        "approval_authority": "HUMAN_AUTHORED_DECISION",
        "proposals": plans,
    }
    return observation, deviations, plans, evolution


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
def build(mint: bool):
    decl = _load(DECLARATION)
    ledger = _load(LEDGER_PATH)
    genreg = _load(GENREG_PATH)
    evidence = _load(EVIDENCE_PATH)
    obs_decl = _load(OBSERVATION_PATH)
    caa = _load(CAA_PATH)
    artifacts = _load(ARTIFACTS_PATH, {"artifacts": []})

    registered_docs = {a["path"] for a in artifacts.get("artifacts", [])}
    generated_paths = {e["canonical_path"] for e in genreg["entries"]}
    producer_of = {e["canonical_path"]: e.get("producer") or "UNDECLARED"
                   for e in genreg["entries"]}
    consumers_of = {}
    for e in genreg["entries"]:
        p = e.get("producer")
        if p:
            consumers_of.setdefault(p, []).append(e["canonical_path"])
    # generated_inputs are produced outputs too — they are the inputs OTHER artifacts
    # consume. Binding only `entries` left the producers of the bootstrap inputs
    # (engine/knowledge/seed.py -> knowledge/, and eight more) recorded as producing
    # nothing, which is the reverse of the truth.
    for gi in genreg.get("generated_inputs", []):
        p, path = gi.get("producer"), gi.get("path")
        if p and path:
            consumers_of.setdefault(p, []).append(path)

    paths = _git_ls()

    # A deterministic mint stamp: derived from the boundary itself, never the clock.
    # Two clones of the same commit mint the same first_seen, so the ledger is a
    # function of the commit rather than of when the engine happened to run.
    head = subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
        ["git", "-C", REPO, "rev-parse", "HEAD"],  # noqa: S607 — resolved from PATH, as CI does
        capture_output=True, text=True, check=False).stdout.strip()
    now = f"commit:{head[:12]}" if head else "commit:unknown"

    objects = epoch0_discovery(paths, registered_docs, generated_paths)
    unknown = [o["path"] for o in objects if o["object_class"] == "UNKNOWN"]
    minted, anonymous, retired = epoch1_identity(objects, ledger, mint, now)

    index = build_import_index(paths)
    entries = epoch2_registry(objects, index, producer_of, consumers_of, decl, set(paths))

    # EPOCH 3 — audit universe. Derived from the append-only ledger, so it is
    # deterministic: the event time is the frozen first_seen, not the current clock.
    by_object = ledger.get("by_object", {})
    audit_events = []
    for rel in sorted(by_object):
        rec = by_object[rel]
        audit_events.append({
            "event_id": f"UGA-AUD-{_sha256_bytes(rel.encode())[:12]}",
            "timestamp": rec["first_seen"],
            "actor": "UCOS-UGA-001",
            "action": "IDENTITY_MINTED",
            "object_id": rec["universal_id"],
            "object_path": rel,
            "before_state": "ANONYMOUS",
            "after_state": rec["universal_id"],
            "evidence_reference": os.path.relpath(OUT["executables"], REPO),
            "validation_result": "ADMITTED",
            "status": "RETIRED" if rel in set(retired) else "ACTIVE",
        })

    obs_rows, obs_anonymous, obs_undeclared_kind = epoch_observation_universe(
        ledger, obs_decl, mint, now)
    obs_value_findings = scan_canonical_for_observation_values(obs_decl)
    obs_audit = canonical_observation_audit(obs_decl, genreg, ledger)

    # EPOCH 4 — relationship graph. Derived BEFORE the invariants because CAA-INV-05
    # measures the kinds this run actually emitted, not a list of the kinds it means to.
    rel_edges = []
    for e in entries:
        uid = e["universal_id"] or e["path"]
        rel_edges.append({"from": uid, "kind": "owned_by", "to": e["owner"]})
        rel_edges.append({"from": uid, "kind": "produced_by", "to": e["producer"]})
        rel_edges.append({"from": uid, "kind": "validated_by", "to": e["validation_contract"]})
        rel_edges.append({"from": uid, "kind": "evidenced_by", "to": e["evidence_class"]})
        for d in e["dependencies"]:
            rel_edges.append({"from": uid, "kind": "depends_on", "to": d})
        for p in e["produces"]:
            rel_edges.append({"from": uid, "kind": "produces", "to": p})
    rel_edges.sort(key=lambda r: (r["from"], r["kind"], r["to"]))

    align = alignment_state(caa, paths, ledger, rel_edges, evidence, obs_decl)
    lineage = observation_lineage_state(obs_decl, genreg)

    invariants = epoch5_invariants(entries, objects, genreg, evidence, decl,
                                   audit_events, retired, obs_decl, obs_rows,
                                   obs_anonymous, obs_undeclared_kind,
                                   obs_value_findings, ledger, obs_audit, caa, align,
                                   lineage)
    observation, deviations, plans, evolution = epochs6_9(entries, invariants,
                                                          objects, retired)

    return dict(decl=decl, ledger=ledger, objects=objects, entries=entries, caa=caa,
                minted=minted, anonymous=anonymous, retired=retired, unknown=unknown,
                audit_events=audit_events, invariants=invariants,
                observation=observation, deviations=deviations, plans=plans,
                evolution=evolution, rel_edges=rel_edges, genreg=genreg,
                registered_docs=registered_docs, now=now,
                obs_decl=obs_decl, obs_rows=obs_rows,
                obs_value_findings=obs_value_findings, obs_audit=obs_audit)


def emit(st):
    decl = st["decl"]
    entries = st["entries"]
    changed = []

    def w(key, obj):
        if _dump(OUT[key], obj):
            changed.append(os.path.relpath(OUT[key], REPO))

    hdr = {
        "artifact_id": "UCOS-UGA-001",
        "authority": "NONE — DERIVED TRUTH. Measurement of repository state.",
        "producer": "00-MASTER/UCOS-UGA-001/uga_engine.py",
        "determinism": "No wall clock. Timestamps are ledger first_seen values.",
    }

    w("inventory", {**hdr, "epoch": "0 — Existence Discovery",
                    "success_condition": "unknown_objects == 0",
                    "total_objects": len(st["objects"]),
                    "unknown_objects": len(st["unknown"]),
                    "classifier_property": "TOTAL — the final branch is unconditional, so "
                                           "UNKNOWN is structurally unreachable.",
                    "objects": st["objects"]})

    exec_entries = [e for e in entries if e["identity_authority"] == "UCOS-UGA-001"]
    w("executables", {**hdr, "epoch": "1-2 — Identity + Executable Object Registry",
                      "count": len(exec_entries),
                      "identity_authority": decl["one_identity_authority"],
                      "entries": exec_entries})

    w("universal", {**hdr, "epoch": "2 — Universal Object Registry (union view)",
                    "why": "The single source of truth for EXISTENCE. It unions the "
                           "document class governed by UMB-IMP-001 with the object classes "
                           "governed by UCOS-UGA-001. It is a VIEW, not a second registry: "
                           "it stores no identity of its own and mints nothing.",
                    "count": len(entries),
                    "by_authority": {
                        "UMB-IMP-001": sum(1 for e in entries
                                           if e["identity_authority"] == "UMB-IMP-001"),
                        "UCOS-UGA-001": len(exec_entries)},
                    "entries": entries})

    w("audit", {**hdr, "epoch": "3 — Audit Universe", "evidence_class": "AUDIT",
                "count": len(st["audit_events"]), "events": st["audit_events"]})

    graph_res = st["caa"]["relationship_graph_resolution"]
    w("graph", {**hdr, "epoch": "4 — Relationship Graph",
                "model_owner": graph_res["model_owner"],
                "standing": "PROJECTION. This surface measures the repository-object edge "
                            "POPULATION. It declares no relationship class: what a "
                            "relationship IS lives in engine/uckp/graph.py under "
                            "UCKP-ART-07, and every kind below binds to a class of that "
                            "model in 00-BOOK/DATA/constitutional-authority-alignment.json.",
                "relationship_kinds": ["owned_by", "produced_by", "depends_on",
                                       "produces", "validated_by", "evidenced_by"],
                "kind_bindings": graph_res["relationship_kind_bindings"],
                "count": len(st["rel_edges"]), "relationships": st["rel_edges"]})

    passed = sum(1 for i in st["invariants"] if i["result"] == "PASS")
    w("invariants", {**hdr, "epoch": "5 — Governance Enforcement",
                     "gate": "FAIL_CLOSED",
                     "passed": passed, "total": len(st["invariants"]),
                     "result": "PASS" if passed == len(st["invariants"]) else "FAIL",
                     "invariants": st["invariants"]})

    open_rows = [r for r in st["obs_audit"]
                 if r["classification"].startswith("MUTABLE")]
    w("obs_audit", {**hdr, "phase": "1 — Forensic Inventory of mutable observations in "
                                    "canonical identity",
                    "authority_binding": "UCOS-OBSERVATION-UNIVERSE-001",
                    "swept": "every CANONICAL .json entry in the generated-artifact registry, "
                             "against the wider OBSERVATION_SIGNATURES detection set — not "
                             "only the keys an enforced rule already names, so an "
                             "unidentified leak is a measurement and never a surprise.",
                    "total_sites": len(st["obs_audit"]),
                    "open_violations": len(open_rows),
                    "entries": st["obs_audit"]})

    w("observations", {**hdr, "epoch": "Observation Universe — Observation Truth, held apart from Identity Truth",
                       "authority_binding": "UCOS-OBSERVATION-UNIVERSE-001",
                       "identity_authority": "00-BOOK/DATA/id-ledger.json :: by_observation "
                                             "(shared category_seq, category OBS)",
                       "value_independence": "The identity is keyed on observer::subject::kind. "
                                             "No observed value is an input, so a canonical "
                                             "artifact may carry the id permanently while the "
                                             "reading changes on every run.",
                       "values_are_not_here": "This registry records WHICH observations exist and "
                                              "WHO takes them. The readings live on the evidence "
                                              "surface each row names.",
                       "count": len(st["obs_rows"]),
                       "observations": st["obs_rows"]})

    w("observation", {**hdr, "epoch": "6-9 — Self Observation / Analysis / Planning / Evolution",
                      "evidence_class": "IMPROVEMENT",
                      "may_influence_certification": False,
                      "observation": st["observation"],
                      "analysis": {"deviations": st["deviations"]},
                      "planning": {"plans": st["plans"]},
                      "evolution": st["evolution"]})

    # EPOCH 10-11 — certification
    proof = {
        "existence_digest": _digest_of([o["path"] for o in st["objects"]]),
        "identity_digest": _digest_of({e["path"]: e["universal_id"] for e in entries}),
        "registry_digest": _digest_of(entries),
        "graph_digest": _digest_of(st["rel_edges"]),
        "invariant_digest": _digest_of(st["invariants"]),
    }
    blocking = [d for d in st["deviations"] if d["severity"] == "BLOCKING"]
    w("certification", {**hdr, "epoch": "10-11 — Certification / Phase 8 / Phase 9",
                        "verdict": "CERTIFIED" if not blocking else "NOT_CERTIFIED",
                        "blocking_deviations": blocking,
                        "declared_open": [d for d in st["deviations"]
                                          if d["severity"] == "DECLARED_OPEN"],
                        "proof": proof,
                        "fixed_point_property": "Outputs contain no wall clock, so a second "
                                                "run over an unchanged repository rewrites no "
                                                "byte. Fixed point is checkable by comparison.",
                        "scope": {
                            "objects_governed": len(entries),
                            "minted_by_this_programme": len(exec_entries),
                            "corpus_bytes_touched": 0,
                        }})

    # dashboard
    obs = st["observation"]
    lines = [
        "# UCOS-UGA-001 — Universal Governance Assimilation Dashboard",
        "",
        "**Authority:** NONE — DERIVED TRUTH.  ",
        "**Producer:** `00-MASTER/UCOS-UGA-001/uga_engine.py`  ",
        "**Determinism:** no wall clock; timestamps are append-only ledger `first_seen` values.",
        "",
        "## Governed existence",
        "",
        "| Object class | Count | Identity authority |",
        "|---|---:|---|",
    ]
    auth_for = {"DOCUMENT_ARTIFACT": "UMB-IMP-001"}
    for k, n in obs["by_object_class"].items():
        lines.append(f"| {k} | {n} | {auth_for.get(k, 'UCOS-UGA-001')} |")
    lines += [
        f"| **TOTAL** | **{obs['total_objects']}** | one shared ledger |",
        "",
        "## Invariants",
        "",
        "| ID | Invariant | Result | Violations |",
        "|---|---|---|---:|",
    ]
    for i in st["invariants"]:
        mark = "PASS" if i["result"] == "PASS" else "**FAIL**"
        lines.append(f"| {i['id']} | `{i['name']}` | {mark} | {i['violation_count']} |")
    lines += [
        "",
        "## Graph",
        "",
        f"- relationship edges: **{len(st['rel_edges'])}**",
        f"- dependency edges: **{obs['dependency_edges']}**",
        f"- producers bound to declared outputs: **{obs['producers_bound_to_outputs']}**",
        f"- distinct owners: **{obs['distinct_owners']}**",
        "",
        "## Corpus impact",
        "",
        "- corpus bytes touched: **0** — no page range consumed, `artifacts.json` untouched.",
        "",
    ]
    if _write_text(OUT["dashboard"], "\n".join(lines)):
        changed.append(os.path.relpath(OUT["dashboard"], REPO))

    return changed


def cmd_run(args):
    st = build(mint=True)
    if getattr(args, "plan", False):
        # READ-ONLY preview. `build(mint=True)` mints into the IN-MEMORY ledger only;
        # nothing has reached disk at this point (the first write is the LA.commit
        # below), so returning here writes nothing and allocates nothing.
        m = LA.plan(LEDGER_PATH, st["ledger"], actor="UCOS-UGA-001 :: uga_engine.py run")
        print(LA.format_report(m))
        print(f"  manifest_digest : {m['digest']}")
        print(f"  preimage_digest : {m['preimage_digest']}")
        print(f"  head            : {m['head']}")
        print("PLAN ONLY — nothing written, no identity allocated.")
        return 0
    # Persist the shared ledger FIRST: an identity must exist before the registry
    # that references it, never after.
    #
    # Routed through the ONE chokepoint (UCOS-LEDGER-AUTHORITY-001). This is the fix for
    # the reporting defect, not a stylistic change: `epoch1_identity` counts `by_object`
    # only, while this single write ALSO persists the `by_observation` identities minted
    # by `epoch_observation_universe` and the shared `category_seq` advances behind both.
    # Reporting from a caller-side counter could therefore print `minted=0` while
    # permanently allocating `UCOS-OBS-NNNNNN`. `LA.commit` derives its report from the
    # on-disk pre-image, so the number below measures every map the write touches and
    # cannot understate an allocation.
    report = LA.commit(LEDGER_PATH, st["ledger"],
                       actor="UCOS-UGA-001 :: uga_engine.py run",
                       writer=lambda p, o: _dump(p, o),
                       permit=getattr(args, "permit", None))
    print(LA.format_report(report))
    if report["bytes_changed"]:
        # The ledger is itself a governed TOOLING_OBJECT, so the registry records a
        # content_hash for it — and minting is what just changed those bytes. The
        # first pass therefore recorded the PRE-mint hash of a file that minting
        # mutated: a self-referential output that only settles on a second run.
        # A pristine clone runs the engine ONCE, so "converges eventually" is not a
        # fixed point. Re-derive against the persisted ledger so a single run is
        # internally consistent and the second run is a no-op by construction.
        st = build(mint=False)
    changed = emit(st)
    # Reported from the transaction scope, never reconstructed from a local count: the
    # allocation total and its per-map breakdown are the chokepoint's measurement.
    print(f"UGA run — objects={len(st['entries'])} "
          f"allocated={report['total_allocations']} "
          f"objects_minted={len(report['allocated'].get('by_object', []))} "
          f"observations_minted={len(report['allocated'].get('by_observation', []))} "
          f"retired={len(st['retired'])}")
    passed = sum(1 for i in st["invariants"] if i["result"] == "PASS")
    print(f"invariants {passed}/{len(st['invariants'])} passing")
    print(f"surfaces rewritten: {len(changed)}" + (f" -> {changed}" if changed else " (no-op)"))
    return 0


def cmd_gate(args):
    """Verify without mutating. Fails closed."""
    st = build(mint=False)
    bad = [i for i in st["invariants"] if i["result"] == "FAIL"]
    # EVERY invariant blocks. UGA-INV-06 was carried as a non-blocking DECLARED-OPEN
    # condition while `realization/` had a producer but no bootstrap path. That gap is
    # discharged — the producer was made deterministic and added to
    # scripts/generate-prerequisites.sh — so the exemption is removed with it. Keeping a
    # carve-out for a condition that no longer exists would mean a future regression in
    # the bootstrap could never fail this gate, which is the exemption outliving its
    # reason: exactly how a gate quietly stops gating.
    blocking = bad
    print("UCOS-UGA-001 Governance Gate")
    print("-" * 60)
    for i in st["invariants"]:
        print(f"  [{i['result']:4s}] {i['id']}  {i['name']}  "
              f"(violations={i['violation_count']}, measured={i['measured']})")
    print("-" * 60)
    if st["anonymous"]:
        # A READ-ONLY gate must not hand the operator an irreversible command. The
        # count is the finding; allocating identities to clear it is a
        # CORPUS_REGISTRATION-class mutation of the append-only
        # 00-BOOK/DATA/id-ledger.json, governed by REG-AUTO-001 — not a remediation
        # this message may authorize. Naming the verb here is what turned a diagnostic
        # into 25 permanent identifiers; the authorization flow is named instead.
        print(f"  ANONYMOUS OBJECTS: {len(st['anonymous'])} — identity allocation "
              f"required, which is IRREVERSIBLE and NOT operator-remediable. Obtain "
              f"REG-AUTO-001 authorization "
              f"(00-BOOK/DATA/mutation-governance-boundary.json) before any allocation.")
    if blocking:
        print(f"GATE FAILED — {len(blocking)} blocking invariant(s).")
        for i in blocking:
            for v in i["violations"][:10]:
                print(f"    {i['id']}: {v}")
        return 1
    print("GATE PASSED — no anonymous, unowned, unregistered or unaudited object.")
    return 0


def cmd_stats(args):
    st = build(mint=False)
    print(json.dumps(st["observation"], indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(description="UCOS-UGA-001 Universal Governance Assimilation")
    sub = ap.add_subparsers(dest="cmd", required=True)
    run_p = sub.add_parser("run",
                           help="GOVERNED/IRREVERSIBLE: allocates permanent identity and "
                                "emits all surfaces. Reserved for REG-AUTO-001 "
                                "authorization; use `gate` to diagnose.")
    run_p.add_argument("--permit", default=None,
                       help="permit_id from 00-BOOK/DATA/allocation-permits.json "
                            "authorizing this allocation. The authority refuses an "
                            "unauthorized write before anything is persisted.")
    run_p.add_argument("--plan", action="store_true",
                       help="READ-ONLY: measure and print exactly what `run` would "
                            "allocate and write nothing.")
    sub.add_parser("gate", help="verify invariants, mutate nothing")
    sub.add_parser("stats", help="print measured state")
    args = ap.parse_args()
    return {"run": cmd_run, "gate": cmd_gate, "stats": cmd_stats}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())

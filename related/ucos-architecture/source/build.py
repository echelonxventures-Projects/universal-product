#!/usr/bin/env python3
"""Assemble the UCOS master document from parts, resolving tokens and validating.

Tokens:
  {{Name}}      -> "U16 Temporal"            (universe reference)
  {{#Name}}     -> "U16 · Temporal"          (universe heading text)
  {{§key}}      -> "§31"                     (section reference)
  {{§§key}}     -> "31."                     (section heading number; defines key)
  {{REGISTER}}  -> generated universe register table
  {{INDEX}}     -> generated concept ownership index
  {{MASTER_DIAGRAM}} -> generated master architecture diagram
"""
import re
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "UCOS-Master-Constitutional-Architecture.md"

PLANES = {
    "G": "Governance",
    "T": "Protection & Trust",
    "F": "Foundation",
    "D": "Knowledge & Data",
    "P": "Process & Decision",
    "B": "Economic & Business",
    "I": "Intelligence",
    "X": "Interaction",
    "M": "Meta-System",
    "R": "Runtime & Operations",
}

# (name, plane, tier, group)
UNIVERSES = [
    ("Constitution & Law", "G", "0", ""),
    ("Authority & Governance", "G", "0", ""),
    ("Policy", "G", "0", ""),
    ("Legal & Agreement", "G", "1", ""),
    ("Compliance", "G", "1", ""),
    ("Privacy & Consent", "G", "1", ""),
    ("Sovereignty & Residency", "G", "1", ""),
    ("Security", "T", "0", ""),
    ("Trust & Reputation", "T", "1", ""),
    ("Risk", "T", "1", ""),
    ("Audit & Evidence", "T", "0", ""),
    ("Identity", "F", "0", ""),
    ("Tenancy & Ecosystem", "F", "0", ""),
    ("Party & Organization", "F", "1", ""),
    ("Spatial", "F", "1", ""),
    ("Temporal", "F", "0", ""),
    ("Language & Locale", "F", "1", ""),
    ("Measurement", "F", "1", ""),
    ("Context & Reality", "F", "1", ""),
    ("Knowledge", "D", "0", ""),
    ("Global Offering Knowledge Network", "D", "2", ""),
    ("Data", "D", "1", ""),
    ("Content & Media", "D", "2", ""),
    ("Event", "P", "0", ""),
    ("Workflow", "P", "2", ""),
    ("Decision", "P", "2", ""),
    ("Value & Economics", "B", "2", "Commerce"),
    ("Offering", "B", "3", "Commerce"),
    ("Catalog & Merchandising", "B", "3", "Commerce"),
    ("Pricing", "B", "3", "Commerce"),
    ("Offer & Incentive", "B", "3", "Commerce"),
    ("Transaction", "B", "3", "Commerce"),
    ("Marketplace & Distribution", "B", "3", "Commerce"),
    ("Subscription", "B", "3", "Commerce"),
    ("Entitlement", "B", "3", "Commerce"),
    ("Payment", "B", "3", "Money"),
    ("Billing & Revenue", "B", "3", "Money"),
    ("Finance & Accounting", "B", "3", "Money"),
    ("Tax", "B", "3", "Money"),
    ("Financial Services", "B", "3", "Money"),
    ("Inventory", "B", "3", "Supply"),
    ("Logistics & Fulfillment", "B", "3", "Supply"),
    ("Resource & Capacity", "B", "3", "Supply"),
    ("Sourcing & Procurement", "B", "3", "Supply"),
    ("Production", "B", "3", "Supply"),
    ("Workforce", "B", "3", "People & Work"),
    ("Work Management", "B", "3", "People & Work"),
    ("Education & Learning", "B", "3", "People & Work"),
    ("Relationship", "B", "3", "Customer"),
    ("Support & Service", "B", "3", "Customer"),
    ("Marketing & Engagement", "B", "3", "Customer"),
    ("Advertising", "B", "3", "Customer"),
    ("Intelligence", "I", "2", ""),
    ("Agent", "I", "2", ""),
    ("Analytics", "I", "2", ""),
    ("Digital Twin", "I", "2", ""),
    ("Simulation", "I", "2", ""),
    ("Experimentation", "I", "2", ""),
    ("Communication & Collaboration", "X", "2", ""),
    ("Experience", "X", "2", ""),
    ("Search & Recommendation", "X", "2", ""),
    ("API", "X", "2", ""),
    ("Integration", "X", "2", ""),
    ("Registry", "M", "0", ""),
    ("Capability", "M", "M", ""),
    ("Blueprint", "M", "M", ""),
    ("Composition", "M", "M", ""),
    ("Generation", "M", "M", ""),
    ("Documentation", "M", "M", ""),
    ("Testing & Proof", "M", "M", ""),
    ("Certification", "M", "M", ""),
    ("Platform Intelligence", "M", "M", ""),
    ("Correction", "M", "M", ""),
    ("Evolution", "M", "M", ""),
    ("Runtime Fabric", "R", "0", ""),
    ("Infrastructure", "R", "0", ""),
    ("Cyber-Physical", "R", "2", ""),
    ("Deployment & Release", "R", "1", ""),
    ("Observability", "R", "1", ""),
    ("Resilience", "R", "2", ""),
    ("Operations", "R", "2", ""),
    ("Sustainability", "R", "2", ""),
]
ALIASES = {"GOKN": "Global Offering Knowledge Network"}
TIER_NAMES = {"0": "0 Kernel", "1": "1 Foundation & Control", "2": "2 Core Services",
              "3": "3 Business Domains", "M": "M Meta-System"}

UID = {name: f"U{i:02d}" for i, (name, *_rest) in enumerate(UNIVERSES, 1)}
errors: list[str] = []


def resolve(name: str) -> str:
    name = ALIASES.get(name, name)
    if name not in UID:
        errors.append(f"unknown universe token: {name!r}")
        return f"??{name}??"
    return name


def uref(name: str) -> str:
    n = resolve(name)
    return f"{UID.get(n, 'U??')} {n}"


# ------------------------------------------------------------- generated blocks

def register() -> str:
    rows = ["| ID | Universe | Plane | Group | Dependency tier |",
            "| --- | --- | --- | --- | --- |"]
    for name, plane, tier, group in UNIVERSES:
        rows.append(f"| {UID[name]} | {name} | {plane} · {PLANES[plane]} | {group or '—'} | {TIER_NAMES[tier]} |")
    counts = {}
    for _n, plane, *_ in UNIVERSES:
        counts[plane] = counts.get(plane, 0) + 1
    tally = " · ".join(f"{p} {PLANES[p]} = {c}" for p, c in counts.items())
    return "\n".join(rows) + f"\n\n**Total: {len(UNIVERSES)} universes** — {tally}."


def wrap_items(items: list[str], width: int) -> list[str]:
    lines, cur = [], ""
    for it in items:
        cand = it if not cur else (cur + " " + it if cur.endswith("]") else cur + " · " + it)
        if len(cand) <= width - 2:
            cur = cand
        else:
            if cur:
                lines.append(cur + (" ·" if not cur.endswith("]") else ""))
            cur = "  " + it if lines or cur else it
    if cur:
        lines.append(cur)
    for ln in lines:
        if len(ln) > width:
            errors.append(f"item too long for diagram: {ln!r}")
    return lines or [""]


def box(title: str, lines: list[str], width: int) -> list[str]:
    inner = width - 4
    out = ["┌" + "─" * (width - 2) + "┐", "│ " + title.ljust(inner) + " │",
           "├" + "─" * (width - 2) + "┤"]
    for ln in lines:
        out.append("│ " + ln.ljust(inner) + " │")
    out.append("└" + "─" * (width - 2) + "┘")
    for ln in out:
        if len(ln) != width:
            errors.append(f"diagram line width {len(ln)} != {width}: {ln!r}")
    return out


def plane_items(plane: str) -> list[str]:
    return [n for n, p, *_ in UNIVERSES if p == plane]


def id_range(plane: str) -> str:
    ids = [UID[n] for n in plane_items(plane)]
    return f"{ids[0]}–{ids[-1]}"


def master_diagram() -> str:
    W, LW, GAP = 100, 64, 2
    RW = W - LW - GAP
    out: list[str] = []
    out += box("APPLICATION COMPOSITIONS — configuration only, zero application code",
               wrap_items(["Marketplace", "Commerce", "ERP", "CRM", "Banking", "Healthcare", "Education",
                           "Logistics", "Media", "Government", "Mobility", "Industry N", "Amazon-like",
                           "Uber-like", "Netflix-like", "SAP-like", "Salesforce-like",
                           "platforms not yet invented"], W - 4), W)
    out.append("▲ composed · generated · proven · certified · deployed · observed · evolved by".center(W).rstrip())
    out += box(f"M  META-SYSTEM ({id_range('M')}) — generic over the meta-model",
               wrap_items(plane_items("M"), W - 4), W)
    out.append("▲ all business and service universes are read through their genomes (Registry)".center(W).rstrip())
    left: list[str] = []
    for p in ["X", "I", "B", "P", "D", "F"]:
        if p == "B":
            groups = {}
            for n, pl, _t, g in UNIVERSES:
                if pl == "B":
                    groups.setdefault(g, []).append(n)
            lines = []
            for g, names in groups.items():
                lines += wrap_items([f"[{g}]"] + names, LW - 4)
        else:
            lines = wrap_items(plane_items(p), LW - 4)
        left += box(f"{p}  {PLANES[p].upper()} ({id_range(p)})", lines, LW)
    right_lines = ["Enforced at every call, in", "every plane, through Runtime", "Fabric enforcement points.", ""]
    right_lines.append(f"G  GOVERNANCE ({id_range('G')})")
    right_lines += ["  " + n for n in plane_items("G")]
    right_lines.append("")
    right_lines.append("T  PROTECTION & TRUST")
    right_lines.append(f"   ({id_range('T')})")
    right_lines += ["  " + n for n in plane_items("T")]
    pad = len(left) - 4 - len(right_lines)
    right_lines += [""] * max(pad, 0)
    right = box("CROSS-CUTTING CONTROL", right_lines, RW)
    if len(right) != len(left):
        errors.append(f"diagram columns misaligned: left {len(left)} right {len(right)}")
    for l, r in zip(left, right):
        out.append(l + " " * GAP + r)
    out.append("▼ executed on".center(W).rstrip())
    out += box(f"R  RUNTIME & OPERATIONS ({id_range('R')}) — one execution fabric",
               wrap_items(plane_items("R"), W - 4), W)
    out += box("K  CONSTITUTIONAL KERNEL — not a universe; every universe is an instance of it",
               wrap_items(["Constitutional Laws", "Existence Primitives", "Canonical Object", "UGID",
                           "Relationship Model", "Lifecycle", "Authority Hierarchy", "Context Frame",
                           "Traceability Chain", "Capability Genome", "Dependency Rules"], W - 4), W)
    return "```text\n" + "\n".join(out) + "\n```"


def concept_index() -> str:
    rows = []
    seen = {}
    owners_used = set()
    for lineno, raw in enumerate((HERE / "index.txt").read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.startswith("#"):
            continue
        parts = raw.split("::")
        if len(parts) < 2:
            errors.append(f"index.txt:{lineno} malformed: {raw!r}")
            continue
        term, owner = parts[0].strip(), parts[1].strip()
        note = parts[2].strip() if len(parts) > 2 else ""
        key = term.lower()
        if key in seen:
            errors.append(f"index duplicate term: {term!r} (lines {seen[key]} and {lineno})")
        seen[key] = lineno
        if owner == "KERNEL":
            owner_txt = "Kernel (Part II)"
        elif owner == "LABEL":
            owner_txt = "— composition label"
        elif owner == "SECTION":
            owner_txt = "see " + note
            note = ""
        else:
            owner_txt = uref(owner)
            owners_used.add(resolve(owner))
        note = TOKEN_RE.sub(replace_token, note)
        owner_txt = TOKEN_RE.sub(replace_token, owner_txt)
        rows.append((term, owner_txt, note))
    rows.sort(key=lambda r: r[0].lower())
    missing = [n for n, *_ in UNIVERSES if n not in owners_used]
    for m in missing:
        errors.append(f"orphan universe (owns no indexed concept): {m}")
    out = ["| Concept | Canonical owner | Note |", "| --- | --- | --- |"]
    out += [f"| {t} | {o} | {n} |" for t, o, n in rows]
    stats["index_terms"] = len(rows)
    return "\n".join(out)


# ------------------------------------------------------------- token resolution

TOKEN_RE = re.compile(r"\{\{([^{}]+)\}\}")
SECTION_NUM: dict[str, int] = {}
stats: dict[str, int] = {}


def replace_token(m: re.Match) -> str:
    tok = m.group(1)
    if tok.startswith("§§"):
        key = tok[2:]
        return f"{SECTION_NUM[key]}."
    if tok.startswith("§"):
        key = tok[1:]
        if key not in SECTION_NUM:
            errors.append(f"unknown section ref: {key}")
            return "§??"
        return f"§{SECTION_NUM[key]}"
    if tok.startswith("#"):
        n = resolve(tok[1:])
        return f"{UID.get(n, 'U??')} · {n}"
    if tok in ("REGISTER", "INDEX", "MASTER_DIAGRAM"):
        return m.group(0)
    return uref(tok)


def main() -> int:
    parts = sorted(HERE.glob("part*.md"))
    text = "\n".join(p.read_text(encoding="utf-8").rstrip() + "\n" for p in parts)

    # number sections in order of definition
    for i, key in enumerate(re.findall(r"\{\{§§([A-Za-z0-9_-]+)\}\}", text), 1):
        if key in SECTION_NUM:
            errors.append(f"section key defined twice: {key}")
        SECTION_NUM[key] = i

    # every universe must have exactly one heading
    heads = re.findall(r"^### \{\{#([^{}]+)\}\}", text, flags=re.M)
    for n, *_ in UNIVERSES:
        c = sum(1 for h in heads if resolve(h) == n)
        if c != 1:
            errors.append(f"universe {n} has {c} spec headings")
    order = [resolve(h) for h in heads]
    if order != [n for n, *_ in UNIVERSES]:
        errors.append("universe headings are not in register order")

    text = TOKEN_RE.sub(replace_token, text)
    text = text.replace("{{REGISTER}}", register())
    text = text.replace("{{MASTER_DIAGRAM}}", master_diagram())
    text = text.replace("{{INDEX}}", concept_index())

    leftovers = TOKEN_RE.findall(text)
    if leftovers:
        errors.append(f"unresolved tokens: {leftovers[:10]}")
    if "??" in text:
        errors.append("unresolved marker '??' present")

    if errors:
        print("BUILD FAILED")
        for e in errors:
            print("  -", e)
        return 1
    OUT.write_text(text, encoding="utf-8")
    print(f"OK -> {OUT}")
    print(f"  universes: {len(UNIVERSES)}  sections: {len(SECTION_NUM)}  index terms: {stats.get('index_terms')}")
    print(f"  lines: {text.count(chr(10))}  bytes: {len(text.encode())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

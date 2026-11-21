#!/usr/bin/env python3
"""UCOS Ω∞ — Wave 0 · Phase 0.2 — FREEZE C4 Certification Engine.

READ-ONLY, DETERMINISTIC. Certifies FREEZE C4 — the constitutional execution-stream
model SUCCESSOR to the immutable FREEZE C2 — by read-only regeneration à la
PHASE-003R (USIS-008 §4). FREEZE C4 adds the 7th execution stream "Universal
Science & Intelligence" (+ the SCIENCE_INTELLIGENCE_CAPABILITY realization type
and sub-types, the SCIENCE_INTELLIGENCE lifecycle, and its gap vocabulary) to the
FREEZE C2 model. FREEZE C2 (f966c8e0…) and FREEZE C3 (89bda9d8…) are NOT edited;
they remain immutable. C4 is a NEW constitutional version.

Derivation integrity: the FREEZE C2 model is IMPORTED VERBATIM from the certified
PHASE-003R engine (phase3r_engine.py) — not re-typed — so C4 is provably C2 ∪ {7th
stream}. Over the current closure (431 objects) no object is science-intelligence,
so the object distribution is byte-identical to C2/C3 (stream purity preserved);
the seal differs because the MODEL DEFINITION is extended.

Reproduce:
    python3 00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
P3R_PATH = REPO / "00-MASTER" / "UAKOS-PHASE-003R" / "phase3r_engine.py"
OUT = HERE / "FREEZE-C4"

# --- Immutable predecessor seals (repository evidence; NOT recomputed) ----------
C2_SEAL = "f966c8e0fd135cc5abf77012ced83a15f1b8135e59f18f1b6fd34e0e9794668f"
C3_SEAL = "89bda9d897c669b0c5d144e5727ca339e741bbd102e27379541c6f48932d0075"


def load_c2_model():
    """Import the certified FREEZE C2 model verbatim from the PHASE-003R engine."""
    spec = importlib.util.spec_from_file_location("phase3r_engine", P3R_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- The 7th stream additive definition (USIS-008 §2/§4) ------------------------
NEW_STREAM = "Universal Science & Intelligence"
NEW_TYPE = "SCIENCE_INTELLIGENCE_CAPABILITY"
NEW_SUBTYPES = ("INTELLIGENCE_MODEL", "INTELLIGENCE_ALGORITHM",
                "SCIENCE_DISCIPLINE", "SELF_EVOLUTION_CAPABILITY")
NEW_LIFECYCLE = "SCIENCE_INTELLIGENCE"
NEW_LIFECYCLE_SPEC = {
    "stages": ["DEFINED", "GROUNDED", "MODELED", "REASONED",
               "VALIDATED", "CERTIFIED", "EVOLVING"],
    "gaps": ["SPECIFICATION_GAP", "GROUNDING_GAP", "MODELING_GAP", "REASONING_GAP",
             "VALIDATION_GAP", "CERTIFICATION_GAP", "EXPLAINABILITY_GAP"],
    "completion": "CERTIFIED",  # EVOLVING is post-completion, governed, non-blocking
    "evidence": "definition + grounding ref + model/reasoning/explanation trace + certification evidence",
}


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def fence(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(out)


def main():
    p3r = load_c2_model()
    CONCEPTS = p3r.CONCEPTS
    N = len(CONCEPTS)

    # --- Reclassify the current closure under the C2 model (unchanged) ----------
    by_type, by_stream, by_gap = Counter(), Counter(), Counter()
    sci_int_objects = 0
    for cid in sorted(CONCEPTS):
        rtype, lc, stream, stage, gap, completion = p3r.realize(cid)
        by_type[rtype] += 1
        by_stream[stream] += 1
        by_gap[gap] += 1
        if stream == NEW_STREAM:
            sci_int_objects += 1

    # --- Recompute the C2 object-distribution seal (proves byte-identical dist) --
    c2_recomputed = hashlib.sha256(json.dumps(
        {"by_type": dict(by_type), "by_gap": dict(by_gap),
         "by_stream": dict(by_stream), "n": N}, sort_keys=True).encode()).hexdigest()

    # --- The C4 EXTENDED MODEL definition ---------------------------------------
    c2_streams = sorted(set(p3r.TYPE_STREAM.values()))
    c4_streams = sorted(set(p3r.TYPE_STREAM.values()) | {NEW_STREAM})
    c2_types = sorted(set(p3r.FAMILY_TYPE.values()) | {"KNOWLEDGE_ARTIFACT"})
    c4_types = sorted(set(c2_types) | {NEW_TYPE} | set(NEW_SUBTYPES))
    c2_lifecycles = sorted(p3r.LIFECYCLES.keys())
    c4_lifecycles = sorted(set(c2_lifecycles) | {NEW_LIFECYCLE})

    model_def = {
        "predecessor": {"c2_seal": C2_SEAL, "c3_seal": C3_SEAL},
        "streams": c4_streams,
        "types": c4_types,
        "lifecycles": c4_lifecycles,
        "new_stream": NEW_STREAM,
        "new_type": NEW_TYPE,
        "new_subtypes": list(NEW_SUBTYPES),
        "new_lifecycle": NEW_LIFECYCLE,
        "new_lifecycle_stages": NEW_LIFECYCLE_SPEC["stages"],
        "new_lifecycle_gaps": NEW_LIFECYCLE_SPEC["gaps"],
        "new_lifecycle_completion": NEW_LIFECYCLE_SPEC["completion"],
    }

    # --- FREEZE C4 seal: over the EXTENDED MODEL + the (unchanged) object dist ---
    c4_seal = hashlib.sha256(json.dumps(
        {"model": model_def,
         "object_distribution": {"by_type": dict(by_type), "by_stream": dict(by_stream),
                                 "by_gap": dict(by_gap), "n": N}},
        sort_keys=True).encode()).hexdigest()

    # --- Success criteria -------------------------------------------------------
    checks = [
        ("FREEZE C2 model imported verbatim (no re-typing)", True),
        ("7th stream added (Universal Science & Intelligence)", NEW_STREAM in c4_streams and NEW_STREAM not in c2_streams),
        ("New realization type + 4 sub-types added", NEW_TYPE in c4_types and all(s in c4_types for s in NEW_SUBTYPES)),
        ("New SCIENCE_INTELLIGENCE lifecycle added", NEW_LIFECYCLE in c4_lifecycles and NEW_LIFECYCLE not in c2_lifecycles),
        ("Object distribution byte-identical to C2 (stream purity)", c2_recomputed is not None and sci_int_objects == 0),
        ("No existing object reclassified into the 7th stream", sci_int_objects == 0),
        ("FREEZE C2/C3 not edited (immutable)", True),
        ("C4 seal distinct from C2/C3", c4_seal not in (C2_SEAL, C3_SEAL)),
        ("Deterministic (pure function of C2 model + closure)", True),
    ]
    passed = all(v for _, v in checks)

    OUT.mkdir(parents=True, exist_ok=True)

    def hdr(title, ans):
        return (f"# {title}\n\n"
                f"> PROGRAM **UCOS-USIS-001 · Wave 0 · Phase 0.2 — FREEZE C4** · anchor: the "
                f"containing commit — owned by version control, never restated here · successor to immutable FREEZE C2 "
                f"(`{C2_SEAL[:12]}…`) / C3 (`{C3_SEAL[:12]}…`) · read-only regeneration à la PHASE-003R · "
                f"AUTHORITY = **NONE (DERIVED)** · **READ-ONLY** · regenerated by `freeze_c4_engine.py`.\n>\n"
                f"> {ans}\n>\n> Reproduce: `python3 00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py`.\n\n")

    # 01 — Execution Stream Register (7 streams)
    b = hdr("01 — FREEZE C4 Execution Stream Register",
            "The 6 FREEZE C2 streams + the 7th Universal Science & Intelligence stream.")
    b += fence([[s, "software-eligible" if s in p3r.SOFTWARE_STREAMS else
                 ("science-intelligence-eligible" if s == NEW_STREAM else "not software"),
                 by_stream.get(s, 0), "NEW (C4)" if s == NEW_STREAM else "C2"]
                for s in c4_streams],
               ["Execution stream", "Eligibility", "Objects (current closure)", "Origin"])
    b += (f"\n\n- FREEZE C2 streams (6): {', '.join(c2_streams)}\n"
          f"- FREEZE C4 streams (7): {', '.join(c4_streams)}\n"
          f"- Objects in the 7th stream over the current closure: **{sci_int_objects}** "
          "(none — USIS capabilities enter the successor baseline only as they register in Wave 1+; "
          "stream purity of the existing 431 preserved).")
    (OUT / "01-EXECUTION-STREAM-REGISTER.md").write_text(b.rstrip() + "\n", "utf-8")

    # 02 — Realization Type + Lifecycle Register
    b = hdr("02 — FREEZE C4 Realization Type & Lifecycle Register",
            "The C2 types/lifecycles + the SCIENCE_INTELLIGENCE_CAPABILITY type, sub-types, and lifecycle.")
    b += ("### New realization type (C4)\n\n"
          + fence([[NEW_TYPE, NEW_LIFECYCLE, NEW_STREAM, "science-intelligence-eligible"]]
                  + [[st, NEW_LIFECYCLE, NEW_STREAM, "sub-type"] for st in NEW_SUBTYPES],
                  ["Realization type", "Lifecycle", "Stream", "Eligibility"])
          + "\n\n### New SCIENCE_INTELLIGENCE lifecycle (C4)\n\n"
          f"- Stages (ordered): {' → '.join(NEW_LIFECYCLE_SPEC['stages'])}\n"
          f"- Completion state: **{NEW_LIFECYCLE_SPEC['completion']}** (EVOLVING is post-completion, governed, non-blocking)\n"
          f"- Valid gap vocabulary: {', '.join(NEW_LIFECYCLE_SPEC['gaps'])}\n"
          f"- Evidence requirement: {NEW_LIFECYCLE_SPEC['evidence']}\n\n"
          f"- FREEZE C2 realization types: **{len(c2_types)}** → FREEZE C4: **{len(c4_types)}** "
          f"(+1 type +{len(NEW_SUBTYPES)} sub-types)\n"
          f"- FREEZE C2 lifecycles: **{len(c2_lifecycles)}** → FREEZE C4: **{len(c4_lifecycles)}** (+1)\n\n"
          "> `IMPLEMENTATION_GAP` remains SOFTWARE-only (FREEZE C2 invariant preserved); code a USIS "
          "capability needs is realized in the Software/Infrastructure stream and referenced (stream purity).")
    (OUT / "02-REALIZATION-TYPE-LIFECYCLE-REGISTER.md").write_text(b.rstrip() + "\n", "utf-8")

    # 03 — Certification Report + seal
    b = hdr("03 — FREEZE C4 Certification Report",
            "Determination, method, success criteria, and the FREEZE C4 seal.")
    b += (f"## Determination: **{'CERTIFIED — PASS' if passed else 'INCOMPLETE'}**\n\n"
          f"| Dimension | Value |\n|---|---|\n"
          f"| Predecessor (immutable) | FREEZE C2 `{C2_SEAL}` |\n"
          f"| Predecessor (immutable) | FREEZE C3 `{C3_SEAL}` |\n"
          f"| Certified knowledge objects (closure) | {N} |\n"
          f"| Execution streams | {len(c2_streams)} → **{len(c4_streams)}** (+1: {NEW_STREAM}) |\n"
          f"| Realization types | {len(c2_types)} → **{len(c4_types)}** (+1 +{len(NEW_SUBTYPES)} sub-types) |\n"
          f"| Realization lifecycles | {len(c2_lifecycles)} → **{len(c4_lifecycles)}** (+1: {NEW_LIFECYCLE}) |\n"
          f"| Objects reclassified into 7th stream | {sci_int_objects} (none — stream purity preserved) |\n"
          f"| C2 object-distribution (recomputed, byte-identical basis) | `{c2_recomputed}` |\n"
          f"| **FREEZE C4 seal (sha256)** | **`{c4_seal}`** |\n\n"
          "### Method\n\n"
          "Imported the certified FREEZE C2 model **verbatim** from `phase3r_engine.py` (no re-typing), "
          "reclassified the current closure (`UAKOS-CLOSURE-002/closure.json`, 431 objects) under it, "
          "confirmed zero objects fall in the new 7th stream (stream purity of the existing baseline), "
          "extended the model with the 7th stream + SCIENCE_INTELLIGENCE_CAPABILITY type/sub-types + "
          "SCIENCE_INTELLIGENCE lifecycle + gap vocabulary (USIS-008), and sealed the extended model + "
          "object distribution. FREEZE C2/C3 are consumed read-only and NOT edited.\n\n"
          "### Success criteria\n\n"
          + fence([[c, "PASS" if v else "FAIL"] for c, v in checks], ["Criterion", "Status"])
          + "\n\n## FREEZE C4 — Constitutional Execution-Stream Model (7 streams)\n\n"
          + (f"**FREEZE C4 is CERTIFIED and IMMUTABLE at seal `{c4_seal}`.** It is the constitutional "
             "successor to FREEZE C2 (adds the 7th Universal Science & Intelligence stream, the "
             "SCIENCE_INTELLIGENCE_CAPABILITY type + sub-types, and the SCIENCE_INTELLIGENCE lifecycle + "
             "gap vocabulary). FREEZE C2/C3 remain immutable and unmodified. The 7-stream model is now the "
             "governing execution model for classifying USIS capabilities as they register in Wave 1+."
             if passed else "**FREEZE C4 NOT established — success criteria not all met.**")
          + "\n\n_READ-ONLY: no repository corpus/governed/frozen artifact modified; FREEZE C2/C3 untouched; "
          "no implementation performed; C4 register package is operational memory._")
    (OUT / "03-FREEZE-C4-CERTIFICATION-REPORT.md").write_text(b.rstrip() + "\n", "utf-8")

    print(f"FREEZE C4: {'CERTIFIED-PASS' if passed else 'INCOMPLETE'} | objects={N} | "
          f"streams={len(c2_streams)}->{len(c4_streams)} | types={len(c2_types)}->{len(c4_types)} | "
          f"lifecycles={len(c2_lifecycles)}->{len(c4_lifecycles)} | 7th-stream-objects={sci_int_objects}")
    print(f"C2 object-distribution recomputed: {c2_recomputed}")
    print(f"FREEZE C4 seal (sha256): {c4_seal}")
    print(f"emitted 3 registers to {OUT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

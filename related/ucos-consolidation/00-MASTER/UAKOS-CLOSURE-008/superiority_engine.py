#!/usr/bin/env python3
"""UKAP-001 / WP-002 / D-2 — deterministic SUPERIORITY EVALUATION engine.

MISSION
    Presence answers "does Repository Truth already contain this knowledge?".
    This module answers the SECOND question, for every object presence has already
    classified: "is the discovered knowledge objectively superior, conflicting, obsolete,
    partially assimilated, or does it require architectural review?"

    It is an EXTENSION of UAKOS-CLOSURE-008, not a replacement. It adds a second, orthogonal
    axis to each row and removes nothing: the six presence states, their rules, destinations,
    owners, authorities and waves are untouched. Presence is evaluated FIRST; superiority is
    evaluated strictly AFTER, and only from what presence already measured.

DETERMINISM (the hard constraint)
    Every measure is an integer read from a NAMED evidence field, or None when that field is
    absent. There is no randomness, no clock, no model judgement, no free-text interpretation
    and no per-object special case. The same knowledge base and the same repository always
    produce byte-identical verdicts. Every threshold is a DECLARED constant in `THRESHOLDS`
    below — declared once, applied uniformly, never tuned per object and never tuned to
    produce a desired outcome.

THE COMPARISON MODEL
    Sixteen declared architectural dimensions. Each dimension is measured INDEPENDENTLY on
    two sides, by two named functions:

        discovered side  the corpus record  — what the evidence establishes
        repository side  the measured presence — what Repository Truth currently carries

    Each side yields an ordinal in 0..2 (or None = not measurable from the available
    evidence). The dimension outcome is the comparison of the two ordinals:

        SUPERIOR      discovered > repository      the discovered form is measurably better
        EQUIVALENT    discovered == repository     no measurable difference
        INFERIOR      discovered < repository      Repository Truth is measurably better
        UNDECIDABLE   either side not measurable   recorded as such, never guessed

    Only fields that CARRY INFORMATION are used. `consumers` and `dependencies` are empty on
    every object in the knowledge base, and `implementation_status` is a copy of the measured
    presence level rather than an independent corpus claim; none of the three can express a
    comparison, so none is used as a measure. Using them would manufacture a signal.

VERDICTS
    Seven, applied in the declared precedence order of `VERDICT_RULES`. Five are the states
    the work package requires; NO_CURRENT_FORM and NOT_SUPERIOR exist so the evaluator is
    TOTAL — every presence-classified object receives exactly one verdict, and "no verdict"
    can never be a silent outcome.

AUTHORITY = NONE (DERIVED TRUTH). This module legislates nothing and ratifies nothing. It
measures and reports. Fail-closed (TRACK-001).
"""

from __future__ import annotations

# --------------------------------------------------------------------------- declared scales
# Ordinal scale shared by every dimension on both sides. Fixed, so a dimension can never
# invent its own range and quietly outweigh the others.
SCALE_MIN = 0
SCALE_MAX = 2

# Every numeric boundary used by any measure, declared ONCE. These are constitutional
# constants of the evaluation, not tunables: they are applied uniformly to every object and
# are recorded in the register so any verdict can be re-derived by hand.
THRESHOLDS: dict[str, int] = {
    "reuse_low": 2,            # conversations / files: below this is single-use
    "reuse_high": 4,           # at or above this is broad reuse
    "relations_high": 4,       # declared related-knowledge count treated as richly composed
    "aliases_high": 3,         # declared alternate names treated as a broad naming surface
    "normative_high": 3,       # normative statements treated as executable intent
    "duplication_high": 8,     # repository files carrying one concept before duplication cost
    "zone_spread_high": 2,     # distinct top-level zones before a concept boundary is spread
}

# Repository zones that are OPERATIONAL MEMORY rather than universal architecture. Presence
# confined to these is presence, but not universal carriage.
OPERATIONAL_MEMORY_ZONES = ("00-MASTER/", "01-WORKING/", "99-FREEZE/", ".runtime/", "dist/")

# Suffixes that make a carrier EXECUTABLE (automation / validation surface) rather than prose.
EXECUTABLE_SUFFIXES = (".py", ".sh", ".yml", ".yaml", ".toml", "Makefile")
# Suffixes that make a carrier DATA-DRIVEN (a scalable mechanism rather than an enumeration).
DATA_DRIVEN_SUFFIXES = (".json", ".yml", ".yaml", ".toml", ".py")

# Corpus authority field → governability ordinal (the corpus's own recorded authority class).
AUTHORITY_ORDINAL = {
    "ASSISTANT-PROPOSAL": 0,
    "USER-DIRECTIVE": 1,
    "SOURCE-RATIFIED": 2,
}

# Corpus hierarchy layer → scalability ordinal (declared layer, not an interpretation).
LAYER_ORDINAL = {
    "IMPLEMENTATION": 1,
    "OPERATIONAL": 1,
    "COMPONENT": 1,
    "STRUCTURAL": 2,
    "APEX": 2,
}

# Measured presence level → ordinal. ABSENT is 0; anything measured is at least 1.
PRESENCE_ORDINAL = {
    "ABSENT": 0,
    "REPO-PRESENT": 1,
    "REPO-DOCUMENTED": 1,
    "REPO-IMPLEMENTED": 2,
    "REPO-OPERATIONAL": 2,
    "REPO-CERTIFIED": 2,
}

# --------------------------------------------------------------------------- outcome legend
SUPERIOR = "SUPERIOR"
EQUIVALENT = "EQUIVALENT"
INFERIOR = "INFERIOR"
UNDECIDABLE = "UNDECIDABLE"

# Compact per-row encoding: one character per dimension, in declared dimension order. Sixteen
# characters replace sixteen stored objects per row, so the full evaluation of 23,859 objects
# stays diffable, replayable and small in version control.
OUTCOME_CHAR = {SUPERIOR: "+", EQUIVALENT: "=", INFERIOR: "-", UNDECIDABLE: "."}
CHAR_OUTCOME = {v: k for k, v in OUTCOME_CHAR.items()}

# --------------------------------------------------------------------------- verdict states
BETTER_THAN_CURRENT = "BETTER_THAN_CURRENT"
CONFLICTING = "CONFLICTING"
OBSOLETE = "OBSOLETE"
REQUIRES_ARCHITECTURAL_REVIEW = "REQUIRES_ARCHITECTURAL_REVIEW"
PARTIALLY_ASSIMILATED = "PARTIALLY_ASSIMILATED"
NO_CURRENT_FORM = "NO_CURRENT_FORM"
NOT_SUPERIOR = "NOT_SUPERIOR"

SUPERIORITY_STATES = [
    BETTER_THAN_CURRENT,
    CONFLICTING,
    OBSOLETE,
    REQUIRES_ARCHITECTURAL_REVIEW,
    PARTIALLY_ASSIMILATED,
    NO_CURRENT_FORM,
    NOT_SUPERIOR,
]

# The five states the work package mandates. Kept explicit so a test can prove they remain
# implemented and reachable, independently of the two totality states.
REQUIRED_STATES = [
    BETTER_THAN_CURRENT,
    CONFLICTING,
    OBSOLETE,
    REQUIRES_ARCHITECTURAL_REVIEW,
    PARTIALLY_ASSIMILATED,
]

# Dimensions whose INFERIOR outcome is a CONSTITUTIONAL objection: adopting a form that is
# worse on any of these cannot be a mechanical decision, so it escalates to review.
CONSTITUTIONAL_DIMENSIONS = (
    "D-10",  # Repository Truth compatibility
    "D-11",  # Knowledge Once
    "D-12",  # Single Source of Truth
    "D-13",  # Dependency correctness
    "D-14",  # Traceability
)

VERDICT_RATIONALE = {
    "SUP-1": "the corpus records this form as SUPERSEDED with no surviving acceptance, or the "
             "presence classification already placed it in a terminal SUPERSEDED state — the "
             "discovered form is obsolete and must never be silently revived",
    "SUP-2": "the evidence contradicts itself (the same object carries both acceptance and "
             "rejection decisions), or the repository carries as CERTIFIED what the evidence "
             "rejects — the conflict is recorded and referred, never resolved by this engine",
    "SUP-3": "Repository Truth carries no comparable form (absent, with no resolving anchor), "
             "so a superiority comparison is vacuous; the object's disposition is entirely a "
             "matter of the presence axis",
    "SUP-4": "Repository Truth carries the concept only partially: presence was corrected as "
             "weak, or the concept is represented only semantically under another identifier — "
             "the actionable finding is to finish assimilating what is already present",
    "SUP-5": "a superior form exists but cannot be adopted mechanically: a constitutional "
             "dimension would regress, or the net comparison is not positive, or the current "
             "form is REPO-CERTIFIED and would have to be decertified first",
    "SUP-6": "the discovered form is superior on strictly more dimensions than it is inferior, "
             "with no constitutional regression and no decertification required — it is "
             "objectively better than the form Repository Truth carries",
    "SUP-7": "no dimension is superior — the form Repository Truth carries stands",
}


# --------------------------------------------------------------------------- evidence structs
def _zones(examples: list[str]) -> list[str]:
    return sorted({e.split("/")[0] for e in examples if e})


def discovered_evidence(obj: dict, collides: bool, relations_resolved: int,
                        relations_declared: int) -> dict:
    """Corpus-side signals ONLY. Nothing measured from the repository appears here."""
    dp = obj.get("decision_profile") or {}
    return {
        "instance_level": bool(obj.get("is_instance_level")),
        "disposition": obj.get("ucos_disposition") or "NOT-UCOS",
        "authority": obj.get("authority") or "",
        "layer": obj.get("hierarchy_layer") or "",
        "relations_declared": relations_declared,
        "relations_resolved": relations_resolved,
        "aliases": len(obj.get("aliases") or []),
        "conversations": int(obj.get("origin_conversation_count") or 0),
        "normative": int(obj.get("normative_statements") or 0),
        "statements": len(obj.get("evidence") or []),
        "accepted": int(dp.get("DECISION_ACCEPTED") or 0),
        "rejected": int(dp.get("DECISION_REJECTED") or 0),
        "superseded": int(dp.get("DECISION_SUPERSEDED") or 0),
        "deferred": int(dp.get("DECISION_DEFERRED") or 0),
        "collides": collides,
    }


def repository_evidence(row: dict, anchors_resolve: int, deps_resolve: bool) -> dict:
    """Repository-side signals ONLY — every one of them measured by the presence pass."""
    examples = [str(a) for a in (row.get("anchors") or [])]
    return {
        "level": str(row.get("presence_level") or "ABSENT"),
        "hits": int(row.get("presence_hits") or 0),
        "corrected": bool(row.get("presence_corrected")),
        "state": str(row.get("state") or ""),
        "anchors": examples,
        "anchors_resolve": anchors_resolve,
        "zones": _zones(examples),
        "executable": any(e.endswith(EXECUTABLE_SUFFIXES) for e in examples),
        "data_driven": any(e.endswith(DATA_DRIVEN_SUFFIXES) for e in examples),
        "authority_exists": bool(row.get("authority")),
        "deps": len(row.get("dependencies") or []),
        "deps_resolve": deps_resolve,
        "equivalence": str(row.get("equivalence") or ""),
    }


def _present(rv: dict) -> bool:
    return rv["level"] != "ABSENT" or bool(rv["anchors"])


# --------------------------------------------------------------------------- D-01 Universality
def d01_discovered(ev: dict) -> int | None:
    if ev["instance_level"]:
        return 0
    return 1 if ev["disposition"] == "NOT-UCOS" else 2


def d01_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    if not rv["anchors"]:
        return 1
    universal = [a for a in rv["anchors"] if not a.startswith(OPERATIONAL_MEMORY_ZONES)]
    return 2 if universal else 1


# ------------------------------------------------------------------------- D-02 Composability
def d02_discovered(ev: dict) -> int | None:
    if ev["relations_declared"] == 0:
        return 0
    return 2 if ev["relations_declared"] >= THRESHOLDS["relations_high"] else 1


def d02_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 2 if rv["deps"] > 0 else 1


# ------------------------------------------------------------------------- D-03 Orthogonality
def d03_discovered(ev: dict) -> int | None:
    return 0 if ev["collides"] else 2


def d03_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    if not rv["zones"]:
        return 1
    return 1 if len(rv["zones"]) > THRESHOLDS["zone_spread_high"] else 2


# --------------------------------------------------------------------------- D-04 Reusability
def _reuse(n: int) -> int:
    if n >= THRESHOLDS["reuse_high"]:
        return 2
    return 1 if n >= THRESHOLDS["reuse_low"] else 0


def d04_discovered(ev: dict) -> int | None:
    return _reuse(ev["conversations"])


def d04_repository(rv: dict) -> int | None:
    return _reuse(rv["hits"])


# ------------------------------------------------------------------------- D-05 Extensibility
def d05_discovered(ev: dict) -> int | None:
    if ev["aliases"] == 0:
        return 0
    return 2 if ev["aliases"] >= THRESHOLDS["aliases_high"] else 1


def d05_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 2 if rv["executable"] else 1


# --------------------------------------------------------------------------- D-06 Scalability
def d06_discovered(ev: dict) -> int | None:
    if ev["instance_level"]:
        return 0
    return LAYER_ORDINAL.get(ev["layer"])


def d06_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 2 if rv["data_driven"] else 1


# ------------------------------------------------------------------------ D-07 Maintainability
def d07_discovered(ev: dict) -> int | None:
    if ev["collides"]:
        return 0
    return 2 if ev["normative"] > 0 else 1


def d07_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 1 if rv["hits"] > THRESHOLDS["duplication_high"] else 2


# ------------------------------------------------------------------------- D-08 Governability
def d08_discovered(ev: dict) -> int | None:
    return AUTHORITY_ORDINAL.get(ev["authority"])


def d08_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 2 if rv["authority_exists"] else 1


# ---------------------------------------------------------------------------- D-09 Automation
def d09_discovered(ev: dict) -> int | None:
    if ev["normative"] == 0:
        return 0
    return 2 if ev["normative"] >= THRESHOLDS["normative_high"] else 1


def d09_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 2 if rv["executable"] else 1


# ------------------------------------------------------- D-10 Repository Truth compatibility
def d10_discovered(ev: dict) -> int | None:
    if ev["rejected"] > 0:
        return 0
    return 1 if (ev["deferred"] > 0 and ev["accepted"] == 0) else 2


def d10_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    if rv["corrected"]:
        return 1
    # An anchor-only presence (no measured level) is carriage, but the weakest kind.
    return PRESENCE_ORDINAL.get(rv["level"], 1) if rv["level"] != "ABSENT" else 1


# ------------------------------------------------------------------------- D-11 Knowledge Once
def d11_discovered(ev: dict) -> int | None:
    return 0 if ev["collides"] else 2


def d11_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    dual = rv["state"] == "ASSIMILATED" and rv["level"] != "ABSENT"
    return 1 if (dual or len(rv["anchors"]) > 1) else 2


# ------------------------------------------------------------------ D-12 Single Source of Truth
def d12_discovered(ev: dict) -> int | None:
    if ev["collides"]:
        return 0
    return 1 if ev["aliases"] > 0 else 2


def d12_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 1 if len(rv["anchors"]) > 1 else 2


# ------------------------------------------------------------------ D-13 Dependency correctness
def d13_discovered(ev: dict) -> int | None:
    if ev["relations_declared"] == 0:
        return 2
    if ev["relations_resolved"] == 0:
        return 0
    return 2 if ev["relations_resolved"] == ev["relations_declared"] else 1


def d13_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    if rv["deps"] == 0:
        return 2
    return 2 if rv["deps_resolve"] else 0


# --------------------------------------------------------------------------- D-14 Traceability
def d14_discovered(ev: dict) -> int | None:
    if ev["conversations"] == 0:
        return 0
    return 2 if ev["statements"] > 0 else 1


def d14_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    if not rv["anchors"]:
        return 1
    return 2 if rv["anchors_resolve"] > 0 else 1


# ----------------------------------------------------------------------- D-15 Validation impact
def d15_discovered(ev: dict) -> int | None:
    if ev["normative"] == 0:
        return 0
    return 2 if ev["accepted"] > 0 else 1


def d15_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 2 if rv["executable"] else 1


# -------------------------------------------------------------------- D-16 Certification impact
def d16_discovered(ev: dict) -> int | None:
    if ev["accepted"] == 0:
        return 0
    return 2 if (ev["superseded"] == 0 and ev["rejected"] == 0) else 1


def d16_repository(rv: dict) -> int | None:
    if not _present(rv):
        return 0
    return 2 if rv["level"] == "REPO-CERTIFIED" else 1


# --------------------------------------------------------------------------- dimension catalog
DIMENSIONS: list[dict] = [
    dict(id="D-01", name="Universality", d=d01_discovered, r=d01_repository,
         discovered="0 instance-level · 1 disposition NOT-UCOS · 2 universal disposition",
         repository="0 absent · 1 carried only in operational-memory zones · 2 carried in a "
                    "universal architecture zone"),
    dict(id="D-02", name="Composability", d=d02_discovered, r=d02_repository,
         discovered="declared related knowledge: 0 none · 1 some · 2 at or above "
                    "`relations_high`",
         repository="0 absent · 1 present without a resolved dependency chain · 2 present with "
                    "a resolved dependency chain"),
    dict(id="D-03", name="Orthogonality", d=d03_discovered, r=d03_repository,
         discovered="0 the normalized name collides with another corpus object · 2 unique",
         repository="0 absent · 1 carried across more than `zone_spread_high` top-level zones · "
                    "2 carried within a single boundary"),
    dict(id="D-04", name="Reusability", d=d04_discovered, r=d04_repository,
         discovered="conversation reuse: 0 below `reuse_low` · 1 below `reuse_high` · 2 at or "
                    "above `reuse_high`",
         repository="repository file reuse, on the same scale"),
    dict(id="D-05", name="Extensibility", d=d05_discovered, r=d05_repository,
         discovered="declared alternate names: 0 none · 1 some · 2 at or above `aliases_high`",
         repository="0 absent · 1 carried only as prose · 2 carried by an executable extension "
                    "point"),
    dict(id="D-06", name="Scalability", d=d06_discovered, r=d06_repository,
         discovered="0 instance-level · declared hierarchy layer ordinal otherwise "
                    "(UNDECIDABLE when the layer is not recorded)",
         repository="0 absent · 1 carried as an enumeration in prose · 2 carried by a "
                    "data-driven mechanism"),
    dict(id="D-07", name="Maintainability", d=d07_discovered, r=d07_repository,
         discovered="0 the concept is restated in the corpus · 1 single form · 2 single form "
                    "carrying normative statements",
         repository="0 absent · 1 carried in more than `duplication_high` files · 2 carried "
                    "within that bound"),
    dict(id="D-08", name="Governability", d=d08_discovered, r=d08_repository,
         discovered="recorded corpus authority class ordinal (UNDECIDABLE when unrecorded)",
         repository="0 absent · 1 present without a named constitutional authority · 2 named "
                    "constitutional authority"),
    dict(id="D-09", name="Automation", d=d09_discovered, r=d09_repository,
         discovered="normative statements: 0 none · 1 some · 2 at or above `normative_high`",
         repository="0 absent · 1 carried only in prose · 2 carried by executable code"),
    dict(id="D-10", name="Repository Truth compatibility", d=d10_discovered, r=d10_repository,
         discovered="0 the corpus records a rejection · 1 deferred without acceptance · "
                    "2 uncontested or accepted",
         repository="0 absent · 1 weak presence (corrected) · 2 measured presence"),
    dict(id="D-11", name="Knowledge Once", d=d11_discovered, r=d11_repository,
         discovered="0 the corpus carries the concept more than once · 2 exactly once",
         repository="0 absent · 1 dual authority or several anchors · 2 exactly one "
                    "representation"),
    dict(id="D-12", name="Single Source of Truth", d=d12_discovered, r=d12_repository,
         discovered="0 collides · 1 several declared names for one concept · 2 single canonical "
                    "name",
         repository="0 absent · 1 more than one anchor · 2 at most one anchor"),
    dict(id="D-13", name="Dependency correctness", d=d13_discovered, r=d13_repository,
         discovered="0 no declared relation resolves · 1 some resolve · 2 all resolve (or none "
                    "declared)",
         repository="0 absent, or a recorded dependency does not resolve · 2 every recorded "
                    "dependency resolves"),
    dict(id="D-14", name="Traceability", d=d14_discovered, r=d14_repository,
         discovered="0 no origin conversation · 1 conversation only · 2 conversation and "
                    "statement evidence",
         repository="0 absent · 1 presence without a resolving anchor · 2 presence with a "
                    "resolving anchor"),
    dict(id="D-15", name="Validation impact", d=d15_discovered, r=d15_repository,
         discovered="0 nothing normative to validate · 1 normative statements · 2 normative "
                    "statements with an accepted decision",
         repository="0 absent · 1 prose only, no executable gate · 2 carried by code and "
                    "therefore gated"),
    dict(id="D-16", name="Certification impact", d=d16_discovered, r=d16_repository,
         discovered="0 no accepted decision · 1 accepted but contested · 2 accepted and never "
                    "superseded or rejected",
         repository="0 absent · 1 present below REPO-CERTIFIED · 2 REPO-CERTIFIED"),
]

DIMENSION_COUNT = len(DIMENSIONS)


def dimension_catalog() -> list[dict]:
    """The declared comparison model, for the machine model and the register. Emitted from the
    same declaration the evaluator executes, so documentation can never drift from behaviour."""
    return [{"id": dim["id"], "name": dim["name"], "discovered_measure": dim["discovered"],
             "repository_measure": dim["repository"],
             "constitutional": dim["id"] in CONSTITUTIONAL_DIMENSIONS}
            for dim in DIMENSIONS]


# --------------------------------------------------------------------------- comparison
def compare(discovered: int | None, repository: int | None) -> str:
    if discovered is None or repository is None:
        return UNDECIDABLE
    if discovered > repository:
        return SUPERIOR
    if discovered < repository:
        return INFERIOR
    return EQUIVALENT


def evaluate_dimensions(ev: dict, rv: dict) -> list[str]:
    """Outcome per dimension, in declared order. Pure function of the two evidence structs."""
    return [compare(dim["d"](ev), dim["r"](rv)) for dim in DIMENSIONS]


def encode(outcomes: list[str]) -> str:
    return "".join(OUTCOME_CHAR[o] for o in outcomes)


def decode(profile: str) -> list[str]:
    return [CHAR_OUTCOME[c] for c in profile]


# --------------------------------------------------------------------------- verdict
def verdict(outcomes: list[str], ev: dict, rv: dict) -> tuple[str, str]:
    """Deterministic verdict + the rule that decided it, in declared precedence order.

    Precedence is from MOST SPECIFIC measured fact to most residual, so a specific finding can
    never be swallowed by a general one:

        SUP-1  the evidence retired the form                       (obsolete)
        SUP-2  the evidence contradicts itself or certified truth   (conflicting)
        SUP-3  there is no current form to compare against         (vacuous)
        SUP-4  the current form is measurably incomplete           (partially assimilated)
        SUP-5  a superior form that cannot be adopted mechanically (review)
        SUP-6  a superior form that can                            (better than current)
        SUP-7  nothing is superior                                 (current form stands)
    """
    superior = [DIMENSIONS[i]["id"] for i, o in enumerate(outcomes) if o == SUPERIOR]
    inferior = [DIMENSIONS[i]["id"] for i, o in enumerate(outcomes) if o == INFERIOR]
    score = len(superior) - len(inferior)

    # SUP-1 obsolete — the evidence retired this form.
    if rv["state"] == "SUPERSEDED" or (ev["superseded"] > 0 and ev["accepted"] == 0):
        return OBSOLETE, "SUP-1"

    # SUP-2 conflicting — the evidence contradicts itself, or contradicts certified truth.
    if (ev["rejected"] > 0 and ev["accepted"] > 0) or (
            rv["state"] == "REJECTED" and rv["level"] != "ABSENT") or (
            rv["level"] == "REPO-CERTIFIED" and ev["rejected"] > 0):
        return CONFLICTING, "SUP-2"

    # SUP-3 nothing to compare against — the presence axis alone governs this object.
    if not _present(rv):
        return NO_CURRENT_FORM, "SUP-3"

    # SUP-4 the repository's own representation is incomplete. This is a MEASURED presence fact
    # and is reported ahead of the dimension comparison, because the actionable finding is
    # "finish assimilating what is already here". The score and profile are still recorded, so
    # no superiority information is lost by this precedence.
    if rv["corrected"] or rv["state"] == "SEMANTICALLY-REPRESENTED":
        return PARTIALLY_ASSIMILATED, "SUP-4"

    if superior:
        # A CONSTITUTIONAL dimension may never regress silently; a net that is not positive is
        # ambiguous rather than better; and a REPO-CERTIFIED counterpart would have to be
        # decertified to adopt the discovered form. Each is an architect's decision.
        constitutional_regression = any(d in CONSTITUTIONAL_DIMENSIONS for d in inferior)
        decertifies = rv["level"] == "REPO-CERTIFIED"
        if constitutional_regression or decertifies or score <= 0:
            return REQUIRES_ARCHITECTURAL_REVIEW, "SUP-5"
        return BETTER_THAN_CURRENT, "SUP-6"

    # SUP-7 the current form stands.
    return NOT_SUPERIOR, "SUP-7"


def evaluate(obj: dict, row: dict, *, collides: bool, relations_declared: int,
             relations_resolved: int, anchors_resolve: int, deps_resolve: bool) -> dict:
    """Evaluate ONE object that presence has already classified.

    Returns exactly the four columns the assimilation row gains. Never mutates `row`, never
    reads the filesystem, never consults a clock — every input is passed in by the caller,
    which is what makes the evaluation replayable and byte-identical.
    """
    ev = discovered_evidence(obj, collides, relations_resolved, relations_declared)
    rv = repository_evidence(row, anchors_resolve, deps_resolve)
    outcomes = evaluate_dimensions(ev, rv)
    state, rule = verdict(outcomes, ev, rv)
    return {
        "superiority": state,
        "superiority_score": (outcomes.count(SUPERIOR) - outcomes.count(INFERIOR)),
        "superiority_profile": encode(outcomes),
        "superiority_rule": rule,
    }


def blank() -> dict:
    """The backward-compatibility default: a row replayed from an assimilation.json written
    before this axis existed carries no verdict, and must not be silently invented. The
    UNEVALUATED marker is what the fail-closed gate detects."""
    return {
        "superiority": "",
        "superiority_score": 0,
        "superiority_profile": "." * DIMENSION_COUNT,
        "superiority_rule": "",
    }

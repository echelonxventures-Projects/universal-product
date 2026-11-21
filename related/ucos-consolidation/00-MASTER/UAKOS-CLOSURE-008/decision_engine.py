#!/usr/bin/env python3
"""UKAP-001 / WP-003 / D-3 — deterministic REPOSITORY DECISION & ACTION engine.

MISSION
    Presence (D-1/WP-001) answers "does Repository Truth already carry this knowledge?".
    Superiority (D-2/WP-002) answers "is the discovered form better, conflicting, obsolete,
    partially assimilated, or in need of architectural review?".

    This module answers the THIRD question, for every object BOTH prior axes have already
    evaluated: "WHAT MUST THE REPOSITORY DO?"

    It is the authoritative bridge between evaluation and future repository modification. It
    determines the action; it never performs it. No repository knowledge is read, written,
    rewritten, promoted or deleted here — the engine emits a governed decision, the declared
    repository operation that decision requires, its priority, its owner and its recorded
    grounds, and stops there.

    It is an EXTENSION of UAKOS-CLOSURE-008, not a replacement. It removes nothing: the six
    presence states and the seven superiority verdicts, with their rules, destinations, owners,
    authorities and waves, are untouched. The decision columns are APPENDED.

DETERMINISM (the hard constraint)
    Every input is a value already recorded on the assimilation row by an earlier axis. There
    is no randomness, no clock, no filesystem, no environment, no model judgement, no free-text
    interpretation and no per-object special case — this module imports NOTHING but
    `__future__`. The rule set is DECLARED once in `DECISION_RULES`, VERSIONED by
    `DECISION_VERSION`, applied in declared precedence order, and REPLAYABLE: `replay()`
    re-derives the decision from the recorded `decision_rationale` alone, so any decision in the
    register can be re-proved without the corpus, without the repository and without this
    engine's caller.

THE SIX REQUIRED ACTIONS
    ACCEPT                 admit knowledge Repository Truth does not carry
    MERGE                  complete a representation Repository Truth carries only partially
    SUPERSEDE              replace a form Repository Truth carries with a measurably better one
    REJECT                 admit nothing — the record IS the action
    ESCALATE_ARCHITECTURE  refer to the owning authority; no mechanical action is permitted
    DEFER                  registered and held until an authorization or prerequisite lands

    Exactly one action per evaluated object. `DEC-13` is the declared TOTALITY residual, so
    "no action" can never be a silent outcome — and because the residual firing would mean the
    rule set has a hole, its use is a BLOCKING gate failure rather than an accepted outcome.

FAIL-SAFE PRECEDENCE
    The rules are ordered from most specific measured fact to most residual, and where two
    clauses could both apply the NON-DESTRUCTIVE one wins. Escalation and rejection change no
    repository knowledge; adoption, merge and supersession do. So a conflict, an obsolescence, a
    retirement or a constitutional regression is decided BEFORE any adoption clause is reached,
    and no mechanical rule can ever overrule an architect.

AUTHORITY = NONE (DERIVED TRUTH). This module legislates nothing, ratifies nothing, certifies
no authority and creates no authority. It decides and records. Fail-closed (TRACK-001).
"""

from __future__ import annotations

# --------------------------------------------------------------------------- version
# The rule set is versioned so a decision can be attributed to the exact model that produced
# it. Any change to DECISION_RULES, ACTIONS, OPERATIONS, PRIORITY_POLICY or the rationale
# encoding is a version change; the assimilation engine additionally seals a digest of
# `ruleset_declaration()` into the machine register, so a silent edit cannot pass the drift gate.
DECISION_VERSION = "UKAP-001/WP-003/D-3/1.0.0"

# --------------------------------------------------------------------------- action registry
ACCEPT = "ACCEPT"
MERGE = "MERGE"
SUPERSEDE = "SUPERSEDE"
REJECT = "REJECT"
ESCALATE_ARCHITECTURE = "ESCALATE_ARCHITECTURE"
DEFER = "DEFER"

# Declared order — used for every rendered table so the register is stable under replay.
ACTIONS = [ACCEPT, MERGE, SUPERSEDE, REJECT, ESCALATE_ARCHITECTURE, DEFER]

# The ACTION REGISTRY. `modifies_knowledge` is the constitutional property that matters: it
# records whether executing the action would change repository knowledge. This engine executes
# NONE of them — the flag tells the destination owner what it is being asked to authorize.
ACTION_REGISTRY: dict[str, dict[str, object]] = {
    ACCEPT: dict(
        summary="admit knowledge Repository Truth does not carry, at its declared canonical "
                "destination",
        modifies_knowledge=True,
        executed_by="the destination owner declared by the presence axis, under its own "
                    "constitutional authority",
        precondition="the object is absent from Repository Truth, is homed, and its dependency "
                     "chain is closed"),
    MERGE: dict(
        summary="complete a representation Repository Truth already carries only partially, in "
                "the EXISTING anchor",
        modifies_knowledge=True,
        executed_by="the owner of the resolving repository anchor",
        precondition="a resolving anchor exists and no constitutional dimension would regress"),
    SUPERSEDE: dict(
        summary="replace the form Repository Truth carries with the measurably superior "
                "discovered form, preserving the supersession record",
        modifies_knowledge=True,
        executed_by="the owner of the resolving repository anchor",
        precondition="the discovered form is BETTER_THAN_CURRENT with no constitutional "
                     "regression and no decertification"),
    REJECT: dict(
        summary="admit nothing into Repository Truth; the recorded decision IS the action",
        modifies_knowledge=False,
        executed_by="no one — the decision is a record, not a change",
        precondition="none: rejection is always executable and always non-destructive"),
    ESCALATE_ARCHITECTURE: dict(
        summary="refer the object to the owning authority; no mechanical action is permitted",
        modifies_knowledge=False,
        executed_by="the owning authority, under its own constitution",
        precondition="none: escalation is always executable and always non-destructive"),
    DEFER: dict(
        summary="register the decision and HOLD it until an authorization or prerequisite lands",
        modifies_knowledge=False,
        executed_by="no one until the hold is released by the authorizing owner",
        precondition="none: a hold is always executable"),
}

# --------------------------------------------------------------------------- operation registry
# The named REPOSITORY OPERATION each decision requires. One action can require different
# operations depending on WHY it was decided — `REJECT` because history may never be promoted is
# a different repository operation from `REJECT` because Knowledge Once forbids a second home —
# so `implementation_action` is strictly more specific than `decision`, and each rule declares
# exactly one operation.
HOME_NEW_KNOWLEDGE = "HOME-NEW-KNOWLEDGE"
COMPLETE_EXISTING_REPRESENTATION = "COMPLETE-EXISTING-REPRESENTATION"
REPLACE_CURRENT_FORM = "REPLACE-CURRENT-FORM"
DISCARD_OBSOLETE = "DISCARD-OBSOLETE"
PRESERVE_RETIREMENT = "PRESERVE-RETIREMENT"
RETAIN_AS_HISTORY = "RETAIN-AS-HISTORY"
RETAIN_CURRENT_FORM = "RETAIN-CURRENT-FORM"
REFER_CONFLICT = "REFER-CONFLICT"
REFER_CONSTITUTIONAL_REGRESSION = "REFER-CONSTITUTIONAL-REGRESSION"
REFER_ARCHITECTURAL_REVIEW = "REFER-ARCHITECTURAL-REVIEW"
REGISTER_AND_HOLD = "REGISTER-AND-HOLD"

# The IMPLEMENTATION PLAN GENERATOR's declared source. Each operation carries an ORDERED step
# sequence with named placeholders resolved per object by `plan_for()`. The plan is declared
# once per operation rather than stored per row, exactly as the presence axis carries its rule
# rationale once per rule — 23,859 copies of the same prose would be duplication, not evidence.
OPERATIONS: dict[str, dict[str, object]] = {
    HOME_NEW_KNOWLEDGE: dict(
        action=ACCEPT,
        summary="author the absent knowledge at its declared canonical destination",
        steps=[
            "{owner} re-confirms at the current HEAD that Repository Truth still carries no "
            "form of this object",
            "author the knowledge at `{destination}`, governed by `{authority}`",
            "record the dependency chain ({dependencies}) and the evidence provenance "
            "({evidence})",
            "re-run `make assimilate-gate`: the object MUST re-classify as ALREADY-REPRESENTED, "
            "which is the executable proof the action landed",
            "regenerate the registers so this decision is re-derived from the new repository "
            "state rather than asserted",
        ]),
    COMPLETE_EXISTING_REPRESENTATION: dict(
        action=MERGE,
        summary="extend the EXISTING anchor so the partial representation becomes complete",
        steps=[
            "{owner} opens the resolving anchor `{anchor}`",
            "read the superiority profile `{profile}` to identify precisely which declared "
            "dimensions the current form does not yet satisfy",
            "extend the EXISTING anchor — creating a second home is prohibited (Knowledge Once)",
            "re-run `make assimilate-gate`: presence MUST strengthen and `presence_corrected` "
            "MUST clear",
            "regenerate the registers so the decision is re-derived",
        ]),
    REPLACE_CURRENT_FORM: dict(
        action=SUPERSEDE,
        summary="replace the inferior current form, preserving the supersession record",
        steps=[
            "{owner} records the current form at `{anchor}` as SUPERSEDED — never deleted",
            "author the superior form at the SAME canonical home, preserving the identifier",
            "carry the supersession record forward so the replacement can never be silently "
            "reversed",
            "re-run `make assimilate-gate` and `./verify.sh`",
            "regenerate the registers so the decision is re-derived",
        ]),
    DISCARD_OBSOLETE: dict(
        action=REJECT,
        summary="admit nothing: the evidence itself retired this form",
        steps=[
            "admit nothing into Repository Truth — the evidence records this form as retired",
            "keep the obsolescence recorded in `{register}` so the form is never silently revived",
            "no repository modification is required: the decision IS the action",
        ]),
    PRESERVE_RETIREMENT: dict(
        action=REJECT,
        summary="preserve the terminal retirement the presence axis already recorded",
        steps=[
            "preserve the terminal retirement recorded by the presence axis (`{presence_state}`)",
            "admit nothing — reversing a retirement is the owning authority's act, never this "
            "engine's",
            "no repository modification is required: the decision IS the action",
        ]),
    RETAIN_AS_HISTORY: dict(
        action=REJECT,
        summary="retain as project history; promotion is prohibited",
        steps=[
            "retain the object as project execution history in the read-only evidence corpus",
            "admit nothing into Repository Truth — promotion of instance-level or NOT-UCOS "
            "history is prohibited",
            "no repository modification is required: the decision IS the action",
        ]),
    RETAIN_CURRENT_FORM: dict(
        action=REJECT,
        summary="the current form stands; a second home would violate Knowledge Once",
        steps=[
            "Repository Truth already carries this object at `{anchor}` and nothing measured is "
            "superior",
            "admit nothing — a second home for one concept would violate Knowledge Once",
            "no repository modification is required: the decision IS the action",
        ]),
    REFER_CONFLICT: dict(
        action=ESCALATE_ARCHITECTURE,
        summary="refer a contradiction; the engine resolves nothing",
        steps=[
            "refer the contradiction to {owner}",
            "the evidence contradicts itself, or certified Repository Truth carries what the "
            "evidence rejects — this engine resolves neither",
            "the owning authority records its determination under its own constitution",
            "re-run the decision engine: the decision is RE-DERIVED from the resolved evidence, "
            "never overwritten by hand",
        ]),
    REFER_CONSTITUTIONAL_REGRESSION: dict(
        action=ESCALATE_ARCHITECTURE,
        summary="refer an adoption that would regress a constitutional dimension",
        steps=[
            "refer to {owner}: acting mechanically here would regress a CONSTITUTIONAL dimension",
            "the regressing dimensions are recorded in the superiority profile `{profile}`",
            "no mechanical action is permitted — a constitutional regression is an architect's "
            "decision by construction",
            "re-run the decision engine after the determination",
        ]),
    REFER_ARCHITECTURAL_REVIEW: dict(
        action=ESCALATE_ARCHITECTURE,
        summary="refer a superior form that cannot be adopted mechanically",
        steps=[
            "refer to {owner}: a superior form exists but cannot be adopted mechanically",
            "the review decides between adoption, merge and retention of the current form",
            "this engine performs no repository modification and recommends no outcome",
            "re-run the decision engine after the determination",
        ]),
    REGISTER_AND_HOLD: dict(
        action=DEFER,
        summary="registered at its destination and held until authorization",
        steps=[
            "the object is REGISTERED at `{destination}` under {owner}, and HELD",
            "the hold is the presence axis's Wave F: the maturity evidence carries no human "
            "commitment, so scheduling it would fabricate one",
            "no repository modification is permitted while the hold stands",
            "on authorization the object re-enters the active waves and the decision is "
            "RE-DERIVED",
        ]),
}

# --------------------------------------------------------------------------- priority policy
IMMEDIATE = "IMMEDIATE"
HIGH = "HIGH"
SCHEDULED = "SCHEDULED"
HELD = "HELD"
NONE = "NONE"

PRIORITIES = [IMMEDIATE, HIGH, SCHEDULED, HELD, NONE]

PRIORITY_RATIONALE = {
    IMMEDIATE: "a constitutional dimension would regress — the highest repository risk the "
               "evaluation can express, and the only class that is unsafe to leave open",
    HIGH: "a contradiction, an architectural review or a supersession of live Repository Truth: "
          "the repository currently carries something the evaluation disputes",
    SCHEDULED: "an admission or a completion in an ACTIVE wave — ordinary scheduled work, "
               "ordered by the wave the presence axis assigned",
    HELD: "registered but authorization-gated (Wave F); no work may start and none is scheduled",
    NONE: "the decision is a record, not a change — there is nothing to implement",
}

# Declared priority per action. Refined by exactly one declared condition (a constitutional
# regression promotes an escalation to IMMEDIATE); nothing else varies, so priority is a pure
# function of the decision and the recorded grounds.
PRIORITY_POLICY: dict[str, str] = {
    ACCEPT: SCHEDULED,
    MERGE: SCHEDULED,
    SUPERSEDE: HIGH,
    REJECT: NONE,
    ESCALATE_ARCHITECTURE: HIGH,
    DEFER: HELD,
}


def priority_for(decision: str, objection: bool) -> str:
    """The declared implementation priority. Deterministic, total, and refined by one rule."""
    if decision == ESCALATE_ARCHITECTURE and objection:
        return IMMEDIATE
    return PRIORITY_POLICY.get(decision, NONE)


# --------------------------------------------------------------------------- owner policy
# The referral ADDRESS for an object whose presence axis assigned no destination owner: the
# canonical owner of the repository zone that carries the anchor. These are EXISTING repository
# authorities and existing zone names; naming one creates no authority and grants none. Where
# the presence axis already recorded an owner (every homed object), that owner wins and this
# table is not consulted at all.
ZONE_OWNER: dict[str, str] = {
    "00-BOOK": "Universal Master Book Authority (00-BOOK)",
    "00-CEP": "Constitutional Engineering Programme Authority (00-CEP)",
    "00-CMG": "Constitutional Meta-Governance Authority (00-CMG)",
    "00-MASTER": "Master Program Authority (00-MASTER)",
    "00-SOURCE": "Source Evidence Authority (00-SOURCE)",
    "00-SOURCE-MANIFEST": "Source Manifest Authority (00-SOURCE-MANIFEST)",
    "01-WORKING": "Constitutional Reconciliation Authority (01-WORKING)",
    "02-MASTER": "Master Program Authority (02-MASTER)",
    "03-CATALOGS": "Canonical Catalog Authority (03-CATALOGS)",
    "04-REFERENCE": "Canonical Reference Authority (04-REFERENCE)",
    "05-GENERATION": "Generation / Factory Authority (05-GENERATION)",
    "06-IMPLEMENTATION": "Implementation Authority (06-IMPLEMENTATION)",
    "07-ENGINEERING": "Engineering Architecture Authority (07-ENGINEERING)",
    "08-RUNTIME": "Runtime Authority (08-RUNTIME)",
    "09-PLATFORM": "Universal Platform Authority (09-PLATFORM)",
    "10-DATA": "Data Authority (10-DATA)",
    "11-SERVICE": "Service Authority (11-SERVICE)",
    "12-APPLICATION": "Application Authority (12-APPLICATION)",
    "13-INFRASTRUCTURE": "Infrastructure Authority (13-INFRASTRUCTURE)",
    "14-SECURITY": "Security Authority (14-SECURITY)",
    "15-UNIVERSAL-SCIENCE-INTELLIGENCE": "Universal Science Intelligence Authority (15-USI)",
    "99-FREEZE": "Architecture Freeze Authority (99-FREEZE)",
    "adr": "Architecture Decision Record Authority (adr/)",
    "application": "Application Implementation Authority (application/)",
    "data": "Data Implementation Authority (data/)",
    "determinism-evidence": "Determinism Evidence Authority (determinism-evidence/)",
    "dist": "Distribution Authority (dist/)",
    "engine": "Engine Implementation Authority (engine/)",
    "infrastructure": "Infrastructure Implementation Authority (infrastructure/)",
    "intelligence": "Intelligence Implementation Authority (intelligence/)",
    "knowledge": "Knowledge Implementation Authority (knowledge/)",
    "platform": "Platform Implementation Authority (platform/)",
    "realization": "Realization Authority (realization/)",
    "scripts": "Operations Tooling Authority (scripts/)",
    "service": "Service Implementation Authority (service/)",
    ".github": "CI Gate Authority (.github/)",
    ".kiro": "Workspace Configuration Authority (.kiro/)",
    ".runtime": "Runtime Operational Memory Authority (.runtime/)",
    "EVO-USIS-014": "Evolution Programme Authority (EVO-USIS-014)",
    "EVO-USIS-015": "Evolution Programme Authority (EVO-USIS-015)",
    "EVO-USIS-016": "Evolution Programme Authority (EVO-USIS-016)",
    "IAC-001A": "Integrated Assimilation Programme Authority (IAC-001A)",
    "IAC-001B": "Integrated Assimilation Programme Authority (IAC-001B)",
    "IAC-001C": "Integrated Assimilation Programme Authority (IAC-001C)",
    "IAC-001D": "Integrated Assimilation Programme Authority (IAC-001D)",
    "IAC-001E": "Integrated Assimilation Programme Authority (IAC-001E)",
}

# An anchor at the repository root is a single file, not a zone; its owner is the repository
# root itself, which is an existing (and named) authority surface.
ROOT_OWNER = "Repository Root Authority (repository root)"

# The register that carries every decision this engine emits. It is the referral address for an
# object with no destination and no resolving anchor: the decision is the record, and the record
# lives here. It is NOT a new authority — it is this program's own operational-memory home.
REGISTER_OWNER = "Assimilation Decision Register (00-MASTER/UAKOS-CLOSURE-008)"
REGISTER_PATH = "00-MASTER/UAKOS-CLOSURE-008/10-REPOSITORY-DECISION-REGISTER.md"


def zone_of(anchor: str) -> str:
    """The declared top-level repository zone that carries an anchor. Anchors may carry a
    `path:detail` suffix, matching the presence axis's semantic-mapping convention."""
    return anchor.split(":")[0].split("/")[0]


def owner_for(row: dict) -> str:
    """The IMPLEMENTATION OWNER, in declared precedence order. Total: never empty.

    1. the owner the PRESENCE axis already assigned (every homed object) — never overridden
    2. the canonical owner of the zone carrying the first resolving anchor
    3. the decision register itself, for an object with neither a destination nor an anchor
       (its decision requires no repository modification, so the record is the whole action)
    """
    declared = str(row.get("owner") or "").strip()
    if declared:
        return declared
    anchors = [str(a) for a in (row.get("anchors") or []) if str(a).strip()]
    if anchors:
        zone = zone_of(anchors[0])
        if zone in ZONE_OWNER:
            return ZONE_OWNER[zone]
        # A root-level file is a file, not a zone. Anything else is addressed by its zone name,
        # which names an existing repository location and invents no authority.
        return ROOT_OWNER if "." in zone else f"Repository Truth owner of `{zone}`"
    return REGISTER_OWNER


# --------------------------------------------------------------------------- grounds encoding
# The RECORDED GROUNDS of a decision: the measured facts, and only the measured facts, that the
# rule set is allowed to read. Every one is a value an earlier axis already wrote onto the row.
#
# Encoded as one compact, fixed-order, self-describing token string per object, so the register
# carries this object's grounds (not a repeated copy of the general clause, which is carried
# once per rule in DECISION_RULES) and so `replay()` can re-derive the decision from the
# register alone.
PRESENCE_CLASSES = ["NOT_PRESENT", "PARTIALLY_PRESENT", "PRESENT", "RETIRED"]

PRESENCE_CLASS_CODE = {
    "NOT_PRESENT": "NP",
    "PARTIALLY_PRESENT": "PP",
    "PRESENT": "PR",
    "RETIRED": "RT",
}

PRESENCE_STATE_CODE = {
    "ALREADY-REPRESENTED": "AR",
    "SEMANTICALLY-REPRESENTED": "SR",
    "ASSIMILATED": "AS",
    "HISTORICAL-EVIDENCE-ONLY": "HE",
    "SUPERSEDED": "SS",
    "REJECTED": "RJ",
}

SUPERIORITY_CODE = {
    "BETTER_THAN_CURRENT": "BTC",
    "CONFLICTING": "CFL",
    "OBSOLETE": "OBS",
    "REQUIRES_ARCHITECTURAL_REVIEW": "RAR",
    "PARTIALLY_ASSIMILATED": "PAS",
    "NO_CURRENT_FORM": "NCF",
    "NOT_SUPERIOR": "NSU",
    "": "UNEVALUATED",
}

DEPENDENCY_CODE = {"NONE": "N", "CLOSED": "C", "OPEN": "O"}
TRACE_CODE = {"ADDRESSED": "T", "REGISTER_ONLY": "U"}

# The declared key order of `decision_rationale`. Fixed, because the string is parsed on replay.
GROUNDS_KEYS = ("P", "Q", "S", "C", "N", "D", "T", "W")

GROUNDS_LEGEND = {
    "P": "presence class, projected from the presence axis (NP not present · PP partially "
         "present · PR present · RT retired)",
    "Q": "terminal presence state (AR already-represented · SR semantically-represented · "
         "AS assimilated · HE historical-evidence-only · SS superseded · RJ rejected)",
    "S": "superiority verdict (BTC · CFL · OBS · RAR · PAS · NCF · NSU · UNEVALUATED)",
    "C": "constitutional objection — 1 when a constitutional dimension is measurably INFERIOR",
    "N": "net superiority score (superior dimensions minus inferior dimensions)",
    "D": "dependency closure of the recorded chain (N none declared · C closed · O open)",
    "T": "traceability of the decision's address — T the object carries evidence provenance AND "
         "a repository address of its own (a resolving anchor or a canonical destination) · "
         "U evidence provenance only, so the decision register itself is the address, which is "
         "correct for every action that modifies no repository knowledge",
    "W": "the wave the presence axis assigned (1..7 active · F future/authorization-gated · "
         "'-' none)",
}

# Waves that carry an evidenced human commitment, i.e. work the presence axis SCHEDULED. Wave F
# is registered but authorization-gated and is therefore not active; '-' means no wave applies.
ACTIVE_WAVES = ("1", "2", "3", "4", "5", "6", "7")
FUTURE_WAVE = "F"


def presence_class(presence_state: str, presence_level: str, has_anchor: bool) -> str:
    """Project the presence axis onto the four decision-relevant classes.

    A PROJECTION, never a re-classification: it reads the presence columns and writes nothing.
    Declared precedence, so the projection is total and single-valued:

        RETIRED            the presence axis reached a terminal retired state
        NOT_PRESENT        no measured level and no anchor — Repository Truth carries nothing
        PARTIALLY_PRESENT  measured, but only weakly or only under another identifier
        PRESENT            Repository Truth carries a comparable form
    """
    if presence_state in ("SUPERSEDED", "REJECTED"):
        return "RETIRED"
    if presence_level == "ABSENT" and not has_anchor:
        return "NOT_PRESENT"
    if presence_state == "SEMANTICALLY-REPRESENTED":
        return "PARTIALLY_PRESENT"
    return "PRESENT"


def grounds_of(row: dict, *, objection: bool, deps_closed: bool) -> dict:
    """The measured grounds for ONE row. Pure function of the row plus two facts the caller
    computed across rows (the constitutional objection decoded from the superiority profile, and
    whether the recorded dependency chain resolves inside the register)."""
    state = str(row.get("state") or "")
    level = str(row.get("presence_level") or "ABSENT")
    anchors = [str(a) for a in (row.get("anchors") or []) if str(a).strip()]
    corrected = bool(row.get("presence_corrected"))
    deps = [d for d in (row.get("dependencies") or []) if d]
    wave = str(row.get("wave") or "").strip() or "-"
    traced = int(row.get("origin_conversations") or 0) >= 1 and bool(
        anchors or str(row.get("destination") or "").strip())
    cls = presence_class(state, level, bool(anchors))
    # A weak (corrected) presence is a MEASURED incompleteness, so it downgrades PRESENT to
    # PARTIALLY_PRESENT. It never upgrades anything, and it never touches the presence columns.
    if cls == "PRESENT" and corrected:
        cls = "PARTIALLY_PRESENT"
    return {
        "P": cls,
        "Q": state,
        "S": str(row.get("superiority") or ""),
        "C": bool(objection),
        "N": int(row.get("superiority_score") or 0),
        "D": "NONE" if not deps else ("CLOSED" if deps_closed else "OPEN"),
        "T": "ADDRESSED" if traced else "REGISTER_ONLY",
        "W": wave,
    }


def encode_grounds(g: dict) -> str:
    """`decision_rationale`: this object's grounds, in declared key order."""
    return "|".join([
        f"P:{PRESENCE_CLASS_CODE[g['P']]}",
        f"Q:{PRESENCE_STATE_CODE.get(g['Q'], '--')}",
        f"S:{SUPERIORITY_CODE.get(g['S'], 'UNEVALUATED')}",
        f"C:{1 if g['C'] else 0}",
        f"N:{int(g['N']):+d}",
        f"D:{DEPENDENCY_CODE[g['D']]}",
        f"T:{TRACE_CODE[g['T']]}",
        f"W:{g['W']}",
    ])


def decode_grounds(rationale: str) -> dict:
    """Invert `encode_grounds`. This is what makes a decision REPLAYABLE from the register
    alone: no corpus, no repository and no caller are required to re-prove it."""
    parts = dict(part.split(":", 1) for part in str(rationale).split("|") if ":" in part)
    if tuple(part.split(":", 1)[0] for part in str(rationale).split("|")) != GROUNDS_KEYS:
        raise ValueError(f"malformed decision_rationale: {rationale!r}")
    inv_p = {v: k for k, v in PRESENCE_CLASS_CODE.items()}
    inv_q = {v: k for k, v in PRESENCE_STATE_CODE.items()}
    inv_s = {v: k for k, v in SUPERIORITY_CODE.items()}
    inv_d = {v: k for k, v in DEPENDENCY_CODE.items()}
    inv_t = {v: k for k, v in TRACE_CODE.items()}
    return {
        "P": inv_p[parts["P"]],
        "Q": inv_q.get(parts["Q"], ""),
        "S": inv_s[parts["S"]],
        "C": parts["C"] == "1",
        "N": int(parts["N"]),
        "D": inv_d[parts["D"]],
        "T": inv_t[parts["T"]],
        "W": parts["W"],
    }


# --------------------------------------------------------------------------- decision rules
# THE DECLARED RULE SET. Ordered, versioned, total and replayable. Each rule is a named clause
# over the recorded grounds and NOTHING else: `when` receives the grounds dict and may read no
# other value, which is exactly why `replay()` from the rationale is sound.
#
# Precedence is FAIL-SAFE: every clause that changes no repository knowledge (escalate, reject,
# hold) is reached before every clause that does (accept, merge, supersede). A conflict, an
# obsolescence, a retirement or a constitutional regression therefore always wins over an
# adoption, and no mechanical rule can overrule an architect.
DECISION_RULES: list[dict] = [
    dict(
        id="DEC-01", action=ESCALATE_ARCHITECTURE, operation=REFER_CONFLICT,
        clause="Superiority = CONFLICTING",
        when=lambda g: g["S"] == "CONFLICTING",
        rationale="the evidence contradicts itself, or certified Repository Truth carries what "
                  "the evidence rejects. A contradiction has no mechanical resolution: acting "
                  "either way would ratify one half of a contradiction, so the object is "
                  "referred and nothing is changed. Decided FIRST because escalation is the "
                  "only action that cannot make a contradiction worse."),
    dict(
        id="DEC-02", action=REJECT, operation=DISCARD_OBSOLETE,
        clause="Superiority = OBSOLETE",
        when=lambda g: g["S"] == "OBSOLETE",
        rationale="the evidence itself retired this form. Admitting it would revive knowledge "
                  "the corpus already replaced, so the repository admits nothing and keeps the "
                  "obsolescence recorded. Non-destructive, hence decided before any adoption."),
    dict(
        id="DEC-03", action=REJECT, operation=PRESERVE_RETIREMENT,
        clause="Presence = RETIRED (the presence axis reached SUPERSEDED or REJECTED)",
        when=lambda g: g["P"] == "RETIRED",
        rationale="the presence axis already drove this object to a terminal retired state. The "
                  "repository's action is to PRESERVE that retirement: reversing it belongs to "
                  "the owning authority under its own constitution, never to this engine."),
    dict(
        id="DEC-04", action=ESCALATE_ARCHITECTURE, operation=REFER_CONSTITUTIONAL_REGRESSION,
        clause="a constitutional dimension is measurably INFERIOR (constitutional regression)",
        when=lambda g: g["C"],
        rationale="acting mechanically would weaken Repository Truth compatibility, Knowledge "
                  "Once, Single Source of Truth, dependency correctness or traceability. A "
                  "constitutional regression is an architect's decision by construction, so it "
                  "outranks every adoption, merge and hold clause below it."),
    dict(
        id="DEC-05", action=REJECT, operation=RETAIN_AS_HISTORY,
        clause="Presence state = HISTORICAL-EVIDENCE-ONLY",
        when=lambda g: g["Q"] == "HISTORICAL-EVIDENCE-ONLY",
        rationale="the presence axis measured this as instance-level project execution history "
                  "or explicitly NOT-UCOS knowledge. It is retained as evidence and never "
                  "promoted, so the repository admits nothing — including by merge, which would "
                  "promote history into universal architecture through the side door."),
    dict(
        id="DEC-06", action=DEFER, operation=REGISTER_AND_HOLD,
        clause="the presence axis assigned Wave F (future / authorization-gated)",
        when=lambda g: g["W"] == FUTURE_WAVE,
        rationale="the object is registered with a canonical destination but its maturity "
                  "evidence carries no human commitment. Scheduling it would fabricate a "
                  "commitment the evidence does not contain, so the decision is declared and "
                  "HELD. Decided before the adoption clauses because a hold is non-destructive "
                  "and an unauthorized admission is not."),
    dict(
        id="DEC-07", action=MERGE, operation=COMPLETE_EXISTING_REPRESENTATION,
        clause="Superiority = PARTIALLY_ASSIMILATED",
        when=lambda g: g["S"] == "PARTIALLY_ASSIMILATED",
        rationale="Repository Truth carries the concept, but only weakly or only under another "
                  "identifier. The actionable repository operation is to COMPLETE the existing "
                  "anchor, never to open a second home — reaching this clause already proves no "
                  "constitutional dimension would regress, because DEC-04 outranks it."),
    dict(
        id="DEC-08", action=SUPERSEDE, operation=REPLACE_CURRENT_FORM,
        clause="Presence carries a comparable form AND Superiority = BETTER_THAN_CURRENT",
        when=lambda g: g["S"] == "BETTER_THAN_CURRENT" and g["P"] in ("PRESENT",
                                                                     "PARTIALLY_PRESENT"),
        rationale="Repository Truth carries a form that is measurably inferior on strictly more "
                  "declared dimensions than it is superior, with no constitutional regression "
                  "and no decertification required. The repository operation is SUPERSESSION of "
                  "the current form at its existing canonical home — not a second home, and not "
                  "a deletion."),
    dict(
        id="DEC-09", action=ACCEPT, operation=HOME_NEW_KNOWLEDGE,
        clause="Presence = NOT_PRESENT AND Superiority = BETTER_THAN_CURRENT",
        when=lambda g: g["P"] == "NOT_PRESENT" and g["S"] == "BETTER_THAN_CURRENT",
        rationale="the work package's declared first principle, declared here verbatim. It is "
                  "STRUCTURALLY UNREACHABLE on any corpus and is retained to make that fact "
                  "provable rather than hidden: the superiority axis returns NO_CURRENT_FORM "
                  "(rule SUP-3) for exactly the objects this clause calls NOT_PRESENT, because "
                  "a comparison against nothing is vacuous. The reachable form of the same "
                  "principle is DEC-10."),
    dict(
        id="DEC-10", action=ACCEPT, operation=HOME_NEW_KNOWLEDGE,
        clause="Presence = NOT_PRESENT AND presence state = ASSIMILATED AND the wave is ACTIVE",
        when=lambda g: (g["P"] == "NOT_PRESENT" and g["Q"] == "ASSIMILATED"
                        and g["W"] in ACTIVE_WAVES),
        rationale="Repository Truth carries no form of this object, the presence axis approved "
                  "it as missing knowledge and homed it with a destination, owner, "
                  "constitutional authority and an ACTIVE wave, and its superiority verdict is "
                  "NO_CURRENT_FORM — which for an absent object IS 'better than what Repository "
                  "Truth carries', because Repository Truth carries nothing. This is the "
                  "reachable expression of DEC-09."),
    dict(
        id="DEC-11", action=ESCALATE_ARCHITECTURE, operation=REFER_ARCHITECTURAL_REVIEW,
        clause="Superiority = REQUIRES_ARCHITECTURAL_REVIEW",
        when=lambda g: g["S"] == "REQUIRES_ARCHITECTURAL_REVIEW",
        rationale="the superiority axis measured a superior form that cannot be adopted "
                  "mechanically: the net comparison is not positive, or the current form is "
                  "REPO-CERTIFIED and would have to be decertified first. Converting that into "
                  "a mechanical repository action would overrule an architect."),
    dict(
        id="DEC-12", action=REJECT, operation=RETAIN_CURRENT_FORM,
        clause="Presence carries the object AND nothing measured is superior",
        when=lambda g: g["P"] in ("PRESENT", "PARTIALLY_PRESENT") and g["S"] in (
            "NOT_SUPERIOR", "NO_CURRENT_FORM"),
        rationale="Repository Truth already carries the object and no dimension is superior. The "
                  "repository admits nothing: a second home for one concept would violate "
                  "Knowledge Once, so the current form stands and the decision is the record."),
    dict(
        id="DEC-13", action=ESCALATE_ARCHITECTURE, operation=REFER_ARCHITECTURAL_REVIEW,
        clause="TOTALITY RESIDUAL — no declared clause above matched",
        when=lambda g: True,
        rationale="the declared TOTALITY residual, so that 'no action' can never be a silent "
                  "outcome: an object that matches no clause is referred to an architect rather "
                  "than escaping the engine. Its use means the rule set has a HOLE, so a single "
                  "occurrence is a BLOCKING gate failure rather than an accepted outcome — the "
                  "residual exists to be provably empty."),
]

RULE_IDS = [r["id"] for r in DECISION_RULES]
RESIDUAL_RULE = DECISION_RULES[-1]["id"]

# A declared rule may legitimately not fire on a given corpus. Two reasons are legitimate and
# both must be DECLARED, because an undeclared silent rule is indistinguishable from dead code:
#
#   STRUCTURAL  the clause is empty by construction on EVERY corpus, not merely on this one
#   GUARD       the clause defends against a row state an earlier axis's own gate prevents
#
# The assimilation engine blocks on any silent rule that has no entry here.
SILENT_RULES: dict[str, dict[str, str]] = {
    "DEC-09": dict(
        kind="STRUCTURAL",
        reason="the superiority axis assigns NO_CURRENT_FORM (rule SUP-3) to exactly the objects "
               "this clause calls NOT_PRESENT, because a comparison against nothing is vacuous. "
               "`NOT_PRESENT AND BETTER_THAN_CURRENT` is therefore empty by construction on "
               "every corpus. The clause is declared verbatim from the work package so the fact "
               "is provable rather than hidden; DEC-10 is the reachable expression of the same "
               "principle."),
}


# --------------------------------------------------------------------------- decide / replay
def apply_rules(g: dict) -> dict:
    """The rule engine: the FIRST declared clause whose condition holds, and nothing else.

    Single-valued and total by construction — `DEC-13` matches unconditionally, so the loop can
    never fall through and no object can leave without exactly one rule and one action.
    """
    for rule in DECISION_RULES:
        if rule["when"](g):
            return rule
    raise AssertionError("unreachable: the totality residual DEC-13 matches unconditionally")


def replay(rationale: str) -> dict:
    """Re-derive a decision from its RECORDED GROUNDS alone.

    This is the executable form of "deterministic replay": given only the `decision_rationale`
    string committed in the register, the same rule set reproduces the same decision, the same
    rule, the same repository operation and the same priority — with no corpus, no repository,
    no caller and no stored decision consulted. The validation gate runs this over every row and
    fails closed on any divergence.
    """
    g = decode_grounds(rationale)
    rule = apply_rules(g)
    return {
        "decision": str(rule["action"]),
        "decision_rule": str(rule["id"]),
        "implementation_action": str(rule["operation"]),
        "implementation_priority": priority_for(str(rule["action"]), bool(g["C"])),
    }


def decide(row: dict, *, objection: bool, deps_closed: bool) -> dict:
    """Decide ONE object that presence AND superiority have already evaluated.

    Returns exactly the five columns the assimilation row gains. Never mutates `row`, never
    reads the filesystem, never consults a clock, and never touches a presence or superiority
    field — which is what keeps the prior axes bit-for-bit intact and the decision replayable.
    """
    g = grounds_of(row, objection=objection, deps_closed=deps_closed)
    rationale = encode_grounds(g)
    rule = apply_rules(g)
    return {
        "decision": str(rule["action"]),
        "decision_rule": str(rule["id"]),
        "decision_rationale": rationale,
        "implementation_action": str(rule["operation"]),
        "implementation_priority": priority_for(str(rule["action"]), bool(g["C"])),
    }


def blank() -> dict:
    """The backward-compatibility default: a row replayed from an `assimilation.json` written
    before this axis existed carries no decision, and must not be given a fabricated one. The
    empty decision is what the fail-closed D-3 gates detect."""
    return {
        "decision": "",
        "decision_rule": "",
        "decision_rationale": "",
        "implementation_action": "",
        "implementation_priority": "",
    }


# --------------------------------------------------------------------------- plan generator
def plan_for(row: dict) -> list[str]:
    """The IMPLEMENTATION PLAN for one object: the declared step sequence of its repository
    operation, with the object's own addresses resolved.

    Generated from the same declaration the register renders, so a plan can never drift from
    the operation it claims to implement. Placeholders that the object does not carry resolve to
    the declared em-dash rather than to an empty string, so a plan step is never silently blank.
    """
    op = OPERATIONS.get(str(row.get("implementation_action") or ""))
    if not op:
        return []
    anchors = [str(a) for a in (row.get("anchors") or []) if str(a).strip()]
    deps = [str(d) for d in (row.get("dependencies") or []) if str(d).strip()]
    fields = {
        "owner": str(row.get("implementation_owner") or owner_for(row)),
        "destination": str(row.get("destination") or "") or "—",
        "authority": str(row.get("authority") or "") or "—",
        "anchor": anchors[0] if anchors else "—",
        "profile": str(row.get("superiority_profile") or "") or "—",
        "presence_state": str(row.get("state") or "") or "—",
        "dependencies": ", ".join(deps) if deps else "none declared",
        "evidence": str(row.get("evidence_conversation") or "") or "—",
        "register": REGISTER_PATH,
    }
    return [step.format(**fields) for step in list(op["steps"])]


# --------------------------------------------------------------------------- declarations
def action_registry() -> list[dict]:
    """The declared ACTION REGISTRY, for the machine model and the register."""
    return [{"action": a,
             "summary": str(ACTION_REGISTRY[a]["summary"]),
             "modifies_repository_knowledge": bool(ACTION_REGISTRY[a]["modifies_knowledge"]),
             "executed_by": str(ACTION_REGISTRY[a]["executed_by"]),
             "precondition": str(ACTION_REGISTRY[a]["precondition"])}
            for a in ACTIONS]


def operation_registry() -> list[dict]:
    """The declared repository OPERATIONS and their generated plans."""
    return [{"operation": name,
             "action": str(op["action"]),
             "summary": str(op["summary"]),
             "steps": list(op["steps"])}
            for name, op in sorted(OPERATIONS.items())]


def rule_registry() -> list[dict]:
    """The declared DECISION RULE REGISTRY, in precedence order. Emitted from the same
    declaration `apply_rules` executes, so the register can never describe a rule set the
    engine does not run."""
    return [{"rule": str(r["id"]),
             "precedence": i + 1,
             "clause": str(r["clause"]),
             "action": str(r["action"]),
             "operation": str(r["operation"]),
             "rationale": str(r["rationale"])}
            for i, r in enumerate(DECISION_RULES)]


def ruleset_declaration() -> dict:
    """The COMPLETE declared decision model as plain data — version, actions, operations,
    rules, priorities and the grounds encoding.

    This is what the assimilation engine digests into the machine register: a silent edit to any
    part of the model changes the digest, so the rule set cannot drift away from the decisions
    that cite it without failing the drift gate.
    """
    return {
        "decision_version": DECISION_VERSION,
        "actions": action_registry(),
        "operations": operation_registry(),
        "rules": rule_registry(),
        "priorities": [{"priority": p, "rationale": PRIORITY_RATIONALE[p]} for p in PRIORITIES],
        "priority_policy": dict(PRIORITY_POLICY),
        "presence_classes": list(PRESENCE_CLASSES),
        "grounds_keys": list(GROUNDS_KEYS),
        "grounds_legend": dict(GROUNDS_LEGEND),
        "residual_rule": RESIDUAL_RULE,
        "silent_rules": {rid: dict(spec) for rid, spec in SILENT_RULES.items()},
        "zone_owners": dict(ZONE_OWNER),
    }

"""UCKP Layer Zero — Constitutional Authority Alignment (Articles 1, 3, 4, 5, 7, 18).

Article 1 says no architectural authority exists outside the root law. That is a
complete statement of the law and was, until this module, an unenforced one: seven
version-controlled instruments each declared itself "AUTHORED REPOSITORY TRUTH …
upstream of every engine that reads it", and not one of them named the authority it
was upstream *under*. Seven instruments each standing at the top of its own chain is
seven roots, and Article 1 admits exactly one.

Nothing in the repository was wrong. Each of the seven really is the authoring surface
for what it declares. What was missing was an EDGE — the one from each instrument to
the law it derives under. An undeclared subordination is indistinguishable, to anything
that has to check, from a rival authority.

This module is the law side of that edge. It declares:

    * :data:`AUTHORITY_ROLES`    — the standings an instrument may hold, each derived
      from the article that creates it, and exactly one of them supreme.
    * :data:`ALIGNMENT_RULES`    — the seven alignment invariants, each bound to the
      article it enforces. They are *rules under* the law, never articles *of* it.
    * :func:`repository_local_urn` — the total, pure, injective derivation carrying
      every identifier the repository has already minted into the object model,
      verbatim.

Three things this module deliberately does not do, because each would defeat the
purpose of doing it at all:

**It does not amend the law.** :mod:`engine.uckp.law` is untouched. Article 17 requires
an unknown future category to be admitted by *registration*, and an alignment programme
that answered "authority is ambiguous" by adding articles would be the first thing the
law it edited forbids. Every rule below enforces an article that already existed.

**It does not re-mint anything.** :func:`repository_local_urn` carries a ledger
identifier through as the URN's local name, unchanged. Any derivation that reshaped
the identifier would be a re-mint wearing a projection's clothes, and Article 5 says an
identity once minted never changes.

**It does not become the enforcement.** The rules are declared here and measured over
repository reality by ``00-MASTER/UCOS-UGA-001/uga_engine.py``, inside the gate
``verify.sh`` already runs. A second enforcement path would be exactly the parallel
authority these rules exist to forbid. :func:`verify_binding` is the join: it proves the
DATA binding that engine reads still says what this module says, so the two planes
cannot drift into two answers.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from engine.uckp.constitution import (
    CONSTITUTION_NAMESPACE,
    CONSTITUTIONAL_OWNER,
    UNIVERSAL_PERSISTENCE,
    UNIVERSAL_PROJECTIONS,
    UNIVERSAL_RUNTIMES,
    root_law_urn,
)
from engine.uckp.identity import UCKO_URN_PREFIX, urn_for
from engine.uckp.law import ROOT_LAW
from engine.uckp.ucko import UCKO
from engine.uckp.values import Policy, Relationship
from engine.uckp.vocabulary import (
    RELATION_TYPE_VOCABULARY,
    RELATIONSHIP_CLASS_VOCABULARY,
)

#: The identity of the repository binding this module is the law side of.
ALIGNMENT_ID = "UCOS-CAA-001"

#: Where the repository states which instrument stands where. DATA, because *which*
#: instruments exist is a repository fact and Article 17 admits a new one by
#: registration; the law those facts are read under is here, because Article 11 forbids
#: a document from holding it.
ALIGNMENT_BINDING_PATH = "00-BOOK/DATA/constitutional-authority-alignment.json"

#: The declaring instrument recorded in every object's provenance (UCKP-INV-07).
ALIGNMENT_INSTRUMENT = "engine.uckp.alignment"

#: The namespace repository identifiers are carried into. Separate from the
#: constitutional namespace on purpose: ``UCOS-ENGINE-000496`` names the FILE that
#: holds the root law and ``UCKP-LAW-0001`` names the LAW. One namespace for both
#: would assert they are one subject, which is the confusion this module resolves.
REPOSITORY_NAMESPACE = "ucos-repository"

#: The shape of an identifier the one repository mint issues. Matching it is what makes
#: the derivation *total over the ledger* rather than total over anything at all.
REPOSITORY_ID_PATTERN = re.compile(r"^UCOS-[A-Z0-9]+-[0-9]{6}$")

#: CAA-INV-08 phrasing that turns a declared ORTHOGONAL scope back into an unrestricted
#: claim in disguise — the safeguard the role exists to prevent (Article 1 admits
#: exactly one unrestricted authority, and ORTHOGONAL is deliberately not it).
_UNRESTRICTED_SCOPE_MARKERS = (
    "every constitutional matter",
    "all constitutional authority",
    "universal supremacy",
    "unrestricted",
    "everything in ucos",
)


class AlignmentError(ValueError):
    """Raised when a binding contradicts the law it claims to derive under."""


@dataclass(frozen=True, slots=True)
class AuthorityRole:
    """A standing an instrument may hold under the root law."""

    role_id: str
    definition: str
    article: str
    may_hold_authority: bool
    cardinality: str

    def to_dict(self) -> dict[str, object]:
        return {
            "role_id": self.role_id,
            "definition": self.definition,
            "article": self.article,
            "may_hold_authority": self.may_hold_authority,
            "cardinality": self.cardinality,
        }


@dataclass(frozen=True, slots=True)
class AlignmentRule:
    """One alignment invariant, enforcing an article that already exists."""

    rule_id: str
    name: str
    statement: str
    article: str
    also: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "statement": self.statement,
            "article": self.article,
            "also": list(self.also),
        }


#: The standings, each derived from the article that creates it. ``EXACTLY_ONE`` appears
#: once and may only ever appear once: two supreme roles is two roots, and Article 1
#: admits one.
AUTHORITY_ROLES: tuple[AuthorityRole, ...] = (
    AuthorityRole(
        "SUPREME",
        "the root constitutional law; its authority derives from itself and every "
        "other chain terminates at it",
        "UCKP-ART-01",
        True,
        "EXACTLY_ONE",
    ),
    AuthorityRole(
        "PROJECTION",
        "a generated or authored view of what the objects already are; it may state "
        "repository reality and may never state law",
        "UCKP-ART-11",
        False,
        "MANY",
    ),
    AuthorityRole(
        "PERSISTENCE",
        "a storage mechanism holding copies of objects and their identities; where a "
        "thing is kept is never what a thing is",
        "UCKP-ART-09",
        False,
        "MANY",
    ),
    AuthorityRole(
        "EXECUTION",
        "a technology that acts on objects; execution never owns knowledge",
        "UCKP-ART-10",
        False,
        "MANY",
    ),
    AuthorityRole(
        "EVIDENCE",
        "the record of what was done, kept so an act can be reviewed after the fact; "
        "evidence supports truth and never constitutes it",
        "UCKP-ART-16",
        False,
        "MANY",
    ),
    AuthorityRole(
        "OBSERVATION",
        "the record of what was seen at a moment; taken outside the commit boundary, "
        "so it may never enter a canonical digest",
        "UCKP-ART-13",
        False,
        "MANY",
    ),
    AuthorityRole(
        "DERIVED",
        "an instrument that records or measures the standing of others and asserts "
        "nothing of its own",
        "UCKP-ART-15",
        False,
        "MANY",
    ),
    AuthorityRole(
        "ORTHOGONAL",
        "an instrument that governs a distinct, non-overlapping axis of constitutional "
        "responsibility — such as recognition and classification of constitutional "
        "instruments — and does not compete for supremacy on the axis Article 1 "
        "governs; it holds no authority outside its own declared scope",
        "UCKP-ART-01",
        False,
        "FEW",
    ),
)

#: The seven alignment invariants. Each enforces an article of the root law; none adds
#: one. The statements live here and are *checked* against the DATA binding by
#: :func:`verify_binding`, so the register the enforcing engine reads cannot drift away
#: from the law without the drift itself failing a test.
ALIGNMENT_RULES: tuple[AlignmentRule, ...] = (
    AlignmentRule(
        "CAA-INV-01",
        "EXACTLY_ONE_SUPREME_CONSTITUTIONAL_AUTHORITY",
        "Exactly one instrument holds role SUPREME, it is UCKP-LAW-0001, and its "
        "declared home exists.",
        "UCKP-ART-01",
    ),
    AlignmentRule(
        "CAA-INV-02",
        "EVERY_AUTHORITY_CLAIM_NAMES_ITS_CONSTITUTIONAL_SUPERIOR",
        "Every tracked instrument whose declared authority matches no disclaiming "
        "token is bound here with a role and at least one article of derivation.",
        "UCKP-ART-01",
        ("UCKP-ART-03",),
    ),
    AlignmentRule(
        "CAA-INV-03",
        "NO_SUBORDINATE_INSTRUMENT_CLAIMS_INDEPENDENT_AUTHORITY",
        "Every bound instrument carries a constitutional_superior block naming "
        "UCKP-LAW-0001, whose declared role and articles match this binding and "
        "resolve in the root law.",
        "UCKP-ART-04",
        ("UCKP-ART-11",),
    ),
    AlignmentRule(
        "CAA-INV-04",
        "EXACTLY_ONE_IDENTITY_AUTHORITY",
        "One append-only mint holds every repository identity, every declared map "
        "resolves in it, and the derivation into the object model is total and "
        "injective over every id it holds.",
        "UCKP-ART-05",
        ("UCKP-ART-03",),
    ),
    AlignmentRule(
        "CAA-INV-05",
        "EXACTLY_ONE_RELATIONSHIP_GRAPH_MODEL_OWNER",
        "One instrument declares what a relationship is, and every relationship kind "
        "any projection emits binds to a class and an article of that model.",
        "UCKP-ART-07",
    ),
    AlignmentRule(
        "CAA-INV-06",
        "EVIDENCE_AND_OBSERVATION_REMAIN_SEPARATE_TRUTHS",
        "The four truths each name a governing article, every observation kind binds "
        "to one of the five evidence classes, no sixth class is created, and neither "
        "register declares the other's subject.",
        "UCKP-ART-13",
        ("UCKP-ART-12",),
    ),
    AlignmentRule(
        "CAA-INV-07",
        "NO_INSTRUMENT_DECLARES_A_RIVAL_OBJECT_MODEL",
        "One object model is declared repository-wide. Every bound instrument that "
        "declares object classes names UCKO as the model they project, and every "
        "declared authority role resolves to an article of the root law.",
        "UCKP-ART-02",
        ("UCKP-ART-17", "UCKP-ART-18"),
    ),
    AlignmentRule(
        "CAA-INV-08",
        "ORTHOGONAL_ROLE_IS_SCOPE_BOUNDED_AND_NON_SUPREME",
        "Every instrument bound under role ORTHOGONAL declares an explicit, "
        "non-unrestricted scope naming the axis its authority is bounded to, and role "
        "ORTHOGONAL never resolves as a supreme role; Article 1 continues to admit "
        "exactly one.",
        "UCKP-ART-01",
        ("UCKP-ART-04",),
    ),
)


# --- identity: one authority, two planes ----------------------------------------


def repository_local_urn(universal_id: str) -> str:
    """Carry a repository identifier into the object model, verbatim (Article 5).

    Total over every identifier the one repository mint issues, pure, and injective:
    the identifier *is* the URN's local name, so two distinct ledger ids can never
    derive one URN and no id is rewritten to make the mapping work. That is the whole
    resolution of the identity duplication — one authority, two planes, one function
    from the lower to the higher.
    """
    text = str(universal_id).strip()
    if not REPOSITORY_ID_PATTERN.match(text):
        raise AlignmentError(f"not a repository identifier: {universal_id!r}")
    return urn_for(REPOSITORY_NAMESPACE, text)


def derivation_is_injective(universal_ids: Iterable[str]) -> tuple[str, ...]:
    """Return every identifier whose derivation collides or cannot be carried through.

    Measurement, not assertion: "one identity authority" is a count over the population
    the ledger actually holds, so a collision is reported rather than presumed absent.
    """
    findings: list[str] = []
    seen: dict[str, str] = {}
    for identifier in universal_ids:
        try:
            urn = repository_local_urn(identifier)
        except AlignmentError as exc:
            findings.append(str(exc))
            continue
        previous = seen.get(urn)
        if previous is not None and previous != identifier:
            findings.append(f"{identifier} and {previous} both derive {urn}")
            continue
        seen[urn] = identifier
    return tuple(sorted(findings))


# --- the law side, as canonical objects (Articles 2 and 8) ----------------------


def _mint(
    *,
    local_name: str,
    concept: str,
    definition: str,
    kind: str,
    category: str,
    derives_from: str,
    relationships: Iterable[Relationship] = (),
    dependencies: Iterable[str] = (),
    policies: Iterable[Policy] = (),
    keywords: Iterable[str] = (),
    metadata: dict[str, object] | None = None,
) -> UCKO:
    """Mint one alignment object with the universal bindings applied."""
    return UCKO.mint(
        namespace=CONSTITUTION_NAMESPACE,
        local_name=local_name,
        concept=concept,
        definition=definition,
        kind=kind,
        category=category,
        authority_tier="constitutional",
        derives_from=derives_from,
        owner=CONSTITUTIONAL_OWNER,
        lifecycle="ratified",
        instrument=ALIGNMENT_INSTRUMENT,
        provider=ALIGNMENT_INSTRUMENT,
        relationships=tuple(relationships),
        dependencies=tuple(dependencies),
        policies=tuple(policies),
        keywords=tuple(keywords),
        metadata=metadata or {},
        runtime_bindings=UNIVERSAL_RUNTIMES,
        projection_bindings=UNIVERSAL_PROJECTIONS,
        persistence_bindings=UNIVERSAL_PERSISTENCE,
    )


def alignment_urn() -> str:
    """The URN of the alignment binding object (pure — no registry needed)."""
    return urn_for(CONSTITUTION_NAMESPACE, ALIGNMENT_ID)


def alignment_object() -> UCKO:
    """The alignment binding itself, as an object deriving from the root law."""
    law_urn = root_law_urn()
    return _mint(
        local_name=ALIGNMENT_ID,
        concept="constitutional authority alignment",
        definition=(
            "the binding that places every authority-claiming instrument in the "
            f"repository under {ROOT_LAW.law_id}, declaring {len(AUTHORITY_ROLES)} "
            f"standings and {len(ALIGNMENT_RULES)} rules that enforce articles the "
            "law already holds, and creating no authority of its own"
        ),
        kind="policy",
        category="authority",
        derives_from=law_urn,
        dependencies=(law_urn,),
        relationships=(
            Relationship("derived-from", law_urn, "authority"),
            Relationship(
                "implements", urn_for(CONSTITUTION_NAMESPACE, "UCKP-ART-01"), "governance"
            ),
        ),
        keywords=("alignment", "authority", "supremacy", "subordination"),
        metadata={
            "binding": ALIGNMENT_BINDING_PATH,
            "roles": str(len(AUTHORITY_ROLES)),
            "rules": str(len(ALIGNMENT_RULES)),
            "supreme_authority": ROOT_LAW.law_id,
            "repository_namespace": REPOSITORY_NAMESPACE,
        },
        policies=(
            Policy(
                policy_id="UCKP-POLICY-ONE-AUTHORITY",
                statement=(
                    "An instrument that claims constitutional authority and names no "
                    "superior is a competing root and is void."
                ),
                enforcement="fail-closed",
            ),
        ),
    )


def role_object(role: AuthorityRole) -> UCKO:
    """One authority role, deriving from the alignment binding it belongs to."""
    return _mint(
        local_name=f"{ALIGNMENT_ID}-ROLE-{role.role_id}",
        concept=f"authority role {role.role_id.lower()}",
        definition=role.definition,
        kind="standard",
        category="authority",
        derives_from=alignment_urn(),
        dependencies=(alignment_urn(),),
        relationships=(
            Relationship("derived-from", alignment_urn(), "authority"),
            Relationship(
                "governs", urn_for(CONSTITUTION_NAMESPACE, role.article), "constitutional"
            ),
        ),
        keywords=("role", "authority", role.role_id.lower()),
        metadata={
            "role": role.role_id,
            "article": role.article,
            "may_hold_authority": "true" if role.may_hold_authority else "false",
            "cardinality": role.cardinality,
        },
    )


def rule_object(rule: AlignmentRule) -> UCKO:
    """One alignment rule, deriving from the alignment binding it belongs to."""
    relationships = [
        Relationship("derived-from", alignment_urn(), "authority"),
        Relationship("implements", urn_for(CONSTITUTION_NAMESPACE, rule.article), "governance"),
    ]
    relationships.extend(
        Relationship("references", urn_for(CONSTITUTION_NAMESPACE, article), "constitutional")
        for article in rule.also
    )
    return _mint(
        local_name=rule.rule_id,
        concept=rule.name.lower().replace("_", " "),
        definition=rule.statement,
        kind="rule",
        # `authority`, not `governance`: these rules decide by what authority an
        # instrument exists, which is what the authority category answers. The
        # governance category holds the objects that decide *about* an object, and
        # putting a rule there because it sounds administrative would blur a
        # distinction the facet model draws deliberately.
        category="authority",
        derives_from=alignment_urn(),
        dependencies=(alignment_urn(),),
        relationships=relationships,
        keywords=("alignment", "invariant", "authority"),
        metadata={
            "enforces": rule.article,
            "also": ",".join(rule.also),
            "measured_by": "00-MASTER/UCOS-UGA-001/uga_engine.py",
            "fails_closed": "true",
        },
    )


def identity_derivation_object() -> UCKO:
    """The identity derivation, as the object that resolves the duplication.

    It is a *rule* rather than a second identity authority, and the distinction is the
    whole point: the rule says how the one repository mint is read in the object model.
    It issues nothing.
    """
    return _mint(
        local_name=f"{ALIGNMENT_ID}-IDENTITY-DERIVATION",
        concept="repository identity derivation",
        definition=(
            "the total, pure and injective function carrying an identifier minted by "
            "the one repository mint into the object model as "
            f"urn:ucos:ucko:{REPOSITORY_NAMESPACE}:<id>, verbatim, so the ledger is "
            "projected into Article 5 without a single identifier changing"
        ),
        kind="rule",
        category="identity",
        derives_from=alignment_urn(),
        dependencies=(alignment_urn(),),
        relationships=(
            Relationship("derived-from", alignment_urn(), "authority"),
            Relationship(
                "implements", urn_for(CONSTITUTION_NAMESPACE, "UCKP-ART-05"), "governance"
            ),
        ),
        keywords=("identity", "derivation", "ledger", "projection"),
        metadata={
            "namespace": REPOSITORY_NAMESPACE,
            "function": f"{ALIGNMENT_INSTRUMENT}.repository_local_urn",
            "id_shape": REPOSITORY_ID_PATTERN.pattern,
            "mints": "nothing",
            "preserves_every_existing_id": "true",
        },
    )


def alignment_objects() -> tuple[UCKO, ...]:
    """Every object this module contributes to the universe."""
    return (
        alignment_object(),
        identity_derivation_object(),
        *(role_object(role) for role in AUTHORITY_ROLES),
        *(rule_object(rule) for rule in ALIGNMENT_RULES),
    )


def ucko_objects() -> tuple[UCKO, ...]:
    """Provider hook (Article 8): the registry discovers these without enumeration."""
    return alignment_objects()


# --- the join: the DATA binding may not drift from the law ----------------------


def _entries(value: object) -> Sequence[object] | None:
    """``value`` as a JSON list, or None.

    A string is a ``Sequence`` and would iterate one character at a time, so the
    exclusion is what stops a mistyped field from being read as a list of entries.
    """
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return value
    return None


def _rule_findings(document: Mapping[str, object]) -> list[str]:
    declared = _entries(document.get("invariants"))
    if declared is None:
        return ["the binding declares no invariants"]
    by_id = {str(entry.get("id")): entry for entry in declared if isinstance(entry, Mapping)}
    findings: list[str] = []
    for rule in ALIGNMENT_RULES:
        entry = by_id.pop(rule.rule_id, None)
        if entry is None:
            findings.append(f"{rule.rule_id} is declared in the law and absent from the binding")
            continue
        if entry.get("name") != rule.name:
            findings.append(f"{rule.rule_id} name differs: {entry.get('name')!r} != {rule.name!r}")
        if entry.get("statement") != rule.statement:
            findings.append(f"{rule.rule_id} statement has drifted from {ALIGNMENT_INSTRUMENT}")
        if entry.get("article") != rule.article:
            findings.append(
                f"{rule.rule_id} enforces {entry.get('article')!r}, not {rule.article!r}"
            )
        if entry.get("fails_closed") is not True:
            findings.append(f"{rule.rule_id} is not declared fails_closed")
    findings.extend(
        f"{extra} is declared in the binding and is not a rule of {ALIGNMENT_INSTRUMENT}"
        for extra in sorted(by_id)
    )
    return findings


def _role_findings(document: Mapping[str, object]) -> list[str]:
    declared = document.get("authority_roles")
    if not isinstance(declared, Mapping):
        return ["the binding declares no authority roles"]
    findings: list[str] = []
    remaining = dict(declared)
    for role in AUTHORITY_ROLES:
        entry = remaining.pop(role.role_id, None)
        if not isinstance(entry, Mapping):
            findings.append(
                f"role {role.role_id} is declared in the law and absent from the binding"
            )
            continue
        if entry.get("definition") != role.definition:
            findings.append(
                f"role {role.role_id} definition has drifted from {ALIGNMENT_INSTRUMENT}"
            )
        if entry.get("article") != role.article:
            findings.append(
                f"role {role.role_id} derives from {entry.get('article')!r}, not {role.article!r}"
            )
        if entry.get("may_hold_authority") is not role.may_hold_authority:
            findings.append(f"role {role.role_id} disagrees about whether it may hold authority")
        if entry.get("cardinality") != role.cardinality:
            findings.append(
                f"role {role.role_id} declares cardinality {entry.get('cardinality')!r}"
            )
    findings.extend(
        f"role {extra} is declared in the binding and is not a role of {ALIGNMENT_INSTRUMENT}"
        for extra in sorted(remaining)
    )
    return findings


def _vocabulary_findings(document: Mapping[str, object]) -> list[str]:
    """Every relationship kind the binding maps must land in the real model.

    The enforcing engine is stdlib-only by constitutional design, so it cannot import
    :mod:`engine.uckp.vocabulary` to check a class name. It checks against the term
    lists the binding declares instead, and this function is what keeps those lists
    honest — a declared class that the model does not hold is caught here rather than
    silently widening what a projection is allowed to claim.
    """
    resolution = document.get("relationship_graph_resolution")
    if not isinstance(resolution, Mapping):
        return ["the binding declares no relationship graph resolution"]
    bindings = resolution.get("relationship_kind_bindings")
    if not isinstance(bindings, Mapping):
        return ["the binding maps no relationship kinds"]
    classes = set(RELATIONSHIP_CLASS_VOCABULARY.term_ids())
    relations = set(RELATION_TYPE_VOCABULARY.term_ids())
    articles = set(ROOT_LAW.article_ids())
    findings: list[str] = []
    for kind, entry in sorted(bindings.items()):
        if not isinstance(entry, Mapping):
            findings.append(f"relationship kind {kind} carries no binding")
            continue
        if entry.get("uckp_class") not in classes:
            findings.append(
                f"relationship kind {kind} binds to class {entry.get('uckp_class')!r}, "
                "which the model does not declare"
            )
        if entry.get("uckp_relation") not in relations:
            findings.append(
                f"relationship kind {kind} binds to relation {entry.get('uckp_relation')!r}, "
                "which the model does not declare"
            )
        if entry.get("article") not in articles:
            findings.append(
                f"relationship kind {kind} names article {entry.get('article')!r}, "
                "which the root law does not hold"
            )
    return findings


def _derivation_findings(document: Mapping[str, object]) -> list[str]:
    """The derivation contract the stdlib-only engine reads must be this module's.

    That engine cannot import Layer Zero — it is stdlib-only by constitutional design,
    so the constitutional gate workflows can run it — and it therefore composes the URN
    from the fields the binding declares. This is where those fields are resolved against
    the real derivation, so "two readers, one truth" is checked rather than hoped for.
    """
    resolution = document.get("identity_authority_resolution")
    if not isinstance(resolution, Mapping):
        return ["the binding declares no identity authority resolution"]
    derivation = resolution.get("derivation")
    if not isinstance(derivation, Mapping):
        return ["the binding declares no identity derivation"]
    findings: list[str] = []
    expected: tuple[tuple[str, object], ...] = (
        ("urn_prefix", UCKO_URN_PREFIX),
        ("namespace", REPOSITORY_NAMESPACE),
        ("id_shape", REPOSITORY_ID_PATTERN.pattern),
        ("function", f"{ALIGNMENT_INSTRUMENT}.repository_local_urn"),
    )
    findings.extend(
        f"the declared derivation {field} is {derivation.get(field)!r}, not {value!r}"
        for field, value in expected
        if derivation.get(field) != value
    )
    sample = "UCOS-ENGINE-000496"
    declared_shape = derivation.get("shape")
    if declared_shape != f"{UCKO_URN_PREFIX}:{REPOSITORY_NAMESPACE}:<UCOS-ID>":
        findings.append(f"the declared derivation shape is {declared_shape!r}")
    if derivation.get("example") != f"{sample} -> {repository_local_urn(sample)}":
        findings.append("the declared derivation example does not match the derivation")
    return findings


def verify_binding(document: Mapping[str, object]) -> tuple[str, ...]:
    """Return every way ``document`` contradicts the law it claims to derive under.

    Empty means aligned. Fail-closed: a binding that cannot be read as a mapping is a
    finding, never a pass, because an unmeasured claim of subordination is the exact
    condition this module exists to end.
    """
    if not isinstance(document, Mapping):
        return ("the alignment binding is not a mapping",)

    findings: list[str] = []
    superior = document.get("constitutional_superior")
    if not isinstance(superior, Mapping) or superior.get("authority") != ROOT_LAW.law_id:
        findings.append(f"the binding does not name {ROOT_LAW.law_id} as its own superior")

    supreme = document.get("supreme_authority")
    if not isinstance(supreme, Mapping):
        findings.append("the binding declares no supreme authority")
    else:
        if supreme.get("id") != ROOT_LAW.law_id:
            findings.append(
                f"the binding declares {supreme.get('id')!r} supreme, not {ROOT_LAW.law_id}"
            )
        if supreme.get("supremacy_clause") != ROOT_LAW.supremacy:
            findings.append("the quoted supremacy clause has drifted from the root law")
        for field, expected in (
            ("articles", len(ROOT_LAW.articles)),
            ("invariants", len(ROOT_LAW.invariants)),
            ("stop_conditions", len(ROOT_LAW.stop_conditions)),
        ):
            if supreme.get(field) != expected:
                findings.append(
                    f"the binding counts {supreme.get(field)!r} {field}; the law holds {expected}"
                )

    findings.extend(_role_findings(document))
    findings.extend(_rule_findings(document))
    findings.extend(_vocabulary_findings(document))
    findings.extend(_derivation_findings(document))

    instruments = _entries(document.get("subordinate_instruments"))
    if instruments is None:
        findings.append("the binding declares no subordinate instruments")
    else:
        roles = {role.role_id for role in AUTHORITY_ROLES}
        supreme_roles = {role.role_id for role in AUTHORITY_ROLES if role.may_hold_authority}
        articles = set(ROOT_LAW.article_ids())
        for entry in instruments:
            if not isinstance(entry, Mapping):
                findings.append("a subordinate instrument entry is not a mapping")
                continue
            name = str(entry.get("id"))
            role = entry.get("role")
            if role not in roles:
                findings.append(f"{name} declares role {role!r}, which is not a declared role")
            elif role in supreme_roles:
                findings.append(f"{name} claims a supreme role; Article 1 admits exactly one")
            elif role == "ORTHOGONAL":
                owns = entry.get("owns")
                if not isinstance(owns, str) or not owns.strip():
                    findings.append(f"{name} claims role ORTHOGONAL but declares no explicit scope")
                else:
                    lowered = owns.strip().lower()
                    if any(marker in lowered for marker in _UNRESTRICTED_SCOPE_MARKERS):
                        findings.append(
                            f"{name} claims role ORTHOGONAL with an unrestricted scope in "
                            f"'owns': {owns!r}"
                        )
            derives = _entries(entry.get("derives_under"))
            if not derives:
                findings.append(f"{name} names no article of derivation")
                continue
            findings.extend(
                f"{name} derives under {article!r}, which the root law does not hold"
                for article in derives
                if article not in articles
            )
    return tuple(findings)


def require_aligned(document: Mapping[str, object]) -> None:
    """Fail closed if the binding contradicts the law (Article 1)."""
    findings = verify_binding(document)
    if findings:
        raise AlignmentError("; ".join(findings))


__all__ = [
    "ALIGNMENT_BINDING_PATH",
    "ALIGNMENT_ID",
    "ALIGNMENT_INSTRUMENT",
    "ALIGNMENT_RULES",
    "AUTHORITY_ROLES",
    "AlignmentError",
    "AlignmentRule",
    "AuthorityRole",
    "REPOSITORY_ID_PATTERN",
    "REPOSITORY_NAMESPACE",
    "alignment_object",
    "alignment_objects",
    "alignment_urn",
    "derivation_is_injective",
    "identity_derivation_object",
    "repository_local_urn",
    "require_aligned",
    "role_object",
    "rule_object",
    "ucko_objects",
    "verify_binding",
]

"""UEC-000001 Part 1 — the vocabulary of enforcement closure.

An ENFORCEMENT ARTIFACT is any tracked object whose purpose is to refuse: a gate engine, a
module gate, a workflow, a Makefile gate target, a verification stage, a declaration that a
gate reads, or a test that proves a gate can fail.

The repository already possesses exactly one closure mechanism over its objects —
REG-AUTO-001 registration, enforced by ``00-BOOK/tools/ukb.py enforce --pre``. Its boundary is
stated in ``00-BOOK/tools/config.py``::

    INCLUDE_EXTENSIONS   = (".md", ".txt", ".docx", ".json")
    EXCLUDE_DIR_PREFIXES ⊇ (".github/", "00-MASTER/", "00-BOOK/tools/", ...)

Measured against ``00-BOOK/DATA/artifacts.json`` at 1597 registered artifacts: 0 are ``.py``,
0 are ``.yml``, 0 live under ``.github/``, 0 live under ``00-MASTER/``. The enforcement surface
is therefore not weakly covered by the repository's closure mechanism — it is **definitionally
outside it**, and was outside it before the first gate was written.

That single condition is the enabling cause of the whole defect class. A deleted workflow
produces no signal because no register ever held it. An engine ships with no test because
"engine has a test" is a relation between two unregisterable objects. ``00-BOOK/tools/`` is
excluded on the stated ground that "the registry must not list itself", which is precisely
why the trust anchor is unregistered (discovery ``D-09``) — a designed exclusion whose
consequence was never governed.

UEC does not extend REG-AUTO-001. Extending it would break its stated invariant and would be a
registry modification, which ``H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-RECORD.md``
§5.4 does not authorize under any approval. UEC instead establishes the **complementary plane**:
a second closure mechanism whose subject is exactly the set REG-AUTO-001 cannot see, with the
disjointness of the two planes measured rather than assumed (UEC-L-10).

THREE-VALUED BY CONSTRUCTION. A law HOLDS, is REFUSED, or FAULTS. A fault is never a pass:
"no enforcement artifact was discovered" and "every enforcement artifact is governed" are
different facts about the world, and a mechanism that collapsed them would let a broken
discoverer certify an empty repository.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

HOLDS = "HOLDS"
REFUSED = "REFUSED"

#: Every artifact kind UEC governs. Closed against nothing: adding a kind is an entry in the
#: declaration's ``discovery_rules``, which is why the kind list is derived from the
#: declaration rather than enumerated here. This tuple records the kinds the DECLARATION at
#: adoption named, and UEC-L-01 refuses a declaration whose rules match none of them.
KIND_ENGINE = "GATE_ENGINE"
KIND_MODULE_GATE = "MODULE_GATE"
KIND_WORKFLOW = "WORKFLOW"
KIND_MAKE_TARGET = "MAKE_GATE_TARGET"
KIND_VERIFY_STAGE = "VERIFY_STAGE"
KIND_DECLARATION = "DECLARATION"
KIND_TEST = "TEST_BINDING"


class EnforcementError(RuntimeError):
    """The declaration or the discovery substrate is unusable. A FAULT, never a verdict.

    Raised when a question cannot be asked: the declaration is absent, a discovery rule is
    malformed, ``Makefile`` or ``verify.sh`` cannot be read. It is never raised because an
    artifact is ungoverned or a gate is untested — those are refusals, and a refusal is an
    answer.
    """


class DeclarationError(EnforcementError):
    """The UEC declaration is absent, unparseable or incoherent."""


@dataclass(frozen=True)
class Rule:
    """A discovery rule: how a kind of enforcement artifact is located, and its floor.

    ``floor`` is the minimum number of matches below which the rule is REFUSED rather than
    satisfied. A rule that matches nothing has stopped seeing, and a closure mechanism whose
    discoverer went blind reports success over an empty world. The floor is what makes that
    state impossible, and UEC-L-01 additionally refuses ``floor <= 0`` so the protection
    cannot be disabled by declaring a floor of zero.
    """

    rule_id: str
    kind: str
    strategy: str
    floor: int
    pattern: str = ""
    root: str = ""
    owner: str = ""

    def __post_init__(self) -> None:
        if not self.rule_id or not self.kind or not self.strategy:
            raise DeclarationError("a discovery rule needs a rule_id, a kind and a strategy")


@dataclass(frozen=True)
class Artifact:
    """One located enforcement artifact.

    ``identity`` is the stable name the declaration governs it by — a repository-relative path
    for a file, a target name for a Makefile target, a label for a verification stage.
    """

    identity: str
    kind: str
    rule_id: str
    detail: Mapping[str, object] = field(default_factory=dict)

    def key(self) -> str:
        return f"{self.kind}::{self.identity}"


@dataclass(frozen=True)
class Law:
    """A UEC law: an identifier, the check that computes it, and whether it refuses.

    ``blocking`` is deliberately part of the declaration AND part of the certification
    identity (see ``declaration.digest_payload``). UCON's digest omits it — proven by
    execution: flipping ``blocking`` on ``UCON-L-01`` leaves ``declaration_digest`` at
    ``192c63af…`` unchanged while turning a CLOSED verdict into OPEN. UEC does not repeat
    that: every field that can change a verdict is inside the digest, and
    ``test_enforcement_closure.py`` proves it by mutation rather than asserting it.
    """

    law_id: str
    check: str
    statement: str
    blocking: bool
    concern: str = ""


@dataclass(frozen=True)
class Withdrawal:
    """An enforcement artifact deliberately removed from governance.

    The only reduction path, and deliberately expensive. Each withdrawal carries an owner, a
    reason and a date; the total is capped by the declaration; and UEC-L-12 refuses a
    withdrawal missing any field. A withdrawal is visible in one ``git diff`` line, which is
    the property a silent deletion lacks.
    """

    identity: str
    kind: str
    owner: str
    reason: str
    date: str

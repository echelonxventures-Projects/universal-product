"""Universal Governance — every admission is governed (Engineering Rule 4).

Governance is expressed as an **open** set of named :class:`Constraint`s grouped into a
:class:`Policy`. A constraint is a pure predicate over a candidate meta-object and a
read-only view of the registry; it returns a verdict and, on failure, a reason. Adding a
new rule is registering a new constraint — never a kernel edit. The kernel ships a small
set of *universal, domain-free* constraints (identity present, classifying meta-type
registered, relationships acyclic, content unique). None of them encodes a business,
technology, provider or Earth assumption; they are structural invariants of the meta-model
itself.

Governance never mutates anything. It only decides. The registry performs the mutation
after a governed :class:`GovernanceDecision` is ``allowed``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from engine.kernel.meta import META_TYPE_ROOT, MetaObject


class RegistryView:
    """The read-only surface a constraint may consult about current registry state.

    A concrete base (not a ``typing.Protocol``) so it carries no uncoverable stub bodies:
    the registry satisfies it structurally (duck-typed); these methods exist only to
    document and type the surface and are never invoked on the base itself.
    """

    def exists(self, identity: str) -> bool:
        """True iff any version of ``identity`` is registered."""
        raise NotImplementedError

    def metatype_exists(self, natural_key: str) -> bool:
        """True iff a meta-type with this natural key is registered."""
        raise NotImplementedError

    def content_owner(self, content_hash: str) -> str | None:
        """The identity that owns a content hash, or None (Knowledge-Once index)."""
        raise NotImplementedError

    def would_cycle(self, identity: str, targets: tuple[str, ...]) -> bool:
        """True iff adding edges ``identity -> targets`` would create a cycle."""
        raise NotImplementedError


#: A constraint check: given a candidate and a registry view, return (ok, reason).
ConstraintFn = Callable[[MetaObject, RegistryView], "tuple[bool, str]"]


@dataclass(frozen=True)
class Constraint:
    """A named, universal invariant evaluated at admission time."""

    name: str
    check: ConstraintFn
    description: str = ""

    def evaluate(self, candidate: MetaObject, view: RegistryView) -> tuple[bool, str]:
        """Evaluate this constraint against a candidate; return ``(ok, reason)``."""
        return self.check(candidate, view)


@dataclass(frozen=True)
class ConstraintOutcome:
    """The outcome of one constraint against one candidate."""

    name: str
    ok: bool
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        """A deterministic, serialisable rendering of this outcome."""
        return {"constraint": self.name, "ok": self.ok, "reason": self.reason}


@dataclass(frozen=True)
class GovernanceDecision:
    """The aggregate verdict of a policy over a candidate."""

    identity: str
    allowed: bool
    outcomes: tuple[ConstraintOutcome, ...]

    @property
    def reasons(self) -> list[str]:
        """The reasons of every failed constraint (empty when allowed)."""
        return [o.reason for o in self.outcomes if not o.ok]

    def to_dict(self) -> dict[str, object]:
        """A deterministic, serialisable rendering of the decision."""
        return {
            "identity": self.identity,
            "allowed": self.allowed,
            "outcomes": [o.to_dict() for o in self.outcomes],
        }


# --------------------------------------------------------------------------- universal
# constraints. Each is a structural invariant of the meta-model; none is domain-specific.


def _identity_present(candidate: MetaObject, _view: RegistryView) -> tuple[bool, str]:
    ok = bool(candidate.identity)
    return ok, "" if ok else "candidate has no minted identity (Rule 3)"


def _metatype_registered(candidate: MetaObject, view: RegistryView) -> tuple[bool, str]:
    # The reflective root classifies itself, so it is always admissible; every other
    # object must be classified by an already-registered meta-type. This is the single
    # invariant that makes the type system open-by-registration: a new concept-category
    # enters by registering its meta-type first, never by editing the kernel.
    if candidate.is_reflective_root:
        return True, ""
    ref = candidate.metatype
    if view.metatype_exists(ref):
        return True, ""
    return False, f"classifying meta-type is not registered: {ref!r} (register it first)"


def _relationships_acyclic(candidate: MetaObject, view: RegistryView) -> tuple[bool, str]:
    targets = candidate.related()
    if view.would_cycle(candidate.identity, targets):
        return False, "relationship edge would introduce a cycle"
    return True, ""


def _content_unique(candidate: MetaObject, view: RegistryView) -> tuple[bool, str]:
    owner = view.content_owner(candidate.content_hash())
    if owner is None or owner == candidate.identity:
        return True, ""
    return False, f"identical content already registered under {owner} (Knowledge Once)"


UNIVERSAL_CONSTRAINTS: tuple[Constraint, ...] = (
    Constraint("identity-present", _identity_present, "Every thing possesses identity."),
    Constraint(
        "metatype-registered",
        _metatype_registered,
        "A thing is classified by an already-registered meta-type (open by registration).",
    ),
    Constraint("relationships-acyclic", _relationships_acyclic, "Relationships stay acyclic."),
    Constraint("content-unique", _content_unique, "Identical content has one canonical home."),
)


@dataclass
class Policy:
    """An ordered, open collection of constraints under a name."""

    name: str
    constraints: list[Constraint] = field(default_factory=list)

    def add(self, constraint: Constraint) -> Policy:
        """Register an additional constraint (unbounded extension, Rule 5)."""
        self.constraints.append(constraint)
        return self

    def evaluate(self, candidate: MetaObject, view: RegistryView) -> GovernanceDecision:
        """Evaluate every constraint in order; allowed iff all pass."""
        outcomes: list[ConstraintOutcome] = []
        for constraint in self.constraints:
            ok, reason = constraint.evaluate(candidate, view)
            outcomes.append(ConstraintOutcome(constraint.name, ok, reason))
        allowed = all(o.ok for o in outcomes)
        return GovernanceDecision(candidate.identity, allowed, tuple(outcomes))

    def constraint_names(self) -> list[str]:
        """The names of this policy's constraints, in order."""
        return [c.name for c in self.constraints]


class Governance:
    """The kernel's governance authority: an open registry of named policies."""

    __slots__ = ("_policies", "_default")

    def __init__(self) -> None:
        self._policies: dict[str, Policy] = {}
        admission = Policy("admission", list(UNIVERSAL_CONSTRAINTS))
        self._policies[admission.name] = admission
        self._default = admission.name

    @property
    def admission(self) -> Policy:
        """The policy applied to every registry admission."""
        return self._policies[self._default]

    def register_policy(self, policy: Policy) -> None:
        """Register a new named policy (never overwriting an existing name silently)."""
        if policy.name in self._policies:
            raise ValueError(f"policy already registered: {policy.name!r}")
        self._policies[policy.name] = policy

    def register_constraint(self, constraint: Constraint, *, policy: str | None = None) -> None:
        """Register an additional constraint into a policy (default: admission)."""
        target = self._policies[policy or self._default]
        target.add(constraint)

    def policy(self, name: str) -> Policy:
        """Return a registered policy by name."""
        return self._policies[name]

    def policy_names(self) -> list[str]:
        """The names of every registered policy, sorted."""
        return sorted(self._policies)

    def evaluate(self, candidate: MetaObject, view: RegistryView) -> GovernanceDecision:
        """Evaluate the admission policy over a candidate."""
        return self.admission.evaluate(candidate, view)

    def describe(self) -> dict[str, object]:
        """A deterministic description of the governance surface."""
        return {
            "policies": {
                name: self._policies[name].constraint_names() for name in sorted(self._policies)
            },
            "default_policy": self._default,
            "root_metatype": META_TYPE_ROOT,
        }


__all__ = [
    "Governance",
    "Policy",
    "Constraint",
    "ConstraintFn",
    "ConstraintOutcome",
    "GovernanceDecision",
    "RegistryView",
    "UNIVERSAL_CONSTRAINTS",
]

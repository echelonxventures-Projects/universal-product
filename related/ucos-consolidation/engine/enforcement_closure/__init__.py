"""UEC-000001 — Universal Enforcement Closure.

AUTHORITY: NONE — DERIVED TRUTH. This programme legislates nothing and owns no gate other than
its own. It creates no identifier, allocates no ownership, and resolves no constitutional
question. What it owns is the QUESTION "can a protection disappear, be added ungoverned, become
vacuous, become untested, or become single-pointed without a fail-closed signal" — never the
question "is this repository compliant", which remains with CMG-000001, UCOS-UGA-001,
UAUE-000001, UOBC-000001, UISD-000001, UVI-000001 and the coverage floor.

WHY THIS PROGRAMME EXISTS. The repository possesses exactly one closure mechanism over its
objects: REG-AUTO-001 registration. Its boundary, stated in ``00-BOOK/tools/config.py``, admits
``.md``/``.txt``/``.docx``/``.json`` and excludes ``.github/``, ``00-MASTER/`` and
``00-BOOK/tools/``. Measured over the 1597 registered artifacts in
``00-BOOK/DATA/artifacts.json``: 0 are ``.py``, 0 are ``.yml``, 0 live under ``.github/``, 0 live
under ``00-MASTER/``.

The enforcement surface is therefore not weakly covered — it is definitionally invisible to the
only closure mechanism the repository has, and was invisible before the first gate was written.
That is the enabling condition behind every measured instance: 7 workflow deletions and 6
Makefile gate-target deletions producing a byte-identical test outcome; a one-line
``return True`` flipping two constitutional gates from CLOSED to OPEN with no test able to kill
it; eight programme engines with zero test files.

UEC does not extend REG-AUTO-001 — extending it would break its stated invariant ("the registry
must not list itself") and would be a registry modification that
``H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-RECORD.md`` §5.4 authorizes under no approval.
UEC establishes the complementary plane, and ``UEC-L-10`` measures the disjointness of the two
rather than assuming it.
"""

from __future__ import annotations

from engine.enforcement_closure.contract import (  # noqa: F401
    LAW_CHECKS,
    Probe,
    inventory,
    load_contract,
    measure,
)
from engine.enforcement_closure.declaration import (  # noqa: F401
    DECLARATION_RELATIVE,
    DIGEST_EXCLUSIONS,
    Declaration,
    load,
    parse,
)
from engine.enforcement_closure.model import (  # noqa: F401
    DeclarationError,
    EnforcementError,
    Law,
    Rule,
    Withdrawal,
)

# NO MODULE-LEVEL ARTIFACT_ID AND NO MODULE-LEVEL AUTHORITY, DELIBERATELY.
#
# Both are fields of ``00-MASTER/UEC-000001/uec-declaration.json`` and are read from it. A copy
# here would be a second answer to "who authorised this", and the two could diverge without any
# law noticing — which is measured, not hypothetical: ``uvi-declaration.json:5`` carries a
# 400-character governed authority statement while ``engine/verification_intelligence/gate.py:634``
# reports the literal ``"NONE — DERIVED TRUTH"``, and the same literal is duplicated in that
# package's ``__init__.py:58``, ``cost_model.py:110`` and ``model.py:273``. Four copies, none
# derived from the declaration that owns the field.
#
# The first draft of this module carried exactly that copy, and ``UCOS-UCAF-001`` refused it:
# UCAF-VAL-17 reported "engine/enforcement_closure/__init__.py:AUTHORITY: token
# 'NONE — DERIVED TRUTH' is classified nowhere". The token was removed rather than classified,
# because classifying it would have registered the duplicate as legitimate.
#
# ``test_enforcement_closure.py::test_declaration_module_exposes_no_hardcoded_authority``
# holds this closed: the reported authority must equal the declared one, and must be longer than
# any placeholder.

__all__ = [
    "DECLARATION_RELATIVE",
    "DIGEST_EXCLUSIONS",
    "Declaration",
    "DeclarationError",
    "EnforcementError",
    "LAW_CHECKS",
    "Law",
    "Probe",
    "Rule",
    "Withdrawal",
    "inventory",
    "load",
    "load_contract",
    "measure",
    "parse",
]

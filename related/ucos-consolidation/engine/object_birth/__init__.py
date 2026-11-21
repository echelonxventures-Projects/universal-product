"""UOBC-000001 — the Universal Object Birth Contract.

Creation is not file generation. Creation is an identity birth event: an object is
identified *before* it exists, and it keeps that identity through every later move and
every later evolution.

Six identity mechanisms already existed in this repository before this package, and all
six identify things that **already exist** — they scan a version-controlled tree and
name what they find. That makes identity a measurement of location, and a measurement
of location changes when the location does. This package is the one missing piece: the
creation-time binding of UCKP Article 5.

It is deliberately **not** a new identity authority. Identity is derived by delegating
to ``engine/uckp/identity.py``, which the repository's authority alignment declares
``role: SUPREME — this IS UCKP-ART-05``. No counter is advanced, no corpus serial is
consumed and no repository identifier is issued, so under that file's own
``second_authority_test`` — "a mint is recognised by the counter it advances" — this
package cannot be a second mint.

What it composes rather than rebuilds:

======================  =========================================================
Concern                 Located owner
======================  =========================================================
Identity derivation     ``engine/uckp/identity.py`` (UCKP-ART-05, SUPREME)
Repository serials      ``00-BOOK/DATA/id-ledger.json`` (PERSISTENCE)
Temporal coordinates    ``engine/temporal/`` (CMG-000002)
Creation context        ``engine/context/`` (UCXI-000001, fifteen kinds)
Lifecycle               UCIC-001 owner; UCL-000001 derived truth
Evolution               ``engine/uckp/evolution.py`` Article-14; CEP-009
Certification           CEP-005 channel
======================  =========================================================

Authority: NONE — DERIVED TRUTH.
"""

from __future__ import annotations

from engine.object_birth.birth import (
    birth,
    derive_identity,
    evolve,
    expected_urn,
    identity_uuid,
    local_name_of,
    namespace_of,
)
from engine.object_birth.contract import LAW_CHECKS, assess, load_contract
from engine.object_birth.ledger import (
    append,
    dumps,
    empty_ledger,
    load,
    records,
    save,
    supersede,
)
from engine.object_birth.model import (
    MANDATORY_FIELD_NAMES,
    BirthContract,
    BirthError,
    BirthLaw,
    BirthRecord,
    BirthStage,
    MandatoryField,
    Namespace,
)
from engine.object_birth.scope import (
    EXCEPTION,
    FAIL,
    PASS,
    ScopePolicy,
    Verdict,
    evaluate,
    load_context,
    load_policy,
)

#: The published contract of this package.
BIRTH_CONTRACT: dict[str, object] = {
    "artifact_id": "UOBC-000001",
    "name": "Universal Object Birth Contract",
    "authority": "NONE — DERIVED TRUTH",
    "identity_plane": "engine/uckp/identity.py (UCKP-ART-05, SUPREME)",
    "mints_repository_serial": False,
    "advances_counter": False,
    "prohibitions": (
        "anonymous objects",
        "temporary identities",
        "post-creation registration",
        "identity replacement during evolution",
    ),
}

__all__ = [
    "EXCEPTION",
    "FAIL",
    "PASS",
    "ScopePolicy",
    "Verdict",
    "evaluate",
    "load_context",
    "load_policy",
    "BIRTH_CONTRACT",
    "LAW_CHECKS",
    "MANDATORY_FIELD_NAMES",
    "BirthContract",
    "BirthError",
    "BirthLaw",
    "BirthRecord",
    "BirthStage",
    "MandatoryField",
    "Namespace",
    "append",
    "assess",
    "birth",
    "derive_identity",
    "dumps",
    "empty_ledger",
    "evolve",
    "expected_urn",
    "identity_uuid",
    "load",
    "load_contract",
    "local_name_of",
    "namespace_of",
    "records",
    "save",
    "supersede",
]

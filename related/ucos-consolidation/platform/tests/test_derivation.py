"""WP-09 — Derivation Purity tests (PRJ-C2 · ACT-C2).

Covers pure derivation contracts, immutable digest-pinned inputs, the deterministic
purity-enforcing derivation engine (reproducible outputs, no hidden state/wall-clock),
derivation verification (bit replay), dependency-graph validation, and non-mixing of
determinisms (AIF-L18 / AIF-L20).
"""

from __future__ import annotations

from platform.foundation.canonical import CanonicalProfile, content_digest
from platform.foundation.derivation import (
    DERIVATION_LEDGER_FORMAT,
    DerivationContract,
    DerivationEngine,
    DerivationInput,
    DerivationResult,
    InputKind,
)
from platform.foundation.errors import (
    DependencyError,
    DerivationError,
    DerivationPurityError,
)

import pytest


def _input(name: str, content, kind=InputKind.SOURCE) -> DerivationInput:
    return DerivationInput.of(name, content, kind=kind)


def _contract(**overrides) -> DerivationContract:
    base = {
        "output_name": "report",
        "generator_version": "gen/1.0.0",
        "inputs": (_input("a", {"x": 1}), _input("b", {"y": 2})),
    }
    base.update(overrides)
    return DerivationContract(**base)


def _sum_deriver(values):
    return {"total": values["a"]["x"] + values["b"]["y"]}


# --------------------------------------------------------------------------------
# DerivationInput — immutable, digest-pinned
# --------------------------------------------------------------------------------


def test_input_of_pins_digest():
    inp = DerivationInput.of("a", {"x": 1})
    assert inp.digest == content_digest({"x": 1}).value
    assert inp.kind is InputKind.SOURCE
    assert inp.to_dict() == {"name": "a", "kind": "source", "digest": inp.digest}


def test_input_validation():
    with pytest.raises(DerivationError):
        DerivationInput("", InputKind.SOURCE, "d")
    with pytest.raises(DerivationError):
        DerivationInput("a", "not-a-kind", "d")  # type: ignore[arg-type]
    with pytest.raises(DerivationError):
        DerivationInput("a", InputKind.SOURCE, "")


# --------------------------------------------------------------------------------
# DerivationContract — purity + non-mixing (AIF-L18 / L20)
# --------------------------------------------------------------------------------


def test_contract_basics():
    contract = _contract()
    assert contract.input_names == ("a", "b")
    assert set(contract.digest_map) == {"a", "b"}
    assert contract.to_dict()["generator_version"] == "gen/1.0.0"


def test_contract_validation_errors():
    with pytest.raises(DerivationError):
        _contract(output_name="  ")
    with pytest.raises(DerivationError):
        _contract(generator_version="")
    with pytest.raises(DerivationError):
        _contract(inputs=(_input("a", 1), _input("a", 2)))  # duplicate name
    with pytest.raises(DerivationError):
        _contract(identity_sources=("missing",))  # unknown identity source
    with pytest.raises(DerivationError):
        _contract(dependencies=(("a", "ghost"),))  # unknown dependency target
    with pytest.raises(DerivationError):
        _contract(dependencies=(("ghost", "a"),))  # unknown dependency node


def test_contract_non_mixing_rejects_derived_identity_source():
    # A DERIVED value may never seed identity determinism (AIF-L20).
    with pytest.raises(DerivationPurityError):
        DerivationContract(
            output_name="o",
            generator_version="gen/1.0.0",
            inputs=(_input("d", {"v": 1}, kind=InputKind.DERIVED),),
            identity_sources=("d",),
        )
    # SOURCE / RECORDED identity sources are permitted.
    ok = DerivationContract(
        output_name="o",
        generator_version="gen/1.0.0",
        inputs=(_input("r", {"v": 1}, kind=InputKind.RECORDED),),
        identity_sources=("r",),
    )
    assert ok.identity_sources == ("r",)


# --------------------------------------------------------------------------------
# Dependency-graph validation
# --------------------------------------------------------------------------------


def test_dependency_graph_is_acyclic_and_closed():
    contract = _contract(dependencies=(("b", "a"),))
    order = contract.validate_dependencies()
    # a before b before the output.
    assert order.index("a") < order.index("b") < order.index("report")


def test_dependency_graph_detects_cycle():
    contract = _contract(dependencies=(("a", "b"), ("b", "a")))
    with pytest.raises(DependencyError):
        contract.validate_dependencies()


# --------------------------------------------------------------------------------
# DerivationEngine — deterministic, reproducible, purity-enforcing
# --------------------------------------------------------------------------------


def test_derive_is_deterministic_and_stamped():
    engine = DerivationEngine()
    contract = _contract()
    values = {"a": {"x": 1}, "b": {"y": 2}}
    result = engine.derive(contract, _sum_deriver, values)
    assert result.output == {"total": 3}
    assert result.output_digest == content_digest({"total": 3}).value
    assert result.generator_version == "gen/1.0.0"
    assert result.stamp["generator_version"] == "gen/1.0.0"
    assert dict(result.input_digests) == contract.digest_map
    assert len(engine) == 1
    assert "report" in engine
    assert engine.get("report") == result
    assert engine.results == (result,)


def test_derive_is_idempotent_and_conflict_detected():
    engine = DerivationEngine()
    contract = _contract()
    values = {"a": {"x": 1}, "b": {"y": 2}}
    first = engine.derive(contract, _sum_deriver, values)
    again = engine.derive(contract, _sum_deriver, values)
    assert first == again
    assert len(engine) == 1
    # A different generator version for the same output name conflicts.
    contract_v2 = _contract(generator_version="gen/2.0.0")
    with pytest.raises(DerivationError):
        engine.derive(contract_v2, _sum_deriver, values)


def test_derive_rejects_input_drift():
    engine = DerivationEngine()
    contract = _contract()
    # Supplied content differs from the pinned digest ⇒ immutable-input violation.
    with pytest.raises(DerivationError):
        engine.derive(contract, _sum_deriver, {"a": {"x": 999}, "b": {"y": 2}})


def test_derive_rejects_mismatched_inputs():
    engine = DerivationEngine()
    contract = _contract()
    with pytest.raises(DerivationError):
        engine.derive(contract, _sum_deriver, {"a": {"x": 1}})  # missing 'b'
    with pytest.raises(DerivationError):
        engine.derive(
            contract, _sum_deriver, {"a": {"x": 1}, "b": {"y": 2}, "c": {}}
        )  # unexpected 'c'


def test_derive_rejects_impure_deriver():
    engine = DerivationEngine()
    contract = _contract()
    values = {"a": {"x": 1}, "b": {"y": 2}}
    calls = {"n": 0}

    def impure(_values):
        calls["n"] += 1
        return {"nonce": calls["n"]}  # changes every call — hidden state

    with pytest.raises(DerivationPurityError):
        engine.derive(contract, impure, values)


def test_derive_rejects_noncanonical_output():
    engine = DerivationEngine()
    contract = _contract()
    values = {"a": {"x": 1}, "b": {"y": 2}}
    with pytest.raises(DerivationError):
        engine.derive(contract, lambda _v: object(), values)  # not serializable


# --------------------------------------------------------------------------------
# Verification (bit replay)
# --------------------------------------------------------------------------------


def test_verify_confirms_and_detects_drift():
    engine = DerivationEngine()
    contract = _contract()
    values = {"a": {"x": 1}, "b": {"y": 2}}
    result = engine.derive(contract, _sum_deriver, values)
    assert engine.verify(contract, _sum_deriver, values, result) is True
    # A different deriver produces a different output ⇒ verification fails.
    assert engine.verify(contract, lambda _v: {"total": 0}, values, result) is False
    # Input drift makes _prepare fail ⇒ verify returns False.
    assert engine.verify(contract, _sum_deriver, {"a": {"x": 9}, "b": {"y": 2}}, result) is False


def test_get_fails_closed():
    engine = DerivationEngine()
    with pytest.raises(DerivationError):
        engine.get("missing")


# --------------------------------------------------------------------------------
# Profile propagation + export + result roundtrip
# --------------------------------------------------------------------------------


def test_derivation_respects_profile():
    engine = DerivationEngine()
    profile = CanonicalProfile("ucos-ccf/keep-ws", strip_trailing_whitespace=False)
    inp = DerivationInput.of("a", "raw   ", profile=profile)
    contract = DerivationContract(output_name="o", generator_version="gen/1.0.0", inputs=(inp,))
    result = engine.derive(contract, lambda v: v["a"], {"a": "raw   "}, profile=profile)
    assert result.output_digest == content_digest("raw   ", profile).value


def test_export_and_result_roundtrip():
    engine = DerivationEngine()
    contract = _contract()
    result = engine.derive(contract, _sum_deriver, {"a": {"x": 1}, "b": {"y": 2}})
    exported = engine.export()
    assert exported["ledger_format"] == DERIVATION_LEDGER_FORMAT
    assert exported["count"] == 1
    assert engine.to_dict() == exported
    restored = DerivationResult.from_dict(result.to_dict())
    assert restored.output_digest == result.output_digest
    assert restored.input_digests == result.input_digests


def test_result_from_dict_errors():
    with pytest.raises(DerivationError):
        DerivationResult.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(DerivationError):
        DerivationResult.from_dict({"output_name": "o"})  # missing fields

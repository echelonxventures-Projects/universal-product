# 04 — DETERMINISTIC REGENERATION

**Claim:** the four projection trees are a pure, byte-stable function of
canonical repository truth — independent regenerations produce identical output.

---

## 1. Determinism proof (byte-identical aggregate hash)

The guard scope was hashed as a single aggregate SHA-256 over the sorted file
set:

```
find 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL -type f \
  | sort | xargs shasum -a 256 | shasum -a 256
```

| Observation point | Aggregate SHA-256 |
|---|---|
| Working tree (pre-mission regeneration) | `9be632c13325316fc82cb818c94bf2c6ddc45b2b8e623c862163c112f31d170a` |
| After `register.sh` run #1 | `9be632c13325316fc82cb818c94bf2c6ddc45b2b8e623c862163c112f31d170a` |
| After `register.sh` run #2 | `9be632c13325316fc82cb818c94bf2c6ddc45b2b8e623c862163c112f31d170a` |

**Three independent regenerations → identical hash.** `DETERMINISM: PASS`.

## 2. Why regeneration is byte-stable

Generation stamps do not defeat determinism. `ukbx.py::_stamp_eq_json`
neutralizes the `generated_at` stamp (and any nested value equal to it) before
comparing new output to the on-disk file, and **skips the rewrite** when the
substantive content is unchanged (`UKB-ADV-INV-07` reproducibility). Therefore:

- A regeneration that changes content updates the file (and its stamp) once.
- Any subsequent regeneration over unchanged truth is a **no-op write** → the
  file, including its stamp, is preserved byte-for-byte → the guard stays clean.

This is why the committed `certification.json` `generated_at` advanced exactly
once (995→1002 artifacts was a real content change) and then remained stable
across run #1 and run #2.

## 3. Identifier stability

IDs and pages are allocated **append-only** from the immutable
`id-ledger.json`; nothing is renumbered or reused. Re-running the pipeline over
the same truth allocates **no** new IDs (page cursor stays `9134`), confirming
idempotency at the identifier layer as well as the byte layer.

## 4. Environment note

Regeneration used the repository's canonical `.ec1-venv` (Python 3.12). `ukb.py`
depends only on the Python standard library plus the local `config.py` /
`governance_telemetry.py`, so the generators carry no third-party ordering
hazards; determinism is a property of the code, not the interpreter build.

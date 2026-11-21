# UCOS-UFEP-001 · Baseline and No-Drift Register

## The baseline a freeze would seal (CEP-007 Article VIII)

Content-addressed and computed as a pure function of the ratified act, its bound
evidence digests and its ratification record. Computing a baseline is not sealing one:
nothing here is recorded frozen, and the version is the baseline's own digest so it
cannot drift from the material it summarises.

| Subject | State | Version | Baseline digest | Lineage |
|---|---|---|---|---|
| `UFEP-SUB-01` | `ELIGIBLE` | 5cb6b1cc7813 | 5cb6b1cc78131c27937ba8541890fc92 | — (no predecessor) |
| `UFEP-SUB-02` | `ELIGIBLE` | fe71b32d2afb | fe71b32d2afb1b071f41fc63cf63b779 | — (no predecessor) |
| `UFEP-SUB-03` | `ELIGIBLE` | 42acbde9dd3c | 42acbde9dd3c653f4821e40cd04af0d6 | — (no predecessor) |
| `UFEP-SUB-04` | `ELIGIBLE` | 2390e02ae665 | 2390e02ae665cf92a8a3fd20d7c4f1ed | — (no predecessor) |
| `UFEP-SUB-05` | `ELIGIBLE` | 169a912c8313 | 169a912c8313cef063b63168110d2072 | — (no predecessor) |

## No-drift guard over the located frozen baseline (CEP-007 Article X)

| Manifest | Entries | Verified | Drifted | Missing | Notice located |
|---|---|---|---|---|---|
| `99-FREEZE/SOURCE-HASHES.txt` | 13 | 13 | 0 | 0 | YES |

## Freeze authorization (recorded, not acted upon)

| Authorization | Instrument | Located | Acted upon here |
|---|---|---|---|
| `UFEP-AUTH-01` | `00-MASTER/UCOS-CRAT-001/07-FOUNDATION-FREEZE-AUTHORIZATION.md` | YES | NO |

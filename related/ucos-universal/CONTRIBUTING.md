# Contributing to UCOS

UCOS is specified before it is built. Every change goes through the same path: change the source, regenerate, check, review.

## The one command
```bash
tools/ci.sh            # everything CI runs, in the same order, with the same pinned tools
tools/ci.sh --fix      # also regenerate generated files before checking
```
`tools/ci.sh` creates a local virtual environment from `tools/requirements.txt` (hash-pinned; regenerate with `python3 tools/lock_requirements.py`) the first time it runs. Go tools are pinned by version and installed into `.tools/bin`. PostgreSQL server binaries, Go, Node, buf and kubectl are needed for the full run; checks whose tool is missing are skipped locally and mandatory in CI. CI runs exactly this script; nothing else gates a merge.

## What is a source and what is generated
| Source (edit these) | Generated (never edit by hand) | Generator |
|---|---|---|
| `constitutions/**`, `UCOS-MASTER-ARCHITECTURE.md`, `docs/**`, `business/**` | — | — |
| `tools/gen_manifests.py` (hand-authored manifests in Part 1) | `spec/capabilities/packs/*.yaml` | `tools/gen_manifests.py` |
| Constitutions + manifests | `spec/registries/errors.yaml`, `spec/object-types/*.json` | `tools/gen_registries.py` |
| Manifests + `spec/events/payloads/hand/*.json` | `spec/api/openapi/capabilities/*.yaml`, `spec/events/payloads/*.json`, `spec/api/asyncapi/ucos-events.yaml` | `tools/gen_contracts.py` |
| `spec/api/proto/**` | `kernel/gen/**` (Go gRPC code) | `buf generate` with pinned plugins (run by `tools/ci.sh --fix`) |
| `tools/gen_golden_data.py` | `generated/golden-data/` (not committed; digest in `spec/seed/golden-data.sha256`) | `tools/gen_golden_data.py` |
| `spec/api/openapi/kernel/*.yaml`, `spec/acceptance/**`, `spec/slo/**`, `spec/policies/**`, `spec/decisions/**`, `spec/workflows/**`, `spec/seed/**`, `db/**`, `kernel/pkg/**`, `deploy/**` | — | — |

Pull requests fail if a generated file differs from what its generator produces. On `main`, the CI bot regenerates and commits them automatically.

## Changing the architecture
1. **Small spec change** (an attribute, a gap rule, a decision default): edit the constitution, add a line to the amendments register in `constitutions/README.md`, open a pull request.
2. **New universe, ownership change, or law change**: open a pull request with an ADR in `docs/adr/` (copy the headings of any existing ADR). It needs Architecture Board approval (U01, gate `ARCH-AUTH-01`).
3. **Fold amendments into the master** at each phase exit: update the master, bump its version, and record them in master §35.

## Conventions
- Time fields follow U13 Appendix E.3; reserved names (`*At`, `window`, `retention`…) are only used with their canonical types.
- Every new gate id must be added to `spec/certification/gates.yaml`; the checker rejects unknown ids.
- Every new error code appears in its universe's spec text; the registry is regenerated from it.
- Commit messages: imperative mood, first line ≤ 72 characters.

## Security issues
Do not open public issues for vulnerabilities. See `SECURITY.md`.

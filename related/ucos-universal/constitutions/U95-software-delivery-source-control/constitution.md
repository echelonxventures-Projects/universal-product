# U95 — Software Delivery & Source Control Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U95-sdlc` |
| Layer | L7 Composition & Generation / L11 Operations |
| Domain | 09 Platform |
| Steward | `ucos:org:developer-experience` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 (platform monorepo, CI/CD, signed builds, GitOps), P3 (tenant definitions-as-code: two-way sync between Studio and Git), P5 (tenant developer workspaces for packs) |
| Depends on | U02 Governance (proposals ↔ pull requests), U57 Capability (packs built here), U74 Certification (CI gates), U65 Security (signing, secret scanning, SBOM), U73 Infra (GitOps deploy), U58 Composition (PD/blueprint as code), U09 Identity (developer identities, SSO), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | every engineering activity; tenants who manage definitions as code; U96 Collaboration (issue↔commit links) |
| Master references | §27.3 (delivery pipeline), §31.3 (repo), §31.4 (CLI), user requirement "git" (A-40) |

> Software Delivery owns **how code and definitions move from authoring to production**: source repositories (Git), branches, commits, pull/merge requests and code review, CI pipelines and their runs, build artifacts and provenance, release trains, GitOps state repositories, developer environments, and the **definitions-as-code bridge** that keeps Builder Studio (no-code) and Git (code) as two views of the same governed definitions.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| SDLC-L1 | Every production artifact (kernel, pack, IaC, definition bundle) is built by CI from a reviewed, signed commit; local builds never reach production. | Admission requires SLSA provenance referencing the CI system & commit. |
| SDLC-L2 | A pull request that changes governed definitions **is** a Governance ChangeProposal (linked 1:1); merge requires the proposal's approvals and certification. | Branch protection + status checks from U02/U74. |
| SDLC-L3 | Studio edits and Git edits converge: Studio writes commits (bot identity on behalf of the user) to the definitions repo; Git merges sync back to the registry; conflicts surface as merge conflicts, never silent overwrites. | Two-way sync service with optimistic concurrency on definition versions. |
| SDLC-L4 | Branch protection, mandatory review (≥ 1, ≥ 2 for T0/T1 and security-relevant paths via CODEOWNERS), signed commits, secret scanning and dependency review are enforced on all UCOS repos. | Repo policy as code; audit. |
| SDLC-L5 | Git provider is a port (GitHub, GitLab, Bitbucket, Gitea/Forgejo self-hosted); UCOS never depends on one vendor's features for correctness. | `scm.provider` abstract capability. |

## 2. Objects
`Repository { id, provider, url, kind: platform-mono|pack|definitions (tenant)|gitops-state|docs, owner, default branch, protection policy }` · `ChangeRequest (PR/MR) { repo, source/target branch, author, reviewers, checks, linkedProposal (U02), linkedIssues (U96), status }` · `PipelineDefinition { repo, stages (build, lint (ucos lint), test, scan, sbom, sign, compose (golden PDs), certify, publish, deploy), triggers }` · `PipelineRun { definition, commit, status, artifacts, evidence (U68), duration: Duration }` · `Artifact { kind: image|pack|bundle|sdk|docs, digest, provenance (SLSA in-toto), signature, sbom }` · `ReleaseTrain { cadence (Temporal), included artifacts, status }` · `DefinitionsRepoMapping { tenant, repo, path conventions (spec/** per master §31.3), sync mode: studio-primary|git-primary|bidirectional }` · `DevEnvironment { owner, kind: cloud-workspace|local-devcontainer, sandbox tenant, TTL }`.

## 3. Commands, Queries, Events, APIs
Commands: `RegisterRepository`, `ApplyRepoPolicy`, `OpenChangeRequest` (from Studio publish or developer), `SyncDefinitions(direction)`, `RunPipeline`, `PromoteRelease`, `CreateDevEnvironment`.
Queries: `ProvenanceOf(artifact)`, `WhatShipped(release)`, `DiffDefinitions(ref1, ref2)`, `BlameDefinition(definition)` (who changed what, linked to proposals).
Events: `sdlc.pr.opened|merged`, `sdlc.pipeline.succeeded|failed`, `sdlc.artifact.published`, `sdlc.sync.conflict`.
Port: `scm.provider` (repos, PRs, checks, webhooks, branch protection), `ci.runner` (GitHub Actions, GitLab CI, Buildkite, Tekton).
```text
POST /v1/sdlc/repositories   POST /v1/sdlc/sync   GET /v1/sdlc/provenance?digest=   POST /hooks/scm/{provider}
```

## 4. Rules
Definitions repo layout = master §31.3 `spec/**`; one YAML file per definition; IDs stable; generated files under `generated/` never edited; CODEOWNERS map paths to universe stewards (U01 authorities); merge queue serialises definition merges per tenant to keep registry versions linear.

## 5. Security & Compliance
Supply-chain controls (SLSA L3, Sigstore, SBOM, dependency pinning, provenance verification at admission), secret scanning (pre-commit + server), least-privilege CI tokens (OIDC federation to clouds, no long-lived keys), change-management evidence for SOC 2/ISO (PR approvals + pipeline results archived to U68).

## 6. Gaps, AI, Ops, UI, Scale
```prolog
gap(unprotected_branch, R)       :- repository(R), production_source(R), not protected(R, default_branch).
gap(artifact_without_provenance, A) :- deployed_artifact(A), not slsa_provenance(A).
gap(definition_drift, T)         :- tenant(T), sync_mode(T, bidirectional), registry_hash(T) != repo_head_hash(T).
```
AI: code-review assistance, definition diffs explained in plain language, CI failure triage, pack scaffolding. Signals: DORA metrics (deployment frequency, lead time, change failure rate, MTTR), `pipeline_duration_s`, `sync_conflicts_total`. Views: developer portal (U63) integration, `sdlc.release.board`, `sdlc.sync.status` (Studio ↔ Git), `provenance.viewer`. T1 (build infra), T0 (admission verification).

## Appendix
- **C.** 0.1.0.

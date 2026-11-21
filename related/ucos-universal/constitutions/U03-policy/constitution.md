# U03 — Policy Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U03-policy` |
| Layer | L0 Constitution & Authority (runtime PDP in L8) |
| Domain | 08 Governance |
| Steward | `ucos:org:security-policy-engineering` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 |
| Depends on | U04 Meta, U01 Authority, U02 Governance, U09 Identity (principal attributes), U16 Context, U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | every command/query (L8), U66 Privacy (purpose obligations), U51 Agent (agent bounds), U73 Infra (admission policies) |
| Master references | §18.5, §19.3, L8 |

> Policy owns **runtime permission and obligation rules** and the engines that evaluate them: authorization policies (RBAC, ABAC, ReBAC and PBAC, unified in Cedar), obligations (masking, step-up, audit level, confirmation), infrastructure/admission policies (OPA), and the static analyser that proves policies safe. It does not own business rules about prices or eligibility (U53 Decision), or who may *decide* on changes (U01 Authority).

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| POL-L1 | Deny by default. Absence of a permit is a deny. | PDP semantics. |
| POL-L2 | Every command and query passes a PDP check with action = `<slug>:<Command>`. | Command bus + gateway PEP; pack SDK cannot bypass. |
| POL-L3 | Forbid overrides permit (Cedar semantics). Constitutional forbids (platform scope) cannot be overridden by tenants. | Policy layering (§5.1). |
| POL-L4 | Every policy set is statically analysed before activation: no tenant policy may permit cross-tenant access or contradict a platform forbid. | Cedar validator + SMT-based analyser in Governance validation. |
| POL-L5 | Decisions return obligations that the PEP MUST fulfil. If an obligation is not understood, the request is denied. | PEP implementation. |
| POL-L6 | Every decision is logged with the matched policy ids (sampled for reads per tier, full for writes). | Audit integration. |

---

## 2. Ontology
- **`Policy`**: one Cedar policy statement with metadata.
- **`PolicySet`**: a versioned bundle (platform, universe defaults from packs, tenant, organization).
- **`Obligation`**: an action the PEP must perform.
- **`EntitySchema`**: the Cedar schema of entity types and actions, **generated** from U04 object types and capability manifests.
- **`PolicyTemplate`**: parameterised policy (e.g. "owner-only for type X").
- **`AdmissionPolicy`**: OPA/Rego for infra and Kubernetes admission.
- **Layers** (evaluation precedence of forbids):

  | Layer | Author | Example |
  |---|---|---|
  | `platform` | Security steward (level 4) | tenant isolation forbid, agent bounds forbid |
  | `universe-default` | Pack (certified) | `commerce.cart.owner-only` |
  | `tenant` | Tenant security admin (level 2–3) | seller permissions |
  | `organization` | Org admin (level 2) | store manager limits |
  | `emergency` | Break-glass (U01) | temporary block of an action |

- **Obligation types:** `mask(fields, style)`, `redact(fields)`, `stepUpAuth(acr)`, `requireReason`, `requireConfirmation(by: human)`, `audit(level: standard|full)`, `notify(role)`, `rateLimit(class)`, `watermark`, `purpose(required: purposeId)`, `limit(maxRows)`, `simulateOnly`.

---

## 3. Objects

### 3.1 `ucos.policy.Policy`
| Attribute | Type | Notes |
|---|---|---|
| `id` | String (`<layer>.<slug>.<name>`) | e.g. `tenant.bazaar.seller-listing-edit` |
| `layer` | Enum | |
| `effect` | `permit|forbid` | derived from body |
| `body` | Cedar source | |
| `obligations` | Array<Obligation> | attached via annotation `@obligation("mask:phone")` |
| `description` | LocalizedText | plain-language explanation shown in UI |
| `owner` | PartyRef | |
| `tenant` | TenantRef or `platform` | |
| `version` | SemVer | |
| `status` | DefinitionStatus | |
| `tests` | Array<PolicyTestRef> | required |

### 3.2 `PolicySet`
`{ id, layer, scope (tenant/org), policies: [PolicyRef@version], entitySchemaVersion, compiledHash, status }`. Each blueprint pins a set of policy-set versions.

### 3.3 `PolicyTest`
```yaml
id: test.seller-cannot-edit-other-seller-listing
principal: { type: Identity, attrs: { roles: [seller], organization: org-A } }
action: catalog:UpdateListing
resource: { type: Catalog::Listing, attrs: { seller: org-B } }
context: { risk: { score: 10 } }
expect: DENY
```

### 3.4 Entity schema generation
Object types (U04) become Cedar entity types with attributes, references become entity references, and capability commands become actions with `appliesTo` resource types. Principal entities are `Identity`, `Agent`, `Service` and `Device`, with attributes from U09 (roles, organization, standing, acr) and U16 context. The generated schema is versioned. Policies are validated against it, so a misspelled attribute is a compile error.

---

## 4. Commands, Queries, Events, APIs & Runtime

| Command | Notes / Events |
|---|---|
| `ProposePolicy` (via Governance) | validates against schema, runs tests, runs analyser |
| `ActivatePolicySet` | compiled bundle distributed to cells → `policy.policyset.activated` |
| `AddPolicyTest` | |
| `AnalysePolicySet` | returns findings: unreachable, shadowed, conflicting, over-permissive |

**Runtime PDP API (gRPC, in-cell sidecar or library):**
```text
IsAuthorized(principal, action, resource, context) → { decision: ALLOW|DENY, obligations[], determiningPolicies[], diagnostics }
BatchIsAuthorized([...])             # list filtering
PartialEvaluate(principal, action, resourceType, context) → residual constraints  # converted to SQL WHERE for queries
```
`PartialEvaluate` makes list queries efficient: the residual (e.g. `resource.seller == "org-A"`) is translated into a query filter by the Object Service. Results are never fetched first and filtered afterwards.

```text
GET  /v1/policy/sets?layer=&tenant=        POST /v1/policy/policies   (proposal)
POST /v1/policy/sets/{id}:analyse          POST /v1/policy/simulate   (what would happen for principal X?)
GET  /v1/policy/schema?version=
```
**Errors:** `POL_DENIED` (403, with `determiningPolicies` returned only to privileged callers), `POL_OBLIGATION_UNSUPPORTED`, `POL_SCHEMA_MISMATCH`, `POL_ANALYSIS_FAILED`, `POL_TEST_FAILED`.

---

## 5. Rules & Algorithms

### 5.1 Layered evaluation (normative)
```text
decision = DENY
if any platform forbid matches → DENY (final)
if any emergency forbid matches → DENY (final)
permits ← matching permits from universe-default ∪ tenant ∪ organization
forbids ← matching forbids from universe-default ∪ tenant ∪ organization
if forbids ≠ ∅ → DENY
if permits ≠ ∅ → ALLOW with obligations = ∪ obligations(permits) ∪ obligations(platform 'always' policies)
```
Obligations are merged with the strictest-wins rule: the highest audit level, the highest ACR, and the union of masks.

### 5.2 Static analysis checks
| Check | Method |
|---|---|
| Tenant isolation preserved | prove: ∀ permit in tenant layer: resource.tenant == principal.tenant is implied (SMT over Cedar) |
| No permit contradicts platform forbid on agents/SoD | containment check |
| Shadowed / unreachable policies | Cedar validator + analysis |
| Over-permissive wildcard | lint: `action` unconstrained or `resource` unconstrained in tenant layer → finding |
| SoD pairs | from U09 role conflicts: prove no principal can be permitted both actions on the same resource where `createdBy == principal` |
| Test coverage | every policy has ≥ 1 ALLOW and ≥ 1 DENY test |

### 5.3 Platform baseline policies (seed)
```cedar
// P-001 tenant isolation
forbid (principal, action, resource)
when { resource has tenant && principal has tenant && resource.tenant != principal.tenant && !(context has tenantLink) };
// P-002 suspended principals
forbid (principal, action, resource) when { principal has status && principal.status != "active" };
// P-003 agents bounded by delegated authority (master §18.5)
forbid (principal is Agent, action, resource) unless { principal.authority.actions.contains(action) && context.agent.budgetRemaining > 0 };
// P-004 simulation isolation
forbid (principal, action, resource) when { context.simulation && action in Action::"group:external-side-effect" };
// P-005 asOf reads only
forbid (principal, action, resource) when { context has asOf && !context.simulation && action in Action::"group:write" };
```

---

## 6. Security & Compliance
- Policies are `internal`; tenant policies are `confidential`.
- PDP bundles are signed (cosign) and verified by cells. A stale bundle older than 10 min without heartbeat raises an alert, and the PEP keeps serving the last good bundle (fail-safe, not fail-open).
- Controls: access control policy (ISO A.5.15), least privilege (PCI 7.2), SoD.

## 7. Validation & Reuse
- Packs ship default policies as `universe-default`.
- Tenants extend with the tenant layer using templates in Studio (master W-policy editor).
- No pack code contains authorization `if` statements on roles; lint `POL-LINT-001` flags role-name literals in code.

## 8. Gaps & Evolution
```prolog
gap(command_without_policy, C)   :- command(C), active(C), not policy_covers_action(C).
gap(policy_without_tests, P)     :- policy(P), active(P), not has_allow_test(P) ; not has_deny_test(P).
gap(sod_unprovable, A, B)        :- sod_pair(A, B), not analysis_proves_sod(A, B).
gap(stale_bundle, Cell)          :- cell(Cell), bundle_age_minutes(Cell, M), M > 10.
```
**Evolution:** policy mining from audit logs proposes tighter policies based on unused permissions. It feeds access reviews.

## 9. AI
- **AI uses:** a natural-language-to-Cedar assistant in Studio (proposal plus generated tests; it must pass the analyser), explanation of denies to users ("You can't approve this payout because you created it"), and policy-mining suggestions.
- **Agents** can never modify policies.

## 10. Operations
- **Signals:** `pdp_latency_us` (p99 target < 5 ms remote, < 300 µs embedded), `pdp_decisions_total{decision}`, `deny_ratio{action}`, `obligation_failures_total` (must be 0), `bundle_age_seconds{cell}`.
- **Runbook:** a deny storm after a policy activation triggers automatic rollback via the Governance guard on `deny_ratio` (more than 3× baseline).

## 11. UI
- **Views:** `policy.editor` (Cedar with schema-aware autocomplete, plain-language preview, test table, analyser findings), `policy.template.gallery`, `policy.simulator` ("Can Ravi approve payout X?", with the determining policies shown), `policy.matrix` (roles × actions heat map).
- **UX:** every policy has a human description, and denies shown to end users use the localised explanation without exposing internals.

## 12. Scale
About 1M decisions/s per large cell, served by an embedded PDP in the gateway and command bus, with bundles in memory. A tenant policy set is typically under 500 policies. T0.

## Appendix
- **A.** OpenFGA for ReBAC-heavy social graphs (P6 evaluation).
- **B. Amendments:** master §18.5 gains layered precedence and `PartialEvaluate`.
- **C.** 0.1.0.

## Appendix D — Reality isolation (amendment A-28, from U77)
Platform policy P-004 is generalised:
```cedar
forbid (principal, action, resource)
when { action in Action::"group:external-side-effect"
       && context.frame.reality.sideEffectPolicy != "full"
       && !(context has realityBridge && context.realityBridge.allows.contains(action)) };
```

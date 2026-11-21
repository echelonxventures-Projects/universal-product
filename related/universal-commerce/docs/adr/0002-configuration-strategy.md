# ADR-0002: Configuration Strategy

## Status
Accepted

## Context
Platform must be configurable without code changes per constitutional principles.

## Decision
- All behavior controlled through registry-based configuration
- Policies over branching logic
- Domain configurations in YAML/JSON
- Feature flags for gradual rollouts

## Examples
```yaml
# config/tenant-123/promotions.yaml
offer:
  maxRedemptions: 1000
  eligibleSegments: ["premium", "vip"]
```

## Consequences
- Non-developers can configure behavior
- Runtime configuration updates
- Versioning and audit trail required

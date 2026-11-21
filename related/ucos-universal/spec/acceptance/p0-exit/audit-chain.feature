@platform:sample-p0 @phase:0 @gate:SEC-TENANT-01 @universe:U68
Feature: Tamper-evident audit chain (Phase 0 exit)
  Every command is audited in a per-tenant, per-day hash chain; tampering is detected (AUD-L1).

  Background:
    Given the blueprint for "sample-p0" is active for tenant "sample" in cell "sandbox-1"
    And a user "asha" of tenant "sample" with role "sample-editor"

  Scenario: The chain of a day verifies
    When "asha" sends command "sample:CreateNote" with title "First"
    And "asha" sends command "sample:CreateNote" with title "Second"
    And the audit appender seals the chain for tenant "sample" for today
    Then the audit chain for tenant "sample" for today verifies
    And the daily Merkle root is anchored to write-once storage

  Scenario: An altered record breaks verification
    Given "asha" sends command "sample:CreateNote" with title "Original"
    And the audit appender seals the chain for tenant "sample" for today
    When an operator with database access alters an audit record for tenant "sample"
    Then the audit chain for tenant "sample" for today fails verification at that record
    And an alert "audit.chain.broken" is raised

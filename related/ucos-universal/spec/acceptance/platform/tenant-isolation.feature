@platform:any @phase:0 @gate:SEC-TENANT-01 @universe:U10
Feature: Tenant isolation
  No tenant can read or change another tenant's data through any path (Law L8).

  Background:
    Given the tenants "bazaar" and "kala" run the golden platform "d2c-in-ae" in the same cell
    And the cell runs in reality "simulated"

  Scenario Outline: Cross-tenant access is denied
    Given an order exists for tenant "kala"
    When a user of tenant "bazaar" requests that order through "<path>"
    Then the response has status 404
    And an audit record of the denied access exists for tenant "bazaar"

    Examples:
      | path            |
      | rest-object     |
      | rest-query      |
      | search          |
      | document-url    |
      | event-replay    |

  Scenario: Token for one tenant with the host of another is rejected
    When a token issued for tenant "bazaar" is used on the host of tenant "kala"
    Then the response has status 401

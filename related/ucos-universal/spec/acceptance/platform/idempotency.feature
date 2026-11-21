@platform:any @phase:0 @gate:TEST-SCEN-01 @universe:U61
Feature: Idempotent commands
  Every command carries an Idempotency-Key (KERNEL-DESIGN §3).

  Background:
    Given the tenant "bazaar" runs the golden platform "d2c-in-ae"
    And the cell runs in reality "simulated"

  Scenario: Replaying the same request returns the stored response
    When the command "order:PlaceOrder" is sent twice with the same idempotency key and the same body
    Then both responses are identical
    And the event "order.order.placed" is emitted exactly once

  Scenario: Reusing a key with a different body is rejected
    When the command "order:PlaceOrder" is sent twice with the same idempotency key and a different body
    Then the second response has status 409 and error "IDEMPOTENCY_KEY_REUSED"

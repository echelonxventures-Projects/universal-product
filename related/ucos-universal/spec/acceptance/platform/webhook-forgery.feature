@platform:d2c-in-ae @phase:1 @gate:SEC-PAY-01 @universe:U29 @universe:U62
Feature: Forged payment webhooks are rejected
  Webhook bodies are never trusted for amounts or states (PY-S1).

  Background:
    Given the tenant "bazaar" runs the golden platform "d2c-in-ae"
    And the cell runs in reality "simulated"
    And a pending payment intent "PI-1" for "1598.00" "INR"

  Scenario: Webhook with an invalid signature
    When a payment webhook for "PI-1" arrives with an invalid signature
    Then the response has status 401
    And the payment intent "PI-1" status is "requires_payment"

  Scenario: Webhook with a valid signature but a different amount
    When a payment webhook for "PI-1" arrives with a valid signature and amount "1.00" "INR"
    And the payment simulator reports the true amount "1598.00" "INR" as captured
    Then the payment intent "PI-1" status is "captured"
    And the captured amount is "1598.00" "INR"

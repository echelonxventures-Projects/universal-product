@platform:d2c-in-ae @phase:1 @gate:TEST-SCEN-01 @universe:U26 @universe:U29 @universe:U31
Feature: Return and refund
  A delivered order is returned within the return window and refunded to the original method.

  Background:
    Given the tenant "bazaar" runs the golden platform "d2c-in-ae"
    And the cell runs in reality "simulated"
    And a delivered order "ORD-1" for buyer "priya" of 2 units of "SKU-TSHIRT-M" paid by "upi"

  Scenario: Return within the window is refunded
    Given the clock is "P3D" after delivery of "ORD-1"
    When "priya" requests a return of 1 units from order "ORD-1" with reason "size-issue"
    And the operator approves the return for order "ORD-1"
    And the return for order "ORD-1" is received in condition "resellable"
    Then a refund of "799.00" "INR" is issued to the original payment method
    And a tax document of kind "credit-note" is issued for the order
    And the event "payment.refund.issued" is emitted exactly once

  Scenario: Return after the window is refused
    Given the clock is "P8D" after delivery of "ORD-1"
    When "priya" requests a return of 1 units from order "ORD-1" with reason "size-issue"
    Then the request fails with error "ORD_RETURN_WINDOW_CLOSED"

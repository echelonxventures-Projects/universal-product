@platform:d2c-in-ae @phase:1 @gate:TEST-SCEN-01 @universe:U29 @universe:U53
Feature: Cash on delivery in India
  COD is allowed by decision table within limits and confirmed without a capture.

  Background:
    Given the tenant "bazaar" runs the golden platform "d2c-in-ae"
    And the cell runs in reality "simulated"
    And the listing "SKU-MUG" is published at "349.00" "INR" with tax category "household-standard"
    And the location "BLR-WH1" has 50 units of "SKU-MUG"
    And a verified buyer "ravi" with delivery address in "ucos:jur:IN-MH"

  Scenario: COD order within the limit is confirmed
    When "ravi" adds 1 units of "SKU-MUG" to the cart
    And "ravi" checks out with payment method "cod"
    Then the order status is "confirmed"
    And the event "order.order.confirmed" is emitted exactly once
    And the decision "commerce.cod-eligibility" returned "true"

  Scenario: COD above the limit is refused
    When "ravi" adds 150 units of "SKU-MUG" to the cart
    And "ravi" checks out with payment method "cod"
    Then the decision "commerce.cod-eligibility" returned "false" with reason "cod.reason.amount"
    And no event "order.order.placed" is emitted

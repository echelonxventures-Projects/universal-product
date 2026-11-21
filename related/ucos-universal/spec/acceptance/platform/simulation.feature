@platform:any @phase:1 @gate:ARCH-CTX-02 @universe:U16 @universe:U77
Feature: Simulation has no side effects
  In a simulated reality, adapters switch to simulators and nothing leaves the platform (CTX-L4, P-004).

  Scenario: A full purchase in a simulated reality sends nothing outside
    Given the tenant "bazaar" runs the golden platform "d2c-in-ae"
    And the cell runs in reality "simulated"
    And a verified buyer "priya" with delivery address in "ucos:jur:IN-KA"
    And the listing "SKU-MUG" is published at "349.00" "INR" with tax category "household-standard"
    And the location "BLR-WH1" has 5 units of "SKU-MUG"
    When "priya" adds 1 units of "SKU-MUG" to the cart
    And "priya" checks out with payment method "upi"
    And the payment simulator captures the payment
    Then no request reached a real external provider
    And every message was captured by the messaging simulator

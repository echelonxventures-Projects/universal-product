@platform:d2c-in-ae @phase:1 @gate:TEST-SCEN-01 @universe:U24 @universe:U29 @universe:U26
Feature: Buyer in India pays by UPI
  The D2C reference platform takes an order in India, collects GST and confirms it after capture.

  Background:
    Given the tenant "bazaar" runs the golden platform "d2c-in-ae"
    And the cell runs in reality "simulated"
    And the listing "SKU-TSHIRT-M" is published at "799.00" "INR" with tax category "apparel-low"
    And the location "BLR-WH1" has 20 units of "SKU-TSHIRT-M"
    And a verified buyer "priya" with delivery address in "ucos:jur:IN-KA"

  Scenario: Successful UPI payment confirms the order
    When "priya" adds 2 units of "SKU-TSHIRT-M" to the cart
    And "priya" checks out with payment method "upi"
    And the payment simulator captures the payment
    Then the order status is "confirmed"
    And the order total is "1598.00" "INR" including tax "76.10" "INR"
    And the event "order.order.placed" is emitted exactly once
    And the event "payment.payment-intent.captured" is emitted exactly once
    And the event "order.order.confirmed" is emitted exactly once
    And a tax document of kind "invoice" is issued for the order
    And 2 units of "SKU-TSHIRT-M" are reserved at "BLR-WH1"
    And a message of purpose "order-confirmation" is sent to "priya" on channel "whatsapp"

  Scenario: Declined UPI payment does not confirm the order
    When "priya" adds 1 units of "SKU-TSHIRT-M" to the cart
    And "priya" checks out with payment method "upi"
    And the payment simulator declines the payment with reason "insufficient-funds"
    Then the order status is "payment_failed"
    And no event "order.order.confirmed" is emitted
    And the reservation for "SKU-TSHIRT-M" is released within "PT15M"

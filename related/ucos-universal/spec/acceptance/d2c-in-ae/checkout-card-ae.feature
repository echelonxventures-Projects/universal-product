@platform:d2c-in-ae @phase:1 @gate:TEST-SCEN-01 @universe:U31 @universe:U14
Feature: Buyer in the UAE pays by card with VAT
  Adding the second country needed no kernel change (Phase 1 exit criterion).

  Background:
    Given the tenant "bazaar" runs the golden platform "d2c-in-ae"
    And the cell runs in reality "simulated"
    And the listing "SKU-TSHIRT-M" is published at "39.00" "AED" with tax category "apparel-low"
    And the location "DXB-WH1" has 10 units of "SKU-TSHIRT-M"
    And a verified buyer "ali" with delivery address in "ucos:jur:AE-DU"

  Scenario: Card payment with 5% VAT
    When "ali" adds 1 units of "SKU-TSHIRT-M" to the cart
    And "ali" checks out with payment method "card"
    And the payment simulator captures the payment
    Then the order status is "confirmed"
    And the order total is "39.00" "AED" including tax "1.86" "AED"
    And a tax document of kind "tax-invoice" is issued for the order
    And no card number is present in any stored record or log

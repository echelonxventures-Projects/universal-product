@platform:b2b-in @phase:1 @gate:TEST-SCEN-01 @universe:U31 @universe:U42
Feature: B2B GST e-invoice with IRN
  B2B supplies above the threshold are registered with the IRP before the invoice is delivered.

  Background:
    Given the tenant "metro-distrib" runs the golden platform "b2b-in"
    And the cell runs in reality "simulated"
    And a business buyer "apex-hotels" with GSTIN "29ABCDE1234F1Z5" in "ucos:jur:IN-KA"
    And the listing "SKU-RICE-25KG" is published at "1450.00" "INR" with tax category "food-5"

  Scenario: Invoice receives an IRN
    When "apex-hotels" places a purchase order for 40 units of "SKU-RICE-25KG" on credit terms "NET30"
    Then a tax document of kind "invoice" is issued for the order
    And the e-invoice simulator registers the document and returns an IRN
    And the event "tax.einvoice.registered" is emitted exactly once
    And the invoice document carries the signed QR code

  Scenario: IRP outage queues the registration
    Given the e-invoice simulator is unavailable
    When "apex-hotels" places a purchase order for 10 units of "SKU-RICE-25KG" on credit terms "NET30"
    Then the e-invoice registration is queued for retry before the legal deadline
    And an alert "tax.einvoice.registration-delayed" is raised

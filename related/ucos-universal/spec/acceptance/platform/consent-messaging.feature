@platform:d2c-in-ae @phase:1 @gate:CMP-MAP-01 @universe:U40 @universe:U66
Feature: Consent-aware messaging
  Marketing needs consent; transactional notices do not; Indian SMS uses DLT templates.

  Background:
    Given the tenant "bazaar" runs the golden platform "d2c-in-ae"
    And the cell runs in reality "simulated"
    And a verified buyer "ravi" with delivery address in "ucos:jur:IN-MH"

  Scenario: Marketing without consent is blocked
    Given "ravi" has not consented to purpose "marketing-whatsapp"
    When a campaign message of purpose "marketing-whatsapp" is sent to "ravi"
    Then the send fails with error "COMM_NO_CONSENT"

  Scenario: Transactional SMS in India uses a registered DLT template
    When a message of purpose "otp" is sent to "ravi" on channel "sms"
    Then the messaging simulator received a DLT template id and header id

@platform:any @phase:0 @gate:TEST-COMP-01 @universe:U58
Feature: Deterministic composition
  The same platform definition and registry snapshot always give the same blueprint (Law L18).

  Scenario Outline: Golden platforms compose identically and without mandatory gaps
    When the platform definition "<pd>" is composed twice against the same snapshot
    Then both blueprint ids are identical
    And the blueprint equals the checked-in expected blueprint for "<pd>"
    And the gap report has 0 mandatory gaps

    Examples:
      | pd             |
      | d2c-in-ae      |
      | b2b-in         |
      | omnichannel-in |
      | marketplace-in-ae |

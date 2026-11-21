@platform:sample-p0 @phase:0 @gate:ARCH-TMP-01 @gate:ARCH-TMP-03 @universe:U13
Feature: Temporal triggers fire on time (Phase 0 exit)
  Scheduled work goes only through the trigger engine and respects time zones and business calendars.

  Background:
    Given the blueprint for "sample-p0" is active for tenant "sample" in cell "sandbox-1"
    And a user "asha" of tenant "sample" with role "sample-editor"

  Scenario: A reminder fires at its TimePoint
    Given the clock is "2027-01-10T09:00:00Z"
    When "asha" schedules a reminder on a note for "2027-01-10T09:30:00Z"
    And the clock advances by "PT31M"
    Then the event "sample.note.reminded" is emitted exactly once

  Scenario Outline: Daily recurrence across a daylight-saving change
    Given the clock is "<start>"
    When a recurring trigger "FREQ=DAILY;BYHOUR=9;BYMINUTE=0" is scheduled in time zone "<tz>"
    And the clock advances by "P3D"
    Then the trigger fired 3 times, each at 09:00 local time in "<tz>"

    Examples:
      | start                | tz               |
      | 2027-03-27T00:00:00Z | Europe/London    |
      | 2027-03-13T00:00:00Z | America/New_York |
      | 2027-01-10T00:00:00Z | Asia/Kolkata     |

  Scenario: A business-time deadline skips holidays
    Given the business calendar "IN-default" has business hours "09:00-18:00" on weekdays and holiday "2027-01-26"
    And the clock is "2027-01-25T10:00:00+05:30"
    When a deadline of "PT16H" business time is scheduled on calendar "IN-default"
    Then the deadline is "2027-01-27T17:00:00+05:30"

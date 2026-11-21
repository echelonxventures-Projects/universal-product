@platform:sample-p0 @phase:0 @gate:GAP-000 @gate:ARCH-CAP-01 @universe:U57 @universe:U58 @universe:U74 @universe:U73
Feature: Sample pack goes from spec to a running object (Phase 0 exit)
  An object type that exists only in spec/ is composed, certified, activated and used through the kernel.

  Background:
    Given an empty cell "sandbox-1" in reality "simulated"
    And the registry snapshot is built from the repository at the current commit

  Scenario: Compose, certify and activate the sample platform
    When the platform definition "sample-p0" is composed twice against the same snapshot
    Then both blueprint ids are identical
    And the blueprint equals the checked-in expected blueprint for "sample-p0"
    And the gap report has 0 mandatory gaps
    When the blueprint for "sample-p0" is certified with profile "blueprint"
    Then every gate in profile "blueprint" passes or is waived
    And a signed attestation exists for the blueprint
    When the Architecture Board approves activation of the blueprint for tenant "sample"
    And the activation agent activates the blueprint in cell "sandbox-1"
    Then the activation reaches phase "COMPLETE"
    And the pack "sample.notes" describes exactly the operations in its manifest

  Scenario: The object type works end to end through the kernel
    Given the blueprint for "sample-p0" is active for tenant "sample" in cell "sandbox-1"
    And a user "asha" of tenant "sample" with role "sample-editor"
    When "asha" sends command "sample:CreateNote" with title "Kernel works"
    Then the object of type "ucos.sample.Note" exists with status "draft"
    And the event "sample.note.created" is emitted exactly once
    And an audit record for "sample:CreateNote" exists for tenant "sample"
    When "asha" sends command "sample:PublishNote" for the note
    Then the object of type "ucos.sample.Note" exists with status "published"

Feature: Convert Lambda to SAM template

  # Assumption: We already have python files with handlers defined for lambda functions
  Scenario:
    Given I generate a list of lambda functions from python files
    When I generate SAM template from the list of lambda functions
    Then I invoke the SAM template using sample event

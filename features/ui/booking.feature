@ui @booking @wip
Feature: Room Booking
  As a potential guest
  I want to book a room
  So that I can stay at the hotel

  Background:
    Given I am on the home page

  Scenario: Access booking calendar from room
    When I click book room for the first room
    Then I should see the booking calendar

  Scenario: Complete a room booking
    When I click book room for the first room
    Then I should see the booking calendar
    When I select dates for a 2 night stay
    And I fill in the guest details
      | field     | value            |
      | firstname | John             |
      | lastname  | Smith            |
      | email     | john@example.com |
      | phone     | 01234567890      |
    And I submit the booking
    Then the booking should be successful

  @negative
  Scenario: Booking requires all guest details
    When I click book room for the first room
    Then I should see the booking calendar
    When I select dates for a 2 night stay
    And I fill in the guest details
      | field     | value |
      | firstname | John  |
      | lastname  |       |
      | email     |       |
      | phone     |       |
    And I submit the booking
    Then I should see a booking error

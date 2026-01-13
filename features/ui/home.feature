@ui @home
Feature: Home Page
  As a potential guest
  I want to view the hotel information and available rooms
  So that I can decide to make a booking

  Background:
    Given I am on the home page

  @smoke
  Scenario: Home page displays hotel information
    Then I should see the hotel name
    And I should see at least 1 room(s)
    And I should see the contact form

  Scenario: View room listings
    Then I should see at least 1 room(s)

  @contact
  Scenario: Submit contact form with valid information
    When I fill in the contact form
      | field   | value                              |
      | name    | Test User                          |
      | email   | test@example.com                   |
      | phone   | 01234567890                        |
      | subject | Inquiry about room availability    |
      | message | I would like to know more details. |
    And I submit the contact form
    Then I should see a contact success message

  @contact @negative
  Scenario: Contact form requires all fields
    When I fill in the contact form
      | field   | value    |
      | name    | Test     |
      | email   |          |
      | phone   |          |
      | subject | Test     |
      | message | Test msg |
    And I submit the contact form
    Then I should not see a contact success message

  @wip
  Scenario: Click book room opens calendar
    When I click book room for the first room
    Then I should see the booking calendar

@ui @admin
Feature: Admin Panel
  As a hotel administrator
  I want to access the admin panel
  So that I can manage rooms, bookings, and messages

  Background:
    Given I am on the admin page

  @login @wip
  Scenario: Successful admin login
    When I login as admin
    Then I should be logged in

  @login @negative
  Scenario: Login with invalid credentials
    When I login with username "wronguser" and password "wrongpass"
    Then I should see a login error
    And I should not be logged in

  @login
  Scenario: Logout from admin panel
    When I login as admin
    Then I should be logged in
    When I logout
    Then I should not be logged in

  @rooms
  Scenario: View rooms in admin panel
    When I login as admin
    Then I should be logged in
    And I should see at least 1 room(s) in the admin list

  @rooms @wip
  Scenario: Create room from admin panel
    When I login as admin
    Then I should be logged in
    When I create a room "401" of type "Double"
    Then I should see at least 1 room(s) in the admin list

  @navigation
  Scenario: Navigate to different admin sections
    When I login as admin
    Then I should be logged in
    When I navigate to branding settings
    Then the URL should contain "admin"

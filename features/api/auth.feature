@api @auth
Feature: Authentication API
  As an API consumer
  I want to authenticate with the system
  So that I can access protected resources

  Background:
    Given the base URL is configured

  @smoke
  Scenario: Successful admin login
    Given I am not authenticated
    When I am authenticated as admin
    Then the token should be valid

  @negative
  Scenario: Login with invalid credentials
    Given I am not authenticated
    When I attempt to login with invalid credentials
    Then the response status code should be 200
    # Note: Restful Booker returns 200 even for invalid credentials
    # but with reason "Bad credentials" in the response

  Scenario: Login with specific credentials
    Given I am not authenticated
    When I am authenticated as "admin" with password "password123"
    Then the token should be valid

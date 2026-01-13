@api @bookings
Feature: Booking API
  As an API consumer
  I want to manage bookings via the API
  So that guests can reserve rooms

  Background:
    Given the base URL is configured

  @smoke
  Scenario: Get all bookings
    When I request all bookings
    Then the response should be successful
    And the response should be valid JSON
    And the response should be an array
    And the response array should not be empty

  @smoke
  Scenario: Create a new booking
    When I create a booking for "John" "Smith"
    Then the response status code should be 200
    And the response should be valid JSON
    And the response should contain "bookingid"

  Scenario: Get booking by ID
    Given bookings exist in the system
    When I request booking with ID 1
    Then the response should be successful
    And the response should be valid JSON
    And the response should contain "firstname"
    And the response should contain "lastname"
    And the response should contain "bookingdates"

  @auth_required
  Scenario: Delete booking requires authentication
    When I create a booking for "Delete" "Me"
    Then the response status code should be 200
    Given I am not authenticated
    When I delete the created booking
    Then the response status code should be 403

  @auth_required
  Scenario: Delete booking as admin
    Given I am authenticated as admin
    When I create a booking for "Remove" "Test"
    Then the response status code should be 200
    When I delete the created booking
    Then the response status code should be 201

  Scenario: Create booking with complete guest information
    When I create a test booking
    Then the response status code should be 200
    And the response should contain "bookingid"
    And the response field "booking.depositpaid" should not be empty

  @negative
  Scenario: Get non-existent booking
    When I request booking with ID 99999999
    Then the response status code should be 404

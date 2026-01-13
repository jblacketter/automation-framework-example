# Add API Endpoint Skill

## Description
Add support for a new API endpoint with service, steps, and feature file.

## Usage
Use this skill when adding tests for a new API endpoint.

## Workflow

### 1. Understand the Endpoint
Document the endpoint details:
- HTTP method (GET, POST, PUT, DELETE, PATCH)
- Path (e.g., `/booking/{id}`)
- Request body schema (if applicable)
- Response schema
- Authentication requirements
- Example curl command

### 2. Add to Existing or Create New Service

**Add to existing service** (`services/booking_service.py`):
```python
def get_booking_by_name(self, firstname: str, lastname: str):
    """Get bookings filtered by guest name."""
    params = {"firstname": firstname, "lastname": lastname}
    response = self.client.get(self.ENDPOINT, params=params)
    return response, ResponseValidator(response)
```

**Create new service** (`services/new_service.py`):
```python
from core.api_client import APIClient
from core.logger import get_logger
from core.response_validator import ResponseValidator

class NewService:
    """Service for interacting with /api/new endpoint."""

    ENDPOINT = "/new"

    def __init__(self):
        self.client = APIClient()
        self.logger = get_logger(__name__)

    def get_all(self):
        """Get all resources."""
        response = self.client.get(self.ENDPOINT)
        return response, ResponseValidator(response)

    def get_by_id(self, resource_id: int):
        """Get a specific resource by ID."""
        response = self.client.get(f"{self.ENDPOINT}/{resource_id}")
        return response, ResponseValidator(response)

    def create(self, data: dict):
        """Create a new resource."""
        response = self.client.post(self.ENDPOINT, json=data)
        return response, ResponseValidator(response)
```

### 3. Add Step Definitions

In `steps/api_steps.py`:
```python
from services.new_service import NewService

@when('I request all new resources')
def step_get_all_new(context):
    """Get all resources from new endpoint."""
    service = NewService()
    context.response, context.validator = service.get_all()

@when('I create a new resource with name "{name}"')
def step_create_new(context, name):
    """Create a new resource."""
    service = NewService()
    data = {"name": name}
    context.response, context.validator = service.create(data)

    # Track for cleanup
    if context.response.status_code == 201:
        resource_id = context.response.json().get("id")
        if not hasattr(context, "resources_to_cleanup"):
            context.resources_to_cleanup = []
        context.resources_to_cleanup.append(resource_id)
```

### 4. Create Feature File

In `features/api/new_endpoint.feature`:
```gherkin
@api @new
Feature: New Endpoint API
  As an API consumer
  I want to interact with the new endpoint
  So that I can manage resources

  Background:
    Given the API is available

  @smoke
  Scenario: Get all resources
    When I request all new resources
    Then the response status code should be 200
    And the response should be a list

  @regression
  Scenario: Create a new resource
    Given I am authenticated as admin
    When I create a new resource with name "Test Resource"
    Then the response status code should be 201
    And the response should contain "id"
```

### 5. Add Cleanup Hook (if needed)

In `environment.py`, add to `after_scenario`:
```python
# Clean up created resources
if hasattr(context, "resources_to_cleanup"):
    service = NewService()
    for resource_id in context.resources_to_cleanup:
        try:
            service.delete(resource_id)
        except Exception as e:
            logger.warning(f"Failed to cleanup resource {resource_id}: {e}")
```

### 6. Run and Verify
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate

# Dry run to check step matching
behave --dry-run features/api/new_endpoint.feature

# Run the tests
behave features/api/new_endpoint.feature --no-capture
```

## File Checklist
- [ ] `services/new_service.py` - Service class
- [ ] `steps/api_steps.py` - Step definitions
- [ ] `features/api/new_endpoint.feature` - Feature file
- [ ] `environment.py` - Cleanup hooks (if creating resources)

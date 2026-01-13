# Create Test Skill

## Description
Create new test scenarios, step definitions, and page objects.

## Usage
Use this skill when the user wants to add new tests to the framework.

## Guidelines

### Creating a New Feature File

Feature files go in `features/api/` or `features/ui/` depending on test type.

Template:
```gherkin
@TAG @DOMAIN
Feature: Feature Name
  As a [role]
  I want [capability]
  So that [benefit]

  Background:
    Given the base URL is configured

  @smoke
  Scenario: Scenario name
    Given [precondition]
    When [action]
    Then [expected result]
```

### Creating API Step Definitions

Add to `steps/api_steps.py`:

```python
from behave import given, when, then
from services.booking_service import BookingService

@when('I do something with "{param}"')
def step_do_something(context, param):
    """Description of what this step does."""
    service = BookingService()
    context.response, context.validator = service.some_method(param)
```

### Creating UI Step Definitions

Add to `steps/ui_steps.py`:

```python
from behave import given, when, then
from pages.some_page import SomePage

@given("I am on the some page")
def step_on_some_page(context):
    """Navigate to the some page."""
    context.some_page = SomePage(context.page)
    context.some_page.navigate()
```

### Creating a New Page Object

Create new file in `pages/`:

```python
from pages.base_page import BasePage

class NewPage(BasePage):
    # Locators
    ELEMENT = "#element-id"

    @property
    def url_path(self) -> str:
        return "/page-path"

    def do_action(self) -> "NewPage":
        self.click(self.ELEMENT)
        return self
```

### Creating a New Service

Create new file in `services/`:

```python
from core.api_client import APIClient
from core.logger import get_logger
from core.response_validator import ResponseValidator

class NewService:
    ENDPOINT = "/api/endpoint"

    def __init__(self):
        self.client = APIClient()
        self.logger = get_logger(__name__)

    def get_something(self, id: int):
        response = self.client.get(f"{self.ENDPOINT}/{id}")
        return response, ResponseValidator(response)
```

## File Locations
- Feature files: `features/api/` or `features/ui/`
- Step definitions: `steps/`
- Page objects: `pages/`
- Services: `services/`

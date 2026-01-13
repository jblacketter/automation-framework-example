# Add Page Object Skill

## Description
Create a new page object for UI testing following the Page Object Model pattern.

## Usage
Use this skill when adding tests for a new page or UI component.

## Workflow

### 1. Analyze the Page
Open the target page in a browser and identify:
- Page URL path
- Key interactive elements (buttons, inputs, links)
- Key content elements (headings, text, images)
- Dynamic elements that need waits
- Forms and their fields

### 2. Create the Page Object

Create `pages/new_page.py`:
```python
"""Page object for the New Page."""

from pages.base_page import BasePage


class NewPage(BasePage):
    """Page object for interacting with the new page."""

    # ==================== Locators ====================
    # Use descriptive constant names in SCREAMING_SNAKE_CASE

    # Navigation
    NAV_LINK = "[data-testid='nav-new']"

    # Form elements
    NAME_INPUT = "#name"
    EMAIL_INPUT = "#email"
    SUBMIT_BUTTON = "button[type='submit']"

    # Content elements
    PAGE_TITLE = "h1"
    SUCCESS_MESSAGE = ".alert-success"
    ERROR_MESSAGE = ".alert-danger"

    # ==================== Properties ====================

    @property
    def url_path(self) -> str:
        """Return the URL path for this page."""
        return "/new-page"

    # ==================== Actions ====================
    # Methods that perform actions return self for chaining

    def fill_form(self, name: str, email: str) -> "NewPage":
        """Fill out the form with provided values."""
        self.fill(self.NAME_INPUT, name)
        self.fill(self.EMAIL_INPUT, email)
        return self

    def submit_form(self) -> "NewPage":
        """Click the submit button."""
        self.click(self.SUBMIT_BUTTON)
        return self

    def complete_form(self, name: str, email: str) -> "NewPage":
        """Fill and submit the form in one action."""
        return self.fill_form(name, email).submit_form()

    # ==================== Assertions ====================
    # Methods that verify state, return bool or raise

    def is_success_message_displayed(self) -> bool:
        """Check if success message is visible."""
        return self.is_visible(self.SUCCESS_MESSAGE)

    def get_success_message(self) -> str:
        """Get the text of the success message."""
        return self.get_text(self.SUCCESS_MESSAGE)

    def get_page_title(self) -> str:
        """Get the main page title text."""
        return self.get_text(self.PAGE_TITLE)

    # ==================== Waits ====================
    # Methods that wait for specific conditions

    def wait_for_form_load(self) -> "NewPage":
        """Wait for form to be ready."""
        self.wait_for_element(self.NAME_INPUT)
        self.wait_for_element(self.SUBMIT_BUTTON)
        return self

    def wait_for_submission_result(self) -> "NewPage":
        """Wait for either success or error message."""
        self.page.wait_for_selector(
            f"{self.SUCCESS_MESSAGE}, {self.ERROR_MESSAGE}",
            timeout=10000
        )
        return self
```

### 3. Add Step Definitions

In `steps/ui_steps.py`:
```python
from pages.new_page import NewPage

@given("I am on the new page")
def step_on_new_page(context):
    """Navigate to the new page."""
    context.new_page = NewPage(context.page)
    context.new_page.navigate()

@when('I fill the form with name "{name}" and email "{email}"')
def step_fill_form(context, name, email):
    """Fill the form with provided values."""
    context.new_page.fill_form(name, email)

@when("I submit the form")
def step_submit_form(context):
    """Submit the form."""
    context.new_page.submit_form()

@then("I should see a success message")
def step_see_success(context):
    """Verify success message is displayed."""
    assert context.new_page.is_success_message_displayed(), \
        "Success message not displayed"
```

### 4. Create Feature File

In `features/ui/new_page.feature`:
```gherkin
@ui @new-page
Feature: New Page
  As a user
  I want to interact with the new page
  So that I can accomplish my goal

  Background:
    Given the browser is open
    And I am on the new page

  @smoke
  Scenario: Page loads successfully
    Then the page title should be "New Page"

  @regression
  Scenario: Submit form successfully
    When I fill the form with name "John" and email "john@example.com"
    And I submit the form
    Then I should see a success message
```

### 5. Run and Verify
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate

# Run in headed mode to watch
HEADLESS=false behave features/ui/new_page.feature --no-capture
```

## Best Practices

### Selector Strategy
1. Prefer `data-testid` attributes (ask devs to add them)
2. Use semantic selectors (`role=`, `text=`)
3. Avoid brittle selectors (nth-child, complex CSS paths)

### Method Naming
- Actions: verb phrases (`click_submit`, `fill_form`, `navigate`)
- Queries: `get_*` or `is_*` (`get_title`, `is_visible`)
- Waits: `wait_for_*` (`wait_for_load`, `wait_for_element`)

### Return Types
- Actions return `self` for chaining
- Queries return the value (str, bool, list)
- Waits return `self` for chaining

## File Checklist
- [ ] `pages/new_page.py` - Page object class
- [ ] `steps/ui_steps.py` - Step definitions
- [ ] `features/ui/new_page.feature` - Feature file

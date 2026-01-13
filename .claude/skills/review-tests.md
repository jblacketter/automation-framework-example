# Review Tests Skill

## Description
Review test code for quality, maintainability, and best practices.

## Usage
Use this skill when reviewing PRs or auditing test quality.

## Review Checklist

### Feature Files

**Structure:**
- [ ] Feature has clear description (As a... I want... So that...)
- [ ] Scenarios have descriptive names
- [ ] Background used for common preconditions
- [ ] Appropriate tags (@smoke, @regression, @wip, @api, @ui)

**Gherkin Quality:**
- [ ] Steps are written in domain language, not implementation
- [ ] Steps are reusable across scenarios
- [ ] Given/When/Then used correctly (setup/action/assertion)
- [ ] No implementation details in feature files

```gherkin
# Bad - implementation details
When I click the button with id "submit-btn"
Then I should see element ".success-message"

# Good - domain language
When I submit the booking request
Then I should see a confirmation message
```

### Step Definitions

**Organization:**
- [ ] Steps in appropriate file (api_steps.py, ui_steps.py, common_steps.py)
- [ ] No duplicate steps across files
- [ ] Shared steps use @step decorator
- [ ] Clear docstrings explaining what each step does

**Implementation:**
- [ ] Steps delegate to services/pages (not direct API/browser calls)
- [ ] Context used appropriately for sharing state
- [ ] Proper error handling with meaningful messages

```python
# Bad - implementation in step
@when('I create a booking')
def step_create_booking(context):
    response = requests.post(f"{BASE_URL}/booking", json={...})
    context.response = response

# Good - delegate to service
@when('I create a booking')
def step_create_booking(context):
    service = BookingService()
    context.response, context.validator = service.create_booking(context.booking_data)
```

### Page Objects

**Structure:**
- [ ] Extends BasePage
- [ ] Locators as class constants (SCREAMING_SNAKE_CASE)
- [ ] url_path property defined
- [ ] Clear separation: locators → actions → queries → waits

**Quality:**
- [ ] Locators are stable (data-testid, id, name preferred)
- [ ] No hardcoded waits (use explicit waits)
- [ ] Actions return self for chaining
- [ ] Meaningful method names

```python
# Bad - hardcoded wait, poor locator
def login(self, user, pwd):
    time.sleep(2)
    self.page.fill("body > div > form > input:nth-child(1)", user)

# Good - explicit wait, stable locator
def login(self, username: str, password: str) -> "LoginPage":
    self.wait_for_element(self.USERNAME_INPUT)
    self.fill(self.USERNAME_INPUT, username)
    return self
```

### Services

**Structure:**
- [ ] Single responsibility (one domain per service)
- [ ] Returns (Response, ResponseValidator) tuple
- [ ] Uses APIClient singleton
- [ ] Proper logging

**Quality:**
- [ ] Endpoints as class constants
- [ ] Methods have type hints
- [ ] Docstrings for public methods
- [ ] No business logic in services (just API calls)

### Test Data

- [ ] No hardcoded sensitive data (use .env)
- [ ] Test data is realistic but obviously fake
- [ ] Resources created in tests are cleaned up
- [ ] Tests are isolated (don't depend on other tests)

## Commands

### Check for Common Issues
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate

# Check for hardcoded sleeps
grep -r "time.sleep" pages/ steps/

# Check for duplicate steps
grep -r "@given\|@when\|@then\|@step" steps/ | sort | uniq -d

# Check for missing type hints
grep -r "def " services/ pages/ | grep -v ": "

# Dry run all features
behave --dry-run
```

### Run Quality Checks
```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy core/ services/ pages/

# Linting
flake8 core/ services/ pages/ steps/
```

## Anti-Patterns to Flag

1. **Flaky tests** - Tests that pass/fail inconsistently
2. **Test interdependence** - Tests that must run in order
3. **Hardcoded data** - Credentials, IDs, dates in code
4. **God objects** - Pages/services doing too much
5. **Missing cleanup** - Created resources not deleted
6. **Implementation in features** - Selectors/URLs in .feature files
7. **Excessive mocking** - Tests that don't test real behavior

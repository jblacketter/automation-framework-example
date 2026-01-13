# Fix Selectors Skill

## Description
Update UI selectors when the target application changes its DOM structure.

## Usage
Use this skill when UI tests fail due to element not found errors, typically after the target site is updated.

## Workflow

### 1. Identify the Failing Selector
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
HEADLESS=false SLOW_MO=1000 behave features/ui/FILE.feature --no-capture
```

Watch the browser to see where it fails.

### 2. Inspect the Current DOM
Open the target URL in a browser and use DevTools (F12) to find the correct selector.

**Selector Priority (most to least reliable):**
1. `data-testid` attributes: `[data-testid="login-button"]`
2. Unique IDs: `#submit-btn`
3. Semantic roles: `role=button[name="Submit"]`
4. Unique class combinations: `.login-form .submit`
5. Text content: `text=Login`
6. CSS path (last resort): `form > div:nth-child(2) > button`

### 3. Update the Page Object
Page objects are in `pages/`. Each has locators defined as class constants:

```python
class AdminPage(BasePage):
    # Locators - update these
    USERNAME_INPUT = "#username"  # Old selector
    USERNAME_INPUT = "[data-testid='username']"  # New selector
```

### 4. Test the Fix
```bash
# Run just the affected scenario
behave features/ui/admin.feature:LINE_NUMBER --no-capture

# Run in headed mode to verify
HEADLESS=false behave features/ui/admin.feature --no-capture
```

### 5. Consider Adding Waits
If elements load dynamically:

```python
def login(self, username: str, password: str) -> "AdminPage":
    self.wait_for_element(self.USERNAME_INPUT)  # Add explicit wait
    self.fill(self.USERNAME_INPUT, username)
    return self
```

## Common Patterns

### Finding Elements by Text
```python
LOGIN_BUTTON = "text=Log in"
LOGIN_BUTTON = "button:has-text('Log in')"
```

### Finding Elements by Role
```python
SUBMIT_BUTTON = "role=button[name='Submit']"
NAV_LINK = "role=link[name='Home']"
```

### Finding Elements in Containers
```python
FORM_SUBMIT = ".login-form >> button[type='submit']"
MODAL_CLOSE = "[data-testid='modal'] >> .close-btn"
```

### Handling Dynamic IDs
```python
# Bad - ID changes on each load
USERNAME = "#username_abc123"

# Good - use stable attributes
USERNAME = "[name='username']"
USERNAME = "[data-testid='username-input']"
```

## Files to Update
- `pages/admin_page.py` - Admin panel selectors
- `pages/home_page.py` - Home page selectors
- `pages/booking_page.py` - Booking flow selectors

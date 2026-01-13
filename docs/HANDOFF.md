# Framework Implementation Handoff

**Date:** January 12, 2026
**Project:** automation-framework-example
**Status:** Core framework complete, tests passing

---

## Summary

We built a production-ready BDD test automation framework from scratch using **Python, Behave, and Playwright**. The framework demonstrates best practices for both API and UI testing against publicly available test applications.

---

## What Was Built

### Core Framework Components (`core/`)

| File | Purpose | Pattern |
|------|---------|---------|
| `config.py` | Environment-based configuration | Singleton |
| `api_client.py` | HTTP client with session pooling, token management | Singleton |
| `browser_factory.py` | Playwright browser lifecycle management | Singleton |
| `logger.py` | Structured logging with sensitive data masking | Module-level |
| `response_validator.py` | Fluent API response assertions | Builder/Fluent |

### Service Layer (`services/`)

| File | Purpose |
|------|---------|
| `auth_service.py` | Authentication (login, token validation) |
| `booking_service.py` | Booking CRUD operations |
| `room_service.py` | Room operations (extensible) |

### Page Objects (`pages/`)

| File | Purpose |
|------|---------|
| `base_page.py` | Abstract base class with common Playwright methods |
| `home_page.py` | Hotel landing page interactions |
| `admin_page.py` | Admin panel login and management |
| `booking_page.py` | Booking calendar and form |

### Test Scenarios (`features/`)

**API Tests:**
- `auth.feature` - Authentication (login, token validation)
- `bookings.feature` - Booking CRUD operations

**UI Tests:**
- `home.feature` - Home page, contact form
- `admin.feature` - Admin login (WIP - selectors need updating)
- `booking.feature` - Booking flow (WIP)

### Step Definitions (`steps/`)

- `common_steps.py` - Shared auth and validation steps
- `api_steps.py` - API-specific steps
- `ui_steps.py` - UI-specific steps

---

## Target Applications

We chose two complementary public applications:

### API Testing: Restful Booker
- **URL:** https://restful-booker.herokuapp.com
- **Why:** Simple, well-documented REST API with CRUD operations
- **Endpoints used:**
  - `POST /auth` - Get auth token
  - `GET /booking` - List all bookings
  - `GET /booking/:id` - Get booking details
  - `POST /booking` - Create booking
  - `PUT /booking/:id` - Update booking (requires auth)
  - `DELETE /booking/:id` - Delete booking (requires auth)
- **Credentials:** admin / password123

### UI Testing: Restful Booker Platform
- **URL:** https://automationintesting.online
- **Why:** Full hotel booking UI with rooms, calendar, contact forms
- **Note:** Site was recently rebuilt with Next.js; some admin selectors need updating

---

## Test Results

```
Smoke Tests: 4 passed, 0 failed
├── API Auth: Login successful ✓
├── API Bookings: Get all bookings ✓
├── API Bookings: Create booking ✓
└── UI Home: Display hotel info ✓
```

---

## Key Design Decisions

### 1. Singleton Pattern for Core Components
- **APIClient:** Single session for connection pooling, shared token state
- **Config:** Single source of truth for environment variables
- **BrowserFactory:** Efficient browser reuse across scenarios

### 2. Service Layer Architecture
- Separates business logic from step definitions
- Services return `(Response, ResponseValidator)` tuples
- Makes tests readable and maintainable

### 3. Page Object Model
- Abstract `BasePage` with common methods
- Each page encapsulates its selectors and interactions
- Fluent interface (methods return `self` for chaining)

### 4. Environment Hooks
- `before_feature`: Initialize browser for UI tests
- `before_scenario`: Reset API client state, create fresh page
- `after_scenario`: Cleanup test data, capture screenshots on failure
- `after_feature`: Close browser

### 5. Test Data Cleanup
- Track created resources in `context.bookings_to_cleanup`
- Automatically delete in `after_scenario` hook
- Ensures test isolation

---

## File Structure

```
automation-framework-example/
├── .claude/                    # Claude Code skills
│   ├── settings.json
│   └── skills/
│       ├── run-tests.md
│       ├── setup-environment.md
│       ├── create-test.md
│       └── debug-test.md
├── .github/workflows/
│   └── tests.yml              # GitHub Actions CI/CD
├── core/                       # Framework core (singletons)
│   ├── api_client.py
│   ├── browser_factory.py
│   ├── config.py
│   ├── logger.py
│   └── response_validator.py
├── docs/                       # Documentation with Mermaid diagrams
│   ├── architecture.md
│   ├── api-flow.md
│   ├── ui-flow.md
│   └── HANDOFF.md             # This file
├── features/
│   ├── api/
│   │   ├── auth.feature
│   │   └── bookings.feature
│   └── ui/
│       ├── home.feature
│       ├── admin.feature
│       └── booking.feature
├── pages/                      # Page Object Model
│   ├── base_page.py
│   ├── home_page.py
│   ├── admin_page.py
│   └── booking_page.py
├── services/                   # API service layer
│   ├── auth_service.py
│   ├── booking_service.py
│   └── room_service.py
├── steps/                      # Behave step definitions
│   ├── common_steps.py
│   ├── api_steps.py
│   └── ui_steps.py
├── .env.example               # Environment template
├── behave.ini                 # Behave configuration
├── environment.py             # Behave hooks
├── pyproject.toml             # Project metadata
├── README.md                  # Quick start guide
└── requirements.txt           # Python dependencies
```

---

## Configuration

**.env file:**
```
BASE_URL=https://automationintesting.online
API_BASE_URL=https://restful-booker.herokuapp.com
BROWSER=chromium
HEADLESS=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password123
SCREENSHOT_ON_FAILURE=true
```

---

## Running Tests

```bash
# Setup
cd ~/projects/automation-framework-example
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Run smoke tests
behave --tags="@smoke"

# Run API tests only
behave features/api/

# Run UI tests only
behave features/ui/

# Run in headed mode (see browser)
HEADLESS=false behave features/ui/
```

---

## What's Left / Known Issues

### 1. Admin Page Selectors (WIP)
The automationintesting.online site was rebuilt with Next.js. The admin login selectors in `pages/admin_page.py` need updating to match the current DOM structure. Tagged with `@wip` to skip in CI.

### 2. Booking Flow (WIP)
The booking calendar interaction in `pages/booking_page.py` needs refinement for the current site implementation. The drag-to-select date range logic may need adjustment. Tagged with `@wip`.

### 3. UI vs API Target Mismatch
The UI site (automationintesting.online) and API (restful-booker.herokuapp.com) are separate applications. The API is simpler and more stable for testing. Consider using only the API for a cleaner demo, or finding a site with both UI and API in sync.

### 4. Contact Form Test
The contact form submission test may be flaky depending on site state. The success message selector might need adjustment.

### 5. Additional Tests to Add
- Booking update/delete via API
- Booking filtering by name/date
- Partial update (PATCH) scenarios
- Negative test cases for validation errors
- End-to-end booking flow (UI + API verification)

---

## Documentation

The `/docs` folder contains Mermaid diagrams for:

- **architecture.md** - Component relationships, class diagrams, directory structure
- **api-flow.md** - API test execution, request lifecycle, error handling
- **ui-flow.md** - Browser lifecycle, page object flow, screenshot capture

These render as visual diagrams in GitHub and compatible Markdown viewers.

---

## Next Steps

1. Update admin page selectors for current site
2. Complete booking flow implementation
3. Add more test scenarios
4. Set up GitHub repo and enable Actions
5. Consider adding Allure reporting for richer test reports

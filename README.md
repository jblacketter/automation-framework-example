# BDD Test Automation Framework

A modern, production-ready test automation framework demonstrating best practices for both **API** and **UI** testing using Python, Behave (BDD), and Playwright.

## Why This Framework?

This framework showcases enterprise-grade test automation patterns I've developed across multiple projects. It's designed to be:

**Maintainable** - Clear separation of concerns with Page Objects, Services, and Steps layers. When selectors change, you update one file. When APIs change, you update one service.

**Scalable** - Singleton patterns for shared resources (browser, API client, config) prevent memory leaks and connection issues as test suites grow.

**Readable** - BDD scenarios written in plain English. Non-technical stakeholders can read and validate test coverage.

**Debuggable** - Structured logging, screenshot capture on failure, and headed browser mode for step-through debugging.

**CI/CD Ready** - GitHub Actions workflow included. Tests run on every push with proper parallelization support.

### Design Decisions

| Decision | Why |
|----------|-----|
| **Singleton APIClient** | Connection pooling, shared auth tokens, consistent logging |
| **Service Layer** | Business logic separate from step definitions; services return `(Response, Validator)` tuples for fluent assertions |
| **Abstract BasePage** | Common Playwright methods (click, fill, wait) in one place; pages focus on their specific locators and actions |
| **Environment Hooks** | Automatic cleanup, screenshot capture, browser lifecycle management |
| **Fluent ResponseValidator** | Chain assertions naturally: `validator.status(200).has_field("id").field_equals("name", "Test")` |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| BDD Framework | Behave |
| UI Automation | Playwright |
| API Testing | Requests |
| Assertions | AssertPy |
| CI/CD | GitHub Actions |

## Target Applications

This framework demonstrates testing against two publicly available applications. They are separate systems (not the same backend), chosen specifically because they're free, publicly accessible, and showcase different testing patterns.

### API Testing: Restful Booker API
- **URL**: [restful-booker.herokuapp.com](https://restful-booker.herokuapp.com)
- **Features**: Authentication, Booking CRUD operations
- **Why**: Simple REST API with full CRUD, token-based auth, well-documented
- **Credentials**: `admin` / `password123`

### UI Testing: Restful Booker Platform
- **URL**: [automationintesting.online](https://automationintesting.online)
- **Features**: Hotel landing page, room listings, booking calendar, contact form
- **Why**: Modern React/Next.js app with realistic booking flows, dynamic content

> **Note**: These are independent test targets. API tests verify CRUD operations against the Restful Booker API. UI tests verify user journeys on the Booking Platform. In a real project, you'd typically test the same application's UI and API together for end-to-end verification.

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/jblacketter/automation-framework-example.git
cd automation-framework-example

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
cp .env.example .env
```

### Running Tests

```bash
# Run all smoke tests
behave --tags="@smoke"

# Run API tests only
behave features/api/

# Run UI tests only
behave features/ui/

# Run with HTML report
behave --format=html --outfile=reports/report.html

# Run in headed mode (see browser)
HEADLESS=false behave features/ui/
```

## Project Structure

```
automation-framework-example/
├── .claude/                 # Claude Code AI assistant configuration
│   ├── settings.json        # Project settings
│   └── skills/              # Development skills (run-tests, debug, etc.)
├── core/                    # Core framework components
│   ├── api_client.py        # HTTP client (singleton)
│   ├── browser_factory.py   # Playwright browser management
│   ├── config.py            # Configuration management
│   ├── logger.py            # Logging with data masking
│   └── response_validator.py # API response assertions
├── services/                # API service layer
│   ├── auth_service.py      # Authentication
│   ├── booking_service.py   # Booking operations
│   └── room_service.py      # Room operations
├── pages/                   # Page Object Model
│   ├── base_page.py         # Base page class
│   ├── home_page.py         # Home page
│   ├── admin_page.py        # Admin panel
│   └── booking_page.py      # Booking flow
├── features/                # BDD feature files
│   ├── api/                 # API test scenarios
│   └── ui/                  # UI test scenarios
├── steps/                   # Step definitions
│   ├── common_steps.py      # Shared steps
│   ├── api_steps.py         # API steps
│   └── ui_steps.py          # UI steps
├── docs/                    # Documentation with Mermaid diagrams
│   ├── architecture.md      # Architecture diagrams
│   ├── api-flow.md          # API flow diagrams
│   ├── ui-flow.md           # UI flow diagrams
│   └── HANDOFF.md           # Implementation handoff document
├── environment.py           # Behave hooks
├── behave.ini               # Behave configuration
├── requirements.txt         # Dependencies
└── .github/workflows/       # CI/CD pipeline
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | UI base URL | `https://automationintesting.online` |
| `API_BASE_URL` | API base URL | `https://restful-booker.herokuapp.com` |
| `BROWSER` | Browser type | `chromium` |
| `HEADLESS` | Headless mode | `true` |
| `SLOW_MO` | Slow down browser actions (ms) | `0` |
| `DEFAULT_TIMEOUT` | Default timeout (ms) | `30000` |
| `NAVIGATION_TIMEOUT` | Navigation timeout (ms) | `60000` |
| `VIEWPORT_WIDTH` | Browser viewport width | `1920` |
| `VIEWPORT_HEIGHT` | Browser viewport height | `1080` |
| `ADMIN_USERNAME` | Admin user | `admin` |
| `ADMIN_PASSWORD` | Admin pass | `password123` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_API_REQUESTS` | Log API requests | `true` |
| `LOG_API_RESPONSES` | Log API responses | `true` |
| `SCREENSHOT_ON_FAILURE` | Capture screenshot on failure | `true` |
| `SCREENSHOT_DIR` | Screenshot output directory | `reports/screenshots` |

## Documentation

Detailed documentation with architecture diagrams available in the `/docs` folder:

- [Architecture Overview](docs/architecture.md) - Framework design and patterns
- [API Testing Flow](docs/api-flow.md) - API test execution flow
- [UI Testing Flow](docs/ui-flow.md) - UI test execution flow

## Key Features

- **Singleton Patterns** - Efficient resource management
- **Page Object Model** - Maintainable UI tests
- **Service Layer** - Clean API test architecture
- **Fluent Assertions** - Readable test validations
- **Auto Cleanup** - Test data lifecycle management
- **Screenshot on Failure** - Easy debugging
- **CI/CD Ready** - GitHub Actions included

## License

MIT License

## Author

Gregory Blacketter

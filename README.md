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

### Why Behave Over pytest-bdd?

Both Behave and pytest-bdd are excellent choices for BDD testing in Python. Here's why this framework uses Behave:

| Aspect | Behave | pytest-bdd |
|--------|--------|------------|
| **Learning Curve** | Lower - standalone tool with clear conventions | Requires pytest knowledge first |
| **Gherkin Purity** | Native Gherkin parsing, closer to Cucumber | Gherkin via decorators, more Pythonic |
| **Ecosystem** | Rich plugin ecosystem (Allure, JUnit, HTML) | Leverages pytest's vast plugin ecosystem |
| **Step Reuse** | Steps are global by default | Explicit fixtures, more control |
| **Parallel Execution** | Via behave-parallel or custom runners | Native pytest-xdist support |

**This framework chose Behave because:**
1. **Readability** - Feature files and step definitions stay close to pure Gherkin/Cucumber patterns, making it easier for non-Python teams to understand
2. **Environment Hooks** - Built-in hooks (`before_feature`, `after_scenario`, etc.) provide clean lifecycle management
3. **Context Object** - Behave's context object is a natural place for sharing state between steps

**When to choose pytest-bdd instead:**
- Your team already uses pytest extensively
- You need pytest fixtures for complex dependency injection
- You want native pytest-xdist parallel execution
- You prefer decorator-based step definitions

Both frameworks can achieve the same test coverage - the choice comes down to team preference and existing tooling.

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
├── factories/               # Test data builders (Builder pattern)
│   ├── booking_builder.py   # Booking data builder
│   ├── guest_builder.py     # Guest data builder
│   └── room_builder.py      # Room data builder
├── services/                # API service layer
│   ├── auth_service.py      # Authentication
│   ├── booking_service.py   # Booking operations
│   └── room_service.py      # Room operations
├── pages/                   # Page Object Model
│   ├── base_page.py         # Base page class (with retry helpers)
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
- **Retry Helpers** - Built-in retry logic for flaky UI interactions
- **Data Builders** - Flexible test data generation with builder pattern

## Parallel Execution

The current singleton pattern is optimized for **sequential test execution** (one scenario at a time). This is the default for Behave and works well for most CI/CD pipelines.

### Current Architecture

```
APIClient (Singleton)     BrowserFactory (Singleton)
       │                           │
       └────── per-scenario ───────┘
               isolation via:
               - Token clearing
               - Fresh browser context
               - New page instance
```

### For True Parallel Execution

If you need to run scenarios in parallel (e.g., using `behave-parallel` or custom threading), the singletons need modification. Here's how:

**Option 1: Thread-Local Storage (Recommended)**

```python
import threading
from typing import Optional

class ThreadLocalAPIClient:
    """Thread-safe API client using thread-local storage."""

    _local = threading.local()

    @classmethod
    def get_instance(cls) -> "APIClient":
        if not hasattr(cls._local, "instance"):
            cls._local.instance = APIClient.__new__(APIClient)
            cls._local.instance._initialized = False
            cls._local.instance.__init__()
        return cls._local.instance

    @classmethod
    def reset(cls) -> None:
        if hasattr(cls._local, "instance"):
            cls._local.instance.session.close()
            del cls._local.instance
```

**Option 2: Context Manager Pattern**

```python
from contextlib import contextmanager

@contextmanager
def isolated_api_client():
    """Create an isolated API client for a test scope."""
    client = APIClient.__new__(APIClient)
    client._initialized = False
    client.__init__()
    try:
        yield client
    finally:
        client.session.close()
```

**Option 3: Dependency Injection**

```python
# In environment.py
def before_scenario(context, scenario):
    # Create fresh instances per scenario
    context.api_client = create_new_api_client()
    context.browser = create_new_browser_context()

# In step definitions
@when("I make an API call")
def step_api_call(context):
    context.api_client.get("/endpoint")  # Use injected client
```

### Parallel Execution with behave-parallel

```bash
# Install
pip install behave-parallel

# Run scenarios in parallel (4 workers)
behave-parallel --processes 4 features/

# Run features in parallel (safer for UI tests)
behave-parallel --processes 4 --parallel-element feature features/
```

**Note:** For UI tests, running features in parallel (not scenarios) is safer since browser lifecycle is per-feature.

## License

MIT License

## Author

Gregory Blacketter

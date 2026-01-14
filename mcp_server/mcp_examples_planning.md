# MCP Server Suite: Test Intelligence Tools


## Overview

Project-specific MCP servers for this repo that demonstrate distinct MCP patterns:

1. **A1. Failure Analyzer** - Artifact retrieval, vision (screenshots), code tracing
2. **A2. Data Factory** - Schema discovery, data generation, introspection
3. **A4. API Client** - Safe service execution, method discovery

**Design Goals:**
- Useful examples with safety rails (timeouts, path validation, bounded output)
- Fit this repository's structure (no reusable package or PyPI distribution)
- Clear demos for Claude Desktop/Code workflows

---

## Project Scope & Assumptions

- Project root is this repository; use `features/`, `steps/`, `pages/`, `services/`, `reports/`.
- Screenshots live under `reports/screenshots/` and results under `reports/results_run_*.json`.
- These servers are examples, not production-hardened tools.

---

## Server 1: Failure Analyzer

### Purpose

When a test fails, developers waste time:
1. Reading cryptic error messages
2. Cross-referencing logs, screenshots, and code
3. Figuring out if it's a test bug, app bug, or flaky test

The Failure Analyzer does this automatically.

### Tools

| Tool | Description |
|------|-------------|
| `get_failure_context` | Gather all artifacts for a failed scenario |
| `analyze_failure` | Analyze failure and suggest root cause |
| `get_screenshot` | Return screenshot as base64 for visual analysis |
| `find_similar_failures` | Find past failures with similar patterns |
| `suggest_fix` | Generate a code fix suggestion |

### Tool Specifications

#### `get_failure_context`

```python
@mcp.tool()
def get_failure_context(
    scenario_name: Optional[str] = None,
    scenario_id: Optional[str] = None,  # UUID from results for non-unique names
    run_id: Optional[str] = None,        # Defaults to latest run
    feature_file: Optional[str] = None,  # Disambiguate same-named scenarios
) -> dict[str, Any]:
    """
    Gather all context needed to analyze a failure.

    Identification priority:
    1. scenario_id (UUID) - most precise, from Behave JSON results
    2. scenario_name + feature_file - for disambiguation
    3. scenario_name alone - matches first found

    Size limits (configurable):
    - Logs: max_log_bytes (default 1MB), truncated with marker
    - Screenshots: max_screenshot_bytes (default 5MB)

    Returns:
        context_id: Unique ID for this context (use to avoid recomputation)
        scenario: Scenario name, feature file, line, tags, id
        error: Error message and full stack trace
        failed_step: The step that failed
        step_definition: Source code of the step definition
        related_code: Page/service code involved
        logs: Relevant log lines (truncated if over limit)
        logs_truncated: bool - whether logs were truncated
        screenshot_path: Path to failure screenshot (if exists)
        previous_steps: Steps that passed before failure
        environment: Browser, viewport, base URL, etc.
        cached: bool - whether this was served from cache
    """
```

**Request:**
- `scenario_id`: Preferred identifier when available
- `scenario_name`: Scenario name (optional)
- `feature_file`: Feature file to disambiguate (optional)
- `run_id`: Specific run ID (optional)

**Response shape:**
```json
{
  "context_id": "ctx_20260113_101532_admin_login",
  "scenario": {
    "id": "abc123-def456",
    "name": "Successful admin login",
    "feature": "features/ui/admin.feature",
    "line": 11,
    "tags": ["@login", "@wip"]
  },
  "error": {
    "message": "TimeoutError: Timeout 30000ms exceeded waiting for selector '.login-btn'",
    "stack_trace": "...",
    "stack_trace_truncated": false
  },
  "failed_step": {
    "keyword": "When",
    "text": "I login as admin",
    "line": 13
  },
  "step_definition": {
    "file": "steps/ui_steps.py",
    "line": 45,
    "function": "step_login_as_admin"
  },
  "related_code": [
    {"file": "pages/admin_page.py", "class": "AdminPage", "method": "login"}
  ],
  "logs": ["..."],
  "logs_truncated": false,
  "screenshot_path": "reports/screenshots/failed_successful_admin_login.png",
  "environment": {"browser": "chromium", "headless": true},
  "cached": false
}
```

**Edge cases:**
- If results are missing or invalid, return `{ "error": "No results found" }`.
- If the scenario cannot be located, return `{ "error": "Scenario not found" }`.
- If a screenshot is missing, return `screenshot_path: null` with a warning.
- If logs are too large, truncate and set `logs_truncated: true`.

**Example output:**
```json
{
  "context_id": "ctx_20260113_101532_admin_login",
  "scenario": {
    "id": "abc123-def456",
    "name": "Successful admin login",
    "feature": "features/ui/admin.feature",
    "line": 11,
    "tags": ["@login", "@wip"]
  },
  "error": {
    "message": "TimeoutError: Timeout 30000ms exceeded waiting for selector '.login-btn'",
    "stack_trace": "...",
    "stack_trace_truncated": false
  },
  "failed_step": {
    "keyword": "When",
    "text": "I login as admin",
    "line": 13
  },
  "step_definition": {
    "file": "steps/ui_steps.py",
    "line": 45,
    "function": "step_login_as_admin",
    "source": "def step_login_as_admin(context):\n    context.admin_page.login(...)..."
  },
  "related_code": [
    {
      "file": "pages/admin_page.py",
      "class": "AdminPage",
      "method": "login",
      "source": "def login(self, username, password):\n    self.click('.login-btn')..."
    }
  ],
  "logs": [
    "2026-01-13 10:15:32 | INFO | Navigating to /admin",
    "2026-01-13 10:15:33 | DEBUG | Waiting for selector .login-btn",
    "2026-01-13 10:16:03 | ERROR | Timeout waiting for .login-btn"
  ],
  "logs_truncated": false,
  "screenshot_path": "reports/screenshots/failed_successful_admin_login.png",
  "previous_steps": [
    {"keyword": "Given", "text": "I am on the admin page", "status": "passed"}
  ],
  "environment": {
    "browser": "chromium",
    "headless": true,
    "viewport": "1920x1080",
    "base_url": "https://automationintesting.online"
  },
  "cached": false
}
```

#### `analyze_failure`

```python
@mcp.tool()
def analyze_failure(
    # Option 1: Let the tool fetch context
    scenario_name: Optional[str] = None,
    scenario_id: Optional[str] = None,
    run_id: Optional[str] = None,

    # Option 2: Pass pre-fetched context (avoids recomputation)
    context_id: Optional[str] = None,  # From previous get_failure_context call
    context: Optional[dict] = None,    # Full context dict (for chaining)

    include_screenshot: bool = True,
) -> dict[str, Any]:
    """
    Analyze a failure and provide diagnosis.

    Context resolution:
    1. If context_id provided, load from cache
    2. If context dict provided, use directly
    3. Otherwise, fetch via get_failure_context

    Screenshot handling:
    - Returns base64 if include_screenshot=True and under size limit
    - Returns path only if over limit (with size info)

    Returns:
        context_id: Reference for subsequent calls
        context: Full failure context
        screenshot_base64: Base64-encoded screenshot (if under limit)
        screenshot_too_large: bool - if screenshot exceeded limit
        analysis: Structured analysis with:
            - likely_cause: Most probable reason for failure
            - category: "selector_changed" | "timing_issue" | "app_bug" | "test_bug" | "environment"
            - confidence: 0.0-1.0
            - evidence: Supporting evidence for diagnosis
        suggestions: List of suggested fixes
    """
```

**Request:**
- `scenario_name` or `scenario_id`, or a cached `context_id`/`context`
- `run_id`: Optional run to target
- `include_screenshot`: Include base64 if under size limit

**Response shape:**
```json
{
  "context_id": "ctx_20260113_101532_admin_login",
  "analysis": {
    "likely_cause": "Selector '.login-btn' no longer exists",
    "category": "selector_changed",
    "confidence": 0.85,
    "evidence": ["Timeout waiting for selector '.login-btn'"]
  },
  "suggestions": [
    {
      "type": "code_change",
      "description": "Update selector in AdminPage.login()",
      "file": "pages/admin_page.py",
      "line": 52,
      "suggested": "self.click('button[type=submit]')",
      "confidence": 0.8
    }
  ],
  "screenshot_base64": "iVBORw0KGgo..."
}
```

**Edge cases:**
- If no context can be resolved, return `{ "error": "Context not found" }`.
- If the screenshot exceeds size limits, return `screenshot_base64: null` and `screenshot_too_large: true`.
- If analysis fails, return `{ "error": "Analysis failed" }` with the `context_id` when possible.

**Example output:**
```json
{
  "context": { "..." },
  "screenshot_base64": "iVBORw0KGgo...",
  "analysis": {
    "likely_cause": "The login button selector '.login-btn' no longer exists on the page",
    "category": "selector_changed",
    "confidence": 0.85,
    "evidence": [
      "Timeout waiting for selector '.login-btn'",
      "Screenshot shows login form is present but button has different class",
      "Last successful run was 3 days ago"
    ]
  },
  "suggestions": [
    {
      "type": "code_change",
      "description": "Update selector in AdminPage.login()",
      "file": "pages/admin_page.py",
      "line": 52,
      "current": "self.click('.login-btn')",
      "suggested": "self.click('button[type=submit]')",
      "confidence": 0.8
    },
    {
      "type": "investigation",
      "description": "Check if login form was redesigned recently"
    }
  ]
}
```

#### `get_screenshot`

```python
@mcp.tool()
def get_screenshot(
    scenario_name: Optional[str] = None,
    screenshot_path: Optional[str] = None,
    run_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Get a screenshot for visual analysis.

    Args:
        scenario_name: Find screenshot for this scenario
        screenshot_path: Direct path to screenshot
        run_id: Specific test run

    Returns:
        path: Full path to screenshot
        base64: Base64-encoded image data
        metadata: Timestamp, dimensions, scenario name
    """
```

**Request:**
- `scenario_name`: Scenario name to find screenshot for (optional)
- `screenshot_path`: Direct path to a screenshot (optional)
- `run_id`: Specific run to search (optional)

**Response shape:**
```json
{
  "path": "reports/screenshots/failed_successful_admin_login.png",
  "base64": "iVBORw0KGgo...",
  "metadata": {
    "scenario_name": "Successful admin login",
    "timestamp": "2026-01-13T10:15:32Z",
    "size_bytes": 245678,
    "width": 1280,
    "height": 720,
    "run_id": "run_20260113_1015"
  }
}
```

**Edge cases:**
- If the screenshot cannot be found, return `{ "error": "Screenshot not found" }`.
- If the file is too large, return metadata only and `base64: null` with a warning.
- If `screenshot_path` is outside the repo, return `{ "error": "Invalid path" }`.

#### `find_similar_failures`

```python
@mcp.tool()
def find_similar_failures(
    error_pattern: Optional[str] = None,
    scenario_name: Optional[str] = None,
    limit: int = 5,
) -> dict[str, Any]:
    """
    Find past failures with similar patterns.

    Useful for identifying:
    - Flaky tests (same test fails intermittently)
    - Recurring issues (same error across different tests)
    - Regression patterns (failures after specific date)

    Returns:
        matches: List of similar past failures with:
            - scenario_name
            - run_id
            - error_message
            - similarity_score
            - timestamp
    """
```

**Request:**
- `error_pattern`: Substring or regex to match (optional)
- `scenario_name`: Scenario to match (optional)
- `limit`: Max results to return

**Response shape:**
```json
{
  "matches": [
    {
      "scenario_name": "Successful admin login",
      "run_id": "run_20260110_0900",
      "error_message": "TimeoutError: Timeout 30000ms exceeded",
      "similarity_score": 0.82,
      "timestamp": "2026-01-10T09:01:12Z"
    }
  ],
  "warnings": []
}
```

**Edge cases:**
- If no history exists, return an empty `matches` list.
- If both `error_pattern` and `scenario_name` are missing, return `{ "error": "No search criteria provided" }`.
- If `limit` is too large, cap it and add a warning.

#### `suggest_fix`

```python
@mcp.tool()
def suggest_fix(
    scenario_name: str,
    run_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Generate a specific code fix for a failure.

    Returns:
        diagnosis: Summary of what went wrong
        fixes: List of suggested fixes, each with:
            - file: File to modify
            - type: "edit" | "add" | "delete"
            - location: Line number or method name
            - current_code: Existing code (for edits)
            - suggested_code: Proposed fix
            - explanation: Why this fix should work
            - confidence: 0.0-1.0
    """
```

**Request:**
- `scenario_name`: Scenario to target
- `run_id`: Optional run ID

**Response shape:**
```json
{
  "diagnosis": "Selector change on admin login button",
  "fixes": [
    {
      "file": "pages/admin_page.py",
      "type": "edit",
      "location": "AdminPage.login",
      "current_code": "self.click('.login-btn')",
      "suggested_code": "self.click('button[type=submit]')",
      "explanation": "Selector is more stable than class",
      "confidence": 0.8
    }
  ]
}
```

**Edge cases:**
- If the scenario is not found, return `{ "error": "Scenario not found" }`.
- If no fix can be suggested, return a diagnosis with an empty `fixes` list.
- If code context is missing, return `{ "error": "Step definition not found" }`.



### Minimal Examples (Project Scenarios)

- `get_failure_context(scenario_name="Successful admin login", feature_file="features/ui/admin.feature")`
- `analyze_failure(context_id="ctx_20260113_101532_admin_login")`
- `get_screenshot(scenario_name="Login with invalid credentials")`
- `find_similar_failures(error_pattern="TimeoutError", limit=3)`
- `suggest_fix(scenario_name="Successful admin login")`

### Implementation Notes

**Screenshot handling:**
- Store screenshots with predictable names: `{scenario_name}_{timestamp}.png`
- Return base64 for Claude's vision capabilities
- Keep last N screenshots per scenario for comparison

**Log parsing:**
- Parse Behave's stdout/stderr
- Extract timestamps and log levels
- Filter to relevant timeframe around failure

**Historical data:**
- Store failure summaries in SQLite or JSON
- Enable pattern matching across runs
- Track fix success rate

---



## Server 2: Data Factory

### Purpose

Expose the `factories/` module for on-demand test data generation.

### Tools

| Tool | Description |
|------|-------------|
| `list_factories` | List available factory classes |
| `get_factory_schema` | Show fields, defaults, and types |
| `generate_data` | Generate a single record with optional overrides |
| `generate_batch` | Generate multiple records for bulk testing |

### Tool Specifications

#### `list_factories`

```python
@mcp.tool()
def list_factories() -> dict[str, Any]:
    """
    Return available factory classes from factories/.
    """
```

**Request:**
- no arguments

**Response shape:**
```json
{
  "factories": [
    {
      "name": "BookingBuilder",
      "module": "factories.booking_builder",
      "product_type": "Booking",
      "supports_batch": true,
      "supports_payload": true
    }
  ],
  "warnings": []
}
```

**Edge cases:**
- If no factories are found, return an empty list with a warning.
- If a factory module fails to import, skip it and report the error in `warnings`.

#### `get_factory_schema`

```python
@mcp.tool()
def get_factory_schema(factory: str) -> dict[str, Any]:
    """
    Inspect a factory and return its fields, defaults, and override keys.
    """
```

**Request:**
- `factory`: Factory class name (e.g., `BookingBuilder`)

**Response shape:**
```json
{
  "factory": "RoomBuilder",
  "product_type": "Room",
  "fields": [
    {"name": "room_name", "type": "str", "required": true, "default": "random"},
    {"name": "room_type", "type": "str", "required": true, "default": "Double"},
    {"name": "accessible", "type": "bool", "required": true, "default": false},
    {"name": "price", "type": "int", "required": true, "default": "random"},
    {"name": "features", "type": "list[str]", "required": false, "default": []},
    {"name": "description", "type": "str", "required": false, "default": null}
  ],
  "overrides": ["room_name", "room_type", "accessible", "price", "features", "description"],
  "notes": [
    "Overrides can map to builder methods when available",
    "If a model exposes to_api_payload(), output uses that shape"
  ]
}
```

**Edge cases:**
- Unknown factory name returns `{ "error": "Factory not found" }`.
- If schema extraction fails, return a partial schema with an `error` field.

#### `generate_data`

```python
@mcp.tool()
def generate_data(
    factory: str,
    overrides: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Generate a single record using a factory.

    Returns:
        factory: Factory name
        data: Generated fields (JSON-safe)
        source: "to_api_payload" | "dataclass" | "dict"
        warnings: Any skipped/unknown overrides
    """
```

**Request:**
- `factory`: Factory class name
- `overrides`: Optional dict applied to builder methods or output fields

**Response shape:**
```json
{
  "factory": "BookingBuilder",
  "source": "to_api_payload",
  "data": {
    "firstname": "Alex",
    "lastname": "Parker",
    "totalprice": 340,
    "depositpaid": false,
    "bookingdates": {
      "checkin": "2026-01-20",
      "checkout": "2026-01-25"
    }
  },
  "warnings": []
}
```

**Edge cases:**
- Unknown factory returns `{ "error": "Factory not found" }`.
- Unknown override keys are ignored and listed in `warnings`.
- If overrides are invalid (type errors, bad dates), return `{ "error": "Invalid overrides" }`.

#### `generate_batch`

```python
@mcp.tool()
def generate_batch(
    factory: str,
    count: int = 5,
    overrides: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Generate multiple records using a factory.
    """
```

**Request:**
- `factory`: Factory class name
- `count`: Number of records to generate
- `overrides`: Optional dict applied to each record

**Response shape:**
```json
{
  "factory": "GuestBuilder",
  "count": 3,
  "data": [
    {"firstname": "Ava", "lastname": "Chen", "email": "ava@example.com", "phone": null},
    {"firstname": "Sam", "lastname": "Ortiz", "email": "sam@example.com", "phone": null},
    {"firstname": "Priya", "lastname": "Iyer", "email": "priya@example.com", "phone": null}
  ],
  "warnings": []
}
```

**Edge cases:**
- If `count` <= 0, return `{ "error": "count must be > 0" }`.
- If `count` is very large, cap and return a warning.

### Minimal Examples (Project Classes)

- `list_factories()` -> `BookingBuilder`, `GuestBuilder`, `RoomBuilder`
- `generate_data(factory="RoomBuilder", overrides={"room_type": "Suite", "price": 350, "accessible": True})`
- `generate_batch(factory="GuestBuilder", count=2, overrides={"email": "test@example.com"})`

---


## Server 3: API Client

### Purpose

Expose the `services/` layer for safe API exploration and debugging.

### Tools

| Tool | Description |
|------|-------------|
| `list_services` | List available service classes |
| `list_methods` | List public methods and signatures for a service |
| `get_api_schema` | Show request/response expectations for a method |
| `call_method` | Invoke a service method with validated args |

### Tool Specifications

#### `list_services`

```python
@mcp.tool()
def list_services() -> dict[str, Any]:
    """
    List available service classes from services/.
    """
```

**Request:**
- no arguments

**Response shape:**
```json
{
  "services": [
    {"name": "AuthService", "module": "services.auth_service"},
    {"name": "BookingService", "module": "services.booking_service"},
    {"name": "RoomService", "module": "services.room_service"}
  ],
  "warnings": []
}
```

**Edge cases:**
- If no services are found, return an empty list with a warning.

#### `list_methods`

```python
@mcp.tool()
def list_methods(service: str) -> dict[str, Any]:
    """
    List public methods for a service with signatures.
    """
```

**Request:**
- `service`: Service class name (e.g., `BookingService`)

**Response shape:**
```json
{
  "service": "BookingService",
  "methods": [
    {
      "name": "get_all_bookings",
      "args": [
        {"name": "firstname", "type": "str", "required": false},
        {"name": "lastname", "type": "str", "required": false},
        {"name": "checkin", "type": "date", "required": false},
        {"name": "checkout", "type": "date", "required": false}
      ],
      "returns": "(Response, ResponseValidator)",
      "auth_required": false
    }
  ]
}
```

**Edge cases:**
- Unknown service returns `{ "error": "Service not found" }`.
- Private methods (prefixed with `_`) are excluded.

#### `get_api_schema`

```python
@mcp.tool()
def get_api_schema(service: str, method: str) -> dict[str, Any]:
    """
    Describe request/response expectations for a service method.
    """
```

**Request:**
- `service`: Service class name
- `method`: Method name

**Response shape:**
```json
{
  "service": "RoomService",
  "method": "create_room",
  "http_method": "POST",
  "endpoint": "/room",
  "auth_required": true,
  "args": [
    {"name": "room_name", "type": "str", "required": true},
    {"name": "room_type", "type": "str", "required": false},
    {"name": "accessible", "type": "bool", "required": false},
    {"name": "price", "type": "int", "required": false},
    {"name": "features", "type": "list[str]", "required": false},
    {"name": "description", "type": "str", "required": false},
    {"name": "image", "type": "str", "required": false}
  ],
  "returns": "(Response, ResponseValidator)",
  "notes": ["Auth inferred from docstring: 'Requires authentication'"]
}
```

**Edge cases:**
- If endpoint or HTTP verb cannot be inferred, return `null` with a note.
- If docstrings are missing, `auth_required` defaults to `unknown`.

#### `call_method`

```python
@mcp.tool()
def call_method(
    service: str,
    method: str,
    args: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Safely invoke a service method.

    Safety rules:
    - Only public methods on known service classes
    - No dynamic imports or eval
    - Timeouts for network calls
    """
```

**Request:**
- `service`: Service class name
- `method`: Method name
- `args`: Method arguments (dates should be ISO strings)

**Response shape (HTTP-style methods):**
```json
{
  "service": "BookingService",
  "method": "get_all_bookings",
  "args": {"lastname": "Parker"},
  "result_type": "http",
  "status_code": 200,
  "response": {"bookings": [{"bookingid": 123}]},
  "elapsed_ms": 85
}
```

**Response shape (value-returning methods):**
```json
{
  "service": "AuthService",
  "method": "login_as_admin",
  "result_type": "value",
  "result": "abc123token"
}
```

**Edge cases:**
- Unknown service/method returns `{ "error": "Service or method not found" }`.
- Invalid args returns `{ "error": "Argument validation failed" }`.
- Network timeouts return `{ "error": "Request timed out" }`.
- If the method returns an unexpected type, return `{ "error": "Unsupported return type" }`.

### Minimal Examples (Project Classes)

- `list_services()` -> `AuthService`, `BookingService`, `RoomService`
- `list_methods(service="AuthService")` -> `login`, `login_as_admin`, `validate_token`, `logout`
- `call_method(service="BookingService", method="get_all_bookings", args={"lastname": "Parker"})`

---

## Usage Examples

### Example 1: Diagnose a Failure

```
User: "The admin login test is failing, can you figure out why?"

Claude: [calls get_failure_context(scenario_name="admin login")]
Claude: [calls get_screenshot(scenario_name="admin login")]
Claude: [analyzes screenshot + context]

Response:
"The test is failing because the login button selector changed.

**Evidence:**
- Error: TimeoutError waiting for '.login-btn'
- Screenshot shows the login form, but button now has class 'btn-primary'
- The selector was last updated 2 weeks ago

**Suggested fix:**
In pages/admin_page.py line 52, change:
  self.click('.login-btn')
to:
  self.click('button[type=submit]')

This selector is more resilient to CSS class changes."
```

### Example 2: Generate Test Data

```
User: "Create a booking payload for next week"

Claude: [calls get_factory_schema(factory="BookingBuilder")]
Claude: [calls generate_data(factory="BookingBuilder", overrides={"nights": 5})]

Response:
"Generated booking data:
{
  "firstname": "Alex",
  "lastname": "Parker",
  "totalprice": 340,
  "depositpaid": false,
  "bookingdates": {
    "checkin": "2026-01-20",
    "checkout": "2026-01-25"
  }
}

Want me to use this payload in an API call or a scenario?"
```

### Example 3: Call an API Method

```
User: "List bookings for the current customer"

Claude: [calls list_services()]
Claude: [calls list_methods(service="BookingService")]
Claude: [calls call_method(service="BookingService", method="get_all_bookings", args={"lastname": "Parker"})]

Response:
"Returned 2 bookings for lastname 'Parker'.
First booking id: 8417
Status code: 200"
```

---


## Development Roadmap

### Phase 1: Failure Analyzer
- [ ] Core failure context gathering
- [ ] Screenshot base64 encoding
- [ ] Log parsing and filtering
- [ ] Basic fix suggestions
- [ ] Historical failure tracking (optional)

### Phase 2: Data Factory
- [ ] Factory discovery and schema inspection
- [ ] Single record generation with overrides
- [ ] Batch generation
- [ ] Safe serialization (dataclasses to dict)

### Phase 3: API Client
- [ ] Service discovery and method signatures
- [ ] Argument validation and safe invocation
- [ ] Auth handling hooks (if needed)
- [ ] Response normalization and timing

---


## Current Status (2026-01-13)

**Planning Phase: COMPLETE**

This document reflects the project-specific A1/A2/A4 scope.

### What's Been Designed

| Component | Status | Notes |
|-----------|--------|-------|
| **Failure Analyzer** | ✅ Complete | 5 tools with specs, context caching, size guards |
| **Data Factory** | ✅ Draft | Tool list and interface defined |
| **API Client** | ✅ Draft | Tool list and safety rules defined |

### Key Design Decisions

1. **Implementation Order**: Failure Analyzer → Data Factory → API Client
2. **Scope**: Project-specific examples (no reusable package or PyPI distribution)
3. **Safety Rails**: timeouts, path validation, bounded output

### Codex Review Feedback (Incorporated)

- ✅ Lean depth over breadth (A1/A2/A4 only)
- ✅ Defer Test Generator + Coverage Gap Finder to qaagent
- ✅ Safety rails emphasized (timeouts, path validation, bounded output)
- ✅ Optional A3 Environment/Config only if time permits

---

## Next Steps (When Resuming)

### Immediate: Prototype Failure Analyzer

1. [ ] Create server skeletons in `mcp_server/`
2. [ ] Implement failure context parsing for Behave JSON results
3. [ ] Add screenshot lookup + base64 encoding with size limits
4. [ ] Add log capture and truncation
5. [ ] Test against real failures in this project

### Then: Data Factory

6. [ ] Implement factory discovery from `factories/`
7. [ ] Implement schema extraction from builders/dataclasses
8. [ ] Implement single record + batch generation
9. [ ] Add override validation and warnings

### Then: API Client

10. [ ] Implement service discovery from `services/`
11. [ ] Implement method signature introspection
12. [ ] Add safe `call_method` wrapper with timeouts
13. [ ] Normalize responses (status, json/text, elapsed)

---

## MCP Server Options Summary (For Codex Review)

**Date:** 2026-01-13
**Status:** Decisions recorded - A1/A2/A4 in scope, others deferred

### Context

The current `test_runner_server.py` provides basic test execution capabilities (6 tools). We want to create more useful and relevant MCP server examples for this project.

**Key constraints:**
- MCP servers created here are **project-specific** (for this automation-framework-example)
- Servers that could be **general-use packages** will be built separately (e.g., in qaagent project, distributed via pip)
- Test Generator is identified as a candidate for the separate qaagent project

---

### Option A: Project-Specific Servers (Build Here)

#### A1. Failure Analyzer (Simplified)
**Purpose:** Diagnose why tests fail and suggest fixes
**Scope:** Project-specific (uses this project's structure)

| Tool | Description |
|------|-------------|
| `get_failure_context` | Gather artifacts for a failed scenario (logs, screenshot, code) |
| `analyze_failure` | Analyze failure with screenshot (vision) and suggest root cause |
| `get_screenshot` | Return screenshot as base64 for visual analysis |

**Value:** Immediate debugging help. Leverages Claude's vision for screenshot analysis.
**Complexity:** Medium - requires parsing Behave JSON, locating screenshots, tracing step definitions.

---

#### A2. Data Factory Server
**Purpose:** Expose the `factories/` module for test data generation via MCP
**Scope:** Project-specific (wraps this project's factories)

| Tool | Description |
|------|-------------|
| `list_factories` | List available data factories (BookingFactory, etc.) |
| `generate_data` | Generate test data using a factory with optional overrides |
| `generate_batch` | Generate multiple records for bulk testing |
| `get_factory_schema` | Show factory fields and their types/defaults |

**Value:** Let Claude generate realistic test data on demand during test creation or debugging.
**Complexity:** Low-Medium - introspect factory classes, call them with parameters.

---

#### A3. Environment/Config Server
**Purpose:** Manage test environments, credentials, and configuration
**Scope:** Project-specific (reads this project's config)

| Tool | Description |
|------|-------------|
| `get_environment` | Get current environment config (base URL, browser, etc.) |
| `list_environments` | List available environments (local, staging, prod) |
| `get_credentials` | Get credentials for a role (admin, user) - masked or test-only |
| `validate_environment` | Check if environment is accessible and healthy |

**Value:** Help Claude understand and interact with different test environments.
**Complexity:** Low - read config files, environment variables.

---

#### A4. API Client Server
**Purpose:** Wrap the `services/` layer as MCP tools for API exploration
**Scope:** Project-specific (exposes this project's service methods)

| Tool | Description |
|------|-------------|
| `list_services` | List available API service classes |
| `list_methods` | List methods for a service with signatures |
| `call_method` | Execute a service method and return response |
| `get_api_schema` | Show expected request/response format for a method |

**Value:** Let Claude explore and test APIs directly without writing code.
**Complexity:** Medium - introspect service classes, handle auth, execute calls safely.

---

#### A5. Report Aggregator Server
**Purpose:** Combine test results, generate summaries, track trends
**Scope:** Project-specific (reads this project's reports)

| Tool | Description |
|------|-------------|
| `get_run_history` | List recent test runs with pass/fail summary |
| `compare_runs` | Compare two runs to identify regressions/fixes |
| `get_flaky_tests` | Identify tests that pass/fail inconsistently |
| `get_trend` | Show pass rate trend over time |
| `generate_summary` | Generate a human-readable test summary |

**Value:** Historical analysis of test health and trends.
**Complexity:** Medium - aggregate multiple result files, compute statistics.

---

#### A6. Coverage Gap Finder (Simplified)
**Purpose:** Identify untested functionality
**Scope:** Project-specific (analyzes this project's code vs tests)

| Tool | Description |
|------|-------------|
| `analyze_coverage` | Full coverage gap analysis (methods vs scenarios) |
| `get_untested_methods` | List service/page methods with no test coverage |
| `get_unused_steps` | Find step definitions never used in scenarios |
| `suggest_priorities` | Prioritize gaps by risk/importance |

**Value:** Proactively find what's missing before bugs escape.
**Complexity:** High - requires AST parsing, step matching, cross-referencing.

---

### Option B: General-Use Servers (Build Separately - qaagent project)

#### B1. Test Generator
**Purpose:** Generate new Behave scenarios from API specs, code analysis, or gaps
**Distribution:** pip package, usable by any Behave project

| Tool | Description |
|------|-------------|
| `generate_api_scenarios` | Generate scenarios for API endpoints |
| `generate_from_gap` | Generate scenarios to fill coverage gaps |
| `suggest_edge_cases` | Suggest edge cases for existing scenarios |
| `preview_scenarios` | Preview generated scenarios before saving |

**Why separate:** Highly reusable across projects. Benefits from dedicated development and testing.
**Target:** qaagent project, pip installable.

---

### Recommendation Matrix

| Server | Value | Complexity | Project-Specific? | Recommendation |
|--------|-------|------------|-------------------|----------------|
| A1. Failure Analyzer | High | Medium | Yes | **Build here** |
| A2. Data Factory | Medium | Low | Yes | **Build here** |
| A3. Environment/Config | Medium | Low | Yes | Consider |
| A4. API Client | High | Medium | Yes | **Build here** |
| A5. Report Aggregator | Medium | Medium | Yes | Consider |
| A6. Coverage Gap Finder | High | High | Partially | Defer or simplify |
| B1. Test Generator | High | High | No | **qaagent project** |

### Suggested MVP for This Project

Based on value and complexity:

1. **Failure Analyzer (A1)** - High immediate value for debugging
2. **Data Factory Server (A2)** - Low complexity, useful for test data
3. **API Client Server (A4)** - High value for API exploration

These three provide complementary capabilities:
- Debug failures (A1)
- Generate test data (A2)
- Explore/test APIs (A4)

---

### Questions for Codex Review

1. Which servers provide the most value for demonstrating MCP patterns?
2. Should we prioritize breadth (more simple servers) or depth (fewer comprehensive servers)?
3. Are there other server ideas not listed that would be more relevant?
4. For A6 (Coverage Gap Finder) - build a simplified version here, or defer entirely to qaagent?
5. What's the right balance between "useful example" and "production-ready tool"?

---

### Codex Review Feedback (2026-01-13)

**Q1. Most value for MCP patterns:**
- Highest signal: **A1 Failure Analyzer**, **A4 API Client**, **A2 Data Factory**
- These cover distinct MCP patterns:
  - A1: Debugging/artifact retrieval
  - A4: Safe execution of service calls
  - A2: Data generation with schema discovery

**Q2. Breadth vs depth:**
- **Lean depth**: 3 solid servers with 3-5 tools each and 1-2 demo flows beats 5-6 thin ones
- Optional 4th: A3 (Environment/Config) is low effort and shows safe config access + masking

**Q3. Other server ideas:**
- Optional: "Locator/Selector Inspector" for UI page objects (list selectors + screenshot context)
- Recommendation: Stick to A1/A2/A4 unless UI-centric example is needed

**Q4. Coverage Gap Finder:**
- **Defer to qaagent**, or keep ultra-lite: just "unused step defs" + "feature files by area"
- Skip full AST cross-referencing - high effort, will look shallow if rushed

**Q5. Useful example vs production-ready:**
- Target: **"useful example with safety rails"**
- Include: timeouts, path validation, bounded output, simple error handling
- Skip: full hardening (RBAC, auditing, complex config) unless part of demo story

---

### Final Decision: Servers to Build

| Server | Tools | MCP Pattern Demonstrated |
|--------|-------|--------------------------|
| **A1. Failure Analyzer** | 3-5 | Artifact retrieval, vision (screenshots), code tracing |
| **A2. Data Factory** | 3-4 | Schema discovery, data generation, introspection |
| **A4. API Client** | 3-4 | Safe service execution, method discovery |

**Optional (if time permits):**
| **A3. Environment/Config** | 3-4 | Config access, credential masking |

**Deferred:**
- A5 Report Aggregator → not needed for MVP
- A6 Coverage Gap Finder → qaagent project (or ultra-lite version)
- B1 Test Generator → qaagent project

---

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-13 | Test Generator → qaagent project | General-use, benefits from dedicated package |
| 2026-01-13 | Build A1, A2, A4 | Codex review: highest signal, distinct MCP patterns |
| 2026-01-13 | Depth over breadth | 3 solid servers beats 5-6 thin ones |
| 2026-01-13 | Coverage Gap Finder → defer/ultra-lite | High complexity, defer full version to qaagent |
| 2026-01-13 | Target "useful example with safety rails" | Not production hardening |

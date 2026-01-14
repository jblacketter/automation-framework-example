# MCP Servers

This directory contains MCP servers for this automation framework. These servers let Claude interact with your test suite—running tests, analyzing failures, and generating test data.

---

## MCP Test Runner

### What It Does

The Test Runner server lets Claude execute and analyze your Behave test suite. Instead of switching to a terminal to run tests and parse output, you can ask Claude to run tests and explain what happened.

### Why It's Useful

**Problem:** Running and debugging tests requires context-switching:
- Run tests in terminal
- Scroll through output to find failures
- Open result files to see details
- Cross-reference error messages with code

**Solution:** Ask Claude in plain English:
- "Run the smoke tests"
- "What failed in the last run?"
- "Why did the login test fail?"
- "Show me what API tests we have"

Claude runs the tests, parses the results, and explains failures in context—including the step definition code and related page objects.

### What You Can Ask Claude

| What You Want | Example Prompt |
|---------------|----------------|
| Run all tests | "Run the test suite" |
| Run by tag | "Run the smoke tests" or "Run tests tagged @api" |
| Run specific feature | "Run the booking API tests" |
| Run one scenario | "Run the 'Create booking' scenario" |
| See what's available | "What test scenarios do we have?" |
| Check last run | "What were the results of the last test run?" |
| Debug a failure | "Why did the admin login test fail?" |
| Coverage overview | "What's our test coverage?" |

### Example Conversation

**You:** "Run the API tests"

**Claude:** *calls `run_tests(tags="@api")`*

"Ran 8 scenarios: 6 passed, 2 failed.

**Failures:**
1. `Create booking with invalid dates` - AssertionError: Expected 400, got 200
2. `Delete booking without auth` - ConnectionError: Connection refused"

**You:** "Why did the invalid dates test fail?"

**Claude:** *calls `analyze_failure(scenario_name="Create booking with invalid dates")`*

"The test expected the API to reject invalid dates (checkout before checkin) with a 400 status, but the API returned 200.

**Failed step:** `Then the response status code should be 400`

**Step definition:** `steps/api_steps.py:67`
```python
@then('the response status code should be {code:d}')
def step_check_status(context, code):
    assert context.response.status_code == code
```

This looks like an API bug—it should validate that checkout date is after checkin date."

### Tools Reference

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `list_features(feature_type)` | See available tests | `"api"`, `"ui"`, or `"all"` |
| `run_tests(tags, feature_path, scenario, dry_run, timeout_seconds)` | Execute tests | Filter by tag, path, or name |
| `get_last_results()` | Get most recent results | — |
| `get_results(run_id)` | Get specific run results | `run_id` from previous run |
| `get_failure_details(scenario_name, run_id)` | Failure info + screenshots | Optional filters |
| `get_test_coverage()` | Coverage summary | — |
| `analyze_failure(scenario_name, run_id)` | Deep failure analysis | Includes code context |

### Filtering Tests

| Filter | Example | What It Does |
|--------|---------|--------------|
| By tag | `tags="@smoke"` | Run scenarios with tag |
| By tag expression | `tags="@api and not @slow"` | Combine tags |
| By feature path | `feature_path="features/api/"` | Run all in directory |
| By scenario name | `scenario="Create booking"` | Run matching scenario |
| Dry run | `dry_run=True` | Show what would run without executing |

### Understanding Results

Results include:
- **Summary**: Total scenarios, passed, failed, skipped
- **Failure details**: Error message, failed step, screenshot path (for UI tests)
- **Code context**: Step definition source, related page/service code
- **Run metadata**: Duration, run ID for future reference

### Tips

- **Start with dry_run**: Use `dry_run=True` to see what would run before executing
- **Use tags for speed**: Run `@smoke` tests for quick feedback
- **Analyze failures in context**: `analyze_failure` shows the step code and related files
- **Check screenshots**: UI test failures include screenshot paths in `reports/screenshots/`

---

## MCP Data Factory

### What It Does

The Data Factory server lets Claude generate realistic test data on demand. Instead of manually crafting JSON payloads or digging through factory code, you can ask Claude to create exactly the test data you need.

### Why It's Useful

**Problem:** Writing test data is tedious. You need to:
- Remember the correct field names and types
- Create valid date ranges
- Generate realistic names and values
- Match the exact API payload format

**Solution:** Ask Claude in plain English:
- "Create a booking for next week"
- "Generate 5 guest records"
- "Make a luxury suite with all amenities"

The server handles the details—field names, date formatting, API payload structure—and returns ready-to-use data.

### What You Can Ask Claude

Once connected, try prompts like:

| What You Want | Example Prompt |
|---------------|----------------|
| Quick test data | "Generate a booking" |
| Specific values | "Create a booking for $500 with deposit paid" |
| Custom guest | "Make a booking for John Smith" |
| Room setup | "Generate an accessible suite at $350/night with WiFi and TV" |
| Bulk data | "Create 10 different guests" |
| Reproducible data | "Generate a guest with seed 42 so I can get the same one later" |
| Explore options | "What fields can I customize for BookingBuilder?" |

### Available Data Types

| Factory | Creates | Output Format |
|---------|---------|---------------|
| `BookingBuilder` | Hotel booking with guest, dates, price | API-ready JSON payload |
| `GuestBuilder` | Guest with name, contact info | Raw field data |
| `RoomBuilder` | Room with type, price, amenities | API-ready JSON payload |

### Example Conversation

**You:** "I need a booking payload for testing the create booking API"

**Claude:** *calls `generate_data(factory="BookingBuilder")`*

```json
{
  "firstname": "Daniel",
  "lastname": "Wagner",
  "totalprice": 216,
  "depositpaid": false,
  "bookingdates": {
    "checkin": "2026-01-20",
    "checkout": "2026-01-22"
  }
}
```

**You:** "Make it a week-long stay with deposit paid, for a guest named Jane Doe"

**Claude:** *calls `generate_data(factory="BookingBuilder", overrides={"nights": 7, "deposit_paid": true, "guest": {"firstname": "Jane", "lastname": "Doe"}})`*

```json
{
  "firstname": "Jane",
  "lastname": "Doe",
  "totalprice": 742,
  "depositpaid": true,
  "bookingdates": {
    "checkin": "2026-01-20",
    "checkout": "2026-01-27"
  }
}
```

### Tools Reference

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `list_factories()` | See what's available | — |
| `get_factory_schema(factory)` | See fields and customization options | `factory`: "BookingBuilder", "GuestBuilder", "RoomBuilder" |
| `generate_data(factory, overrides, seed)` | Create one record | `overrides`: customize fields, `seed`: reproducible output |
| `generate_batch(factory, count, overrides, seed)` | Create multiple records | `count`: 1-100 |

### Customization Options

You can override most fields using natural names:

| Override | Example Value | Notes |
|----------|---------------|-------|
| `total_price` | `500` | Sets the booking price |
| `deposit_paid` | `true` / `false` | Mark deposit status |
| `nights` | `7` | Calculate checkout from checkin |
| `check_in` | `"2026-02-01"` | Specific date (ISO format) |
| `guest` | `{"firstname": "Jane"}` | Nested guest customization |
| `room_type` | `"Suite"` | Single, Double, Twin, Family, Suite |
| `price` | `350` | Room price per night |
| `accessible` | `true` | Wheelchair accessible |
| `features` | `["WiFi", "TV"]` | Room amenities |

### Tips

- **Start simple**: Just ask for what you need in plain English
- **Iterate**: Generate basic data first, then refine with overrides
- **Use seed for debugging**: Same seed = same output, helpful for reproducing issues
- **Batch for load testing**: Generate up to 100 records at once

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server locally:

```bash
python mcp_server/test_runner_server.py
```

Or run the data factory server:

```bash
python mcp_server/data_factory_server.py
```

## Claude Desktop Configuration (macOS)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "test-runner": {
      "command": "python",
      "args": ["/full/path/to/automation-framework-example/mcp_server/test_runner_server.py"],
      "env": {
        "PATH": "/full/path/to/automation-framework-example/.venv/bin"
      }
    },
    "data-factory": {
      "command": "python",
      "args": ["/full/path/to/automation-framework-example/mcp_server/data_factory_server.py"]
    }
  }
}
```

## Claude Code Configuration

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "test-runner": {
      "command": "python",
      "args": ["mcp_server/test_runner_server.py"]
    },
    "data-factory": {
      "command": "python",
      "args": ["mcp_server/data_factory_server.py"]
    }
  }
}
```

## Venv Handling

The server resolves the Behave executable in this order:

1. `sys.executable -m behave` (current Python environment)
2. `MCP_BEHAVE_PATH` environment variable
3. `.venv/bin/behave` or `venv/bin/behave` under project root
4. `behave` found on PATH

If none are found, the tool returns an error.

## Notes

- Results are stored in `reports/results_run_*.json` and only the last 10 runs are kept.
- Screenshots (UI failures) are in `reports/screenshots/`.

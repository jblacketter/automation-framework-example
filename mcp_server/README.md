# MCP Test Runner

This MCP server exposes the Behave test suite to AI assistants (Claude Desktop / Claude Code).

## Tools

- `list_features(feature_type="all")`: List features and scenarios with tags.
- `run_tests(tags=None, feature_path=None, scenario=None, dry_run=False, timeout_seconds=300)`: Run Behave with filters.
- `get_last_results()`: Fetch the most recent results.
- `get_results(run_id)`: Fetch results for a specific run.
- `get_failure_details(scenario_name=None, run_id=None)`: Failure list + stdout/stderr tails + screenshots.
- `get_test_coverage()`: Coverage summary for api/ui features.
- `analyze_failure(scenario_name, run_id=None)`: Failure details + code context.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server locally:

```bash
python mcp_server/test_runner_server.py
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

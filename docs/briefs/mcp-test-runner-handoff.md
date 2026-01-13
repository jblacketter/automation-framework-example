# MCP Test Runner - Codex Implementation Handoff

**Date:** January 12, 2026
**From:** Claude Code
**To:** Codex
**Status:** Ready for implementation

---

## Project Location

```
/Users/jackblacketter/projects/automation-framework-example
```

**Important:** Not `PythonProject` - that was the old name.

---

## Task Summary

Implement an MCP server that allows AI assistants to execute and analyze BDD tests.

Reference documents:
- Brief: `docs/briefs/mcp-test-runner.md`
- Original design: `mcp_server/MCP_TEST_RUNNER_DESIGN.md`

---

## Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `mcp_server/__init__.py` | Create | Empty or minimal package init |
| `mcp_server/test_runner_server.py` | Create | Main implementation |
| `mcp_server/README.md` | Create | Setup and usage docs |
| `requirements.txt` | Modify | Add `fastmcp>=0.1.0` |
| `.claude/settings.json` | Modify | Add mcpServers config |

---

## Tools to Implement

### 1. `list_features(feature_type: str = "all") -> dict`
- Returns features/scenarios with tags
- Key by `{type}/{stem}` to avoid collisions (e.g., `api/auth`, `ui/home`)
- Include feature-level tags

### 2. `run_tests(...) -> dict`
```python
def run_tests(
    tags: str = None,
    feature_path: str = None,
    scenario: str = None,
    dry_run: bool = False,
    timeout_seconds: int = 300
) -> dict:
```
- Generate `run_id` (e.g., `run_20260112_221845`)
- Save results to `reports/results_{run_id}.json`
- Validate `feature_path` is within project root
- Use `sys.executable -m behave` (see venv handling below)
- Return: `run_id`, `results_path`, `summary`, `stdout_tail`, `stderr_tail`
- Auto-cleanup: keep last 10 result files

### 3. `get_last_results() -> dict`
- Return most recent results file
- Handle missing/corrupted JSON gracefully

### 4. `get_results(run_id: str) -> dict`
- Return specific run by ID
- Error if not found

### 5. `get_failure_details(scenario_name: str = None, run_id: str = None) -> dict`
- Return errors + stdout/stderr tails + screenshot paths
- Filter by scenario_name if provided

### 6. `get_test_coverage() -> dict`
- Summarize tests by area (api/ui)
- Return feature counts, scenario counts, file list

### 7. `analyze_failure(scenario_name: str, run_id: str = None) -> dict`
- Return: error message, failed step
- Include step definition code (~20 lines context)
- Include related page object/service code if identifiable
- Bound output to prevent huge responses

---

## Key Implementation Details

### Venv Handling
```python
import sys
import shutil

def get_behave_command():
    """Get behave command with proper venv handling."""
    # Primary: use current Python's behave module
    if _can_run_behave_module():
        return [sys.executable, "-m", "behave"]

    # Fallback: environment variable
    if os.environ.get("MCP_BEHAVE_PATH"):
        return [os.environ["MCP_BEHAVE_PATH"]]

    # Fallback: common venv locations
    for venv_path in [".venv/bin/behave", "venv/bin/behave"]:
        full_path = PROJECT_ROOT / venv_path
        if full_path.exists():
            return [str(full_path)]

    # Last resort: PATH
    if shutil.which("behave"):
        return ["behave"]

    raise RuntimeError("Cannot find behave executable")
```

### Subprocess with Timeout
```python
try:
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout_seconds
    )
except subprocess.TimeoutExpired as e:
    return {
        "error": f"Test run timed out after {timeout_seconds}s",
        "stdout_tail": e.stdout[-2000:] if e.stdout else None,
        "stderr_tail": e.stderr[-1000:] if e.stderr else None
    }
```

### Path Validation
```python
def validate_feature_path(path: str) -> Path:
    """Ensure path is within project root."""
    resolved = (PROJECT_ROOT / path).resolve()
    if not str(resolved).startswith(str(PROJECT_ROOT.resolve())):
        raise ValueError(f"Path '{path}' is outside project root")
    return resolved
```

### Result File Management
```python
def cleanup_old_results(keep: int = 10):
    """Keep only the last N result files."""
    results = sorted(
        REPORTS_DIR.glob("results_run_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    for old_file in results[keep:]:
        old_file.unlink()
```

### JSON Error Handling
```python
def load_results(path: Path) -> dict:
    """Load results with error handling."""
    if not path.exists():
        return {"error": f"Results file not found: {path}"}
    try:
        with open(path) as f:
            content = f.read()
            if not content.strip():
                return {"error": "Results file is empty"}
            return json.loads(content)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in results: {e}"}
```

### Handle All Behave Element Types
```python
def _get_scenario_status(element: dict) -> str:
    """Handle scenario, scenario_outline, and all statuses."""
    for step in element.get("steps", []):
        result = step.get("result", {})
        status = result.get("status", "undefined")
        if status == "failed":
            return "failed"
        if status in ("skipped", "undefined", "untested"):
            return "skipped"
    return "passed"
```

---

## Settings.json Update

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "test-runner": {
      "command": "python",
      "args": ["mcp/test_runner_server.py"]
    }
  }
}
```

---

## Success Criteria Checklist

After implementation, Claude Code will validate:

- [ ] Server starts without errors: `python mcp/test_runner_server.py`
- [ ] `list_features("all")` returns api + ui features without key collisions
- [ ] `run_tests(tags="@smoke")` executes and returns run_id
- [ ] `run_tests(dry_run=True)` shows what would run
- [ ] `get_last_results()` returns the run just executed
- [ ] `get_results(run_id)` returns specific run
- [ ] `get_failure_details()` includes stdout/stderr tails
- [ ] `get_test_coverage()` shows correct counts
- [ ] `analyze_failure()` returns code context
- [ ] Timeout works (can test with artificially low value)
- [ ] Path validation rejects `../../../etc/passwd`
- [ ] Old results cleaned up (keep last 10)

---

## Notes

- The existing framework has 4 passing smoke tests (3 API, 1 UI)
- WIP tests are tagged `@wip` and skipped
- Screenshots go to `reports/screenshots/`
- Behave JSON output works: `behave --format json --outfile reports/results.json`

Ready for implementation!

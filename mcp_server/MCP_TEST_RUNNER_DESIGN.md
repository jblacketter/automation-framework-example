# MCP Test Runner Server Design

## Purpose

Add an MCP server to the automation framework that allows AI assistants to execute and analyze BDD tests. This demonstrates practical AI-assisted test automation—a key differentiator for the job search.

---

## File Structure

```
automation-framework-example/
├── mcp_server/
│   ├── __init__.py
│   ├── test_runner_server.py    # Main MCP server
│   └── README.md                # Setup instructions
├── ... (existing framework files)
└── requirements.txt             # Add fastmcp
```

---

## Tools to Implement

| Tool | Purpose | Parameters |
|------|---------|------------|
| `list_features` | Show available test features/scenarios | `feature_type: api\|ui\|all` |
| `run_tests` | Execute tests | `tags`, `feature_path`, `scenario` (all optional) |
| `get_last_results` | Get results from most recent run | none |
| `get_failure_details` | Get logs/screenshots for a failure | `scenario_name` (optional) |
| `get_test_coverage` | Show which features have tests | none |

---

## Server Implementation

### mcp_server/test_runner_server.py

```python
"""
Test Runner MCP Server

Allows AI assistants to execute and analyze BDD tests.
"""

import json
import subprocess
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("test-runner")

PROJECT_ROOT = Path(__file__).parent.parent
FEATURES_DIR = PROJECT_ROOT / "features"
REPORTS_DIR = PROJECT_ROOT / "reports"


@mcp.tool()
def list_features(feature_type: str = "all") -> dict:
    """
    List available test features and scenarios.
    
    Args:
        feature_type: Filter by 'api', 'ui', or 'all'
    
    Returns:
        Dict with features and their scenarios
    """
    features = {}
    
    search_paths = []
    if feature_type in ("api", "all"):
        search_paths.append(FEATURES_DIR / "api")
    if feature_type in ("ui", "all"):
        search_paths.append(FEATURES_DIR / "ui")
    
    for path in search_paths:
        if path.exists():
            for feature_file in path.glob("*.feature"):
                features[feature_file.stem] = _parse_feature(feature_file)
    
    return features


@mcp.tool()
def run_tests(
    tags: str = None,
    feature_path: str = None,
    scenario: str = None,
    dry_run: bool = False
) -> dict:
    """
    Execute BDD tests with optional filters.
    
    Args:
        tags: Behave tag expression (e.g., '@smoke', '@api and not @wip')
        feature_path: Specific feature file or directory (e.g., 'features/api/')
        scenario: Specific scenario name to run
        dry_run: If True, show what would run without executing
    
    Returns:
        Test execution results with pass/fail counts and details
    """
    cmd = ["behave", "--format", "json", "--outfile", "reports/results_run_<run_id>.json"]
    
    if tags:
        cmd.extend(["--tags", tags])
    if feature_path:
        cmd.append(feature_path)
    if scenario:
        cmd.extend(["--name", scenario])
    if dry_run:
        cmd.append("--dry-run")
    
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    
    return _parse_results(result, dry_run)


@mcp.tool()
def get_last_results() -> dict:
    """
    Get results from the most recent test run.
    
    Returns:
        Parsed test results with summary and failure details
    """
    results_file = REPORTS_DIR / "results_run_<run_id>.json"
    
    if not results_file.exists():
        return {"error": "No results found. Run tests first."}
    
    with open(results_file) as f:
        raw_results = json.load(f)
    
    return _summarize_results(raw_results)


@mcp.tool()
def get_failure_details(scenario_name: str = None) -> dict:
    """
    Get detailed failure information including logs and screenshots.
    
    Args:
        scenario_name: Specific scenario to get details for (optional)
    
    Returns:
        Failure details with error messages, stack traces, and screenshot paths
    """
    results = get_last_results()
    
    if "error" in results:
        return results
    
    failures = results.get("failures", [])
    
    if scenario_name:
        failures = [f for f in failures if scenario_name.lower() in f["name"].lower()]
    
    # Attach screenshots if available
    for failure in failures:
        screenshot = _find_screenshot(failure["name"])
        if screenshot:
            failure["screenshot_path"] = str(screenshot)
    
    return {"failures": failures, "screenshot_dir": str(REPORTS_DIR / "screenshots")}


@mcp.tool()
def get_test_coverage() -> dict:
    """
    Show test coverage summary - which areas have tests.
    
    Returns:
        Coverage summary by feature area
    """
    coverage = {
        "api": {"features": 0, "scenarios": 0, "files": []},
        "ui": {"features": 0, "scenarios": 0, "files": []}
    }
    
    for test_type in ["api", "ui"]:
        path = FEATURES_DIR / test_type
        if path.exists():
            for feature_file in path.glob("*.feature"):
                scenarios = _parse_feature(feature_file)
                coverage[test_type]["features"] += 1
                coverage[test_type]["scenarios"] += len(scenarios)
                coverage[test_type]["files"].append({
                    "name": feature_file.stem,
                    "scenario_count": len(scenarios)
                })
    
    coverage["total_features"] = coverage["api"]["features"] + coverage["ui"]["features"]
    coverage["total_scenarios"] = coverage["api"]["scenarios"] + coverage["ui"]["scenarios"]
    
    return coverage


# =============================================================================
# Helper Functions
# =============================================================================

def _parse_feature(feature_path: Path) -> list:
    """Parse a feature file and extract scenario names with tags."""
    scenarios = []
    current_tags = []
    
    with open(feature_path) as f:
        for line in f:
            line = line.strip()
            
            # Capture tags
            if line.startswith("@"):
                current_tags = line.split()
            
            # Capture scenarios
            elif line.startswith("Scenario:") or line.startswith("Scenario Outline:"):
                scenario_name = line.split(":", 1)[1].strip()
                scenarios.append({
                    "name": scenario_name,
                    "tags": current_tags
                })
                current_tags = []
    
    return scenarios


def _parse_results(result: subprocess.CompletedProcess, dry_run: bool) -> dict:
    """Parse behave execution results."""
    if dry_run:
        return {"dry_run": True, "output": result.stdout}
    
    results_file = REPORTS_DIR / "results_run_<run_id>.json"
    if results_file.exists():
        try:
            raw = json.loads(results_file.read_text())
            summary = _summarize_results(raw)
            summary["exit_code"] = result.returncode
            return summary
        except json.JSONDecodeError:
            pass
    
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout[-2000:] if result.stdout else None,
        "stderr": result.stderr[-1000:] if result.stderr else None,
        "error": "Failed to parse results JSON"
    }


def _summarize_results(raw_results: list) -> dict:
    """Summarize raw behave JSON results."""
    summary = {
        "total_scenarios": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "failures": [],
        "duration_seconds": 0
    }
    
    for feature in raw_results:
        for element in feature.get("elements", []):
            if element["type"] == "scenario":
                summary["total_scenarios"] += 1
                
                # Calculate duration
                for step in element.get("steps", []):
                    if "result" in step and "duration" in step["result"]:
                        summary["duration_seconds"] += step["result"]["duration"]
                
                status = _get_scenario_status(element)
                summary[status] += 1
                
                if status == "failed":
                    summary["failures"].append({
                        "feature": feature["name"],
                        "name": element["name"],
                        "error": _get_error_message(element),
                        "failed_step": _get_failed_step(element)
                    })
    
    # Round duration
    summary["duration_seconds"] = round(summary["duration_seconds"], 2)
    
    return summary


def _get_scenario_status(scenario: dict) -> str:
    """Determine overall scenario status from steps."""
    for step in scenario.get("steps", []):
        result = step.get("result", {})
        if result.get("status") == "failed":
            return "failed"
        if result.get("status") == "skipped":
            return "skipped"
    return "passed"


def _get_error_message(scenario: dict) -> str:
    """Extract error message from failed scenario."""
    for step in scenario.get("steps", []):
        result = step.get("result", {})
        if result.get("status") == "failed":
            error = result.get("error_message", ["Unknown error"])
            if isinstance(error, list):
                error = "\n".join(error)
            return error[:1000]  # Truncate long errors
    return "Unknown error"


def _get_failed_step(scenario: dict) -> str:
    """Get the step that failed."""
    for step in scenario.get("steps", []):
        result = step.get("result", {})
        if result.get("status") == "failed":
            return f"{step.get('keyword', '')} {step.get('name', '')}"
    return None


def _find_screenshot(scenario_name: str) -> Path | None:
    """Find screenshot for a failed scenario."""
    screenshot_dir = REPORTS_DIR / "screenshots"
    if not screenshot_dir.exists():
        return None
    
    # Create safe search pattern from scenario name
    safe_name = "".join(c if c.isalnum() else "_" for c in scenario_name)[:30].lower()
    
    for screenshot in screenshot_dir.glob("*.png"):
        if safe_name in screenshot.stem.lower():
            return screenshot
    
    # Return most recent if no match
    screenshots = sorted(screenshot_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    return screenshots[0] if screenshots else None


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    mcp.run()
```

---

## Setup Instructions

### 1. Add dependency to requirements.txt

```
fastmcp>=0.1.0
```

### 2. Create the MCP folder structure

```bash
mkdir -p mcp
touch mcp_server/__init__.py
# Copy test_runner_server.py content
```

### 3. Test locally

```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
python mcp_server/test_runner_server.py
```

### 4. Configure for Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

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

### 5. Configure for Claude Code

Add to `.claude/settings.json` in the project:

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

---

## Example Usage

Once configured, you can ask Claude:

- **"Run the smoke tests"** → Executes `behave --tags=@smoke`
- **"What tests are available?"** → Lists all features and scenarios
- **"What failed in the last run?"** → Shows failure details with errors
- **"Run just the API booking tests"** → Executes `behave features/api/bookings.feature`
- **"Show me test coverage"** → Summarizes tests by area

---

## Demo Value

This MCP server demonstrates:

1. **Practical AI integration** — Not just using AI, but building tools for AI
2. **Modern Python patterns** — Type hints, pathlib, clean architecture
3. **Understanding of MCP** — Shows you can build developer tools
4. **Test automation depth** — Combines framework knowledge with AI tooling

In an interview: *"Let me show you how I've integrated AI into my test workflow"* → Run tests via Claude, analyze failures, all conversationally.

---

## Future Extensions

Once the basic server works, consider adding complementary MCP servers:

| Server | Tools | Purpose |
|--------|-------|---------|
| **Failure Analyzer (A1)** | `analyze_failure`, `get_screenshot`, `suggest_fix` | Diagnose failures with artifacts |
| **Data Factory (A2)** | `list_factories`, `generate_data`, `generate_batch` | Generate test data |
| **API Client (A4)** | `list_services`, `call_method`, `get_api_schema` | Explore/test APIs safely |
| **Test Generator (qaagent)** | `generate_scenario`, `analyze_api_spec` | Deferred to qaagent |

---

*Ready to implement in IDE*

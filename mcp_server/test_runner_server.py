"""
Test Runner MCP Server.

Provides tools for listing, running, and analyzing Behave tests.
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastmcp import FastMCP

mcp = FastMCP("test-runner")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FEATURES_DIR = PROJECT_ROOT / "features"
REPORTS_DIR = PROJECT_ROOT / "reports"

RESULTS_GLOB = "results_run_*.json"
STDOUT_TAIL_CHARS = 2000
STDERR_TAIL_CHARS = 1000
KEEP_RESULTS = 10

STEP_DECORATOR_RE = re.compile(
    r'@(?:given|when|then|step)\(\s*[rRuUfF]*[\'"](.+?)[\'"]\s*\)'
)


def _tail(text: Optional[str], limit: int) -> Optional[str]:
    if not text:
        return None
    if len(text) <= limit:
        return text
    return text[-limit:]


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_feature_path(path_value: str) -> Path:
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    resolved = candidate.resolve()
    if not _is_within_root(resolved, PROJECT_ROOT.resolve()):
        raise ValueError(f"Path '{path_value}' is outside project root")
    if not resolved.exists():
        raise ValueError(f"Path '{path_value}' does not exist")
    return resolved


def _can_run_behave_module() -> bool:
    return importlib.util.find_spec("behave") is not None


def _get_behave_command() -> list[str]:
    if _can_run_behave_module():
        return [sys.executable, "-m", "behave"]

    env_path = os.environ.get("MCP_BEHAVE_PATH")
    if env_path:
        return [env_path]

    for venv_path in [".venv/bin/behave", "venv/bin/behave"]:
        full_path = PROJECT_ROOT / venv_path
        if full_path.exists():
            return [str(full_path)]

    if shutil.which("behave"):
        return ["behave"]

    raise RuntimeError("Cannot find behave executable")


def _generate_run_id() -> str:
    return f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _results_path_for_run_id(run_id: str) -> Path:
    return REPORTS_DIR / f"results_{run_id}.json"


def _meta_path_for_run_id(run_id: str) -> Path:
    return REPORTS_DIR / f"results_{run_id}_meta.json"


def _extract_run_id(results_path: Path) -> str:
    stem = results_path.stem
    if not stem.startswith("results_"):
        return ""
    return stem[len("results_") :]


def _validate_run_id(run_id: str) -> str:
    if not re.match(r"^[A-Za-z0-9_-]+$", run_id):
        raise ValueError("Invalid run_id format")
    return run_id


def _cleanup_old_results(keep: int = KEEP_RESULTS) -> None:
    results = sorted(
        REPORTS_DIR.glob(RESULTS_GLOB),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for old_file in results[keep:]:
        run_id = _extract_run_id(old_file)
        meta_path = _meta_path_for_run_id(run_id)
        try:
            old_file.unlink()
        except OSError:
            pass
        if meta_path.exists():
            try:
                meta_path.unlink()
            except OSError:
                pass


def _load_results(path: Path) -> dict[str, Any] | list[Any]:
    if not path.exists():
        return {"error": f"Results file not found: {path}"}
    try:
        content = path.read_text()
    except OSError as exc:
        return {"error": f"Failed to read results file: {exc}"}
    if not content.strip():
        return {"error": "Results file is empty"}
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON in results: {exc}"}


def _summarize_results(raw_results: list[Any]) -> dict[str, Any]:
    summary = {
        "total_scenarios": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "failures": [],
        "duration_seconds": 0.0,
    }

    for feature in raw_results:
        for element in feature.get("elements", []):
            if element.get("type") not in ("scenario", "scenario_outline"):
                continue
            summary["total_scenarios"] += 1
            for step in element.get("steps", []):
                duration = step.get("result", {}).get("duration")
                if isinstance(duration, (int, float)):
                    summary["duration_seconds"] += duration
            status = _get_scenario_status(element)
            summary[status] += 1
            if status == "failed":
                summary["failures"].append(
                    {
                        "feature": feature.get("name"),
                        "name": element.get("name"),
                        "error": _get_error_message(element),
                        "failed_step": _get_failed_step(element),
                    }
                )

    summary["duration_seconds"] = round(summary["duration_seconds"], 2)
    return summary


def _get_scenario_status(element: dict[str, Any]) -> str:
    steps = element.get("steps", [])
    if not steps:
        return "skipped"
    for step in steps:
        status = step.get("result", {}).get("status", "undefined")
        if status == "failed":
            return "failed"
        if status in ("skipped", "undefined", "untested"):
            return "skipped"
    return "passed"


def _get_error_message(element: dict[str, Any]) -> str:
    for step in element.get("steps", []):
        result = step.get("result", {})
        if result.get("status") == "failed":
            error = result.get("error_message", ["Unknown error"])
            if isinstance(error, list):
                error = "\n".join(error)
            return str(error)[:1000]
    return "Unknown error"


def _get_failed_step(element: dict[str, Any]) -> Optional[str]:
    for step in element.get("steps", []):
        result = step.get("result", {})
        if result.get("status") == "failed":
            keyword = step.get("keyword", "").strip()
            name = step.get("name", "").strip()
            if keyword:
                return f"{keyword} {name}".strip()
            return name
    return None


def _load_run_meta(run_id: str) -> dict[str, Any]:
    meta_path = _meta_path_for_run_id(run_id)
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text())
    except json.JSONDecodeError:
        return {}


def _write_run_meta(run_id: str, meta: dict[str, Any]) -> None:
    meta_path = _meta_path_for_run_id(run_id)
    meta_path.write_text(json.dumps(meta, indent=2))


def _build_results_payload(run_id: str, results_path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "run_id": run_id,
        "results_path": str(results_path),
    }
    raw = _load_results(results_path)
    if isinstance(raw, dict) and "error" in raw:
        payload["error"] = raw["error"]
        return payload
    if not isinstance(raw, list):
        payload["error"] = "Unexpected results format"
        return payload
    payload["summary"] = _summarize_results(raw)
    return payload


def _merge_run_meta(payload: dict[str, Any], run_id: str) -> dict[str, Any]:
    meta = _load_run_meta(run_id)
    for key in ("stdout_tail", "stderr_tail", "exit_code", "dry_run", "timed_out", "created_at"):
        if key in meta:
            payload[key] = meta[key]
    return payload


def _find_latest_results_file() -> Optional[Path]:
    results = list(REPORTS_DIR.glob(RESULTS_GLOB))
    if not results:
        return None
    return max(results, key=lambda path: path.stat().st_mtime)


def _parse_feature(feature_path: Path) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    feature_tags: list[str] = []
    pending_tags: list[str] = []
    feature_name: Optional[str] = None

    with feature_path.open() as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("@"):
                pending_tags.extend(line.split())
                continue
            if line.startswith("Feature:"):
                feature_name = line.split(":", 1)[1].strip()
                feature_tags = pending_tags
                pending_tags = []
                continue
            if line.startswith("Scenario:") or line.startswith("Scenario Outline:"):
                scenario_name = line.split(":", 1)[1].strip()
                scenarios.append({"name": scenario_name, "tags": pending_tags})
                pending_tags = []

    return {
        "name": feature_name or feature_path.stem,
        "tags": feature_tags,
        "scenarios": scenarios,
        "path": str(feature_path.relative_to(PROJECT_ROOT)),
    }


def _find_screenshot(scenario_name: str) -> Optional[Path]:
    screenshot_dir = REPORTS_DIR / "screenshots"
    if not screenshot_dir.exists():
        return None

    safe_name = "".join(c if c.isalnum() else "_" for c in scenario_name)[:30].lower()
    for screenshot in screenshot_dir.glob("*.png"):
        if safe_name in screenshot.stem.lower():
            return screenshot

    screenshots = sorted(
        screenshot_dir.glob("*.png"), key=lambda path: path.stat().st_mtime, reverse=True
    )
    return screenshots[0] if screenshots else None


def _strip_step_keyword(step_text: str) -> str:
    text = step_text.strip()
    for keyword in ("Given", "When", "Then", "And", "But"):
        if text.startswith(f"{keyword} "):
            return text[len(keyword) + 1 :]
    return text


def _pattern_to_regex(pattern: str) -> re.Pattern:
    escaped = re.escape(pattern)
    escaped = re.sub(r"\\\{[^}]+\\\}", r".+", escaped)
    return re.compile(f"^{escaped}$")


def _format_snippet(lines: list[str], center_index: int, before: int = 10, after: int = 10) -> str:
    start = max(0, center_index - before)
    end = min(len(lines), center_index + after + 1)
    return "\n".join(f"{idx + 1}: {lines[idx]}" for idx in range(start, end))


def _find_step_definition(step_text: str) -> tuple[Optional[dict[str, Any]], list[str]]:
    if not step_text:
        return None, []
    target = _strip_step_keyword(step_text)

    steps_dir = PROJECT_ROOT / "steps"
    for step_file in steps_dir.rglob("*.py"):
        lines = step_file.read_text().splitlines()
        for idx, line in enumerate(lines):
            match = STEP_DECORATOR_RE.search(line)
            if not match:
                continue
            pattern = match.group(1)
            if not _pattern_to_regex(pattern).fullmatch(target):
                continue
            def_idx = None
            for jdx in range(idx + 1, len(lines)):
                if lines[jdx].lstrip().startswith("def "):
                    def_idx = jdx
                    break
            if def_idx is None:
                continue
            def_line = lines[def_idx].strip()
            func_match = re.match(r"def\s+([A-Za-z0-9_]+)", def_line)
            func_name = func_match.group(1) if func_match else None
            snippet = _format_snippet(lines, def_idx)
            context_lines = lines[max(0, def_idx - 10) : min(len(lines), def_idx + 11)]
            return (
                {
                    "pattern": pattern,
                    "file": str(step_file.relative_to(PROJECT_ROOT)),
                    "line": def_idx + 1,
                    "function": func_name,
                    "snippet": snippet,
                },
                context_lines,
            )
    return None, []


def _camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _find_related_code(context_lines: list[str]) -> list[dict[str, Any]]:
    related: list[dict[str, Any]] = []
    if not context_lines:
        return related
    text = "\n".join(context_lines)
    class_names = sorted(
        {
            match
            for match in re.findall(r"\b[A-Z][A-Za-z0-9]+(?:Page|Service)\b", text)
        }
    )

    for class_name in class_names:
        folder = "pages" if class_name.endswith("Page") else "services"
        file_path = PROJECT_ROOT / folder / f"{_camel_to_snake(class_name)}.py"
        if not file_path.exists():
            continue
        lines = file_path.read_text().splitlines()
        class_idx = None
        for idx, line in enumerate(lines):
            if line.strip().startswith(f"class {class_name}"):
                class_idx = idx
                break
        if class_idx is None:
            class_idx = 0
        snippet = _format_snippet(lines, class_idx)
        related.append(
            {
                "name": class_name,
                "file": str(file_path.relative_to(PROJECT_ROOT)),
                "line": class_idx + 1,
                "snippet": snippet,
            }
        )
        if len(related) >= 2:
            break
    return related


@mcp.tool()
def list_features(feature_type: str = "all") -> dict[str, Any]:
    """
    List available test features and scenarios.

    Args:
        feature_type: Filter by 'api', 'ui', or 'all'

    Returns:
        Dict with features and their scenarios.
    """
    if feature_type not in ("api", "ui", "all"):
        return {"error": "feature_type must be 'api', 'ui', or 'all'"}

    features: dict[str, Any] = {}
    search_paths: list[tuple[str, Path]] = []
    if feature_type in ("api", "all"):
        search_paths.append(("api", FEATURES_DIR / "api"))
    if feature_type in ("ui", "all"):
        search_paths.append(("ui", FEATURES_DIR / "ui"))

    for label, path in search_paths:
        if not path.exists():
            continue
        for feature_file in path.glob("*.feature"):
            key = f"{label}/{feature_file.stem}"
            features[key] = _parse_feature(feature_file)

    return {"features": features}


@mcp.tool()
def run_tests(
    tags: Optional[str] = None,
    feature_path: Optional[str] = None,
    scenario: Optional[str] = None,
    dry_run: bool = False,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    """
    Execute Behave tests with optional filters.

    Args:
        tags: Behave tag expression (e.g., '@smoke')
        feature_path: Feature file or directory (e.g., 'features/api/')
        scenario: Specific scenario name to run
        dry_run: If True, show what would run without executing
        timeout_seconds: Timeout in seconds before aborting

    Returns:
        Test execution results including run_id and summary.
    """
    run_id = _generate_run_id()
    results_path = _results_path_for_run_id(run_id)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        behave_cmd = _get_behave_command()
    except RuntimeError as exc:
        return {"error": str(exc)}

    cmd = behave_cmd + ["--format", "json", "--outfile", str(results_path)]

    if tags:
        cmd.extend(["--tags", tags])
    if feature_path:
        try:
            resolved = _validate_feature_path(feature_path)
        except ValueError as exc:
            return {"error": str(exc)}
        cmd.append(str(resolved))
    if scenario:
        cmd.extend(["--name", scenario])
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stdout_tail = _tail(exc.stdout, STDOUT_TAIL_CHARS)
        stderr_tail = _tail(exc.stderr, STDERR_TAIL_CHARS)
        meta = {
            "run_id": run_id,
            "results_path": str(results_path),
            "exit_code": None,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
            "dry_run": dry_run,
            "timed_out": True,
            "created_at": datetime.now().isoformat(),
        }
        _write_run_meta(run_id, meta)
        return {
            "error": f"Test run timed out after {timeout_seconds}s",
            "run_id": run_id,
            "results_path": str(results_path),
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
            "timed_out": True,
        }

    stdout_tail = _tail(result.stdout, STDOUT_TAIL_CHARS)
    stderr_tail = _tail(result.stderr, STDERR_TAIL_CHARS)
    meta = {
        "run_id": run_id,
        "results_path": str(results_path),
        "exit_code": result.returncode,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
        "dry_run": dry_run,
        "timed_out": False,
        "created_at": datetime.now().isoformat(),
    }
    _write_run_meta(run_id, meta)
    _cleanup_old_results()

    if dry_run and not results_path.exists():
        return {
            "run_id": run_id,
            "results_path": str(results_path),
            "dry_run": True,
            "exit_code": result.returncode,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
            "note": "Dry run does not produce results JSON.",
        }

    payload = _build_results_payload(run_id, results_path)
    payload["exit_code"] = result.returncode
    payload["stdout_tail"] = stdout_tail
    payload["stderr_tail"] = stderr_tail
    payload["dry_run"] = dry_run
    return payload


@mcp.tool()
def get_last_results() -> dict[str, Any]:
    """
    Get results from the most recent test run.

    Returns:
        Parsed test results with summary and failure details.
    """
    latest = _find_latest_results_file()
    if not latest:
        return {"error": "No results found. Run tests first."}
    run_id = _extract_run_id(latest)
    payload = _build_results_payload(run_id, latest)
    return _merge_run_meta(payload, run_id)


@mcp.tool()
def get_results(run_id: str) -> dict[str, Any]:
    """
    Get results for a specific run.

    Args:
        run_id: Run identifier (e.g., run_20260112_221845)
    """
    try:
        run_id = _validate_run_id(run_id)
    except ValueError as exc:
        return {"error": str(exc)}
    results_path = _results_path_for_run_id(run_id)
    payload = _build_results_payload(run_id, results_path)
    return _merge_run_meta(payload, run_id)


@mcp.tool()
def get_failure_details(
    scenario_name: Optional[str] = None, run_id: Optional[str] = None
) -> dict[str, Any]:
    """
    Get detailed failure information including logs and screenshots.

    Args:
        scenario_name: Specific scenario to get details for (optional)
        run_id: Optional run identifier (defaults to latest)
    """
    if run_id:
        payload = get_results(run_id)
    else:
        payload = get_last_results()

    if "error" in payload:
        return payload

    summary = payload.get("summary", {})
    failures = summary.get("failures", [])
    if scenario_name:
        failures = [
            failure
            for failure in failures
            if scenario_name.lower() in str(failure.get("name", "")).lower()
        ]

    for failure in failures:
        screenshot = _find_screenshot(failure.get("name", ""))
        if screenshot:
            failure["screenshot_path"] = str(screenshot)

    return {
        "run_id": payload.get("run_id"),
        "results_path": payload.get("results_path"),
        "stdout_tail": payload.get("stdout_tail"),
        "stderr_tail": payload.get("stderr_tail"),
        "failures": failures,
        "screenshot_dir": str(REPORTS_DIR / "screenshots"),
    }


@mcp.tool()
def get_test_coverage() -> dict[str, Any]:
    """
    Show test coverage summary - which areas have tests.

    Returns:
        Coverage summary by feature area.
    """
    coverage = {
        "api": {"features": 0, "scenarios": 0, "files": []},
        "ui": {"features": 0, "scenarios": 0, "files": []},
    }

    for test_type in ("api", "ui"):
        path = FEATURES_DIR / test_type
        if not path.exists():
            continue
        for feature_file in path.glob("*.feature"):
            feature_data = _parse_feature(feature_file)
            scenario_count = len(feature_data.get("scenarios", []))
            coverage[test_type]["features"] += 1
            coverage[test_type]["scenarios"] += scenario_count
            coverage[test_type]["files"].append(
                {"name": feature_file.stem, "scenario_count": scenario_count}
            )

    coverage["total_features"] = coverage["api"]["features"] + coverage["ui"]["features"]
    coverage["total_scenarios"] = coverage["api"]["scenarios"] + coverage["ui"]["scenarios"]
    return coverage


@mcp.tool()
def analyze_failure(scenario_name: str, run_id: Optional[str] = None) -> dict[str, Any]:
    """
    Analyze a failed scenario and return related code context.

    Args:
        scenario_name: Scenario name to analyze
        run_id: Optional run identifier (defaults to latest)
    """
    if not scenario_name:
        return {"error": "scenario_name is required"}

    if run_id:
        payload = get_results(run_id)
    else:
        payload = get_last_results()

    if "error" in payload:
        return payload

    summary = payload.get("summary", {})
    failures = summary.get("failures", [])
    match = None
    for failure in failures:
        if scenario_name.lower() in str(failure.get("name", "")).lower():
            match = failure
            break

    if not match:
        return {
            "error": f"No failure found for scenario '{scenario_name}'",
            "run_id": payload.get("run_id"),
            "results_path": payload.get("results_path"),
        }

    step_info, context_lines = _find_step_definition(match.get("failed_step", ""))
    related = _find_related_code(context_lines)

    return {
        "run_id": payload.get("run_id"),
        "results_path": payload.get("results_path"),
        "scenario": match.get("name"),
        "error": match.get("error"),
        "failed_step": match.get("failed_step"),
        "step_definition": step_info,
        "related_code": related,
    }


if __name__ == "__main__":
    mcp.run()

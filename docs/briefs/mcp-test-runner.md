# Task Brief: MCP Test Runner Server

## Roles
- Lead: Collaborative (Claude Code + Codex)
- Reviewer: Claude (web) + Codex
- Arbiter: Human

## Summary
- **What:** Build an MCP server that allows AI assistants to execute and analyze BDD tests
- **Why:** Demonstrates practical AI integration for test automation - a portfolio differentiator showing not just AI usage, but building tools for AI
- **Type:** New feature (Python + MCP)

## Target
- **Integration:** Claude Desktop, Claude Code
- **Framework:** FastMCP
- **Tests:** Existing Behave test suite

---

## Review Findings (Codex)

### P1 - Must Fix
| Issue | Location | Resolution |
|-------|----------|------------|
| `run_tests` calls behave from PATH without venv | :86, :400 | Use `sys.executable -m behave` with fallback |
| No subprocess timeout - hung run blocks server | :118 | Add configurable timeout (5 min default) |
| `get_last_results` has no error handling for json.load | :128 | Add try/except, handle corrupted/empty files |

### P2 - Should Fix
| Issue | Location | Resolution |
|-------|----------|------------|
| Single results.json overwritten, unsafe for concurrent | :104, :128 | Add run_id + timestamped result files |
| `list_features` keys collide (api/ui same filename) | :69, :212 | Key by `{type}/{stem}` or full relative path |
| `_summarize_results` ignores scenario_outline, undefined | :271, :298 | Handle all behave element types and statuses |
| `get_failure_details` doesn't retain stdout/stderr | :147, :237 | Store and return stdout/stderr tails |

### P3 - Consider
| Issue | Location | Resolution |
|-------|----------|------------|
| `feature_path` unvalidated, can escape repo | :104 | Validate path is within project root |

---

## Decisions Made

### 1. Venv Handling ✅
**Decision:** Use `sys.executable -m behave` as primary method
- Fallback chain: `sys.executable` → `MCP_BEHAVE_PATH` env var → `.venv/bin/behave` → `venv/bin/behave`
- This works regardless of how server is launched

### 2. Concurrent Runs ✅
**Decision:** Add `run_id` + timestamped result files
- Each run gets unique ID (e.g., `run_20260112_221845`)
- Results stored as `reports/results_{run_id}.json`
- `get_last_results()` returns most recent as convenience
- `get_results(run_id)` for specific run

### 3. Timeout ✅
**Decision:** Configurable with 5-minute default
- `run_tests(timeout_seconds=300)` parameter
- Can override per-run for known long suites
- Returns partial results + timeout error on expiry

### 4. `analyze_failure` Tool ✅
**Decision:** Yes, add it
- Returns: error, failed step, step definition code, page object/service code
- Bound output to relevant files + small line windows (~20 lines context)
- Enables AI to suggest fixes with full context

---

## Open Questions (Remaining)

### 5. Return shape for `run_tests`
Should `run_tests` return:
```python
{
    "run_id": "run_20260112_221845",
    "results_path": "reports/results_run_20260112_221845.json",
    "summary": {...},
    "stdout_tail": "...",
    "stderr_tail": "..."
}
```
**Recommendation:** Yes - makes subsequent calls deterministic

### 6. Result retention
How many runs to retain?
- (a) Last 10 runs (auto-cleanup old)
- (b) Last N runs (configurable)
- (c) All runs (manual cleanup)
- (d) Time-based (last 24 hours)

**Recommendation:** (a) Last 10 runs - reasonable default, prevents disk bloat

---

## Success Criteria

### Core Functionality
- [ ] `list_features` returns features/scenarios with tags (no key collisions)
- [ ] `run_tests` executes behave with tag/path/scenario filters
- [ ] `run_tests` returns run_id for deterministic follow-up
- [ ] `run_tests` supports dry-run mode
- [ ] `run_tests` has configurable timeout (5 min default)
- [ ] `get_last_results` returns most recent parsed results
- [ ] `get_results(run_id)` returns specific run results
- [ ] `get_failure_details` returns errors + stdout/stderr + screenshot paths
- [ ] `get_test_coverage` summarizes tests by area
- [ ] `analyze_failure` returns code context for AI fix suggestions

### Technical Quality
- [ ] Venv handled via `sys.executable -m behave` with fallbacks
- [ ] Subprocess timeout prevents hanging
- [ ] JSON parsing has error handling
- [ ] Path validation prevents repo escape
- [ ] Results use run_id, no overwrites
- [ ] Auto-cleanup retains last 10 runs
- [ ] Type hints on all functions
- [ ] Docstrings with clear Args/Returns

### Integration
- [ ] Works with Claude Desktop (config documented)
- [ ] Works with Claude Code (config in settings.json)
- [ ] README with setup instructions
- [ ] Demo examples showing usage

### Testing
- [ ] Manual test: list features via MCP
- [ ] Manual test: run smoke tests via MCP
- [ ] Manual test: get failure details via MCP
- [ ] Manual test: concurrent runs don't collide
- [ ] Server starts without errors

## Out of Scope
- AI-powered failure analysis (beyond code context)
- Test generation from specs
- Test data management
- Allure or HTML report integration
- Remote/CI execution (local only for now)

## Files to Create/Modify
- [ ] `mcp_server/__init__.py` - Package init
- [ ] `mcp_server/test_runner_server.py` - Main server implementation
- [ ] `mcp_server/README.md` - Setup and usage instructions
- [ ] `requirements.txt` - Add fastmcp dependency
- [ ] `.claude/settings.json` - Add MCP server config

## References
- Design doc: `mcp_server/MCP_TEST_RUNNER_DESIGN.md`
- FastMCP docs: https://github.com/jlowin/fastmcp
- MCP specification: https://modelcontextprotocol.io

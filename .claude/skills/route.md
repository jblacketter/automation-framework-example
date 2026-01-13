# Skill: /route

Suggest which model or approach should handle a test automation task.

## When to Use
- Before starting complex test development
- When unsure which model should lead (Claude Code vs Codex)
- When deciding between different implementation approaches
- When task has specific constraints (speed, thoroughness)

## Routing Criteria

### By Task Type

| Task Type | Recommended Lead | Rationale |
|-----------|------------------|-----------|
| New test scenarios | Claude Code | Good at BDD structure, domain language |
| Fix broken selectors | Claude Code | Needs browser inspection, iterative |
| API service implementation | Codex | Optimized for code generation |
| Page object creation | Codex | Structured code with patterns |
| Debug flaky tests | Claude Code | Needs investigation, reasoning |
| Architecture review | Claude | Strong reasoning, catches issues |
| Bulk test generation | Codex | Fast code generation at scale |
| Documentation | Claude | Clear explanations, structure |

### By Constraint

| Constraint | Routing Decision |
|------------|------------------|
| Quick fix needed | Claude Code (interactive) |
| Many similar tests | Codex (batch generation) |
| Complex debugging | Claude Code (reasoning) |
| Code review | Claude (thorough analysis) |
| Exploratory testing | Claude Code (adaptive) |

### Trust Levels

| Level | Role | Assigned To |
|-------|------|-------------|
| Lead | Generates code/tests | Claude Code or Codex (task-dependent) |
| Reviewer | Reviews output | Claude or Codex (opposite of lead) |
| Arbiter | Final decision | Human (always) |

## Instructions

When this skill is invoked:

1. Ask about the task (if not provided):
   - What needs to be done?
   - Is this new tests, fixes, or refactoring?
   - Any time constraints?

2. Apply routing criteria:
   - Match task type to recommended model
   - Apply constraint filters
   - Consider current context

3. Provide recommendation:

```markdown
## Routing Recommendation

**Task:** [Task description]

**Type:** [New tests / Fix / Refactor / Review]

**Recommendation:**
- Lead: [Model] - [Reason]
- Reviewer: [Model] - [Reason]

**Approach:**
- [Specific approach or skill to use]

**Notes:**
- [Any special considerations]
```

## Examples

User: `/route add API tests for the room endpoint`

Response:
```
Lead: Codex
Reason: Bulk test generation, structured API patterns
Reviewer: Claude
Approach: Use /brief to define scope, then generate service + steps + feature
```

User: `/route fix the admin login test`

Response:
```
Lead: Claude Code
Reason: Needs browser inspection, iterative selector updates
Reviewer: Human (verify selectors work)
Approach: Use fix-selectors skill, run in headed mode
```

User: `/route review the booking service implementation`

Response:
```
Lead: Claude
Reason: Code review needs reasoning, pattern analysis
Use: /review services/booking_service.py
```

User: `/route`

Response: "What test automation task are you trying to route? Describe the work needed."

## Workflow Integration

This skill works with:
- `/brief` - Define task scope before routing
- `/review` - Review output after lead completes
- `/decide` - Log routing decisions for future reference

# Skill: /review

Run the reviewer checklist against test code or framework changes. Encodes the lead/reviewer workflow.

## When to Use
- After generating new tests or framework code
- Before merging generated output
- When you want a structured quality check
- As part of the lead/reviewer flow

## Quick Handoff

When the user just says "review" with no arguments:

1. **Check recent file changes** - List recently modified files in `features/`, `steps/`, `pages/`, `services/`, `core/`
2. **Check the todo list** - What was being worked on?
3. **Identify the review target** - Most recently changed test-related files

The user should NOT need to copy/paste content. Read the file directly.

## Instructions

When this skill is invoked:

1. Identify what is being reviewed:
   - If a file path is provided, review that file
   - If just "review" with no args, use Quick Handoff rules
   - Read the file directly - do not ask user to paste content

2. Determine which checklist(s) apply:
   - `checklists/test_review.md` - for test scenarios and steps
   - `checklists/page_object_review.md` - for page objects
   - `checklists/service_review.md` - for API services
   - `checklists/framework_review.md` - for core framework changes

3. Run through each applicable checklist item and assess:
   - [x] Pass - requirement met
   - [ ] Fail - requirement not met (explain why)
   - [-] N/A - not applicable to this review

4. Provide a structured verdict:

```markdown
## Review: [file_path]

### Test Quality
- [x] Scenarios written in domain language
- [x] Steps are reusable
- [ ] Missing cleanup for created data ← **FAIL**

### Code Quality
- [x] Type hints present
- [x] Docstrings for public methods
- [x] No hardcoded credentials

### Issues Found
1. [Specific issue with location/line]

### Suggested Fixes
1. [How to fix issue 1]

### Verdict
**FAIL** - 1 issue found. Add cleanup hook for created bookings.
```

5. If FAIL:
   - The lead should revise and resubmit
   - If still failing after 2 attempts, escalate to human

## Parameters

- `/review [file_path]` - Review specific file
- `/review --type=test` - Review only test files
- `/review --type=page` - Review only page objects
- `/review` - Review most recent changes

## Examples

User: `/review features/api/bookings.feature`

Response: Run test review checklist against the feature file, output structured verdict.

User: `/review pages/admin_page.py`

Response: Run page object checklist, check selectors, methods, and patterns.

User: `/review`

Response: "Recent changes: `steps/api_steps.py` (10 mins ago), `features/api/auth.feature` (15 mins ago). Which would you like me to review?"

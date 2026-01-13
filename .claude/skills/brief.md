# Skill: /brief

Create, display, or update a task brief for current work on the automation framework.

## When to Use
- Starting new test development work (create a brief first)
- Checking scope during implementation (display current brief)
- Scope changed (update the brief)
- Reviewing what success looks like

## Instructions

### Display Mode (`/brief` or `/brief [name]`)

1. If name specified, read `docs/briefs/[name].md`
2. If no name specified, show list of available briefs
3. Display the brief contents, highlighting:
   - Current roles (Lead/Reviewer)
   - Success criteria (checked vs unchecked)
   - Open questions

### Create Mode (`/brief create [name]`)

1. Create `docs/briefs/` directory if needed
2. Interactively fill in:
   - Summary (What test/feature are we building?)
   - Test type (API, UI, or both)
   - Success criteria (as checkboxes)
   - Out of scope
3. Save to `docs/briefs/[name].md`

### Update Mode (`/brief update [name]`)

1. Read existing brief
2. Ask what needs to change:
   - Add/remove success criteria
   - Resolve open questions
   - Update constraints
   - Mark items complete
3. Save updated brief

### Check Mode (`/brief check [name]`)

1. Read the brief
2. For each success criterion, assess current status:
   - [ ] Not started
   - [~] In progress
   - [x] Complete
3. Report completion percentage and blockers

## Template

```markdown
# Task Brief: [Name]

## Roles
- Lead: [Claude Code/Codex/Human]
- Reviewer: [Claude/Codex/Human]

## Summary
- **What:** [What tests or features are being built]
- **Why:** [Why this is needed]
- **Type:** [API/UI/Both]

## Target Application
- **URL:** [Which test target]
- **Endpoints/Pages:** [Specific areas being tested]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] All tests pass locally
- [ ] Tests pass in CI

## Out of Scope
- [Item 1]

## Open Questions
- [Question 1]

## Files to Create/Modify
- [ ] `features/[type]/[name].feature`
- [ ] `steps/[type]_steps.py`
- [ ] `services/[name]_service.py` (if API)
- [ ] `pages/[name]_page.py` (if UI)
```

## Examples

User: `/brief`

Response: "Available briefs: admin-login-fix, booking-flow. Which would you like to see?"

User: `/brief create room-api-tests`

Response: "Creating brief for 'room-api-tests'. What endpoints are we testing? (GET /room, POST /room, etc.)"

User: `/brief check admin-login-fix`

Response: "admin-login-fix: 1/4 success criteria complete (25%). Blockers: Need to identify current admin page selectors."

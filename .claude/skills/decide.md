# Skill: /decide

Log a decision to the project decision log with structured fields.

## When to Use
- After making an architectural or implementation choice
- When resolving an open question about test design
- When choosing between test approaches or patterns
- After discussions that result in a clear direction

## Decision Log Location

The decision log is `docs/decision_log.md`.

## Instructions

When this skill is invoked:

1. Ask the user for the decision details if not provided:
   - What was decided?
   - What was the context?
   - What alternatives were considered?
   - What's the rationale?

2. Determine who decided (Human, Claude, Codex, or collaborative)

3. Append a new entry to `docs/decision_log.md` in reverse chronological order using this format:

```markdown
---
## YYYY-MM-DD: [Decision Title]
- **Decision:** [Clear statement of what was decided]
- **Context:** [Why this decision was needed]
- **Alternatives considered:**
  - [Option 1]
  - [Option 2]
- **Rationale:** [Why this option was chosen]
- **Decided by:** [Human/Claude/Codex/Collaborative]
- **Affects:** [Files or components affected]
```

4. Confirm the decision was logged and summarize it back to the user.

## Common Decision Categories for Test Automation

- **Test targets:** Which application/API to test against
- **Selectors:** How to locate elements (data-testid vs CSS vs XPath)
- **Test data:** How to manage test data lifecycle
- **Assertions:** Which assertion library/pattern to use
- **Waits:** Explicit vs implicit waits, timeout values
- **Architecture:** Service layer vs direct API calls
- **CI/CD:** Pipeline configuration, parallelization
- **Tagging:** How to organize tests (@smoke, @regression, etc.)

## Examples

User: `/decide we're using data-testid attributes for all new selectors`

Response: Log entry created for "Selector Strategy" with data-testid as the decision, noting alternatives like CSS classes and XPath, and the rationale of stability and maintainability.

User: `/decide`

Response: Ask "What decision would you like to log?" and gather the required fields interactively.

User: `/decide separate API and UI test targets`

Response: Log entry for "Test Target Architecture" explaining the decision to use restful-booker.herokuapp.com for API and automationintesting.online for UI, with rationale about public accessibility and stability.

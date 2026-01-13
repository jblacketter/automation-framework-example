# Skill: /memory

Query or store information in project memory. Supports both retrieval ("what did we decide about X?") and storage ("remember this pattern").

## When to Use
- To recall past decisions, patterns, or context
- To store a reusable test pattern or framework insight
- To check what the project "knows" about a topic
- To build up test automation knowledge over time

## Memory Structure

Memory is stored in `memory/` at repo root:

```
memory/
├── decisions/          # Linked from docs/decision_log.md
├── patterns/           # Reusable test patterns, conventions
├── findings/           # Test results, analysis outputs
├── context/            # Project-specific knowledge
└── index.json          # Manifest of all memory entries
```

**Bootstrap:** If `memory/` doesn't exist, create it and the subdirectories before storing.

Each memory entry is a JSON file:
```json
{
  "id": "pat_001",
  "type": "pattern|decision|finding|context",
  "timestamp": "2026-01-12T10:30:00Z",
  "project": "automation-framework-example",
  "title": "Selector stability pattern",
  "content": "...",
  "tags": ["selectors", "page-objects", "ui-testing"],
  "source": "discussion|code|analysis"
}
```

## Instructions

### Query Mode (`/memory [question]`)

1. Parse the user's question to understand what they're looking for
2. Search memory entries by:
   - Title/content text match
   - Tag match
   - Type filter (decisions, patterns, etc.)
3. Return relevant entries with context
4. If nothing found, say so and suggest checking `docs/decision_log.md`

### Store Mode (`/memory store [content]`)

1. Ask for or infer:
   - Type (pattern, context, finding)
   - Title (short description)
   - Tags (for later retrieval)
   - ID prefix: `dec_`/`pat_`/`find_`/`ctx_` (must match type)
2. Create a new JSON file in the appropriate directory
3. Update `index.json`
4. Confirm storage with the entry ID

### List Mode (`/memory list [type]`)

1. Show all memory entries, optionally filtered by type
2. Display: ID, title, date, tags

## Common Tags for This Project

- `api-testing`, `ui-testing`, `bdd`, `behave`
- `page-objects`, `selectors`, `locators`
- `services`, `api-client`, `authentication`
- `fixtures`, `cleanup`, `test-data`
- `playwright`, `browser`, `headless`
- `flaky-tests`, `debugging`, `ci-cd`

## Examples

User: `/memory what pattern do we use for API response validation?`

Response: Search for "response" or "validation" in patterns. Return: "pat_001: ResponseValidator fluent pattern - Chain assertions with `.status(200).has_field('id').field_equals('name', 'Test')`"

User: `/memory store Always use data-testid attributes for stable selectors`

Response: "Storing as pattern. Title: 'Stable selector strategy'. Tags: [selectors, page-objects, ui-testing]. Confirm? (y/n)"

User: `/memory list patterns`

Response: List all entries in `memory/patterns/` directory with titles and dates.

# Test Review Checklist

Use this checklist when reviewing feature files and step definitions.

## Feature File Quality

### Structure
- [ ] Feature has clear description (As a... I want... So that...)
- [ ] Scenarios have descriptive, unique names
- [ ] Background used for common preconditions (not repeated in each scenario)
- [ ] Appropriate tags applied (@smoke, @regression, @api, @ui, @wip)

### Gherkin Quality
- [ ] Steps written in domain language, not implementation details
- [ ] No selectors, URLs, or technical details in feature files
- [ ] Given/When/Then used correctly (setup/action/assertion)
- [ ] Steps are potentially reusable across scenarios

### Test Design
- [ ] Each scenario tests ONE thing
- [ ] Scenarios are independent (can run in any order)
- [ ] Test data is realistic but obviously fake
- [ ] Negative cases covered where appropriate

## Step Definition Quality

### Organization
- [ ] Steps in appropriate file (api_steps.py, ui_steps.py, common_steps.py)
- [ ] No duplicate steps across files
- [ ] Shared steps use `@step` decorator
- [ ] Clear docstrings explaining what each step does

### Implementation
- [ ] Steps delegate to services/pages (no direct API/browser calls)
- [ ] Context used appropriately for sharing state
- [ ] Created resources tracked for cleanup
- [ ] Meaningful assertion messages

### Code Quality
- [ ] Type hints on parameters
- [ ] No hardcoded credentials or URLs
- [ ] Logging for debugging complex steps
- [ ] Error handling with clear messages

## Anti-Patterns to Flag

- [ ] No implementation details in feature files (selectors, endpoints)
- [ ] No hardcoded waits (`time.sleep`)
- [ ] No test interdependence
- [ ] No missing cleanup for created resources
- [ ] No duplicate test coverage

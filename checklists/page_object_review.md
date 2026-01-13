# Page Object Review Checklist

Use this checklist when reviewing page object classes.

## Structure

### Class Organization
- [ ] Extends `BasePage`
- [ ] Locators defined as class constants (SCREAMING_SNAKE_CASE)
- [ ] `url_path` property defined
- [ ] Clear section separation: Locators → Properties → Actions → Queries → Waits

### Naming Conventions
- [ ] Class name matches page purpose (e.g., `AdminPage`, `BookingPage`)
- [ ] Locator names describe the element (e.g., `USERNAME_INPUT`, `SUBMIT_BUTTON`)
- [ ] Method names are verb phrases for actions (`click_submit`, `fill_form`)
- [ ] Query methods use `get_*` or `is_*` prefix

## Locator Quality

### Stability
- [ ] Prefers `data-testid` attributes where available
- [ ] Uses stable attributes (id, name, role) over structure
- [ ] Avoids brittle selectors (nth-child, complex CSS paths)
- [ ] No dynamic IDs or classes that change on refresh

### Readability
- [ ] Locators are self-documenting
- [ ] Complex selectors have comments explaining them
- [ ] Related locators grouped together

## Method Quality

### Actions
- [ ] Actions return `self` for method chaining
- [ ] Actions have clear, single responsibility
- [ ] Waits included where elements load dynamically
- [ ] No hardcoded `time.sleep()` calls

### Queries
- [ ] Query methods return meaningful values (str, bool, list)
- [ ] Boolean queries named with `is_*` or `has_*`
- [ ] Text queries handle empty/missing elements gracefully

### Waits
- [ ] Explicit waits used for dynamic content
- [ ] Reasonable timeout values (not too short, not too long)
- [ ] Wait methods return `self` for chaining

## Code Quality

- [ ] Type hints on all method signatures
- [ ] Docstrings for public methods
- [ ] No business logic in page objects (just interactions)
- [ ] Uses inherited methods from `BasePage` where appropriate
- [ ] Logging for complex interactions

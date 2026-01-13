# Decision Log

Architectural and implementation decisions for the automation framework.

---

## 2026-01-12: Separate API and UI Test Targets
- **Decision:** Use different applications for API testing (restful-booker.herokuapp.com) and UI testing (automationintesting.online)
- **Context:** Need publicly accessible test targets that don't require authentication setup or account creation
- **Alternatives considered:**
  - Single application with both API and UI (couldn't find suitable public option)
  - Use automationintesting.online for both (API structure changed, returns 404s)
  - Mock servers (defeats purpose of demonstrating real integration)
- **Rationale:** Both applications are free, publicly accessible, and well-documented. The API is stable for CRUD demos. The UI shows realistic booking flows. Clear separation makes it obvious which tests target which system.
- **Decided by:** Collaborative (Claude + Human)
- **Affects:** `core/config.py`, `.env`, all feature files, documentation

---

## 2026-01-12: Singleton Pattern for Core Components
- **Decision:** Use singleton pattern for APIClient, Config, and BrowserFactory
- **Context:** Need to manage shared state (auth tokens, browser instances) across test scenarios without memory leaks
- **Alternatives considered:**
  - Create new instances per scenario (wasteful, connection overhead)
  - Dependency injection framework (overkill for test framework)
  - Global variables (no encapsulation, harder to test)
- **Rationale:** Singletons provide controlled access to shared resources, enable connection pooling, and make token management transparent. The pattern is well-understood and appropriate for test infrastructure.
- **Decided by:** Claude
- **Affects:** `core/api_client.py`, `core/browser_factory.py`, `core/config.py`

---

## 2026-01-12: Service Layer Returns (Response, Validator) Tuples
- **Decision:** API services return tuple of (Response, ResponseValidator) instead of just Response
- **Context:** Want fluent assertions without requiring step definitions to instantiate validators
- **Alternatives considered:**
  - Return only Response (steps create validator - more boilerplate)
  - Return only Validator (loses access to raw response)
  - Subclass Response with validation methods (couples concerns)
- **Rationale:** Tuple unpacking is Pythonic. Steps get both raw access and fluent validation. Pattern is consistent across all services.
- **Decided by:** Claude
- **Affects:** All files in `services/`, `steps/api_steps.py`, `steps/common_steps.py`

---

## 2026-01-12: Use @step Decorator for Shared Steps
- **Decision:** Steps that can be used with Given/When/Then use the `@step` decorator instead of specific `@given`/`@when`/`@then`
- **Context:** Some steps like "I am authenticated as admin" make sense in multiple contexts
- **Alternatives considered:**
  - Duplicate steps with different decorators (DRY violation)
  - Always use specific decorators (limits flexibility)
- **Rationale:** Behave's `@step` decorator registers the step for all keywords. Reduces duplication and allows natural language flexibility.
- **Decided by:** Claude
- **Affects:** `steps/common_steps.py`

---

## 2026-01-12: Tag WIP Tests Instead of Deleting
- **Decision:** Tests that don't work due to site changes are tagged `@wip` and skipped in CI
- **Context:** Admin page selectors broke when automationintesting.online was rebuilt
- **Alternatives considered:**
  - Delete broken tests (loses test coverage intent)
  - Comment out tests (invisible, easy to forget)
  - Fix immediately (time-consuming, site may change again)
- **Rationale:** `@wip` tag preserves the test intent, documents what needs fixing, and keeps CI green. Tests can be fixed when prioritized.
- **Decided by:** Collaborative
- **Affects:** `features/ui/admin.feature`, `features/ui/booking.feature`, `behave.ini`

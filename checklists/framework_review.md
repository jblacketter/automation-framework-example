# Framework Review Checklist

Use this checklist when reviewing core framework components.

## Architecture

### Design Patterns
- [ ] Singleton pattern implemented correctly (thread-safe if needed)
- [ ] Clear separation of concerns
- [ ] Dependencies injected or accessed via singletons
- [ ] No circular dependencies

### Configuration
- [ ] Environment variables used for configuration
- [ ] Sensible defaults provided
- [ ] Configuration documented in `.env.example`
- [ ] No hardcoded values that should be configurable

## Code Quality

### Type Safety
- [ ] Type hints on all public methods
- [ ] Return types specified
- [ ] Complex types use typing module (Optional, List, Dict)

### Documentation
- [ ] Module-level docstring explaining purpose
- [ ] Class docstrings describing responsibility
- [ ] Method docstrings for non-obvious behavior
- [ ] Examples in docstrings where helpful

### Error Handling
- [ ] Appropriate exceptions raised (not generic Exception)
- [ ] Errors logged with context
- [ ] Graceful degradation where possible
- [ ] Clear error messages for debugging

## Security

### Credentials
- [ ] No hardcoded passwords or tokens
- [ ] Credentials loaded from environment
- [ ] Sensitive data masked in logs
- [ ] No credentials in version control

### Input Validation
- [ ] User input validated before use
- [ ] SQL/command injection prevented
- [ ] Path traversal prevented

## Testing Considerations

### Testability
- [ ] Components can be mocked/stubbed
- [ ] No hidden dependencies
- [ ] State can be reset between tests

### Resource Management
- [ ] Resources properly cleaned up
- [ ] Connections closed/pooled appropriately
- [ ] Memory leaks prevented
- [ ] File handles closed

## CI/CD Compatibility

- [ ] No interactive prompts
- [ ] Headless mode supported
- [ ] Configurable timeouts
- [ ] Artifacts saved on failure (screenshots, logs)

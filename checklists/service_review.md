# Service Review Checklist

Use this checklist when reviewing API service classes.

## Structure

### Class Organization
- [ ] Single responsibility (one domain per service)
- [ ] Endpoint paths as class constants
- [ ] Uses `APIClient` singleton for requests
- [ ] Logger initialized for the service

### Method Signatures
- [ ] Returns `(Response, ResponseValidator)` tuple
- [ ] Type hints on parameters and return types
- [ ] Docstrings describing what the method does

## API Interaction

### Request Handling
- [ ] Uses appropriate HTTP method (GET, POST, PUT, DELETE, PATCH)
- [ ] Request body structured correctly
- [ ] Headers set appropriately (Content-Type, auth tokens)
- [ ] Query parameters passed correctly for GET requests

### Response Handling
- [ ] Returns raw Response for flexibility
- [ ] ResponseValidator created for fluent assertions
- [ ] No assumptions about response structure in service layer

### Authentication
- [ ] Auth-required endpoints check for token
- [ ] Token passed via appropriate mechanism (header, cookie)
- [ ] Clear error if auth missing when required

## Code Quality

### Error Handling
- [ ] Doesn't swallow exceptions silently
- [ ] Logs errors with context
- [ ] Allows caller to handle failures

### Logging
- [ ] Request details logged (method, endpoint)
- [ ] Sensitive data masked (passwords, tokens)
- [ ] Response status logged

### Maintainability
- [ ] No hardcoded URLs (uses config)
- [ ] No hardcoded credentials
- [ ] Related operations grouped logically
- [ ] Complex logic extracted to helper methods

## Anti-Patterns to Flag

- [ ] No business logic in services (that belongs in steps)
- [ ] No direct `requests` calls (use APIClient)
- [ ] No response parsing in service layer
- [ ] No hardcoded test data

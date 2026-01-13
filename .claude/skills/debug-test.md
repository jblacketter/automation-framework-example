# Debug Test Skill

## Description
Debug failing tests and troubleshoot issues.

## Usage
Use this skill when tests are failing and the user needs help debugging.

## Commands

### Run Single Scenario with Verbose Output
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
behave features/path/to/file.feature:LINE_NUMBER --no-capture
```

### Run with Full Traceback
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
behave --tags="@TAG" --no-capture --verbose
```

### Run UI Tests in Headed Mode (See Browser)
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
HEADLESS=false SLOW_MO=500 behave features/ui/ --no-capture
```

### Check Step Definition Matching
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
behave --dry-run features/path/to/file.feature
```

### View Screenshots from Failed Tests
```bash
ls -la ~/projects/automation-framework-example/reports/screenshots/
open ~/projects/automation-framework-example/reports/screenshots/
```

## Common Issues

### Step Not Found
- Check step text matches exactly (including quotes, spacing)
- Verify step is imported in the correct file
- Use `@step` decorator for steps used with Given/When/Then

### Element Not Found (UI)
- Check selector is correct
- Add explicit wait: `wait_for_element(selector)`
- Take screenshot to see current state
- Run in headed mode to observe

### API Request Failed
- Check BASE_URL and API_BASE_URL in .env
- Verify authentication is set up
- Check request/response logs
- Verify endpoint path is correct

### Authentication Issues
- Verify ADMIN_USERNAME and ADMIN_PASSWORD in .env
- Check token is being set: `context.auth_token`
- Clear tokens between scenarios: `APIClient().clear_token()`

## Debugging Tips

1. **Add logging**: Use `self.logger.info("message")` in page objects/services
2. **Take screenshots**: Call `context.browser_factory.take_screenshot("debug")`
3. **Print response**: Add `print(context.response.text)` in step
4. **Check API logs**: Look for Request/Response lines in output

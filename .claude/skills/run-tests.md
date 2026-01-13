# Run Tests Skill

## Description
Run Behave tests with various configurations.

## Usage
Use this skill when the user wants to run tests.

## Commands

### Run All Smoke Tests
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
behave --tags="@smoke" --no-capture
```

### Run API Tests Only
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
behave features/api/ --no-capture
```

### Run UI Tests Only
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
behave features/ui/ --no-capture
```

### Run Tests by Tag
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
behave --tags="@TAG_NAME" --no-capture
```

### Run Tests with HTML Report
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
behave --format=html --outfile=reports/report.html
```

### Run UI Tests in Headed Mode
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
HEADLESS=false behave features/ui/ --no-capture
```

## Available Tags
- `@smoke` - Smoke tests
- `@api` - API tests
- `@ui` - UI tests
- `@auth` - Authentication tests
- `@bookings` - Booking tests
- `@wip` - Work in progress (excluded by default)
- `@negative` - Negative test cases

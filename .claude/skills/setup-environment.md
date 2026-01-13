# Setup Environment Skill

## Description
Set up the development environment for the automation framework.

## Usage
Use this skill when the user needs to set up or reset their environment.

## Commands

### Full Setup (New Environment)
```bash
cd ~/projects/automation-framework-example

# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment file
cp .env.example .env

echo "Setup complete! Run 'behave --tags=@smoke' to verify."
```

### Activate Existing Environment
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
```

### Update Dependencies
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Install All Playwright Browsers
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
playwright install
```

### Verify Installation
```bash
cd ~/projects/automation-framework-example
source .venv/bin/activate
python -c "from core import Config, APIClient; print('Core modules OK')"
python -c "from services import AuthService, BookingService; print('Services OK')"
python -c "from pages import HomePage, AdminPage; print('Pages OK')"
behave --dry-run --tags="@smoke"
```

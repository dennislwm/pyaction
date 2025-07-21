# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based financial monitoring system that:
- Downloads stock data for XLU, VTI, and SPY from Yahoo Finance
- Calculates technical indicators (ROC, DBS signals) to monitor utilities vs broad market trends
- Generates email alerts when trend shifts occur
- Creates and updates charts as PNG images
- Runs automatically via GitHub Actions on a daily schedule

## Core Architecture

### Main Components
- `pymonitor.py`: Core application with financial data analysis and alerting logic
- `test_pymonitor.py`: Test suite for data processing functions
- `requirements.txt`: Python dependencies including pandas, yfinance, ta (technical analysis)
- `Dockerfile`: Container setup for GitHub Actions execution
- `.github/workflows/pymonitor.yml`: Automated daily execution workflow

### Key Dependencies
- **pyfxgit.ChartCls**: Custom charting library for financial data visualization
- **yfinance**: Yahoo Finance data retrieval
- **ta**: Technical analysis indicators (ROC - Rate of Change)
- **pandas**: Data manipulation and analysis
- **ruamel.yaml**: Configuration file handling

### Data Flow
1. Download 52 weeks of stock data for XLU, VTI, SPY
2. Calculate XLU/VTI ratio (utilities vs broad market)
3. Apply ROC indicator (20-period) to ratio data
4. Generate DBS signal from ROC values (-4 to +4 range)
5. Calculate moving average and detect trend shifts
6. Send email alerts on trend changes (BULLISH/BEARISH/NEUTRAL)
7. Generate and save chart as `_ChartC_0.1_Dbs.png`

## Development Commands

### Running the Application
```bash
# Run the monitoring system
python3 pymonitor.py

# Run with email notifications (requires Gmail configuration)
INPUT_GMAIL="your-email@gmail.com" INPUT_GMAIL_APP_PASSWORD="your-app-password" python3 pymonitor.py
```

### Testing
```bash
# Run unit tests
python3 test_pymonitor.py

# Run specific test function
python3 -c "from test_pymonitor import test_all; test_all()"
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific dependencies for development
pip install numpy pandas pyfxgit ruamel.yaml ta yfinance
```

### Code Quality
```bash
# Lint with flake8 (matches GitHub Actions workflow)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Check Python syntax
python3 -m py_compile pymonitor.py test_pymonitor.py
```

### Docker Operations
```bash
# Build container image
docker build -t pymonitor .

# Run monitoring system in container
docker run pymonitor pymonitor.py

# Run with environment variables for email
docker run -e INPUT_GMAIL="email@gmail.com" -e INPUT_GMAIL_APP_PASSWORD="password" pymonitor pymonitor.py
```

## Configuration

### Configuration Priority
The application supports configuration via (in order of precedence):
1. `config.yaml` file (highest priority)
2. Environment variables: `INPUT_GMAIL`, `INPUT_GMAIL_APP_PASSWORD`

### Email Configuration
Gmail app passwords are required for email functionality:
- Setup: https://myaccount.google.com/apppasswords
- Environment variables used in GitHub Actions for automated notifications
- Local development can use `config.yaml` file:

```yaml
pymonitor:
  gmail: "your-email@gmail.com"
  gmail_app_password: "your-16-character-app-password"
```

### Trading Signal Parameters
Key constants defined in `pymonitor.py`:
- `DBS_LIMIT = 3.75`: Threshold for bullish/bearish signals
- `DBS_PERIOD = 7`: Moving average period (consider 7-12 range)
- Signal states: `NEUTRAL`, `BULLISH`, `BEARISH`

## Signal Logic

- **DBS_LIMIT**: 3.75 (threshold for trend signals)
- **DBS_PERIOD**: 7 (moving average period)
- **Signals**: BULLISH (≤ -3.75), BEARISH (≥ 3.75), NEUTRAL (between thresholds)
- **Alerts**: Only sent on trend changes, not when maintaining same signal

## GitHub Actions

### Automated Workflow (`pymonitor.yml`)
The workflow runs daily at 00:01 UTC (`cron: '1 0 * * *'`) and:
1. Sets up Python 3.8 environment on Ubuntu
2. Installs dependencies (`pip`, `flake8`, `requirements.txt`)
3. Runs code quality checks with flake8
4. Executes the monitoring script with GitHub secrets for email
5. Commits and pushes any chart updates to the repository

### Manual Triggers
- **Push to repository**: Triggers workflow on any push
- **Manual dispatch**: `workflow_dispatch` allows manual execution
- **Scheduled**: Daily execution at 00:01 UTC (08:01 Singapore time)

### Environment Variables in Actions
```yaml
env:
  INPUT_GMAIL: ${{ secrets.GMAIL }}
  INPUT_GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
```

## Output Files

### Generated Assets
- `_ChartC_0.1_Dbs.png`: Generated chart showing SPY price with DBS indicators and trend signals
- Chart automatically updated and committed by GitHub Actions workflow
- Chart linked in email notifications for trend shift alerts

### Chart Components
- **Main plot**: SPY price data with candlestick representation
- **Upper oscillator**: DbsMa (moving average) with ±3.75 threshold lines
- **Lower oscillator**: Raw Dbs signal values with ±3 bounds
- **Color coding**: Red spans for bearish periods, green spans for bullish periods

## GitHub CLI Integration

The project supports GitHub CLI (`gh`) for repository management and automation:

### Common GitHub CLI Commands

```bash
# Repository management
gh repo view                    # View current repository details
gh repo clone <repo>           # Clone a repository
gh repo create <name>          # Create new repository

# Workflow management  
gh workflow list               # List all workflows
gh workflow view pymonitor     # View pymonitor workflow details
gh workflow run pymonitor      # Trigger workflow manually
gh run list                    # List recent workflow runs
gh run view <run-id>          # View specific run details

# Pull request management
gh pr create                   # Create new pull request
gh pr list                     # List pull requests
gh pr view <number>           # View PR details
gh pr checkout <number>       # Checkout PR locally

# Issue management
gh issue create               # Create new issue
gh issue list                 # List issues
gh issue view <number>        # View issue details

# Authentication
gh auth login                 # Login to GitHub
gh auth status               # Check authentication status
```

### Workflow Integration

**Manual workflow execution**:
```bash
# Trigger pymonitor workflow manually
gh workflow run pymonitor

# View recent pymonitor runs
gh run list --workflow=pymonitor

# View specific run details with logs
gh run view <run-id> --log

# Check workflow status
gh workflow view pymonitor
```

**Monitoring workflow runs**:
```bash
# List recent runs with status
gh run list --limit 10

# Watch a running workflow
gh run watch <run-id>

# Download run artifacts (if any)
gh run download <run-id>
```

## Error Handling

### Email Notifications
- Silent failure if no Gmail credentials configured (prints no email sent)
- Only sends alerts on trend changes, not recurring signals
- Includes chart attachment and repository links

### Data Processing
- Error handling for Yahoo Finance API failures
- Graceful degradation if chart generation fails
- Maintains data integrity across market holidays and weekends
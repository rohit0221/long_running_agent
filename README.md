# Long-Running Test Coverage Agent - Quick Start

## Current Baseline Coverage (After Reset)

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| `calculator.py` | 47% | subtract, multiply, divide, power |
| `analytics.py` | 75% | get_events, clear |
| `helpers.py` | 43% | parse_int |
| `validators.py` | 64% | validate_phone |
| `models.py` | 88% | Item class (no tests yet) |
| **Overall** | **70%** | **21 uncovered statements** |

## How to Run the Agent

### 1. Activate the virtual environment
```powershell
cd C:\GitHub\long_running_agent
.\.venv\Scripts\activate
```

### 2. Run a single session
```powershell
python -m harness.run_session --session-id 1
```

### 3. Run multiple sessions (e.g., 1-10)
```powershell
for ($i = 1; $i -le 10; $i++) {
    python -m harness.run_session --session-id $i
}
```

### 4. Inspect the results

After each session, check:
- **`coverage_plan.json`** - per-module coverage and status
- **`coverage_history.json`** - chronological session history
- **`agent_progress.log`** - detailed human-readable log
- **`target_repo/tests/`** - the generated/updated test files

## What the Agent Does

1. **Health check** - runs tests to ensure the repo is not broken
2. **Select target** - picks the module with lowest coverage
3. **Generate tests** - calls OpenAI gpt-5-nano to create comprehensive tests
4. **Backup** - saves the current test file as `*.bak`
5. **Apply changes** - writes the new test file
6. **Verify** - re-runs tests
   - ✅ **Success** → keeps changes, updates coverage, deletes backup
   - ❌ **Failure** → restores backup, logs `REVERTED`

## Reset to Baseline (Start Fresh)

```powershell
# Delete all agent-generated artifacts
Remove-Item -Force -ErrorAction SilentlyContinue `
    coverage_plan.json, coverage_history.json, agent_progress.log, coverage.xml, .coverage

# Delete any backup files
Get-ChildItem -Path target_repo\tests -Filter *.bak -Recurse | Remove-Item -Force

# The minimal test files are already in place - you're ready to run!
```

## Expected Behavior

Over 5-10 sessions you should see:
- Coverage increasing from ~70% toward 95%+
- Modules moving from `pending` → `in_progress` → `done`
- Some sessions may be `REVERTED` (LLM generates broken tests)
- The repo is **never left in a broken state** (backup/restore mechanism)

## Troubleshooting

**Import Error**: Always run from the repository root using `python -m harness.run_session`, not `python harness\run_session.py`

**No modules to improve**: All modules have reached their target coverage. Check `coverage_plan.json` to see the status.

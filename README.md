# Automation Audit - Playwright Tests

Playwright + pytest tests for the "Automation Audit" section of Guardrails
(Config > Automation > Guardrails):

- Emails patterns to unassign
- Subjects
- Words in User Message
- Words in Assistant's Reply

15 automated cases out of 83 planned - see `Automation_Audit_Test_Cases.xlsx`
for the full matrix and `Automation_Audit_Test_Plan.docx` for the test plan.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Auth

The app uses Google SSO, which blocks automated logins. To run against the
real environment, open a Chrome window with remote debugging on, log in by
hand, then point the tests at that window instead of a fresh browser:

```bash
open -a "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-debug-profile"
# log in manually in the window that opens, then:
export GUARDRAILS_CDP_URL="http://localhost:9222"
```

## Run

```bash
pytest -m smoke   # fast pass
pytest             # full suite
```

## Notes

- Tests always end by discarding their changes (never Save), so they can
  run repeatedly without leaving test data behind.
- Two tests are marked `xfail` - they document two real bugs found while
  exploring the feature (a stale-input issue after a rejected duplicate,
  and a missing accessible name on the remove button), rather than being
  skipped or deleted.
- Verified passing both against a local fixture and the live DEV app.

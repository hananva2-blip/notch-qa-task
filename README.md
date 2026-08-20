# Automation Audit - automated test subset

Playwright + pytest implementation of a subset of the test cases in
`Automation_Audit_Test_Cases.xlsx` (column `Automated = Y`), covering the
"Automation Audit" block of Config > Automation > Guardrails:

- Emails patterns to unassign
- Subjects
- Words in User Message
- Words in Assistant's Reply

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

If the target environment requires authentication, capture a storage state
once (log in manually, then save the session) and point the suite at it:

```bash
playwright codegen --save-storage=state.json https://guardio.app.getnotch.dev
export GUARDRAILS_STORAGE_STATE=$(pwd)/state.json
```

## Run

```bash
export GUARDRAILS_BASE_URL="https://guardio.app.getnotch.dev"   # optional, this is the default
export GUARDRAILS_VERSION="NM-17AUGUST-143816"                   # optional, this is the default
pytest -m smoke                 # fast smoke pass
pytest                          # full automated subset
pytest -m "not a11y and not validation"   # e.g. skip the two known-defect (xfail) cases
```

## Execution status

The DOM locator strategy in `pages/guardrails_page.py` was built and verified
directly against the real page (live element inspection - heading nesting
depth, the textarea + button structure, the missing aria-label, the
duplicate-input defect - all confirmed by hand first).

Full end-to-end execution of `pytest`, however, was run and verified green
against a local static fixture (`mock_site/`) that reproduces the real DOM
shape and the two known defects, **not against the live
guardio.app.getnotch.dev**: this was written and validated from a sandboxed
environment whose outbound network only reaches an allowlist, which the
target app is not on. Result of the last run against the fixture:

```
13 passed, 2 xfailed in ~8s
```

Before relying on this in CI, run it once for real from a machine that can
reach the target app (e.g. `pytest` with `GUARDRAILS_BASE_URL` pointed at
your actual environment) - the locators are expected to hold since they're
based on the real DOM, but an app this actively developed can always shift
underneath.

## What's covered here vs. the full matrix

This is a proof-of-implementation subset (15 of 68 planned cases), chosen to
span every suite in the plan rather than to exhaustively implement one suite:
smoke, functional, validation/boundary, UI, state management, regression and
accessibility. Integration (does a deployed rule actually unassign a real
conversation), performance, security and cross-browser cases are documented
in the matrix but need a seeded test conversation / staging pipeline and a
non-shared environment to automate safely - see the "Assumptions & Risks"
section of the test plan.

## Design notes

- **No stable test hooks in the app.** The chip-list component exposes no
  `data-testid` and its CSS classes are auto-generated (styled-components
  hashes) that are not safe to hardcode. `pages/guardrails_page.py` locates
  each field by its own heading text instead. Recommend the engineering team
  add `data-testid`s (and `aria-label`s - see the A11Y-03 case) to make this
  more robust and readable.
- **Every mutating test ends by discarding**, never saving, so the suite can
  run repeatedly against a shared draft without accumulating test data. A
  `conftest.py` fixture also discards automatically if a test fails midway.
- **Two tests are intentionally `xfail`** (`VAL-06`, `A11Y-03`): they encode
  the *correct* expected behavior for two defects found during manual
  exploration, so they read as an expected failure today and flip to a
  visible pass once the underlying bug is fixed, rather than being silently
  skipped or deleted.

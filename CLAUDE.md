# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is
A QA practice workspace. It holds manual test cases, Python UI and API automation (pytest + Playwright + requests), bug reports, and run reports for public practice sites. The user is learning QA and delegates testing work to Claude. Every site in `SITES.md` is built for testing practice. Do not test any other site unless the user says they own it or have permission to test it.

## Commands
Python 3.12 is installed for the user at `%LOCALAPPDATA%\Programs\Python\Python312` (it is not on PATH; `py` is). Everything runs from the project venv in `.venv`.
- Setup: `py -3.12 -m venv .venv`, then `.venv\Scripts\python -m pip install -r requirements.txt` and `.venv\Scripts\python -m playwright install chromium`
- `.venv\Scripts\python -m pytest`: run all tests (Chromium only)
- `.venv\Scripts\python -m pytest tests/test_saucedemo.py`: run one site
- `.venv\Scripts\python -m pytest -k sd_login_003`: run a single case, or a group by ID prefix (e.g. `-k rb_`). `-k` is case-insensitive
- `... -m pytest --headed --slowmo 500`: watch the browser
- HTML report: `report/index.html`. Failures keep a screenshot, video and trace under `test-results/`
- `.venv\Scripts\python -m playwright show-trace <path>/trace.zip`: step through a failed test
- `.venv\Scripts\python -m playwright codegen --target python-pytest <url>`: record actions to discover locators

Settings live in `pytest.ini`. There is no build or lint step.

## Architecture
- **One site, four artifacts, all linked by case ID.** For a site prefix like `SD`, the files are: `test-cases/<site>.md` (manual cases), `tests/test_<site>.py` (one test function per case, named `test_<id>_<title>` in snake_case, e.g. `test_sd_login_003_wrong_password`), `bug-reports/<PREFIX>-BUG-NNN.md`, and `test-runs/YYYY-MM-DD-<site>.md`. When a case changes, keep all of these in sync. Templates are `bug-reports/_TEMPLATE.md` and `test-runs/_TEMPLATE.md`.
- **Case ID format:** `<PREFIX>-<AREA>-<NNN>`. Site prefixes are in `SITES.md` (SD = SauceDemo, TI = The Internet, RB = Restful-Booker).
- **UI tests** use pytest-playwright's `page` fixture (sync API). There is no global base URL: `test_the_internet.py` overrides the `browser_context_args` fixture to set `base_url`, and `test_saucedemo.py` uses a `URL` constant. `tests/conftest.py` sets the test ID attribute to `data-test`, so `get_by_test_id()` matches `data-test="..."`.
- **API tests** (`test_restful_booker.py`) use the `requests` library through an `api` fixture, not a browser. A write needs the header `Cookie: token=<token>` from `POST /auth`. The API is shared by everyone, so every test creates its own booking with random names and never depends on existing data.
- **Known defects** are reproduced with `@pytest.mark.xfail(reason="<BUG-ID>: ...")`. They show as XFAIL while the bug exists. `xfail_strict = true` in `pytest.ini`, so if one starts passing it is reported as FAILED ("XPASS(strict)"): either the bug was fixed or the test is broken. Investigate before removing the marker.

## Test-writing rules learned from this repo
- **Guard against empty matches.** Before asserting on a collection, check its count (`expect(locator).to_have_count(n)`). SD-PROB-001 once passed silently because a stale CSS locator matched 0 images.
- **Confirm the failure reason for expected-fail tests** outside Playwright (curl, DevTools) before filing a bug. An xfail test can fail for the wrong reason. `pytest --runxfail` shows the real failure.
- **App bug or test bug?** Decide before reporting. TI-FORM-003 failed because pressing Enter submitted the form and reloaded the page; the site itself was fine.
- **API tests check side effects, not only status codes.** For example, after a DELETE, a GET should return 404.
- **Locators:** use `get_by_role` / `get_by_label` / `get_by_placeholder` first, then `get_by_test_id`. Never use `wait_for_timeout()` or `time.sleep()`. Rely on web-first `expect`.

## Hooks
`.claude/settings.json` runs Python hooks from `.claude/hooks/` (through `run.sh`, which uses the `.venv` Python): `allowed_sites.py` blocks test traffic to sites not in `SITES.md`, `block_fixed_sleeps.py` rejects fixed sleeps in `tests/`, and `check_tests.py` runs `pytest --collect-only` after a test file is edited, `lint_and_typecheck.py` runs ruff (`ruff.toml`) and mypy (`mypy.ini`) on every edited `.py` file, and `run_tests_on_stop.py` (Stop hook) runs the full suite before a turn ends whenever `.py` files or `pytest.ini` have uncommitted changes, blocking the stop on failure (~3 min). If a hook blocks you, fix the cause; don't work around it.

## The testing loop for a new site or feature
Explore (manually, or with the claude-in-chrome skill) → write cases → automate → run → write the run report and bug reports → commit.

## Git
The remote is the private repo https://github.com/mindful321/qa-practice, branch `main`. `gh` is at `C:\Program Files\GitHub CLI\gh.exe` and is already logged in. Commit only when the user asks.

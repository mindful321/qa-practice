# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is
A QA practice workspace. It holds manual test cases, Playwright UI and API automation, bug reports, and run reports for public practice sites. The user is learning QA and delegates testing work to Claude. Every site in `SITES.md` is built for testing practice. Do not test any other site unless the user says they own it or have permission to test it.

## Commands
Node is installed at `C:\Program Files\nodejs`. If `npm` or `npx` isn't found in a fresh shell, prepend that folder to PATH.
- `npm test`: run all specs (Chromium only)
- `npx playwright test tests/saucedemo.spec.ts`: run one site
- `npx playwright test -g "SD-LOGIN-003"`: run a single case, or a group by ID prefix (e.g. `-g "RB-"`)
- `npm run test:headed` / `npm run test:ui`: watch the browser / interactive debugging
- `npm run report`: open the HTML report. Failures keep a screenshot, video and trace under `test-results/`
- `npx playwright show-trace <path>/trace.zip`: step through a failed test
- `npx playwright codegen <url>`: record actions to discover locators

There is no build or lint step. TypeScript is run directly by Playwright.

## Architecture
- **One site, four artifacts, all linked by case ID.** For a site prefix like `SD`, the files are: `test-cases/<site>.md` (manual cases), `tests/<site>.spec.ts` (one `test()` per case, named `<ID> <title>`), `bug-reports/<PREFIX>-BUG-NNN.md`, and `test-runs/YYYY-MM-DD-<site>.md`. When a case changes, keep all of these in sync. Templates are `bug-reports/_TEMPLATE.md` and `test-runs/_TEMPLATE.md`.
- **Case ID format:** `<PREFIX>-<AREA>-<NNN>`. Site prefixes are in `SITES.md` (SD = SauceDemo, TI = The Internet, RB = Restful-Booker).
- **`playwright.config.ts` has no global `baseURL`.** Each spec sets its own with `test.use({ baseURL })`, except `saucedemo.spec.ts`, which uses a `URL` constant. `testIdAttribute` is `data-test`, so `getByTestId()` matches `data-test="..."`.
- **API tests** (`restful-booker.spec.ts`) use Playwright's `request` fixture, not a browser. A write needs the header `Cookie: token=<token>` from `POST /auth`. The API is shared by everyone, so every test creates its own booking with random names and never depends on existing data.
- **Known defects** are reproduced with `test.fail(true, '<BUG-ID>: ...')`. They count as passing while the bug exists. If one starts reporting "Expected to fail, but passed", either the bug was fixed or the test is broken. Investigate before removing the annotation.

## Test-writing rules learned from this repo
- **Guard against empty matches.** Before asserting on a collection, check its count (`toHaveCount(n)`). SD-PROB-001 once passed silently because a stale CSS locator matched 0 images.
- **Confirm the failure reason for expected-fail tests** outside Playwright (curl, DevTools) before filing a bug. A `test.fail()` test can fail for the wrong reason.
- **App bug or test bug?** Decide before reporting. TI-FORM-003 failed because pressing Enter submitted the form and reloaded the page; the site itself was fine.
- **API tests check side effects, not only status codes.** For example, after a DELETE, a GET should return 404.
- **Locators:** use `getByRole` / `getByLabel` / `getByPlaceholder` first, then `getByTestId`. Never use `waitForTimeout`. Rely on web-first `expect`.

## The testing loop for a new site or feature
Explore (manually, or with the claude-in-chrome skill) → write cases → automate → run → write the run report and bug reports → commit.

## Git
The remote is the private repo https://github.com/mindful321/qa-practice, branch `main`. `gh` is at `C:\Program Files\GitHub CLI\gh.exe` and is already logged in. Commit only when the user asks.

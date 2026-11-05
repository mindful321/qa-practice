# QA Practice

[![Playwright tests](https://github.com/mindful321/qa-practice/actions/workflows/playwright.yml/badge.svg)](https://github.com/mindful321/qa-practice/actions/workflows/playwright.yml)

This repo is my QA portfolio. It holds manual test cases, Playwright UI and API automation, bug reports and test run reports for public sites built for testing practice. I do the work together with an AI agent (Claude Code), and the repo has guardrails that keep the agent to the same standards I follow.

## What's covered

| Site | Type | Automated cases | Bugs found |
|---|---|---|---|
| [SauceDemo](https://www.saucedemo.com) | UI: login, sorting, cart, checkout | 16 | [SD-BUG-001](bug-reports/SD-BUG-001.md) |
| [The Internet](https://the-internet.herokuapp.com) | UI: auth, forms, alerts, frames, dynamic content, drag and drop | 20 | [TI-BUG-001](bug-reports/TI-BUG-001.md) |
| [Restful-Booker](https://restful-booker.herokuapp.com) | REST API: auth, CRUD, negative cases | 14 | [RB-BUG-001](bug-reports/RB-BUG-001.md), [RB-BUG-002](bug-reports/RB-BUG-002.md), [RB-BUG-003](bug-reports/RB-BUG-003.md) |

Some highlights from the bug reports:
- `POST /auth` returns **200 OK** for wrong credentials instead of 401 ([RB-BUG-001](bug-reports/RB-BUG-001.md)).
- A booking with missing fields returns **500** instead of 400 ([RB-BUG-002](bug-reports/RB-BUG-002.md)).
- `DELETE /booking/{id}` returns **201 Created** ([RB-BUG-003](bug-reports/RB-BUG-003.md)).

## How the repo is organized

Every test case has an ID like `SD-LOGIN-003` (site, area, number), and the same ID links four kinds of files:

| Folder | Contents |
|---|---|
| [`test-cases/`](test-cases/) | Manual test cases: steps, test data, expected results |
| [`tests/`](tests/) | Playwright specs, one `test()` per case, named `<ID> <title>` |
| [`bug-reports/`](bug-reports/) | One report per defect, with severity, priority, steps and evidence |
| [`test-runs/`](test-runs/) | Dated run reports with pass/fail per case |

[`SITES.md`](SITES.md) lists every practice site and its prefix.

## Running the tests

```bash
npm ci
npx playwright install chromium
npm test                                   # all specs
npx playwright test -g "SD-LOGIN-003"      # one case
npx playwright test -g "RB-"               # one site, by ID prefix
npm run report                             # open the HTML report
```

## Approach

- **Known defects stay in the suite.** A test that reproduces a confirmed bug is marked `test.fail(true, '<BUG-ID>: ...')`. It passes while the bug exists. If the bug gets fixed, Playwright reports "Expected to fail, but passed", so the change gets noticed.
- **API tests check side effects, not only status codes.** For example, after a DELETE the test checks that a GET returns 404.
- **API tests are independent.** The Restful-Booker API is shared by everyone, so each test creates its own booking with random data and never relies on existing records.
- **Locators follow Playwright's priority:** `getByRole`, `getByLabel` and `getByPlaceholder` first, then `getByTestId`. No fixed sleeps: assertions wait for conditions.
- **App bug or test bug?** That gets decided before filing. Each failure's cause is confirmed outside Playwright (curl, DevTools) before a bug report is written.

## CI

[GitHub Actions](.github/workflows/playwright.yml) runs the whole suite in Chromium on every push and pull request to `main`. The HTML report is uploaded as an artifact on every run, and traces and screenshots are uploaded when a test fails.

## AI agent guardrails

[`CLAUDE.md`](CLAUDE.md) gives the agent the repo's conventions. [Claude Code hooks](https://docs.claude.com/en/docs/claude-code/hooks) in [`.claude/settings.json`](.claude/settings.json) enforce the most important ones automatically, so they don't depend on the agent remembering:

| Hook | When it runs | What it does |
|---|---|---|
| [`allowed-sites.js`](.claude/hooks/allowed-sites.js) | Before shell commands and browser navigation | Blocks `curl`, `Invoke-WebRequest`, `playwright codegen` and browser visits to any site not listed in `SITES.md`, so the agent only tests sites built for practice |
| [`block-wait-for-timeout.js`](.claude/hooks/block-wait-for-timeout.js) | Before a file in `tests/` is edited | Rejects any edit that adds `waitForTimeout()`, the main cause of slow, flaky tests |
| [`check-spec.js`](.claude/hooks/check-spec.js) | After a `*.spec.ts` file is edited | Runs `playwright test --list` on the file, which catches syntax errors and duplicate test names in about a second |

The repo also defines a read-only [code-reviewer agent](.claude/agents/code-reviewer.md) that checks specs for weak assertions, flaky patterns, and mismatches with the manual cases.

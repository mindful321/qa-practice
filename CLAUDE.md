# QA Practice Workspace

This workspace is for practicing website testing. Every site listed in `SITES.md` is a public site built for testing practice. Do not test any other site unless the user says they own it or have permission to test it.

## The testing loop (repeat it for each site or feature)
1. **Explore.** Click through the feature, either manually or with the claude-in-chrome skill. Write down the flows, inputs, and rules.
2. **Write test cases.** Put them in `test-cases/<site>.md` using the template below. Cover positive, negative, boundary, and UI checks.
3. **Automate.** Write the specs in `tests/<site>.spec.ts`. Use one `test()` per test case, and start each test name with the case ID.
4. **Execute.** Run `npx playwright test tests/<site>.spec.ts`.
5. **Report.** Write the run results to `test-runs/YYYY-MM-DD-<site>.md`. Create one bug report per defect in `bug-reports/<SITE>-BUG-NNN.md`.

## Conventions
- **Case IDs:** `<SITE>-<AREA>-<NNN>`, e.g. `SD-LOGIN-003`. Site prefixes are listed in `SITES.md`.
- **Locators:** in order of preference, use `getByRole`, `getByLabel`, `getByPlaceholder`, then `getByTestId` (this reads `data-test`). Avoid CSS/XPath chains.
- **Waits:** never use `waitForTimeout`. Rely on auto-waiting and web-first assertions (`await expect(...)`).
- **Isolation:** each test must be able to run on its own. Don't share state between tests.
- **Known bugs:** mark a test that reproduces a known defect with `test.fail()` and name its bug ID in a comment. The suite stays green, and Playwright warns you if the bug ever gets fixed.
- **Priority:** P1 = blocks the core flow, P2 = important, P3 = minor or cosmetic.
- **Severity (bugs):** Critical / Major / Minor / Trivial.

## Commands
- `npm test`: run everything
- `npx playwright test tests/saucedemo.spec.ts --headed`: watch the browser
- `npx playwright test -g "SD-LOGIN"`: run cases by ID prefix
- `npm run test:ui`: interactive UI mode
- `npm run report`: open the HTML report (it includes screenshots and traces of failures)
- `npx playwright codegen <url>`: record clicks and generate locators

## Templates

### Test case
```
### <ID>: <Title>
- **Priority:** P1/P2/P3
- **Type:** Positive / Negative / Boundary / UI
- **Preconditions:** ...
- **Test data:** ...
- **Steps:**
  1. ...
- **Expected result:** ...
- **Automated:** yes (tests/<file>) / no
```

### Bug report: see `bug-reports/_TEMPLATE.md`
### Test run report: see `test-runs/_TEMPLATE.md`

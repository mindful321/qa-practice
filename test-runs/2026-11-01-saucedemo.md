# Test Run: SauceDemo, 2026-11-01

- **URL:** https://www.saucedemo.com
- **Browser/OS:** Chromium (Playwright 1.x), Windows 11 Pro
- **Tester:** Claude
- **Scope:** Login, sorting, cart, checkout, logout, problem_user defects

## Summary
| Total | Passed | Failed | Blocked | Known-bug (expected fail) |
|---|---|---|---|---|
| 16 | 14 | 0 | 0 | 2 |

## Results
| ID | Title | Result | Bug | Notes |
|---|---|---|---|---|
| SD-LOGIN-001 | Valid login | Pass | | |
| SD-LOGIN-002 | Locked-out user | Pass | | |
| SD-LOGIN-003 | Wrong password | Pass | | |
| SD-LOGIN-004 | Empty username | Pass | | |
| SD-LOGIN-005 | Empty password | Pass | | |
| SD-LOGIN-006 | Inventory protected | Pass | | |
| SD-SORT-001 | Price low to high | Pass | | |
| SD-SORT-002 | Name Z to A | Pass | | |
| SD-CART-001 | Add updates badge | Pass | | |
| SD-CART-002 | Remove clears badge | Pass | | |
| SD-CHK-001 | End-to-end purchase | Pass | | Totals $39.98 / $3.20 / $43.18 |
| SD-CHK-002 | First name required | Pass | | |
| SD-CHK-003 | Postal code required | Pass | | |
| SD-SESS-001 | Logout | Pass | | |
| SD-PROB-001 | Images unique | Fail (expected) | SD-BUG-001 | Every image is sl-404.jpg |
| SD-PROB-002 | Last name accepts input | Fail (expected) | (to be logged) | |

## Lessons from this run
- On the first run, SD-PROB-001 passed even though the bug was present. Its CSS locator matched 0 images, and an empty list counts as "all unique". The fix was to assert the element count (`toHaveCount(6)`) before checking anything else. **Lesson: a test that finds nothing can pass silently. Always assert that you found what you're checking.**

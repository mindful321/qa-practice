# SD-BUG-001: All products show the same image for problem_user

| Field | Value |
|---|---|
| Severity | Major |
| Priority | P2 |
| Environment | Chromium (Playwright), Windows 11, https://www.saucedemo.com |
| Test case | SD-PROB-001 |
| Status | Confirmed (known defect on this practice site) |
| Reported | 2026-11-01 |

## Preconditions
User `problem_user` / `secret_sauce`.

## Steps to reproduce
1. Open https://www.saucedemo.com.
2. Log in as `problem_user` / `secret_sauce`.
3. Look at the product images on the Products page.

## Expected result
Each of the 6 products shows its own product photo (backpack, bike light, etc.).

## Actual result
All 6 products show the same placeholder image of a dog, so users can't tell the products apart by their pictures.

## Evidence
Automated check SD-PROB-001 collects the `src` of every inventory image and finds only 1 unique value instead of 6.

## Notes
Happens every time (100%). It does not happen for `standard_user`.

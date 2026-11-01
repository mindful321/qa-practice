# TI-BUG-001: Two of the three images on /broken_images fail to load (404)

| Field | Value |
|---|---|
| Severity | Minor |
| Priority | P3 |
| Environment | Chromium (Playwright), Windows 11, https://the-internet.herokuapp.com/broken_images |
| Test case | TI-BUG-CHK-001 |
| Status | Confirmed (intentional defect on this practice site) |
| Reported | 2026-11-01 |

## Steps to reproduce
1. Open https://the-internet.herokuapp.com/broken_images.
2. Look at the three images, or check the Network tab in DevTools.

## Expected result
All three images load and display.

## Actual result
Only `img/avatar-blank.jpg` loads (200). `asdf.jpg` and `hjkl.jpg` return **404** and show as broken image icons.

## Evidence
The automated check finds 3 `<img>` elements, and 2 of them have `naturalWidth = 0`. Requesting each image directly with curl gives 404, 404 and 200.

# Test Run: The Internet + Restful-Booker, 2026-11-01

- **Browser/OS:** Chromium (Playwright), Windows 11 Pro
- **Tester:** Claude
- **Scope:** The Internet (auth, form controls, alerts, dynamic content, frames, upload, mouse actions, broken images) and the Restful-Booker API (auth, CRUD, authorization, validation)

## Summary
| Suite | Total | Passed | Failed | Known-bug (expected fail) |
|---|---|---|---|---|
| The Internet | 20 | 19 | 0 | 1 |
| Restful-Booker | 14 | 11 | 0 | 3 |
| **Full suite (incl. SauceDemo)** | **50** | **44** | **0** | **6** |

## Bugs found
| ID | Summary | Severity |
|---|---|---|
| TI-BUG-001 | 2 of 3 images on /broken_images return 404 | Minor |
| RB-BUG-001 | Wrong login returns 200 instead of 401 | Major |
| RB-BUG-002 | Invalid booking body returns 500 instead of 400 | Major |
| RB-BUG-003 | DELETE returns 201 Created | Minor |

Each known bug was confirmed outside Playwright with curl, so the expected-fail tests fail for the reason they claim.

## Lessons from this run
- **TI-FORM-003 failed on the first run, and the cause was the test.** Pressing Enter inside the input submits the surrounding form and reloads the page, which clears the result. The test now presses `a` and `Tab`. **Lesson: when a test fails, find out whether the bug is in the app or in the test before you file a report.**
- **API tests need their own data.** Restful-Booker is shared by everyone who practices on it, so each test creates a booking with a unique random name and never relies on existing bookings.
- **Check side effects, not only status codes.** RB-DEL-001 checks that the booking is really gone (GET returns 404), even though the DELETE's status code is wrong.

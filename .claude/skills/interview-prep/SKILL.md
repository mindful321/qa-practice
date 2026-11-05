---
name: interview-prep
description: Explain in simple words exactly how each practice website in this repo was tested, framed to prepare the user for a QA Engineer interview (AI skills + Python). Use when the user asks to explain the testing, prepare for an interview, practice interview answers, or understand what was done on a site.
---

# Interview prep: explain how each site was tested

## Who this is for
The user is preparing for a **QA Engineer interview that focuses on AI skills and Python**. This repo is their training ground. Your job is to help them understand the work well enough to **explain it confidently in their own words**, not to impress them with jargon.

## Before explaining
Read the real material. Never describe work from memory or invent it:
1. `SITES.md`: which sites exist and which were actually tested (a site counts as tested only if it has a spec in `tests/`)
2. For each tested site: `test-cases/<site>.md`, `tests/<site>.spec.ts`, its `bug-reports/<PREFIX>-BUG-*.md`, and `test-runs/*<site>*.md`
3. `CLAUDE.md`, for the conventions and lessons learned

If the user names one site, cover only that site. Otherwise cover each tested site in turn.

## How to explain each site
Use plain language. Short sentences. Define every technical term the first time it appears, e.g. "a *locator* is how the test finds a button on the page". Use this structure:

1. **What the site is.** One or two sentences, like you'd tell a friend.
2. **What I tested and why.** Group the cases by feature (login, cart...). For each group, give the *idea* behind it, not every step. Name the testing technique in simple terms:
   - *Positive test*: the happy path, where a normal user does the right thing
   - *Negative test*: wrong input, so the app should refuse it politely
   - *Boundary / validation test*: empty fields, missing data
   - *Security check*: e.g. opening a protected page without logging in
   - *API test*: talking to the server directly, with no browser involved
3. **How the test works, step by step.** Walk through ONE representative test in plain words: "it opens the page, types the username, clicks Login, then checks the page title says Products." Then show the key lines of code and explain each line.
4. **Bugs found.** For each bug: what's wrong, how it was found, how it was proven (curl, DevTools), and why it matters to a real user or business.
5. **What went wrong in my own testing and what I learned.** Use the "Lessons" sections in `test-runs/`. These make the strongest interview stories, because they show judgment.
6. **How I'd say it in an interview.** A 30–60 second spoken answer in the first person ("I tested..."), using **STAR** (Situation, Task, Action, Result).

## Python translation (important)
The specs in this repo are **TypeScript**, but the interview is about **Python**. For every code snippet you show, also show the Python equivalent using `pytest` + `playwright` (sync API), and point out the differences:
- `test('ID ...', async ({ page }) => {...})` becomes `def test_id(page):` (a pytest function, with no async/await)
- `await expect(locator).toHaveText(x)` becomes `expect(locator).to_have_text(x)` (snake_case)
- `test.beforeEach` becomes a pytest **fixture**
- `test.fail()` becomes `@pytest.mark.xfail(reason="BUG-ID")`
- the API `request` fixture becomes `playwright.request.new_context(base_url=...)`, or the `requests` library
- running one test: `pytest -k "login"`

Remind the user they should be able to write these basics in Python themselves. Offer to port a site's suite to Python if they haven't yet.

## AI skills angle
Interviewers for "QA with AI skills" ask how the candidate *uses* AI and how they *check* its work. Draw on what really happened in this repo:
- AI (Claude) drafted the test cases and automation, and the human role was to review, run, and question the results
- **Verifying AI output:** the SauceDemo image test passed when it should have failed, because an AI-written locator matched nothing. It was caught by questioning a suspicious result. This is the key story: *AI speeds up the work, but a tester must verify that the tests really test something*
- Bugs were confirmed independently (curl) instead of trusting a single tool
- Also mention ideas the user could talk about: AI for generating test data, for exploratory-testing ideas, for summarising failures, and testing AI features themselves (non-deterministic output, hallucinations, bias)

## Finish with practice
End each explanation with **3–5 likely interview questions** about that site, each with a short model answer. Then offer a **mock interview**: you ask one question at a time, the user answers in their own words, and you give gentle, specific feedback on clarity, correct terms, and STAR structure.

## Style rules
- Plain words first, the technical term second ("we checked the server's reply code, the *status code*")
- Never claim something was tested if it isn't in the repo. Say "not tested yet" honestly
- Keep each site's explanation to roughly one screen, and offer to go deeper on any part

# RB-BUG-003: DELETE /booking/{id} returns 201 Created

| Field | Value |
|---|---|
| Severity | Minor |
| Priority | P3 |
| Environment | https://restful-booker.herokuapp.com (API) |
| Test case | RB-DEL-001 |
| Status | Confirmed |
| Reported | 2026-11-01 |

## Steps to reproduce
1. Get a token: `POST /auth` with admin / password123.
2. Create a booking: `POST /booking`, and note the `bookingid`.
3. `DELETE /booking/{id}` with the header `Cookie: token=<token>`.

## Expected result
**200 OK** or **204 No Content**.

## Actual result
**201 Created**, with the body `Created`. The booking really is deleted, because a follow-up `GET` returns 404.

## Impact
201 means a resource was created, so the API contract is misleading. Generated clients and strict HTTP libraries may handle this response wrongly.

## Related
`GET /ping` also returns 201. That's a minor quirk, noted under RB-HEALTH-001 and not filed as a separate bug.

# RB-BUG-002: POST /booking with missing fields returns 500 instead of 400

| Field | Value |
|---|---|
| Severity | Major |
| Priority | P2 |
| Environment | https://restful-booker.herokuapp.com (API) |
| Test case | RB-BOOK-006 |
| Status | Confirmed |
| Reported | 2026-11-01 |

## Steps to reproduce
```
curl -X POST https://restful-booker.herokuapp.com/booking \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"firstname":"OnlyName"}'
```

## Expected result
**400 Bad Request**, with a message that names the missing fields (lastname, totalprice, depositpaid, bookingdates).

## Actual result
**500 Internal Server Error**.

## Impact
The server isn't validating input, so a client mistake looks like a server crash. Clients can't tell what to fix, and the error inflates server-error alerts.

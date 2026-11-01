# RB-BUG-001: POST /auth returns 200 OK for wrong credentials

| Field | Value |
|---|---|
| Severity | Major |
| Priority | P2 |
| Environment | https://restful-booker.herokuapp.com (API) |
| Test case | RB-AUTH-002 |
| Status | Confirmed |
| Reported | 2026-11-01 |

## Steps to reproduce
```
curl -X POST https://restful-booker.herokuapp.com/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'
```

## Expected result
Status **401 Unauthorized**.

## Actual result
Status **200 OK** with the body `{"reason":"Bad credentials"}`.

## Impact
A client that checks only the status code treats a failed login as successful. Monitoring tools also can't detect failed logins or brute-force attempts.

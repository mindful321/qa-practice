# Restful-Booker (API): Test Cases

**Base URL:** https://restful-booker.herokuapp.com. **Admin credentials:** admin / password123
**API docs:** https://restful-booker.herokuapp.com/apidoc/index.html

API test cases check the **status code**, the **response body**, and **side effects** (did the data really change?). The test data each test creates is listed with it.

## Health and auth
### RB-HEALTH-001: Health check responds
- **Request:** `GET /ping`
- **Expected result:** a 2xx status. (The API returns 201 Created here, although 200 OK would be the normal code for a health check. This is a minor quirk, worth a note but not a bug report.)

### RB-AUTH-001: Get a token with valid credentials
- **Request:** `POST /auth` with body `{ "username": "admin", "password": "password123" }`
- **Expected result:** 200, and the body has a non-empty `token` string.

### RB-AUTH-002: Wrong credentials are rejected
- **Request:** `POST /auth` with a wrong password.
- **Expected result:** **401 Unauthorized**, and no token.
- **Known defect:** the API returns 200 with `{"reason":"Bad credentials"}` instead (RB-BUG-001).

## Create and read
### RB-BOOK-001: Create a booking
- **Request:** `POST /booking` with a full valid booking (Accept: application/json).
- **Expected result:** 200. The body has a numeric `bookingid`, and every field in `booking` matches what was sent.

### RB-BOOK-002: Read a booking by ID
- **Precondition:** a booking was created (RB-BOOK-001).
- **Request:** `GET /booking/{id}`
- **Expected result:** 200, and the returned fields match the booking that was created.

### RB-BOOK-003: Booking appears in the list
- **Request:** `GET /booking`
- **Expected result:** 200, and the returned array contains `{ bookingid: <id> }`.

### RB-BOOK-004: Filter bookings by name
- **Request:** `GET /booking?firstname=<unique>&lastname=<unique>`
- **Expected result:** 200, and the results include the booking that was created.

### RB-BOOK-005: Unknown ID returns 404
- **Request:** `GET /booking/999999999`
- **Expected result:** 404.

### RB-BOOK-006: Invalid payload is rejected
- **Request:** `POST /booking` with the body `{ "firstname": "OnlyName" }`
- **Expected result:** **400 Bad Request**.
- **Known defect:** the API returns 500 Internal Server Error instead (RB-BUG-002).

## Update and delete (need the token cookie)
### RB-UPD-001: Full update with PUT
- **Request:** `PUT /booking/{id}` with the header `Cookie: token=<token>` and a full new body.
- **Expected result:** 200, the body shows the new values, and a GET afterwards confirms them.

### RB-UPD-002: Partial update with PATCH
- **Request:** `PATCH /booking/{id}` with `{ "firstname": "Patched" }` and the token.
- **Expected result:** 200. Only the first name changes; the other fields stay the same.

### RB-UPD-003: Update without a token is forbidden
- **Request:** `PUT /booking/{id}` with no token.
- **Expected result:** 403, and the booking is unchanged.

### RB-DEL-001: Delete a booking
- **Request:** `DELETE /booking/{id}` with the token.
- **Expected result:** a success status (normally **200 or 204**), and a GET afterwards returns 404.
- **Note:** the API returns 201 Created for a delete, which is the wrong status code (RB-BUG-003).

### RB-DEL-002: Delete without a token is forbidden
- **Expected result:** 403, and the booking still exists.

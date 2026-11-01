import { test, expect, APIRequestContext } from '@playwright/test';

test.use({
  baseURL: 'https://restful-booker.herokuapp.com',
  extraHTTPHeaders: { Accept: 'application/json' },
});

// Unique names so we can find "our" booking among thousands made by other users.
const uid = () => Math.random().toString(36).slice(2, 8);
const newBooking = (first = `QA${uid()}`, last = `Tester${uid()}`) => ({
  firstname: first,
  lastname: last,
  totalprice: 150,
  depositpaid: true,
  bookingdates: { checkin: '2026-12-01', checkout: '2026-12-05' },
  additionalneeds: 'Breakfast',
});

async function getToken(request: APIRequestContext): Promise<string> {
  const res = await request.post('/auth', { data: { username: 'admin', password: 'password123' } });
  expect(res.status()).toBe(200);
  return (await res.json()).token;
}

async function createBooking(request: APIRequestContext, body = newBooking()) {
  const res = await request.post('/booking', { data: body });
  expect(res.status()).toBe(200);
  const json = await res.json();
  return { id: json.bookingid as number, body };
}

// ---------- Health and auth ----------
test('RB-HEALTH-001 health check responds', async ({ request }) => {
  const res = await request.get('/ping');
  expect(res.ok()).toBe(true); // 201 in practice, see the test case note
});

test('RB-AUTH-001 valid credentials return a token', async ({ request }) => {
  const res = await request.post('/auth', { data: { username: 'admin', password: 'password123' } });
  expect(res.status()).toBe(200);
  const json = await res.json();
  expect(typeof json.token).toBe('string');
  expect(json.token.length).toBeGreaterThan(0);
});

test('RB-AUTH-002 wrong credentials are rejected with 401 (RB-BUG-001)', async ({ request }) => {
  test.fail(true, 'RB-BUG-001: returns 200 + {"reason":"Bad credentials"} instead of 401');
  const res = await request.post('/auth', { data: { username: 'admin', password: 'wrong' } });
  expect((await res.json()).token).toBeUndefined();
  expect(res.status()).toBe(401);
});

// ---------- Create and read ----------
test('RB-BOOK-001 create a booking', async ({ request }) => {
  const body = newBooking();
  const res = await request.post('/booking', { data: body });
  expect(res.status()).toBe(200);
  const json = await res.json();
  expect(typeof json.bookingid).toBe('number');
  expect(json.booking).toEqual(body);
});

test('RB-BOOK-002 read a booking by id', async ({ request }) => {
  const { id, body } = await createBooking(request);
  const res = await request.get(`/booking/${id}`);
  expect(res.status()).toBe(200);
  expect(await res.json()).toEqual(body);
});

test('RB-BOOK-003 booking appears in the list', async ({ request }) => {
  const { id } = await createBooking(request);
  const res = await request.get('/booking');
  expect(res.status()).toBe(200);
  expect(await res.json()).toContainEqual({ bookingid: id });
});

test('RB-BOOK-004 filter bookings by name', async ({ request }) => {
  const { id, body } = await createBooking(request);
  const res = await request.get('/booking', {
    params: { firstname: body.firstname, lastname: body.lastname },
  });
  expect(res.status()).toBe(200);
  expect(await res.json()).toContainEqual({ bookingid: id });
});

test('RB-BOOK-005 unknown id returns 404', async ({ request }) => {
  const res = await request.get('/booking/999999999');
  expect(res.status()).toBe(404);
});

test('RB-BOOK-006 invalid payload is rejected with 400 (RB-BUG-002)', async ({ request }) => {
  test.fail(true, 'RB-BUG-002: returns 500 instead of 400 for a missing required field');
  const res = await request.post('/booking', { data: { firstname: 'OnlyName' } });
  expect(res.status()).toBe(400);
});

// ---------- Update and delete ----------
test.describe('Update and delete', () => {
  let token: string;
  test.beforeEach(async ({ request }) => { token = await getToken(request); });
  const auth = () => ({ Cookie: `token=${token}` });

  test('RB-UPD-001 full update with PUT', async ({ request }) => {
    const { id } = await createBooking(request);
    const updated = { ...newBooking('Updated', 'Person'), totalprice: 999, depositpaid: false };
    const res = await request.put(`/booking/${id}`, { data: updated, headers: auth() });
    expect(res.status()).toBe(200);
    expect(await res.json()).toEqual(updated);
    expect(await (await request.get(`/booking/${id}`)).json()).toEqual(updated);
  });

  test('RB-UPD-002 partial update with PATCH', async ({ request }) => {
    const { id, body } = await createBooking(request);
    const res = await request.patch(`/booking/${id}`, { data: { firstname: 'Patched' }, headers: auth() });
    expect(res.status()).toBe(200);
    expect(await res.json()).toEqual({ ...body, firstname: 'Patched' });
  });

  test('RB-UPD-003 update without token is forbidden', async ({ request }) => {
    const { id, body } = await createBooking(request);
    const res = await request.put(`/booking/${id}`, { data: newBooking('Hacker', 'Nope') });
    expect(res.status()).toBe(403);
    expect(await (await request.get(`/booking/${id}`)).json()).toEqual(body);
  });

  test('RB-DEL-001 delete a booking (RB-BUG-003)', async ({ request }) => {
    test.fail(true, 'RB-BUG-003: DELETE returns 201 Created instead of 200/204');
    const { id } = await createBooking(request);
    const res = await request.delete(`/booking/${id}`, { headers: auth() });
    // The side effect is checked first, so the real behaviour is verified even though the status code is wrong.
    expect((await request.get(`/booking/${id}`)).status()).toBe(404);
    expect([200, 204]).toContain(res.status());
  });

  test('RB-DEL-002 delete without token is forbidden', async ({ request }) => {
    const { id } = await createBooking(request);
    const res = await request.delete(`/booking/${id}`);
    expect(res.status()).toBe(403);
    expect((await request.get(`/booking/${id}`)).status()).toBe(200);
  });
});

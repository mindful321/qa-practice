"""API tests for Restful-Booker, written with `requests` (no browser).

The API is shared by everyone, so every test creates its own booking with random
names and never depends on existing data.
"""

import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 15  # seconds per request


def uid() -> str:
    return uuid.uuid4().hex[:6]


def new_booking(first: str | None = None, last: str | None = None) -> dict:
    """Unique names so we can find "our" booking among thousands made by other users."""
    return {
        "firstname": first or f"QA{uid()}",
        "lastname": last or f"Tester{uid()}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-05"},
        "additionalneeds": "Breakfast",
    }


class Api:
    """A thin wrapper so tests can write api.get("/booking/1") instead of full URLs."""

    def __init__(self, session: requests.Session):
        self.session = session

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        return self.session.request(method, BASE_URL + path, timeout=TIMEOUT, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)


@pytest.fixture
def api():
    with requests.Session() as session:
        session.headers["Accept"] = "application/json"
        yield Api(session)


def create_booking(api: Api, body: dict | None = None) -> tuple[int, dict]:
    body = body or new_booking()
    res = api.post("/booking", json=body)
    assert res.status_code == 200
    return res.json()["bookingid"], body


# ---------- Health and auth ----------
def test_rb_health_001_health_check_responds(api: Api):
    res = api.get("/ping")
    assert res.ok  # 201 in practice, see the test case note


def test_rb_auth_001_valid_credentials_return_a_token(api: Api):
    res = api.post("/auth", json={"username": "admin", "password": "password123"})
    assert res.status_code == 200
    token = res.json().get("token")
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.xfail(reason='RB-BUG-001: returns 200 + {"reason":"Bad credentials"} instead of 401')
def test_rb_auth_002_wrong_credentials_are_rejected_with_401(api: Api):
    res = api.post("/auth", json={"username": "admin", "password": "wrong"})
    assert "token" not in res.json()
    assert res.status_code == 401


# ---------- Create and read ----------
def test_rb_book_001_create_a_booking(api: Api):
    body = new_booking()
    res = api.post("/booking", json=body)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["bookingid"], int)
    assert data["booking"] == body


def test_rb_book_002_read_a_booking_by_id(api: Api):
    booking_id, body = create_booking(api)
    res = api.get(f"/booking/{booking_id}")
    assert res.status_code == 200
    assert res.json() == body


def test_rb_book_003_booking_appears_in_the_list(api: Api):
    booking_id, _ = create_booking(api)
    res = api.get("/booking")
    assert res.status_code == 200
    assert {"bookingid": booking_id} in res.json()


def test_rb_book_004_filter_bookings_by_name(api: Api):
    booking_id, body = create_booking(api)
    res = api.get("/booking", params={"firstname": body["firstname"], "lastname": body["lastname"]})
    assert res.status_code == 200
    assert {"bookingid": booking_id} in res.json()


def test_rb_book_005_unknown_id_returns_404(api: Api):
    res = api.get("/booking/999999999")
    assert res.status_code == 404


@pytest.mark.xfail(reason="RB-BUG-002: returns 500 instead of 400 for a missing required field")
def test_rb_book_006_invalid_payload_is_rejected_with_400(api: Api):
    res = api.post("/booking", json={"firstname": "OnlyName"})
    assert res.status_code == 400


# ---------- Update and delete ----------
class TestUpdateAndDelete:
    @pytest.fixture
    def auth(self, api: Api) -> dict:
        """Writes need the header Cookie: token=<token> from POST /auth."""
        res = api.post("/auth", json={"username": "admin", "password": "password123"})
        assert res.status_code == 200
        return {"Cookie": f"token={res.json()['token']}"}

    def test_rb_upd_001_full_update_with_put(self, api: Api, auth: dict):
        booking_id, _ = create_booking(api)
        updated = {**new_booking("Updated", "Person"), "totalprice": 999, "depositpaid": False}
        res = api.put(f"/booking/{booking_id}", json=updated, headers=auth)
        assert res.status_code == 200
        assert res.json() == updated
        assert api.get(f"/booking/{booking_id}").json() == updated

    def test_rb_upd_002_partial_update_with_patch(self, api: Api, auth: dict):
        booking_id, body = create_booking(api)
        res = api.patch(f"/booking/{booking_id}", json={"firstname": "Patched"}, headers=auth)
        assert res.status_code == 200
        assert res.json() == {**body, "firstname": "Patched"}

    def test_rb_upd_003_update_without_token_is_forbidden(self, api: Api):
        booking_id, body = create_booking(api)
        res = api.put(f"/booking/{booking_id}", json=new_booking("Hacker", "Nope"))
        assert res.status_code == 403
        assert api.get(f"/booking/{booking_id}").json() == body

    @pytest.mark.xfail(reason="RB-BUG-003: DELETE returns 201 Created instead of 200/204")
    def test_rb_del_001_delete_a_booking(self, api: Api, auth: dict):
        booking_id, _ = create_booking(api)
        res = api.delete(f"/booking/{booking_id}", headers=auth)
        # The side effect is checked first, so the real behaviour is verified even though
        # the status code is wrong.
        assert api.get(f"/booking/{booking_id}").status_code == 404
        assert res.status_code in (200, 204)

    def test_rb_del_002_delete_without_token_is_forbidden(self, api: Api):
        booking_id, _ = create_booking(api)
        res = api.delete(f"/booking/{booking_id}")
        assert res.status_code == 403
        assert api.get(f"/booking/{booking_id}").status_code == 200

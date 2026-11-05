import re

import pytest
from playwright.sync_api import Page, expect

URL = "https://www.saucedemo.com/"
PASSWORD = "secret_sauce"


def login(page: Page, username: str, password: str = PASSWORD) -> None:
    page.goto(URL)
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()


def error(page: Page):
    return page.get_by_test_id("error")


def cart_badge(page: Page):
    return page.get_by_test_id("shopping-cart-badge")


def prices(page: Page) -> list[float]:
    texts = page.get_by_test_id("inventory-item-price").all_text_contents()
    return [float(t.replace("$", "")) for t in texts]


@pytest.fixture
def logged_in(page: Page) -> Page:
    login(page, "standard_user")
    return page


# ---------- Login ----------
class TestLogin:
    def test_sd_login_001_valid_login_with_standard_user(self, page: Page):
        login(page, "standard_user")
        expect(page).to_have_url(re.compile(r"inventory\.html"))
        expect(page.get_by_test_id("title")).to_have_text("Products")
        expect(page.get_by_test_id("inventory-item")).to_have_count(6)

    def test_sd_login_002_locked_out_user_cannot_log_in(self, page: Page):
        login(page, "locked_out_user")
        expect(error(page)).to_have_text("Epic sadface: Sorry, this user has been locked out.")
        expect(page).not_to_have_url(re.compile("inventory"))

    def test_sd_login_003_wrong_password(self, page: Page):
        login(page, "standard_user", "wrong_pass")
        expect(error(page)).to_have_text(
            "Epic sadface: Username and password do not match any user in this service"
        )

    def test_sd_login_004_empty_username(self, page: Page):
        page.goto(URL)
        page.get_by_role("button", name="Login").click()
        expect(error(page)).to_have_text("Epic sadface: Username is required")

    def test_sd_login_005_empty_password(self, page: Page):
        page.goto(URL)
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_role("button", name="Login").click()
        expect(error(page)).to_have_text("Epic sadface: Password is required")

    def test_sd_login_006_inventory_is_protected_without_login(self, page: Page):
        page.goto(URL + "inventory.html")
        expect(error(page)).to_contain_text(
            "You can only access '/inventory.html' when you are logged in"
        )


# ---------- Sorting ----------
class TestSorting:
    def test_sd_sort_001_price_low_to_high(self, logged_in: Page):
        logged_in.get_by_test_id("product-sort-container").select_option("lohi")
        expect(logged_in.get_by_test_id("inventory-item-price")).to_have_count(6)  # guard
        p = prices(logged_in)
        assert p == sorted(p)

    def test_sd_sort_002_name_z_to_a(self, logged_in: Page):
        logged_in.get_by_test_id("product-sort-container").select_option("za")
        names_locator = logged_in.get_by_test_id("inventory-item-name")
        expect(names_locator).to_have_count(6)  # guard
        names = names_locator.all_text_contents()
        assert names == sorted(names, reverse=True)


# ---------- Cart ----------
class TestCart:
    def test_sd_cart_001_add_item_updates_badge(self, logged_in: Page):
        logged_in.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
        expect(cart_badge(logged_in)).to_have_text("1")
        expect(logged_in.get_by_test_id("remove-sauce-labs-backpack")).to_be_visible()

    def test_sd_cart_002_remove_item_clears_badge(self, logged_in: Page):
        logged_in.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
        logged_in.get_by_test_id("remove-sauce-labs-backpack").click()
        expect(cart_badge(logged_in)).to_have_count(0)


# ---------- Checkout ----------
class TestCheckout:
    @pytest.fixture
    def with_backpack(self, logged_in: Page) -> Page:
        logged_in.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
        return logged_in

    def test_sd_chk_001_complete_purchase_end_to_end(self, with_backpack: Page):
        page = with_backpack
        page.get_by_test_id("add-to-cart-sauce-labs-bike-light").click()
        page.get_by_test_id("shopping-cart-link").click()
        page.get_by_test_id("checkout").click()
        page.get_by_placeholder("First Name").fill("John")
        page.get_by_placeholder("Last Name").fill("Doe")
        page.get_by_placeholder("Zip/Postal Code").fill("12345")
        page.get_by_test_id("continue").click()

        expect(page.get_by_test_id("subtotal-label")).to_have_text("Item total: $39.98")
        expect(page.get_by_test_id("tax-label")).to_have_text("Tax: $3.20")
        expect(page.get_by_test_id("total-label")).to_have_text("Total: $43.18")

        page.get_by_test_id("finish").click()
        expect(page.get_by_test_id("complete-header")).to_have_text("Thank you for your order!")

    def test_sd_chk_002_first_name_is_required(self, with_backpack: Page):
        page = with_backpack
        page.get_by_test_id("shopping-cart-link").click()
        page.get_by_test_id("checkout").click()
        page.get_by_test_id("continue").click()
        expect(error(page)).to_have_text("Error: First Name is required")

    def test_sd_chk_003_postal_code_is_required(self, with_backpack: Page):
        page = with_backpack
        page.get_by_test_id("shopping-cart-link").click()
        page.get_by_test_id("checkout").click()
        page.get_by_placeholder("First Name").fill("John")
        page.get_by_placeholder("Last Name").fill("Doe")
        page.get_by_test_id("continue").click()
        expect(error(page)).to_have_text("Error: Postal Code is required")


# ---------- Session ----------
def test_sd_sess_001_logout_returns_to_login_page(logged_in: Page):
    page = logged_in
    page.get_by_role("button", name="Open Menu").click()
    page.get_by_test_id("logout-sidebar-link").click()
    expect(page.get_by_role("button", name="Login")).to_be_visible()
    page.go_back()
    expect(page.get_by_test_id("inventory-item")).to_have_count(0)


# ---------- problem_user: known defects ----------
# xfail = "this is expected to fail because of a known bug". It is reported as XFAIL
# while the bug exists. If the bug is fixed, the test passes and pytest reports it as
# a failure (xfail_strict in pytest.ini), so you know to remove the marker.
class TestProblemUserKnownBugs:
    @pytest.mark.xfail(reason="SD-BUG-001: every product shows the same image")
    def test_sd_prob_001_product_images_are_unique(self, page: Page):
        login(page, "problem_user")
        images = page.get_by_test_id("inventory-item").locator("img")
        # Guard: make sure we actually found the images, so an empty match can't "pass".
        expect(images).to_have_count(6)
        srcs = images.evaluate_all("imgs => imgs.map(i => i.getAttribute('src'))")
        assert len(set(srcs)) == 6

    @pytest.mark.xfail(reason="Known: Last Name field rejects typing for problem_user")
    def test_sd_prob_002_last_name_field_accepts_input(self, page: Page):
        login(page, "problem_user")
        page.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
        page.get_by_test_id("shopping-cart-link").click()
        page.get_by_test_id("checkout").click()
        page.get_by_placeholder("Last Name").fill("Doe")
        expect(page.get_by_placeholder("Last Name")).to_have_value("Doe", timeout=3_000)

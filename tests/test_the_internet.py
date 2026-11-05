import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://the-internet.herokuapp.com"
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "base_url": BASE_URL}


# ---------- Form authentication ----------
class TestAuthentication:
    @staticmethod
    def login(page: Page, user: str, password: str) -> None:
        page.goto("/login")
        page.get_by_label("Username").fill(user)
        page.get_by_label("Password").fill(password)
        page.get_by_role("button", name="Login").click()

    @staticmethod
    def flash(page: Page):
        return page.locator("#flash")

    def test_ti_auth_001_valid_login(self, page: Page):
        self.login(page, "tomsmith", "SuperSecretPassword!")
        expect(page).to_have_url(re.compile(r"/secure$"))
        expect(self.flash(page)).to_contain_text("You logged into a secure area!")

    def test_ti_auth_002_invalid_username(self, page: Page):
        self.login(page, "wronguser", "SuperSecretPassword!")
        expect(self.flash(page)).to_contain_text("Your username is invalid!")
        expect(page).to_have_url(re.compile(r"/login$"))

    def test_ti_auth_003_invalid_password(self, page: Page):
        self.login(page, "tomsmith", "wrong")
        expect(self.flash(page)).to_contain_text("Your password is invalid!")

    def test_ti_auth_004_logout(self, page: Page):
        self.login(page, "tomsmith", "SuperSecretPassword!")
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(re.compile(r"/login$"))
        expect(self.flash(page)).to_contain_text("You logged out of the secure area!")


class TestBasicAuth:
    @pytest.fixture
    def browser_context_args(self, browser_context_args):
        return {**browser_context_args, "http_credentials": {"username": "admin", "password": "admin"}}

    def test_ti_auth_005_basic_auth_with_valid_credentials(self, page: Page):
        page.goto("/basic_auth")
        expect(page.get_by_text("Congratulations! You must have the proper credentials.")).to_be_visible()


# ---------- Form controls ----------
def test_ti_form_001_checkboxes_toggle(page: Page):
    page.goto("/checkboxes")
    boxes = page.get_by_role("checkbox")
    expect(boxes).to_have_count(2)  # guard
    expect(boxes.nth(0)).not_to_be_checked()
    expect(boxes.nth(1)).to_be_checked()
    boxes.nth(0).check()
    boxes.nth(1).uncheck()
    expect(boxes.nth(0)).to_be_checked()
    expect(boxes.nth(1)).not_to_be_checked()


def test_ti_form_002_dropdown_selection(page: Page):
    page.goto("/dropdown")
    dropdown = page.locator("#dropdown")
    dropdown.select_option(label="Option 2")
    expect(dropdown).to_have_value("2")


def test_ti_form_003_key_press_is_detected(page: Page):
    page.goto("/key_presses")
    # Note: Enter submits the surrounding form and reloads the page, so test with other keys.
    page.locator("#target").press("a")
    expect(page.locator("#result")).to_have_text("You entered: A")
    page.locator("#target").press("Tab")
    expect(page.locator("#result")).to_have_text("You entered: TAB")


def test_ti_form_004_add_and_remove_elements(page: Page):
    page.goto("/add_remove_elements/")
    add = page.get_by_role("button", name="Add Element")
    for _ in range(3):
        add.click()
    delete = page.get_by_role("button", name="Delete")
    expect(delete).to_have_count(3)
    delete.first.click()
    expect(delete).to_have_count(2)


# ---------- JavaScript alerts ----------
class TestJavaScriptAlerts:
    @pytest.fixture(autouse=True)
    def open_alerts_page(self, page: Page):
        page.goto("/javascript_alerts")

    @staticmethod
    def result(page: Page):
        return page.locator("#result")

    def test_ti_alert_001_js_alert_accepted(self, page: Page):
        page.once("dialog", lambda dialog: dialog.accept())
        page.get_by_role("button", name="Click for JS Alert").click()
        expect(self.result(page)).to_have_text("You successfully clicked an alert")

    def test_ti_alert_002_js_confirm_dismissed(self, page: Page):
        page.once("dialog", lambda dialog: dialog.dismiss())
        page.get_by_role("button", name="Click for JS Confirm").click()
        expect(self.result(page)).to_have_text("You clicked: Cancel")

    def test_ti_alert_003_js_prompt_with_text(self, page: Page):
        page.once("dialog", lambda dialog: dialog.accept("Hello QA"))
        page.get_by_role("button", name="Click for JS Prompt").click()
        expect(self.result(page)).to_have_text("You entered: Hello QA")


# ---------- Dynamic content ----------
def test_ti_dyn_001_hidden_element_appears_after_loading(page: Page):
    page.goto("/dynamic_loading/1")
    page.get_by_role("button", name="Start").click()
    expect(page.get_by_role("heading", name="Hello World!")).to_be_visible(timeout=15_000)


def test_ti_dyn_002_element_rendered_after_loading(page: Page):
    page.goto("/dynamic_loading/2")
    expect(page.get_by_role("heading", name="Hello World!")).to_have_count(0)
    page.get_by_role("button", name="Start").click()
    expect(page.get_by_role("heading", name="Hello World!")).to_be_visible(timeout=15_000)


def test_ti_dyn_003_remove_and_enable_controls(page: Page):
    page.goto("/dynamic_controls")
    page.get_by_role("button", name="Remove").click()
    expect(page.locator("#message")).to_have_text("It's gone!", timeout=15_000)
    expect(page.get_by_role("checkbox")).to_have_count(0)

    text_input = page.locator('#input-example input[type="text"]')
    expect(text_input).to_be_disabled()
    page.get_by_role("button", name="Enable").click()
    expect(page.locator("#message")).to_have_text("It's enabled!", timeout=15_000)
    expect(text_input).to_be_editable()


# ---------- Frames, files, mouse ----------
def test_ti_frame_001_read_nested_frames(page: Page):
    page.goto("/nested_frames")
    top = page.frame_locator('frame[name="frame-top"]')
    expect(top.frame_locator('frame[name="frame-left"]').locator("body")).to_have_text("LEFT")
    expect(page.frame_locator('frame[name="frame-bottom"]').locator("body")).to_have_text("BOTTOM")


def test_ti_file_001_file_upload(page: Page):
    page.goto("/upload")
    page.locator("#file-upload").set_input_files(FIXTURES / "sample.txt")
    page.get_by_role("button", name="Upload").click()
    expect(page.get_by_role("heading", name="File Uploaded!")).to_be_visible()
    expect(page.locator("#uploaded-files")).to_have_text("sample.txt")


def test_ti_mouse_001_drag_and_drop_swaps_boxes(page: Page):
    page.goto("/drag_and_drop")
    expect(page.locator("#column-a header")).to_have_text("A")
    page.locator("#column-a").drag_to(page.locator("#column-b"))
    expect(page.locator("#column-a header")).to_have_text("B")
    expect(page.locator("#column-b header")).to_have_text("A")


def test_ti_mouse_002_hover_reveals_user_info(page: Page):
    page.goto("/hovers")
    first = page.locator(".figure").first
    expect(first.get_by_text("name: user1")).to_be_hidden()
    first.hover()
    expect(first.get_by_text("name: user1")).to_be_visible()
    expect(first.get_by_role("link", name="View profile")).to_be_visible()


# ---------- Known defects ----------
@pytest.mark.xfail(reason="TI-BUG-001: broken images on /broken_images")
def test_ti_bug_chk_001_all_images_load(page: Page):
    page.goto("/broken_images")
    images = page.locator("#content img")
    expect(images).to_have_count(3)  # guard: never pass on an empty match
    widths = images.evaluate_all("imgs => imgs.map(i => i.naturalWidth)")
    assert all(w > 0 for w in widths)

import pytest
from playwright.sync_api import Playwright, expect

# Web-first assertions retry until this timeout (milliseconds), like Playwright's default.
expect.set_options(timeout=5_000)


@pytest.fixture(scope="session", autouse=True)
def use_data_test_attribute(playwright: Playwright):
    """The practice sites use data-test="..." attributes, so get_by_test_id() reads those."""
    playwright.selectors.set_test_id_attribute("data-test")

"""Navigation checks that create no data on the site."""
import re

import pytest
from playwright.sync_api import expect

import config


@pytest.mark.navigation
def test_tc_n01_home_get_started_opens_register(pw_page):
    pw_page.goto(config.BASE_URL)
    pw_page.locator("a[href='/register']:visible").first.click()
    expect(pw_page).to_have_url(re.compile(r"/register"))


@pytest.mark.navigation
def test_tc_n02_register_page_loads(signup):
    signup.open()
    expect(signup.terms_checkbox).to_be_visible()
    expect(signup.continue_button).to_be_visible()


@pytest.mark.navigation
def test_tc_n03_go_to_login_link(signup):
    signup.open()
    signup.page.get_by_text("Go to Login").click()
    expect(signup.page).to_have_url(re.compile(r"/login"))


@pytest.mark.navigation
def test_tc_n04_terms_and_privacy_links_present(signup):
    signup.open()
    expect(signup.page.get_by_role("link", name="Terms of Service")).to_have_attribute("href", re.compile("terms"))
    expect(signup.page.get_by_role("link", name="Privacy Policy")).to_have_attribute("href", re.compile("privacy"))

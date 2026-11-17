"""Shared fixtures: browser, page with video/console monitoring, screenshot on failure."""
import pytest
from playwright.sync_api import sync_playwright

import config
from helpers import build_user, get_logger, load_data
from pages.signup_page import SignupPage

log = get_logger()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, "rep_" + call.when, outcome.get_result())


@pytest.fixture(scope="session")
def pw_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel=config.BROWSER_CHANNEL, headless=config.HEADLESS, slow_mo=config.SLOW_MO
        )
        yield browser
        browser.close()


@pytest.fixture
def pw_page(request, pw_browser):
    ctx = pw_browser.new_context(
        viewport={"width": 1366, "height": 800},
        record_video_dir=str(config.VIDEO_DIR) if config.RECORD_VIDEO else None,
    )
    page = ctx.new_page()
    page.set_default_timeout(config.TIMEOUT_MS)
    console_errors = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errors.append(str(e)))
    yield page
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        path = config.SCREENSHOT_DIR / f"FAILED_{request.node.name}.png"
        try:
            page.screenshot(path=str(path), full_page=True)
            log.error("Failure screenshot: %s", path.name)
        except Exception as exc:  # page may already be closed
            log.error("Could not take failure screenshot: %s", exc)
    for err in console_errors:
        log.warning("Browser console error: %s", err)
    ctx.close()


@pytest.fixture
def signup(pw_page):
    return SignupPage(pw_page)


@pytest.fixture
def user():
    return build_user()


@pytest.fixture(scope="session")
def data():
    return load_data()

"""Stand-alone runner: automates the whole signup once and records a video.

    python signup_automation_script.py

Creates ONE real account on the live site. Needs .env (see .env.example).
The email code is entered according to OTP_MODE (prompt / env / imap).
"""
import sys

from playwright.sync_api import sync_playwright

import config
from helpers import build_user, get_logger
from pages.signup_page import SignupPage

log = get_logger()


def main():
    user = build_user()
    log.info("Starting signup for generated test user (email %s)", user["email"])
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS,
                                    slow_mo=config.SLOW_MO or 300)
        ctx = browser.new_context(viewport={"width": 1366, "height": 800},
                                  record_video_dir=str(config.VIDEO_DIR))
        page = ctx.new_page()
        page.set_default_timeout(config.TIMEOUT_MS)
        signup = SignupPage(page)
        try:
            signup.run_full_signup(user)
            log.info("RESULT: signup completed - dashboard confirmed at %s", page.url)
            code = 0
        except Exception as exc:
            signup.snap("script_failure")
            log.error("RESULT: signup FAILED: %s", exc)
            code = 1
        finally:
            ctx.close()  # finalises the .webm video in videos/
            browser.close()
    sys.exit(code)


if __name__ == "__main__":
    main()

"""Page object for the Authorized Partner agent registration flow.

Locators come from a recorded manual session (Playwright codegen). The flow is:
  /register terms page -> Step 1 Account -> email code -> Step 2 Agency Details
  -> Step 3 Professional Experience -> Step 4 Verification and Preferences
  -> logged-in dashboard (/admin/profile).
"""
import re

from playwright.sync_api import Page, expect

import config
from helpers import get_logger, get_otp

log = get_logger()


class SignupPage:
    def __init__(self, page: Page):
        self.page = page

    # ---------- generic helpers ----------
    def snap(self, name):
        path = config.SCREENSHOT_DIR / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        log.info("Screenshot saved: %s", path.name)
        return path

    @property
    def next_button(self):
        return self.page.get_by_role("button", name="Next", exact=True)

    def click_next(self):
        self.next_button.click()

    def expect_message(self, text):
        """A validation message containing `text` (case-insensitive) is visible."""
        expect(self.page.get_by_text(re.compile(re.escape(text), re.I)).first).to_be_visible(timeout=20000)

    # ---------- terms page ----------
    def open(self):
        log.info("Opening %s/register", config.BASE_URL)
        self.page.goto(f"{config.BASE_URL}/register")
        expect(self.page.get_by_role("heading", name=re.compile("Register Your Agency", re.I))).to_be_visible()

    @property
    def terms_checkbox(self):
        return self.page.get_by_role("checkbox", name=re.compile("I agree to the Terms"))

    @property
    def continue_button(self):
        return self.page.get_by_role("button", name="Continue")

    def accept_terms_and_continue(self):
        self.terms_checkbox.click()
        self.continue_button.click()
        expect(self.page.get_by_role("textbox", name="First Name")).to_be_visible()

    # ---------- step 1: account ----------
    def fill_account(self, first, last, email, phone, password, confirm=None):
        p = self.page
        p.get_by_role("textbox", name="First Name").fill(first)
        p.get_by_role("textbox", name="Last Name").fill(last)
        p.get_by_role("textbox", name="Email Address").fill(email)
        p.locator("input[name='password']").fill(password)
        p.locator("input[name='confirmPassword']").fill(password if confirm is None else confirm)
        p.get_by_role("textbox", name="Phone Number").fill(phone)

    def expect_still_on_account_step(self):
        expect(self.page.get_by_role("textbox", name="First Name")).to_be_visible()
        expect(self.page.get_by_role("button", name="Verify Code")).to_have_count(0)

    def step1_account(self, user):
        self.fill_account(user["first_name"], user["last_name"], user["email"], user["phone"], user["password"])
        self.click_next()

    # ---------- email code ----------
    def enter_otp(self):
        try:
            expect(self.page.get_by_text(re.compile("verification code", re.I)).first).to_be_visible(timeout=30000)
        except AssertionError:
            msgs = self.page.locator("[role='status'], [role='alert'], p:visible").all_inner_texts()
            log.error("Code screen did not appear. Messages on page: %s", [m for m in msgs if m.strip()])
            raise
        self.snap("otp_screen")
        code = get_otp()  # never logged or stored
        box = self.page.get_by_role("textbox").first
        box.click()
        box.press_sequentially(code, delay=150)
        expect(box).to_have_value(code)
        self.page.get_by_role("button", name="Verify Code").click()
        expect(self.page.get_by_text("About your Agency")).to_be_visible(timeout=30000)

    # ---------- step 2: agency ----------
    def step2_agency(self, user, website=None, submit=True):
        p = self.page
        p.get_by_role("textbox", name=re.compile(r"^Name")).fill(user["agency_name"])
        p.get_by_role("textbox", name="Role in Agency").fill(user["role"])
        p.get_by_role("textbox", name="Email Address").fill(user["email"])
        # The field already shows a fixed "https://" prefix, so type only the domain.
        p.get_by_role("textbox", name="Website").fill(website if website is not None else user["website"])
        p.get_by_role("textbox", name="Address", exact=True).fill(user["address"])
        p.get_by_role("combobox").click()
        p.get_by_text(user["region"], exact=True).first.click()
        p.keyboard.press("Escape")
        if submit:
            self.click_next()

    # ---------- step 3: experience ----------
    def step3_experience(self, user):
        p = self.page
        expect(p.get_by_text("Experience and Performance Metrics")).to_be_visible()
        p.get_by_role("combobox", name="Years of Experience").click()
        p.get_by_role("option", name=user["years_of_experience"]).click()
        p.get_by_role("spinbutton", name="Number of Students Recruited").fill(user["students_per_year"])
        p.get_by_role("textbox", name="Focus Area").fill(user["focus_area"])
        p.get_by_role("spinbutton", name="Success Metrics").fill(user["success_metric"])
        p.get_by_role("checkbox", name=user["service"]).click()
        self.click_next()

    # ---------- step 4: preferences + documents ----------
    def fill_preferences(self, user):
        p = self.page
        expect(p.get_by_text("Provide Business Details and Set Preferences")).to_be_visible()
        p.get_by_role("textbox", name="Business Registration Number").fill(user["registration_number"])
        p.get_by_role("combobox", name="Preferred Countries").click()
        p.get_by_text(user["region"], exact=True).first.click()
        p.keyboard.press("Escape")
        p.get_by_role("checkbox", name=user["institution_type"]).click()

    def upload_document(self, path=None):
        self.page.get_by_role("button", name="Choose File").first.set_input_files(str(path or config.UPLOAD_FILE))

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="Submit")

    def submit(self):
        self.submit_button.click()

    def step4_preferences(self, user):
        self.fill_preferences(user)
        self.upload_document()
        self.submit()

    # ---------- result ----------
    def expect_dashboard(self):
        """Success = redirected to the logged-in area showing the My Profile heading."""
        expect(self.page).to_have_url(re.compile(r"/admin"), timeout=30000)
        expect(self.page.get_by_role("heading", name="My Profile")).to_be_visible()

    # ---------- whole flow ----------
    def run_full_signup(self, user):
        self.open()
        self.accept_terms_and_continue()
        self.snap("step0_terms_accepted")
        self.step1_account(user)
        self.enter_otp()
        self.snap("step2_agency")
        self.step2_agency(user)
        self.snap("step3_experience")
        self.step3_experience(user)
        self.snap("step4_preferences")
        self.step4_preferences(user)
        self.expect_dashboard()
        self.snap("final_dashboard")
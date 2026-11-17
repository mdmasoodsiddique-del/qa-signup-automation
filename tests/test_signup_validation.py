"""Negative / validation tests. Messages asserted are ones seen on the real site;
for fields where the message text was not observed, the test asserts the user stays on the step."""
import pytest

import config


@pytest.fixture
def on_account_step(signup):
    signup.open()
    signup.accept_terms_and_continue()
    return signup


@pytest.mark.validation
def test_tc_v01_terms_not_accepted_blocks_signup(signup):
    """Continue must not move to the account step without accepting the terms."""
    signup.open()
    if signup.continue_button.is_enabled():
        signup.continue_button.click()
    signup.page.get_by_role("textbox", name="First Name").wait_for(state="hidden", timeout=3000)


@pytest.mark.validation
def test_tc_v02_empty_account_form(on_account_step):
    on_account_step.click_next()
    on_account_step.snap("v02_empty_account_form")
    on_account_step.expect_still_on_account_step()


@pytest.mark.validation
def test_tc_v03_invalid_email_format(on_account_step, user, data):
    on_account_step.fill_account(user["first_name"], user["last_name"],
                                 data["invalid_values"]["bad_email"], user["phone"], user["password"])
    on_account_step.click_next()
    on_account_step.snap("v03_invalid_email")
    on_account_step.expect_still_on_account_step()


@pytest.mark.validation
def test_tc_v04_password_too_short(on_account_step, user, data):
    pw = data["invalid_values"]["short_password"]
    on_account_step.fill_account(user["first_name"], user["last_name"], user["email"], user["phone"], pw)
    on_account_step.click_next()
    on_account_step.snap("v04_short_password")
    on_account_step.expect_message(data["observed_messages"]["password_short"])


@pytest.mark.validation
def test_tc_v05_password_confirmation_mismatch(on_account_step, user):
    on_account_step.fill_account(user["first_name"], user["last_name"], user["email"], user["phone"],
                                 user["password"], confirm=user["password"] + "x")
    on_account_step.click_next()
    on_account_step.snap("v05_password_mismatch")
    on_account_step.expect_still_on_account_step()


@pytest.mark.validation
def test_tc_v06_invalid_phone_number(on_account_step, user, data):
    on_account_step.fill_account(user["first_name"], user["last_name"], user["email"],
                                 data["invalid_values"]["bad_phone"], user["password"])
    on_account_step.click_next()
    on_account_step.snap("v06_invalid_phone")
    on_account_step.expect_message(data["observed_messages"]["phone_format"])


@pytest.mark.validation
@pytest.mark.duplicate
@pytest.mark.skipif(not config.DUPLICATE_PHONE, reason="Set DUPLICATE_PHONE in .env (a number already registered)")
def test_tc_v07_duplicate_phone_number(on_account_step, user, data):
    on_account_step.fill_account(user["first_name"], user["last_name"], user["email"],
                                 config.DUPLICATE_PHONE, user["password"])
    on_account_step.click_next()
    on_account_step.snap("v07_duplicate_phone")
    on_account_step.expect_message(data["observed_messages"]["phone_duplicate"])


@pytest.mark.validation
@pytest.mark.e2e
@pytest.mark.skipif(not config.RUN_E2E, reason="Needs the email code; set RUN_E2E=1")
def test_tc_v08_invalid_website_and_missing_document(signup, user, data):
    """Later-step validation. Needs a real signup up to step 4; it does NOT press the final valid Submit."""
    signup.open()
    signup.accept_terms_and_continue()
    signup.step1_account(user)
    signup.enter_otp()
    signup.step2_agency(user, website=data["invalid_values"]["bad_website"])
    signup.snap("v08_invalid_website")
    signup.expect_message(data["observed_messages"]["website_invalid"])
    signup.step2_agency(user)
    signup.step3_experience(user)
    signup.fill_preferences(user)
    signup.submit()
    signup.snap("v08_document_required")
    signup.expect_message(data["observed_messages"]["document_required"])

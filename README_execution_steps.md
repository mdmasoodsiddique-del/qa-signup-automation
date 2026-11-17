# QA Signup Automation - Authorized Partner

Automation of the agent registration flow at https://authorized-partner.vercel.app/register
using Python, Playwright and Pytest.

## Result summary

- Full signup run (signup_automation_script.py): completed once on the live site, ending on the logged-in dashboard /admin/profile (heading "My Profile"). Evidence: screenshots/final_dashboard.png and demo_video.webm.
- Pytest: 11 passed, 2 skipped (see reports/test_report.pdf and reports/test_report.html).
- The 2 skipped tests (test_tc_s01, test_tc_v08) create data on the live site and need the email code. They were not executed.

## Important limitation

After the account page, the site emails a one-time 6-digit code that cannot be bypassed. The script pauses and asks for the code (OTP_MODE=prompt), so that one step is manual. All other steps are automated. An optional mailbox reader (OTP_MODE=imap) exists in helpers.py but was not verified.

## Signup flow

1. /register: accept terms, click Continue
2. Step 1 Account: first and last name, email, password, confirm password, phone (+977)
3. Email verification code
4. Step 2 Agency Details: name, role, email, website, address, region
5. Step 3 Professional Experience: years, students per year, focus area, success metric, service
6. Step 4 Verification and Preferences: registration number, preferred countries, institution type, document upload, Submit
7. Success: redirect to /admin/profile

## Environment and versions

- Windows 11, Python 3.12.9
- Playwright (Python) 1.65.2, pytest 9.2.0, pytest-html 4.2.0, python-dotenv 1.2.4, reportlab 5.1.0
- Browser: Microsoft Edge through Playwright channel "msedge" (the PC policy blocks Playwright's bundled Chromium)

## Setup

    python -m venv venv
    venv\Scripts\activate
    python -m pip install -r requirements.txt
    copy .env.example .env

Edit .env and set TEST_EMAIL_BASE to a mailbox you control (it receives the code). Do not commit .env. To use bundled Chromium instead of Edge, leave BROWSER_CHANNEL empty and run: python -m playwright install chromium

## How to run

Tests that create no accounts:

    python -m pytest

Full signup (creates one real account; type the emailed code when asked):

    python signup_automation_script.py

Live-site pytest tests: set RUN_E2E=1 in .env first.

Single test:

    python -m pytest tests/test_signup_navigation.py::test_tc_n03_go_to_login_link

PDF report from the last pytest run:

    python generate_report_pdf.py

## Test data and accounts

- All data is synthetic: name "Test Agent", agency "Test Agency QA", fake registration number, dummy upload test_data/test_document.pdf.
- A fresh phone number (98 + 8 random digits), password and email alias (mailbox+qa<timestamp>@gmail.com) are generated on every run.
- A dedicated test mailbox was used for the email code. No passwords or secrets are stored in this repository.
- The site has no known test environment or cleanup, so several test accounts were created during development.

## Project structure

    signup_automation_script.py   full signup run
    config.py, helpers.py, conftest.py
    pages/signup_page.py          page object
    tests/                        navigation, validation and success tests
    test_data/                    test_users.json, test_document.pdf
    reports/                      test_report.pdf and .html
    screenshots/                  evidence
    demo_video.webm               recording of the successful run (Playwright format; plays in Chrome, Edge, VLC)

## Known limitations

- Manual email-code entry (see above).
- Messages for empty fields, invalid email and mismatched passwords were not observed, so those tests only check that the form does not advance.
- Dropdown items on this site are not exposed as ARIA options, so they are selected by visible text.
- Tests were run on one machine only.

## Troubleshooting

- pip.exe blocked: use python -m pip
- Browser error "spawn UNKNOWN": use BROWSER_CHANNEL=msedge
- Validation messages appear slowly (server check): tests wait up to 20 seconds.

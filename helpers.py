"""Test-data generation, logging and email-code (OTP) handling."""
import email
import email.utils
import imaplib
import json
import logging
import random
import re
import string
import time

import config

_RUN_START = time.time()


def get_logger(name="signup"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def load_data():
    with open(config.TEST_DATA_DIR / "test_users.json", encoding="utf-8") as f:
        return json.load(f)


def random_phone():
    """Nepal-style mobile: 98 + 8 random digits (entered without the +977 code)."""
    return "98" + "".join(random.choices(string.digits, k=8))


def random_password():
    return "Qa@" + "".join(random.choices(string.ascii_letters + string.digits, k=10)) + "1"


def make_email():
    base = config.TEST_EMAIL_BASE
    if "@" not in base:
        raise RuntimeError("Set TEST_EMAIL_BASE in .env to a mailbox you control.")
    if config.TEST_EMAIL_MODE == "plus":
        local, domain = base.split("@", 1)
        return f"{local}+qa{int(time.time())}@{domain}"
    return base


def build_user():
    """Valid user data from JSON plus values generated fresh for this run."""
    user = dict(load_data()["valid_user"])
    user["email"] = make_email()
    user["phone"] = random_phone()
    user["password"] = config.TEST_PASSWORD or random_password()
    return user


def get_otp():
    """Return the 6-digit email code according to OTP_MODE."""
    mode = config.OTP_MODE
    if mode == "env":
        if not config.OTP_CODE:
            raise RuntimeError("OTP_MODE=env but OTP_CODE is empty.")
        return config.OTP_CODE
    if mode == "imap":
        return _otp_from_imap()
    return input("Enter the 6-digit code from your test mailbox: ").strip()


def _otp_from_imap():
    """Read the newest 6-digit code from emails that arrived after this run started."""
    log = get_logger()
    deadline = time.time() + config.OTP_TIMEOUT
    while time.time() < deadline:
        mail = imaplib.IMAP4_SSL(config.IMAP_HOST)
        mail.login(config.IMAP_USER, config.IMAP_PASSWORD)
        mail.select("INBOX")
        _, data = mail.search(None, "ALL")
        for num in reversed(data[0].split()[-10:]):
            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            try:
                sent = email.utils.parsedate_to_datetime(msg["Date"]).timestamp()
            except Exception:
                continue
            if sent < _RUN_START - 30:
                continue
            body = ""
            for part in msg.walk():
                if part.get_content_type() in ("text/plain", "text/html"):
                    body += part.get_payload(decode=True).decode(errors="ignore")
            match = re.search(r"\b(\d{6})\b", body)
            if match:
                mail.logout()
                log.info("Email code read automatically from the test mailbox")
                return match.group(1)
        mail.logout()
        time.sleep(5)
    raise TimeoutError("No 6-digit code found in the mailbox in time.")
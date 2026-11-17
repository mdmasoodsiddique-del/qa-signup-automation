"""Central configuration. Values come from environment variables / .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")


def _bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes")


BASE_URL = os.getenv("BASE_URL", "https://authorized-partner.vercel.app").rstrip("/")
BROWSER_CHANNEL = os.getenv("BROWSER_CHANNEL", "msedge").strip() or None
HEADLESS = _bool("HEADLESS")
SLOW_MO = int(os.getenv("SLOW_MO", "0") or 0)
RECORD_VIDEO = _bool("RECORD_VIDEO", "true")
TIMEOUT_MS = 15000

TEST_EMAIL_BASE = os.getenv("TEST_EMAIL_BASE", "").strip()
TEST_EMAIL_MODE = os.getenv("TEST_EMAIL_MODE", "plus").strip().lower()
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "").strip()

OTP_MODE = os.getenv("OTP_MODE", "prompt").strip().lower()
OTP_CODE = os.getenv("OTP_CODE", "").strip()
OTP_TIMEOUT = int(os.getenv("OTP_TIMEOUT", "120") or 120)
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.getenv("IMAP_USER", "")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", "")

RUN_E2E = _bool("RUN_E2E")
DUPLICATE_PHONE = os.getenv("DUPLICATE_PHONE", "").strip()

SCREENSHOT_DIR = ROOT / "screenshots"
VIDEO_DIR = ROOT / "videos"
REPORT_DIR = ROOT / "reports"
TEST_DATA_DIR = ROOT / "test_data"
UPLOAD_FILE = TEST_DATA_DIR / "test_document.pdf"
for _d in (SCREENSHOT_DIR, VIDEO_DIR, REPORT_DIR):
    _d.mkdir(exist_ok=True)

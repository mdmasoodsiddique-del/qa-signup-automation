"""TC-S01: full end-to-end signup. Creates a real account on the live site."""
import pytest

import config

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not config.RUN_E2E, reason="Set RUN_E2E=1 in .env to create an account on the live site"),
]


def test_tc_s01_complete_signup(signup, user):
    """Terms -> account -> email code -> agency -> experience -> preferences -> dashboard."""
    signup.run_full_signup(user)

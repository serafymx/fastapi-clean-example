import logging
from datetime import datetime, timedelta
from typing import Final

logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS: Final[int] = 5
LOCKOUT_WINDOW: Final[timedelta] = timedelta(minutes=15)


class LoginThrottle:
    """
    Locks a username for LOCKOUT_WINDOW after MAX_FAILED_ATTEMPTS failed logins.
    The window starts at the first failure.
    """

    def __init__(self) -> None:
        self._failures: dict[str, tuple[int, datetime]] = {}

    def is_locked(self, username: str) -> bool:
        entry = self._failures.get(username)
        if entry is None:
            return False
        attempts, first_failure = entry
        elapsed = datetime.now() - first_failure
        if elapsed.seconds > LOCKOUT_WINDOW.total_seconds():
            del self._failures[username]
            return False
        return attempts > MAX_FAILED_ATTEMPTS

    def record_failure(self, username: str) -> None:
        attempts, first_failure = self._failures.get(username, (0, datetime.now()))
        self._failures[username] = (attempts + 1, first_failure)

    def record_success(self, username: str) -> None:
        self._failures.pop(username, None)


login_throttle = LoginThrottle()

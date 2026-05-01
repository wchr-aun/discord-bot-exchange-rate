from datetime import datetime, UTC, timedelta
from setup import REVOLUT_DCA_DAY_OF_WEEK, REVOLUT_DCA_EXECUTION_HOUR


def get_next_execution_datetime(now=None):
    if now is None:
        now = datetime.now(UTC)

    # Target time on the target day of week
    days_ahead = (REVOLUT_DCA_DAY_OF_WEEK - now.weekday()) % 7
    target = now.replace(
        hour=REVOLUT_DCA_EXECUTION_HOUR, minute=0, second=0, microsecond=0
    ) + timedelta(days=days_ahead)

    # If target is in the past, move to next week
    if target <= now:
        target += timedelta(days=7)

    return target


def get_upcoming_execution_date_str(now=None):
    return get_next_execution_datetime(now).strftime("%Y-%m-%d")


def is_execution_day(now=None):
    if now is None:
        now = datetime.now(UTC)
    return now.weekday() == REVOLUT_DCA_DAY_OF_WEEK


def get_seconds_to_next_execution_hour(now=None):
    if now is None:
        now = datetime.now(UTC)

    target = now.replace(
        hour=REVOLUT_DCA_EXECUTION_HOUR, minute=0, second=0, microsecond=0
    )
    if target <= now:
        target += timedelta(days=1)

    return (target - now).total_seconds()

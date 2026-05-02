import datetime as dt
from datetime import datetime
from zoneinfo import ZoneInfo


def format_datetime(datetime_str: str, timezone_str: str | None = None) -> str:
    """
    - Parse `datetime_str` with `datetime.fromisoformat()` — this handles ISO 8601 strings including timezone offsets
    - If `timezone_str` is provided, convert to that timezone before formatting (use `zoneinfo`)
    - If datetime_str has no attached time shift, e.g., +10:00, call it UTC.
    - Return a human-readable string that includes the date components
    """  # noqa: E501

    if timezone_str is None:
        timezone_str = "UTC"
    parsed = datetime.fromisoformat(datetime_str)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    in_tz = parsed.astimezone(ZoneInfo(timezone_str))
    return f"{in_tz: %d %b %Y, %H:%M:%S %Z}"

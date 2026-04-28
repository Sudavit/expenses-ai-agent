import datetime as dt
from zoneinfo import ZoneInfo


def format_datetime(datetime_str: str, timezone_str: str | None = None) -> str:
    """
    - Parse `datetime_str` with `datetime.fromisoformat()` — this handles ISO 8601 strings including timezone offsets
    - If `timezone_str` is provided, convert to that timezone before formatting (use `zoneinfo`)
    - Return a human-readable string that includes the date components
    """  # noqa: E501

    if timezone_str is None:
        timezone_str = "UTC"
    in_utc = dt.datetime.fromisoformat(datetime_str)
    in_tz = in_utc.astimezone(ZoneInfo(timezone_str))
    return f"{in_tz: %d %b %Y}"

from expenses_ai_agent.tools.tools import (
    CURRENCY_CONVERSION_TOOL,
)
from expenses_ai_agent.utils.date_formatter import format_datetime


class TestDateFormatter:
    """Tests for the date formatting utility."""

    def test_format_datetime_with_timezone_additional(self):
        """Should support timezone conversion."""
        result_with_tz_str = format_datetime(
            "2024-06-15T12:00:00+00:00", timezone_str="Europe/Madrid"
        )
        result_without_tz_str = format_datetime("2024-06-15T12:00:00+02:00")

        assert result_with_tz_str == result_without_tz_str


class TestToolSchemas:
    """Tests for OpenAI-compatible tool schemas."""

    def test_currency_tool_has_required_structure_fixed(self):
        """Tool schema should follow OpenAI function calling format."""
        tool = CURRENCY_CONVERSION_TOOL
        assert tool["type"] == "function"

        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool

        params = tool["parameters"]
        assert "type" in params
        assert "properties" in params
        assert "required" in params

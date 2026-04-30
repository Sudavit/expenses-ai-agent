from decimal import Decimal

import pytest

from expenses_ai_agent.conf.config import SecretKey, UndefinedValueError, get_api_config
from expenses_ai_agent.storage.exceptions import CurrencyConversionError
from expenses_ai_agent.tools.tools import (
    CURRENCY_CONVERSION_TOOL,
)
from expenses_ai_agent.utils.currency import convert_currency
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


class TestAPIConfig:
    """Test ability to get API keys"""

    def test_api_keys_accessible(self):
        """All secret keys available"""
        for api_key in SecretKey:
            assert isinstance(get_api_config(api_key), str)

    def test_bad_api_key_raises(self):
        """Bad secret key raises exception"""
        with pytest.raises(UndefinedValueError):
            get_api_config("Sudavit")


class TestCurrencyExceptions:
    """Tests for custom currency-conversion exceptions."""

    def test_expense_not_found_error_exists(self):
        """CurrencyConversionError should be a custom exception."""
        error = CurrencyConversionError("This is a currency-conversion error")
        assert isinstance(error, Exception)
        assert "Currency conversion failure" in str(error)

    def test_bad_currency_conversion_raises(self):
        """Converting to a non-existing currency should raise an exception."""
        with pytest.raises(CurrencyConversionError):
            # convert to Canadian Tire Money
            convert_currency(
                amount=Decimal("1.00"), from_currency="CAD", to_currency="CTM"
            )

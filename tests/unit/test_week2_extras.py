from decimal import Decimal

import pytest
from decouple import UndefinedValueError, config

from expenses_ai_agent.llms.exceptions import LLMParseError
from expenses_ai_agent.tools.tools import (
    CURRENCY_CONVERSION_TOOL,
)
from expenses_ai_agent.utils.currency import convert_currency
from expenses_ai_agent.utils.date_formatter import format_datetime
from expenses_ai_agent.utils.exceptions import CurrencyConversionError


class TestDateFormatter:
    """Tests for the date formatting utility."""

    def test_correctly_handling_implicit_tz(self):
        result_hawaii = format_datetime("2000-01-01:00:00-10:00", timezone_str="HST")
        result_gmt = format_datetime("2000-01-01:00:00")  # implicit UTC
        assert result_hawaii[:-3] == result_gmt[:-3]


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


class TestAPIKeyConfig:
    """Test ability to get API keys"""

    def test_api_keys_accessible(self):
        """All secret keys available, non-empty strings"""
        for api_key in ["EXCHANGE_RATE_API_KEY", "OPENAI_API_KEY"]:
            assert config(api_key, default="")
            assert isinstance(api_key, str)

    def test_bad_api_key_raises(self):
        """Bad secret key raises exception"""
        with pytest.raises(UndefinedValueError):
            config("Sudavit")


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
                # CTM == Canadian Tire Money
                amount=Decimal("1.00"),
                from_currency="CAD",
                to_currency="CTM",
            )


class TestLLMExceptions:
    """Tests for custom LLM exceptions."""

    def test_llmparse_error_exists(self):
        """LLMParseError should be a custom exception."""
        error = LLMParseError("This is an LLM parsing error")
        assert isinstance(error, Exception)
        assert "LLM parsing" in str(error)

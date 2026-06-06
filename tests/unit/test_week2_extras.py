import pytest
from decouple import UndefinedValueError, config
from jsonschema import validate
from pydantic import ValidationError
from unittest.mock import MagicMock, patch


from expenses_ai_agent.api.schemas.expense import ExpenseClassifyRequest
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.exceptions import (
    LLMParseError,
    LLMNoKeyError,
)


from expenses_ai_agent.tools.tools import (
    CURRENCY_CONVERSION_TOOL,
    DATETIME_FORMATTER_TOOL,
    OPENAI_TOOL_META_SCHEMA,
)
from expenses_ai_agent.utils.date_formatter import format_datetime
from expenses_ai_agent.utils.exceptions import CurrencyConversionError



class TestDateFormatter:
    """Tests for the date formatting utility."""

    def test_correctly_handling_implicit_tz(self):
        result_hawaii = format_datetime("2000-01-01:00:00-10:00", timezone_str="HST")
        result_gmt = format_datetime("2000-01-01:00:00")  # implicit UTC
        assert result_hawaii[:-3] == result_gmt[:-3]


class TestToolSchemas:
    # This validates the outer "envelope"
    def test_currency_tool_has_required_structure(self):
        validate(instance=CURRENCY_CONVERSION_TOOL, schema=OPENAI_TOOL_META_SCHEMA)

    def test_datetime_tool_has_required_structure(self):
        validate(instance=DATETIME_FORMATTER_TOOL, schema=OPENAI_TOOL_META_SCHEMA)


class TestAPIKeyConfig:
    """Test ability to get API keys"""

    def test_api_keys_accessible(self, monkeypatch):
        """All secret keys available, non-empty strings"""
        for api_key in ["EXCHANGE_RATE_API_KEY", "OPENAI_API_KEY"]:
            monkeypatch.setenv(api_key, "dummy_value_for_unit_test")
            assert config(api_key, default="")
            assert isinstance(api_key, str)

    def test_bad_api_key_raises(self):
        """Bad secret key raises exception"""
        with pytest.raises(UndefinedValueError):
            config("Sudavit")


class TestCurrencyExceptions:
    """Tests for custom -conversion exceptions."""

    def test_expense_not_found_error_exists(self):
        """CurrencyConversionError should be a custom exception."""
        error = CurrencyConversionError("This is a currency-conversion error")
        assert isinstance(error, Exception)
        assert "Currency conversion failure" in str(error)


class TestLLMExceptions:
    """Tests for custom LLM exceptions."""

    def test_llmparse_error_exists(self):
        """LLMParseError should be a custom exception."""
        error = LLMParseError("This is an LLM parsing error")
        assert isinstance(error, Exception)
        assert "LLM parsing" in str(error)


    def test_openai_assistant_missing_key_raises_error(self):
        """Should raise LLMNoKeyError if no API key is found in env or arguments."""
        # We patch decouple.config inside the openai module to return an empty string
        with patch("expenses_ai_agent.llms.openai.config", return_value=""):
            with pytest.raises(LLMNoKeyError) as exc_info:
                OpenAIAssistant(api_key=None)
                
            assert "set $OPENAI_API_KEY or pass in to OpenAIAssistant()" in str(exc_info.value)



    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_openai_assistant_completion_parse_failure_raises_error(self, mock_openai_class):
        """Should raise LLMParseError if the response parsed attribute evaluates to None."""
        # Mock the internal client and beta completion endpoint
        mock_client = mock_openai_class.return_value
        mock_response = MagicMock()
        
        # Force the parsed field to be None to simulate validation failure
        mock_response.choices[0].message.parsed = None
        mock_client.beta.chat.completions.parse.return_value = mock_response
        
        # Initialize assistant with a dummy key to bypass the init check
        assistant = OpenAIAssistant(api_key="fake-key")
        
        with pytest.raises(LLMParseError) as exc_info:
            assistant.completion(messages=[{"role": "user", "content": "test"}])
            
        assert "Failed to parse response from OpenAI" in str(exc_info.value)


    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_get_available_models_returns_sequence_of_ids(self,mock_openai_class):
        """Should successfully fetch and extract model IDs from the client listing."""
        # 1. Access the mock instance returned by the class constructor
        mock_client = mock_openai_class.return_value
        
        # 2. Forge individual model objects containing an 'id' attribute
        mock_model_1 = MagicMock()
        mock_model_1.id = "jeff"
        
        mock_model_2 = MagicMock()
        mock_model_2.id = "juanjo"

        mock_model_3 = MagicMock()
        mock_model_3.id = "bob"
        
        # 3. Attach the mocked list to the models endpoint tree
        mock_client.models.list.return_value = [
            mock_model_1, 
            mock_model_2, 
            mock_model_3
        ]
        
        # 4. Instantiate our assistant and execute the target method
        assistant = OpenAIAssistant(api_key="valid-mock-key")
        models = assistant.get_available_models()
        
        # 5. Validation Assertions
        assert len(models) == 3
        assert "jeff" in models
        assert "juanjo" in models
        assert "bob" in models
        # Structural Check: Ensure the underlying client method was explicitly invoked
        mock_client.models.list.assert_called_once()

class TestExpenseSchemasEdgeCases:
    """Extra validations to force absolute schema coverage."""

    def test_expense_classify_request_whitespace_only_raises_error(self):
        """Should fail validation when description contains only whitespace."""

        # Pydantic will intercept the ValueError and wrap it inside a ValidationError
        with pytest.raises(ValidationError) as exc_info:
            ExpenseClassifyRequest(description="   ")

        # Verify that our specific exception message survived the Pydantic wrapper
        assert "description cannot be empty or whitespace" in str(exc_info.value)


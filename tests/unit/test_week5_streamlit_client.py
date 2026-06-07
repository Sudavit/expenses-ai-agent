from unittest.mock import MagicMock, patch

import httpx

import expenses_ai_agent.streamlit.api_client as api_client_module
from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient


class TestExpenseApiClientExhaustive:
    """Exhaustive unit test suite to lock down api_client.py at 100% code coverage."""

    def test_client_dunder_methods(self):
        """Validates hash calculation and equivalence operations."""
        client_a = ExpenseAPIClient("https://api.test.com/")
        client_b = ExpenseAPIClient("https://api.test.com")
        client_c = ExpenseAPIClient("https://api.different.com")

        assert hash(client_a) == hash(client_b)
        assert client_a == client_b
        assert client_a != client_c
        assert client_a != "not-a-client-object"

    @patch.object(api_client_module, "st")
    def test_get_expenses_connection_error(self, mock_st, monkeypatch):
        """Covers Lines 31-32: Triggers the network disconnection catch block."""
        api_client = ExpenseAPIClient("https://api.test.com")

        # Use monkeypatch to safely substitute the attribute without type errors
        mock_get = MagicMock(side_effect=httpx.ConnectError("Connection refused"))
        monkeypatch.setattr(api_client.client, "get", mock_get)

        result = api_client.get_expenses(user_id=123)

        assert result == []
        mock_st.error.assert_called_once()

    @patch.object(api_client_module, "st")
    def test_classify_only_expense_success_and_failure(self, mock_st, monkeypatch):
        """Validates classification network calls and error catching."""
        api_client = ExpenseAPIClient("https://api.test.com")

        # 1. Happy Path
        mock_response = MagicMock()
        mock_response.json.return_value = {"category": "Food", "confidence": 0.95}
        mock_post = MagicMock(return_value=mock_response)
        monkeypatch.setattr(api_client.client, "post", mock_post)

        result = api_client.classify_only_expense("Starbucks coffee", user_id=123)
        assert result["category"] == "Food"

        # 2. Error Path (Lines 51-53)
        mock_post.side_effect = httpx.ConnectError("Timeout")
        err_result = api_client.classify_only_expense("Starbucks coffee", user_id=123)
        assert err_result == {}
        mock_st.error.assert_called_once()

    @patch.object(api_client_module, "st")
    def test_delete_expense_success_and_failure(self, mock_st, monkeypatch):
        """Validates item deletion network calls and error catching."""
        api_client = ExpenseAPIClient("https://api.test.com")

        # 1. Happy Path
        mock_response = MagicMock()
        mock_delete = MagicMock(return_value=mock_response)
        monkeypatch.setattr(api_client.client, "delete", mock_delete)

        api_client.delete_expense(expense_id=42)
        mock_delete.assert_called_once_with("https://api.test.com/expenses/42")

        # 2. Error Path (Lines 63-64)
        mock_delete.side_effect = httpx.ConnectError("Unreachable")
        api_client.delete_expense(expense_id=42)
        mock_st.error.assert_called_once()

    @patch.object(api_client_module, "st")
    def test_get_summary_connection_error(self, mock_st, monkeypatch):
        """Triggers analytics disconnection catch block."""
        api_client = ExpenseAPIClient("https://api.test.com")

        mock_get = MagicMock(side_effect=httpx.ConnectError("Dropped"))
        monkeypatch.setattr(api_client.client, "get", mock_get)

        result = api_client.get_summary(user_id=123)
        assert result == {}
        mock_st.error.assert_called_once()

    @patch.object(api_client_module, "st")
    def test_persist_expense_success_and_all_failures(self, mock_st, monkeypatch):
        """
        Validates schema creation, successful POSTs,
        and both exception catch blocks.
        """
        api_client = ExpenseAPIClient("https://api.test.com")

        # 1. Happy Path
        mock_response = MagicMock()
        mock_post = MagicMock(return_value=mock_response)
        monkeypatch.setattr(api_client.client, "post", mock_post)

        api_client.persist_expense("Uber ride", amount=25.50, user_id=123)
        mock_post.assert_called_once()

        # 2. HTTP Status Error Path (Lines 104-105)
        mock_err_response = MagicMock()
        mock_err_response.text = "Invalid amount format"
        status_error = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=mock_err_response
        )

        mock_post.side_effect = status_error
        api_client.persist_expense("Uber ride", amount=25.50, user_id=123)
        mock_st.error.assert_any_call(
            "Backend validation rejected transaction: Invalid amount format"
        )

        # 3. Connection Error Path (Lines 106-107)
        mock_post.side_effect = httpx.ConnectError("Failed")
        api_client.persist_expense("Uber ride", amount=25.50, user_id=123)
        mock_st.error.assert_any_call("Backend connection failed: Failed")

    def test_get_expenses_success_path(self, monkeypatch):
        """Exercises raise_for_status and item data unpacking."""
        api_client = ExpenseAPIClient("https://api.test.com")

        # 1. Forge a mock response object with successful status and valid payload array
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": 1, "amount": 10.50, "category": "Food"},
                {"id": 2, "amount": 4.20, "category": "Coffee"},
            ]
        }

        # 2. Safely monkeypatch the client attribute to satisfy the type checker
        mock_get = MagicMock(return_value=mock_response)
        monkeypatch.setattr(api_client.client, "get", mock_get)

        # 3. Execute and verify the data unpacking flow
        result = api_client.get_expenses(user_id=123)

        assert len(result) == 2
        assert result[0]["category"] == "Food"
        mock_response.raise_for_status.assert_called_once()

    def test_get_summary_success_path(self, monkeypatch):
        """Exercises raise_for_status and summary payload return."""
        api_client = ExpenseAPIClient("https://api.test.com")

        # 1. Forge a mock response object
        # mirroring an analytics summary dictionary mapping
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"total_spent": 14.70, "currency": "EUR"}

        # 2. Monkeypatch without type violation warnings
        mock_get = MagicMock(return_value=mock_response)
        monkeypatch.setattr(api_client.client, "get", mock_get)

        # 3. Execute and verify the direct payload return
        result = api_client.get_summary(user_id=123)

        assert result["total_spent"] == 14.70
        mock_response.raise_for_status.assert_called_once()

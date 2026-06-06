from unittest.mock import MagicMock, patch

from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient
from expenses_ai_agent.streamlit.views.expenses import render


class TestStreamlitExpensesViewCoverage:
    """Isolates the interactive Streamlit grid view to push coverage to 100%."""

    @patch("expenses_ai_agent.streamlit.views.expenses.st")
    def test_render_clicking_delete_button_triggers_client_and_rerun(self, mock_st):
        """
        Interactive Path: Should invoke client deletion API
        and trigger a page rerun when clicked.
        """
        # 1. Setup a dummy expense item list payload
        # matching the view's data iteration structure
        mock_expense = {
            "id": 42,
            "category": "Food",
            "amount": "12.50",
            "currency": "EUR",
            "description": "Lunch transaction",
        }

        # 2. Configure our API client mock to return this list smoothly
        mock_client = MagicMock(spec=ExpenseAPIClient)
        mock_client.get_expenses.return_value = [mock_expense]

        # 3. FIX THE UNPACKING deadLock:
        # Forge two independent mock column container environments
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()

        # Tell the mock st.columns method to return a list containing our two variables
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # 4. STREAMLIT INTERACTION SIMULATION MECHANICS:
        # Construct the exact unique dynamic widget key that the button uses:
        target_widget_key = f"del_{mock_expense['id']}"

        # Force st.button matching this key to return True,
        # mimicking a physical user mouse click
        def mock_button_click(label, key=None):
            if key == target_widget_key:
                return True
            return False

        mock_st.button.side_effect = mock_button_click

        # 5. Invoke the render method directly under test isolation
        render(client=mock_client, user_id=12345)

        # 6. VERIFICATIONS & ARCHITECTURAL STAMP:
        # Verify that the deletion handler was executed
        # against the mock client with the correct ID
        mock_client.delete_expense.assert_called_once_with(42)

        # Verify that st.rerun() was cleanly requested to reload the interface state
        mock_st.rerun.assert_called_once()

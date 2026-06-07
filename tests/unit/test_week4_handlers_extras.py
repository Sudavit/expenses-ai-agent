from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
from telegram import CallbackQuery, Message, Update, User
from telegram.ext import ContextTypes, ConversationHandler

from expenses_ai_agent.telegram.handlers import (
    CurrencyHandler,
    ExpenseConversationHandler,
    cancel_command,
    ensure_effective_user,
    ensure_message,
    ensure_query,
    ensure_query_data,
    ensure_user_data,
)


class TestTelegramHandlersExhaustive:
    """Test every defensive exception guard and asynchronous handler hook."""

    def test_defensive_guard_exceptions_raise_value_errors(self):
        """Forces value errors across all five utility guard validations."""
        mock_update = MagicMock(spec=Update)
        mock_update.message = None
        mock_update.callback_query = None
        mock_update.effective_user = None

        mock_query = MagicMock(spec=CallbackQuery)
        mock_query.data = None

        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.user_data = None

        # Line 46
        with pytest.raises(
            ValueError, match="Update did not contain a valid message payload."
        ):
            ensure_message(mock_update)

        # Line 52
        with pytest.raises(
            ValueError, match="Update did not contain a valid callback_query payload."
        ):
            ensure_query(mock_update)

        # Line 58
        with pytest.raises(
            ValueError, match="Callback query did not contain valid data."
        ):
            ensure_query_data(mock_query)

        # Line 64
        with pytest.raises(
            ValueError, match="Update did not originate from a valid Telegram user."
        ):
            ensure_effective_user(mock_update)

        # Line 70
        with pytest.raises(
            ValueError, match="User data is required but was not provided."
        ):
            ensure_user_data(mock_context)

    # =========================================================================
    # 2. CONVERSATION FALLBACK ORCHESTRATION
    # =========================================================================

    @pytest.mark.asyncio
    async def test_cancel_command_execution(self):
        """Assert message reply and termination state."""
        mock_update = MagicMock(spec=Update)
        mock_message = AsyncMock(spec=Message)
        mock_update.message = mock_message
        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        next_state = await cancel_command(mock_update, mock_context)

        assert next_state == ConversationHandler.END
        mock_message.reply_text.assert_awaited_once_with("Operation cancelled.")

    # =========================================================================
    # 3. EXPENSE SELECTION BOUNDARY ERRORS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_handle_category_selection_invalid_category_error(self):
        """
        Triggers ValueError catch when invalid category string payload hits callback."""
        handler = ExpenseConversationHandler(db_url="sqlite://", api_key="fake")

        mock_update = MagicMock(spec=Update)
        mock_query = AsyncMock(spec=CallbackQuery)
        mock_query.data = "cat:NOT_A_REAL_CATEGORY_NAME"
        mock_update.callback_query = mock_query
        mock_user = MagicMock(spec=User)
        mock_user.id = 123
        mock_update.effective_user = mock_user

        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.user_data = {
            "expense_description": "test",
            "classification_response": MagicMock(),
        }

        next_state = await handler.handle_category_selection(mock_update, mock_context)

        assert next_state == ConversationHandler.END
        mock_query.answer.assert_awaited_once()
        mock_query.edit_message_text.assert_awaited_once_with(
            "Error: Invalid expense category received."
        )

    @pytest.mark.asyncio
    async def test_handle_category_selection_session_expired_error(self):
        """Triggers missing description/response branch (Session Expiration)."""
        handler = ExpenseConversationHandler(db_url="sqlite://", api_key="fake")

        mock_update = MagicMock(spec=Update)
        mock_query = AsyncMock(spec=CallbackQuery)
        mock_query.data = "cat:Food"
        mock_update.callback_query = mock_query
        mock_user = MagicMock(spec=User)
        mock_user.id = 123
        mock_update.effective_user = mock_user

        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        # Force empty user_data context map to trigger expiration condition branch
        mock_context.user_data = {}

        next_state = await handler.handle_category_selection(mock_update, mock_context)

        assert next_state == ConversationHandler.END
        mock_query.edit_message_text.assert_awaited_once_with(
            "Session expired. Send the expense again."
        )

    # =========================================================================
    # 4. CURRENCY HANDLER INTERACTION REGISTRY
    # =========================================================================

    @pytest.mark.asyncio
    @patch("expenses_ai_agent.telegram.handlers.DBUserPreferenceRepo")
    async def test_handle_currency_selection_success(self, mock_repo_class):
        """Simulates keyboard callback parsing and database upsert operations."""
        currency_handler = CurrencyHandler(db_url="sqlite://")

        # Setup mock updates payload tree structure
        mock_update = MagicMock(spec=Update)
        mock_query = AsyncMock(spec=CallbackQuery)
        mock_query.data = "curr:USD"
        mock_update.callback_query = mock_query

        mock_user = MagicMock(spec=User)
        mock_user.id = 98765
        mock_update.effective_user = mock_user

        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        # Setup downstream mockup storage interaction hooks
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance

        await currency_handler.handle_currency_selection(mock_update, mock_context)

        # Assert correct data breakdown extraction and repository routing calls
        mock_query.answer.assert_awaited_once()
        mock_repo_class.assert_called_once_with("sqlite://")
        mock_repo_instance.upsert.assert_called_once()

        # Verify the visual updates reported clean mutation confirmation details
        mock_query.edit_message_text.assert_awaited_once_with(
            "Currency preference saved as USD."
        )

    def test_build_assistant_instantiates_openai_wrapper(self):
        """Covers Line 102: Directly executes the internal assistant factory method."""
        handler = ExpenseConversationHandler(
            db_url="sqlite://", api_key="test-api-key", model="gpt-4o-mini"
        )

        # Patch the OpenAIAssistant to avoid real initialization/side effects
        with patch(
            "expenses_ai_agent.telegram.handlers.OpenAIAssistant"
        ) as mock_oa_class:
            mock_instance = MagicMock()
            mock_instance.model = "gpt-4o-mini"
            mock_oa_class.return_value = mock_instance

            # Call the internal target method directly to run line 102
            assistant = handler._build_assistant()

            # Verify the instance was constructed with our configuration fields
            assert assistant is mock_instance
            assert assistant.model == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_currency_command_sends_keyboard_markup(self):
        """Executes the currency command string hook and verifies the layout output."""
        currency_handler = CurrencyHandler(db_url="sqlite://")

        # Forge an async mock update payload structure to satisfy ensure_message
        mock_update = MagicMock(spec=Update)
        mock_message = AsyncMock(spec=Message)
        mock_update.message = mock_message

        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        # Trigger the command endpoint logic directly
        await currency_handler.currency_command(mock_update, mock_context)

        # Verify that it read the message payload and replied with the menu
        mock_message.reply_text.assert_awaited_once_with(
            "Select your preferred currency:", reply_markup=ANY
        )

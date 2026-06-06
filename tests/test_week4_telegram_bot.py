import os
import runpy
from unittest.mock import MagicMock, patch

from telegram.ext import Application

from expenses_ai_agent.telegram.bot import build_application, main


class TestTelegramBotOrchestration:
    """
    Unit tests for bot.py
    without network side-effects.
    """

    @patch("expenses_ai_agent.telegram.bot.Application.builder")
    @patch("expenses_ai_agent.telegram.bot.CurrencyHandler")
    @patch("expenses_ai_agent.telegram.bot.ExpenseConversationHandler")
    def test_build_application_wires_handlers_and_returns_app(
        self, mock_conv_handler_class, mock_currency_handler_class, mock_builder_fn
    ):
        """
        Build_application correctly registers all Telegram routing handlers.
        """
        # 1. Setup the fluent ApplicationBuilder mock pipeline
        mock_builder_instance = MagicMock()
        mock_builder_fn.return_value = mock_builder_instance
        mock_builder_instance.token.return_value = mock_builder_instance

        mock_app_instance = MagicMock(spec=Application)
        mock_builder_instance.build.return_value = mock_app_instance

        # 2. Setup internal custom handlers wrappers
        mock_conv_handler = mock_conv_handler_class.return_value
        mock_conv_handler.build.return_value = MagicMock()

        # 3. Call the target function under complete isolation
        app = build_application(
            token="fake-bot-token", db_url="sqlite://", api_key="fake-key"
        )

        # ==========================================
        # VERIFICATIONS
        # ==========================================
        assert app == mock_app_instance

        # Verify the application builder bound the correct token secret
        mock_builder_instance.token.assert_called_once_with("fake-bot-token")
        mock_builder_instance.build.assert_called_once()

        # Verify that add_handler was invoked to register the required 6 core routes:
        # (start, help, cancel, currency command, callback queries, conversation flow)
        assert mock_app_instance.add_handler.call_count == 6

        # Verify constructors were invoked with the correct dependencies
        mock_currency_handler_class.assert_called_once_with(db_url="sqlite://")
        mock_conv_handler_class.assert_called_once_with(
            db_url="sqlite://", api_key="fake-key"
        )

    @patch("expenses_ai_agent.telegram.bot.build_application")
    @patch("expenses_ai_agent.telegram.bot.config")
    @patch("expenses_ai_agent.telegram.bot.logging.basicConfig")
    def test_main_initializes_and_starts_polling(
        self, mock_logging, mock_config, mock_build_app
    ):
        """
        Validate environment initialization
        and the safe launch of the run_polling framework loop.
        """

        # 1. Mock decouple.config to safely yield fake environmental constraints
        def mock_config_side_effect(key, default=None):
            if key == "TELEGRAM_BOT_TOKEN":
                return "token-xyz"
            if key == "DATABASE_URL":
                return "sqlite:///test.db"
            if key == "OPENAI_API_KEY":
                return "openai-xyz"
            return default

        mock_config.side_effect = mock_config_side_effect

        # 2. Stub the return application layout
        mock_app = MagicMock()
        mock_build_app.return_value = mock_app

        # 3. Trigger the script's main entry point execution flow
        main()

        # ==========================================
        # VERIFICATIONS
        # ==========================================
        # Validate logging setup baseline
        mock_logging.assert_called_once()

        # Confirm app factory receives configuration items
        # extracted from env properties
        mock_build_app.assert_called_once_with(
            token="token-xyz", db_url="sqlite:///test.db", api_key="openai-xyz"
        )

        # CRITICAL DECOUPLING CHECK:
        # Ensure the long-polling execution hook was triggered cleanly
        mock_app.run_polling.assert_called_once()


class TestTelegramBotScriptEntrypoint:
    """Validates the physical script execution pathway of bot.py when run as main."""

    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "dummy-test-token-format",
            "OPENAI_API_KEY": "dummy-test-openai-key-format",
        },
    )
    @patch("expenses_ai_agent.telegram.bot.Application.builder")
    def test_bot_script_execution_as_main_entrypoint(self, mock_builder_fn):
        """Simulate executing the file directly from a terminal context."""

        # 1. Setup a fluent mock builder pipeline
        # to satisfy instantiation tracking
        mock_builder_instance = MagicMock()
        mock_builder_fn.return_value = mock_builder_instance
        mock_builder_instance.token.return_value = mock_builder_instance

        mock_app_instance = MagicMock(spec=Application)
        mock_builder_instance.build.return_value = mock_app_instance

        # 2. Target the literal location of the file in your project workspace
        target_file_path = "src/expenses_ai_agent/telegram/bot.py"

        # 3. Force run_path to execute the file
        # while binding its execution name to __main__
        runpy.run_path(target_file_path, run_name="__main__")

        # ==========================================
        # VERIFICATION
        # ==========================================
        # Verify that the script successfully entered main()
        # and ran the initialization chain
        mock_builder_fn.assert_called_once()
        mock_builder_instance.token.assert_called_once_with("dummy-test-token-format")
        # Confirm that the interpreter passed the conditional block and invoked main()

        # Verify that the script reached the very last line of main()
        # and started the engine loop
        mock_app_instance.run_polling.assert_called_once()

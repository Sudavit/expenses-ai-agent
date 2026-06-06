import logging

from decouple import config
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

from expenses_ai_agent.telegram.handlers import (
    CurrencyHandler,
    ExpenseConversationHandler,
    cancel_command,
    help_command,
    start_command,
)
from expenses_ai_agent.telegram.keyboards import CURRENCY_CALLBACK_PREFIX

logger = logging.getLogger(__name__)


def build_application(token: str, db_url: str, api_key: str) -> Application:
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    currency_handler = CurrencyHandler(db_url=db_url)
    application.add_handler(
        CommandHandler("currency", currency_handler.currency_command)
    )
    application.add_handler(
        CallbackQueryHandler(
            currency_handler.handle_currency_selection,
            pattern=f"^{CURRENCY_CALLBACK_PREFIX}",
        )
    )
    application.add_handler(
        ExpenseConversationHandler(db_url=db_url, api_key=api_key).build()
    )
    return application


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    token = config("TELEGRAM_BOT_TOKEN", default="")
    db_url = config("DATABASE_URL", default="sqlite:///./expenses.db")
    api_key = config("OPENAI_API_KEY")

    application = build_application(token=token, db_url=db_url, api_key=api_key)
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()

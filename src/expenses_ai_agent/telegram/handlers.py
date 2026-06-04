from enum import IntEnum

from telegram import CallbackQuery, Update, User
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.services.preprocessing import InputPreprocessor
from expenses_ai_agent.storage.models import Currency, ExpenseCategory
from expenses_ai_agent.storage.repo import (
    DBExpenseRepository as DBExpenseRepo,
)
from expenses_ai_agent.storage.repo import (
    DBUserPreferenceRepo,
)
from expenses_ai_agent.telegram.keyboards import (
    CATEGORY_CALLBACK_PREFIX,
    build_category_confirmation_keyboard,
    build_currency_selection_keyboard,
)

WELCOME_TEXT = (
    "Welcome! Send me an expense and I'll classify it.\n"
    "Example: Coffee at Starbucks $5.50\n\n"
    "Commands: /help"
)

HELP_TEXT = (
    "/start — welcome message\n"
    "/help — this message\n"
    "/currency — set your preferred currency\n"
    "/cancel — cancel the current operation\n\n"
    "Or just send any expense description to classify it."
)


def ensure_message(update: Update):
    if update.message is None:
        raise ValueError("Update did not contain a valid message payload.")
    return update.message


def ensure_query(update: Update) -> CallbackQuery:
    if update.callback_query is None:
        raise ValueError("Update did not contain a valid callback_query payload.")
    return update.callback_query


def ensure_query_data(query: CallbackQuery) -> str:
    if query.data is None:
        raise ValueError("Callback query did not contain valid data.")
    return query.data


def ensure_effective_user(update: Update) -> User:
    if update.effective_user is None:
        raise ValueError("Update did not originate from a valid Telegram user.")
    return update.effective_user


def ensure_user_data(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if context.user_data is None:
        raise ValueError("User data is required but was not provided.")
    return context.user_data


class ConversationState(IntEnum):
    WAITING_FOR_CATEGORY = 0


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = ensure_message(update)
    await message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = ensure_message(update)
    await message.reply_text(HELP_TEXT)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = ensure_message(update)
    await message.reply_text("Operation cancelled.")
    return ConversationHandler.END


class ExpenseConversationHandler:
    def __init__(self, db_url: str, api_key: str, model: str = "gpt-4o-mini"):
        self._db_url = db_url
        self._api_key = api_key
        self._model = model
        self._preprocessor = InputPreprocessor()

    def _build_assistant(self) -> OpenAIAssistant:
        return OpenAIAssistant(api_key=self._api_key, model=self._model)

    def _build_service(self) -> ClassificationService:
        return ClassificationService(
            self._build_assistant(), DBExpenseRepo(self._db_url)
        )

    def _get_categories(self) -> list[str]:
        return [c.value for c in ExpenseCategory]

    def build(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.handle_expense_text
                )
            ],
            states={
                ConversationState.WAITING_FOR_CATEGORY: [
                    CallbackQueryHandler(
                        self.handle_category_selection,
                        pattern=f"^{CATEGORY_CALLBACK_PREFIX}",
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_command)],
        )

    async def handle_expense_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        message = ensure_message(update)
        user_data = ensure_user_data(context)

        processed = self._preprocessor.preprocess(message.text)
        if not processed.is_valid:
            await message.reply_text(
                f"Sorry, I couldn't process that: {processed.error}"
            )
            return ConversationHandler.END
        if processed.warnings:
            await message.reply_text("Note: " + "; ".join(processed.warnings))

        result = self._build_service().classify(processed.text)
        user_data["expense_description"] = processed.text
        user_data["classification_response"] = result.response

        keyboard = build_category_confirmation_keyboard(
            suggested_category=result.response.category,
            all_categories=self._get_categories(),
        )
        await message.reply_text(
            f"Classified as {result.response.category} "
            f"({result.response.confidence:.0%} confidence)\n"
            f"Amount: {result.response.total_amount} {result.response.currency}",
            reply_markup=keyboard,
        )
        return ConversationState.WAITING_FOR_CATEGORY

    async def handle_category_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        query = ensure_query(update)
        user_data = ensure_user_data(context)
        effective_user = ensure_effective_user(update)
        query_data = ensure_query_data(query)
        await query.answer()
        category = query_data.split(":", 1)[1]
        try:
            category = ExpenseCategory(category)
        except ValueError:
            await query.edit_message_text("Error: Invalid expense category received.")
            return ConversationHandler.END

        description = user_data.get("expense_description")
        response = user_data.get("classification_response")
        if description is None or response is None:
            await query.edit_message_text("Session expired. Send the expense again.")
            return ConversationHandler.END

        self._build_service().persist_with_category(
            expense_description=description,
            category=category,
            response=response,
            telegram_user_id=effective_user.id,
        )
        await query.edit_message_text(f"Saved as {category}!")
        return ConversationHandler.END


class CurrencyHandler:
    def __init__(self, db_url: str):
        self._db_url = db_url

    async def currency_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        message = ensure_message(update)
        await message.reply_text(
            "Select your preferred currency:",
            reply_markup=build_currency_selection_keyboard(),
        )

    async def handle_currency_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = ensure_query(update)
        effective_user = ensure_effective_user(update)
        query_data = ensure_query_data(query)
        await query.answer()
        currency_code = query_data.split(":", 1)[1]
        DBUserPreferenceRepo(self._db_url).upsert(
            telegram_user_id=effective_user.id,
            currency=Currency(currency_code),
        )
        await query.edit_message_text(f"Currency preference saved as {currency_code}.")

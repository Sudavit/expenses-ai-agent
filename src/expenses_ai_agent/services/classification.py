from dataclasses import dataclass

from expenses_ai_agent.llms.base import Assistant, Messages
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT
from expenses_ai_agent.prompts.user import USER_PROMPT
from expenses_ai_agent.storage.models import Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import ExpenseRepository


@dataclass(frozen=True)
class ClassificationResult:
    response: ExpenseCategorizationResponse
    persisted: bool = False


@dataclass
class ClassificationService:
    assistant: Assistant
    expense_repo: ExpenseRepository | None = None

    def classify(
        self,
        expense_description: str,
        persist: bool = False,
    ) -> ClassificationResult:
        """
        Classifies an expense description and optionally persists the result.
        Defaults to not persisting to allow for classification
        without storage side effects.
        """
        messages = self._build_messages(expense_description)
        response = self.assistant.completion(messages)

        if persist and self.expense_repo:
            self._persist_expense(expense_description, response)

        return ClassificationResult(response=response, persisted=persist)

    def persist_with_category(
        self,
        expense_description: str,
        category: ExpenseCategory,
        response: ExpenseCategorizationResponse,
        telegram_user_id: int | None = None,
    ) -> None:
        response = response.model_copy(update={"category": category})

        if self.expense_repo:
            self._persist_expense(expense_description, response, telegram_user_id)

    def _build_messages(self, expense_description: str) -> Messages:
        return [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT.format(expense_description=expense_description),
            },
        ]

    def _persist_expense(
        self,
        expense_description: str,
        response: ExpenseCategorizationResponse,
        telegram_user_id: int | None = None,
    ) -> None:
        expense = Expense(
            amount=response.total_amount,
            currency=response.currency,
            category=ExpenseCategory(response.category),
            description=expense_description,
            telegram_user_id=telegram_user_id,
        )
        if self.expense_repo:
            self.expense_repo.add(expense)

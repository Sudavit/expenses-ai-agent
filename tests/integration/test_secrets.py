from decimal import Decimal
from unittest.mock import create_autospec, patch

import pytest
from decouple import config
from fastapi.testclient import TestClient

from expenses_ai_agent.api.deps import get_expense_repo
from expenses_ai_agent.api.main import app
from expenses_ai_agent.llms.openai import PRICE_PER_MILLION_TOKENS, OpenAIAssistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import (
    ClassificationResult,
    ClassificationService,
)
from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import ExpenseRepository
from expenses_ai_agent.utils.currency import convert_currency
from expenses_ai_agent.utils.exceptions import CurrencyConversionError


@pytest.fixture
def mock_expense_repo():
    repo = create_autospec(ExpenseRepository)
    expenses = [
        Expense(
            id=1,
            amount=Decimal("10.00"),
            currency=Currency.EUR,
            category=ExpenseCategory.FOOD,
            telegram_user_id=12345,
        ),
        Expense(
            id=2,
            amount=Decimal("20.00"),
            currency=Currency.USD,
            category=ExpenseCategory.FOOD,
            telegram_user_id=12345,
        ),
    ]
    repo.list_by_user.return_value = expenses
    repo.get.return_value = expenses[0]
    repo.get_all.return_value = expenses
    return repo


@pytest.fixture
def test_client(mock_expense_repo):
    app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


class TestSecrets:
    @pytest.mark.integration
    def test_convert_currency_same_currency(self):
        """Converting to the same currency should return the original amount."""
        result = convert_currency(Decimal("50.00"), "EUR", "EUR")

        assert result == Decimal("50.00")

    @pytest.mark.integration
    def test_api_keys_accessible(self):
        """All secret keys available, non-empty strings"""
        for api_key in ["EXCHANGE_RATE_API_KEY", "OPENAI_API_KEY"]:
            assert config(api_key, default="")
            assert isinstance(api_key, str)

    @pytest.mark.integration
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

    @pytest.mark.integration
    def test_calculate_cost_correctly(self):
        """
        Call the function, get a correct return.
        """

        # TODO: replace this with a mock?
        assistant = OpenAIAssistant()
        assert assistant.calculate_cost(prompt_tokens=1, completion_tokens=2) == (
            (
                PRICE_PER_MILLION_TOKENS["gpt-4o-mini"]["input"]
                + 2 * PRICE_PER_MILLION_TOKENS["gpt-4o-mini"]["output"]
            )
            / Decimal(1_000_000)
        )

    @pytest.mark.integration
    def test_classify_expense(self, test_client, mock_expense_repo):
        """POST /expenses/classify should classify and store expense."""
        with patch(
            "expenses_ai_agent.api.routes.expenses.ClassificationService"
        ) as mock_cls:
            mock_service = create_autospec(ClassificationService)
            mock_result = create_autospec(ClassificationResult)
            mock_result.response = ExpenseCategorizationResponse(
                category=ExpenseCategory.FOOD,
                total_amount=Decimal("5.50"),
                currency=Currency.USD,
                confidence=0.95,
                cost=Decimal("0.001"),
            )
            mock_result.persisted = True
            mock_service.classify.return_value = mock_result
            mock_cls.return_value = mock_service

            response = test_client.post(
                "/api/v1/expenses/classify",
                json={"description": "Coffee $5.50"},
                headers={"X-User-ID": "12345"},
            )

            assert response.status_code == 201
            data = response.json()
            assert "category" in data

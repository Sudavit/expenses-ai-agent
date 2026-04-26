from decimal import Decimal

import pytest

from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
from expenses_ai_agent.storage.models import Currency, Expense
from expenses_ai_agent.storage.repo import (
    InMemoryExpenseRepository,
)


class TestInMemoryExpenseRepositoryExtras:
    """
    Extra tests for the in-memory expense repository.
    """

    @pytest.fixture
    def repo(self):
        return InMemoryExpenseRepository()

    @pytest.fixture
    def sample_expense(self):
        return Expense(
            amount=Decimal("42.50"),
            currency=Currency.EUR,
            description="Test expense",
        )

    @pytest.fixture
    def sample_expense_2(self):
        return Expense(
            amount=Decimal("50.42"),
            currency=Currency.GBP,
            description="Second test expense",
        )

    def test_update_expense_by_id(self, repo, sample_expense, sample_expense_2):
        """Should retrieve expense by ID."""
        repo.add(sample_expense)
        old_sample_expense = repo.get(sample_expense.id)

        assert old_sample_expense.amount != sample_expense_2.amount
        assert old_sample_expense.currency != sample_expense_2.currency
        assert old_sample_expense.description != sample_expense_2.description
        assert sample_expense_2.id is None

        repo.update(sample_expense.id, sample_expense_2)

        new_sample_expense = repo.get(sample_expense.id)
        assert new_sample_expense.amount == sample_expense_2.amount
        assert new_sample_expense.currency == sample_expense_2.currency
        assert new_sample_expense.description == sample_expense_2.description
        assert new_sample_expense.id == old_sample_expense.id

    def test_get_nonexistent_returns_none(self, repo, sample_expense_2):
        """Updating a non-existent expense should raise ExpenseNotFoundError."""
        with pytest.raises(ExpenseNotFoundError):
            repo.update(999, sample_expense_2)

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from expenses_ai_agent.api import deps
from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.api.main import app
from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
from expenses_ai_agent.storage.models import Currency, ExpenseCategory

client = TestClient(app)

# Create mock objects for the dependencies
mock_repo = MagicMock()


# Define dependency override functions
def override_expense_repo():
    return mock_repo


def override_user_id():
    return 42  # Base user ID for testing


@pytest.fixture(autouse=True)
def setup_dependencies():
    """Sets up and clears dependency overrides for each test."""
    # Override using explicit module references to eliminate import mismatches
    app.dependency_overrides[get_expense_repo] = override_expense_repo
    app.dependency_overrides[get_user_id] = override_user_id
    app.dependency_overrides[deps.get_expense_repo] = override_expense_repo
    app.dependency_overrides[deps.get_user_id] = override_user_id

    yield

    app.dependency_overrides.clear()
    mock_repo.reset_mock()
    mock_repo.get.side_effect = None
    mock_repo.delete.side_effect = None


class TestGetExpenseEndpoint:
    ROUTE_URL = "/api/v1/expenses/1"

    def test_get_expense_success(self):
        # Arrange: Mock a matching expense object
        mock_expense = MagicMock()
        mock_expense.id = 1
        mock_expense.telegram_user_id = 42  # Matches override_user_id
        mock_expense.amount: Decimal = Decimal("15.50")
        mock_expense.category: ExpenseCategory = ExpenseCategory.FOOD
        mock_expense.description = "test"
        mock_expense.date = "2026-05-30T12:00:00"  # Mock timestamp if required
        mock_expense.currency: Currency = Currency.USD
        mock_repo.get.return_value = mock_expense

        # Act
        response = client.get(self.ROUTE_URL)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_repo.get.assert_called_once_with(1)

    def test_get_expense_wrong_user_returns_404(self):
        # Arrange: Mock an expense belonging to a different user
        mock_expense = MagicMock()
        mock_expense.id = 1
        mock_expense.telegram_user_id = 999  # Does NOT match override_user_id
        mock_repo.get.return_value = mock_expense

        # Act
        response = client.get(self.ROUTE_URL)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Expense with id 1 not found"

    def test_get_expense_not_found_exception_returns_404(self):
        # Arrange: Force the mock repo to raise the specific error
        mock_repo.get.side_effect = ExpenseNotFoundError(expense_id=1)

        # Act
        response = client.get(self.ROUTE_URL)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Expense with id 1 not found"

    def test_print_routes(self):
        for route in app.routes:
            # 💡 Use getattr with a fallback to safely handle all Route variations
            path = getattr(route, "path", "No path attribute available")
            name = getattr(route, "name", "No name attribute available")
            print(f"Path: {path} -> Name: {name}")


class TestDeleteExpenseEndpoint:
    ROUTE_URL = "/api/v1/expenses/1"

    def test_delete_expense_success(self):
        mock_expense = MagicMock()
        mock_expense.id = 1
        mock_expense.telegram_user_id = 42  # Matches override_user_id
        mock_repo.get.return_value = mock_expense

        mock_repo.delete.side_effect = None

        response = client.delete(self.ROUTE_URL)

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_expense_wrong_user_returns_404(self):
        # Arrange: Mock an expense belonging to a different user

        mock_expense = MagicMock()
        mock_expense.id = 1
        mock_expense.telegram_user_id = 999  # Does NOT match override_user_id
        mock_repo.get.return_value = mock_expense

        # Act
        response = client.delete(self.ROUTE_URL)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Expense with id 1 not found"

    def test_delete_expense_not_found_exception_returns_404(self):
        # Arrange: Force the mock repo to raise the specific error
        mock_repo.delete.side_effect = ExpenseNotFoundError(expense_id=1)

        # Act
        response = client.delete(self.ROUTE_URL)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Expense with id 1 not found"

    def test_print_routes(self):
        for route in app.routes:
            # 💡 Use getattr with a fallback to safely handle all Route variations
            path = getattr(route, "path", "No path attribute available")
            name = getattr(route, "name", "No name attribute available")
            print(f"Path: {path} -> Name: {name}")

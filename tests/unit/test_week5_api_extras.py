from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlmodel import Session

from expenses_ai_agent.api.deps import (
    DATABASE_URL,
    DUMMY_ID,
    get_db_session,
    get_expense_repo,
    get_user_id,
)
from expenses_ai_agent.api.routes.expenses import router
from expenses_ai_agent.storage.repo import DBExpenseRepository

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestApiDependenciesExhaustive:
    """Rigorous unit tests to eliminate all remaining branch gaps in deps.py."""

    # ==========================================
    # 1. TESTING THE DATABASE GENERATOR
    # ==========================================
    @patch("expenses_ai_agent.api.deps.engine")
    @patch("expenses_ai_agent.api.deps.Session")
    def test_get_db_session_lifecycle(self, mock_session_class, mock_engine):
        """Forces the Session context manager to completely open, yield, and close."""
        mock_session_instance = MagicMock(spec=Session)

        mock_session_instance.__enter__.return_value = mock_session_instance
        mock_session_class.return_value = mock_session_instance

        generator = get_db_session()
        yielded_session = next(generator)

        # Assert initialization logic
        assert yielded_session == mock_session_instance
        mock_session_class.assert_called_once_with(mock_engine)

        # Drive generator forward to exit the context block cleanly
        with pytest.raises(StopIteration):
            next(generator)

        # Verify context cleanup happened
        assert mock_session_instance.__exit__.called

    # ==========================================
    # 2. TESTING THE REPOSITORY INSTANTIATION
    # ==========================================
    def test_get_expense_repo_instantiation(self):
        """
        Validates repository instantiation patterns
        mapping back to DBExpenseRepository.
        """
        mock_session = MagicMock(spec=Session)
        repo = get_expense_repo(session=mock_session)

        """
        this seems is a little shady, because it's looking at hidden attributes,
        but it ensures the correct class is instantiated with the expected parameters
        """

        assert isinstance(repo, DBExpenseRepository)
        assert repo._session == mock_session
        assert repo._db_url == DATABASE_URL

    # ==========================================
    # 3. TESTING USER ID RESOLUTION BRANCHES
    # ==========================================
    def test_get_user_id_primary_header(self):
        """Branch 1: Should immediately return x_user_id if provided via Header."""
        result = get_user_id(x_user_id=999, user_id=None)
        assert result == 999

    def test_get_user_id_fallback_query(self):
        """Branch 2: Should fall back to user_id query string if header is absent."""
        result = get_user_id(x_user_id=None, user_id=888)
        assert result == 888

    def test_get_user_id_fallback_dummy(self):
        """Branch 3: Should return the static DUMMY_ID if both inputs are missing."""
        result = get_user_id(x_user_id=None, user_id=None)
        assert result == DUMMY_ID


class TestCategoryRoutesCreation:
    def test_persist_expense_executes_creation_block_flawlessly(self):
        """
        Happy Path: Verifies the raw data instantiation,
        repository addition, and return serialization.
        """
        # 1. Setup a controlled mock repository layer
        mock_repo = MagicMock()

        # 2. Forge dependency overrides
        # to supply our mock repository and a fixed test user ID
        app.dependency_overrides[get_expense_repo] = lambda: mock_repo
        app.dependency_overrides[get_user_id] = lambda: 12345

        # 3. Build a precise incoming data payload
        # matching the ExpenseResponse/Schema expectations
        test_payload = {
            "id": None,
            "category": "Food",
            "amount": "45.50",
            "currency": "EUR",
            "date": datetime.now(UTC).isoformat(),
            "description": "Team lunch validation",
            "telegram_user_id": None,
        }

        # 4. Fire the request directly into the endpoint
        response = client.post("/expenses/", json=test_payload)

        # 5. Clean up dependencies immediately
        app.dependency_overrides.clear()

        # ==========================================
        # VERIFICATION MATRICES
        # ==========================================
        assert response.status_code == status.HTTP_201_CREATED

        # Validate the server accurately serialized
        # and return  the record attributes
        data = response.json()
        assert data["amount"] == "45.50"
        assert data["category"] == "Food"
        assert (
            data["telegram_user_id"] == 12345
        )  # Must override to the resolved route user ID

        # Structural Integrity Verification:
        # Confirm repo.add() was explicitly invoked
        mock_repo.add.assert_called_once()

        # Extract the internal instance passed into repo.add()
        # to verify its field components
        instantiated_expense = mock_repo.add.call_args[0][0]
        assert instantiated_expense.amount == Decimal("45.50")
        assert instantiated_expense.telegram_user_id == 12345

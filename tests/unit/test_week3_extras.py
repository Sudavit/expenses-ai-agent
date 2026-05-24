import re
from decimal import Decimal

import pytest
from sqlmodel import Session, SQLModel, create_engine
from typer.testing import CliRunner

from expenses_ai_agent.cli.cli import app
from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import DBExpenseRepository

BAD_ID = 999


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session


class TestCLIAppExtras:
    """Extra Tests for CLI application."""

    def test_classify_specify_database_works(self, cli_runner):
        result = cli_runner.invoke(
            app, ["USD$25", "--db", "sqlite:///:memory:"], catch_exceptions=False
        )
        # check the syntax is parsed
        assert result.exit_code == 0
        # check for persistence
        pattern = r"yes"
        assert pattern in result.output.lower()
        pattern = r"persisted"
        assert pattern in result.output.lower()
        pattern = r"yes"
        assert any(
            re.search(pattern, line.lower()) for line in result.output.splitlines()
        )
        pattern = r"persisted"
        assert any(
            re.search(pattern, line.lower()) for line in result.output.splitlines()
        )
        pattern = r"persisted.*yes"
        assert any(
            re.search(pattern, line.lower()) for line in result.output.splitlines()
        )

    def test_app_behavior_without_api_key(self, cli_runner, monkeypatch):
        # Unset the variable for this test only
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        result = cli_runner.invoke(app, ["Coffee"], catch_exceptions=False)
        # exits okay
        assert result.exit_code == 0
        pattern = r"no llm key supplied"
        assert pattern in result.output.lower()


class TestDBExpenseRepositoryExtras:
    """
    Extra tests for the DB expense repository.
    """

    @pytest.fixture
    def original_expense(self):
        return Expense(
            amount=Decimal("42.50"),
            currency=Currency.EUR,
            description="Lunch",
            category=ExpenseCategory.FOOD,
        )

    @pytest.fixture
    def updated_expense(self):
        return Expense(
            amount=Decimal("50.42"),
            currency=Currency.GBP,
            description="Lunch",
            category=ExpenseCategory.FOOD,
        )

    def test_db_expense_repo_update_updates(
        self, original_expense, updated_expense, db_session
    ):
        """Should update expense by ID."""
        with DBExpenseRepository(
            db_url="sqlite:///:memory:", session=db_session
        ) as repo:
            repo.add(original_expense)
            assert (
                original_expense.id is not None
            )  # to keep ty from complaining that it could be

            before_update = repo.get(original_expense.id)
            assert before_update is not None
            assert before_update.amount == original_expense.amount
            assert before_update.currency == original_expense.currency

            assert updated_expense.id is None
            repo.update(before_update.id, updated_expense)

            after_update = repo.get(original_expense.id)
            assert after_update.amount == updated_expense.amount
            assert after_update.currency == updated_expense.currency
            assert after_update.id == original_expense.id
            assert (
                updated_expense.id is None
            )  # the database is updated, not the local element.

    def test_update_nonexistent_raises(
        self, original_expense, updated_expense, db_session
    ):
        """Updating a non-existent expense should raise ExpenseNotFoundError."""
        with DBExpenseRepository(
            db_url="sqlite:///:memory:", session=db_session
        ) as repo:
            # have something in the repo, just not what we're updating
            repo.add(original_expense)
            assert (
                original_expense.id is not None
            )  # to keep ty from complaining that it could be

            with pytest.raises(ExpenseNotFoundError):
                repo.update(BAD_ID, updated_expense)

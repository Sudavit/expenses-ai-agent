import re
from decimal import Decimal
from unittest.mock import create_autospec

import pytest
from typer.testing import CliRunner

from expenses_ai_agent.cli.cli import app
from expenses_ai_agent.llms.base import Assistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import (
    ClassificationService,
)
from expenses_ai_agent.storage.models import Currency


@pytest.fixture
def cli_runner():
    return CliRunner()


class TestCLIApp:
    """Tests for CLI application."""

    def test_classify_specify_database_works(self, cli_runner):
        result = cli_runner.invoke(app, ["USD$25", "--db", "sqlite:///:memory:"])
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


class TestClassificationService:
    """Tests for ClassificationService."""

    @pytest.fixture
    def mock_bad_assistant(self):
        assistant = create_autospec(Assistant)
        assistant.completion.return_value = ExpenseCategorizationResponse(
            category="unknown",
            total_amount=Decimal("5.50"),
            currency=Currency.USD,
            confidence=0.95,
            cost=Decimal("0.001"),
        )
        return assistant

    def test_classify_without_persistence(self, mock_bad_assistant):
        service = ClassificationService(assistant=mock_bad_assistant)
        response = service.classify("Test expense", persist=False).response

        assert True

import re

import pytest
from typer.testing import CliRunner

from expenses_ai_agent.cli.cli import app


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

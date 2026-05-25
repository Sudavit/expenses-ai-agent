"""
Build `cli/cli.py` using Typer:

- `app = typer.Typer()` — the Typer application (imported as `app` in tests)
- `classify` command — takes `description: str` as argument and `--db` as a flag
  - Without `--db`: classifies and prints result, does not persist
  - With `--db`: classifies and persists to the database
- Use Rich for formatted output via a private `_display_result(result)` helper:
"""

from contextlib import nullcontext

import typer
from decouple import config
from rich.console import Console
from rich.table import Table

from expenses_ai_agent.llms.exceptions import LLMNoKeyError
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.services.classification import (
    ClassificationResult,
    ClassificationService,
)
from expenses_ai_agent.storage.repo import DBExpenseRepository

app = typer.Typer(
    name="expenses-ai-agent",
    help="AI-powered expense classification",
)
console = Console()


@app.command()
def classify(
    description: str = typer.Argument(..., help="Expense description"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="provide exception traceback."
    ),
    db_name: str | None = typer.Option(
        None,
        "--db",
        help=(
            "Persist to named database (path or URL, e.g., '--db sqlite:///my_purchases.db')."
            " Use '--db default' use sqlite:///expenses.db [or $DATABASE_URL if set]."
        ),
    ),
):
    """Classify an expense using AI."""
    persist = db_name is not None

    try:
        assistant = OpenAIAssistant(model="gpt-4o-mini")
    except LLMNoKeyError as e:
        console.print(f"[green]No LLM Key Supplied: {e}[/green]")
        # TODO: instead of immediately exiting,
        #   this path can permit other LLM-free usage
        if verbose:
            console.print_exception()
        raise typer.Exit(code=0)

    try:
        db_url = config("DATABASE_URL", default="sqlite:///expenses.db") if db_name == "default" else db_name
        repo_ctx = DBExpenseRepository(db_url=db_url) if db_url else nullcontext()
        with repo_ctx as repo:
            service = ClassificationService(assistant=assistant, expense_repo=repo)
            result = service.classify(description, persist=persist)
            _display_result(result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


def _display_result(result: ClassificationResult) -> None:
    table = Table(title="Classification Result")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    response = result.response
    table.add_row("Category", response.category)
    table.add_row("Amount", str(response.total_amount))
    table.add_row("Currency", str(response.currency))
    table.add_row("Confidence", f"{response.confidence:.0%}")
    table.add_row("Persisted", "Yes" if result.persisted else "No")

    console.print(table)



"""
Build `cli/cli.py` using Typer:

- `app = typer.Typer()` — the Typer application (imported as `app` in tests)
- `classify` command — takes `description: str` as argument and `--db` as a flag
  - Without `--db`: classifies and prints result, does not persist
  - With `--db`: classifies and persists to the database
- Use Rich for formatted output via a private `_display_result(result)` helper:
"""

import typer
from decouple import config
from rich.console import Console
from rich.table import Table

from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.services.classification import (
    ClassificationResult,
    ClassificationService,
)
from expenses_ai_agent.storage.repo import DBExpenseRepo

app = typer.Typer(
    name="expenses-ai-agent",
    help="AI-powered expense classification",
)
console = Console()


@app.command()
def classify(
    description: str = typer.Argument(..., help="Expense description"),
    db: bool = typer.Option(False, "--db", help="Persist to database"),
):
    """Classify an expense using AI."""
    try:
        service = _build_service(db=db)
        result = service.classify(description, persist=db)
        _display_result(result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
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


def _build_service(db: bool) -> ClassificationService:
    assistant = OpenAIAssistant(model="gpt-4o-mini")
    expense_repo = DBExpenseRepo(db_url=config("DATABASE_URL")) if db else None
    return ClassificationService(assistant=assistant, expense_repo=expense_repo)

"""
- `__init__(self, model: str = "gpt-4o-mini", api_key: str | None = None)` — loads `OPENAI_API_KEY` from env via `config()` if `api_key` is not passed; creates `OpenAI` client
- `completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse` — calls `client.beta.chat.completions.parse()` with `response_format=ExpenseCategorizationResponse`; sets `result.cost` from `calculate_cost()` before returning
- `calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal` — return a cost estimate based on token counts
- `get_available_models(self) -> list[str]` — calls `client.models.list()` and returns model IDs

Use `client.beta.chat.completions.parse()` — OpenAI's structured output API that parses the response directly into a Pydantic model.

**None checks required:** The OpenAI SDK types `message.parsed` as `ExpenseCategorizationResponse | None` and `response.usage` as `CompletionUsage | None`. Your `completion` implementation must handle both:
"""  # noqa: E501

from collections.abc import Sequence
from decimal import Decimal

from expenses_ai_agent.llms.base import MESSAGES
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse


def OpenAIAssistant(model, api_key):
    def __init__(self, model=model, api_key=api_key):
        self.model = model
        self.api_key = api_key

    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        resp = ExpenseCategorizationResponse(
            category="Yo Mama",
            total_amount=Decimal("0.00"),
            confidence=0.0,
        )

        return resp

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        return Decimal("0.00")

    def get_available_models(self) -> Sequence[str]:
        return []

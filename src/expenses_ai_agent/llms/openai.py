"""
- `__init__(self, model: str = "gpt-4o-mini", api_key: str | None = None)` — loads `OPENAI_API_KEY` from env via `config()` if `api_key` is not passed; creates `OpenAI` client
- `completion(self, messages: Messages) -> ExpenseCategorizationResponse` — calls `client.beta.chat.completions.parse()` with `response_format=ExpenseCategorizationResponse`; sets `result.cost` from `calculate_cost()` before returning
- `calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal` — return a cost estimate based on token counts
- `get_available_models(self) -> list[str]` — calls `client.models.list()` and returns model IDs

Use `client.beta.chat.completions.parse()` — OpenAI's structured output API that parses the response directly into a Pydantic model.

**None checks required:** The OpenAI SDK types `message.parsed` as `ExpenseCategorizationResponse | None` and `response.usage` as `CompletionUsage | None`. Your `completion` implementation must handle both:
"""  # noqa: E501

from collections.abc import Sequence
from decimal import Decimal
from typing import Any, cast

from decouple import UndefinedValueError, config
from openai import OpenAI

from expenses_ai_agent.llms.base import Messages
from expenses_ai_agent.llms.exceptions import LLMParseError
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse

PRICE_PER_MILLION_TOKENS = {
    "gpt-5.5": {
        "input": Decimal("5.00"),
        "cached_input": Decimal("0.50"),
        "output": Decimal("30.00"),
    },
    "gpt-5.4": {
        "input": Decimal("2.50"),
        "cached_input": Decimal("0.25"),
        "output": Decimal("15.00"),
    },
    "gpt-5.4-mini": {
        "input": Decimal("0.75"),
        "cached_input": Decimal("0.075"),
        "output": Decimal("4.50"),
    },
}


class OpenAIAssistant:
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        if api_key is None:
            self.api_key = config("OPENAI_API_KEY", default="")
        else:
            self.api_key = api_key
        if not self.api_key:
            raise UndefinedValueError("OPENAI_API_KEY must be set")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def completion(self, messages: Messages) -> ExpenseCategorizationResponse | None:
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=cast(Any, messages),
            response_format=ExpenseCategorizationResponse,
        )
        result = response.choices[0].message.parsed
        if result is None:
            raise LLMParseError("Failed to parse response from OpenAI")

        if response.usage:
            result.cost = self.calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
            )
        return result

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        # OpenAI pricing page is here: https://openai.com/api/pricing/
        return Decimal("0.00")

    def get_available_models(self) -> Sequence[str]:
        models = [model.id for model in self.client.models.list()]
        return models

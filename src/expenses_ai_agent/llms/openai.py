"""
- `__init__(self, model: str = "gpt-4o-mini", api_key: str | None = None)` — loads `OPENAI_API_KEY` from env via `config()` if `api_key` is not passed; creates `OpenAI` client
- `completion(self, messages: Messages) -> ExpenseCategorizationResponse` — calls `client.beta.chat.completions.parse()` with `response_format=ExpenseCategorizationResponse`; sets `result.cost` from `calculate_cost()` before returning
- `calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal` — return a cost estimate based on token counts
- `get_available_models(self) -> list[str]` — calls `client.models.list()` and returns model IDs

Use `client.beta.chat.completions.parse()` — OpenAI's structured output API that parses the response directly into a Pydantic model.

**None checks required:** The OpenAI SDK types `message.parsed` as `ExpenseCategorizationResponse | None` and `response.usage` as `CompletionUsage | None`. Your `completion` implementation must handle both:
"""  # noqa: E501

from decimal import Decimal
from typing import Any, cast

# from decouple import config
from openai import OpenAI

from expenses_ai_agent.conf.config import get_api_config
from expenses_ai_agent.llms.base import Messages
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse


class OpenAIAssistant:
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        if api_key is None:
            self.api_key = get_api_config("OPENAI_API_KEY")
        else:
            self.api_key = api_key
        self.model = model
        self.client = OpenAI()

    def completion(self, messages: Messages) -> ExpenseCategorizationResponse | None:
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=cast(Any, messages),
            response_format=ExpenseCategorizationResponse,
        )
        result = response.choices[0].message.parsed
        if result is None:
            raise ValueError("Failed to parse response from OpenAI")

        if response.usage:
            result.cost = self.calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
            )
        return result

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        # do something here
        return Decimal("0.00")

    # def get_available_models(self) -> Sequence[str]:
    def get_available_models(self) -> list[str]:
        models = [model.id for model in self.client.models.list()]
        return models

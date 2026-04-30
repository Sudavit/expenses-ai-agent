"""
- `Messages = list[dict[str, str]]` — type alias for chat message lists
- `Cost = dict[str, list[Decimal]]` — type alias for cost tracking
- `LLMProvider(StrEnum)` — with `OPENAI` and `GROQ` values
- `Assistant(Protocol)` — with these method signatures:
  - `completion(self, messages: Messages) -> ExpenseCategorizationResponse`
  - `calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal`
  - `get_available_models(self) -> Sequence[str]`
"""

# TODO:  collections.abc.Sequence == 'typing.Sequence'
# and the latter is deprecated
from collections.abc import Sequence
from decimal import Decimal
from enum import StrEnum, auto
from typing import Protocol

from expenses_ai_agent.llms.output import ExpenseCategorizationResponse

type Messages = list[dict[str, str]]  # type alias for chat message lists

type Cost = dict[str, list[Decimal]]  # type alias for cost tracking


class LLMProvider(StrEnum):
    OPENAI = auto()
    GROQ = auto()


class Assistant(Protocol):
    def completion(self, messages: Messages) -> ExpenseCategorizationResponse: ...
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal: ...
    def get_available_models(self) -> Sequence[str]: ...

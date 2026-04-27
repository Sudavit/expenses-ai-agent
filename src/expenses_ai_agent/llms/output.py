r"""
Create `ExpenseCategorizationResponse` in `llms/output.py`. It needs these fields:

| Field | Type | Notes |
|-------|------|-------|
| `category` | `str` | required |
| `total_amount` | `Decimal` | required, add `Field(description="Numeric amount extracted from the expense description")` |
| `currency` | `Currency` | required, from `storage.models`, add `Field(description="Currency code from the description, default EUR")` |
| `confidence` | `float` | required, add `Field(description="Confidence score 0.0-1.0")` |
| `cost` | `Decimal` | `Field(default=Decimal("0"), description="Leave as 0 — set programmatically after the API call")` |
| `comments` | `str \| None` | optional, defaults to `None` |
| `timestamp` | `datetime` | auto-set via `default_factory` |

The `Field(description=...)` on each field is important — OpenAI's structured output passes the description to the LLM, which uses it to know what value to fill in. Without descriptions, the LLM may fill numeric fields with `0`.

`uv run pytest tests/unit/test_week2.py -k TestExpenseCategorizationResponse` (5 tests)
"""


class ExpenseCategorizationResponse:
    pass

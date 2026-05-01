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
"""  # noqa: E501

from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from expenses_ai_agent.storage.models import Currency


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ExpenseCategorizationResponse(BaseModel):
    category: str
    total_amount: Decimal = Field(
        description="Numeric amount extracted from the expense description"
    )
    currency: Currency = Field(
        description="Currency code from the description, default EUR"
    )
    confidence: float = Field(description="Confidence score 0.0-1.0")
    cost: Decimal = Field(
        default=Decimal("0"),
        description="Leave as 0 — set programmatically after the API call",
    )
    comments: str | None = None
    timestamp: datetime = Field(default_factory=_utc_now)

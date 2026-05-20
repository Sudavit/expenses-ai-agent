from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from expenses_ai_agent.storage.models import Currency, ExpenseCategory


class ExpenseClassifyRequest(BaseModel):
    description: str = Field(
        ...,  # Required field
        min_length=3,
        max_length=500,
        examples=["Coffee at Starbucks $5.50"],
    )

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("description cannot be empty or whitespace")
        return stripped


class ExpenseClassifyResponse(BaseModel):
    """Response body after expense classification."""

    id: int
    category: str
    amount: Decimal
    currency: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ExpenseResponse(BaseModel):
    """Single expense in a list."""

    id: int | None
    category: ExpenseCategory | None
    amount: Decimal
    currency: Currency
    date: datetime
    description: str | None  # TODO: Not in "Response Schemas"
    telegram_user_id: int | None  # TODO: Not in "Response Schemas"

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int


"""
TODO: where's this go?
expense = repo.get(expense_id)
return ExpenseClassifyResponse.model_validate(expense)
"""

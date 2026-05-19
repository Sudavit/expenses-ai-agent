from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from expenses_ai_agent.storage.models import Currency, ExpenseCategory


class ExpenseClassifyRequest(BaseModel):
    description: str


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None
    amount: Decimal
    currency: Currency
    date: datetime
    description: str | None
    telegram_user_id: int | None
    category: ExpenseCategory | None


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int

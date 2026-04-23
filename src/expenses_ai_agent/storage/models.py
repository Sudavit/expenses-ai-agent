from datetime import UTC, datetime
from decimal import Decimal
from enum import UNIQUE, StrEnum, auto, verify
from typing import Any, Self

from sqlmodel import Field, SQLModel


@verify(UNIQUE)
class Currency(StrEnum):
    EUR = auto()
    USD = auto()
    GBP = auto()
    JPY = auto()
    CHF = auto()
    CAD = auto()
    AUD = auto()
    CNY = auto()
    INR = auto()
    MXN = auto()


@verify(UNIQUE)
class ExpenseCategory(StrEnum):
    FOOD = auto()
    TRANSPORT = auto()
    ENTERTAINMENT = auto()
    SHOPPING = auto()
    HEALTH = auto()
    BILLS = auto()
    EDUCATION = auto()
    TRAVEL = auto()
    SERVICES = auto()
    GIFTS = auto()
    INVESTMENTS = auto()
    OTHER = auto()


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal = Field(default=Decimal("0.00"))
    currency: Currency = Field(default=Currency.EUR)
    date: datetime = Field(default_factory=_utc_now)
    description: str | None = Field(default="No description provided")
    telegram_user_id: int | None = Field(default=None)
    category: ExpenseCategory | None = Field(default=ExpenseCategory.OTHER)

    def __str__(self) -> str:
        return (
            f"{self.description or 'Expense'}: {self.amount} "
            f"{self.currency.value} ({self.category})"
        )

    @classmethod
    def create(cls, **kwargs: Any) -> Self:
        """
        Factory method to create an Expense using keyword arguments.
        Strictly forbidden: float-based currency operations.
        """
        # kwargs now collects amount, currency, description, etc. into a dict
        # and we unpack them again into the constructor.
        return cls(**kwargs)

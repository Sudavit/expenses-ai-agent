from datetime import UTC, datetime
from decimal import Decimal
from enum import UNIQUE, StrEnum, verify
from typing import Any, Self

from sqlmodel import Field, SQLModel


@verify(UNIQUE)
class Currency(StrEnum):
    EUR = ("EUR",)
    USD = ("USD",)
    GBP = ("GBP",)
    JPY = ("JPY",)
    CHF = ("CHF",)
    CAD = ("CAD",)
    AUD = ("AUD",)
    CNY = ("CNY",)
    INR = ("INR",)
    MXN = ("MXN",)


@verify(UNIQUE)
class ExpenseCategory(StrEnum):
    FOOD = ("Food",)
    TRANSPORT = ("Transport",)
    ENTERTAINMENT = ("Entertainment",)
    SHOPPING = ("Shopping",)
    HEALTH = ("Health",)
    BILLS = ("Bills",)
    EDUCATION = ("Education",)
    TRAVEL = ("Travel",)
    SERVICES = ("Services",)
    GIFTS = ("Gifts",)
    INVESTMENTS = ("Investments",)
    OTHER = ("Other",)


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal = Field(default=Decimal("0.00"))
    currency: Currency = Field(default=Currency.EUR)
    date: datetime = Field(default_factory=_utc_now)
    description: str | None = Field(default="No description provided")
    telegram_user_id: int | None = None
    category: ExpenseCategory | None = Field(default=ExpenseCategory.OTHER)

    @classmethod
    def create(cls, **kwargs: Any) -> Self:
        """
        Factory method to create an Expense using keyword arguments.
        Strictly forbidden: float-based currency operations.
        """
        # kwargs now collects amount, currency, description, etc. into a dict
        # and we unpack them again into the constructor.
        return cls(**kwargs)

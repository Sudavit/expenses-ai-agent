from enum import UNIQUE, StrEnum, verify


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

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

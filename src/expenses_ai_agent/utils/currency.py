from decimal import Decimal

import requests
from decouple import UndefinedValueError, config

from expenses_ai_agent.utils.exceptions import CurrencyConversionError

EXCHANGE_RATE_API_KEY = config("EXCHANGE_RATE_API_KEY", default="")


def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    """
    - If `from_currency == to_currency`, return `amount` unchanged (no API call)
    - Otherwise use `requests.get` to call the ExchangeRate API pair endpoint:
      `https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}`
    - The response JSON contains a `conversion_rate` key — multiply `amount` by it
    - Load `EXCHANGE_RATE_API_KEY` from environment variables via `python-decouple`
    """

    if not EXCHANGE_RATE_API_KEY:
        raise UndefinedValueError("EXCHANGE_RATE_API_KEY must be set")

    if from_currency == to_currency:
        return amount

    response = requests.get(
        f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{from_currency}/{to_currency}"
    )
    data = response.json()
    if data["result"] != "success":
        raise CurrencyConversionError(f"{data['error-type']}")
    rate = Decimal(data["conversion_rate"])
    return rate * amount

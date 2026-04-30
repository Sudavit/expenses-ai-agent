from enum import StrEnum

from decouple import UndefinedValueError, config


# perhaps this should use auto()
class SecretKey(StrEnum):
    EXCHANGE_RATE_API_KEY = "EXCHANGE_RATE_API_KEY"
    OPENAI_API_KEY = "OPENAI_API_KEY"


def get_api_config(key: str):
    try:
        return config(key)
    except UndefinedValueError:
        raise UndefinedValueError

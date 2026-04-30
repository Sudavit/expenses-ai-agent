import sys
from enum import StrEnum

from decouple import UndefinedValueError, config


# perhaps this should use auto()
class SecretKey(StrEnum):
    EXCHANGE_RATE_API_KEY = "EXCHANGE_RATE_API_KEY"
    OPENAI_API_KEY = "OPENAI_API_KEY"


def get_api_config(key: str):
    try:
        # decouple automatically checks the environment FIRST,
        # then falls back to the .env file.
        # api_secret = config("API_SECRET")

        # return api_key, api_secret
        return config(key)
    except UndefinedValueError as e:
        # Fail fast if the configuration is missing
        print(f"Configuration Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # key, secret = get_api_config()
    EXCHANGE_RATE_API_KEY = get_api_config(SecretKey.EXCHANGE_RATE_API_KEY)
    OPENAI_API_KEY = get_api_config("OPENAI_API_KEY")
    print("Configuration loaded successfully.")

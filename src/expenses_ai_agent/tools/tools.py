"""
Create `tools/tools.py` with two module-level dicts following the OpenAI tool schema format (see Helpful References):

- `CURRENCY_CONVERSION_TOOL` — for `convert_currency`; `amount`, `from_currency`, `to_currency` are all required
- `DATETIME_FORMATTER_TOOL` — for `format_datetime`; `datetime_str` is required, `timezone_str` is optional
"""  # noqa: E501

OPENAI_TOOL_META_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"const": "function"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "parameters": {
            "type": "object",
            "properties": {
                "type": {"const": "object"},
                "properties": {"type": "object"},
                "required": {"type": "array", "items": {"type": "string"}},
                "additionalProperties": {"type": "boolean"},
            },
            "required": ["type", "properties", "required", "additionalProperties"],
            "additionalProperties": False,
        },
        "strict": {"type": "boolean"},
    },
    "required": ["type", "name", "description", "parameters"],
    "additionalProperties": False,
}

CURRENCY_CONVERSION_TOOL = {
    "type": "function",
    "name": "convert_currency",
    "description": "Convert a specific amount from one currency to another using ISO codes.",  # noqa: E501
    "parameters": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "string",
                "description": "The numerical amount to convert (e.g., 150.50).",
            },
            "from_currency": {
                "type": "string",
                "description": "The 3-letter ISO 4217 code of the source currency.",
                "enum": [
                    "EUR",
                    "USD",
                    "GBP",
                    "JPY",
                    "CHF",
                    "CAD",
                    "AUD",
                    "CNY",
                    "INR",
                    "MXN",
                ],
            },
            "to_currency": {
                "type": "string",
                "description": "The 3-letter ISO 4217 code of the target currency.",
                "enum": [
                    "EUR",
                    "USD",
                    "GBP",
                    "JPY",
                    "CHF",
                    "CAD",
                    "AUD",
                    "CNY",
                    "INR",
                    "MXN",
                ],
            },
        },
        "required": ["amount", "from_currency", "to_currency"],
        "additionalProperties": False,
    },
    "strict": True,  # Guarantees the output matches this schema exactly
}

DATETIME_FORMATTER_TOOL = {
    "type": "function",
    "name": "format_datetime",
    "description": "Reformat ISO datetime string to be human-friendly, converting timezone if needed.",  # noqa: E501
    "parameters": {
        "type": "object",
        "properties": {
            "datetime_str": {
                "type": "string",
                "description": "An ISO 8601 datetime string (e.g., '2023-10-25T14:30:00Z').",  # noqa: E501
            },
            "timezone_str": {
                "type": "string",
                "description": "IANA timezone string for final time (e.g., 'America/New_York' or 'Europe/London').",  # noqa: E501
            },
        },
        "required": [
            "datetime_str",
            "timezone_str",
        ],  # Both must be required for Strict Mode
        "additionalProperties": False,
    },
    "strict": True,
}

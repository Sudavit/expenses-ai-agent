"""
Create `tools/tools.py` with two module-level dicts following the OpenAI tool schema format (see Helpful References):

- `CURRENCY_CONVERSION_TOOL` — for `convert_currency`; `amount`, `from_currency`, `to_currency` are all required
- `DATETIME_FORMATTER_TOOL` — for `format_datetime`; `datetime_str` is required, `timezone_str` is optional
"""  # noqa: E501

CURRENCY_CONVERSION_TOOL = {
    "type": "function",
    "name": "convert_currency",
    "description": "Convert currency amount from one currency to another",
    "parameters": {
        "type": "object",
        "properties": {
            "amount": {"type": "Decimal", "description": "Amount in original currency"},
            "from_currency": {
                "type": "string",
                "description": "ISO name of original currency",
            },
            "to_currency": {
                "type": "string",
                "description": "ISO name of currency being converted to",
            },
        },
        "required": ["amount", "from_currency", "to_currency"],
        "additionalProperties": False,
    },
}


DATETIME_FORMATTER_TOOL = {
    "type": "function",
    "name": "format_datetime",
    "description": "reformat ISO datetime string to be human-friendly, converting timezone if needed",  # noqa: E501
    "parameters": {
        "type": "object",
        "properties": {
            "datetime_str": {"type": "string", "description": "An ISO datetime string"},
            "timezone_str": {
                "type": "string",
                "description": "timezone to use in final, displayed time",
            },
        },
        "required": ["datetime_str"],
        "additionalProperties": False,
    },
}

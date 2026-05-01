class CurrencyConversionError(Exception):
    def __init__(self, error_type: str):
        self.error_type = error_type
        super().__init__(f"Currency conversion failure with error type: {error_type}")

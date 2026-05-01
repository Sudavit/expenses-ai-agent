class LLMParseError(Exception):
    def __init__(self, error_str: str):
        self.error_str = error_str
        super().__init__(error_str)

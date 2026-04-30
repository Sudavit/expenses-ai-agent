class ExpenseNotFoundError(Exception):
    def __init__(self, expense_id: int):
        self.expense_id = expense_id
        super().__init__(f"Expense with id {expense_id} not found")


class CurrencyConversionError(Exception):
    def __init__(self, error_type: str):
        self.error_type = error_type
        super().__init__(f"Currency conversion failure with error type: {error_type}")

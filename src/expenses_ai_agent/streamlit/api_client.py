class ExpenseAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_expenses(user_id: int | None = None) -> list[dict]:
        return []  # TODO: implement

    def classify_expense(description: str, user_id: int | None = None) -> dict:
        return {}

    def delete_expense(expense_id: int) -> None:
        return

    def get_summary(user_id: int | None = None) -> dict:
        return {}

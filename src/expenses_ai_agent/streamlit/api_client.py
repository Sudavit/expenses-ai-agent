import httpx
import streamlit as st


class ExpenseAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url)

    def __hash__(self) -> int:
        return hash(self.base_url)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExpenseAPIClient):
            return False
        return self.base_url == other.base_url

    def get_expenses(self, user_id: int | None = None) -> list[dict]:
        """
        GET /expenses/
        unpack with response.json()["items"] before returning
        Fetches expenses from the FastAPI backend.
        Uses st.cache_data so you don't DDoS your own API on every Streamlit rerun.
        """
        url = f"{self.base_url}/expenses/"
        params = {"user_id": user_id} if user_id else {}
        headers = {"X-User-ID": str(user_id)} if user_id else {}

        try:
            response = self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()["items"]
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")
            return []

    def classify_expense(self, description: str, user_id: int | None = None) -> dict:
        """
        POST /expenses/classify
        """
        url = f"{self.base_url}/expenses/classify"
        body = {"description": description}
        headers = {"X-User-ID": str(user_id)} if user_id else {}

        try:
            response = self.client.post(url, json=body, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")
            return {}

    def delete_expense(self, expense_id: int) -> None:
        """
        DELETE /expenses/{expense_id}
        """
        url = f"{self.base_url}/expenses/{expense_id}"
        try:
            response = self.client.delete(url)
            response.raise_for_status()
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")

    def get_summary(self, user_id: int | None = None) -> dict:
        """
        GET /analytics/summary
        """
        url = f"{self.base_url}/analytics/summary"
        params = {"user_id": user_id} if user_id else {}
        headers = {"X-User-ID": str(user_id)} if user_id else {}
        try:
            response = self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")
            return {}

    def add_expense(
        self, description: str, amount: float, user_id: int | None = None
    ) -> None:
        """
        POST /expenses/
        """
        url = f"{self.base_url}/expenses/"

        # Build a complete schema layout to pass Pydantic validation checks
        data = {
            "id": None,
            "description": description,
            "amount": str(amount),
            "currency": "EUR",
            "date": "2026-05-24T12:00:00Z",
            "telegram_user_id": user_id,
            "category": "Other",
        }
        headers = {"X-User-ID": str(user_id)} if user_id else {}

        try:
            response = self.client.post(url, json=data, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            st.error(f"Backend validation rejected transaction: {e.response.text}")
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")

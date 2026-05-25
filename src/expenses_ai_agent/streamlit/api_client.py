import httpx
import streamlit as st


class ExpenseAPIClient:
    def __init__(self, base_url: str):
        # Strip trailing slashes to guarantee clean routing appends
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
        # Support passing identity cleanly via headers or query text
        params = {"user_id": user_id} if user_id else {}
        headers = {"X-User-ID": str(user_id)} if user_id else {}

        try:
            response = self.client.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()["items"]
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")
            return []

    def classify_expense(self, description: str, user_id: int | None = None) -> dict:
        """
        POST /expenses/classify
        """
        url = f"{self.base_url}/expenses/classify"
        # Match Pydantic payload body expectations
        body = {"description": description}
        headers = {"X-User-ID": str(user_id)} if user_id else {}

        try:
            response = self.client.post(url, json=body, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
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
            response.raise_for_status()  # Raise an exception for HTTP errors
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
            response.raise_for_status()  # Raise an exception for HTTP errors
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
        data = {
            "description": description,
            "amount": amount,
            "currency": "EUR",  # Fallback to schema requirement baseline
            "date": "2026-05-24T00:00:00",
            "telegram_user_id": user_id,
            "category": "Other",
        }
        headers = {"X-User-ID": str(user_id)} if user_id else {}

        try:
            response = self.client.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")

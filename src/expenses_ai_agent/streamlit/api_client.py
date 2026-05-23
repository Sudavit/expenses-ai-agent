import httpx
import streamlit as st

FASTAPI_URL = "http://127.0.0.1:8000"


class ExpenseAPIClient:
    """ """

    # TODO:
    # call raise_for_status() to propagate errors.
    # Forward user_id as an X-User-ID header
    #   headers={"X-User-ID": str(user_id) if user_id is not None.

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)

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
        url = f"{FASTAPI_URL}/expenses/"
        params = {"user_id": user_id} if user_id else {}

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()["items"]
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")
            return []

    def classify_expense(self, description: str, user_id: int | None = None) -> dict:
        """
        POST /expenses/classify
        """
        url = f"{FASTAPI_URL}/expenses/classify"
        params = {}
        if user_id is None:
            params = {"description": description}
        else:
            params = {"description": description, "user_id": user_id}

        try:
            response = self.client.post(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")
            return {}

    def delete_expense(self, expense_id: int) -> None:
        """
        DELETE /expenses/{expense_id}
        """
        url = f"{FASTAPI_URL}/expenses/{expense_id}"
        try:
            response = self.client.delete(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")

    def get_summary(self, user_id: int | None = None) -> dict:
        """
        GET /analytics/summary
        """
        url = f"{FASTAPI_URL}/analytics/summary"
        params = {"user_id": user_id} if user_id else {}
        try:
            response = self.client.get(url, params=params)
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
        url = f"{FASTAPI_URL}/expenses/"
        data = {
            "description": description,
            "amount": amount,
        }
        if user_id is not None:
            data["user_id"] = user_id

        try:
            response = self.client.post(url, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except httpx.ConnectError as e:
            st.error(f"Backend connection failed: {e}")

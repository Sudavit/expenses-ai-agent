import streamlit as st
from httpx import RequestError

from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient


def render(client: ExpenseAPIClient, user_id: int | None = None) -> None:

    st.header("Add Expense")

    with st.form("add_expense_form"):
        description = st.text_input("Description", key="description")
        submitted = st.form_submit_button("Add Expense")

    if not submitted:
        return

    if not description.strip():
        st.warning("Please fill in all fields.")
        return

    try:
        classification = client.classify_only_expense(
            description=description, user_id=user_id
        )
    except RequestError:
        st.error("Cannot connect to the backend.")
        return

    amount_value = float(classification["total_amount"])
    client.persist_expense(
        description=description, amount=amount_value, user_id=user_id
    )
    st.success(f"Expense added successfully! Category: {classification['category']}")

import streamlit as st

from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient


# streamlit/views/expenses.py
def render(client: ExpenseAPIClient, user_id: int | None = None) -> None:

    st.header("Expenses")
    expenses = client.get_expenses(user_id=user_id)
    # render a row per expense using st.columns
    # left column: category, amount, currency, description
    # right column: st.button("Delete", key=f"del_{item['id']}")
    # that calls client.delete_expense(item["id"]) then st.rerun() to refresh the list)
    # Display table...
    for item in expenses.get("items", []):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"{item['category']} - {item['amount']} {item['currency']}")
            st.write(item["description"])
        with col2:
            if st.button("Delete", key=f"del_{item['id']}"):
                client.delete_expense(item["id"])
                st.rerun()

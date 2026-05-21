import streamlit as st

from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient


# streamlit/views/add_expense.py
def render(client: ExpenseAPIClient, user_id: int | None = None) -> None:

    st.header("Add Expense")
    description = st.text_input("Description")
    amount = st.text_input("Amount")

    with st.form("add_expense_form"):
        st.text_input("Description", key="description")
        st.text_input("Amount", key="amount")

        if st.form_submit_button("Add Expense"):
            # Handle form submission
            submitted = True

    if submitted and description.strip() and amount.strip():
        try:
            amount_value = float(amount)
            # Call API to add expense
            client.add_expense(
                description=description, amount=amount_value, user_id=user_id
            )
            st.success("Expense added successfully!")
        except ValueError:
            st.error("Please enter a valid number for amount.")
    elif submitted:
        st.error("Please fill in all fields.")

    with st.spinner("Adding expense..."):
        client.classify_expense(description=description, user_id=user_id)

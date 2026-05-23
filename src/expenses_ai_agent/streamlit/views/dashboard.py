# streamlit/views/dashboard.py
import plotly.express as px
import streamlit as st

from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

# TODO: Wrap in try/except with separate handlers:
#   except HTTPStatusError as e should include the status code
#   (e.g. e.response.status_code) in the message;
#   except RequestError should say "Cannot connect..."
#   — the tests assert on these substrings


def render(client: ExpenseAPIClient, user_id: int | None = None) -> None:
    st.header("Dashboard")
    summary = client.get_summary(user_id=user_id)

    # pie chart of summary["category_totals"]["category_breakdown"]
    # with plotly express, title "Expenses by Category"
    # show st.info if the data dictionary is empty.
    if not summary["category_totals"].get("category_breakdown"):
        st.info("No expense data available for category breakdown.")
    else:
        px.pie(
            names=summary["category_totals"].get("category_breakdown", {}).keys(),
            values=[
                float(v)
                for v in summary["category_totals"]
                .get("category_breakdown", {})
                .values()
            ],
            title="Expenses by Category",
        )

    # pie chart of summary["category_totals"]["category_breakdown"]
    # with plotly express, title "Expenses by Category"
    # show st.info if the data dictionary is empty.
    if not summary["monthly_trends"].get("monthly_totals"):
        st.info("No expense data available for monthly trends.")
    else:
        px.bar(
            x=list(summary["monthly_trends"].get("monthly_totals", {}).keys()),
            y=[
                float(v)
                for v in summary["monthly_trends"].get("monthly_totals", {}).values()
            ],
            title="Monthly Expenses",
        )

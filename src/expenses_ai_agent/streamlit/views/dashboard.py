# streamlit/views/dashboard.py
import plotly.express as px
import streamlit as st
from httpx import HTTPStatusError, RequestError

from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient


def render(client: ExpenseAPIClient, user_id: int | None = None) -> None:
    st.header("Dashboard")

    try:
        summary = client.get_summary(user_id=user_id)
    except HTTPStatusError as exc:
        st.error(f"Failed to load dashboard data: {exc.response.status_code}")
        return
    except RequestError:
        st.error("Cannot connect to the backend.")
        return

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
    if not summary["monthly_totals"].get("monthly_totals"):
        st.info("No expense data available for monthly trends.")
    else:
        px.bar(
            x=list(summary["monthly_totals"].get("monthly_totals", {}).keys()),
            y=[
                float(v)
                for v in summary["monthly_totals"].get("monthly_totals", {}).values()
            ],
            title="Monthly Expenses",
        )

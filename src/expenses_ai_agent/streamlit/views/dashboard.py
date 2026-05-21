# streamlit/views/dashboard.py
import plotly.express as px
import streamlit as st

from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient


def render(client: ExpenseAPIClient, user_id: int | None = None) -> None:
    st.header("Dashboard")
    summary = client.get_summary(user_id=user_id)
    # Display charts...
    px.pie(
        names=summary["category_totals"].get("category_breakdown", {}).keys(),
        values=[
            float(v)
            for v in summary["category_totals"].get("category_breakdown", {}).values()
        ],
        title="Expenses by Category",
    )

    px.bar(
        x=list(summary["monthly_trends"].get("monthly_totals", {}).keys()),
        y=[
            float(v)
            for v in summary["monthly_trends"].get("monthly_totals", {}).values()
        ],
        title="Monthly Expenses",
    )

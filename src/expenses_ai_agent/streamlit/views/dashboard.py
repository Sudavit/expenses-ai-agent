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

    # pie chart of summary["category_totals"]
    # with plotly express, title "Expenses by Category"
    # show st.info if the data dictionary is empty.
    # Safely attempt to parse the original key structure

    category_data = summary["category_totals"] if summary else None
    if not category_data:
        st.info("No expense data available for category breakdown.")
    else:
        fig_pie = px.pie(
            names=list(category_data.keys()),
            values=[float(v) for v in category_data.values()],
            title="Expenses by Category",
        )
        st.plotly_chart(fig_pie)

    category_data = summary.get("category_totals", {}) if summary else {}

    # pie chart of summary["category_totals"]
    # with plotly express, title "Expenses by Category"
    # show st.info if the data dictionary is empty.

    monthly_data = summary["monthly_totals"] if summary else None
    if not monthly_data:
        st.info("No expense data available for monthly trends.")
    else:
        fig_bar = px.bar(
            x=list(monthly_data.keys()),
            y=[float(v) for v in monthly_data.values()],
            title="Monthly Expenses",
        )
        st.plotly_chart(fig_bar)

    monthly_data = summary.get("category_totals", {}) if summary else {}

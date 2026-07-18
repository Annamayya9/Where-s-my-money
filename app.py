from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal

import pandas as pd
import streamlit as st

from splitwise_client import SplitwiseClient, as_decimal


st.set_page_config(page_title="Splitwise Credit Card Spending", layout="wide")

st.title("Splitwise Monthly Credit-Card Spending")

access_token = st.secrets.get("SPLITWISE_ACCESS_TOKEN")
if not access_token:
    st.error("Missing SPLITWISE_ACCESS_TOKEN in .streamlit/secrets.toml")
    st.stop()

today = date.today()

col1, col2 = st.columns(2)
with col1:
    selected_month = st.selectbox(
        "Month",
        options=list(range(1, 13)),
        index=today.month - 1,
        format_func=lambda month: calendar.month_name[month],
    )

with col2:
    selected_year = st.number_input(
        "Year",
        min_value=2000,
        max_value=2100,
        value=today.year,
        step=1,
    )

start_date = date(int(selected_year), int(selected_month), 1)
if selected_month == 12:
    end_date_exclusive = date(int(selected_year) + 1, 1, 1)
else:
    end_date_exclusive = date(int(selected_year), int(selected_month) + 1, 1)


def money(value: Decimal) -> str:
    return f"${value.quantize(Decimal('0.01'))}"


@st.cache_data(show_spinner=False)
def load_expenses(token: str, start: date, end: date) -> tuple[int, list[dict]]:
    client = SplitwiseClient(token)
    current_user_id = client.get_current_user_id()
    expenses = client.get_expenses_for_date_range(start, end)
    return current_user_id, expenses


if st.button("Calculate spending", type="primary"):
    with st.spinner("Fetching Splitwise expenses..."):
        current_user_id, expenses = load_expenses(
            access_token,
            start_date,
            end_date_exclusive,
        )

    included_rows = []

    total_paid_upfront = Decimal("0")
    actual_personal_spending = Decimal("0")
    total_others_owe_back = Decimal("0")

    for expense in expenses:
        if expense.get("deleted_at"):
            continue

        if expense.get("payment") is True:
            continue

        current_user_entry = next(
            (
                user
                for user in expense.get("users", [])
                if int(user.get("user", {}).get("id", 0)) == current_user_id
            ),
            None,
        )

        if not current_user_entry:
            continue

        paid_share = as_decimal(current_user_entry.get("paid_share"))
        owed_share = as_decimal(current_user_entry.get("owed_share"))

        if paid_share <= 0:
            continue

        others_owe_back = paid_share - owed_share

        total_paid_upfront += paid_share
        actual_personal_spending += owed_share
        total_others_owe_back += others_owe_back

        included_rows.append(
            {
                "Date": expense.get("date", "")[:10],
                "Description": expense.get("description", ""),
                "Category": expense.get("category", {}).get("name", ""),
                "Currency": expense.get("currency_code", ""),
                "Paid upfront": money(paid_share),
                "Personal spending": money(owed_share),
                "Others owe back": money(others_owe_back),
            }
        )

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Total paid upfront", money(total_paid_upfront))
    metric_col2.metric("Actual personal spending", money(actual_personal_spending))
    metric_col3.metric("Amount others owe back", money(total_others_owe_back))

    st.subheader("Included expenses")

    if included_rows:
        st.dataframe(
            pd.DataFrame(included_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No matching expenses found for this month.")

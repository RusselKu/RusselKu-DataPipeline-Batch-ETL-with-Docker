import streamlit as st
import pandas as pd
from utils.db import get_db

def app():
    st.header("🌍 Currency Names and Current Rates")

    db = get_db()
    if db is None:
        st.error("Failed to connect to the database")
        return

    # Get currency names
    doc_names = db["processed_processed_exchange_rates_names"].find_one({"_id": "currency_names"})
    if not doc_names or "currencies" not in doc_names:
        st.warning("Currency names not available")
        return

    df_names = pd.DataFrame([
        {"Code": code.upper(), "Name": name}
        for code, name in doc_names["currencies"].items()
    ])

    # Get latest exchange rates
    doc_rates = db["processed_exchange_rates_api"].find_one(sort=[("_id", -1)])
    if not doc_rates or "rates" not in doc_rates:
        st.warning("Exchange rates not available")
        return

    df_rates = pd.DataFrame([
        {"Code": code.upper(), "Rate": data.get("rate")}
        for code, data in doc_rates["rates"].items()
        if isinstance(data, dict) and "rate" in data
    ])

    # Merge both DataFrames on "Code"
    df_merged = pd.merge(df_names, df_rates, on="Code", how="inner")

    # 🔍 Real-time search
    search = st.text_input("🔎 Search by code or currency name", placeholder="e.g., usd, peso, bitcoin...")

    if search:
        df_merged = df_merged[
            df_merged["Code"].str.contains(search, case=False) |
            df_merged["Name"].str.contains(search, case=False)
        ]

    # Show table
    st.dataframe(
        df_merged.sort_values("Code"),
        hide_index=True,
        use_container_width=True,
        height=min(600, 40 * len(df_merged) + 100)
    )

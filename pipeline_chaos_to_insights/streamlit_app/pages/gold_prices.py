import streamlit as st
import pandas as pd
from utils.db import get_db
from utils.charts import line_chart

def app():
    st.header("🥇 Gold Prices (PLN)")

    db = get_db()
    if db is None:
        st.error("Unable to connect to the database")
        return

    gold_data = list(db["processed_gold_prices"].find().sort("_id", -1).limit(30))

    if gold_data:
        records = []
        for entry in reversed(gold_data): 
            for ts in entry.get("time_series", []):
                records.append({
                    "Date": pd.to_datetime(ts["date"]),
                    "Price": ts["price_pln"]
                })

        gold_df = pd.DataFrame(records)

        if not gold_df.empty:

            gold_df = gold_df.sort_values(by="Date")

            # sub tbale 
            st.subheader("📋 Price history (last 30 days)")

            # Style
            styled_df = gold_df.style.set_table_styles(
                [
                    {"selector": "th", "props": [("background-color", "#FFA500"), ("color", "black"), ("font-size", "14px")]},
                    {"selector": "td", "props": [("color", "#111"), ("font-size", "13px")]}
                ]
            )

            st.dataframe(styled_df, hide_index=True, height=300, use_container_width=False)

            # Space and divisor 
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()

            # Line graph 
            fig = line_chart(gold_df, "Date", "Price", "Last 30 Days Gold Prices")
            st.plotly_chart(fig, use_container_width=True)

            # Price change indicator
            price_change = gold_df.iloc[-1]['Price'] - gold_df.iloc[0]['Price']
            st.metric(
                "🔺 Cambio en 30 días",
                f"{gold_df.iloc[-1]['Price']:.2f} PLN",
                f"{price_change:.2f} PLN ({(price_change / gold_df.iloc[0]['Price']) * 100:.2f}%)"
            )
        else:
            st.warning("No gold price data available for graphing")
    else:
        st.warning("No data avalaible")

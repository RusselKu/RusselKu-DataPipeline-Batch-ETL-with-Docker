import streamlit as st
import pandas as pd
from utils.db import get_db
from utils.charts import bar_chart, line_chart
import plotly.express as px

def app():
    st.header("💱 Exchange Rates")

    db = get_db()
    if db is None:
        st.error("Could not connect to the database")
        return

    latest = db["processed_exchange_rates_api"].find_one(sort=[("_id", -1)])

    if not latest or "rates" not in latest:
        st.warning("No data available")
        return

    rates_data = latest["rates"]
    df = pd.DataFrame({
        "Currency": list(rates_data.keys()),
        "Rate": [v["rate"] if isinstance(v, dict) else v for v in rates_data.values()]
    })

    # Sort descending and select top 10
    df_top10 = df.sort_values(by="Rate", ascending=False).head(10).reset_index(drop=True)

    st.subheader("💸 Top 10 currencies by exchange rate")

    # Improved table style and size
    styled_df = df_top10.style.set_table_styles(
        [
            {"selector": "th", "props": [("background-color", "#6A0DAD"), ("color", "white"), ("font-size", "16px")]},
            {"selector": "td", "props": [("color", "#111"), ("font-size", "14px"), ("padding", "8px 12px")]},
        ]
    ).set_properties(**{'max-width': '600px', 'white-space': 'nowrap'})

    st.dataframe(styled_df, use_container_width=True, height=350)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # Bar chart for top 10
    st.plotly_chart(
        bar_chart(df_top10, "Currency", "Rate", "Comparison of top 10 currency rates"),
        use_container_width=True
    )

    # Line chart for top 10
    st.subheader("📈 Rate trends")
    st.plotly_chart(
        line_chart(df_top10, "Currency", "Rate", "Top 10 currency rates - line chart"),
        use_container_width=True
    )

    # Pie chart to show share of each currency in top 10
    st.subheader("🥧 Currency distribution")

    fig_pie = px.pie(
        df_top10,
        names="Currency",
        values="Rate",
        title="Top 10 currencies proportion by rate",
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig_pie, use_container_width=True)

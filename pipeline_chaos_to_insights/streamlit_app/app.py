import streamlit as st
from pages import exchange_rates, gold_prices, currency_names

st.set_page_config(page_title="Financial & Commodities Dashboard", layout="wide")

# Inject custom CSS
with open("styles/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Select a page:", 
                        ("Exchange Rates", "Gold Prices", "Currency Names"))

st.title("💰 Financial & Commodities Dashboard")
st.divider()

if page == "Exchange Rates":
    exchange_rates.app()
elif page == "Gold Prices":
    gold_prices.app()
elif page == "Currency Names":
    currency_names.app()
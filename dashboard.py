
# RH AlphaRadar – KI-gestütztes Signal-Dashboard
import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt

st.set_page_config(page_title="RH AlphaRadar", layout="wide")
st.title("📈 RH AlphaRadar – KI-Trading-Dashboard")

assets = {
    "ETFs": ["IQQW.DE", "EQQQ.DE", "2B76.DE", "AIAI.DE", "ESPO.DE"],
    "Aktien": ["NVDA", "TSLA", "AMZN", "MSFT", "SAP.DE", "AIR.DE"]
}

selected_group = st.selectbox("Asset-Gruppe", list(assets.keys()))
stocks = assets[selected_group]

end = dt.date.today()
start = end - dt.timedelta(days=90)

@st.cache_data
def load_data(symbol):
    df = yf.download(symbol, start=start, end=end)
    df["Return"] = df["Adj Close"].pct_change().fillna(0)
    df["Momentum"] = df["Adj Close"] / df["Adj Close"].rolling(window=14).mean()
    return df

st.subheader("📊 Signalübersicht")
signal_data = []
for symbol in stocks:
    df = load_data(symbol)
    last_price = df["Adj Close"].iloc[-1]
    momentum = df["Momentum"].iloc[-1]
    score = round((momentum - 1) * 100, 2)
    signal_data.append((symbol, last_price, score))

signal_df = pd.DataFrame(signal_data, columns=["Ticker", "Kurs", "Momentum-Score"])
signal_df = signal_df.sort_values(by="Momentum-Score", ascending=False)
st.dataframe(signal_df)

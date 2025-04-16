
# RH AlphaRadar – KI-gestütztes Signal-Dashboard
import streamlit as st
from PIL import Image

logo = Image.open("logo_rh_alpharadar.png")
st.set_page_config(page_title="RH AlphaRadar", layout="wide", page_icon=logo)

# Optional: Logo oben anzeigen
st.image(logo, width=100)

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
    df = yf.download(symbol, start=start, end=end, progress=False)
    if df.empty or "Adj Close" not in df.columns:
        return None
    df["Return"] = df["Adj Close"].pct_change().fillna(0)
    df["Momentum"] = df["Adj Close"] / df["Adj Close"].rolling(window=14).mean()
    return df

st.subheader("📊 Signalübersicht")
signal_data = []
for symbol in stocks:
    df = load_data(symbol)
    if df is None:
        continue
    last_price = df["Adj Close"].iloc[-1]
    momentum = df["Momentum"].iloc[-1]
    score = round((momentum - 1) * 100, 2)
    signal_data.append((symbol, last_price, score))

signal_df = pd.DataFrame(signal_data, columns=["Ticker", "Kurs", "Momentum-Score"])
signal_df = signal_df.sort_values(by="Momentum-Score", ascending=False)
st.dataframe(signal_df)

# Testnachricht über Telegram senden
import requests

BOT_TOKEN = "8126985237:AAGKurwSf_zv263XY2FmYladow6cH05o1e8"
CHAT_ID = 7428599123  # deine persönliche ID

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, data=data)
    return response.json()

# Einmalige Testnachricht (z. B. nach Button-Klick)
if st.button("📩 Testnachricht senden"):
    result = send_telegram_message("✅ <b>RH AlphaRadar</b> ist jetzt live!\\n\\nAb sofort erhältst du deine Handelssignale direkt per Telegram.")
    st.success("Nachricht gesendet!" if result["ok"] else "Fehler beim Senden.")


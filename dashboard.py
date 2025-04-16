
import streamlit as st
from PIL import Image
import os
import pandas as pd
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt

st.set_page_config(page_title="RH AlphaRadar – Signalübersicht", page_icon="favicon.png", layout="wide")

# Logo einbinden
logo_path = "logo_rh_alpharadar.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=120)

st.title("📈 RH AlphaRadar – KI-Trading-Dashboard")

stocks = ["NVDA", "TSLA", "AMZN", "MSFT", "ASML", "META", "SAP.DE", "AIR.DE", "LVMH.PA"]

selected_stock = st.selectbox("📊 Einzelaktien-Analyse", stocks)

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

st.subheader("📌 Aktuelle Signale")
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

st.subheader("📉 Kursentwicklung & Momentum")
df = load_data(selected_stock)
if df is not None:
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df.index, df["Adj Close"], label="Kurs", color="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(df.index, df["Momentum"], label="Momentum", color="tab:orange")
    ax1.set_ylabel("Kurs")
    ax2.set_ylabel("Momentum")
    plt.title(f"{selected_stock} – Kurs & Momentum")
    st.pyplot(fig)



# Telegram-Funktion einbinden
import requests

BOT_TOKEN = "8126985237:AAGKurwSf_zv263XY2FmYladow6cH05o1e8"
CHAT_ID = 7428599123

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    return requests.post(url, data=data)

# Button zur Testnachricht im Streamlit-Dashboard
if st.button("📩 Telegram-Testnachricht senden"):
    message = """✅ RH AlphaRadar: Dein Signal-Dashboard ist aktiv.
Neue Momentum-Signale verfügbar."""

    response = send_telegram_message(message)
    if response.status_code == 200:
        st.success("Testnachricht erfolgreich gesendet.")
    else:
        st.error("Fehler beim Senden der Nachricht.")

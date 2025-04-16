
import streamlit as st
from PIL import Image
import os
import pandas as pd
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="RH AlphaRadar – Signalübersicht", page_icon="favicon.png", layout="wide")

# Logo einbinden
logo_path = "logo_rh_alpharadar.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=120)

st.title("📈 RH AlphaRadar – KI-Trading-Dashboard")

watchlists = {
    "Tech/US": ["NVDA", "TSLA", "AMZN", "MSFT", "ASML", "META"],
    "DAX": ["SAP.DE", "AIR.DE", "SIE.DE", "DAI.DE", "ALV.DE", "BMW.DE", "BAS.DE", "BAYN.DE", "LIN.DE"],
    "MDAX": ["RHM.DE", "PUM.DE", "FIE.DE", "CTS.DE", "HNR1.DE", "EVK.DE", "1COV.DE", "ZAL.DE"]
}

selected_watchlist = st.selectbox("📂 Watchlist auswählen", list(watchlists.keys()))
stocks = watchlists[selected_watchlist]
selected_stock = st.selectbox("📊 Einzelaktien-Analyse", options=stocks)

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

# Daten je Watchlist vorbereiten
all_scores = {}
for name, symbols in watchlists.items():
    scores = []
    for symbol in symbols:
        df = load_data(symbol)
        if df is not None and "Momentum" in df.columns:
            score = round((df["Momentum"].iloc[-1] - 1) * 100, 2)
            scores.append(score)
    if scores:
        avg_score = round(sum(scores) / len(scores), 2)
        all_scores[name] = avg_score

# Ø Momentum-Score je Watchlist – Balkendiagramm
st.subheader("📊 Vergleich: Ø Momentum-Score je Watchlist")
score_df = pd.DataFrame(list(all_scores.items()), columns=["Watchlist", "Ø Momentum-Score"])
fig2, ax2 = plt.subplots()
ax2.bar(score_df["Watchlist"], score_df["Ø Momentum-Score"], color=["#4c78a8", "#f58518", "#54a24b"])
ax2.set_ylabel("Ø Momentum-Score")
ax2.set_title("Momentum-Vergleich der Watchlists")
st.pyplot(fig2)

# 📈 Score-Trend über mehrere Wochen – fiktiv für Demo
st.subheader("📈 Score-Trend (Demo)")
trend_data = {
    "Tech/US": [1.5, 2.0, 2.8, 2.4, 2.1],
    "DAX": [0.8, 1.1, 1.3, 1.4, 1.2],
    "MDAX": [0.9, 1.0, 1.1, 1.0, 0.95]
}
weeks = ["KW10", "KW11", "KW12", "KW13", "KW14"]

fig3, ax3 = plt.subplots()
for name, values in trend_data.items():
    ax3.plot(weeks, values, label=name, linewidth=2)
ax3.set_title("Score-Trend der letzten Wochen")
ax3.set_ylabel("Ø Momentum-Score")
ax3.set_xlabel("Kalenderwoche")
ax3.grid(True)
ax3.legend()
st.pyplot(fig3)

# Signalübersicht
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

# Kursentwicklung
st.subheader("📉 Kursentwicklung & Momentum")
df = load_data(selected_stock)
if df is not None:
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df.index, df["Adj Close"], label="Kurs", color="#4c78a8")
    ax2 = ax1.twinx()
    ax2.plot(df.index, df["Momentum"], label="Momentum", color="#f58518")
    ax1.set_ylabel("Kurs")
    ax2.set_ylabel("Momentum")
    plt.title(f"{selected_stock} – Kurs & Momentum")
    st.pyplot(fig)

# Telegram-Integration
BOT_TOKEN = "8126985237:AAGKurwSf_zv263XY2FmYladow6cH05o1e8"
CHAT_ID = 7428599123

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    return requests.post(url, data=data)

def send_telegram_chart(image_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as image_file:
        data = {"chat_id": CHAT_ID}
        files = {"photo": image_file}
        return requests.post(url, data=data, files=files)

if st.button("📩 Telegram-Testnachricht senden"):
    msg = "✅ RH AlphaRadar: Neue Score-Daten verfügbar.
Woche: KW14"
    r1 = send_telegram_message(msg)
    r2 = send_telegram_chart("watchlist_scores_chart.png")
    if r1.status_code == 200 and r2.status_code == 200:
        st.success("Telegram-Text + Chart erfolgreich gesendet.")
    else:
        st.error("Fehler beim Senden über Telegram.")

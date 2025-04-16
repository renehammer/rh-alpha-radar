
# Telegram-Bot Konfiguration
import requests

BOT_TOKEN = "8126985237:AAGKurwSf_zv263XY2FmYladow6cH05o1e8"
CHAT_ID = 7428599123

def send_telegram_message(message, chat_id=CHAT_ID):
    if chat_id is None:
        raise ValueError("Chat ID ist nicht gesetzt. Bitte zuerst setzen.")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    return response.json()

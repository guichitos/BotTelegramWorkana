#send_telegram_message.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def mensaje(titulo_mg, enlace_mg):
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no están configurados.")
        return

    mensaje_texto = f"Nuevo proyecto publicado - {titulo_mg}\n{enlace_mg}"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje_texto
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Mensaje enviado correctamente a Telegram.")
    else:
        print(f"Error al enviar mensaje a Telegram: {response.text}")


if __name__ == "__main__":
    titulo_prueba = "Proyecto de prueba Telegram"
    enlace_prueba = "https://www.workana.com/job/proyecto-prueba-telegram"

    try:
        mensaje(titulo_prueba, enlace_prueba)
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

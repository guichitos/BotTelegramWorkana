#mensaje_telegram.py
import requests

def mensaje(titulo_mg, enlace_mg):
    TELEGRAM_BOT_TOKEN = '8017150739:AAGb1UzPk9mWdY5GIfCh2pwLi6J1_NY4Kvk'
    TELEGRAM_CHAT_ID = '1341946489'
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
    # Datos de prueba
    titulo_prueba = "Proyecto de prueba Telegram"
    enlace_prueba = "https://www.workana.com/job/proyecto-prueba-telegram"

    try:
        mensaje(titulo_prueba, enlace_prueba)
    except Exception as e:
        print(f"❌ Error enviando mensaje a Telegram: {e}")
#leer_mensajes.py
import os
import requests

import config.env
from telegram_admin_utils import get_admin_chat_id


def leer_todos_los_mensajes():
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN no está configurado.")
        return []
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    if response.status_code == 200:
        datos = response.json()
        mensajes = []
        for resultado in datos['result']:
            chat_id = resultado['message']['chat']['id']
            texto = resultado['message'].get('text', '')
            mensajes.append((chat_id, texto))
        return mensajes
    else:
        print(f"Error al obtener mensajes: {response.text}")
        return []


def leer_ultimo_mensaje():
    mensajes = leer_todos_los_mensajes()
    if mensajes:
        return mensajes[-1]  # Último mensaje recibido
    else:
        return None

def leer_ultimo_mensaje_usuario():
    mensajes = leer_todos_los_mensajes()
    admin_chat_id = get_admin_chat_id()
    if admin_chat_id is None:
        print("Error: No se encontró usuario admin en bot_users.")
        return None
    for mensaje in reversed(mensajes):
        chat_id, texto = mensaje
        if chat_id == int(admin_chat_id):  # Asegura que es del usuario admin
            return mensaje
    return None



def main():
    print("--- Último mensaje recibido ---")
    ultimo = leer_ultimo_mensaje()
    if ultimo:
        print(f"Chat ID: {ultimo[0]} - Texto: {ultimo[1]}")
    else:
        print("No se encontraron mensajes.")

    print("\n--- Todos los mensajes ---")
    todos = leer_todos_los_mensajes()
    for idx, (chat_id, texto) in enumerate(todos):
        print(f"{idx+1}. Chat ID: {chat_id} - Texto: {texto}")


if __name__ == "__main__":
    main()

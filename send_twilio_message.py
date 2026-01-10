# send_twilio_message.py
import os

import config.env
from twilio.rest import Client

def mensaje(titulo_mg, enlace_mg):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_FROM')
    to_number = os.getenv('TWILIO_TO')

    if not account_sid or not auth_token or not from_number or not to_number:
        raise ValueError("Faltan variables de entorno en el archivo .env")

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_=from_number,
        body=f'Nuevo proyecto publicado - {titulo_mg} url: {enlace_mg}',
        to=to_number
    )
    print(f"✅ Mensaje enviado con SID: {message.sid}")

if __name__ == "__main__":
    # Datos de prueba
    titulo_prueba = "Proyecto de prueba Twilio"
    enlace_prueba = "https://www.workana.com/job/proyecto-prueba-twilio"

    try:
        mensaje(titulo_prueba, enlace_prueba)
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")

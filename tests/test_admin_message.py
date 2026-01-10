import os
import unittest

import config.env

from send_telegram_message import mensaje
from telegram_admin_utils import get_admin_chat_id

# Este test verifica que el bot pueda enviar un mensaje a un usuario admin.
# No requiere que 01_bot.py esté corriendo; usa el token para enviar vía API.
# Resultado exitoso esperado: mensaje enviado correctamente (assert True) y
# el test finaliza sin skip cuando TELEGRAM_BOT_TOKEN está configurado y
# existe un admin en bot_users.


class TestAdminMessage(unittest.TestCase):
    def test_admin_can_receive_message(self):
        token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
        if not token:
            self.skipTest(
                "TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN no está configurado. "
                "Define la variable de entorno para poder enviar el mensaje."
            )

        admin_chat_id = get_admin_chat_id()
        if admin_chat_id is None:
            self.skipTest(
                "No existe usuario admin en bot_users. "
                "Agrega un admin para ejecutar la prueba."
            )

        ok = mensaje(
            "Test de mensaje admin",
            "https://www.workana.com/",
            chat_id=admin_chat_id,
        )
        self.assertTrue(
            ok,
            (
                "No se pudo enviar el mensaje al admin. "
                "Verifica TELEGRAM_BOT_TOKEN, conectividad de red y que "
                "admin_chat_id sea válido."
            ),
        )


if __name__ == "__main__":
    unittest.main()

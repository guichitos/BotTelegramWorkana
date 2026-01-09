import os
import unittest

from send_telegram_message import mensaje
from telegram_admin_utils import get_admin_chat_id


class TestAdminMessage(unittest.TestCase):
    def test_admin_can_receive_message(self):
        if not os.getenv("TELEGRAM_BOT_TOKEN"):
            self.skipTest("TELEGRAM_BOT_TOKEN no está configurado.")

        admin_chat_id = get_admin_chat_id()
        if admin_chat_id is None:
            self.skipTest("No existe usuario admin en bot_users.")

        ok = mensaje(
            "Test de mensaje admin",
            "https://www.workana.com/",
            chat_id=admin_chat_id,
        )
        self.assertTrue(ok, "No se pudo enviar el mensaje al admin.")


if __name__ == "__main__":
    unittest.main()

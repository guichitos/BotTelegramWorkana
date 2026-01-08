import unittest

from workana_bot_database_model import WorkanaBotDatabase


class TestAdminUser(unittest.TestCase):
    def test_admin_user_exists_with_name_and_id(self):
        db = WorkanaBotDatabase()
        query = (
            "SELECT telegram_user_id, username "
            "FROM bot_users WHERE role = 'admin' ORDER BY id ASC LIMIT 1"
        )
        result = db.execute_query(query)
        self.assertTrue(result, "No se encontró usuario admin en bot_users.")

        telegram_user_id, username = result[0]
        self.assertIsNotNone(telegram_user_id, "El admin no tiene telegram_user_id.")
        self.assertIsNotNone(username, "El admin no tiene username.")
        self.assertNotEqual(str(username).strip(), "", "El username del admin está vacío.")


if __name__ == "__main__":
    unittest.main()

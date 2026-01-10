import unittest

from workana_bot_database_model import WorkanaBotDatabase


# Este test valida que exista un usuario admin en la tabla bot_users.
# Resultado exitoso esperado: la consulta devuelve al menos un registro y
# el usuario admin encontrado tiene telegram_user_id definido, username no
# nulo y no vacío.
class TestAdminUser(unittest.TestCase):
    def test_admin_user_exists_with_name_and_id(self):
        db = WorkanaBotDatabase()
        config = db._get_connection_config()
        masked_password = "***" if config.get("password") else "(empty)"
        print(
            "DB config -> "
            f"host={config.get('host')} "
            f"port={config.get('port')} "
            f"database={config.get('database')} "
            f"user={config.get('user')} "
            f"password={masked_password}"
        )
        db.connect()
        self.assertTrue(
            db.IsConnected,
            (
                "No se pudo conectar a la base de datos. "
                f"host={config.get('host')} "
                f"port={config.get('port')} "
                f"database={config.get('database')} "
                f"user={config.get('user')}"
            ),
        )
        db.disconnect()
        query = (
            "SELECT telegram_user_id, username "
            "FROM bot_users WHERE role = 'admin' ORDER BY id ASC LIMIT 1"
        )
        result = db.execute_query(query)
        print(f"Resultado admin -> {result}")
        self.assertTrue(result, "No se encontró usuario admin en bot_users.")

        telegram_user_id, username = result[0]
        self.assertIsNotNone(telegram_user_id, "El admin no tiene telegram_user_id.")
        self.assertIsNotNone(username, "El admin no tiene username.")
        self.assertNotEqual(str(username).strip(), "", "El username del admin está vacío.")


if __name__ == "__main__":
    unittest.main()
